---
name: video-topic-bootstrap
description: Use when starting a new math video topic, creating or normalizing a topic workspace, drafting the first topic outline, rebuilding a missing outline from existing materials, or making story/script/scene changes that require the topic outline to stay synchronized.
---

# Video Topic Bootstrap

Use this skill as the project entry point for a new video topic, or whenever an existing topic lacks a current outline.

## Core Rule

Every substantial video topic must have a maintained outline before narration, scene implementation, preview rendering, or final release work continues.

The outline is not a one-time draft. Update it in the same work session whenever the audience promise, chapter order, derivation path, visual plan, narration structure, or final output status changes.

## Startup Workflow

1. Read `README.md`, `docs/workflow.md`, and the closest existing topic docs before creating a new topic.
2. Choose a stable lowercase slug for `topics/<topic>/`. Prefer concise English words joined by hyphens.
3. Check whether the topic directory already exists. If it exists, preserve user files and normalize only missing structure.
4. Create or verify these directories: `audio`, `docs`, `exports`, `exports/final`, `exports/covers`, and `scenes`. Add `timeline` or renderer-specific folders only when the topic needs them.
5. Create `topics/<topic>/docs/<topic_slug_with_underscores>_outline.md` for new topics. If an existing topic already uses `docs/outline.md`, keep that convention instead of renaming casually.
6. Create or update `topics/<topic>/docs/design_notes.md` for topic-specific decisions, critique, and reusable lessons.
7. Use `math-video-outline` to draft or revise the creative outline before writing final narration.

## Outline Contents

Keep the outline practical and synchronized with production. Include:

- Topic title, slug, status, and last-updated date.
- Audience promise: what the viewer should understand by the end.
- Hook: the concrete scene, question, or surprise that opens the video.
- Chapter beats with intended visuals and rough timing when known.
- Math path: variables, assumptions, derivation breadcrumbs, and reveal order.
- Risk points where viewers may need an extra bridge or visual anchor.
- Narration/source artifacts and current preview/final output paths after they exist.
- Open decisions or next edits, if the topic is still in progress.

## Keeping The Outline Current

Update the outline when any of these changes:

- The hook, audience promise, chapter order, or conclusion.
- A derivation step is added, removed, split, or reworded.
- Visual explanation changes the viewer's order of discovery.
- Narration/SRT timing changes chapter boundaries or pacing.
- A preview or final render becomes the current reference output.
- User feedback resolves or replaces a prior story/design decision.

If a change is purely implementation detail, such as fixing a typo in code or rerunning the same render, a design note is optional and the outline may stay unchanged.

## Handoff To Other Skills

- Use `math-video-outline` for hook quality, chapter flow, analogies, and derivation clarity.
- Use `narration-script-review` before TTS or SRT generation.
- Use `story-state-timeline-review` when screen text, narration, or visuals may reveal information too early.
- Use `manim-scene-iteration` while implementing and iterating Manim scenes.
- Use `render-preview-pipeline` for preview/final render, muxing, covers, and validation.
- Use `project-self-evolution` after user critique to update global rules, topic notes, or this skill.

## Safety

- Do not delete or rename existing topic files just to match the preferred structure.
- Do not let a topic proceed as "current" with only scattered narration, scenes, or final videos and no outline.
- Keep durable production facts in the outline; keep one-off implementation commands in `design_notes.md` or task notes.
