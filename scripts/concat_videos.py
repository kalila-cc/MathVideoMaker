import argparse
import subprocess
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FFMPEG = PROJECT_ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"


def resolve_path(value: str | Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Concatenate MP4 chapter videos with FFmpeg.")
    parser.add_argument("--out", required=True, help="Output MP4 path.")
    parser.add_argument("--ffmpeg", default=str(DEFAULT_FFMPEG), help="Path to ffmpeg executable.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output if it exists.")
    parser.add_argument("videos", nargs="+", help="Input MP4 files in order.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ffmpeg = resolve_path(args.ffmpeg)
    output = resolve_path(args.out)
    videos = [resolve_path(item) for item in args.videos]

    if not ffmpeg.exists():
        raise SystemExit(f"FFmpeg not found: {ffmpeg}")
    for video in videos:
        if not video.exists():
            raise SystemExit(f"Video not found: {video}")
    if output.exists() and not args.overwrite:
        raise SystemExit(f"Output already exists. Use --overwrite: {output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as file:
        list_path = Path(file.name)
        for video in videos:
            safe_path = video.as_posix().replace("'", r"'\''")
            file.write(f"file '{safe_path}'\n")

    try:
        command = [
            str(ffmpeg),
            "-y" if args.overwrite else "-n",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_path),
            "-c",
            "copy",
            str(output),
        ]
        result = subprocess.run(command, text=True, capture_output=True)
        if result.returncode != 0:
            raise SystemExit(result.stderr.strip() or "FFmpeg concat failed.")
    finally:
        list_path.unlink(missing_ok=True)

    print(f"Created: {output}")


if __name__ == "__main__":
    main()
