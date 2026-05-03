---
name: story-state-timeline-review
description: Review Chinese video narration, subtitles, screen text, and animation scripts for audience-known-information continuity. Use before TTS/rendering or after preview feedback when a script may mention names, motives, conclusions, math interpretations, character actions, or metaphor labels before the viewer has actually seen or heard enough to know them.
---

# Story State Timeline Review

Use this skill as a gate after writing narration and animation scripts, and before final TTS/rendering. The goal is to prevent "writer knowledge" from leaking into viewer-facing text too early.

## Core Rule

At any timecode, narration and screen text may only rely on information the viewer can already perceive from earlier or current frames:

- Visible objects, actions, labels, and changes on screen.
- Spoken names, rules, motives, or interpretations already introduced.
- Patterns the viewer has had enough repetitions to notice.

Do not treat code variables, future reveals, author intent, math meaning, or later scene concepts as viewer-known information.

## Workflow

1. Collect the narration draft, SRT if available, animation script, screen text strings, and key frames if the issue comes from a rendered preview.
2. Build a compact timeline table with these columns:
   - `time/beat`
   - `viewer can know now`
   - `new information introduced`
   - `terms/actions now allowed`
   - `terms/actions still forbidden`
3. Audit every narration line, subtitle, title, label, and on-screen callout against the timeline.
4. Mark a line as blocking if it uses information before introduction, asks the viewer to react in a way the scene has not earned, or names a conclusion before the visual evidence exists.
5. Rewrite blocking lines using only observable information from that beat, or move the reveal later.
6. If the user asked for implementation, edit the script/source files directly and then rerun the relevant preview step.

## What To Catch

- Character leakage: mentioning a character name, intention, behavior rule, or action before the character appears or is named.
- Premature conclusion: using words like "答案", "加法器", "规律", "秩序", "混沌", "进位", or "读写" before the scene has built the visual basis for that concept.
- Unmotivated audience framing: saying "别急着下结论", "你可能以为", or "继续看" unless the previous beat clearly created that expectation.
- Future-scene leakage: using terms from the next segment in a bridge before those objects have appeared.
- Negative framing leakage: do not say "先不看 X", "暂时不把它当成 X", or "别急着叫它 X" before X has appeared or become a natural viewer thought. Negating an unintroduced concept still introduces it too early.
- Metaphor without anchor: saying "收灯", "收齐", "记忆", "习惯", "小习惯", "房间在计算" when the viewer has only seen toggles, movement, or marks.
- Soft-rule wording: avoid calling deterministic iteration rules "习惯" or "小习惯"; prefer "行为规则", "动作规则", "处理规则", or a direct rule description such as "看脚下，动一下，留下变化，再走开".
- False comparison: reject comparison sentences unless both sides share the same axis. "有的越走越乱，有的把灯慢慢收齐" is not a clean comparison because one side describes global pattern complexity and the other invents an unclear collection action.
- Pronoun drift: using "它", "这个", "那一步" after a scene change when the referent is no longer visually obvious.
- Screen/voice mismatch: narration says one object or action while screen text labels another.
- Scene-entry mismatch: if narration says the viewer is entering a room, meeting a character, or seeing a concrete object, the frame should first show that story scene or object. Do not replace scene entry with an abstract flowchart unless the narration has explicitly moved into abstraction.

## Rewrite Strategy

- Replace conclusions with observable actions: "它把答案写出来了" -> "有些灯被留下，有些灯暗下去。"
- Replace motives with behavior: "小光想收齐灯" -> "小光每到一格，只处理眼前这几盏灯。"
- Replace soft-rule wording with deterministic wording: "小光的巡灯习惯" -> "小光的行为规则" or "小光每到一格怎么做".
- Replace false comparisons with one shared axis: "同样是简单规则，一个让痕迹铺开成复杂花纹，另一个让灯的变化变得可追踪。"
- Replace future labels with neutral preview: "接下来看看加法器" -> "接下来换成两排小灯。"
- Replace premature negative framing with visible-object language: "我们先不看数字" -> "只看灯怎么亮、痕迹怎么留下。"
- Introduce names at first appearance, not in the bridge before appearance.
- Reveal interpretation only after the viewer has watched enough steps to connect behavior and result.
- If a line needs a concept that is not yet known, either add an earlier visual introduction or delay the line.

## Review Output

Return a concise review with:

- Verdict: `Ready` or `Needs revision`.
- Timeline gaps: the timecode/beat where viewer-known information is insufficient.
- Blocking lines: quote the problematic text, explain what the viewer knows at that moment, and why the line jumps ahead.
- Replacement lines: provide concrete Chinese rewrites that fit the same beat.
- Follow-up checks: note whether TTS, SRT, screen text, or rendered key frames must be regenerated.

If editing files, report changed paths and the validation performed.

## Example

Problem line before the character appears:

`先别急着下结论，继续看小光怎么收灯。`

Why it fails:

- The viewer has not been invited to make a conclusion.
- `小光` has not appeared or been named in this segment.
- `收灯` is a future interpretation, not an action the viewer has seen.

Safer rewrite for a bridge:

`下一段里，房间会变成两排小灯。先只看灯怎么亮、痕迹怎么留下。`
