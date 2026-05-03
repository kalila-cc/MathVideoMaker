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
- Keep the TTS rate consistent within one topic. Use the topic notes if they specify a rate; otherwise start from `--rate +14%` for these Chinese math videos and do not silently fall back to `+0%`.
- After any narration rewrite, regenerate the MP3 and SRT together, then realign Manim scene waits to the new SRT boundaries. Replacing only the audio is a common cause of segment titles, visuals, and voiceover drifting apart.
- For enumerated cases or step-by-step rules, align each narrated point to the exact visual beat where that point appears. If one TTS pass cannot create reliable boundaries, generate separate audio/SRT clips per point and place them at fixed offsets with silence between them.
- If a branded intro or silent lead-in precedes the narration, measure the actual rendered intro duration for the target quality and use it for mux delay and segmented-preview `audioDelay`; low-quality and high-quality renders can differ by a few frames.
- For narration that references concrete visual state, such as entering a new scene, looking at the right panel, seeing a marked difference, or reaching a numeric milestone, extract key frames at those timestamps and verify the stated object or value is already visible.
- When adding or removing a slate, bridge, or segment, rebuild the combined SRT with the new offsets instead of manually trusting old chapter timings.
- For symbolic point labels followed by Chinese function words, avoid phrases that can merge into quantity words, such as `P 二对...` being read like `P 两对...`. Rephrase as `P 二影响...`, `P 二这个点...`, or add a clear noun after the label.
- Avoid compact compounds that Chinese TTS may split awkwardly after symbolic labels, such as `后半段`. Prefer `曲线后面`, `后面这一段`, or `靠近终点的一侧` when the visual meaning allows it.

## Commands

```powershell
.\.venv\Scripts\python scripts\make_voice.py --text-file topics\<topic>\audio\narration.txt --out topics\<topic>\audio\preview.mp3 --srt topics\<topic>\audio\preview.srt --rate +14%
```

Write generated MP3/SRT next to the narration text in the same topic `audio/` directory. After generation, inspect the SRT boundaries and align Manim scene durations to them.
