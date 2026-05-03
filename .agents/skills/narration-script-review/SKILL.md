---
name: narration-script-review
description: Review Chinese math popular-science narration drafts immediately after the script is written and before generating TTS audio/SRT. Use for topic audio narration files or pasted narration text to check chapter clarity, conversational tone, opening hook, accessible analogies, likely Chinese polyphone mistakes, and formula wording that may be misread by TTS.
---

# Narration Script Review

Use this skill as the gate before running `scripts/make_voice.py`.

## Workflow

1. Read the narration draft and identify the intended chapter or visual beats.
2. Review the draft against the checklist below.
3. If issues are found, edit the narration file directly when the user asked for implementation; otherwise provide concrete rewrite suggestions.
4. Do not generate TTS until blocking narration issues are resolved.
5. After edits that affect spoken text, regenerate both MP3 and SRT with `narration-tts-sync`.

## Review Checklist

- Chapter clarity: The script should have clear content progression, usually one paragraph per visual beat or chapter. The voiceover should not say "第几章"; chapter labels belong to the video UI or screen.
- Conversational tone: Prefer relaxed spoken Chinese, as if explaining to one curious person. Avoid textbook phrasing, production notes, and stiff transitions like "接下来我们将".
- Opening hook: The first 5-15 seconds should start from a concrete scene, surprising phenomenon, or natural question. Avoid opening with formulas, definitions, or assumptions about what the audience is thinking.
- Accessible analogy: Abstract math should have a physical image, daily-life metaphor, or visual anchor before formal language. Assume the audience does not have advanced math background.
- Variable grounding: New symbols should be tied to visible objects or real quantities before they are used in equations.
- Derivation clarity: Do not let the narration skip complex algebra. When a result depends on decomposition, substitution, projection, cancellation, differentiation, or simultaneous conditions, the script should state the intermediate step and why it is valid before naming the result.
- Local task: Before a derivation starts, the narration should state what is being solved, such as finding a ray's line equation or an envelope condition. Do not assume the viewer can infer the task from a vague title.
- Formula purpose: When a formula is rewritten into a new form, the narration should say why that form is being used, such as making a family of curves comparable, enabling a derivative condition, or preparing for an envelope calculation.
- Envelope derivative: If the script uses `\partial F/\partial t=0`, it must say which variables are fixed and why this is not differentiating the constant equation `F=0`. A concise explanation is enough when the screen adds a small note.
- Formula narration: Spoken text should describe formulas in TTS-safe words, while the screen can still show compact mathematical notation.
- TTS polyphones: Avoid `行` when referring to formula rows, such as `这一行` or `最后那行`; use `这个式子`, `这条等式`, or `屏幕上的这一步` instead. `平行` is fine when the intended reading is `xing2`.
- Polyphone risk: Rewrite ambiguous Chinese words that edge-tts may misread.
- Cognitive load: When a paragraph mentions a specific equation among many visible formulas, ensure the scene plan highlights that expression.

## TTS-Safe Formula Wording

- Use `sine`, `cosine`, `secant`, `cosecant`, `tangent`, `cotangent` in narration text when abbreviations may be read incorrectly.
- Say powers naturally: "三次方", "平方", "三分之二次方"; avoid raw strings like `L^(2/3)` in narration.
- Say fractions and division explicitly: "x 除以 a", "三分之二", "括号里 x 除以 L".
- Say equation roles before compact symbols: "这个点在这根棍子上，所以 F 等于 0" is clearer than only reading `F=0`.
- Keep displayed formulas standard in `MathTex`; only the narration text needs TTS-safe wording.

## Polyphone Watchlist

Prefer unambiguous wording over hoping TTS guesses correctly:

- `量`: use `变量`, `物理量`, `数值`, `长度`, or `高度`.
- `行`: use `一排`, `直线`, `可以`, or another specific phrase.
- `重`: use `重新`, `重复`, `重量`, or `重要`.
- `长`: use `长度`, `变长`, `很长`, or `生长`.
- `得`: use `得到`, `必须`, `跑得快`, or rewrite the phrase.
- `为`: use `作为`, `因为`, `变成`, or `等于`.
- `数`: use `数字`, `函数`, `倒数`, `数值`, or `数量`.

When in doubt, rewrite the sentence so pronunciation is determined by context.

## Required Output

Return a compact review with:

- Verdict: `Ready for TTS` or `Needs revision`.
- Blocking issues: Only items that can cause misunderstanding or bad TTS output.
- Suggested rewrites: Provide replacement Chinese lines, not just critique.
- Formula read-aloud fixes: List formula snippets and safer spoken wording.
- Polyphone fixes: List risky words and replacements.

If the user asked you to update the file, make the edits and report the changed path plus validation performed.
