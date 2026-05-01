---
name: project-self-evolution
description: Use after user feedback on generated math videos, previews, narration, visual design, derivation clarity, timing, gallery UX, or project workflow to extract reusable lessons and update docs, topic notes, scripts, or local skills so future video creation improves.
---

# Project Self Evolution

Use this skill to make the project learn from each video iteration.

## Feedback Capture

When the user gives critique or improvement suggestions, actively extract reusable lessons before moving on.

Classify each point:

- Story and hook: opening, audience curiosity, pacing, chapter flow.
- Explanation clarity: variable introduction, analogy, derivation bridges, missing steps.
- Visual language: layout, typography, formula formatting, motion, labels, cover frame.
- Narration and TTS: spoken tone, pronunciation, chapter wording, SRT alignment.
- Render pipeline: low-quality preview, parallel rendering, audio muxing, covers.
- Gallery UX: metadata, title, description, chapter jumps, delete behavior.
- Project structure: topic paths, cleanup rules, reusable scripts.

## Distillation

For each critique, write a reusable principle in this shape:

- Problem observed: what made the current video weaker.
- Better rule: what future videos should do.
- Where to encode it: `docs/creative_quality_principles.md`, topic notes, a specific skill, or a script.

Do not merely copy user wording. Compress it into transferable guidance that can improve a different video later.

## Durable Homes

- Put global creative rules in `docs/creative_quality_principles.md`.
- Put topic-specific lessons in `topics/<topic>/docs/design_notes.md`.
- Update specialized skills when the behavior should trigger during future work:
  - `math-video-outline` for hooks, analogies, chapter flow, and explanation bridges.
  - `manim-scene-iteration` for visual layout, labels, formula typography, and cover frames.
  - `narration-tts-sync` for spoken tone, pronunciation, SRT, and timing.
  - `render-preview-pipeline` for low-quality preview, muxing, verification, and parallel rendering.
  - `video-gallery-maintenance` for metadata, covers, chapters, and local deletion UX.
- Use README only as a navigation page.
- Use scripts only when a repeated manual check should become deterministic automation.

## Iteration Loop

1. Review the latest feedback and identify what is one-off versus reusable.
2. Update the smallest durable home that will affect future work.
3. Remove stale or contradictory guidance instead of appending forever.
4. Keep skills concise and action-oriented.
5. Validate docs, scripts, and skill frontmatter.
6. Report what changed and which future behavior it improves.

## Quality Memory Checklist

Before starting a new substantial video, check whether the current plan obeys the accumulated quality memory:

- Does the opening start from a concrete scene or question instead of a formula?
- Are new variables visually tied to physical quantities before they appear in formulas?
- Are derivation jumps bridged with an intermediate visual or algebraic step?
- Is narration relaxed and human, avoiding production-language titles?
- Are formula typography, Latin letters, and numeric text visually professional?
- Is the first frame a short readable cover, not a long pause or black preview?
- Are low-quality preview, audio sync, cover, metadata, and chapter jumps verified before final render?

## Validation

After edits, run the lightest relevant checks:

- Parse Python scripts with `python -B -m py_compile`.
- Parse PowerShell scripts with `System.Management.Automation.Language.Parser`.
- Check skill frontmatter has only `name` and `description`.
- Scan docs and scripts for stale root paths unless intentional legacy fallbacks.
- Remove temporary `__pycache__` created by validation.

## Safety

- Do not delete source scenes, narration drafts, topic docs, or metadata unless explicitly requested.
- Prefer dry-run cleanup before destructive cleanup.
- If a lesson only affects one video, keep it in that topic's design notes instead of global quality rules.
