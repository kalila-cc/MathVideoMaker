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

## Gallery Behavior

- Keep chapter controls close to the main player.
- Prefer generated explicit covers for important videos; automatic posters can catch black frames.
- Local deletion must only target MP4 files inside configured export roots.
- After deleting videos, also prune generated posters and stale metadata.
- Prefer topic-local paths, such as `topics/astroid-envelope/exports/final/video.mp4` and `topics/astroid-envelope/exports/covers/cover.jpg`.
- The gallery scans `topics/*/exports/final` and `topics/*/exports/manim/videos`, with legacy root `exports/` paths only as a migration fallback.
- Generated covers live at `topics/<topic>/exports/covers` and are ignored by Git.
- Generated posters live beside their topic at `topics/<topic>/exports/posters`.

## Cleanup Commands

```powershell
.\.venv\Scripts\python scripts\clean_generated_videos.py --preset old-astroid-iterations --preset manim-partials --delete-orphan-posters --prune-metadata
.\.venv\Scripts\python scripts\clean_generated_videos.py --preset old-astroid-iterations --preset manim-partials --delete-orphan-posters --prune-metadata --execute
```

## Service

```powershell
.\.venv\Scripts\python scripts\serve_videos.py
```
