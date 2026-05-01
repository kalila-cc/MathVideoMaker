import argparse
import re
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIO = PROJECT_ROOT / "topics" / "pythagorean" / "audio" / "demo.mp3"
DEFAULT_FFMPEG = PROJECT_ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"


def resolve_path(value: str | Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def manim_video_roots() -> list[Path]:
    roots: list[Path] = []
    topics = PROJECT_ROOT / "topics"
    if topics.exists():
        for topic in sorted(topics.iterdir()):
            if topic.is_dir():
                roots.append(topic / "exports" / "manim" / "videos")

    roots.append(PROJECT_ROOT / "exports" / "manim" / "videos")
    return roots


def latest_manim_video() -> Path:
    videos = []
    for root in manim_video_roots():
        if not root.exists():
            continue
        for path in root.rglob("*.mp4"):
            if "partial_movie_files" in path.parts:
                continue
            videos.append(path)

    if not videos:
        raise SystemExit("No Manim MP4 found under topics/*/exports/manim/videos or exports/manim/videos.")

    return max(videos, key=lambda item: item.stat().st_mtime)


def default_output_for(video: Path) -> Path:
    topic_root = topic_root_for(video)
    if topic_root:
        return topic_root / "exports" / "final" / f"{video.stem}_with_audio.mp4"
    return PROJECT_ROOT / "exports" / "final" / f"{video.stem}_with_audio.mp4"


def topic_root_for(path: Path) -> Path | None:
    topics = PROJECT_ROOT / "topics"
    try:
        rel = path.resolve().relative_to(topics.resolve())
    except ValueError:
        return None
    if not rel.parts:
        return None
    return topics / rel.parts[0]


def video_duration_seconds(video: Path, ffmpeg: Path) -> float | None:
    result = subprocess.run(
        [str(ffmpeg), "-hide_banner", "-i", str(video)],
        text=True,
        capture_output=True,
    )
    output = result.stderr + result.stdout
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", output)
    if not match:
        return None

    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Mux narration audio into a generated MP4 without re-encoding the video stream."
    )
    parser.add_argument("--video", help="Input MP4. Defaults to latest Manim video.")
    parser.add_argument("--audio", default=str(DEFAULT_AUDIO), help="Input narration audio.")
    parser.add_argument("--out", help="Output MP4. Prefer topics/<topic>/exports/final/<video>_with_audio.mp4.")
    parser.add_argument("--ffmpeg", default=str(DEFAULT_FFMPEG), help="Path to ffmpeg executable.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output if it exists.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    video = resolve_path(args.video) if args.video else latest_manim_video()
    audio = resolve_path(args.audio)
    output = resolve_path(args.out) if args.out else default_output_for(video)
    ffmpeg = resolve_path(args.ffmpeg)

    if not video.exists():
        raise SystemExit(f"Video not found: {video}")
    if not audio.exists():
        raise SystemExit(f"Audio not found: {audio}")
    if not ffmpeg.exists():
        raise SystemExit(f"FFmpeg not found: {ffmpeg}")
    if output.exists() and not args.overwrite:
        raise SystemExit(f"Output already exists. Use --overwrite: {output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    duration = video_duration_seconds(video, ffmpeg)

    command = [
        str(ffmpeg),
        "-y" if args.overwrite else "-n",
        "-i",
        str(video),
        "-i",
        str(audio),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
    ]

    if duration:
        # Keep the full video duration and trim longer narration. Shorter audio simply ends early.
        command.extend(["-t", f"{duration:.3f}"])

    command.append(str(output))

    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or "FFmpeg failed.")

    print(f"Created: {output}")


if __name__ == "__main__":
    main()
