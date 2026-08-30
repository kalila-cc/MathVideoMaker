from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "topics" / "gacha-pity-probability"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
TIMELINE_PATH = TOPIC / "audio" / "gacha_pity_probability_v5_timeline.json"
SRT_PATH = TOPIC / "audio" / "gacha_pity_probability_v5_final.srt"
AUDIO_PATH = TOPIC / "audio" / "gacha_pity_probability_v5_narration.mp3"
OUTPUT_PATH = TOPIC / "exports" / "final" / "GachaPityProbability_v5_1080p60_final.mp4"
TEMP_OUTPUT_PATH = OUTPUT_PATH.with_name("GachaPityProbability_v5_1080p60_encoding.mp4")
LOG_PATH = TOPIC / "exports" / "qa" / "v5_hd_final_encode.log"

WORKER_BY_SCENE = {
    "ThreeNumbersHookV4": "a",
    "CohortAfterEachPullV4": "a",
    "PullFiftyThreeViewsV4": "a",
    "ConditionalProbabilityCurveFullV4": "a",
    "FirstGoldPmfCurveFullV4": "a",
    "CumulativeCdfCurveFullV4": "a",
    "CompactCurveRelationshipV4": "b",
    "HardPityCurveDashboardV4": "b",
    "IntegratedRateVsHardPityV4": "b",
    "NonUniquePerPullCurvesV4": "b",
    "CommunitySampleDistributionV5": "c",
    "CommunityFitComparisonV5": "c",
    "FinalEstimatedCurvesV5": "c",
    "FiveStarThenUpIdentityV4": "b",
    "UpWaitingTwoPeaksV4": "b",
    "CapturingRadianceBasicsV4": "c",
    "CapturingRadianceHistoryV4": "c",
    "ProbabilityStateConclusionV5": "c",
}


def ffmpeg_filter_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix().replace("'", r"\'")


def clip_path(scene: dict[str, object]) -> Path:
    name = str(scene["name"])
    worker = WORKER_BY_SCENE[name]
    source_stem = Path(str(scene["source"])).stem
    return (
        TOPIC
        / "exports"
        / "manim_hd_v5"
        / f"worker_{worker}"
        / "videos"
        / source_stem
        / "1080p60"
        / f"{name}.mp4"
    )


def main() -> None:
    if not FFMPEG.exists():
        raise FileNotFoundError(f"Missing FFmpeg: {FFMPEG}")
    timeline = json.loads(TIMELINE_PATH.read_text(encoding="utf-8"))
    fps = int(timeline["fps"])
    total_frames = int(timeline["total_frames"])
    video_duration = total_frames / fps
    scenes = timeline["scenes"]
    if len(scenes) != 18 or set(WORKER_BY_SCENE) != {scene["name"] for scene in scenes}:
        raise ValueError("Unexpected formal scene set")

    clips = [clip_path(scene) for scene in scenes]
    missing = [path for path in [*clips, SRT_PATH, AUDIO_PATH] if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing final inputs:\n" + "\n".join(map(str, missing)))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    command = [str(FFMPEG), "-hide_banner", "-y"]
    for clip in clips:
        command.extend(["-i", str(clip)])
    audio_input_index = len(clips)
    command.extend(["-i", str(AUDIO_PATH)])

    filters: list[str] = []
    labels: list[str] = []
    for index, scene in enumerate(scenes):
        frames = int(scene["frames"])
        label = f"v{index}"
        filters.append(
            f"[{index}:v]fps={fps},scale=1920:1080:flags=lanczos,"
            f"tpad=stop_mode=clone:stop_duration=1,trim=end_frame={frames},"
            f"setpts=PTS-STARTPTS[{label}]"
        )
        labels.append(f"[{label}]")
    filters.append(f"{''.join(labels)}concat=n={len(clips)}:v=1:a=0[joined]")
    filters.append(
        f"[joined]fps={fps},tpad=stop_mode=clone:stop_duration=1,"
        f"trim=end_frame={total_frames},setpts=N/({fps}*TB)[base]"
    )
    filters.append(
        "[base]subtitles='"
        + ffmpeg_filter_path(SRT_PATH)
        + "':fontsdir='assets/fonts':"
        + "force_style='FontName=Smiley Sans Oblique,FontSize=14,"
        + "Outline=0.9,Shadow=0.3,Alignment=2,MarginV=10'[vout]"
    )
    filters.append(
        f"[{audio_input_index}:a]loudnorm=I=-16:TP=-1.5:LRA=11,"
        "aresample=48000,apad[aout]"
    )

    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "18",
            "-profile:v",
            "high",
            "-level:v",
            "4.2",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(fps),
            "-frames:v",
            str(total_frames),
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "1",
            "-t",
            f"{video_duration:.9f}",
            "-movflags",
            "+faststart",
            str(TEMP_OUTPUT_PATH),
        ]
    )

    print(f"encoding {len(clips)} scenes / {total_frames} frames", flush=True)
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, encoding="utf-8")
    LOG_PATH.write_text(result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise SystemExit(f"FFmpeg failed; see {LOG_PATH}")
    TEMP_OUTPUT_PATH.replace(OUTPUT_PATH)
    print(OUTPUT_PATH, flush=True)
    print(f"frames={total_frames} duration={video_duration:.9f}s", flush=True)


if __name__ == "__main__":
    main()
