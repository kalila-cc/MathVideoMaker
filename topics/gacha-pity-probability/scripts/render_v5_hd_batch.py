from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "topics" / "gacha-pity-probability"
SCENE_DIR = TOPIC / "scenes"
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
FFMPEG_BIN = ROOT / "tools" / "ffmpeg" / "bin"
MIKTEX_BIN = (
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "Programs"
    / "MiKTeX"
    / "miktex"
    / "bin"
    / "x64"
)

BATCHES: dict[str, list[tuple[str, list[str]]]] = {
    "a": [
        (
            "gacha_pity_probability_v4.py",
            [
                "ThreeNumbersHookV4",
                "CohortAfterEachPullV4",
                "PullFiftyThreeViewsV4",
                "ConditionalProbabilityCurveFullV4",
                "FirstGoldPmfCurveFullV4",
                "CumulativeCdfCurveFullV4",
            ],
        )
    ],
    "b": [
        (
            "gacha_pity_probability_v4.py",
            [
                "CompactCurveRelationshipV4",
                "HardPityCurveDashboardV4",
                "IntegratedRateVsHardPityV4",
                "NonUniquePerPullCurvesV4",
                "FiveStarThenUpIdentityV4",
                "UpWaitingTwoPeaksV4",
            ],
        )
    ],
    "c": [
        (
            "gacha_pity_probability_v5.py",
            [
                "CommunitySampleDistributionV5",
                "CommunityFitComparisonV5",
                "FinalEstimatedCurvesV5",
                "ProbabilityStateConclusionV5",
            ],
        ),
        (
            "gacha_pity_probability_v4.py",
            [
                "CapturingRadianceBasicsV4",
                "CapturingRadianceHistoryV4",
            ],
        ),
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render one isolated v5 HD scene batch.")
    parser.add_argument("--batch", choices=sorted(BATCHES), required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not PYTHON.exists():
        raise FileNotFoundError(f"Missing Python runtime: {PYTHON}")

    media_dir = TOPIC / "exports" / "manim_hd_v5" / f"worker_{args.batch}"
    log_dir = TOPIC / "exports" / "qa" / "v5_hd_render_logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    prefixes = [path for path in (FFMPEG_BIN, MIKTEX_BIN) if path.exists()]
    env["PATH"] = os.pathsep.join([*(str(path) for path in prefixes), env.get("PATH", "")])

    for source_name, scene_names in BATCHES[args.batch]:
        source_path = SCENE_DIR / source_name
        command = [
            str(PYTHON),
            "-m",
            "manim",
            "-qh",
            "--disable_caching",
            "--media_dir",
            str(media_dir),
            str(source_path),
            *scene_names,
        ]
        print(f"rendering {source_name}: {', '.join(scene_names)}", flush=True)
        result = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        log_path = log_dir / f"worker_{args.batch}_{source_path.stem}.log"
        log_path.write_text(
            (result.stdout or "") + "\n" + (result.stderr or ""), encoding="utf-8"
        )
        if result.returncode != 0:
            raise SystemExit(f"Manim failed; see {log_path}")

        output_dir = media_dir / "videos" / source_path.stem / "1080p60"
        missing = [name for name in scene_names if not (output_dir / f"{name}.mp4").exists()]
        if missing:
            raise FileNotFoundError(f"Missing rendered scenes in {output_dir}: {missing}")

    print(f"batch {args.batch} complete: {media_dir}", flush=True)


if __name__ == "__main__":
    main()
