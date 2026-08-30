from __future__ import annotations

import json
import math
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "topics" / "gacha-pity-probability"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"

DISPLAY_PATH = TOPIC / "audio" / "gacha_pity_probability_v5_narration.txt"
RAW_SRT_PATH = TOPIC / "audio" / "gacha_pity_probability_v5_narration_raw.srt"
AUDIO_PATH = TOPIC / "audio" / "gacha_pity_probability_v5_narration.mp3"
FINAL_SRT_PATH = TOPIC / "audio" / "gacha_pity_probability_v5_final.srt"
TIMELINE_PATH = TOPIC / "audio" / "gacha_pity_probability_v5_timeline.json"

FPS = 60
SCENES = [
    {"name": "ThreeNumbersHookV4", "source": "gacha_pity_probability_v4.py"},
    {"name": "CohortAfterEachPullV4", "source": "gacha_pity_probability_v4.py"},
    {"name": "PullFiftyThreeViewsV4", "source": "gacha_pity_probability_v4.py"},
    {"name": "ConditionalProbabilityCurveFullV4", "source": "gacha_pity_probability_v4.py"},
    {"name": "FirstGoldPmfCurveFullV4", "source": "gacha_pity_probability_v4.py"},
    {"name": "CumulativeCdfCurveFullV4", "source": "gacha_pity_probability_v4.py"},
    {"name": "CompactCurveRelationshipV4", "source": "gacha_pity_probability_v4.py"},
    {"name": "HardPityCurveDashboardV4", "source": "gacha_pity_probability_v4.py"},
    {"name": "IntegratedRateVsHardPityV4", "source": "gacha_pity_probability_v4.py"},
    {"name": "NonUniquePerPullCurvesV4", "source": "gacha_pity_probability_v4.py"},
    {"name": "CommunitySampleDistributionV5", "source": "gacha_pity_probability_v5.py"},
    {"name": "CommunityFitComparisonV5", "source": "gacha_pity_probability_v5.py"},
    {"name": "FinalEstimatedCurvesV5", "source": "gacha_pity_probability_v5.py"},
    {"name": "FiveStarThenUpIdentityV4", "source": "gacha_pity_probability_v4.py"},
    {"name": "UpWaitingTwoPeaksV4", "source": "gacha_pity_probability_v4.py"},
    {"name": "CapturingRadianceBasicsV4", "source": "gacha_pity_probability_v4.py"},
    {"name": "CapturingRadianceHistoryV4", "source": "gacha_pity_probability_v4.py"},
    {"name": "ProbabilityStateConclusionV5", "source": "gacha_pity_probability_v5.py"},
]
EXPECTED_COUNTS = [6, 10, 10, 5, 8, 7, 7, 7, 7, 5, 8, 6, 8, 8, 10, 8, 7, 10]


@dataclass(frozen=True)
class Cue:
    start_ms: int
    end_ms: int
    text: str


def parse_time(value: str) -> int:
    hours, minutes, tail = value.split(":")
    seconds, millis = tail.split(",")
    return (
        int(hours) * 3_600_000
        + int(minutes) * 60_000
        + int(seconds) * 1000
        + int(millis)
    )


def format_time(milliseconds: int) -> str:
    milliseconds = max(0, milliseconds)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def parse_srt(path: Path) -> list[Cue]:
    blocks = re.split(r"\r?\n\r?\n", path.read_text(encoding="utf-8-sig").strip())
    cues: list[Cue] = []
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3:
            raise ValueError(f"Malformed SRT block: {block!r}")
        start_text, end_text = lines[1].split(" --> ")
        cues.append(Cue(parse_time(start_text), parse_time(end_text), " ".join(lines[2:])))
    return cues


def decoded_audio_duration_seconds() -> float:
    if not FFMPEG.exists():
        raise FileNotFoundError(f"Missing FFmpeg: {FFMPEG}")
    command = [
        str(FFMPEG),
        "-v",
        "error",
        "-i",
        str(AUDIO_PATH),
        "-f",
        "null",
        "NUL",
        "-progress",
        "pipe:1",
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    values = re.findall(r"^out_time_us=(\d+)$", result.stdout, flags=re.MULTILINE)
    if not values:
        raise RuntimeError("FFmpeg did not report out_time_us")
    return int(values[-1]) / 1_000_000


def main() -> None:
    paragraphs = [
        [line.strip() for line in block.splitlines() if line.strip()]
        for block in DISPLAY_PATH.read_text(encoding="utf-8").strip().split("\n\n")
    ]
    actual_counts = [len(paragraph) for paragraph in paragraphs]
    if actual_counts != EXPECTED_COUNTS:
        raise ValueError(f"Unexpected display paragraph counts: {actual_counts}")
    if len(SCENES) != len(paragraphs):
        raise ValueError("Scene/paragraph count mismatch")

    display_lines = [line for paragraph in paragraphs for line in paragraph]
    raw_cues = parse_srt(RAW_SRT_PATH)
    if len(raw_cues) != len(display_lines):
        raise ValueError(
            f"Raw/display cue mismatch: {len(raw_cues)} raw vs {len(display_lines)} display"
        )

    duration_seconds = decoded_audio_duration_seconds()
    duration_ms = int(round(duration_seconds * 1000))
    total_frames = math.ceil(duration_seconds * FPS)

    final_cues: list[Cue] = []
    for index, (raw_cue, display_text) in enumerate(zip(raw_cues, display_lines)):
        next_start = raw_cues[index + 1].start_ms if index + 1 < len(raw_cues) else duration_ms
        end_ms = min(raw_cue.end_ms, next_start, duration_ms)
        if end_ms <= raw_cue.start_ms:
            raise ValueError(f"Non-positive cue after overlap clipping: {index + 1}")
        if "\n" in display_text:
            raise ValueError(f"Multiline subtitle text at cue {index + 1}")
        final_cues.append(Cue(raw_cue.start_ms, end_ms, display_text))

    srt_lines: list[str] = []
    for index, cue in enumerate(final_cues, start=1):
        srt_lines.extend(
            [
                str(index),
                f"{format_time(cue.start_ms)} --> {format_time(cue.end_ms)}",
                cue.text,
                "",
            ]
        )
    FINAL_SRT_PATH.write_text("\n".join(srt_lines).rstrip() + "\n", encoding="utf-8-sig")

    paragraph_first_indices: list[int] = []
    cursor = 0
    for count in EXPECTED_COUNTS:
        paragraph_first_indices.append(cursor)
        cursor += count

    boundary_frames = [0]
    for first_index in paragraph_first_indices[1:]:
        boundary_frames.append(round(final_cues[first_index].start_ms * FPS / 1000))
    boundary_frames.append(total_frames)
    if boundary_frames != sorted(boundary_frames) or len(set(boundary_frames)) != len(boundary_frames):
        raise ValueError(f"Invalid scene boundaries: {boundary_frames}")

    timeline_scenes: list[dict[str, object]] = []
    cue_cursor = 0
    for index, scene in enumerate(SCENES):
        start_frame = boundary_frames[index]
        end_frame = boundary_frames[index + 1]
        frames = end_frame - start_frame
        scene_cues = final_cues[cue_cursor : cue_cursor + EXPECTED_COUNTS[index]]
        cue_cursor += EXPECTED_COUNTS[index]
        scene_start_ms = round(start_frame * 1000 / FPS)
        timeline_scenes.append(
            {
                "index": index + 1,
                **scene,
                "cue_count": EXPECTED_COUNTS[index],
                "start_frame": start_frame,
                "end_frame": end_frame,
                "frames": frames,
                "duration_seconds": frames / FPS,
                "cues": [
                    {
                        "start_seconds": (cue.start_ms - scene_start_ms) / 1000,
                        "end_seconds": (cue.end_ms - scene_start_ms) / 1000,
                        "text": cue.text,
                    }
                    for cue in scene_cues
                ],
            }
        )

    timeline = {
        "fps": FPS,
        "audio_duration_seconds": duration_seconds,
        "total_frames": total_frames,
        "video_duration_seconds": total_frames / FPS,
        "cue_count": len(final_cues),
        "scene_count": len(timeline_scenes),
        "scenes": timeline_scenes,
    }
    TIMELINE_PATH.write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {len(final_cues)} cues to {FINAL_SRT_PATH}")
    print(f"wrote {len(timeline_scenes)} scenes to {TIMELINE_PATH}")
    print(f"audio={duration_seconds:.6f}s total_frames={total_frames}")
    for scene in timeline_scenes:
        print(
            f"{scene['index']:02d} {scene['name']}: "
            f"{scene['frames']} frames / {scene['duration_seconds']:.6f}s"
        )


if __name__ == "__main__":
    main()
