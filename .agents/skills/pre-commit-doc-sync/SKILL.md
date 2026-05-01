---
name: pre-commit-doc-sync
description: Use before committing changes in this project to inspect staged and unstaged diffs, identify whether README/docs/topic notes/skills/metadata need updates, and list the exact file paths that must be checked so implementation and documentation do not drift apart.
---

# Pre Commit Doc Sync

Use this skill immediately before creating or amending a commit.

## Diff First

Inspect both staged and unstaged changes:

```powershell
git status --short
git diff --stat
git diff --cached --stat
git diff
git diff --cached
```

If the commit is already staged, treat `git diff --cached` as the source of truth. If there are unstaged edits that belong to the same change, include them or call them out.

## Documentation Decision

For every changed path, decide whether docs or skills must change:

- `scripts/*.py` or `scripts/*.ps1`: check command examples, workflow docs, README script list, and relevant skills.
- `serve_videos.py`, `data/videos.json`, covers, posters, chapter logic, delete behavior: check gallery docs and `video-gallery-maintenance`.
- `topics/<topic>/scenes/*`: check topic design notes, workflow docs, and `manim-scene-iteration`.
- `topics/<topic>/audio/*`: check topic notes, TTS guidance, and `narration-tts-sync`.
- `.gitignore`, `.gitattributes`, generated assets, cleanup behavior: check README maintenance rules and gallery cleanup docs.
- `.agents/skills/*`: check README skills list and overlap with existing skills.
- `README.md` or `docs/*`: check links, stale duplicated content, and whether README should stay concise.

If no documentation update is needed, record why.

## Required Path Checklist

Always check these project entry points:

- `README.md`
- `docs/workflow.md`
- `docs/gallery_and_cleanup.md`
- `docs/creative_quality_principles.md`
- `data/videos.json`
- `.gitignore`
- `.gitattributes`
- `.agents/skills/*/SKILL.md`

Check topic-specific files when the diff touches that topic:

- `topics/<topic>/docs/design_notes.md`
- `topics/<topic>/docs/*.md`
- `topics/<topic>/scenes/*.py`
- `topics/<topic>/audio/*_narration.txt`
- `topics/<topic>/audio/*.srt`

## Generated Asset Guard

Before commit, verify generated files are not tracked unless intentionally small and source-like:

```powershell
git ls-files | Select-String -Pattern 'exports/covers|exports/final|exports/manim|exports/posters|\.jpg$|\.mp4$|\.mp3$|\.wav$|\.pid$|^tools/|^\.venv/'
```

Expected: no matches. SRT files and narration text may be tracked because they preserve timing and script intent.

## Validation

Run the lightest checks relevant to changed files:

- Python scripts: `python -B -m py_compile`.
- PowerShell scripts: parse with `System.Management.Automation.Language.Parser`.
- Markdown links in touched docs: verify relative targets exist.
- Skills: verify frontmatter contains only `name` and `description`.
- Git ignore: use `git check-ignore -v <path>` for representative generated files.

Remove any `__pycache__` created by validation.

## Commit Readiness Output

Before committing, report:

- Changed implementation paths.
- Documentation paths checked.
- Documentation updates made or intentionally skipped.
- Generated assets confirmed ignored.
- Validation commands run.
