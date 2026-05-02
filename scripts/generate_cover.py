import argparse
import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FFMPEG = PROJECT_ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
DEFAULT_METADATA_FILE = PROJECT_ROOT / "data" / "videos.json"


def resolve_path(value: str | Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def is_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def topic_root_for(path: Path) -> Path | None:
    topics = PROJECT_ROOT / "topics"
    try:
        rel = path.resolve().relative_to(topics.resolve())
    except ValueError:
        return None
    if not rel.parts:
        return None
    return topics / rel.parts[0]


def final_video_roots() -> list[Path]:
    roots: list[Path] = []
    topics = PROJECT_ROOT / "topics"
    if topics.exists():
        for topic in sorted(topics.iterdir()):
            if topic.is_dir():
                roots.append(topic / "exports" / "final")
    roots.append(PROJECT_ROOT / "exports" / "final")
    return roots


def latest_final_video() -> Path:
    videos: list[Path] = []
    for root in final_video_roots():
        if root.exists():
            videos.extend(path for path in root.rglob("*.mp4") if path.is_file())
    if not videos:
        raise SystemExit("No final MP4 found under topics/*/exports/final or exports/final.")
    return max(videos, key=lambda path: path.stat().st_mtime)


def default_output_for(video: Path, variant: str = "cover") -> Path:
    topic_root = topic_root_for(video)
    suffix = f"_{variant}" if variant else ""
    if topic_root:
        return topic_root / "exports" / "covers" / f"{video.stem}{suffix}.jpg"
    return PROJECT_ROOT / "exports" / "covers" / f"{video.stem}{suffix}.jpg"


def update_metadata(video: Path, primary_cover: Path, mobile_cover: Path | None, metadata_file: Path) -> None:
    if metadata_file.exists():
        raw = json.loads(metadata_file.read_text(encoding="utf-8-sig"))
    else:
        raw = {"videos": {}}

    if not isinstance(raw, dict):
        raw = {"videos": {}}
    videos = raw.setdefault("videos", {})
    if not isinstance(videos, dict):
        raw["videos"] = {}
        videos = raw["videos"]

    video_rel = video.relative_to(PROJECT_ROOT).as_posix()
    primary_rel = primary_cover.relative_to(PROJECT_ROOT).as_posix()
    mobile_rel = mobile_cover.relative_to(PROJECT_ROOT).as_posix() if mobile_cover else primary_rel
    item = videos.setdefault(video_rel, {})
    if not isinstance(item, dict):
        item = {}
        videos[video_rel] = item
    item["cover"] = primary_rel
    item["covers"] = {
        "desktop": primary_rel,
        "mobile": mobile_rel,
    }
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    metadata_file.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_cover(ffmpeg: Path, video: Path, output: Path, time: str, scale: int, overwrite: bool) -> None:
    if output.exists() and not overwrite:
        raise SystemExit(f"Output already exists. Use --overwrite: {output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        str(ffmpeg),
        "-y" if overwrite else "-n",
        "-ss",
        str(time),
        "-i",
        str(video),
        "-frames:v",
        "1",
        "-vf",
        f"scale={scale}:-1",
        "-q:v",
        "3",
        str(output),
    ]
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or "FFmpeg failed.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a local cover image from a video frame.")
    parser.add_argument("--video", help="Source MP4. Defaults to latest topic final video.")
    parser.add_argument("--mobile-video", help="Optional separate MP4 source for a requested platform variant.")
    parser.add_argument("--out", help="Primary cover output path. Alias for --desktop-out.")
    parser.add_argument("--desktop-out", help="Compatibility alias for the primary cover output path.")
    parser.add_argument("--mobile-out", help="Optional separate mobile/feed cover output path. Omit by default.")
    parser.add_argument("--time", default="0.100", help="Seek time in seconds, e.g. 0.100.")
    parser.add_argument("--scale", type=int, default=1280, help="Output width in pixels. Height keeps aspect ratio.")
    parser.add_argument("--desktop-scale", type=int, help="Compatibility alias for primary cover output width. Defaults to --scale.")
    parser.add_argument("--mobile-scale", type=int, default=720, help="Optional separate variant output width.")
    parser.add_argument("--ffmpeg", default=str(DEFAULT_FFMPEG), help="Path to ffmpeg executable.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output if it exists.")
    parser.add_argument("--update-metadata", action="store_true", help="Write cover and compatibility covers.desktop/mobile to data/videos.json.")
    parser.add_argument(
        "--metadata-video",
        help="Video entry to update in metadata. Use this when the cover is rendered from a separate cover scene.",
    )
    parser.add_argument("--metadata-file", default=str(DEFAULT_METADATA_FILE), help="Metadata JSON path for --update-metadata.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    video = resolve_path(args.video) if args.video else latest_final_video()
    mobile_video = resolve_path(args.mobile_video) if args.mobile_video else video
    metadata_video = resolve_path(args.metadata_video) if args.metadata_video else video
    primary_arg = args.desktop_out or args.out
    output = resolve_path(primary_arg) if primary_arg else default_output_for(video, "cover")
    mobile_output = resolve_path(args.mobile_out) if args.mobile_out else None
    ffmpeg = resolve_path(args.ffmpeg)
    metadata_file = resolve_path(args.metadata_file)

    if not video.exists():
        raise SystemExit(f"Video not found: {video}")
    if video.suffix.lower() != ".mp4":
        raise SystemExit(f"Input must be an MP4 file: {video}")
    if not mobile_video.exists():
        raise SystemExit(f"Mobile video not found: {mobile_video}")
    if mobile_video.suffix.lower() != ".mp4":
        raise SystemExit(f"Mobile input must be an MP4 file: {mobile_video}")
    if not is_inside(video, PROJECT_ROOT):
        raise SystemExit(f"Video must be inside the project: {video}")
    if not is_inside(mobile_video, PROJECT_ROOT):
        raise SystemExit(f"Mobile video must be inside the project: {mobile_video}")
    if not is_inside(metadata_video, PROJECT_ROOT):
        raise SystemExit(f"Metadata video must be inside the project: {metadata_video}")
    if not ffmpeg.exists():
        raise SystemExit(f"FFmpeg not found: {ffmpeg}")

    render_cover(ffmpeg, video, output, args.time, args.desktop_scale or args.scale, args.overwrite)
    if mobile_output:
        render_cover(ffmpeg, mobile_video, mobile_output, args.time, args.mobile_scale, args.overwrite)

    if args.update_metadata:
        update_metadata(metadata_video, output, mobile_output, metadata_file)

    print(f"Created: {output}")
    if mobile_output:
        print(f"Created: {mobile_output}")


if __name__ == "__main__":
    main()
