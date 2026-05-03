---
name: manim-scene-iteration
description: Use when creating, editing, or debugging Manim scenes for this project, especially versioned math animation iterations with low-quality previews.
---

# Manim Scene Iteration

Use this skill when changing files under `topics/<topic>/scenes/`.

## Versioning

- Prefer copying the last stable scene to a new version, such as `topics/astroid-envelope/scenes/astroid_envelope_v6.py`, before structural changes.
- Keep old versions as comparison points unless the user explicitly asks to delete source code.
- Make small timing and text edits in the current version rather than regenerating everything from scratch.

## Scene Structure

- Split complex videos into multiple Manim `Scene` classes.
- Keep each scene aligned to a narration paragraph or chapter beat.
- Use a short `CoverFrame` scene when a video needs a first-frame thumbnail. Design it for mobile two-column feeds: when previewed at roughly 160-200 px wide, the main title should still be basically readable. Prefer a short one- or two-line title, high contrast, generous margins, and avoid relying on small subtitles or dense formulas to carry the topic. For title sizing, prefer fitting to a target width over guessing with fixed `scale()` values; the main title should visibly occupy a large share of the frame. Default to exporting only one high-resolution cover image; do not create persistent 200 px check files unless the user asks for them.
- For covers about envelopes, caustics, or other emergent curves, the primary visual should show enough generating lines or construction traces that the boundary looks naturally formed, not like a standalone decorative curve. Make the line family readable in the thumbnail while keeping the title as the dominant signal. Do not draw a thick highlighted boundary curve over the line family unless the user explicitly wants that; it can hide the natural envelope formation.
- Scene title and subtitle text should be neutral content summaries of the current beat. Do not reuse narration slogans, metaphor words, or production phrases as page headers when they sound odd without the spoken context.
- Avoid long static waits after the main visual is drawn. If narration keeps explaining the same figure for more than a few seconds, use semantic motion such as moving control points, sweeping a parameter, changing weights, or pulsing the relevant relation while preserving the scene's target duration.
- Formula-heavy narration should be split into staged visual beats. Do not reveal a full derivation panel and leave it static through a long voiceover; replace or morph the panel by step, keep only the current few formulas visible, and pair each spoken step with a diagram action such as drawing a component, flipping a vector, sweeping a parameter, or emphasizing the referenced object.
- For mathematical text, prefer `MathTex`. For Chinese prose in Manim `Text`, default to the local Smiley Sans / 得意黑 asset at `assets/fonts/SmileySans-Oblique.ttf` via `register_font`, matching the established Bezier visual system. Do not fall back to `Microsoft YaHei` unless the asset is missing or the topic deliberately needs a different style; if you do, record the reason in topic notes.
- Keep one UI font by default; mixing Times New Roman into the same `Text` via `t2f` can raise inline letters/numbers above the Chinese baseline or trigger ambiguous Pango style ranges. When inline math needs professional glyphs, split the line into `Text` + `MathTex` pieces and align them manually.
- Avoid constructing new `Text` or `MathTex` inside an `always_redraw` callback when the glyphs do not actually change. Create labels once and use updaters or `next_to(...)` against moving geometry; repeated text creation is slower and can collide with Manim's shared SVG/text cache during parallel renders.
- Formula stacks should avoid repeated left-hand expressions when the equality target is unchanged. Keep the equals signs and right-hand results left-aligned so the viewer compares the transformed part instead of rereading the same left side.
- Avoid slow glyph-by-glyph `Write` on long `MathTex` formulas in preview-critical scenes. It can show awkward partial braces or isolated symbols in low-quality frames. Prefer row-level `FadeIn`, `ReplacementTransform`, or short formula chunks while the diagram supplies the motion.
- When a formula stack sits inside a panel or framed note, constrain both its width and height against the actual panel interior. Width-only fitting can still let tall formulas or bottom notes spill outside the frame, so preview the densest beat before accepting the layout.
- Keep right-side panel typography visually consistent across chapters. Do not use unconditional `scale_to_fit_width` or `scale_to_fit_height` on sparse formula stacks, because it can enlarge later panels until they feel louder than earlier ones; only scale down when content would overflow.
- For mobile-first previews, right-side panel text should be comfortably readable at 480p preview scale. After normalizing panel typography, sample frames on dense formula beats and raise the shared panel size constants if body text or secondary formulas look too faint or small.
- When the user is reviewing primarily on mobile, be willing to enlarge panel typography more aggressively than desktop instincts suggest. Increase shared constants in visible steps, then validate the densest right-side panels for overflow before rendering a full preview.
- Treat the coffee-cup-caustic approved panel typography as the minimum for future 16:9 Manim math videos: `PANEL_TITLE_SIZE >= 0.42`, `PANEL_BODY_SIZE >= 0.34`, `PANEL_NOTE_SIZE >= 0.34`, `PANEL_FORMULA_SIZE >= 0.66`, `PANEL_FORMULA_LARGE_SIZE >= 0.72`, and `PANEL_FORMULA_SMALL_SIZE >= 0.54`. If a dense panel cannot fit at this size, split the beat or reduce content first; only go below this baseline for a clearly justified exception after screenshot review.
- Complex derivations must be animated as clear intermediate steps, not compressed jumps. In a formula stack, introduce at most one nontrivial move per beat: define components, simplify obvious coefficients, substitute known expressions, expand coordinates or terms, apply identities, then combine. If the panel becomes crowded, split the derivation across scenes or staged panels instead of deleting the bridge.
- Before a derivation formula stack appears, the scene title, panel title, or first callout must state the concrete task being solved. Avoid labels like "source", "condition", or "setup" by themselves when the viewer needs to know whether we are finding a line equation, an envelope condition, a derivative, or a parameterization.
- Do not jump directly to compact vector reflection formulas. If a scene uses a formula like `\vec{d}=\vec{i}-2(\vec{i}\cdot\vec{n})\vec{n}`, first show the decomposition into normal and tangent components, simplify the projection coefficient immediately when the known vectors make it obvious, explain that reflection preserves the tangent component and reverses the normal component, then collapse the expression.
- Do not introduce an implicit line equation without its construction. If a formula like `x\sin(2t)-y\cos(2t)=R\sin t` comes from a point and direction, first show the point, the direction, a perpendicular helper vector or equivalent determinant relation, then expand to the implicit equation. Label the helper vector on the diagram when it appears in the formula stack.
- When using a perpendicular helper vector to write a line equation, show the original direction vector and the helper vector together on the diagram, preferably from a shared anchor or with an explicit `\vec d\cdot\vec m=0` cue. This lets viewers see why the point-normal equation is valid.
- Give arbitrary points stable symbolic names before using their coordinates. Prefer labels like `P_0=(x,y)` on both the diagram and formula panel instead of an unlabeled `(x,y)` dot or a generic `X`.
- In derivation panels, retain the previous formula while adding the next transformation when the viewer needs to compare them. Avoid replacing the whole panel in one beat; use a transform/slide that keeps the old equation visible until the new equation is established.
- For envelope conditions, do not visually imply that `\partial F/\partial t=0` comes from differentiating `F=0` as a constant. The formula stack may stay concise with `F=0` and `\partial F/\partial t=0`, but include a small note or narration cue that the candidate point Q is fixed, `x,y` are held constant, and only the family parameter `t` varies.
- When an envelope solve produces a parametric curve, do not jump from the conditions directly to final `x(t), y(t)`. Show the original equation and the derivative equation as a system in the unknowns `x,y`, state that `R,t` are parameters, then show at least one intermediate solution before simplifying to the final parameterization.
- When adding an alternate coordinate form after a named curve is solved, introduce the coordinate convention before the formula. For polar equations, visibly mark the pole, polar axis, radial distance, and angle on the diagram; when time permits, animate the radial segment `\rho` and angle `\theta` sweeping around the curve instead of leaving them as static labels. Note that the new equation describes the same curve as the previous parameterization or Cartesian form.
- When a solved named curve has a standard geometric or mechanical construction, such as a rolling-circle generation, prefer adding a compact animation before secondary coordinate forms. Keep the solved curve visible, show the construction object and traced point, and explicitly say it is another generation of the same curve rather than a new result.
- Do not add formula highlight or focus animations unless there is an explicit timestamped cue map tying narration text to that exact expression. Prefer clear sequencing, spacing, and color hierarchy; unsynced highlights are worse than no highlights.
- When narration or formulas reference geometric symbols such as `P_0`, `P_1`, `Q_0`, `B(t)`, or vector symbols such as `\vec{i}`, `\vec{n}`, and `\vec{d}`, the corresponding point, moving marker, arrow, direction line, or vector label must be visibly labeled in the same scene. Match label color to the formula color when the formula and diagram are meant to correspond. Do a quick global pass for unlabeled symbol references before rendering previews.
- When a sidebar legend or explanatory list describes labeled geometry, include the symbol and the description together, such as `O：圆心`, `R：半径`, `t：角度`, and `OP：法线`. A label that only says "圆心" or "半径" forces the viewer to re-match the diagram and formula.
- When a family parameter is actually a geometric angle, prefer `\theta` over a generic `t` unless time is explicitly intended. Update the first definition, formulas, sidebar labels, narration, subtitles, and all downstream derivation text together so the video does not switch notation midstream.
- When a scene displays coordinate vectors or coordinate formulas, the diagram side must show the relevant coordinate axes or basis reference in the same scene. Also center formula stacks as a group inside their panel; avoid leaving a large empty band on one side of a formula container unless that space has a deliberate visual purpose.
- Before stitching a whole math preview, do a global pass across scenes for coordinate references: every scene showing `x,y` formulas needs visible Cartesian axes or an equivalent basis, and every scene showing polar equations needs the pole, polar axis, radial segment, and angle cue. Apply this to payoff scenes too, not only derivation scenes.
- When animating a family of reflected rays, keep one current incident ray highlighted along with the current reflected ray and reflection point. A static background bundle alone can make the reflected line look disconnected from the incoming light.
- Whenever a scene teaches incident or reflected light, add a visible direction cue on the highlighted or representative ray. Use short arrow overlays on top of the ray when full `Arrow` objects would clutter dense bundles; the arrow must point with light travel, not just label the line. In opening or payoff scenes about the accumulated caustic shape, do not force a reflected-direction arrow if it competes with the bright boundary; keep direction cues for the incoming light or for later explanatory scenes.
- Direction cues and vector arrows should have a clear lifetime. Fade out old direction arrows before introducing point-normal, displacement, envelope, or coordinate-conversion geometry if the old arrow would look like a second vector label. When cleaning redundancy, check both the text label and the arrow object in a still frame.
- For background grids, palette tuning, line visibility, and other global look changes, render a one-frame preview first and copy it to a unique filename. Reusing the same still name can make the app show a cached image and hide real changes.
- Default future Manim math videos to the approved subtle grid background from the Bezier video unless a topic has a deliberate art direction: grid line `#8FA8D8`, `stroke_width=1.6`, `opacity=0.155`, `spacing=0.48` on the project dark background. If changing any of these values, preview one still before updating the full video.
- Keep source files under `topics/<topic>/scenes/` and generated media under `topics/<topic>/exports/`.

## Timing

1. Generate narration and SRT first.
2. Render low quality with `-ql`.
3. Measure each scene duration with FFmpeg.
4. Adjust `self.wait(...)` until scene boundaries match narration boundaries.

## Commands

```powershell
.\scripts\render_scene.ps1 -SceneFile topics\astroid-envelope\scenes\astroid_envelope_v6.py -SceneName StoryHook
.\scripts\render_scenes_parallel.ps1 -SceneFile topics\astroid-envelope\scenes\astroid_envelope_v6.py -SceneNames CoverFrame,StoryHook -MaxParallel 3
```

The render scripts infer `--media_dir topics\<topic>\exports\manim` from the scene path. If running Manim directly, pass that `--media_dir` manually so intermediate renders do not go back to the root `exports/` folder.
