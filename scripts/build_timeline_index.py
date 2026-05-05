import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FFMPEG = PROJECT_ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"


def resolve_path(value: str | Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def parse_time(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if value is None:
        raise ValueError("Missing time value.")

    text = str(value).strip().replace(",", ".")
    parts = text.split(":")
    if len(parts) == 1:
        return float(parts[0])
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    raise ValueError(f"Invalid time value: {value!r}")


def format_time(seconds: float | None) -> str | None:
    if seconds is None:
        return None
    seconds = max(0.0, float(seconds))
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds - hours * 3600 - minutes * 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def probe_duration(path: Path, ffmpeg: Path) -> float:
    result = subprocess.run(
        [str(ffmpeg), "-hide_banner", "-i", str(path)],
        text=True,
        capture_output=True,
    )
    output = result.stderr + result.stdout
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", output)
    if not match:
        raise SystemExit(f"Could not probe duration: {path}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def parse_srt_time(value: str) -> float:
    return parse_time(value)


def parse_srt(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8-sig")
    blocks = re.split(r"\n\s*\n", text.strip())
    cues: list[dict[str, Any]] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 3:
            continue
        try:
            index = int(lines[0])
        except ValueError:
            continue
        if "-->" not in lines[1]:
            continue
        start_text, end_text = [item.strip() for item in lines[1].split("-->", 1)]
        start = parse_srt_time(start_text)
        end = parse_srt_time(end_text)
        cues.append(
            {
                "index": index,
                "start": round(start, 3),
                "end": round(end, 3),
                "startTime": format_time(start),
                "endTime": format_time(end),
                "text": " ".join(lines[2:]),
            }
        )
    return cues


def load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            items.extend(flatten_strings(item))
        return items
    if isinstance(value, dict):
        items = []
        for item in value.values():
            items.extend(flatten_strings(item))
        return items
    return []


def text_matches(text: str, query: str, use_regex: bool = False) -> bool:
    if use_regex:
        return re.search(query, text, re.IGNORECASE) is not None
    return query.lower() in text.lower()


def first_matching_cue(cues: list[dict[str, Any]], query: str, use_regex: bool = False) -> dict[str, Any] | None:
    for cue in cues:
        if text_matches(cue["text"], query, use_regex):
            return cue
    return None


def build_index(config: dict[str, Any], config_path: Path, ffmpeg: Path) -> dict[str, Any]:
    if not ffmpeg.exists():
        raise SystemExit(f"FFmpeg not found: {ffmpeg}")

    srt_path = resolve_path(config["srt"]) if config.get("srt") else None
    cues = parse_srt(srt_path) if srt_path else []
    scenes: list[dict[str, Any]] = []
    offset = parse_time(config.get("startOffset", 0))

    for raw_scene in config.get("scenes", []):
        scene = dict(raw_scene)
        clip = resolve_path(scene["clip"])
        if not clip.exists():
            raise SystemExit(f"Scene clip not found: {clip}")
        duration = parse_time(scene["duration"]) if scene.get("duration") is not None else probe_duration(clip, ffmpeg)
        global_start = offset
        global_end = global_start + duration
        scenes.append(
            {
                "id": scene["id"],
                "sceneName": scene.get("sceneName", scene["id"]),
                "clip": clip.relative_to(PROJECT_ROOT).as_posix(),
                "duration": round(duration, 3),
                "globalStart": round(global_start, 3),
                "globalEnd": round(global_end, 3),
                "globalStartTime": format_time(global_start),
                "globalEndTime": format_time(global_end),
            }
        )
        offset = global_end

    scene_by_id = {scene["id"]: scene for scene in scenes}
    raw_beats = [dict(beat) for beat in config.get("beats", [])]
    raw_beats.sort(key=lambda beat: (scene_by_id[beat["scene"]]["globalStart"], parse_time(beat.get("start", 0))))

    beats: list[dict[str, Any]] = []
    for index, raw_beat in enumerate(raw_beats):
        scene = scene_by_id.get(raw_beat["scene"])
        if not scene:
            raise SystemExit(f"Beat references unknown scene: {raw_beat}")
        local_start = parse_time(raw_beat.get("start", 0))
        if raw_beat.get("end") is not None:
            local_end = parse_time(raw_beat["end"])
        elif raw_beat.get("duration") is not None:
            local_end = local_start + parse_time(raw_beat["duration"])
        else:
            local_end = float(scene["duration"])
            for later in raw_beats[index + 1 :]:
                if later["scene"] == raw_beat["scene"]:
                    local_end = parse_time(later.get("start", local_end))
                    break

        global_start = float(scene["globalStart"]) + local_start
        global_end = float(scene["globalStart"]) + local_end
        beat = {
            **raw_beat,
            "localStart": round(local_start, 3),
            "localEnd": round(local_end, 3),
            "globalStart": round(global_start, 3),
            "globalEnd": round(global_end, 3),
            "globalStartTime": format_time(global_start),
            "globalEndTime": format_time(global_end),
        }
        for query in raw_beat.get("narrationQueries", []):
            cue = first_matching_cue(cues, query)
            if cue:
                beat.setdefault("matchedNarration", []).append(
                    {
                        "query": query,
                        "cueIndex": cue["index"],
                        "cueStart": cue["start"],
                        "cueEnd": cue["end"],
                        "cueStartTime": cue["startTime"],
                        "cueEndTime": cue["endTime"],
                        "deltaStartSeconds": round(global_start - float(cue["start"]), 3),
                        "text": cue["text"],
                    }
                )
        beats.append(beat)

    checks = run_checks(config.get("alignmentChecks", []), beats, cues)

    final_video = resolve_path(config["finalVideo"]).relative_to(PROJECT_ROOT).as_posix() if config.get("finalVideo") else None
    return {
        "topic": config.get("topic"),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceConfig": config_path.relative_to(PROJECT_ROOT).as_posix(),
        "finalVideo": final_video,
        "srt": srt_path.relative_to(PROJECT_ROOT).as_posix() if srt_path else None,
        "scenes": scenes,
        "beats": beats,
        "srtCues": cues,
        "alignmentChecks": checks,
    }


def run_checks(raw_checks: list[dict[str, Any]], beats: list[dict[str, Any]], cues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    beat_by_id = {beat["id"]: beat for beat in beats}
    results: list[dict[str, Any]] = []
    for raw in raw_checks:
        beat = beat_by_id.get(raw["beat"])
        query = raw.get("query", "")
        cue = None
        if raw.get("cueIndex") is not None:
            cue = next((item for item in cues if item["index"] == int(raw["cueIndex"])), None)
        elif query:
            cue = first_matching_cue(cues, query, bool(raw.get("regex")))

        result = {
            "id": raw["id"],
            "beat": raw["beat"],
            "query": query,
            "status": "fail",
            "message": "",
        }
        if not beat:
            result["message"] = "Beat not found."
            results.append(result)
            continue
        if not cue:
            result["message"] = "Narration cue not found."
            result["visualStartTime"] = beat["globalStartTime"]
            result["visualEndTime"] = beat["globalEndTime"]
            results.append(result)
            continue

        visual_start = float(beat["globalStart"])
        visual_end = float(beat["globalEnd"])
        cue_start = float(cue["start"])
        delta = visual_start - cue_start
        max_lead = float(raw.get("maxLead", 1.0))
        max_lag = float(raw.get("maxLag", 0.35))
        active_required = bool(raw.get("requireActiveAtCueStart", True))
        start_ok = -max_lead <= delta <= max_lag
        active_ok = (visual_start <= cue_start <= visual_end) if active_required else True
        status = "ok" if start_ok and active_ok else "fail"
        problems = []
        if not start_ok:
            problems.append(f"delta {delta:.3f}s outside [-{max_lead:.3f}, {max_lag:.3f}]")
        if not active_ok:
            problems.append("visual beat is not active at cue start")

        result.update(
            {
                "status": status,
                "message": "; ".join(problems) if problems else "aligned",
                "visualStart": round(visual_start, 3),
                "visualEnd": round(visual_end, 3),
                "visualStartTime": beat["globalStartTime"],
                "visualEndTime": beat["globalEndTime"],
                "cueIndex": cue["index"],
                "cueStart": cue["start"],
                "cueEnd": cue["end"],
                "cueStartTime": cue["startTime"],
                "cueEndTime": cue["endTime"],
                "deltaStartSeconds": round(delta, 3),
                "cueText": cue["text"],
            }
        )
        results.append(result)
    return results


def search_index(index: dict[str, Any], query: str, use_regex: bool = False) -> dict[str, list[dict[str, Any]]]:
    beat_matches: list[dict[str, Any]] = []
    for beat in index.get("beats", []):
        haystack = "\n".join(flatten_strings(beat))
        if text_matches(haystack, query, use_regex):
            beat_matches.append(
                {
                    "id": beat["id"],
                    "scene": beat["scene"],
                    "label": beat.get("label"),
                    "globalStart": beat["globalStart"],
                    "globalEnd": beat["globalEnd"],
                    "globalStartTime": beat["globalStartTime"],
                    "globalEndTime": beat["globalEndTime"],
                }
            )

    cue_matches: list[dict[str, Any]] = []
    for cue in index.get("srtCues", []):
        if text_matches(cue["text"], query, use_regex):
            cue_matches.append(cue)

    check_matches = [
        check
        for check in index.get("alignmentChecks", [])
        if text_matches("\n".join(flatten_strings(check)), query, use_regex)
    ]
    return {"beats": beat_matches, "srtCues": cue_matches, "checks": check_matches}


def print_search_results(results: dict[str, list[dict[str, Any]]]) -> None:
    print("VISUAL_BEATS")
    for beat in results["beats"]:
        print(
            f"- {beat['globalStartTime']} -> {beat['globalEndTime']} "
            f"[{beat['scene']}/{beat['id']}] {beat.get('label') or ''}"
        )
    if not results["beats"]:
        print("- none")

    print("SRT_CUES")
    for cue in results["srtCues"]:
        print(f"- {cue['startTime']} -> {cue['endTime']} [cue {cue['index']}] {cue['text']}")
    if not results["srtCues"]:
        print("- none")

    if results["checks"]:
        print("ALIGNMENT_CHECKS")
        for check in results["checks"]:
            print(
                f"- {check['status']} {check['id']} delta={check.get('deltaStartSeconds')} "
                f"visual={check.get('visualStartTime')} cue={check.get('cueStartTime')}"
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and query a structured timeline index for a rendered video.")
    parser.add_argument("--config", required=True, help="Timeline config JSON.")
    parser.add_argument("--out", help="Output timeline index JSON. Defaults beside the config.")
    parser.add_argument("--ffmpeg", default=str(DEFAULT_FFMPEG), help="Path to ffmpeg executable.")
    parser.add_argument("--search", help="Search visual beats and SRT cues by text.")
    parser.add_argument("--regex", action="store_true", help="Treat --search and check queries as regular expressions.")
    parser.add_argument("--check", action="store_true", help="Print alignment check results.")
    parser.add_argument("--strict", action="store_true", help="Exit nonzero when any configured check fails.")
    parser.add_argument("--no-write", action="store_true", help="Do not write the timeline index JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = resolve_path(args.config)
    output_path = resolve_path(args.out) if args.out else config_path.with_name(f"{config_path.stem}_index.json")
    index = build_index(load_config(config_path), config_path, resolve_path(args.ffmpeg))

    if not args.no_write:
        write_json(output_path, index)
        print(f"Wrote: {output_path}")

    if args.search:
        print_search_results(search_index(index, args.search, args.regex))

    failed = [check for check in index.get("alignmentChecks", []) if check.get("status") != "ok"]
    if args.check:
        print("ALIGNMENT_SUMMARY")
        for check in index.get("alignmentChecks", []):
            print(
                f"- {check['status']} {check['id']} "
                f"visual={check.get('visualStartTime')} cue={check.get('cueStartTime')} "
                f"delta={check.get('deltaStartSeconds')} {check.get('message', '')}"
            )

    if args.strict and failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
