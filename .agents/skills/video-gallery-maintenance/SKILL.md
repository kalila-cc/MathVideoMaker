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
- `covers`: explicit `desktop` and `mobile` image paths when automatic poster extraction is not good enough. Keep `cover` as a desktop fallback for older gallery code.
- `chapters`: fine-grained `{title,start,end}` entries for jump controls.
- `segments`: optional explicit list of MP4 scene clips for a virtual segmented preview. Use this when a local preview should behave like one complete video before concat/mux has been run.
- `audio` and `audioDelay`: optional narration MP3 and timeline delay for segmented previews, because raw Manim scene clips often have no audio stream.
- Avoid writing Chinese metadata through PowerShell stdin/here-strings; use UTF-8 files or Unicode escapes, then read `data/videos.json` back with Python to confirm titles and descriptions are not garbled.
- Final entries should use public-facing metadata: clean title, final status, topic tags, and stable description. Remove iteration labels such as `v10`, `低清预览`, `字体试用`, or platform/build notes unless they are genuinely part of the published title.

## Gallery Behavior

- Keep chapter controls close to the main player.
- Prefer generated explicit covers for important videos; automatic posters can catch black frames.
- Generate and store desktop and mobile/feed covers separately under `topics/<topic>/exports/covers`. The gallery should use the desktop cover on wide viewports and the mobile cover on narrow/mobile viewports.
- Local deletion must only target MP4 files inside configured export roots.
- After deleting videos, also prune generated posters and stale metadata.
- Prefer topic-local paths, such as `topics/astroid-envelope/exports/final/video.mp4` and `topics/astroid-envelope/exports/covers/cover.jpg`.
- The gallery scans only complete-video roots such as `topics/*/exports/final`, with legacy root `exports/final` as a migration fallback. Do not show Manim scene drafts from `exports/manim/videos` unless the user explicitly asks for segment debugging.
- The gallery should skip silent intermediate masters such as `*_silent.mp4` and `*_silent_master.mp4`; these are build artifacts, not review targets.
- Scene draft clips can still be previewed as one logical video when they are explicitly listed in a metadata `segments` entry. These segmented entries are non-deletable in the gallery and do not create a new MP4. Add `audio` when the scene clips are silent and the preview needs narration.
- Generated covers live at `topics/<topic>/exports/covers` and are ignored by Git. Metadata may reference them even though the image files themselves are local generated assets.
- Generated posters live beside their topic at `topics/<topic>/exports/posters`.
- Final gallery cleanup should leave only complete videos intended for preview; silent masters, Manim scene drafts, old previews, render logs, stale covers, and orphan posters should be removed after the new final passes validation.
- After a final entry is accepted, prune old preview and segmented metadata for the same topic so the gallery does not present stale versions as current work.
- Default gallery ordering should be newest `modified` time first. Treat `priority` as a tie-breaker or metadata hint, not the primary display order.

## Troubleshooting

- On Windows, `serve_videos.py --stop` can fail with `WinError 87` if the PID file is stale. Check the actual listener with `Get-NetTCPConnection -LocalPort 8765 -State Listen`, stop that process if needed, and restart the service.
- If `rg` fails with `Access is denied`, use PowerShell `Select-String` as a fallback search tool for the current turn.

## Cleanup Commands

```powershell
.\.venv\Scripts\python scripts\clean_generated_videos.py --preset old-astroid-iterations --preset manim-partials --delete-orphan-posters --prune-metadata
.\.venv\Scripts\python scripts\clean_generated_videos.py --preset old-astroid-iterations --preset manim-partials --delete-orphan-posters --prune-metadata --execute
```

## Service

```powershell
.\.venv\Scripts\python scripts\serve_videos.py
```
