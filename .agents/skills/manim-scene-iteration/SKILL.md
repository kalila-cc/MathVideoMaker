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
- Use a short `CoverFrame` scene when a video needs a first-frame thumbnail.
- For mathematical text, prefer `MathTex`; for Chinese `Text`, map Latin letters and numbers to Times New Roman when mixed into Chinese copy.
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
