from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


TOPIC_DIR = Path(__file__).resolve().parents[1]
DISPLAY_PATH = TOPIC_DIR / "audio" / "gacha_pity_probability_v5_narration.txt"
OLD_SRT_PATH = TOPIC_DIR / "audio" / "gacha_pity_probability_v4_final.srt"
OUTPUT_PATH = TOPIC_DIR / "audio" / "gacha_pity_probability_v5_review_480p.srt"

OLD_COUNTS = [6, 10, 10, 5, 8, 7, 7, 7, 7, 5, 14, 12, 10, 11, 8, 7, 10]
OLD_DURATIONS = [
    23.466667,
    37.183333,
    38.666667,
    19.0,
    31.633333,
    27.666667,
    28.75,
    33.716667,
    29.35,
    19.866667,
    58.116667,
    44.433333,
    34.6,
    41.533333,
    32.433333,
    27.316667,
    38.1,
]
IDEAL_NEW_DURATIONS = [
    *OLD_DURATIONS[:10],
    32.0,
    26.4,
    38.0,
    *OLD_DURATIONS[12:],
]
FPS = 15
_cumulative = 0.0
_boundaries = [0]
for _duration in IDEAL_NEW_DURATIONS:
    _cumulative += _duration
    _boundaries.append(round(_cumulative * FPS))
NEW_FRAME_COUNTS = [
    _boundaries[index + 1] - _boundaries[index]
    for index in range(len(IDEAL_NEW_DURATIONS))
]
NEW_DURATIONS = [frames / FPS for frames in NEW_FRAME_COUNTS]


@dataclass(frozen=True)
class Cue:
    start: float
    end: float
    text: str


def parse_time(value: str) -> float:
    hours, minutes, tail = value.split(":")
    seconds, millis = tail.split(",")
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000


def format_time(seconds: float) -> str:
    millis = max(0, int(round(seconds * 1000)))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def parse_srt(path: Path) -> list[Cue]:
    blocks = re.split(r"\r?\n\r?\n", path.read_text(encoding="utf-8-sig").strip())
    cues: list[Cue] = []
    for block in blocks:
        lines = block.splitlines()
        start_text, end_text = lines[1].split(" --> ")
        cues.append(Cue(parse_time(start_text), parse_time(end_text), " ".join(lines[2:])))
    return cues


def split_groups(items: list[Cue], counts: list[int]) -> list[list[Cue]]:
    groups: list[list[Cue]] = []
    cursor = 0
    for count in counts:
        groups.append(items[cursor : cursor + count])
        cursor += count
    if cursor != len(items):
        raise ValueError(f"SRT cue count mismatch: grouped {cursor}, found {len(items)}")
    return groups


def to_local(group: list[Cue], scene_start: float) -> list[tuple[float, float]]:
    return [(cue.start - scene_start, cue.end - scene_start) for cue in group]


def estimated_intervals(lines: list[str], duration: float) -> list[tuple[float, float]]:
    weights = []
    for line in lines:
        ascii_groups = len(re.findall(r"[A-Za-z0-9.%]+", line))
        weights.append(max(2.4, 1.25 + 0.17 * len(line) + 0.22 * ascii_groups))
    start = 0.1
    usable = duration - start - 0.05
    scale = usable / sum(weights)
    intervals: list[tuple[float, float]] = []
    cursor = start
    for index, weight in enumerate(weights):
        end = duration - 0.05 if index == len(weights) - 1 else cursor + weight * scale
        intervals.append((cursor, end))
        cursor = end
    return intervals


def scaled_intervals(
    intervals: list[tuple[float, float]], source_duration: float, target_duration: float
) -> list[tuple[float, float]]:
    scale = target_duration / source_duration
    return [(start * scale, end * scale) for start, end in intervals]


def main() -> None:
    paragraphs = [
        [line for line in block.splitlines() if line.strip()]
        for block in DISPLAY_PATH.read_text(encoding="utf-8").strip().split("\n\n")
    ]
    expected_counts = [6, 10, 10, 5, 8, 7, 7, 7, 7, 5, 8, 6, 8, 8, 10, 8, 7, 10]
    actual_counts = [len(paragraph) for paragraph in paragraphs]
    if actual_counts != expected_counts:
        raise ValueError(f"Unexpected v5 paragraph counts: {actual_counts}")

    old_groups = split_groups(parse_srt(OLD_SRT_PATH), OLD_COUNTS)
    old_starts: list[float] = []
    cursor = 0.0
    for duration in OLD_DURATIONS:
        old_starts.append(cursor)
        cursor += duration
    old_local = [to_local(group, start) for group, start in zip(old_groups, old_starts)]

    local_intervals: list[list[tuple[float, float]]] = []
    for index in range(10):
        local_intervals.append(
            scaled_intervals(old_local[index], OLD_DURATIONS[index], NEW_DURATIONS[index])
        )
    local_intervals.append(estimated_intervals(paragraphs[10], NEW_DURATIONS[10]))
    local_intervals.append(estimated_intervals(paragraphs[11], NEW_DURATIONS[11]))
    local_intervals.append(estimated_intervals(paragraphs[12], NEW_DURATIONS[12]))

    old_up = old_local[12]
    local_intervals.append(
        scaled_intervals(
            [
                (old_up[0][0], old_up[1][1]),
                (old_up[2][0], old_up[3][1]),
                *old_up[4:],
            ],
            OLD_DURATIONS[12],
            NEW_DURATIONS[13],
        )
    )
    old_double_peak = old_local[13]
    local_intervals.append(
        scaled_intervals(
            [*old_double_peak[:9], (old_double_peak[9][0], old_double_peak[10][1])],
            OLD_DURATIONS[13],
            NEW_DURATIONS[14],
        )
    )
    for old_index, new_index in zip(range(14, 17), range(15, 18)):
        local_intervals.append(
            scaled_intervals(
                old_local[old_index], OLD_DURATIONS[old_index], NEW_DURATIONS[new_index]
            )
        )

    if len(local_intervals) != len(paragraphs):
        raise ValueError("Scene interval count mismatch")
    for scene_index, (intervals, lines) in enumerate(zip(local_intervals, paragraphs), start=1):
        if len(intervals) != len(lines):
            raise ValueError(
                f"Scene {scene_index} interval count {len(intervals)} != text count {len(lines)}"
            )

    output: list[str] = []
    cue_index = 1
    global_start = 0.0
    for duration, lines, intervals in zip(NEW_DURATIONS, paragraphs, local_intervals):
        for line, (local_start, local_end) in zip(lines, intervals):
            output.extend(
                [
                    str(cue_index),
                    f"{format_time(global_start + local_start)} --> {format_time(global_start + local_end)}",
                    line,
                    "",
                ]
            )
            cue_index += 1
        global_start += duration

    OUTPUT_PATH.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8-sig")
    print(f"wrote {cue_index - 1} cues to {OUTPUT_PATH}")
    print(f"scene durations: {NEW_DURATIONS}")
    print(f"scene frames: {NEW_FRAME_COUNTS}")
    print(f"total duration: {sum(NEW_DURATIONS):.6f}s")


if __name__ == "__main__":
    main()
