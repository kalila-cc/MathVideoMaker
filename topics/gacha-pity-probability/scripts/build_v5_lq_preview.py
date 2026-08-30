from __future__ import annotations

import subprocess
from pathlib import Path

from build_v5_review_srt import NEW_FRAME_COUNTS


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "topics" / "gacha-pity-probability"
FFMPEG = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
V4 = TOPIC / "exports" / "sync_lq"
V4_CURRENT = TOPIC / "exports" / "manim" / "videos" / "gacha_pity_probability_v4" / "480p15"
V5 = TOPIC / "exports" / "manim" / "videos" / "gacha_pity_probability_v5" / "480p15"
OUTPUT = TOPIC / "exports" / "final" / "GachaPityProbability_v5_480p15_subtitled_silent.mp4"
LOG = TOPIC / "exports" / "qa" / "gacha_pity_probability_v5_preview_ffmpeg.log"
SRT = TOPIC / "audio" / "gacha_pity_probability_v5_review_480p.srt"


CLIPS = [
    V4 / "worker_a" / "videos" / "gacha_pity_probability_v4" / "480p15" / "ThreeNumbersHookV4.mp4",
    V4 / "worker_a" / "videos" / "gacha_pity_probability_v4" / "480p15" / "CohortAfterEachPullV4.mp4",
    V4 / "worker_a" / "videos" / "gacha_pity_probability_v4" / "480p15" / "PullFiftyThreeViewsV4.mp4",
    V4 / "worker_a" / "videos" / "gacha_pity_probability_v4" / "480p15" / "ConditionalProbabilityCurveFullV4.mp4",
    V4 / "worker_a" / "videos" / "gacha_pity_probability_v4" / "480p15" / "FirstGoldPmfCurveFullV4.mp4",
    V4 / "worker_a" / "videos" / "gacha_pity_probability_v4" / "480p15" / "CumulativeCdfCurveFullV4.mp4",
    V4 / "worker_b" / "videos" / "gacha_pity_probability_v4" / "480p15" / "CompactCurveRelationshipV4.mp4",
    V4 / "worker_b" / "videos" / "gacha_pity_probability_v4" / "480p15" / "HardPityCurveDashboardV4.mp4",
    V4 / "worker_b" / "videos" / "gacha_pity_probability_v4" / "480p15" / "IntegratedRateVsHardPityV4.mp4",
    V4 / "worker_b" / "videos" / "gacha_pity_probability_v4" / "480p15" / "NonUniquePerPullCurvesV4.mp4",
    V5 / "CommunitySampleDistributionV5.mp4",
    V5 / "CommunityFitComparisonV5.mp4",
    V5 / "FinalEstimatedCurvesV5.mp4",
    V4_CURRENT / "FiveStarThenUpIdentityV4.mp4",
    V4_CURRENT / "UpWaitingTwoPeaksV4.mp4",
    V4_CURRENT / "CapturingRadianceBasicsV4.mp4",
    V4 / "worker_c" / "videos" / "gacha_pity_probability_v4" / "480p15" / "CapturingRadianceHistoryV4.mp4",
    V5 / "ProbabilityStateConclusionV5.mp4",
]


def ffmpeg_filter_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix().replace("'", r"\'")


def main() -> None:
    if not FFMPEG.exists():
        raise SystemExit(f"Missing ffmpeg: {FFMPEG}")
    if len(CLIPS) != len(NEW_FRAME_COUNTS):
        raise SystemExit("Clip/frame-count mismatch")
    missing = [path for path in [*CLIPS, SRT] if not path.exists()]
    if missing:
        raise SystemExit("Missing inputs:\n" + "\n".join(map(str, missing)))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)

    command = [str(FFMPEG), "-hide_banner", "-y"]
    for clip in CLIPS:
        command.extend(["-i", str(clip)])

    filters: list[str] = []
    labels: list[str] = []
    for index, frames in enumerate(NEW_FRAME_COUNTS):
        label = f"v{index}"
        filters.append(
            f"[{index}:v]fps=15,scale=854:480:flags=lanczos,"
            f"tpad=stop_mode=clone:stop_duration=1,trim=end_frame={frames},"
            f"setpts=PTS-STARTPTS[{label}]"
        )
        labels.append(f"[{label}]")
    filters.append(f"{''.join(labels)}concat=n={len(CLIPS)}:v=1:a=0[joined]")
    filters.append(
        f"[joined]fps=15,tpad=stop_mode=clone:stop_duration=1,"
        f"trim=end_frame={sum(NEW_FRAME_COUNTS)},setpts=N/(15*TB)[base]"
    )
    subtitle_path = ffmpeg_filter_path(SRT)
    filters.append(
        "[base]subtitles='"
        + subtitle_path
        + "':fontsdir='assets/fonts':"
        + "force_style='FontName=Smiley Sans Oblique,FontSize=14,"
        + "Outline=0.9,Shadow=0.3,Alignment=2,MarginV=10'[vout]"
    )

    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[vout]",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "23",
            "-profile:v",
            "high",
            "-pix_fmt",
            "yuv420p",
            "-r",
            "15",
            "-frames:v",
            str(sum(NEW_FRAME_COUNTS)),
            "-movflags",
            "+faststart",
            str(OUTPUT),
        ]
    )
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, encoding="utf-8")
    LOG.write_text(result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise SystemExit(result.stderr)
    print(OUTPUT)
    print(f"frames={sum(NEW_FRAME_COUNTS)} duration={sum(NEW_FRAME_COUNTS) / 15:.6f}s")


if __name__ == "__main__":
    main()
