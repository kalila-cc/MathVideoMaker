---
name: math-video-outline
description: Use when planning or revising a Chinese math popular-science video outline, hook, chapter flow, analogy, or audience-facing explanation strategy.
---

# Math Video Outline

Use this skill before writing or revising a math animation script.

## Workflow

1. Start from a concrete scene, question, or surprise. Do not open with formulas, theorem names, or "chapter" language.
2. Define the audience promise in one sentence: what will viewers understand by the end?
3. Split the explanation into small beats: hook, variables, intuitive model, formal step, conclusion, real-world echo.
4. For each abstract step, attach a visual metaphor or physical anchor.
5. Flag jumps where a viewer may ask "where did this come from?" and add a bridge.
6. For derivation-led shape topics, delay the final shape name until the outline has earned it. Use neutral goals such as "what path will this rule produce?" before the visual or algebraic reveal, then name the curve as a result.
7. For complex derivations, write an explicit breadcrumb chain before scripting: known quantities, intermediate variables or components, obvious simplifications, combination step, and final result. Each nontrivial algebraic move needs a spoken reason or a visible operation; split the beat instead of skipping steps.
8. State the local task before a derivation begins, such as "求这条光线的直线方程" or "找这族线的包络条件"; do not rely on an abstract section title to imply what is being solved.
9. State the job of each new formula form before using it. If a line is rewritten as an implicit equation, sum, derivative condition, matrix form, or parameterized family, say what that form makes possible in the next step.
10. Before committing to a section, check whether it still supports the audience promise. If a compelling side mechanism pulls the topic toward a different promise, split it into a future topic instead of forcing it into the current outline.
11. For formula-derivation videos, prefer a hook based on the viewer's practical friction, such as "memorized formulas stop helping at the next case," then ask what can be computed from structure.
12. For "physical phenomenon -> family of objects -> envelope/trace -> named curve" videos, outline these as separate beats. First show the visible phenomenon, then derive the generating family, then explain why the envelope/trace operation is needed, and only after that name the final curve or give secondary coordinate forms.

## Style Rules

- Prefer relaxed spoken Chinese, like explaining to one curious person.
- Avoid phrases that expose the production process, such as "先别急着想公式" unless the viewer would naturally be thinking that.
- Chapter labels should summarize content, not production structure.
- Do not use a named theme such as "秩序", "混沌", "加法器", or "答案" before the outline has established the visible evidence for it.
- If a role or system is defined by simple behavior rules, the outline must introduce the concrete rules before relying on that behavior as an explanation.
- Comparisons need a shared axis. Reject lines that compare global complexity on one side with an unrelated metaphorical action on the other.
- Avoid mechanism-sounding metaphors such as machines, doors, gears, or telescopes unless the visual makes the mechanism immediately readable. When in doubt, show the algebraic process itself.
- Do not open a section with unexplained numbers, coefficients, or named patterns. Show the calculation or counting source first, then name the pattern.
- Do not title a derivation beat only with an abstract category such as "来源" or "条件". The viewer should hear or see the concrete math task before the formulas start.
- Do not compress multi-step derivations into a single "therefore" line. If the result depends on decomposition, substitution, projection, cancellation, differentiation, or solving simultaneous conditions, give those steps their own beats.
- For envelope derivations, do not describe `\partial F/\partial t=0` as differentiating the equation `F=0`. Keep the displayed conditions concise if useful, but state that a candidate point is fixed, the family parameter varies, and the derivative tests whether neighboring curves also touch that point.
- Do not introduce a formula only because it is mathematically valid. Tell the viewer why this representation is useful for the story or the next operation.
- Do not introduce a named curve or standard equation before the viewer has seen the mechanism that generates it. Use aliases or search terms only after a short operational definition, such as "the brightest boundary formed by many reflected rays."
- Remove or compress attractive side results if they do not support the central derivation path.
- End by showing the full object or payoff visually, not only as an equation.

## Output

Produce a concise outline with proposed chapter titles, intended visuals, any risk points that need extra explanation, and a suggested topic slug for `topics/<topic>/`.
