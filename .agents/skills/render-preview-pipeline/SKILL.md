---
name: render-preview-pipeline
description: Use when rendering, concatenating, muxing audio, validating, or preparing low-quality preview/final videos in this project.
---

# Render Preview Pipeline

Use this skill for end-to-end preview generation.

## Standard Flow

1. Render low-quality scene clips first.
2. For fast local iteration, optionally register those clips in `data/videos.json` as a `segments` virtual preview and inspect them in the gallery before concatenating. If the clips are silent, attach the narration with `audio` and align it with `audioDelay`.
3. During segmented-preview review, update only the changed scene clips and metadata. Do not regenerate the complete concatenated MP4 after every segment tweak; wait until the overall chapter flow is close to approved.
4. Concatenate clips into a silent MP4 when the segmented preview is approved enough for whole-video review.
5. Mux narration audio into the video.
6. Generate a readable local cover separately from the video timeline. Default to one high-resolution, mobile/feed-first cover; only make separate desktop/mobile variants or low-resolution check images if the user explicitly asks.
7. Verify duration, audio presence, and local gallery metadata.
8. Only render final high quality after the low-quality preview is approved.

Keep outputs topic-local:

- Manim intermediate clips: `topics/<topic>/exports/manim/videos/...`
- Silent or muxed previews: `topics/<topic>/exports/final/...`
- Generated local covers: `topics/<topic>/exports/covers/...`
- Auto posters: `topics/<topic>/exports/posters/...`

## Commands

```powershell
.\scripts\render_scenes_parallel.ps1 -SceneFile topics\astroid-envelope\scenes\astroid_envelope_v6.py -SceneNames CoverFrame,StoryHook,VariablesMatter -MaxParallel 3

.\.venv\Scripts\python scripts\concat_videos.py --out topics\astroid-envelope\exports\final\example_silent.mp4 --overwrite path\to\clip1.mp4 path\to\clip2.mp4

.\.venv\Scripts\python scripts\add_audio.py --video topics\astroid-envelope\exports\final\example_silent.mp4 --audio topics\astroid-envelope\audio\narration.mp3 --out topics\astroid-envelope\exports\final\example_with_audio.mp4 --overwrite

.\.venv\Scripts\python scripts\generate_cover.py --video topics\astroid-envelope\exports\final\example_with_audio.mp4 --time 0.100 --out topics\astroid-envelope\exports\covers\example_cover.jpg --overwrite --update-metadata
```

## Validation

- Use FFmpeg to confirm video duration and audio stream.
- For videos with timeline drift or dense narration/animation sync, maintain a topic-local timeline config and run `scripts/build_timeline_index.py --config <config> --check` after rendering changed clips. Use `--search <text>` to locate where a visual beat and matching SRT cue appear on the accumulated whole-video timeline.
- When narration is shortened, a derivation is collapsed, or a scene duration changes, rebuild the accumulated timeline before judging sync. Downstream chapter offsets, gallery chapter metadata, and case-by-case comparison beats can all become stale even if the final MP4 duration looks plausible.
- When a branded intro or silent pre-roll precedes narration, measure the actual rendered intro clip for each quality and use that duration for sync. HD mux delay and segmented-preview `audioDelay` may differ because 60 fps and 15 fps renders round to different clip lengths; do not reuse an old nominal delay after changing the intro.
- When muxing delayed narration after an intro, prefer `adelay=<intro_ms>:all=1` with an explicit `-t <final_video_duration>` measured from the silent master. Avoid relying on `apad + -shortest` if FFmpeg appears to hang.
- If a final MP4 includes an intro delay, generate a final SRT with every cue shifted by the same measured delay, and update gallery chapters by the same offset.
- For final release, rerender high-quality clips from the current scene source; do not reuse an older HD MP4 after visual or narration fixes.
- When rendering multiple Manim scenes in parallel, avoid sharing one writable `media_dir` for scenes that create `Text`/`MathTex` during animation. Manim hashes text into shared SVG files and may use non-unique temporary parse files; if a text-cache race appears, rerender the affected scene serially or isolate each scene's `media_dir` and copy only the final MP4 back.
- Keep the new final MP4 until it passes resolution, frame-rate, duration, audio, cover, and gallery checks; only then clean old outputs.
- After final approval, prune the topic outputs down to the final MP4, the one cover referenced by final metadata, and any final narration/SRT files worth preserving. Remove old low-quality previews, segmented preview entries, silent masters, Manim render caches, debug frames, generated posters, stale covers, and obsolete MP3/SRT drafts.
- Treat generated covers like other build artifacts during final cleanup: keep only the final cover for the accepted video unless the user explicitly asks to preserve variants.
- Before recursive cleanup, resolve the target paths and verify they are inside `topics/<topic>/exports` or the explicitly named topic `audio` directory.
- The current environment may not expose global `ffmpeg` or `ffprobe`. Prefer `tools\ffmpeg\bin\ffmpeg.exe` when present; otherwise use `.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe -hide_banner -i <video>` to inspect streams.
- Do not keep a cover frame in the final video just for thumbnail capture. Render cover art as a separate scene or image, export one mobile/feed-first JPG into `topics/<topic>/exports/covers`, and reference it from metadata.
- When the final video starts with ChatGPT branding, render the topic cover from `CoverFrame` or another topic-specific cover source; do not use the branding slate as the gallery cover.
- Do not commit generated MP4, MP3, poster, or cover files.
- Prefer project-local `tools\ffmpeg\bin\ffmpeg.exe`.
- Playwright may have the package installed but no browser binary. For gallery QA, use an already installed Chrome/Edge executable path instead of installing browsers during the task.
