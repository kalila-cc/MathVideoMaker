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
- Use a short `CoverFrame` scene when a video needs a first-frame thumbnail. Design it for mobile two-column feeds: when previewed at roughly 160-200 px wide, the main title should still be basically readable. Prefer a short one- or two-line title, high contrast, generous margins, and avoid relying on small subtitles or dense formulas to carry the topic. For title sizing, prefer fitting to a target width over guessing with fixed `scale()` values; the main title should visibly occupy a large share of the frame. Default to exporting only one high-resolution cover image; do not create persistent 200 px check files unless the user asks for them.
- Scene title and subtitle text should be neutral content summaries of the current beat. Do not reuse narration slogans, metaphor words, or production phrases as page headers when they sound odd without the spoken context.
- Avoid long static waits after the main visual is drawn. If narration keeps explaining the same figure for more than a few seconds, use semantic motion such as moving control points, sweeping a parameter, changing weights, or pulsing the relevant relation while preserving the scene's target duration.
- For mathematical text, prefer `MathTex`. For Chinese prose in `Text`, keep one UI font by default; mixing Times New Roman into the same `Text` via `t2f` can raise inline letters/numbers above the Chinese baseline. When inline math needs professional glyphs, split the line into `Text` + `MathTex` pieces and align them manually.
- Avoid constructing new `Text` or `MathTex` inside an `always_redraw` callback when the glyphs do not actually change. Create labels once and use updaters or `next_to(...)` against moving geometry; repeated text creation is slower and can collide with Manim's shared SVG/text cache during parallel renders.
- Formula stacks should avoid repeated left-hand expressions when the equality target is unchanged. Keep the equals signs and right-hand results left-aligned so the viewer compares the transformed part instead of rereading the same left side.
- Do not add formula highlight or focus animations unless there is an explicit timestamped cue map tying narration text to that exact expression. Prefer clear sequencing, spacing, and color hierarchy; unsynced highlights are worse than no highlights.
- When narration or formulas reference geometric symbols such as `P_0`, `P_1`, `Q_0`, or `B(t)`, the corresponding points or moving marker must be visibly labeled in the same scene. Do a quick global pass for unlabeled symbol references before rendering previews.
- For background grids, palette tuning, line visibility, and other global look changes, render a one-frame preview first and copy it to a unique filename. Reusing the same still name can make the app show a cached image and hide real changes.
- Default future Manim math videos to the approved subtle grid background from the Bezier video unless a topic has a deliberate art direction: grid line `#8FA8D8`, `stroke_width=1.6`, `opacity=0.155`, `spacing=0.48` on the project dark background. If changing any of these values, preview one still before updating the full video.
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
