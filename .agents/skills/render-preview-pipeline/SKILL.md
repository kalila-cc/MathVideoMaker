---
name: render-preview-pipeline
description: Use when rendering, concatenating, muxing audio, validating, or preparing low-quality preview/final videos in this project.
---

# Render Preview Pipeline

Use this skill for end-to-end preview generation.

## Standard Flow

1. Render low-quality scene clips first.
2. Concatenate clips into a silent MP4.
3. Mux narration audio into the video.
4. Generate a readable local cover from the short cover frame.
5. Verify duration, audio presence, and local gallery metadata.
6. Only render final high quality after the low-quality preview is approved.

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
- If the first frame is just for thumbnail capture, keep it short and add the remaining time to the real opening scene.
- Do not commit generated MP4, MP3, poster, or cover files.
- Prefer project-local `tools\ffmpeg\bin\ffmpeg.exe`.
