---
name: video-gallery-maintenance
description: Use when updating the local video gallery, data/videos.json metadata, covers, chapter jump points, cleanup scripts, or local video deletion behavior.
---

# Video Gallery Maintenance

Use this skill for `scripts/serve_videos.py`, `data/videos.json`, `topics/<topic>/exports/`, and generated video cleanup.

## Metadata

Each important video should have:

- `title`: readable title for the gallery.
- `description`: what this version demonstrates or fixes.
- `topic`, `tags`, `status`, `priority`.
- `cover`: explicit image path when automatic poster extraction is not good enough.
- `chapters`: fine-grained `{title,start,end}` entries for jump controls.
- Avoid writing Chinese metadata through PowerShell stdin/here-strings; use UTF-8 files or Unicode escapes, then read `data/videos.json` back with Python to confirm titles and descriptions are not garbled.

## Gallery Behavior

- Keep chapter controls close to the main player.
- Prefer generated explicit covers for important videos; automatic posters can catch black frames.
- Local deletion must only target MP4 files inside configured export roots.
- After deleting videos, also prune generated posters and stale metadata.
- Prefer topic-local paths, such as `topics/astroid-envelope/exports/final/video.mp4` and `topics/astroid-envelope/exports/covers/cover.jpg`.
- The gallery scans only complete-video roots such as `topics/*/exports/final`, with legacy root `exports/final` as a migration fallback. Do not show Manim scene drafts from `exports/manim/videos` unless the user explicitly asks for segment debugging.
- Generated covers live at `topics/<topic>/exports/covers` and are ignored by Git.
- Generated posters live beside their topic at `topics/<topic>/exports/posters`.
- Final gallery cleanup should leave only complete videos intended for preview; silent masters, Manim scene drafts, old previews, render logs, stale covers, and orphan posters should be removed after the new final passes validation.

## Cleanup Commands

```powershell
.\.venv\Scripts\python scripts\clean_generated_videos.py --preset old-astroid-iterations --preset manim-partials --delete-orphan-posters --prune-metadata
.\.venv\Scripts\python scripts\clean_generated_videos.py --preset old-astroid-iterations --preset manim-partials --delete-orphan-posters --prune-metadata --execute
```

## Service

```powershell
.\.venv\Scripts\python scripts\serve_videos.py
```
