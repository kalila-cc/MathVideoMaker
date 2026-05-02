---
name: hybrid-video-overlay
description: Use when a math video segment needs mixed rendering, such as keeping Manim responsible for the consistent background, title, formulas, and typography while rendering local dynamic UI/cards/diagrams with Remotion or another renderer and compositing them back into a Manim-generated video. Trigger this for background color mismatches between renderers, transparent overlay workflows, local segment-only iteration, alpha-video debugging, or FFmpeg overlay composition in this project.
---

# Hybrid Video Overlay

Use this skill to build a topic-local test segment from a Manim shell and a transparent dynamic overlay. The goal is to preserve Manim's visual system while using Remotion for local UI or high-frequency dynamic content.

## Decision

Use this workflow when:

- A Remotion/native segment visibly changes the page background compared with adjacent Manim chapters.
- Only a local dynamic region needs a non-Manim renderer, such as dashboards, sliders, code cards, or canvas-like motion.
- Manim should remain the source of truth for title text, global background, bottom formulas, and formula fonts.

Avoid it when a scene can be rendered cleanly in one renderer without style drift.

## Architecture

Split the segment into two synchronized videos:

- **Manim shell**: background color, title/subtitle, bottom formula, narration-aligned static text, and any global chapter framing.
- **Transparent overlay**: cards, charts, interactive-looking controls, curves, markers, code snippets, and other local dynamic content.

Keep both at the same width, height, fps, and duration. For this project the common target is `1920x1080`, `60 fps`, topic-local outputs under `topics/<topic>/exports/...`.

## Implementation Steps

1. Add a Manim shell scene beside the original segment scene.
   - Set `self.camera.background_color` to the same project `BG`.
   - Use the existing title helper, `MathTex` template, and topic typography.
   - Let Manim own bottom formulas when font parity matters. In this project `MathTex` uses `mathptmx`, and `LATIN_FONT` is `Times New Roman`.
   - Keep the shell duration equal to the target segment duration with the topic's `finish_to(...)` helper.

2. Refactor the Remotion segment into reusable content and a transparent overlay composition.
   - Extract card/dynamic content into a component such as `ProgrammingLinksCards`.
   - Keep the original full-frame composition if still useful for comparison.
   - Add a second composition such as `ProgrammingLinksOverlay1080` whose root `AbsoluteFill` has `background: "transparent"`.
   - Ensure global CSS does not force a background:

```css
:root {
  background: transparent;
}

body {
  margin: 0;
  overflow: hidden;
  background: transparent;
}
```

3. Do not render transition/background/title/bottom formula in the overlay.
   - The overlay should be visually empty outside the local dynamic elements.
   - Align panels and card dimensions in pixel coordinates against the Manim shell.
   - If overlay labels must match math notation, use `fontFamily: "'Times New Roman', Times, serif"` and italic styling for point labels or formulas.
   - If the global Manim background, grid, title, or bottom formula changes later, rerender the shell and recomposite the official hybrid segment before concatenating the final video. A previously approved overlay can stay unchanged, but the base shell cannot be reused after global visual-system changes.

## Rendering Commands

Render the Manim shell:

```powershell
.\scripts\render_scene.ps1 `
  -SceneFile topics\<topic>\scenes\<scene_file>.py `
  -SceneName <HybridShellScene> `
  -Quality "-qh"
```

Render the transparent overlay. Prefer ProRes 4444 for reliable alpha in the local FFmpeg pipeline:

```powershell
npx remotion render src/index.ts <OverlayComposition> `
  ..\exports\final\<OverlayName>_1080p60_alpha.mov `
  --image-format=png `
  --pixel-format=yuva444p10le `
  --codec=prores `
  --prores-profile=4444 `
  --overwrite
```

Do not rely on VP9 WebM alpha for this workflow unless it is explicitly revalidated. In prior testing, WebM carried `alpha_mode=1` but decoded as an opaque full-frame layer during FFmpeg overlay composition.

Composite into a separate test MP4 first:

```powershell
$ffmpeg = Join-Path (Get-Location) "tools\ffmpeg\bin\ffmpeg.exe"
$base = "topics\<topic>\exports\manim\videos\<scene_file_stem>\1080p60\<HybridShellScene>.mp4"
$overlay = "topics\<topic>\exports\final\<OverlayName>_1080p60_alpha.mov"
$out = "topics\<topic>\exports\final\<HybridName>_test_1080p60_silent.mp4"

& $ffmpeg -y -i $base -i $overlay `
  -filter_complex "[0:v]format=rgba[base];[1:v]format=rgba[ov];[base][ov]overlay=0:0:format=auto:shortest=1,format=yuv420p[v]" `
  -map "[v]" -an -c:v libx264 -preset medium -crf 18 -movflags +faststart $out
```

Only replace the official segment or update gallery metadata after visual approval.

## Alpha Validation

Before a full rerender, test a still from the overlay:

```powershell
npx remotion still src/index.ts <OverlayComposition> `
  ..\exports\final\<OverlayName>_alpha_probe.png `
  --frame=<frame_number> `
  --image-format=png `
  --overwrite

& $ffmpeg -y -i "topics\<topic>\exports\final\<OverlayName>_alpha_probe.png" `
  -vf alphaextract -frames:v 1 -update 1 `
  "topics\<topic>\exports\final\<OverlayName>_alpha_probe_alpha.png"
```

Interpret the extracted alpha image:

- Black: transparent area, should show Manim shell after composition.
- White/gray: visible overlay content.
- Full white frame: the overlay is still opaque, usually due to CSS or a full-screen background element.

## QA Checklist

- Render/test only the segment under discussion before touching remaining chapters.
- Confirm the test MP4 is video-only when building a silent segment.
- Extract frames at the beginning, around the formula entrance, and during peak motion:

```powershell
& $ffmpeg -y -ss 23 -i $out -frames:v 1 -update 1 "topics\<topic>\exports\final\hybrid_test_frames\frame_023s.png"
```

- Check that Manim title, background, and formulas remain visible.
- Check that card bottoms do not collide with Manim formula panels.
- Check that left and right cards use identical top and height values.
- After recomposition, extract at least one frame from the preceding Manim-only chapter and one frame from the hybrid chapter to confirm background color, grid spacing, and overlay transparency still match.
- Keep generated `.mov`, `.mp4`, debug frames, and probes out of commits unless the user explicitly asks to publish artifacts.
