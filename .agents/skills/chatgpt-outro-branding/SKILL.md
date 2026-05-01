---
name: chatgpt-outro-branding
description: Use when a generated math video needs a ChatGPT/OpenAI-branded ending, credit slate, logo outro, attribution card, or ChatGPT mark appended at the end before final publishing.
---

# ChatGPT Outro Branding

## Overview

Use this skill to append a polished ChatGPT-branded outro to a finished Manim video while keeping the main narration and derivation untouched. Always preview the outro alone first, then render and splice the approved high-quality outro into the full video.

## Required Assets

- Use the project material asset: `assets/brand/chatgpt_logo_line.svg`.
- Do not use any logo file with a colored square, white background, or raster-looking fill.
- Keep the mark as a transparent linear SVG on the existing dark video style.
- If the asset is missing, recreate or restore a line-only SVG under `assets/brand/` and ensure it is tracked by Git.

## Scene Pattern

Prefer a separate Manim scene file for the outro, for example:

- `topics/<topic>/scenes/chatgpt_outro.py`

Recommended structure:

- Dark background matching the topic video.
- A subtle panel or negative space, not a flashy glow.
- `SVGMobject(str(CHATGPT_LINE_LOGO)).set_fill(opacity=0).set_stroke(...)`.
- `ChatGPT` wordmark in Times New Roman or the topic's approved Latin font.
- A Chinese credit line meaning "the video was fully produced by ChatGPT".
- Optional small subtitle describing the production scope, such as topic selection, derivation, animation, and audio compositing.
- No top decorative line if it crowds the composition.
- Keep bottom footer text small and spaced away from the credit lines.

## Workflow

1. Check whether a reusable outro scene already exists for the topic.
2. Edit only the outro scene unless the main video timing needs to change.
3. Render the outro alone in low quality first:

```powershell
.\scripts\render_scene.ps1 -SceneFile topics\<topic>\scenes\chatgpt_outro.py -SceneName ChatGPTOutro -Quality -ql
```

4. Show or reference the low-quality outro preview and wait for user approval before touching the final full video.
5. After approval, render the outro in high quality:

```powershell
.\scripts\render_scene.ps1 -SceneFile topics\<topic>\scenes\chatgpt_outro.py -SceneName ChatGPTOutro -Quality -qh
```

6. Concatenate the approved high-quality outro after the existing high-quality main scene clips.
7. Mux the narration audio onto the new silent master with `scripts/add_audio.py`.
8. Generate a new cover with `scripts/generate_cover.py --update-metadata`.
9. Update `data/videos.json` so the new full video has a clear title, description, final-video status, cover, and a final chapter for the ChatGPT outro.

## Quality Checks

- Verify the final MP4 is still `1920x1080 / 60fps` when preparing a Bilibili-ready export.
- Verify the final MP4 has an audio stream.
- Confirm the outro is silent unless the user explicitly asks for outro audio.
- Keep the outro around 6-8 seconds unless the user asks otherwise.
- Do not commit generated MP4, MP3, cover JPG, poster JPG, or Manim export directories.
- Do commit reusable source assets such as `assets/brand/chatgpt_logo_line.svg` and source scenes such as `topics/<topic>/scenes/chatgpt_outro.py`.

## Current Project Example

For the astroid-envelope topic, the approved scene and asset are:

- Scene: `topics/astroid-envelope/scenes/chatgpt_outro.py`
- Asset: `assets/brand/chatgpt_logo_line.svg`
- Low-quality preview path: `topics/astroid-envelope/exports/manim/videos/chatgpt_outro/480p15/ChatGPTOutro.mp4`
- High-quality render path: `topics/astroid-envelope/exports/manim/videos/chatgpt_outro/1080p60/ChatGPTOutro.mp4`
