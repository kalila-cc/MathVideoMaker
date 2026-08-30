from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from build_v5_final_timeline import parse_srt
from build_v5_final_video import FFMPEG, LOG_PATH, OUTPUT_PATH, TIMELINE_PATH, clip_path


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "topics" / "gacha-pity-probability"
REPORT_PATH = TOPIC / "exports" / "qa" / "v5_final_qa.json"
CURRENT_SOURCES = [
    TOPIC / "scenes" / "gacha_pity_probability_v1.py",
    TOPIC / "scenes" / "gacha_pity_probability_v4.py",
    TOPIC / "scenes" / "gacha_pity_probability_v5.py",
]


def run(command: list[str], *, accept_nonzero: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, encoding="utf-8")
    if result.returncode != 0 and not accept_nonzero:
        raise RuntimeError(result.stderr or result.stdout)
    return result


def probe(path: Path) -> str:
    result = run([str(FFMPEG), "-hide_banner", "-i", str(path)], accept_nonzero=True)
    return result.stderr


def main() -> None:
    timeline = json.loads(TIMELINE_PATH.read_text(encoding="utf-8"))
    expected_frames = int(timeline["total_frames"])
    scenes = timeline["scenes"]
    clips = [clip_path(scene) for scene in scenes]
    missing = [path for path in [OUTPUT_PATH, LOG_PATH, *clips] if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing QA inputs:\n" + "\n".join(map(str, missing)))

    newest_source_mtime = max(path.stat().st_mtime for path in CURRENT_SOURCES)
    stale_clips = [path for path in clips if path.stat().st_mtime <= newest_source_mtime]
    if stale_clips:
        raise ValueError("HD clips older than current source:\n" + "\n".join(map(str, stale_clips)))

    clip_reports = []
    for scene, path in zip(scenes, clips):
        media_info = probe(path)
        if not re.search(r"Video:.*1920x1080.*60 fps", media_info):
            raise ValueError(f"Unexpected HD video stream: {path}\n{media_info}")
        if re.search(r"Stream #\d+:\d+.*Audio:", media_info):
            raise ValueError(f"Scene unexpectedly has audio: {path}")
        decode = run([str(FFMPEG), "-v", "error", "-i", str(path), "-f", "null", "NUL"])
        clip_reports.append(
            {
                "scene": scene["name"],
                "path": str(path),
                "bytes": path.stat().st_size,
                "decode_exit_code": decode.returncode,
            }
        )

    final_info = probe(OUTPUT_PATH)
    if not re.search(r"Video:.*1920x1080.*60 fps", final_info):
        raise ValueError(f"Unexpected final video stream:\n{final_info}")
    if not re.search(r"Audio: aac.*48000 Hz, mono", final_info):
        raise ValueError(f"Unexpected final audio stream:\n{final_info}")

    decode = run([str(FFMPEG), "-v", "error", "-i", str(OUTPUT_PATH), "-f", "null", "NUL"])
    frame_result = run(
        [
            str(FFMPEG),
            "-v",
            "error",
            "-i",
            str(OUTPUT_PATH),
            "-map",
            "0:v:0",
            "-an",
            "-f",
            "null",
            "NUL",
            "-progress",
            "pipe:1",
        ]
    )
    frame_values = re.findall(r"^frame=(\d+)$", frame_result.stdout, flags=re.MULTILINE)
    if not frame_values:
        raise ValueError("FFmpeg frame progress did not report a final frame count")
    actual_frames = int(frame_values[-1])
    if actual_frames != expected_frames:
        raise ValueError(f"Frame mismatch: expected {expected_frames}, decoded {actual_frames}")

    final_srt = TOPIC / "audio" / "gacha_pity_probability_v5_final.srt"
    cues = parse_srt(final_srt)
    if len(cues) != int(timeline["cue_count"]):
        raise ValueError("Final SRT cue-count mismatch")
    for index, cue in enumerate(cues[:-1]):
        if cue.end_ms > cues[index + 1].start_ms:
            raise ValueError(f"Subtitle overlap at cue {index + 1}")
        if "\n" in cue.text:
            raise ValueError(f"Multiline subtitle at cue {index + 1}")

    encode_log = LOG_PATH.read_text(encoding="utf-8")
    font_match = re.search(
        r"fontselect: \(Smiley Sans Oblique,.*?\) -> SmileySans-Oblique",
        encode_log,
    )
    if not font_match:
        raise ValueError("Encode log does not prove SmileySans-Oblique font selection")

    loudness_result = run(
        [
            str(FFMPEG),
            "-hide_banner",
            "-i",
            str(OUTPUT_PATH),
            "-map",
            "0:a:0",
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
            "-f",
            "null",
            "NUL",
        ]
    )
    loudness_match = re.search(r"\{\s*\"input_i\".*?\}", loudness_result.stderr, re.DOTALL)
    if not loudness_match:
        raise ValueError("Could not parse loudness analysis")
    loudness = json.loads(loudness_match.group(0))
    integrated_lufs = float(loudness["input_i"])
    true_peak_db = float(loudness["input_tp"])
    if abs(integrated_lufs - (-16.0)) > 0.6:
        raise ValueError(f"Integrated loudness out of tolerance: {integrated_lufs} LUFS")
    if true_peak_db > -1.0:
        raise ValueError(f"True peak too high: {true_peak_db} dBTP")

    report = {
        "status": "pass",
        "output": str(OUTPUT_PATH),
        "bytes": OUTPUT_PATH.stat().st_size,
        "resolution": "1920x1080",
        "fps": 60,
        "frames": actual_frames,
        "duration_seconds": actual_frames / 60,
        "audio": "AAC 48000 Hz mono",
        "integrated_lufs": integrated_lufs,
        "true_peak_dbtp": true_peak_db,
        "subtitle_cues": len(cues),
        "subtitle_font": "SmileySans-Oblique",
        "full_decode_exit_code": decode.returncode,
        "clips": clip_reports,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(REPORT_PATH)
    print(json.dumps({key: value for key, value in report.items() if key != "clips"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
