---
name: chatgpt-outro-branding
description: Use when a generated math video needs a ChatGPT/OpenAI-branded opening, ending, credit slate, logo outro, attribution card, or ChatGPT mark before final publishing.
---

# ChatGPT Outro Branding

## Overview

Use this skill to add a polished ChatGPT-branded intro or outro to a finished Manim video while keeping the main narration and derivation untouched. Prefer an opening slate when the user wants the ending to stay focused on the math payoff. Reuse the previously approved ChatGPT intro slate exactly by default; do not redesign colors, layout, wording, timing, or animation unless the user explicitly asks for a new branding treatment. Always preview the branding scene alone first when a new or changed slate is required, then render and splice the approved high-quality slate into the full video.

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
- A Chinese credit line that accurately describes the production scope. If the user supplied or chose the topic, do not claim ChatGPT handled topic selection. Prefer stating the work actually done, such as "本片制作由 ChatGPT 完成" with scope chips for derivation, animation, narration/subtitles, and compositing; only mention topic ownership if the user asks for it.
- Optional small subtitle or chips describing the production scope, such as derivation, animation, narration, subtitles, and audio/video compositing.
- No top decorative line if it crowds the composition.
- Keep bottom footer text small and spaced away from the credit lines.
- When using scope chips or tags, pace them for readability: stagger the appearances clearly and leave them fully visible for at least about one second before fading out.

## Workflow

1. Check whether a reusable outro scene already exists for the topic.
2. For an intro slate, first look for an already approved 5.05s ChatGPT intro in prior final videos such as `topics/power-sum-polynomials/exports/final/PowerSumPolynomials_final_1080p60_chatgpt_intro.mp4`; extract and reuse that slate unchanged when available.
3. Edit only the branding scene unless the main video timing needs to change or no approved reusable slate exists.
4. Render the outro alone in low quality first when the branding scene is new or changed:

```powershell
.\scripts\render_scene.ps1 -SceneFile topics\<topic>\scenes\chatgpt_outro.py -SceneName ChatGPTOutro -Quality -ql
```

5. Show or reference the low-quality outro preview and wait for user approval before touching the final full video.
6. After approval, render the outro in high quality:

```powershell
.\scripts\render_scene.ps1 -SceneFile topics\<topic>\scenes\chatgpt_outro.py -SceneName ChatGPTOutro -Quality -qh
```

7. Concatenate the approved high-quality branding scene before or after the existing high-quality main scene clips according to the approved placement.
8. Mux the narration audio onto the new silent master with `scripts/add_audio.py`.
9. Generate a new cover with `scripts/generate_cover.py --update-metadata`.
10. Update `data/videos.json` so the new full video has a clear title, description, final-video status, cover metadata, and a chapter for the ChatGPT branding slate when it is part of the video.

## Quality Checks

- Verify the final MP4 is still `1920x1080 / 60fps` when preparing a Bilibili-ready export.
- Verify the final MP4 has an audio stream.
- Confirm the branding slate is silent unless the user explicitly asks for branding audio.
- Keep an intro slate short, but use the same animated language as the approved outro when the user asks for the prior animation style. A static intro is only appropriate when explicitly requested or when it is just covering a deliberate narration delay. Keep an outro around 6-8 seconds unless the user asks otherwise.
- Do not commit generated MP4, MP3, cover JPG, poster JPG, or Manim export directories.
- Do commit reusable source assets such as `assets/brand/chatgpt_logo_line.svg` and source scenes such as `topics/<topic>/scenes/chatgpt_outro.py`.

## Current Project Example

For the astroid-envelope topic, the approved scene and asset are:

- Scene: `topics/astroid-envelope/scenes/chatgpt_outro.py`
- Asset: `assets/brand/chatgpt_logo_line.svg`
- Low-quality preview path: `topics/astroid-envelope/exports/manim/videos/chatgpt_outro/480p15/ChatGPTOutro.mp4`
- High-quality render path: `topics/astroid-envelope/exports/manim/videos/chatgpt_outro/1080p60/ChatGPTOutro.mp4`
