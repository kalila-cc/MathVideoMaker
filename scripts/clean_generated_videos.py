import argparse
import base64
import json
import shutil
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
METADATA_FILE = PROJECT_ROOT / "data" / "videos.json"
LEGACY_ALLOWED_ROOTS = [
    PROJECT_ROOT / "exports" / "final",
    PROJECT_ROOT / "exports" / "manim" / "videos",
    PROJECT_ROOT / "exports" / "posters",
    PROJECT_ROOT / "exports" / "covers",
]

VIDEO_SUFFIXES = {".mp4", ".mov", ".webm", ".gif"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}

PRESETS = {
    "old-astroid-iterations": [
        "exports/final/LadderAstroidEnvelope_with_audio.mp4",
        "exports/final/LadderAstroidEnvelope_v2_*.mp4",
        "exports/final/LadderAstroidEnvelope_v3_*.mp4",
        "exports/final/LadderAstroidEnvelope_v4_*.mp4",
        "exports/final/LadderAstroidEnvelope_v5_*.mp4",
        "topics/astroid-envelope/exports/final/LadderAstroidEnvelope_with_audio.mp4",
        "topics/astroid-envelope/exports/final/LadderAstroidEnvelope_v2_*.mp4",
        "topics/astroid-envelope/exports/final/LadderAstroidEnvelope_v3_*.mp4",
        "topics/astroid-envelope/exports/final/LadderAstroidEnvelope_v4_*.mp4",
        "topics/astroid-envelope/exports/final/LadderAstroidEnvelope_v5_*.mp4",
        "exports/manim/videos/astroid_envelope",
        "exports/manim/videos/astroid_envelope_v2",
        "exports/manim/videos/astroid_envelope_v3",
        "exports/manim/videos/astroid_envelope_v4",
        "exports/manim/videos/astroid_envelope_v5",
        "topics/astroid-envelope/exports/manim/videos/astroid_envelope",
        "topics/astroid-envelope/exports/manim/videos/astroid_envelope_v2",
        "topics/astroid-envelope/exports/manim/videos/astroid_envelope_v3",
        "topics/astroid-envelope/exports/manim/videos/astroid_envelope_v4",
        "topics/astroid-envelope/exports/manim/videos/astroid_envelope_v5",
        "exports/covers/LadderAstroidEnvelope_v5_cover.jpg",
        "topics/astroid-envelope/exports/covers/LadderAstroidEnvelope_v5_cover.jpg",
    ],
    "manim-partials": [
        "exports/manim/videos/**/partial_movie_files",
        "topics/*/exports/manim/videos/**/partial_movie_files",
    ],
}


def reconfigure_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def is_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def allowed_roots() -> list[Path]:
    roots = list(LEGACY_ALLOWED_ROOTS)
    topics = PROJECT_ROOT / "topics"
    if topics.exists():
        for topic in topics.iterdir():
            if not topic.is_dir():
                continue
            exports = topic / "exports"
            roots.extend(
                [
                    exports / "final",
                    exports / "manim" / "videos",
                    exports / "posters",
                    exports / "covers",
                ]
            )
    return roots


def ensure_safe_target(path: Path) -> Path:
    resolved = path.resolve()
    roots = allowed_roots()
    if not any(is_inside(resolved, root) for root in roots):
        raise ValueError(f"Refusing to touch path outside allowed export roots: {path}")
    if resolved in [root.resolve() for root in roots]:
        raise ValueError(f"Refusing to delete export root itself: {path}")
    return resolved


def expand_glob(pattern: str) -> list[Path]:
    normalized = pattern.replace("\\", "/")
    matches = list(PROJECT_ROOT.glob(normalized))
    return [ensure_safe_target(match) for match in matches]


def collect_targets(args: argparse.Namespace) -> list[Path]:
    patterns: list[str] = []
    for preset in args.preset:
        if preset not in PRESETS:
            raise SystemExit(f"Unknown preset: {preset}. Available presets: {', '.join(sorted(PRESETS))}")
        patterns.extend(PRESETS[preset])
    patterns.extend(args.glob)

    targets: dict[Path, Path] = {}
    for pattern in patterns:
        for path in expand_glob(pattern):
            targets[path] = path

    return sorted(targets, key=lambda item: (len(item.parts), item.as_posix()), reverse=True)


def path_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    total = 0
    for child in path.rglob("*"):
        if child.is_file():
            total += child.stat().st_size
    return total


def human_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{size} B"


def decode_generated_poster_target(path: Path) -> Path | None:
    if path.suffix.lower() not in IMAGE_SUFFIXES:
        return None
    try:
        padded = path.stem + "=" * (-len(path.stem) % 4)
        rel = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
    except Exception:
        return None
    target = (PROJECT_ROOT / rel).resolve()
    if not is_inside(target, PROJECT_ROOT):
        return None
    return target


def poster_roots() -> list[Path]:
    roots = [PROJECT_ROOT / "exports" / "posters"]
    topics = PROJECT_ROOT / "topics"
    if topics.exists():
        for topic in topics.iterdir():
            if topic.is_dir():
                roots.append(topic / "exports" / "posters")
    return roots


def collect_orphan_posters() -> list[Path]:
    orphans: list[Path] = []
    for poster_root in poster_roots():
        if not poster_root.exists():
            continue
        for poster in poster_root.iterdir():
            if not poster.is_file():
                continue
            target = decode_generated_poster_target(poster)
            if target and not target.exists():
                orphans.append(ensure_safe_target(poster))
    return sorted(orphans, key=lambda item: item.as_posix())


def delete_targets(targets: list[Path], execute: bool) -> tuple[int, int]:
    total_size = sum(path_size(path) for path in targets if path.exists())
    for path in targets:
        label = "DIR " if path.is_dir() else "FILE"
        print(f"{'DELETE' if execute else 'DRY'} {label} {path.relative_to(PROJECT_ROOT).as_posix()} ({human_size(path_size(path))})")
        if not execute:
            continue
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    return len(targets), total_size


def load_metadata() -> dict[str, object]:
    if not METADATA_FILE.exists():
        return {"videos": {}}
    return json.loads(METADATA_FILE.read_text(encoding="utf-8-sig"))


def prune_missing_metadata(execute: bool) -> int:
    raw = load_metadata()
    videos = raw.get("videos", raw) if isinstance(raw, dict) else {}
    if not isinstance(videos, dict):
        return 0

    missing: list[str] = []
    for key in list(videos.keys()):
        if not isinstance(key, str):
            continue
        candidate = (PROJECT_ROOT / key.replace("\\", "/")).resolve()
        if not is_inside(candidate, PROJECT_ROOT):
            continue
        if key.lower().endswith(tuple(VIDEO_SUFFIXES)) and not candidate.exists():
            missing.append(key)

    for key in missing:
        print(f"{'PRUNE' if execute else 'DRY'} META {key}")
        if execute:
            videos.pop(key, None)

    if execute and missing:
        if isinstance(raw, dict) and "videos" in raw:
            raw["videos"] = videos
            METADATA_FILE.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        else:
            METADATA_FILE.write_text(json.dumps(videos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return len(missing)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safely clean generated local video artifacts.")
    parser.add_argument(
        "--preset",
        action="append",
        default=[],
        help=f"Cleanup preset. Available: {', '.join(sorted(PRESETS))}",
    )
    parser.add_argument(
        "--glob",
        action="append",
        default=[],
        help="Additional project-relative glob to delete, limited to legacy exports roots or topics/<topic>/exports output roots.",
    )
    parser.add_argument("--delete-orphan-posters", action="store_true", help="Delete generated poster files whose source video no longer exists.")
    parser.add_argument("--prune-metadata", action="store_true", help="Remove data/videos.json entries for missing local video files.")
    parser.add_argument("--execute", action="store_true", help="Actually delete files. Without this flag the script only prints a dry-run.")
    return parser.parse_args()


def main() -> None:
    reconfigure_stdout()
    args = parse_args()

    targets = collect_targets(args)
    if args.delete_orphan_posters:
        targets.extend(collect_orphan_posters())
        targets = sorted({path: path for path in targets}.values(), key=lambda item: (len(item.parts), item.as_posix()), reverse=True)

    count, total_size = delete_targets(targets, args.execute)
    pruned = prune_missing_metadata(args.execute) if args.prune_metadata else 0

    mode = "deleted" if args.execute else "would delete"
    print(f"\nSummary: {mode} {count} target(s), {human_size(total_size)}. Metadata entries pruned: {pruned}.")
    if not args.execute:
        print("Dry-run only. Re-run with --execute to apply.")


if __name__ == "__main__":
    main()
