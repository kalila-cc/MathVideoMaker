---
name: narration-tts-sync
description: Use when writing Chinese narration, generating TTS audio/SRT, fixing pronunciation, or syncing voiceover with rendered video.
---

# Narration TTS Sync

Use this skill for files under `topics/<topic>/audio/` and narration timing.

## Writing Rules

- Write natural spoken Chinese, not textbook narration.
- Keep one paragraph per major visual beat.
- Avoid saying "第几章" in the voiceover.
- Use daily-life phrasing before formal math language.

## Pronunciation

For TTS, write trigonometric names as full English words in the narration text when needed:

- `sine` instead of `sin`
- `cosine` instead of `cos`
- `secant` instead of `sec`
- `cosecant` instead of `csc`
- `tangent` instead of `tan`
- `cotangent` instead of `cot`

The video can still display standard formula abbreviations with `MathTex`.

Avoid isolated Chinese polyphones that edge-tts may misread. Prefer unambiguous spoken wording:

- Use `变量` or `符号` instead of an isolated `量` in phrases like `几个量`.
- Use `物理量`, `数值`, `长度`, or `高度` when that is the intended meaning.
- After changing wording for pronunciation, regenerate both MP3 and SRT so scene timing remains aligned.

## Commands

```powershell
.\.venv\Scripts\python scripts\make_voice.py --text-file topics\<topic>\audio\narration.txt --out topics\<topic>\audio\preview.mp3 --srt topics\<topic>\audio\preview.srt --rate +14%
```

Write generated MP3/SRT next to the narration text in the same topic `audio/` directory. After generation, inspect the SRT boundaries and align Manim scene durations to them.
