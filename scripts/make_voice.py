import argparse
import asyncio
from pathlib import Path

import edge_tts


DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"


async def synthesize(args: argparse.Namespace) -> None:
    text = args.text
    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")

    if not text or not text.strip():
        raise SystemExit("No text provided. Use --text or --text-file.")

    media_path = Path(args.out)
    media_path.parent.mkdir(parents=True, exist_ok=True)

    communicate = edge_tts.Communicate(
        text=text,
        voice=args.voice,
        rate=args.rate,
        volume=args.volume,
        pitch=args.pitch,
    )

    submaker = edge_tts.SubMaker()
    with media_path.open("wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)

    if args.srt:
        srt_path = Path(args.srt)
        srt_path.parent.mkdir(parents=True, exist_ok=True)
        srt_path.write_text(submaker.get_srt(), encoding="utf-8-sig")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Mandarin narration audio and optional subtitles with edge-tts."
    )
    parser.add_argument("--text", help="Text to synthesize.")
    parser.add_argument("--text-file", help="UTF-8 text file to synthesize.")
    parser.add_argument("--out", default="topics/draft/audio/narration.mp3", help="Output audio path.")
    parser.add_argument("--srt", help="Optional SRT subtitle output path.")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="Voice name.")
    parser.add_argument("--rate", default="+0%", help="Speaking rate, for example +10% or -10%.")
    parser.add_argument("--volume", default="+0%", help="Volume, for example +0% or -10%.")
    parser.add_argument("--pitch", default="+0Hz", help="Pitch, for example +0Hz or -10Hz.")
    return parser.parse_args()


def main() -> None:
    asyncio.run(synthesize(parse_args()))


if __name__ == "__main__":
    main()
