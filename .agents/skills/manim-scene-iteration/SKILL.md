---
name: manim-scene-iteration
description: Use when creating, editing, or debugging Manim scenes for this project, especially versioned math animation iterations with low-quality previews.
---

# Manim Scene Iteration

Use this skill when changing files under `topics/<topic>/scenes/`.

## Versioning

- Prefer copying the last stable scene to a new version, such as `topics/astroid-envelope/scenes/astroid_envelope_v6.py`, before structural changes.
- Keep old versions as comparison points unless the user explicitly asks to delete source code.
- Make small timing and text edits in the current version rather than regenerating everything from scratch.

## Scene Structure

- Split complex videos into multiple Manim `Scene` classes.
- Keep each scene aligned to a narration paragraph or chapter beat.
- Use a short `CoverFrame` scene when a video needs a first-frame thumbnail. Design it for mobile two-column feeds: when downscaled to roughly 160-200 px wide, the main title should still be basically readable. Prefer a short one- or two-line title, high contrast, generous margins, and avoid relying on small subtitles or dense formulas to carry the topic. For title sizing, prefer fitting to a target width over guessing with fixed `scale()` values; the main title should visibly occupy a large share of the frame. After rendering, inspect both the full frame and a 160-200 px thumbnail; the title plus one core visual should occupy the main area instead of leaving large unused space.
- Scene title and subtitle text should be neutral content summaries of the current beat. Do not reuse narration slogans, metaphor words, or production phrases as page headers when they sound odd without the spoken context.
- For mathematical text, prefer `MathTex`. For Chinese prose in `Text`, keep one UI font by default; mixing Times New Roman into the same `Text` via `t2f` can raise inline letters/numbers above the Chinese baseline. When inline math needs professional glyphs, split the line into `Text` + `MathTex` pieces and align them manually.
- Formula stacks should avoid repeated left-hand expressions when the equality target is unchanged. Keep the equals signs and right-hand results left-aligned so the viewer compares the transformed part instead of rereading the same left side.
- Do not add formula highlight or focus animations unless there is an explicit timestamped cue map tying narration text to that exact expression. Prefer clear sequencing, spacing, and color hierarchy; unsynced highlights are worse than no highlights.
- Keep source files under `topics/<topic>/scenes/` and generated media under `topics/<topic>/exports/`.

## Timing

1. Generate narration and SRT first.
2. Render low quality with `-ql`.
3. Measure each scene duration with FFmpeg.
4. Adjust `self.wait(...)` until scene boundaries match narration boundaries.

## Commands

```powershell
.\scripts\render_scene.ps1 -SceneFile topics\astroid-envelope\scenes\astroid_envelope_v6.py -SceneName StoryHook
.\scripts\render_scenes_parallel.ps1 -SceneFile topics\astroid-envelope\scenes\astroid_envelope_v6.py -SceneNames CoverFrame,StoryHook -MaxParallel 3
```

The render scripts infer `--media_dir topics\<topic>\exports\manim` from the scene path. If running Manim directly, pass that `--media_dir` manually so intermediate renders do not go back to the root `exports/` folder.
