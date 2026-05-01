import argparse
import base64
import html
import json
import mimetypes
import os
import re
import signal
import subprocess
import sys
import webbrowser
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except Exception:
        pass


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FFMPEG = PROJECT_ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
DEFAULT_PID_FILE = PROJECT_ROOT / ".video_gallery.pid"
DEFAULT_METADATA_FILE = PROJECT_ROOT / "data" / "videos.json"
DEFAULT_POSTER_DIR = PROJECT_ROOT / "exports" / "posters"
DEFAULT_TOPICS_DIR = PROJECT_ROOT / "topics"
LEGACY_VIDEO_ROOTS = [
    PROJECT_ROOT / "exports" / "final",
    PROJECT_ROOT / "exports" / "manim" / "videos",
]


def is_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def default_video_roots() -> list[Path]:
    roots: list[Path] = []
    if DEFAULT_TOPICS_DIR.exists():
        for topic in sorted(DEFAULT_TOPICS_DIR.iterdir()):
            if not topic.is_dir():
                continue
            roots.extend(
                [
                    topic / "exports" / "final",
                    topic / "exports" / "manim" / "videos",
                ]
            )
    roots.extend(LEGACY_VIDEO_ROOTS)
    return roots


DEFAULT_VIDEO_ROOTS = default_video_roots()


def encode_relpath(path: Path) -> str:
    rel = path.resolve().relative_to(PROJECT_ROOT).as_posix()
    return base64.urlsafe_b64encode(rel.encode("utf-8")).decode("ascii").rstrip("=")


def decode_relpath(value: str) -> Path:
    padded = value + "=" * (-len(value) % 4)
    rel = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
    path = (PROJECT_ROOT / rel).resolve()
    if not is_inside(path, PROJECT_ROOT):
        raise ValueError("Path escapes project root.")
    return path


def human_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{size} B"


def probe_video(path: Path, ffmpeg: Path) -> dict[str, object]:
    if not ffmpeg.exists():
        return {"duration": None, "has_audio": None}

    result = subprocess.run(
        [str(ffmpeg), "-hide_banner", "-i", str(path)],
        text=True,
        capture_output=True,
    )
    output = result.stderr + result.stdout
    duration_match = re.search(r"Duration:\s*([0-9:.]+)", output)
    duration = duration_match.group(1) if duration_match else None
    return {
        "duration": duration,
        "duration_seconds": duration_to_seconds(duration),
        "has_audio": "Audio:" in output,
    }


def duration_to_seconds(duration: str | None) -> float | None:
    if not duration:
        return None

    match = re.match(r"(\d+):(\d+):(\d+(?:\.\d+)?)", duration)
    if not match:
        return None

    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def poster_seek_time(duration_seconds: float | None) -> float:
    if not duration_seconds or duration_seconds <= 0:
        return 0.5
    if duration_seconds < 2:
        return max(0.1, duration_seconds * 0.5)
    return min(max(0.8, duration_seconds * 0.22), max(0.1, duration_seconds - 0.2))


def generated_poster_path(video: Path) -> Path:
    topic_root = topic_root_for(video)
    if topic_root:
        return topic_root / "exports" / "posters" / f"{encode_relpath(video)}.jpg"
    return DEFAULT_POSTER_DIR / f"{encode_relpath(video)}.jpg"


def topic_root_for(path: Path) -> Path | None:
    try:
        rel = path.resolve().relative_to(DEFAULT_TOPICS_DIR.resolve())
    except ValueError:
        return None
    if not rel.parts:
        return None
    return DEFAULT_TOPICS_DIR / rel.parts[0]


def generate_poster(video: Path, ffmpeg: Path, duration_seconds: float | None) -> Path | None:
    if not ffmpeg.exists():
        return None

    poster = generated_poster_path(video)
    if poster.exists() and poster.stat().st_mtime >= video.stat().st_mtime:
        return poster

    poster.parent.mkdir(parents=True, exist_ok=True)
    command = [
        str(ffmpeg),
        "-y",
        "-ss",
        f"{poster_seek_time(duration_seconds):.3f}",
        "-i",
        str(video),
        "-frames:v",
        "1",
        "-vf",
        "scale=720:-1",
        "-q:v",
        "3",
        str(poster),
    ]
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Warning: failed to generate poster for {video}: {result.stderr}", file=sys.stderr)
        return poster if poster.exists() else None
    return poster


def load_video_metadata(metadata_file: Path = DEFAULT_METADATA_FILE) -> dict[str, dict[str, object]]:
    if not metadata_file.exists():
        return {}

    try:
        raw = json.loads(metadata_file.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        print(f"Warning: failed to parse {metadata_file}: {exc}", file=sys.stderr)
        return {}

    videos = raw.get("videos", raw) if isinstance(raw, dict) else {}
    if not isinstance(videos, dict):
        return {}

    normalized: dict[str, dict[str, object]] = {}
    for key, value in videos.items():
        if isinstance(key, str) and isinstance(value, dict):
            normalized[key.replace("\\", "/")] = value
    return normalized


def metadata_for(rel_path: str, file_name: str, metadata: dict[str, dict[str, object]]) -> dict[str, object]:
    return metadata.get(rel_path) or metadata.get(file_name) or {}


def resolve_metadata_cover(meta: dict[str, object]) -> Path | None:
    cover = meta.get("cover")
    if not isinstance(cover, str) or not cover.strip():
        return None

    path = Path(cover)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    path = path.resolve()
    if not path.exists() or not is_inside(path, PROJECT_ROOT):
        return None
    if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        return None
    return path


def asset_url(path: Path | None) -> str | None:
    if not path:
        return None
    return f"/asset/{encode_relpath(path)}"


def normalize_chapters(raw: object) -> list[dict[str, object]]:
    if not isinstance(raw, list):
        return []

    chapters: list[dict[str, object]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            continue

        try:
            start = max(0.0, float(item.get("start", 0)))
        except (TypeError, ValueError):
            continue

        title = item.get("title") or f"段落 {index + 1}"
        chapter: dict[str, object] = {
            "title": str(title),
            "start": round(start, 3),
        }

        end_value = item.get("end")
        if end_value is not None:
            try:
                chapter["end"] = round(max(start, float(end_value)), 3)
            except (TypeError, ValueError):
                pass

        chapters.append(chapter)

    return sorted(chapters, key=lambda chapter: float(chapter["start"]))


def remove_video_metadata(rel_path: str, file_name: str, metadata_file: Path = DEFAULT_METADATA_FILE) -> int:
    if not metadata_file.exists():
        return 0

    try:
        raw = json.loads(metadata_file.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return 0

    videos = raw.get("videos", raw) if isinstance(raw, dict) else {}
    if not isinstance(videos, dict):
        return 0

    keys = {
        rel_path,
        rel_path.replace("/", "\\"),
        file_name,
    }
    removed = 0
    for key in list(keys):
        if key in videos:
            videos.pop(key, None)
            removed += 1

    if removed:
        if isinstance(raw, dict) and "videos" in raw:
            raw["videos"] = videos
            metadata_file.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        else:
            metadata_file.write_text(json.dumps(videos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return removed


def scan_videos(roots: list[Path], ffmpeg: Path) -> list[dict[str, object]]:
    videos: list[dict[str, object]] = []
    seen: set[Path] = set()
    metadata = load_video_metadata()

    for root in roots:
        root = root.resolve()
        if not root.exists():
            continue

        for path in root.rglob("*.mp4"):
            path = path.resolve()
            if path in seen or "partial_movie_files" in path.parts:
                continue
            if not is_inside(path, PROJECT_ROOT):
                continue

            seen.add(path)
            stat = path.stat()
            rel = path.relative_to(PROJECT_ROOT).as_posix()
            probe = probe_video(path, ffmpeg)
            meta = metadata_for(rel, path.name, metadata)
            cover_path = resolve_metadata_cover(meta) or generate_poster(
                path, ffmpeg, probe.get("duration_seconds") if isinstance(probe.get("duration_seconds"), float) else None
            )
            tags = meta.get("tags", [])
            if not isinstance(tags, list):
                tags = []
            chapters = normalize_chapters(meta.get("chapters"))
            videos.append(
                {
                    "id": encode_relpath(path),
                    "name": meta.get("title") or path.stem,
                    "title": meta.get("title") or path.stem,
                    "description": meta.get("description") or "还没有介绍文案。可以在 data/videos.json 里补充这个视频的核心问题、观看收获和适用场景。",
                    "topic": meta.get("topic") or "未分类",
                    "tags": [str(tag) for tag in tags],
                    "status": meta.get("status") or ("成片" if "/exports/final/" in f"/{rel}" else "渲染片段"),
                    "priority": int(meta.get("priority") or 0),
                    "file": path.name,
                    "path": rel,
                    "url": f"/media/{encode_relpath(path)}",
                    "posterUrl": asset_url(cover_path),
                    "posterPath": cover_path.relative_to(PROJECT_ROOT).as_posix() if cover_path else None,
                    "size": stat.st_size,
                    "sizeLabel": human_size(stat.st_size),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                    "duration": probe["duration"],
                    "durationSeconds": probe.get("duration_seconds"),
                    "hasAudio": probe["has_audio"],
                    "chapters": chapters,
                }
            )

    return sorted(videos, key=lambda item: (item["priority"], item["modified"]), reverse=True)


def index_html() -> bytes:
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>VideoMaker 赛博数学动画控制台</title>
  <style>
    :root {
      --bg: #06101a;
      --bg-deep: #02070d;
      --ink: #e9fbff;
      --soft: #a8c9d4;
      --muted: #5d7f8d;
      --panel: rgba(4, 18, 30, 0.78);
      --panel-2: rgba(3, 14, 24, 0.88);
      --line: rgba(111, 230, 255, 0.18);
      --accent: #26d9ff;
      --accent-ink: #03131b;
      --accent-soft: rgba(38, 217, 255, 0.14);
      --ok: #78f3bd;
      --danger: #ff6f7c;
      --danger-soft: rgba(255, 111, 124, 0.15);
      --amber: var(--accent);
      --mint: var(--ok);
      --rose: var(--danger);
      --blue: var(--accent);
      --shadow: 0 28px 86px rgba(0, 8, 20, 0.48);
      --inner-edge: inset 0 1px 0 rgba(233, 251, 255, 0.09);
    }

    * { box-sizing: border-box; }
    html { color-scheme: dark; }

    body {
      margin: 0;
      color: var(--ink);
      font-family: "Geist", "Satoshi", "Microsoft YaHei UI", "Noto Sans SC", sans-serif;
      background:
        linear-gradient(rgba(111, 230, 255, 0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(111, 230, 255, 0.03) 1px, transparent 1px),
        radial-gradient(circle at 12% 10%, rgba(38, 217, 255, 0.24), transparent 34rem),
        radial-gradient(circle at 86% 6%, rgba(120, 243, 189, 0.13), transparent 32rem),
        radial-gradient(circle at 50% 100%, rgba(38, 217, 255, 0.10), transparent 42rem),
        var(--bg);
      background-size: 48px 48px, 48px 48px, auto, auto, auto, auto;
      min-height: 100dvh;
      overflow-x: hidden;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background:
        linear-gradient(112deg, transparent 0 39%, rgba(38, 217, 255, 0.12) 39.3% 39.7%, transparent 40.2% 100%),
        linear-gradient(18deg, transparent 0 62%, rgba(120, 243, 189, 0.055) 62.2% 62.5%, transparent 63% 100%),
        radial-gradient(circle at 50% -16%, rgba(233, 251, 255, 0.10), transparent 42rem);
      opacity: 0.88;
    }

    body::after {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background: repeating-linear-gradient(
        180deg,
        rgba(233, 251, 255, 0.025) 0,
        rgba(233, 251, 255, 0.025) 1px,
        transparent 1px,
        transparent 6px
      );
      opacity: 0.34;
    }

    .page {
      position: relative;
      width: min(1960px, calc(100vw - 24px));
      margin: 0 auto;
      padding: 18px 0 34px;
    }

    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(320px, 520px);
      gap: 22px;
      align-items: center;
      padding: 14px 0 18px;
    }

    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      color: var(--amber);
      font-family: "Geist Mono", "Cascadia Code", "Consolas", monospace;
      font-size: 12px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
    }

    .eyebrow::before {
      content: "";
      width: 46px;
      height: 1px;
      background: linear-gradient(90deg, var(--amber), transparent);
    }

    h1 {
      margin: 8px 0 10px;
      max-width: 960px;
      font-size: clamp(38px, 5.2vw, 86px);
      line-height: 0.94;
      letter-spacing: -0.065em;
      text-wrap: balance;
    }

    .subtitle {
      margin: 0;
      max-width: 900px;
      color: var(--soft);
      line-height: 1.8;
      font-size: 15.5px;
    }

    code {
      color: var(--mint);
      background: rgba(94, 234, 212, 0.09);
      border: 1px solid rgba(94, 234, 212, 0.14);
      border-radius: 8px;
      padding: 2px 6px;
    }

    .stats {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      align-self: stretch;
    }

    .metric {
      border: 1px solid var(--line);
      border-radius: 24px;
      background:
        linear-gradient(180deg, rgba(111, 230, 255, 0.10), rgba(111, 230, 255, 0.025)),
        rgba(2, 7, 13, 0.34);
      padding: 15px 16px;
      box-shadow: var(--inner-edge);
    }

    .metric strong {
      display: block;
      font-size: 28px;
      line-height: 1;
      letter-spacing: -0.05em;
      color: var(--accent);
      text-shadow: 0 0 18px rgba(38, 217, 255, 0.26);
    }

    .metric span {
      display: block;
      margin-top: 7px;
      color: var(--muted);
      font-size: 12px;
    }

    .console {
      display: grid;
      grid-template-columns: minmax(0, 1fr) clamp(340px, 22vw, 430px);
      gap: 18px;
      align-items: stretch;
    }

    .stage, .rail {
      border: 1px solid var(--line);
      box-shadow: var(--shadow);
      overflow: hidden;
      backdrop-filter: blur(20px);
    }

    .stage {
      position: relative;
      min-height: calc(100dvh - 184px);
      border-radius: 36px;
      background:
        radial-gradient(circle at 16% 0%, rgba(38, 217, 255, 0.18), transparent 31rem),
        linear-gradient(145deg, rgba(111, 230, 255, 0.10), rgba(111, 230, 255, 0.024)),
        var(--panel);
      box-shadow: var(--shadow), var(--inner-edge);
    }

    .stage::before,
    .rail::before {
      content: "";
      position: absolute;
      inset: 12px;
      border: 1px solid rgba(38, 217, 255, 0.08);
      border-radius: inherit;
      pointer-events: none;
    }

    .stage-inner {
      padding: clamp(15px, 1.5vw, 24px);
    }

    .player-chrome {
      border: 1px solid rgba(255, 255, 255, 0.16);
      border-radius: 28px;
      background: var(--bg-deep);
      overflow: hidden;
      box-shadow: 0 24px 62px rgba(0, 8, 20, 0.58), 0 0 0 1px rgba(38, 217, 255, 0.08), var(--inner-edge);
    }

    .chrome-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 14px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.09);
      color: var(--muted);
      font-family: "Geist Mono", "Cascadia Code", "Consolas", monospace;
      font-size: 11px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }

    .dots {
      display: flex;
      gap: 7px;
    }

    .dots span {
      width: 10px;
      height: 10px;
      border-radius: 999px;
      background: var(--rose);
    }

    .dots span:nth-child(2) { background: var(--amber); }
    .dots span:nth-child(3) { background: var(--mint); }

    .player-wrap {
      background:
        linear-gradient(135deg, rgba(38, 217, 255, 0.10), transparent 28%),
        radial-gradient(circle at 60% 40%, rgba(120, 243, 189, 0.07), transparent 34rem),
        var(--bg-deep);
    }

    video {
      width: 100%;
      display: block;
      background: var(--bg-deep);
    }

    .stage-video {
      aspect-ratio: 16 / 9;
      object-fit: contain;
      max-height: min(68dvh, 720px);
      min-height: 360px;
    }

    .featured-meta {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(210px, 340px);
      gap: clamp(16px, 2vw, 28px);
      padding: 20px 4px 2px;
      align-items: start;
    }

    .kicker {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 10px;
    }

    .featured-meta h2 {
      margin: 0 0 12px;
      font-size: clamp(26px, 2.9vw, 46px);
      line-height: 1.05;
      letter-spacing: -0.045em;
      word-break: break-word;
    }

    .description {
      margin: 0 0 12px;
      max-width: 980px;
      color: var(--soft);
      line-height: 1.85;
      font-size: 15px;
    }

    .path {
      margin: 0;
      color: var(--muted);
      font-family: "Geist Mono", "Cascadia Code", "Consolas", monospace;
      font-size: 12px;
      line-height: 1.7;
      word-break: break-all;
    }

    .meta-row, .tag-row {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .meta-row {
      justify-content: flex-start;
      align-content: start;
      max-width: 360px;
      padding-top: 2px;
    }

    .tag-row {
      margin-top: 12px;
    }

    .badge, .tag {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 999px;
      padding: 7px 10px;
      background: rgba(255, 255, 255, 0.06);
      color: var(--soft);
      font-size: 12px;
      white-space: nowrap;
      box-shadow: var(--inner-edge);
    }

    .tag {
      color: var(--accent);
      background: var(--accent-soft);
      border-color: rgba(38, 217, 255, 0.24);
    }

    .topic {
      color: var(--accent-ink);
      background: var(--amber);
      border-color: transparent;
    }

    .delete-video {
      width: 100%;
      min-height: 44px;
      display: inline-flex;
      justify-content: center;
      align-items: center;
      gap: 9px;
      border: 1px solid rgba(255, 111, 124, 0.58);
      border-radius: 16px;
      padding: 11px 14px;
      color: #ffecef;
      background:
        linear-gradient(135deg, rgba(255, 111, 124, 0.28), rgba(255, 111, 124, 0.10)),
        rgba(255, 111, 124, 0.08);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08), 0 0 22px rgba(255, 111, 124, 0.10);
      cursor: pointer;
      font: inherit;
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.02em;
      transition: transform 180ms cubic-bezier(0.16, 1, 0.3, 1), border-color 180ms ease, background 180ms ease, box-shadow 180ms ease;
    }

    .delete-video::before {
      content: "";
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: var(--danger);
      box-shadow: 0 0 14px rgba(255, 111, 124, 0.48);
    }

    .delete-video:hover {
      border-color: rgba(255, 111, 124, 0.86);
      background:
        linear-gradient(135deg, rgba(255, 111, 124, 0.36), rgba(255, 111, 124, 0.14)),
        rgba(255, 111, 124, 0.10);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.10), 0 0 30px rgba(255, 111, 124, 0.18);
      transform: translateY(-1px);
    }

    .chapter-panel {
      margin: 12px 2px 0;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 22px;
      padding: 12px;
      background:
        linear-gradient(135deg, rgba(38, 217, 255, 0.12), rgba(120, 243, 189, 0.045)),
        rgba(255, 255, 255, 0.035);
      box-shadow: var(--inner-edge);
    }

    .chapter-head {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 12px;
      margin-bottom: 10px;
    }

    .chapter-head strong {
      font-size: 14px;
      letter-spacing: -0.02em;
    }

    .chapter-head span {
      color: var(--muted);
      font-size: 12px;
      font-family: "Geist Mono", "Cascadia Code", "Consolas", monospace;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .chapter-list {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 8px;
    }

    .chapter-btn {
      position: relative;
      overflow: hidden;
      min-height: 58px;
      border: 1px solid rgba(255, 255, 255, 0.11);
      border-radius: 15px;
      padding: 9px 9px 10px;
      color: var(--soft);
      background: rgba(0, 0, 0, 0.18);
      cursor: pointer;
      text-align: left;
      font: inherit;
      transition: transform 180ms cubic-bezier(0.16, 1, 0.3, 1), border-color 180ms ease, background 180ms ease;
    }

    .chapter-btn:hover {
      transform: translateY(-1px);
      border-color: rgba(38, 217, 255, 0.55);
      background: rgba(255, 255, 255, 0.075);
    }

    .chapter-btn.active {
      color: var(--ink);
      border-color: rgba(38, 217, 255, 0.78);
      background: rgba(38, 217, 255, 0.12);
      box-shadow: inset 0 0 0 1px rgba(38, 217, 255, 0.24);
    }

    .chapter-label {
      display: block;
      margin-bottom: 4px;
      font-size: 12px;
      line-height: 1.32;
      font-weight: 700;
    }

    .chapter-time {
      display: block;
      color: var(--muted);
      font-family: "Geist Mono", "Cascadia Code", "Consolas", monospace;
      font-size: 10px;
    }

    .chapter-track {
      display: block;
      position: absolute;
      left: 9px;
      right: 9px;
      bottom: 7px;
      height: 3px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.12);
    }

    .chapter-fill {
      display: block;
      width: 0%;
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--accent), var(--ok));
      transition: width 120ms linear;
    }

    .rail {
      position: relative;
      border-radius: 32px;
      background:
        linear-gradient(180deg, rgba(111, 230, 255, 0.08), rgba(111, 230, 255, 0.024)),
        var(--panel-2);
      min-height: calc(100dvh - 184px);
      display: flex;
      flex-direction: column;
      box-shadow: var(--shadow), var(--inner-edge);
    }

    .rail-head {
      padding: 15px;
      border-bottom: 1px solid var(--line);
    }

    .rail-title {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      margin-bottom: 12px;
    }

    .rail-title h2 {
      margin: 0;
      font-size: 23px;
      letter-spacing: -0.04em;
    }

    .live-dot {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      color: var(--mint);
      font-size: 11px;
      font-family: "Geist Mono", "Cascadia Code", "Consolas", monospace;
    }

    .live-dot::before {
      content: "";
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: var(--mint);
      box-shadow: 0 0 0 4px rgba(120, 243, 189, 0.12), 0 0 18px rgba(120, 243, 189, 0.18);
      animation: pulse 1.9s ease-in-out infinite;
    }

    .search-box {
      position: relative;
      display: block;
    }

    .search-box span {
      position: absolute;
      left: 13px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--muted);
      font-family: "Geist Mono", "Cascadia Code", "Consolas", monospace;
      font-size: 12px;
    }

    input {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 12px 13px 12px 37px;
      background: rgba(0, 0, 0, 0.22);
      color: var(--ink);
      font-size: 14px;
      outline: none;
      transition: border-color 160ms ease, box-shadow 160ms ease;
    }

    input:focus {
      border-color: rgba(38, 217, 255, 0.62);
      box-shadow: 0 0 0 4px rgba(38, 217, 255, 0.11);
    }

    .library {
      overflow: auto;
      padding: 12px;
      display: grid;
      gap: 10px;
      scrollbar-color: rgba(38, 217, 255, 0.45) rgba(255, 255, 255, 0.05);
    }

    .card-wrap {
      position: relative;
    }

    .card {
      width: 100%;
      min-height: 96px;
      display: grid;
      grid-template-columns: 116px minmax(0, 1fr);
      gap: 10px;
      text-align: left;
      border: 1px solid rgba(255, 255, 255, 0.10);
      border-radius: 22px;
      padding: 9px;
      color: inherit;
      background:
        linear-gradient(135deg, rgba(111, 230, 255, 0.07), rgba(111, 230, 255, 0.022)),
        rgba(0, 0, 0, 0.16);
      cursor: pointer;
      font: inherit;
      transition: transform 190ms cubic-bezier(0.16, 1, 0.3, 1), border-color 190ms ease, background 190ms ease;
      animation: rise-in 420ms cubic-bezier(0.16, 1, 0.3, 1) both;
      animation-delay: calc(var(--i, 0) * 42ms);
    }

    .card-delete {
      position: absolute;
      top: 10px;
      right: 10px;
      z-index: 2;
      border: 1px solid rgba(255, 111, 124, 0.64);
      border-radius: 12px;
      padding: 6px 10px;
      color: #ffecef;
      background: rgba(82, 20, 30, 0.84);
      box-shadow: 0 8px 24px rgba(0, 8, 20, 0.26);
      cursor: pointer;
      font: inherit;
      font-size: 12px;
      font-weight: 700;
      backdrop-filter: blur(10px);
      transition: background 160ms ease, border-color 160ms ease, transform 160ms ease;
    }

    .card-delete:hover {
      transform: translateY(-1px);
      background: rgba(193, 106, 98, 0.26);
      border-color: rgba(193, 106, 98, 0.78);
    }

    .card:hover {
      transform: translateY(-2px);
      border-color: rgba(38, 217, 255, 0.52);
      background: rgba(38, 217, 255, 0.075);
    }

    .card.active {
      border-color: var(--amber);
      box-shadow: inset 0 0 0 1px rgba(38, 217, 255, 0.30), 0 0 26px rgba(38, 217, 255, 0.08);
      background:
        linear-gradient(135deg, rgba(38, 217, 255, 0.14), rgba(120, 243, 189, 0.034)),
        rgba(0, 0, 0, 0.18);
    }

    .thumb {
      position: relative;
      overflow: hidden;
      border-radius: 15px;
      background: var(--bg-deep);
      aspect-ratio: 16 / 9;
      align-self: start;
    }

    .thumb video {
      height: 100%;
      object-fit: cover;
      opacity: 0.74;
      filter: saturate(1.08) contrast(1.04);
      transition: transform 240ms cubic-bezier(0.16, 1, 0.3, 1), opacity 200ms ease;
    }

    .card:hover .thumb video,
    .card.active .thumb video {
      opacity: 0.96;
      transform: scale(1.025);
    }

    .thumb::after {
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, transparent 45%, rgba(0,0,0,0.56));
    }

    .card h3 {
      margin: 0 0 6px;
      font-size: 15px;
      line-height: 1.24;
      letter-spacing: -0.02em;
      word-break: break-word;
    }

    .card-desc {
      margin: 0 0 8px;
      color: var(--soft);
      font-size: 12px;
      line-height: 1.55;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .card .meta {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      font-size: 11px;
      line-height: 1.5;
    }

    .card .badge {
      padding: 4px 7px;
      font-size: 11px;
    }

    .empty {
      margin: 0;
      padding: 28px;
      color: var(--muted);
      line-height: 1.8;
      border: 1px dashed rgba(111, 230, 255, 0.18);
      border-radius: 24px;
      background: rgba(111, 230, 255, 0.035);
    }

    .notice {
      position: fixed;
      right: 18px;
      bottom: 18px;
      max-width: min(420px, calc(100vw - 36px));
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 12px 14px;
      color: var(--ink);
      background: rgba(3, 14, 24, 0.92);
      box-shadow: 0 18px 50px rgba(0, 8, 20, 0.40), var(--inner-edge);
      backdrop-filter: blur(18px);
      opacity: 0;
      transform: translateY(12px);
      pointer-events: none;
      transition: opacity 180ms ease, transform 180ms cubic-bezier(0.16, 1, 0.3, 1);
    }

    .notice.show {
      opacity: 1;
      transform: translateY(0);
    }

    .loading-grid {
      display: grid;
      gap: 14px;
    }

    .skeleton-video,
    .skeleton-line,
    .skeleton-card {
      position: relative;
      overflow: hidden;
      border-radius: 18px;
      background: rgba(111, 230, 255, 0.075);
    }

    .skeleton-video {
      aspect-ratio: 16 / 9;
      min-height: 360px;
    }

    .skeleton-line {
      height: 14px;
      width: min(620px, 72%);
    }

    .skeleton-line.short {
      width: min(420px, 48%);
    }

    .skeleton-card {
      height: 104px;
      animation-delay: calc(var(--i, 0) * 80ms);
    }

    .skeleton-video::after,
    .skeleton-line::after,
    .skeleton-card::after {
      content: "";
      position: absolute;
      inset: 0;
      transform: translateX(-100%);
      background: linear-gradient(90deg, transparent, rgba(111, 230, 255, 0.20), transparent);
      animation: shimmer 1.45s ease-in-out infinite;
    }

    button:active {
      transform: translateY(1px) scale(0.99);
    }

    button:focus-visible,
    input:focus-visible {
      outline: 2px solid rgba(38, 217, 255, 0.72);
      outline-offset: 3px;
    }

    button:disabled {
      cursor: wait;
      opacity: 0.58;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.45; transform: scale(0.72); }
    }

    @keyframes shimmer {
      100% { transform: translateX(100%); }
    }

    @keyframes rise-in {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: 0.001ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition-duration: 0.001ms !important;
      }
    }

    @media (min-width: 1600px) {
      .console {
        grid-template-columns: minmax(0, 1fr) 380px;
      }
    }

    @media (max-width: 1120px) {
      .hero, .console {
        grid-template-columns: 1fr;
      }

      .stage, .rail {
        min-height: 0;
      }

      .stage-video {
        min-height: 0;
        max-height: none;
      }
    }

    @media (max-width: 680px) {
      .page {
        width: min(100vw - 16px, 1880px);
        padding-top: 10px;
      }

      .stats {
        grid-template-columns: 1fr;
      }

      .featured-meta {
        grid-template-columns: 1fr;
      }

      .meta-row {
        justify-content: flex-start;
        max-width: none;
      }

      .card {
        grid-template-columns: 92px minmax(0, 1fr);
      }
    }
  </style>
</head>
<body>
  <div class="page">
    <header class="hero">
      <div>
        <div class="eyebrow">Cyber Preview Deck</div>
        <h1>数学动画控制台</h1>
        <p class="subtitle">把正在迭代的成片、章节跳转、封面和元数据放进一个冷色 HUD 审片界面。主播放器负责判断节奏，右侧片库负责快速切换版本；标题、简介、主题和标签来自 <code>data/videos.json</code>。</p>
      </div>
      <div class="stats" id="stats"></div>
    </header>

    <main class="console">
      <section class="stage" aria-label="当前播放视频">
        <div class="stage-inner" id="stage"></div>
      </section>

      <aside class="rail" aria-label="视频片库">
        <div class="rail-head">
        <div class="rail-title">
          <h2>片库</h2>
          <span class="live-dot">LIVE SCAN</span>
        </div>
        <label class="search-box">
          <span>⌕</span>
          <input id="search" placeholder="搜索标题、简介、标签或路径" autocomplete="off">
          </label>
        </div>
        <div class="library" id="library"></div>
      </aside>
    </main>
  </div>
  <div class="notice" id="notice" role="status" aria-live="polite"></div>

  <script>
    const state = { videos: [], filtered: [], active: 0 };
    const library = document.querySelector("#library");
    const stage = document.querySelector("#stage");
    const stats = document.querySelector("#stats");
    const search = document.querySelector("#search");
    const notice = document.querySelector("#notice");

    function esc(value) {
      return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
      })[char]);
    }

    function formatModified(value) {
      if (!value) return "未知时间";
      return value.replace("T", " ");
    }

    function formatCompactDate(value) {
      if (!value) return "未知";
      return value.replace("T", " ").slice(5, 16);
    }

    function formatBytes(value) {
      let size = Number(value) || 0;
      const units = ["B", "KB", "MB", "GB"];
      for (const unit of units) {
        if (size < 1024 || unit === units[units.length - 1]) {
          return unit === "B" ? `${Math.round(size)} B` : `${size.toFixed(1)} ${unit}`;
        }
        size /= 1024;
      }
      return "0 B";
    }

    function formatClock(value) {
      const seconds = Math.max(0, Number(value) || 0);
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const secs = Math.floor(seconds % 60).toString().padStart(2, "0");
      if (hours > 0) return `${hours}:${minutes.toString().padStart(2, "0")}:${secs}`;
      return `${minutes}:${secs}`;
    }

    function tags(video) {
      return Array.isArray(video.tags) ? video.tags : [];
    }

    function chapters(video) {
      return Array.isArray(video.chapters) ? video.chapters : [];
    }

    function posterAttr(video) {
      return video.posterUrl ? ` poster="${esc(video.posterUrl)}"` : "";
    }

    function renderLoading() {
      stats.innerHTML = `
        <div class="metric"><strong>...</strong><span>扫描视频</span></div>
        <div class="metric"><strong>...</strong><span>读取元数据</span></div>
        <div class="metric"><strong>...</strong><span>读取章节</span></div>
      `;
      stage.innerHTML = `
        <div class="loading-grid" aria-label="加载中">
          <div class="skeleton-video"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line short"></div>
        </div>
      `;
      library.innerHTML = [0, 1, 2, 3].map(index => `<div class="skeleton-card" style="--i:${index}"></div>`).join("");
    }

    function chapterMarkup(video) {
      const items = chapters(video);
      if (!items.length) return "";
      const buttons = items.map((chapter, index) => {
        const start = Number(chapter.start) || 0;
        const nextStart = items[index + 1] ? Number(items[index + 1].start) : Number(video.durationSeconds || chapter.end || 0);
        const end = Number(chapter.end || nextStart || 0);
        const endAttr = end > start ? ` data-chapter-end="${end}"` : "";
        const timeLabel = end > start ? `${formatClock(start)} - ${formatClock(end)}` : formatClock(start);
        return `
          <button class="chapter-btn" type="button" data-chapter-start="${start}"${endAttr}>
            <span class="chapter-label">${esc(chapter.title || ("段落 " + (index + 1)))}</span>
            <span class="chapter-time">${timeLabel}</span>
            <span class="chapter-track"><span class="chapter-fill"></span></span>
          </button>
        `;
      }).join("");
      return `
        <section class="chapter-panel" aria-label="章节进度">
          <div class="chapter-head">
            <strong>章节进度</strong>
            <span>点击跳转</span>
          </div>
          <div class="chapter-list">${buttons}</div>
        </section>
      `;
    }

    function bindChapterControls(video) {
      const player = stage.querySelector(".stage-video");
      const buttons = Array.from(stage.querySelectorAll("[data-chapter-start]"));
      if (!player || !buttons.length) return;

      const update = () => {
        const now = player.currentTime || 0;
        const fallbackEnd = Number(video.durationSeconds || player.duration || 0);
        buttons.forEach((button, index) => {
          const start = Number(button.dataset.chapterStart) || 0;
          const nextStart = buttons[index + 1] ? Number(buttons[index + 1].dataset.chapterStart) : fallbackEnd;
          const end = Number(button.dataset.chapterEnd || nextStart || fallbackEnd || start);
          const active = now >= start && (now < end || index === buttons.length - 1);
          const span = Math.max(0.001, end - start);
          const progress = active ? Math.min(100, Math.max(0, ((now - start) / span) * 100)) : now >= end ? 100 : 0;
          button.classList.toggle("active", active);
          const fill = button.querySelector(".chapter-fill");
          if (fill) fill.style.width = `${progress}%`;
        });
      };

      buttons.forEach(button => {
        button.addEventListener("click", () => {
          const target = Number(button.dataset.chapterStart) || 0;
          player.currentTime = target;
          player.play().catch(() => {});
          update();
        });
      });
      player.addEventListener("timeupdate", update);
      player.addEventListener("loadedmetadata", update);
      update();
    }

    async function deleteVideo(video) {
      const title = video.title || video.name || video.file;
      const confirmed = window.confirm(`确定要删除这个本地视频文件吗？\n\n${title}\n${video.path}\n\n这个操作会从磁盘删除 MP4 文件。`);
      if (!confirmed) return;

      const player = stage.querySelector(".stage-video");
      if (player) player.pause();
      const deleteButtons = document.querySelectorAll(`[data-delete-video="${video.id}"], [data-delete-id="${video.id}"]`);
      deleteButtons.forEach(button => {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.textContent = "删除中";
      });

      try {
        const response = await fetch(`/api/videos/${encodeURIComponent(video.id)}`, { method: "DELETE" });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) {
          showNotice(payload.error || "删除失败。");
          deleteButtons.forEach(button => {
            button.disabled = false;
            button.textContent = button.dataset.originalText || "删除";
          });
          return;
        }
      } catch (error) {
        showNotice(`删除失败：${error}`);
        deleteButtons.forEach(button => {
          button.disabled = false;
          button.textContent = button.dataset.originalText || "删除";
        });
        return;
      }

      state.videos = state.videos.filter(item => item.id !== video.id);
      applyFilter();
      showNotice("本地视频文件已删除。");
    }

    function bindDeleteButton(video) {
      const button = stage.querySelector("[data-delete-video]");
      if (!button) return;
      button.addEventListener("click", event => {
        event.preventDefault();
        deleteVideo(video).catch(error => {
          window.alert(`删除失败：${error}`);
        });
      });
    }

    function renderStats() {
      const total = state.videos.length;
      const totalSize = state.videos.reduce((sum, video) => sum + Number(video.size || 0), 0);
      const latest = state.videos.reduce((best, video) => {
        if (!best) return video;
        return String(video.modified || "") > String(best.modified || "") ? video : best;
      }, null);
      stats.innerHTML = `
        <div class="metric"><strong>${total}</strong><span>本地视频</span></div>
        <div class="metric"><strong>${formatBytes(totalSize)}</strong><span>总容量</span></div>
        <div class="metric"><strong>${formatCompactDate(latest && latest.modified)}</strong><span>最近更新</span></div>
      `;
    }

    function renderStage(video) {
      if (!video) {
        stage.innerHTML = '<p class="empty">还没有找到 MP4。先渲染一个 Manim 场景，或把成片放到 <code>topics/&lt;主题&gt;/exports/final</code>。</p>';
        return;
      }
      const tagHtml = tags(video).map(tag => `<span class="tag">${esc(tag)}</span>`).join("");
      stage.innerHTML = `
        <div class="player-chrome">
          <div class="chrome-top">
            <div class="dots"><span></span><span></span><span></span></div>
            <span>Preview Monitor</span>
          </div>
          <div class="player-wrap">
            <video class="stage-video" src="${video.url}"${posterAttr(video)} controls preload="metadata"></video>
          </div>
        </div>
        ${chapterMarkup(video)}
        <div class="featured-meta">
          <div>
            <div class="kicker">
              <span class="badge topic">${esc(video.topic || "未分类")}</span>
              <span class="badge">${esc(video.status || "渲染片段")}</span>
            </div>
            <h2>${esc(video.title || video.name)}</h2>
            <p class="description">${esc(video.description)}</p>
            <p class="path">${esc(video.path)}</p>
            <div class="tag-row">${tagHtml}</div>
          </div>
          <div class="meta-row">
            <span class="badge">${esc(video.duration || "未知时长")}</span>
            <span class="badge">${esc(video.sizeLabel)}</span>
            <span class="badge">${esc(formatModified(video.modified))}</span>
            <button class="delete-video" type="button" data-delete-video="${esc(video.id)}">删除本地视频</button>
          </div>
        </div>
      `;
      bindChapterControls(video);
      bindDeleteButton(video);
    }

    function renderLibrary() {
      if (!state.filtered.length) {
        library.innerHTML = '<p class="empty">没有匹配的视频。换个关键词，或者先生成一个新片段。</p>';
        renderStage(null);
        return;
      }
      library.innerHTML = state.filtered.map((video, index) => `
        <div class="card-wrap">
          <button class="card ${index === state.active ? 'active' : ''}" data-index="${index}" style="--i:${index}" type="button">
            <div class="thumb">
              <video src="${video.url}"${posterAttr(video)} preload="metadata" muted playsinline></video>
            </div>
            <div>
              <h3>${esc(video.title || video.name)}</h3>
              <p class="card-desc">${esc(video.description)}</p>
              <div class="meta">
                <span class="badge">${esc(video.duration || "未知时长")}</span>
                <span class="badge">${esc(video.topic || "未分类")}</span>
              </div>
            </div>
          </button>
          <button class="card-delete" type="button" data-delete-index="${index}" data-delete-id="${esc(video.id)}">删除文件</button>
        </div>
      `).join("");

      library.querySelectorAll(".card").forEach(card => {
        card.addEventListener("click", () => {
          state.active = Number(card.dataset.index);
          renderStage(state.filtered[state.active]);
          renderLibrary();
        });
      });
      library.querySelectorAll(".card-delete").forEach(button => {
        button.addEventListener("click", event => {
          event.preventDefault();
          event.stopPropagation();
          const video = state.filtered[Number(button.dataset.deleteIndex)];
          if (!video) return;
          deleteVideo(video).catch(error => {
            window.alert(`删除失败：${error}`);
          });
        });
      });
      renderStage(state.filtered[state.active] || state.filtered[0]);
    }

    function applyFilter() {
      const q = search.value.trim().toLowerCase();
      state.filtered = state.videos.filter(video => {
        const haystack = [
          video.title,
          video.name,
          video.description,
          video.file,
          video.path,
          video.topic,
          video.status,
          ...tags(video)
        ].map(value => String(value || "").toLowerCase());
        return !q || haystack.some(value => value.includes(q));
      });
      state.active = 0;
      renderLibrary();
    }

    async function boot() {
      const response = await fetch("/api/videos");
      state.videos = await response.json();
      state.filtered = state.videos;
      renderStats();
      renderLibrary();
    }

    search.addEventListener("input", applyFilter);
    renderLoading();
    boot().catch(error => {
      stage.innerHTML = `<p class="empty">加载失败：${esc(error)}</p>`;
    });
  </script>
</body>
</html>
""".encode("utf-8")


class VideoGalleryHandler(BaseHTTPRequestHandler):
    server_version = "VideoMakerGallery/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path

        if route == "/" or route == "/index.html":
            self.send_bytes(index_html(), "text/html; charset=utf-8")
            return

        if route == "/api/videos":
            payload = json.dumps(self.server.scan(), ensure_ascii=False).encode("utf-8")
            self.send_bytes(payload, "application/json; charset=utf-8")
            return

        if route == "/health":
            self.send_bytes(b"ok\n", "text/plain; charset=utf-8")
            return

        if route.startswith("/media/"):
            self.send_media(route.removeprefix("/media/"))
            return

        if route.startswith("/asset/"):
            self.send_asset(route.removeprefix("/asset/"))
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path

        if route.startswith("/api/videos/"):
            self.delete_video(route.removeprefix("/api/videos/"))
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def log_message(self, format: str, *args: object) -> None:
        sys.stderr.write("%s - %s\n" % (self.log_date_time_string(), format % args))

    def send_bytes(self, payload: bytes, content_type: str) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def send_json(self, payload: dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_media(self, media_id: str) -> None:
        try:
            path = decode_relpath(unquote(media_id))
        except Exception:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid media id")
            return

        if not path.exists() or path.suffix.lower() != ".mp4":
            self.send_error(HTTPStatus.NOT_FOUND, "Media not found")
            return

        file_size = path.stat().st_size
        start = 0
        end = file_size - 1
        status = HTTPStatus.OK
        range_header = self.headers.get("Range")

        if range_header:
            match = re.match(r"bytes=(\d*)-(\d*)", range_header)
            if match:
                if match.group(1):
                    start = int(match.group(1))
                if match.group(2):
                    end = int(match.group(2))
                end = min(end, file_size - 1)
                status = HTTPStatus.PARTIAL_CONTENT

        if start > end or start >= file_size:
            self.send_error(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
            return

        content_type = mimetypes.guess_type(path.name)[0] or "video/mp4"
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        if status == HTTPStatus.PARTIAL_CONTENT:
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.end_headers()

        with path.open("rb") as file:
            file.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = file.read(min(1024 * 1024, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def send_asset(self, asset_id: str) -> None:
        try:
            path = decode_relpath(unquote(asset_id))
        except Exception:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid asset id")
            return

        if not path.exists() or path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            self.send_error(HTTPStatus.NOT_FOUND, "Asset not found")
            return

        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        payload = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def delete_video(self, media_id: str) -> None:
        try:
            path = decode_relpath(unquote(media_id))
        except Exception:
            self.send_json({"error": "Invalid media id"}, HTTPStatus.BAD_REQUEST)
            return

        roots = [root.resolve() for root in self.server.roots]
        if path.suffix.lower() != ".mp4" or not any(is_inside(path, root) for root in roots):
            self.send_json({"error": "Only local MP4 files inside configured video roots can be deleted."}, HTTPStatus.FORBIDDEN)
            return

        if not path.exists():
            self.send_json({"error": "Media not found"}, HTTPStatus.NOT_FOUND)
            return

        rel = path.relative_to(PROJECT_ROOT).as_posix()
        size = path.stat().st_size
        poster = generated_poster_path(path)
        removed_poster = False

        try:
            path.unlink()
            if poster.exists():
                poster.unlink()
                removed_poster = True
            removed_metadata = remove_video_metadata(rel, path.name)
        except PermissionError:
            self.send_json({"error": "The file is currently in use. Stop playback and try again."}, HTTPStatus.CONFLICT)
            return
        except OSError as exc:
            self.send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self.send_json(
            {
                "deleted": rel,
                "size": size,
                "posterRemoved": removed_poster,
                "metadataRemoved": removed_metadata,
            }
        )


class VideoGalleryServer(ThreadingHTTPServer):
    def __init__(self, address: tuple[str, int], roots: list[Path], ffmpeg: Path):
        super().__init__(address, VideoGalleryHandler)
        self.roots = roots
        self.ffmpeg = ffmpeg

    def scan(self) -> list[dict[str, object]]:
        return scan_videos(self.roots, self.ffmpeg)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve a local web gallery for generated videos.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind.")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind.")
    parser.add_argument(
        "--video-root",
        action="append",
        help="Directory to scan for MP4 files. Can be repeated.",
    )
    parser.add_argument("--ffmpeg", default=str(DEFAULT_FFMPEG), help="Path to ffmpeg executable.")
    parser.add_argument("--no-open", action="store_true", help="Do not open a browser automatically.")
    parser.add_argument("--list", action="store_true", help="List discovered videos as JSON and exit.")
    parser.add_argument("--pid-file", default=str(DEFAULT_PID_FILE), help="PID file for this server.")
    parser.add_argument("--stop", action="store_true", help="Stop a previously started gallery server.")
    return parser.parse_args()


def stop_server(pid_file: Path) -> None:
    if not pid_file.exists():
        raise SystemExit(f"No PID file found: {pid_file}")
    pid = int(pid_file.read_text(encoding="utf-8").strip())
    os.kill(pid, signal.SIGTERM)
    print(f"Stopped gallery server process: {pid}")


def main() -> None:
    args = parse_args()
    ffmpeg = Path(args.ffmpeg).resolve()
    roots = [Path(item).resolve() for item in args.video_root] if args.video_root else DEFAULT_VIDEO_ROOTS
    pid_file = Path(args.pid_file).resolve()

    if args.stop:
        stop_server(pid_file)
        return

    if args.list:
        print(json.dumps(scan_videos(roots, ffmpeg), ensure_ascii=False, indent=2))
        return

    server = VideoGalleryServer((args.host, args.port), roots, ffmpeg)
    host, port = server.server_address
    url = f"http://{host}:{port}/"
    pid_file.write_text(str(os.getpid()), encoding="utf-8")

    def cleanup(*_: object) -> None:
        if pid_file.exists():
            pid_file.unlink()
        server.server_close()
        raise SystemExit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print(f"Video gallery: {url}")
    print(f"Scanning: {', '.join(str(root) for root in roots)}")
    if not args.no_open:
        webbrowser.open(url)

    try:
        server.serve_forever()
    finally:
        if pid_file.exists():
            pid_file.unlink()


if __name__ == "__main__":
    main()
