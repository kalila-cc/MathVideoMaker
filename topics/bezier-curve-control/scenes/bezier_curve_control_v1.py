from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import numpy as np
from manim import *


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SMILEY_FONT_FILE = PROJECT_ROOT / "assets" / "fonts" / "SmileySans-Oblique.ttf"
FONT = "Smiley Sans"
LATIN_FONT = "Times New Roman"
CODE_FONT = "Consolas"

BG = "#07111F"
INK = "#F8F4E3"
MUTED = "#AAB4C2"
BLUE = "#7DD3FC"
AMBER = "#F6B73C"
MINT = "#5EEAD4"
ROSE = "#FF5C7A"
VIOLET = "#A78BFA"
PANEL = "#0D1727"
GRID = "#1A2A3D"

LATIN_PATTERN = re.compile(r"[A-Za-z0-9_.:/,+#()-]+")

TIMES_TEX_TEMPLATE = TexTemplate()
TIMES_TEX_TEMPLATE.add_to_preamble(r"\usepackage{mathptmx}")
MathTex.set_default(tex_template=TIMES_TEX_TEMPLATE)


TARGET_DURATIONS = {
    "StoryHook": 18.77,
    "LinearInterpolation": 22.44,
    "QuadraticConstruction": 23.71,
    "CoefficientDerivation": 27.83,
    "QuadraticFormula": 23.91,
    "CubicConstruction": 25.12,
    "WeightControl": 28.40,
    "EndpointTangents": 27.58,
    "SmoothJoin": 21.69,
    "ProgrammingLinks": 46.19,
}


def latin_font_map(text: str) -> dict[str, str]:
    return {token: LATIN_FONT for token in LATIN_PATTERN.findall(text)}


def cn(text: str, size: float = 0.36, color: str = INK) -> Text:
    with register_font(SMILEY_FONT_FILE):
        return Text(text, font=FONT, slant=OBLIQUE, color=color).scale(size)


def code_line(text: str, size: float = 0.28, color: str = INK) -> Text:
    return Text(text, font=CODE_FONT, color=color).scale(size)


def latin_label(text: str, size: float = 0.36, color: str = INK) -> Text:
    return Text(text, font=LATIN_FONT, color=color).scale(size)


def finish_to(scene: Scene, target: float) -> None:
    remaining = target - scene.time
    if remaining > 0:
        scene.wait(remaining)


def scene_title(title: str, subtitle: str | None = None) -> VGroup:
    heading = cn(title, 0.52).to_edge(UP, buff=0.36)
    if not subtitle:
        return VGroup(heading)
    sub = cn(subtitle, 0.31, MUTED).next_to(heading, DOWN, buff=0.12)
    return VGroup(heading, sub)


def panel(width: float, height: float, color: str = PANEL) -> RoundedRectangle:
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.18,
        stroke_color="#2A3A50",
        stroke_width=1.5,
        fill_color=color,
        fill_opacity=0.94,
    )


def notebook_grid(spacing: float = 0.48) -> VGroup:
    width = config.frame_width + spacing
    height = config.frame_height + spacing
    x_values = np.arange(-width / 2, width / 2 + spacing, spacing)
    y_values = np.arange(-height / 2, height / 2 + spacing, spacing)
    grid = VGroup(
        *[Line(DOWN * height / 2 + RIGHT * x, UP * height / 2 + RIGHT * x, color="#8FA8D8", stroke_width=1.6) for x in x_values],
        *[Line(LEFT * width / 2 + UP * y, RIGHT * width / 2 + UP * y, color="#8FA8D8", stroke_width=1.6) for y in y_values],
    )
    grid.set_opacity(0.155)
    grid.set_z_index(-100)
    return grid


def set_scene_background(scene: Scene) -> None:
    scene.camera.background_color = BG
    scene.add(notebook_grid())


def point_label(dot: Mobject, label: str, color: str = INK, direction: np.ndarray = UP) -> MathTex:
    return MathTex(label, color=color).scale(0.55).next_to(dot, direction, buff=0.08)


def lerp(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    return (1 - t) * a + t * b


def quadratic_point(points: Iterable[np.ndarray], t: float) -> np.ndarray:
    p0, p1, p2 = list(points)
    a = lerp(p0, p1, t)
    b = lerp(p1, p2, t)
    return lerp(a, b, t)


def cubic_point(points: Iterable[np.ndarray], t: float) -> np.ndarray:
    p0, p1, p2, p3 = list(points)
    a = lerp(p0, p1, t)
    b = lerp(p1, p2, t)
    c = lerp(p2, p3, t)
    d = lerp(a, b, t)
    e = lerp(b, c, t)
    return lerp(d, e, t)


def bezier_curve(points: list[np.ndarray], color: str = AMBER, width: float = 7, t_max: float = 1.0) -> VMobject:
    fn = quadratic_point if len(points) == 3 else cubic_point
    t_max = np.clip(t_max, 0.001, 1.0)
    samples = max(3, int(120 * t_max))
    curve = VMobject()
    curve.set_points_smoothly([fn(points, t) for t in np.linspace(0, t_max, samples)])
    curve.set_fill(opacity=0)
    curve.set_stroke(color=color, width=width)
    return curve


def control_polygon(points: list[np.ndarray], colors: list[str] | None = None) -> VGroup:
    colors = colors or [BLUE] * len(points)
    lines = VGroup(
        *[
            Line(points[i], points[i + 1], color=BLUE, stroke_width=3, stroke_opacity=0.42)
            for i in range(len(points) - 1)
        ]
    )
    dots = VGroup(*[Dot(point, color=colors[i], radius=0.075) for i, point in enumerate(points)])
    return VGroup(lines, dots)


def dot_with_label(point: np.ndarray, label: str, color: str, direction: np.ndarray = UP) -> VGroup:
    dot = Dot(point, color=color, radius=0.075)
    lab = MathTex(label, color=color).scale(0.55).next_to(dot, direction, buff=0.08)
    return VGroup(dot, lab)


def progress_slider(t_tracker: ValueTracker, width: float = 4.8, center: np.ndarray = DOWN * 3.25) -> VGroup:
    left = center + LEFT * width / 2
    right = center + RIGHT * width / 2

    def make_group() -> VGroup:
        t = t_tracker.get_value()
        rail = Line(left, right, color="#3B4A5F", stroke_width=8)
        active = Line(left, lerp(left, right, t), color=AMBER, stroke_width=8)
        knob = Dot(lerp(left, right, t), color=AMBER, radius=0.09)
        t_label = latin_label("t", 0.42, AMBER).next_to(knob, UP, buff=0.08)
        zero = latin_label("0", 0.32, MUTED).next_to(rail, LEFT, buff=0.12)
        one = latin_label("1", 0.32, MUTED).next_to(rail, RIGHT, buff=0.12)
        return VGroup(rail, active, knob, t_label, zero, one)

    return always_redraw(make_group)


def weight_values(t: float) -> tuple[float, float, float, float]:
    return ((1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t**2, t**3)


def weight_bars(t_tracker: ValueTracker, origin: np.ndarray) -> VGroup:
    labels = ["w0", "w1", "w2", "w3"]
    colors = [BLUE, MINT, ROSE, VIOLET]
    width = 2.75
    rows = []
    for index, (label, color) in enumerate(zip(labels, colors)):
        y = -index * 0.5

        def make_row(i=index, lab=label, col=color, ypos=y) -> VGroup:
            weight = weight_values(t_tracker.get_value())[i]
            label_mob = latin_label(lab, 0.34, col).move_to(origin + UP * ypos)
            bg = Rectangle(width=width, height=0.18, stroke_color="#314054", fill_color="#162235", fill_opacity=1)
            bg.next_to(label_mob, RIGHT, buff=0.22)
            fg = Rectangle(width=max(0.02, width * weight), height=0.18, stroke_width=0, fill_color=col, fill_opacity=0.95)
            fg.align_to(bg, LEFT).move_to(bg.get_left() + RIGHT * fg.width / 2)
            value = DecimalNumber(weight, num_decimal_places=2, color=MUTED).scale(0.33).next_to(bg, RIGHT, buff=0.15)
            return VGroup(label_mob, bg, fg, value)

        rows.append(always_redraw(make_row))
    return VGroup(*rows)


def de_casteljau_layers(points: list[np.ndarray], t: float) -> tuple[list[np.ndarray], list[np.ndarray], list[np.ndarray]]:
    first = [lerp(points[i], points[i + 1], t) for i in range(len(points) - 1)]
    second = [lerp(first[i], first[i + 1], t) for i in range(len(first) - 1)]
    third = [lerp(second[0], second[1], t)] if len(second) == 2 else []
    return first, second, third


def cover_background() -> VGroup:
    grid = VGroup(
        *[Line(LEFT * 7.2 + UP * y, RIGHT * 7.2 + UP * y, color=GRID, stroke_width=1) for y in np.linspace(-3.6, 3.6, 9)],
        *[Line(LEFT * x + DOWN * 4.0, LEFT * x + UP * 4.0, color=GRID, stroke_width=1) for x in np.linspace(-7.2, 7.2, 13)],
    ).set_opacity(0.28)
    halo = bezier_curve(
        [LEFT * 5.4 + DOWN * 2.7, LEFT * 1.8 + UP * 2.6, RIGHT * 1.7 + UP * 2.35, RIGHT * 5.6 + DOWN * 2.2],
        AMBER,
        26,
    ).set_opacity(0.08)
    return VGroup(grid, halo)


def cover_curve_visual(scale: float = 1.0) -> VGroup:
    p0 = LEFT * 3.8 + DOWN * 1.55
    p1 = LEFT * 2.55 + UP * 1.72
    p2 = RIGHT * 1.75 + UP * 1.62
    p3 = RIGHT * 3.95 + DOWN * 1.22
    points = [p0, p1, p2, p3]
    card = RoundedRectangle(
        width=8.65,
        height=4.85,
        corner_radius=0.22,
        stroke_color="#31425B",
        stroke_width=2.2,
        fill_color="#0B1626",
        fill_opacity=0.82,
    )
    grid = VGroup(
        *[Line(card.get_left() + RIGHT * x, card.get_left() + RIGHT * x + UP * 4.45, color=GRID, stroke_width=1) for x in np.linspace(0.7, 8.0, 9)],
        *[Line(card.get_bottom() + UP * y, card.get_bottom() + UP * y + RIGHT * 8.15, color=GRID, stroke_width=1) for y in np.linspace(0.55, 4.3, 6)],
    ).move_to(card).set_opacity(0.36)
    handles = VGroup(
        Line(p0, p1, color=BLUE, stroke_width=5, stroke_opacity=0.9),
        Line(p2, p3, color=BLUE, stroke_width=5, stroke_opacity=0.9),
    )
    curve = bezier_curve(points, AMBER, 14)
    glow = curve.copy().set_stroke(width=28, opacity=0.16)
    dots = VGroup(
        dot_with_label(p0, "P_0", AMBER, DOWN),
        dot_with_label(p1, "P_1", BLUE, UP),
        dot_with_label(p2, "P_2", BLUE, UP),
        dot_with_label(p3, "P_3", AMBER, DOWN),
    ).scale(1.18)
    visual = VGroup(card, grid, handles, glow, curve, dots)
    visual.scale(scale)
    return visual


def cover_title(lines: list[str], target_width: float, size: float = 1.0) -> VGroup:
    title = VGroup(*[cn(line, size, INK) for line in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    title.scale_to_fit_width(target_width)
    return title


class CoverFrameDesktop(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        self.add(cover_background())

        badge = cn("贝塞尔曲线", 0.34, BG)
        badge_box = RoundedRectangle(
            width=2.55,
            height=0.56,
            corner_radius=0.2,
            stroke_width=0,
            fill_color=AMBER,
            fill_opacity=1,
        )
        badge.move_to(badge_box)
        title = cover_title(["几个点", "管住曲线？"], 9.85)
        subtitle = cn("从钢笔工具到动画缓动", 0.42, MUTED)
        text_block = VGroup(VGroup(badge_box, badge), title, subtitle).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        text_block.to_edge(LEFT, buff=0.22).shift(UP * 0.48)

        visual = cover_curve_visual(0.44).to_edge(RIGHT, buff=0.18).shift(DOWN * 1.92)

        self.add(visual, text_block)


class CoverFrameMobile(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        self.add(cover_background())

        badge = cn("贝塞尔曲线", 0.32, BG)
        badge_box = RoundedRectangle(
            width=2.35,
            height=0.52,
            corner_radius=0.18,
            stroke_width=0,
            fill_color=AMBER,
            fill_opacity=1,
        )
        badge.move_to(badge_box)
        title = cover_title(["几个点，", "管住曲线？"], 8.35)
        title_group = VGroup(VGroup(badge_box, badge), title).arrange(DOWN, buff=0.18)
        title_group.to_edge(LEFT, buff=0.22).to_edge(UP, buff=0.24)

        visual = cover_curve_visual(0.53).shift(RIGHT * 4.18 + DOWN * 1.75)
        callout = VGroup(cn("控制点不在曲线上，", 0.42, AMBER), cn("却能改掉整条线。", 0.42, AMBER)).arrange(
            DOWN, aligned_edge=LEFT, buff=0.06
        )
        callout.next_to(title_group, DOWN, buff=0.18).align_to(title_group, LEFT)

        self.add(visual, title_group, callout)


class StoryHook(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("几个点，凭什么管住一条曲线？", "从钢笔工具里的锚点和手柄开始")
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.9)

        canvas = RoundedRectangle(
            width=10.8,
            height=5.2,
            corner_radius=0.22,
            stroke_color="#2B3B52",
            fill_color="#0B1626",
            fill_opacity=0.72,
        ).shift(DOWN * 0.42)
        grid = VGroup(
            *[Line(canvas.get_left() + RIGHT * x, canvas.get_left() + RIGHT * x + UP * 5.2, color=GRID, stroke_width=1) for x in np.linspace(0.8, 10.0, 12)],
            *[Line(canvas.get_bottom() + UP * y, canvas.get_bottom() + UP * y + RIGHT * 10.8, color=GRID, stroke_width=1) for y in np.linspace(0.6, 4.6, 8)],
        ).set_opacity(0.45)
        self.play(FadeIn(canvas), FadeIn(grid), run_time=0.8)

        p0 = LEFT * 4.2 + DOWN * 1.55
        p1 = LEFT * 2.1 + UP * 1.65
        p2 = RIGHT * 1.4 + UP * 1.35
        p3 = RIGHT * 4.2 + DOWN * 1.3
        points = [p0, p1, p2, p3]
        handles = VGroup(Line(p0, p1, color=BLUE, stroke_width=3), Line(p2, p3, color=BLUE, stroke_width=3))
        dots = VGroup(
            dot_with_label(p0, "P_0", AMBER, DOWN),
            dot_with_label(p1, "P_1", BLUE, UP),
            dot_with_label(p2, "P_2", BLUE, UP),
            dot_with_label(p3, "P_3", AMBER, DOWN),
        )
        curve = bezier_curve(points, AMBER, 9)
        ghost = curve.copy().set_stroke(width=18, opacity=0.13)

        self.play(FadeIn(handles), LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.15), run_time=1.4)
        self.play(Create(ghost), Create(curve), run_time=2.0)

        note = cn("控制点不全在曲线上，却能精确改变曲线形状。", 0.34, MUTED).to_edge(DOWN, buff=0.38)
        question = cn("贝塞尔曲线要解释的，就是这件事。", 0.36, AMBER).next_to(note, UP, buff=0.14)
        self.play(FadeIn(question, shift=UP * 0.08), FadeIn(note, shift=UP * 0.08), run_time=1.0)
        self.play(handles.animate.set_stroke(width=5, opacity=0.9), curve.animate.set_stroke(width=11), run_time=1.2)

        p1_shift = ValueTracker(0)
        p2_shift = ValueTracker(0)
        p1_motion = LEFT * 0.95 + DOWN * 0.72
        p2_motion = RIGHT * 0.95 + DOWN * 0.75

        def moving_points() -> list[np.ndarray]:
            return [p0, p1 + p1_shift.get_value() * p1_motion, p2 + p2_shift.get_value() * p2_motion, p3]

        dynamic_handles = always_redraw(
            lambda: VGroup(
                Line(moving_points()[0], moving_points()[1], color=BLUE, stroke_width=5, stroke_opacity=0.9),
                Line(moving_points()[2], moving_points()[3], color=BLUE, stroke_width=5, stroke_opacity=0.9),
            )
        )
        dynamic_dots = always_redraw(
            lambda: VGroup(
                dot_with_label(moving_points()[0], "P_0", AMBER, DOWN),
                dot_with_label(moving_points()[1], "P_1", BLUE, UP),
                dot_with_label(moving_points()[2], "P_2", BLUE, UP),
                dot_with_label(moving_points()[3], "P_3", AMBER, DOWN),
            )
        )
        dynamic_curve = always_redraw(lambda: bezier_curve(moving_points(), AMBER, 11))
        dynamic_ghost = always_redraw(lambda: bezier_curve(moving_points(), AMBER, 24).set_stroke(opacity=0.13))
        self.remove(*VGroup(handles, dots, ghost, curve).get_family())
        self.add(dynamic_ghost, dynamic_curve, dynamic_handles, dynamic_dots)
        self.add(question, note)

        self.play(p1_shift.animate.set_value(1.15), p2_shift.animate.set_value(-1.0), run_time=3.2, rate_func=smooth)
        self.play(p1_shift.animate.set_value(-0.75), p2_shift.animate.set_value(1.15), run_time=3.2, rate_func=smooth)
        self.play(p1_shift.animate.set_value(0.45), p2_shift.animate.set_value(-0.55), run_time=2.4, rate_func=smooth)
        self.play(p1_shift.animate.set_value(0), p2_shift.animate.set_value(0), run_time=1.6, rate_func=smooth)
        finish_to(self, TARGET_DURATIONS["StoryHook"])


class LinearInterpolation(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("先理解一段线上的移动点", "参数 t 只是从起点走到终点的进度")
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)

        a = LEFT * 4 + DOWN * 0.4
        b = RIGHT * 4 + UP * 0.9
        line = Line(a, b, color=BLUE, stroke_width=6)
        a_group = dot_with_label(a, "A", AMBER, DOWN)
        b_group = dot_with_label(b, "B", MINT, UP)
        self.play(Create(line), FadeIn(a_group), FadeIn(b_group), run_time=1.1)

        t = ValueTracker(0)
        mover = always_redraw(lambda: Dot(lerp(a, b, t.get_value()), color=ROSE, radius=0.095))
        mover_label = always_redraw(lambda: latin_label("L(t)", 0.36, ROSE).next_to(mover, UP, buff=0.08))
        slider = progress_slider(t)
        self.play(FadeIn(slider), FadeIn(mover), FadeIn(mover_label), run_time=0.7)
        self.play(t.animate.set_value(1), run_time=5.0, rate_func=linear)
        self.play(t.animate.set_value(0.35), run_time=1.4, rate_func=smooth)

        formula_box = panel(6.5, 1.25).to_edge(RIGHT, buff=0.55).shift(DOWN * 1.15)
        formula = MathTex(r"L(t)=(1-t)A+tB,\qquad 0\le t\le 1", color=INK).scale(0.72).move_to(formula_box)
        explain = cn("位置 = A 的权重 + B 的权重", 0.29, MUTED).next_to(formula, DOWN, buff=0.16)
        self.play(FadeIn(formula_box, shift=LEFT * 0.12), Write(formula), FadeIn(explain), run_time=1.4)
        self.play(t.animate.set_value(0.72), run_time=2.2, rate_func=smooth)
        finish_to(self, TARGET_DURATIONS["LinearInterpolation"])


class QuadraticConstruction(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("三点曲线：先分点，再分点", "同一个参数 t 同时控制所有移动点")
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)

        p0 = LEFT * 4.2 + DOWN * 1.55
        p1 = LEFT * 0.8 + UP * 1.9
        p2 = RIGHT * 4.0 + DOWN * 1.2
        points = [p0, p1, p2]
        base = control_polygon(points, [AMBER, BLUE, AMBER])
        labels = VGroup(
            MathTex(r"P_0", color=AMBER).scale(0.55).next_to(p0, DOWN, buff=0.08),
            MathTex(r"P_1", color=BLUE).scale(0.55).next_to(p1, UP, buff=0.08),
            MathTex(r"P_2", color=AMBER).scale(0.55).next_to(p2, DOWN, buff=0.08),
        )
        self.play(FadeIn(base), FadeIn(labels), run_time=1.0)

        t = ValueTracker(0)

        def construction() -> VGroup:
            tt = t.get_value()
            a, b = de_casteljau_layers(points, tt)[0]
            q = quadratic_point(points, tt)
            first_line = Line(a, b, color=MINT, stroke_width=4)
            dots = VGroup(Dot(a, color=MINT, radius=0.075), Dot(b, color=MINT, radius=0.075), Dot(q, color=ROSE, radius=0.09))
            curve = bezier_curve(points, AMBER, 7, tt)
            return VGroup(first_line, dots, curve)

        live = always_redraw(construction)
        slider = progress_slider(t)
        caption = cn("两次线性插值，最后一个点留下轨迹。", 0.34, MUTED).next_to(slider, UP, buff=0.28)
        self.play(FadeIn(slider), FadeIn(caption), FadeIn(live), run_time=0.8)
        self.play(t.animate.set_value(1), run_time=12.2, rate_func=linear)
        self.play(t.animate.set_value(0.18), run_time=2.6, rate_func=smooth)
        self.play(t.animate.set_value(0.78), run_time=2.7, rate_func=smooth)
        final_curve = bezier_curve(points, AMBER, 9)
        self.play(Create(final_curve), run_time=1.4)
        self.play(t.animate.set_value(0.48), final_curve.animate.set_stroke(width=11), run_time=1.4)
        finish_to(self, TARGET_DURATIONS["QuadraticConstruction"])


class CoefficientDerivation(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("这些系数从哪里来？", "把两次线性插值代回去，再合并同类项")
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)

        p0 = LEFT * 5.25 + DOWN * 1.35
        p1 = LEFT * 3.35 + UP * 1.6
        p2 = LEFT * 1.05 + DOWN * 1.05
        t_value = 0.48
        q0 = lerp(p0, p1, t_value)
        q1 = lerp(p1, p2, t_value)
        b = lerp(q0, q1, t_value)

        base = control_polygon([p0, p1, p2], [AMBER, BLUE, AMBER])
        labels = VGroup(
            VGroup(MathTex(r"P_0", color=AMBER).scale(0.52), cn("起点", 0.21, AMBER))
            .arrange(DOWN, buff=0.03)
            .next_to(p0, DOWN, buff=0.1),
            VGroup(MathTex(r"P_1", color=BLUE).scale(0.52), cn("控制点", 0.21, BLUE))
            .arrange(DOWN, buff=0.03)
            .next_to(p1, UP, buff=0.1),
            VGroup(MathTex(r"P_2", color=AMBER).scale(0.52), cn("终点", 0.21, AMBER))
            .arrange(DOWN, buff=0.03)
            .next_to(p2, DOWN, buff=0.1),
        )
        q_line = Line(q0, q1, color=MINT, stroke_width=4)
        q_dots = VGroup(Dot(q0, color=MINT, radius=0.075), Dot(q1, color=MINT, radius=0.075))
        q_labels = VGroup(
            MathTex(r"Q_0", color=MINT).scale(0.5).next_to(q0, LEFT, buff=0.08),
            MathTex(r"Q_1", color=MINT).scale(0.5).next_to(q1, RIGHT, buff=0.08),
        )
        b_dot = Dot(b, color=ROSE, radius=0.09)
        b_label = latin_label("B(t)", 0.34, ROSE).next_to(b_dot, UP, buff=0.08)
        curve = bezier_curve([p0, p1, p2], AMBER, 7).set_stroke(opacity=0.55)

        self.play(FadeIn(base), FadeIn(labels), run_time=1.0)
        self.play(FadeIn(q_line), FadeIn(q_dots), FadeIn(q_labels), FadeIn(b_dot), FadeIn(b_label), run_time=1.1)
        self.play(Create(curve), run_time=1.0)

        box = panel(6.75, 5.15).to_edge(RIGHT, buff=0.36).shift(DOWN * 0.02)
        box_title = cn("从构造式展开", 0.32).move_to(box.get_top() + DOWN * 0.36)
        q0_formula = MathTex(r"Q_0=(1-t)P_0+tP_1", color=MINT).scale(0.48)
        q1_formula = MathTex(r"Q_1=(1-t)P_1+tP_2", color=MINT).scale(0.48)
        b_formula = MathTex(r"B(t)=(1-t)Q_0+tQ_1", color=INK).scale(0.50)
        subst = MathTex(
            r"=(1-t)[(1-t)P_0+tP_1]+t[(1-t)P_1+tP_2]",
            color=INK,
        ).scale(0.42)
        collect = MathTex(
            r"=(1-t)^2P_0+\big((1-t)t+t(1-t)\big)P_1+t^2P_2",
            color=INK,
        ).scale(0.39)
        final = MathTex(
            r"=(1-t)^2P_0+2(1-t)tP_1+t^2P_2",
            color=AMBER,
        ).scale(0.46)
        note = cn("P1 出现两次，所以中间权重前面多了一个 2。", 0.24, MUTED)
        stack = VGroup(q0_formula, q1_formula, b_formula, subst, collect, final, note).arrange(
            DOWN, aligned_edge=LEFT, buff=0.24
        )
        stack.next_to(box_title, DOWN, buff=0.35).align_to(box, LEFT).shift(RIGHT * 0.42)

        self.play(FadeIn(box, shift=LEFT * 0.12), FadeIn(box_title), run_time=0.7)
        self.play(FadeIn(q0_formula, shift=UP * 0.06), FadeIn(q1_formula, shift=UP * 0.06), run_time=1.2)
        self.play(FadeIn(b_formula, shift=UP * 0.06), run_time=0.9)
        self.play(FadeIn(subst, shift=UP * 0.06), run_time=1.2)

        p1_hint = cn("这里有两个 P1 项", 0.24, BLUE).next_to(subst, RIGHT, buff=0.18)
        self.play(FadeIn(p1_hint, shift=LEFT * 0.06), run_time=0.7)
        self.play(FadeIn(collect, shift=UP * 0.06), run_time=1.3)
        self.play(FadeIn(final, shift=UP * 0.06), FadeIn(note), run_time=1.2)
        finish_to(self, TARGET_DURATIONS["CoefficientDerivation"])


class QuadraticFormula(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("构造过程压缩成公式", "每一项都是一个控制点的权重")
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)

        p0 = LEFT * 5.65 + DOWN * 1.38
        p1 = LEFT * 4.05 + UP * 1.72
        p2 = LEFT * 1.75 + DOWN * 1.12
        points = [p0, p1, p2]
        curve = bezier_curve(points, AMBER, 8)
        base = control_polygon(points, [AMBER, BLUE, AMBER])
        point_roles = VGroup(
            VGroup(
                MathTex(r"P_0", color=AMBER).scale(0.58),
                cn("起点", 0.24, AMBER),
            ).arrange(DOWN, buff=0.04).next_to(p0, DOWN, buff=0.12),
            VGroup(
                MathTex(r"P_1", color=BLUE).scale(0.58),
                cn("控制点", 0.24, BLUE),
            ).arrange(DOWN, buff=0.04).next_to(p1, UP, buff=0.12),
            VGroup(
                MathTex(r"P_2", color=AMBER).scale(0.58),
                cn("终点", 0.24, AMBER),
            ).arrange(DOWN, buff=0.04).next_to(p2, DOWN, buff=0.12),
        )
        self.play(FadeIn(base), FadeIn(point_roles), Create(curve), run_time=1.6)

        box = panel(6.05, 4.05).to_edge(RIGHT, buff=0.36).shift(UP * 0.05)
        formula = MathTex(
            r"B(t)=(1-t)^2P_0+2(1-t)tP_1+t^2P_2",
            color=INK,
        ).scale(0.48)
        weight_rows = VGroup(
            VGroup(
                MathTex(r"P_0", color=AMBER).scale(0.44),
                cn("起点", 0.21, MUTED),
                MathTex(r"\times\ (1-t)^2", color=AMBER).scale(0.44),
            ).arrange(RIGHT, buff=0.16),
            VGroup(
                MathTex(r"P_1", color=BLUE).scale(0.44),
                cn("控制点", 0.21, MUTED),
                MathTex(r"\times\ 2(1-t)t", color=BLUE).scale(0.44),
            ).arrange(RIGHT, buff=0.16),
            VGroup(
                MathTex(r"P_2", color=AMBER).scale(0.44),
                cn("终点", 0.21, MUTED),
                MathTex(r"\times\ t^2", color=AMBER).scale(0.44),
            ).arrange(RIGHT, buff=0.16),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        note = cn("B(t) 是三个控制点按权重混合出的结果。", 0.25, MUTED)
        stack = VGroup(formula, weight_rows, note).arrange(DOWN, aligned_edge=LEFT, buff=0.36).move_to(box)
        self.play(FadeIn(box, shift=LEFT * 0.12), Write(formula), run_time=1.2)
        self.play(FadeIn(weight_rows, shift=UP * 0.08), FadeIn(note), run_time=1.0)

        t = ValueTracker(0.05)

        def weighted_point() -> VGroup:
            tt = t.get_value()
            q = quadratic_point(points, tt)
            w0, w1, w2 = (1 - tt) ** 2, 2 * (1 - tt) * tt, tt**2
            rays = VGroup(
                Line(p0, q, color=AMBER, stroke_width=max(1.0, 6 * w0), stroke_opacity=0.35),
                Line(p1, q, color=BLUE, stroke_width=max(1.0, 6 * w1), stroke_opacity=0.35),
                Line(p2, q, color=AMBER, stroke_width=max(1.0, 6 * w2), stroke_opacity=0.35),
            )
            q_dot = Dot(q, color=ROSE, radius=0.095)
            q_label = latin_label("B(t)", 0.34, ROSE).next_to(q_dot, UP, buff=0.08)
            return VGroup(rays, q_dot, q_label)

        wp = always_redraw(weighted_point)
        self.play(FadeIn(wp), run_time=0.6)
        self.play(t.animate.set_value(0.95), run_time=6.2, rate_func=linear)
        self.play(t.animate.set_value(0.5), run_time=1.4, rate_func=smooth)

        cubic_box = panel(6.05, 1.18).next_to(box, DOWN, buff=0.16)
        cubic_title = cn("同样多展开一层，三次就会合并出", 0.22, MUTED)
        cubic_coeff = MathTex(r"1,\quad 3,\quad 3,\quad 1", color=AMBER).scale(0.55)
        cubic_weights = MathTex(
            r"(1-t)^3,\quad 3(1-t)^2t,\quad 3(1-t)t^2,\quad t^3",
            color=INK,
        ).scale(0.34)
        cubic_hint = VGroup(cubic_title, cubic_coeff, cubic_weights).arrange(DOWN, buff=0.08).move_to(cubic_box)
        self.play(FadeIn(cubic_box, shift=UP * 0.06), FadeIn(cubic_hint, shift=UP * 0.06), run_time=1.0)
        finish_to(self, TARGET_DURATIONS["QuadraticFormula"])


class CubicConstruction(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("四点曲线：钢笔工具常用的版本", "三次贝塞尔仍然是重复线性插值")
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)

        points = [
            LEFT * 4.7 + DOWN * 1.55,
            LEFT * 2.6 + UP * 1.85,
            RIGHT * 1.6 + UP * 1.35,
            RIGHT * 4.3 + DOWN * 1.35,
        ]
        base = control_polygon(points, [AMBER, BLUE, BLUE, AMBER])
        labels = VGroup(
            *[
                MathTex(fr"P_{i}", color=AMBER if i in (0, 3) else BLUE).scale(0.5).next_to(
                    points[i], DOWN if i in (0, 3) else UP, buff=0.08
                )
                for i in range(4)
            ]
        )
        self.play(FadeIn(base), FadeIn(labels), run_time=1.0)

        t = ValueTracker(0)

        def live_layers() -> VGroup:
            tt = t.get_value()
            first, second, third = de_casteljau_layers(points, tt)
            first_lines = VGroup(*[Line(first[i], first[i + 1], color=MINT, stroke_width=3.6) for i in range(2)])
            second_line = Line(second[0], second[1], color=ROSE, stroke_width=4.2)
            dots = VGroup(
                *[Dot(p, color=MINT, radius=0.06) for p in first],
                *[Dot(p, color=ROSE, radius=0.07) for p in second],
                Dot(third[0], color=AMBER, radius=0.095),
            )
            curve = bezier_curve(points, AMBER, 7, tt)
            return VGroup(first_lines, second_line, dots, curve)

        live = always_redraw(live_layers)
        slider = progress_slider(t)
        self.play(FadeIn(slider), FadeIn(live), run_time=0.7)
        self.play(t.animate.set_value(1), run_time=7.2, rate_func=linear)

        formula_box = panel(7.4, 1.55).to_edge(DOWN, buff=0.28)
        formula = MathTex(
            r"B(t)=(1-t)^3P_0+3(1-t)^2tP_1+3(1-t)t^2P_2+t^3P_3",
            color=INK,
        ).scale(0.48).move_to(formula_box).shift(UP * 0.12)
        note = cn("四个控制点的加权平均", 0.27, MUTED).next_to(formula, DOWN, buff=0.1)
        self.play(FadeIn(formula_box), Write(formula), FadeIn(note), run_time=1.4)
        finish_to(self, TARGET_DURATIONS["CubicConstruction"])


class WeightControl(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("拖一个控制点，曲线怎么算着变？", "控制点的位移会按权重传到曲线上")
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)

        p0 = LEFT * 5.2 + DOWN * 1.45
        p1_base = LEFT * 3.75 + UP * 1.65
        p2 = LEFT * 1.2 + UP * 1.1
        p3 = RIGHT * 1.05 + DOWN * 1.35
        shift = ValueTracker(0)
        t = ValueTracker(0.33)

        def current_points() -> list[np.ndarray]:
            return [p0, p1_base + UP * shift.get_value(), p2, p3]

        curve = always_redraw(lambda: bezier_curve(current_points(), AMBER, 8))
        polygon = always_redraw(lambda: control_polygon(current_points(), [AMBER, BLUE, BLUE, AMBER]))
        marker = always_redraw(lambda: Dot(cubic_point(current_points(), t.get_value()), color=ROSE, radius=0.095))
        p0_label = MathTex(r"P_0", color=AMBER).scale(0.46).next_to(p0, DOWN, buff=0.08)
        p1_label = always_redraw(
            lambda: MathTex(r"P_1", color=BLUE).scale(0.46).next_to(p1_base + UP * shift.get_value(), LEFT, buff=0.1)
        )
        p2_label = MathTex(r"P_2", color=BLUE).scale(0.46).next_to(p2, UP, buff=0.08)
        p3_label = MathTex(r"P_3", color=AMBER).scale(0.46).next_to(p3, DOWN, buff=0.08)
        point_labels = VGroup(p0_label, p1_label, p2_label, p3_label)
        original_curve = bezier_curve([p0, p1_base, p2, p3], "#607087", 4).set_stroke(opacity=0.55)
        self.play(FadeIn(original_curve), FadeIn(polygon), FadeIn(point_labels), Create(curve), FadeIn(marker), run_time=1.2)

        bars_panel = panel(4.35, 2.6).to_edge(RIGHT, buff=0.36).shift(UP * 0.15)
        bars_title = cn("四个权重", 0.34).move_to(bars_panel.get_top() + DOWN * 0.34)
        bars_origin = bars_panel.get_left() + RIGHT * 0.66 + UP * 0.6
        bars = weight_bars(t, bars_origin)
        sum_formula = MathTex(r"\Delta B(t)=\displaystyle\sum_{i=0}^{3} w_i(t)\Delta P_i", color=AMBER).scale(0.46)
        single_label = cn("只动 P1 时", 0.22, BLUE)
        single_formula = MathTex(r"\Delta B(t)=w_1(t)\Delta P_1", color=BLUE).scale(0.4)
        single_row = VGroup(single_label, single_formula).arrange(RIGHT, buff=0.12)
        formula = VGroup(sum_formula, single_row).arrange(DOWN, buff=0.1).next_to(bars_panel, DOWN, buff=0.2)
        self.play(FadeIn(bars_panel, shift=LEFT * 0.1), FadeIn(bars_title), FadeIn(bars), Write(formula), run_time=1.4)

        self.play(t.animate.set_value(0.05), run_time=1.0)
        self.play(t.animate.set_value(0.95), run_time=4.2, rate_func=linear)
        self.play(t.animate.set_value(0.33), run_time=0.9)
        arrow = Arrow(p1_base, p1_base + UP * 1.1, color=BLUE, buff=0.08, stroke_width=6)
        label = cn("移动 P1", 0.3, BLUE).next_to(arrow, LEFT, buff=0.12)
        self.play(FadeIn(arrow), FadeIn(label), shift.animate.set_value(1.1), run_time=2.2, rate_func=smooth)
        self.play(t.animate.set_value(0.75), run_time=2.5, rate_func=smooth)
        finish_to(self, TARGET_DURATIONS["WeightControl"])


class EndpointTangents(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("手柄为什么决定出发和到达方向？", "端点切线来自三次贝塞尔的导数")
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)

        p0 = LEFT * 5.0 + DOWN * 1.45
        p1 = LEFT * 3.4 + UP * 1.55
        p2 = LEFT * 0.85 + UP * 1.35
        p3 = RIGHT * 1.15 + DOWN * 1.35
        points = [p0, p1, p2, p3]
        handles = VGroup(Line(p0, p1, color=BLUE, stroke_width=3), Line(p2, p3, color=BLUE, stroke_width=3))
        curve = bezier_curve(points, AMBER, 8)
        dots = control_polygon(points, [AMBER, BLUE, BLUE, AMBER])[1]
        point_labels = VGroup(
            MathTex(r"P_0", color=AMBER).scale(0.5).next_to(p0, LEFT + DOWN, buff=0.08),
            MathTex(r"P_1", color=BLUE).scale(0.48).next_to(p1, UP, buff=0.08),
            MathTex(r"P_2", color=BLUE).scale(0.48).next_to(p2, UP, buff=0.08),
            MathTex(r"P_3", color=AMBER).scale(0.5).next_to(p3, RIGHT + DOWN, buff=0.08),
        )
        self.play(FadeIn(handles), FadeIn(dots), FadeIn(point_labels), Create(curve), run_time=1.3)

        start_arrow = Arrow(p0, p0 + normalize(p1 - p0) * 1.7, color=MINT, buff=0, stroke_width=6)
        end_arrow = Arrow(p3 - normalize(p3 - p2) * 1.7, p3, color=ROSE, buff=0, stroke_width=6)
        start_label = cn("离开起点的方向", 0.27, MINT).next_to(start_arrow, LEFT, buff=0.14).shift(DOWN * 0.12)
        end_label = cn("进入终点的方向", 0.27, ROSE).next_to(end_arrow, RIGHT, buff=0.12).shift(DOWN * 0.1)
        self.play(GrowArrow(start_arrow), FadeIn(start_label), run_time=1.0)
        self.play(GrowArrow(end_arrow), FadeIn(end_label), run_time=1.0)

        box = panel(4.7, 2.25).to_edge(RIGHT, buff=0.35).shift(UP * 1.1)
        f1 = MathTex(r"B'(0)=3(P_1-P_0)", color=MINT).scale(0.68)
        f2 = MathTex(r"B'(1)=3(P_3-P_2)", color=ROSE).scale(0.68)
        note = cn("方向和长度，都来自端点处的导数。", 0.28, MUTED)
        stack = VGroup(f1, f2, note).arrange(DOWN, aligned_edge=LEFT, buff=0.26).move_to(box)
        self.play(FadeIn(box, shift=LEFT * 0.12), Write(f1), run_time=1.0)
        self.play(Write(f2), FadeIn(note), run_time=1.0)

        long_handle = Line(p0, p0 + (p1 - p0) * 1.35, color=MINT, stroke_width=5)
        short_handle = Line(p3 - (p3 - p2) * 0.55, p3, color=ROSE, stroke_width=5)
        self.play(Transform(handles[0], long_handle), Transform(handles[1], short_handle), run_time=1.4)
        self.play(curve.animate.set_stroke(width=10), run_time=0.8)
        finish_to(self, TARGET_DURATIONS["EndpointTangents"])


class SmoothJoin(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("两段曲线怎样接得平滑？", "连接点和两侧导数要说同一件事")
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)

        join = ORIGIN + DOWN * 0.25
        p = [LEFT * 5 + DOWN * 1.5, LEFT * 3.0 + UP * 1.25, LEFT * 1.0 + UP * 1.0, join]
        q_bad = [join, RIGHT * 0.7 + DOWN * 1.35, RIGHT * 3.2 + UP * 1.4, RIGHT * 5 + DOWN * 1.45]
        q_direction = [join, join + normalize(join - p[2]) * 2.15, RIGHT * 3.2 + UP * 1.4, RIGHT * 5 + DOWN * 1.45]
        q_equal = [join, join + (join - p[2]), RIGHT * 3.2 + UP * 1.4, RIGHT * 5 + DOWN * 1.45]

        first = bezier_curve(p, AMBER, 8)
        second_bad = bezier_curve(q_bad, ROSE, 8)
        handles_bad = VGroup(
            Line(p[2], join, color=BLUE, stroke_width=3),
            Line(join, q_bad[1], color=ROSE, stroke_width=3),
        )
        join_dot = Dot(join, color=MINT, radius=0.085)
        p2_dot = Dot(p[2], color=BLUE, radius=0.075)
        q1_bad_dot = Dot(q_bad[1], color=ROSE, radius=0.075)
        join_label = MathTex(r"P_3=Q_0", color=MINT).scale(0.48).next_to(join, DOWN, buff=0.12)
        p2_label = MathTex(r"P_2", color=BLUE).scale(0.46).next_to(p[2], LEFT, buff=0.1)
        q1_bad_label = MathTex(r"Q_1", color=ROSE).scale(0.46).next_to(q_bad[1], DOWN, buff=0.08)
        key_points_bad = VGroup(p2_dot, q1_bad_dot, join_label, p2_label, q1_bad_label)
        self.play(Create(first), Create(second_bad), FadeIn(handles_bad), FadeIn(join_dot), FadeIn(key_points_bad), run_time=1.7)
        kink = cn("连接点重合，但方向突然折了一下。", 0.32, MUTED).to_edge(DOWN, buff=0.55)
        self.play(FadeIn(kink), run_time=0.7)

        second_direction = bezier_curve(q_direction, AMBER, 8)
        handles_direction = VGroup(
            Line(p[2], join, color=BLUE, stroke_width=3),
            Line(join, q_direction[1], color=BLUE, stroke_width=3),
        )
        key_points_direction = VGroup(
            Dot(p[2], color=BLUE, radius=0.075),
            Dot(q_direction[1], color=BLUE, radius=0.075),
            MathTex(r"P_3=Q_0", color=MINT).scale(0.48).next_to(join, DOWN, buff=0.12),
            MathTex(r"P_2", color=BLUE).scale(0.46).next_to(p[2], LEFT, buff=0.1),
            MathTex(r"Q_1", color=BLUE).scale(0.46).next_to(q_direction[1], DOWN, buff=0.08),
        )
        smooth_note = cn("两侧手柄排成一条直线，切线方向就接上了。", 0.32, AMBER).to_edge(DOWN, buff=0.55)
        if self.time < 4.55:
            self.wait(4.55 - self.time)
        self.play(
            Transform(second_bad, second_direction),
            Transform(handles_bad, handles_direction),
            Transform(key_points_bad, key_points_direction),
            Transform(kink, smooth_note),
            run_time=1.8,
        )

        box = panel(6.6, 2.15).to_edge(RIGHT, buff=0.35).shift(UP * 1.2)
        f1 = MathTex(r"P_3=Q_0", color=MINT).scale(0.68)
        f_direction = MathTex(r"P_3-P_2\parallel Q_1-Q_0", color=AMBER).scale(0.58)
        text = cn("方向接上，长度还没有锁定。", 0.28, MUTED)
        stack = VGroup(f1, f_direction, text).arrange(DOWN, aligned_edge=LEFT, buff=0.26).move_to(box)
        self.play(FadeIn(box, shift=LEFT * 0.12), Write(f1), run_time=0.8)
        self.play(Write(f_direction), FadeIn(text), run_time=0.8)

        second_equal = bezier_curve(q_equal, AMBER, 8)
        handles_equal = VGroup(
            Line(p[2], join, color=BLUE, stroke_width=3),
            Line(join, q_equal[1], color=BLUE, stroke_width=3),
        )
        key_points_equal = VGroup(
            Dot(p[2], color=BLUE, radius=0.075),
            Dot(q_equal[1], color=BLUE, radius=0.075),
            MathTex(r"P_3=Q_0", color=MINT).scale(0.48).next_to(join, DOWN, buff=0.12),
            MathTex(r"P_2", color=BLUE).scale(0.46).next_to(p[2], LEFT, buff=0.1),
            MathTex(r"Q_1", color=BLUE).scale(0.46).next_to(q_equal[1], DOWN, buff=0.08),
        )
        left_vector = Arrow(p[2], join, color=AMBER, buff=0.08, stroke_width=7, max_tip_length_to_length_ratio=0.16)
        right_vector = Arrow(join, q_equal[1], color=AMBER, buff=0.08, stroke_width=7, max_tip_length_to_length_ratio=0.16)
        left_label = MathTex(r"P_3-P_2", color=AMBER).scale(0.43).next_to(left_vector, LEFT, buff=0.10)
        right_label = MathTex(r"Q_1-Q_0", color=AMBER).scale(0.43).next_to(right_vector, RIGHT, buff=0.10)
        vectors = VGroup(left_vector, right_vector, left_label, right_label)
        f_equal = MathTex(r"P_3-P_2=Q_1-Q_0", color=AMBER).scale(0.62).move_to(f_direction)
        strict_text = cn("导数向量相等，方向和长度都相同。", 0.28, MUTED).move_to(text)
        strict_note = cn("更严格一点：两边的导数向量相等。", 0.32, AMBER).to_edge(DOWN, buff=0.55)
        if self.time < 12.05:
            self.wait(12.05 - self.time)
        self.play(
            Transform(second_bad, second_equal),
            Transform(handles_bad, handles_equal),
            Transform(key_points_bad, key_points_equal),
            Transform(f_direction, f_equal),
            Transform(text, strict_text),
            Transform(kink, strict_note),
            GrowArrow(left_vector),
            GrowArrow(right_vector),
            FadeIn(VGroup(left_label, right_label), shift=UP * 0.05),
            run_time=1.55,
        )
        finish_to(self, TARGET_DURATIONS["SmoothJoin"])


class ProgrammingLinks(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("编程里的贝塞尔曲线", "程序通常存控制点，再按公式算路径")
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)

        left_panel = panel(5.4, 4.9).to_edge(LEFT, buff=0.45).shift(DOWN * 0.2)
        right_panel = panel(5.7, 4.9).to_edge(RIGHT, buff=0.45).shift(DOWN * 0.2)
        self.play(FadeIn(left_panel), FadeIn(right_panel), run_time=0.8)

        graph_origin = left_panel.get_left() + RIGHT * 0.78 + DOWN * 1.78
        graph_width = 3.55
        graph_height = 2.35
        css_x1 = ValueTracker(0.42)
        css_y1 = ValueTracker(0.0)
        css_x2 = ValueTracker(0.58)
        css_y2 = ValueTracker(1.0)
        sample_t = ValueTracker(0.0)
        x_axis = Line(graph_origin, graph_origin + RIGHT * graph_width, color=BLUE, stroke_width=3)
        y_axis = Line(graph_origin, graph_origin + UP * graph_height, color=BLUE, stroke_width=3)

        def css_values() -> tuple[float, float, float, float]:
            return css_x1.get_value(), css_y1.get_value(), css_x2.get_value(), css_y2.get_value()

        def css_point(x: float, y: float) -> np.ndarray:
            return graph_origin + RIGHT * (x * graph_width) + UP * (y * graph_height)

        def css_points() -> list[np.ndarray]:
            x1, y1, x2, y2 = css_values()
            return [
                graph_origin,
                css_point(x1, y1),
                css_point(x2, y2),
                graph_origin + RIGHT * graph_width + UP * graph_height,
            ]

        def css_num(value: float) -> str:
            if abs(value) < 0.005:
                return "0"
            if abs(value - 1) < 0.005:
                return "1"
            return f"{value:.2f}".replace("0.", ".")

        def css_code_text() -> Text:
            x1, y1, x2, y2 = css_values()
            return code_line(
                f"cubic-bezier({css_num(x1)}, {css_num(y1)}, {css_num(x2)}, {css_num(y2)});",
                0.25,
                INK,
            )

        easing = always_redraw(lambda: bezier_curve(css_points(), AMBER, 7))
        handles = always_redraw(
            lambda: VGroup(
                Line(css_points()[0], css_points()[1], color=BLUE, stroke_width=2.6),
                Line(css_points()[2], css_points()[3], color=BLUE, stroke_width=2.6),
            )
        )
        easing_dots = always_redraw(
            lambda: VGroup(
                *[
                    Dot(point, color=AMBER if index in (0, 3) else BLUE, radius=0.055)
                    for index, point in enumerate(css_points())
                ]
            )
        )
        easing_labels = always_redraw(
            lambda: VGroup(
                MathTex(r"P_0", color=AMBER).scale(0.34).next_to(css_points()[0], LEFT + DOWN, buff=0.04),
                MathTex(r"P_1", color=BLUE).scale(0.34).next_to(css_points()[1], DOWN, buff=0.06),
                MathTex(r"P_2", color=BLUE).scale(0.34).next_to(css_points()[2], UP, buff=0.06),
                MathTex(r"P_3", color=AMBER).scale(0.34).next_to(css_points()[3], RIGHT + UP, buff=0.04),
            )
        )
        css_marker = always_redraw(
            lambda: Dot(cubic_point(css_points(), sample_t.get_value()), color=ROSE, radius=0.06)
        )
        graph_label = cn("动画缓动曲线", 0.31, AMBER).next_to(y_axis, UP, buff=0.18)
        css_anchor = left_panel.get_top() + DOWN * 0.62
        css_header = code_line("transition-timing-function:", 0.24, MUTED).move_to(css_anchor).align_to(left_panel, LEFT).shift(RIGHT * 0.5)
        css_code = always_redraw(lambda: css_code_text().next_to(css_header, DOWN, buff=0.16).align_to(css_header, LEFT))
        css_map = always_redraw(
            lambda: VGroup(
                latin_label("P0=(0,0), P3=(1,1) fixed", 0.2, MUTED),
                latin_label(
                    f"P1=({css_num(css_x1.get_value())},{css_num(css_y1.get_value())}), "
                    f"P2=({css_num(css_x2.get_value())},{css_num(css_y2.get_value())})",
                    0.22,
                    BLUE,
                ),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.08).next_to(css_code, DOWN, buff=0.14).align_to(css_header, LEFT)
        )
        axis_hint = latin_label("x=time, y=progress", 0.18, MUTED).next_to(x_axis, DOWN, buff=0.1)
        self.play(
            FadeIn(VGroup(css_header, css_code)),
            FadeIn(css_map, shift=DOWN * 0.05),
            Create(x_axis),
            Create(y_axis),
            FadeIn(handles),
            FadeIn(easing_dots),
            FadeIn(easing_labels),
            Create(easing),
            FadeIn(graph_label),
            FadeIn(axis_hint),
            run_time=2.0,
        )

        def map_row(left_text: str, right_tex: str, color: str) -> VGroup:
            row_box = RoundedRectangle(
                width=4.9,
                height=0.66,
                corner_radius=0.08,
                stroke_color="#36516B",
                stroke_width=1.2,
                fill_color="#132238",
                fill_opacity=0.94,
            )
            left = code_line(left_text, 0.27, color).move_to(row_box.get_left() + RIGHT * 1.05)
            arrow = MathTex(r"\rightarrow", color=MUTED).scale(0.52).move_to(row_box)
            right = MathTex(right_tex, color=color).scale(0.52).move_to(row_box.get_right() + LEFT * 1.42)
            return VGroup(row_box, left, arrow, right)

        def css_mapping_group() -> VGroup:
            x1, y1, x2, y2 = css_values()
            css_mapping_title = cn("CSS 参数映射", 0.42, AMBER)
            css_mapping_func = code_line("cubic-bezier(x1, y1, x2, y2)", 0.3, INK)
            css_mapping_fixed = latin_label("P0=(0,0), P3=(1,1)", 0.3, MUTED)
            css_mapping_rows = VGroup(
                map_row(f"({css_num(x1)}, {css_num(y1)})", r"P_1=(x_1,y_1)", BLUE),
                map_row(f"({css_num(x2)}, {css_num(y2)})", r"P_2=(x_2,y_2)", MINT),
            ).arrange(DOWN, buff=0.14)
            css_mapping_hint = cn("x 是时间输入，y 是输出进度", 0.31, MUTED)
            css_mapping = VGroup(
                css_mapping_title,
                css_mapping_func,
                css_mapping_fixed,
                css_mapping_rows,
                css_mapping_hint,
            ).arrange(DOWN, buff=0.2)
            css_mapping.move_to(right_panel).shift(UP * 0.12)
            return css_mapping

        css_mapping = always_redraw(css_mapping_group)
        self.play(FadeIn(css_mapping, shift=UP * 0.08), run_time=1.0)
        self.wait(0.6)
        self.add(css_marker)
        self.play(
            css_x1.animate.set_value(0.28),
            css_y1.animate.set_value(0.24),
            css_x2.animate.set_value(0.82),
            css_y2.animate.set_value(0.88),
            sample_t.animate.set_value(1.0),
            run_time=3.0,
            rate_func=smooth,
        )
        self.play(
            css_x1.animate.set_value(0.56),
            css_y1.animate.set_value(0.04),
            css_x2.animate.set_value(0.70),
            css_y2.animate.set_value(1.0),
            sample_t.animate.set_value(0.18),
            run_time=2.4,
            rate_func=smooth,
        )

        svg_c1x = ValueTracker(110)
        svg_c1y = ValueTracker(20)
        svg_c2x = ValueTracker(210)
        svg_c2y = ValueTracker(20)
        svg_left = right_panel.get_center() + LEFT * 2.1 + DOWN * 1.25
        svg_right = right_panel.get_center() + RIGHT * 2.0 + DOWN * 1.2
        svg_top_y = right_panel.get_center()[1] + 0.95
        svg_bottom_y = right_panel.get_center()[1] - 1.35
        svg_left_x = svg_left[0]
        svg_right_x = svg_right[0]

        def svg_point(x: float, y: float) -> np.ndarray:
            sx = svg_left_x + (x - 40) / 240 * (svg_right_x - svg_left_x)
            sy = svg_bottom_y + (180 - y) / 160 * (svg_top_y - svg_bottom_y)
            return np.array([sx, sy, 0.0])

        def svg_points() -> list[np.ndarray]:
            return [
                svg_point(40, 180),
                svg_point(svg_c1x.get_value(), svg_c1y.get_value()),
                svg_point(svg_c2x.get_value(), svg_c2y.get_value()),
                svg_point(280, 180),
            ]

        def svg_code_group() -> VGroup:
            c1x, c1y = round(svg_c1x.get_value()), round(svg_c1y.get_value())
            c2x, c2y = round(svg_c2x.get_value()), round(svg_c2y.get_value())
            return VGroup(
                code_line('d="M 40 180', 0.24, MUTED),
                code_line(f'   C {c1x} {c1y}, {c2x} {c2y}, 280 180"', 0.24, INK),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(right_panel.get_top() + DOWN * 0.38)

        svg_curve = always_redraw(lambda: bezier_curve(svg_points(), MINT, 8))
        svg_handles = always_redraw(
            lambda: VGroup(
                Line(svg_points()[0], svg_points()[1], color=BLUE, stroke_width=2.6),
                Line(svg_points()[2], svg_points()[3], color=BLUE, stroke_width=2.6),
            )
        )
        svg_dots = always_redraw(
            lambda: VGroup(*[Dot(p, color=AMBER if i in (0, 3) else BLUE, radius=0.06) for i, p in enumerate(svg_points())])
        )
        svg_labels = always_redraw(
            lambda: VGroup(
                *[
                    MathTex(fr"P_{i}", color=AMBER if i in (0, 3) else BLUE).scale(0.38).next_to(
                        svg_points()[i],
                        DOWN if i in (0, 3) else UP,
                        buff=0.06,
                    )
                    for i in range(4)
                ]
            )
        )
        svg_marker = always_redraw(lambda: Dot(cubic_point(svg_points(), sample_t.get_value()), color=ROSE, radius=0.065))
        svg_code = always_redraw(svg_code_group)
        self.play(FadeOut(css_mapping, shift=UP * 0.08), run_time=0.4)
        self.play(FadeIn(svg_code), FadeIn(svg_handles), FadeIn(svg_dots), FadeIn(svg_labels), Create(svg_curve), run_time=1.8)

        def canvas_code_group() -> VGroup:
            c1x, c1y = round(svg_c1x.get_value()), round(svg_c1y.get_value())
            c2x, c2y = round(svg_c2x.get_value()), round(svg_c2y.get_value())
            return VGroup(
                code_line("ctx.moveTo(40, 180);", 0.20, MUTED),
                code_line(f"ctx.bezierCurveTo({c1x},{c1y},{c2x},{c2y},280,180);", 0.18, INK),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.11).next_to(svg_code, DOWN, buff=0.16).align_to(svg_code, LEFT)

        canvas_code = always_redraw(canvas_code_group)
        self.play(FadeIn(canvas_code, shift=UP * 0.08), run_time=1.0)

        formula_box = panel(10.5, 1.38).to_edge(DOWN, buff=0.35)
        formula = MathTex(
            r"B(t)=(1-t)^3P_0+3(1-t)^2tP_1+3(1-t)t^2P_2+t^3P_3",
            color=INK,
        ).scale(0.50).move_to(formula_box).shift(UP * 0.28)
        note = cn("存下控制点，运行时按公式算出曲线上的位置。", 0.25, MUTED).next_to(formula, DOWN, buff=0.08)
        self.play(FadeIn(formula_box), Write(formula), FadeIn(note), run_time=1.3)

        payoff = cn("钢笔工具、SVG 路径、Canvas、网页动画，背后用的是同一种规则。", 0.25, AMBER)
        payoff.next_to(note, DOWN, buff=0.08)
        self.play(FadeIn(payoff, shift=UP * 0.08), run_time=1.0)
        self.add(svg_marker)
        self.play(
            css_x1.animate.set_value(0.42),
            css_y1.animate.set_value(0.0),
            css_x2.animate.set_value(0.58),
            css_y2.animate.set_value(1.0),
            svg_c1x.animate.set_value(88),
            svg_c1y.animate.set_value(55),
            svg_c2x.animate.set_value(235),
            svg_c2y.animate.set_value(28),
            sample_t.animate.set_value(0.92),
            run_time=4.0,
            rate_func=smooth,
        )
        self.play(
            css_x1.animate.set_value(0.22),
            css_y1.animate.set_value(0.0),
            css_x2.animate.set_value(0.76),
            css_y2.animate.set_value(1.0),
            svg_c1x.animate.set_value(128),
            svg_c1y.animate.set_value(8),
            svg_c2x.animate.set_value(188),
            svg_c2y.animate.set_value(92),
            sample_t.animate.set_value(0.18),
            run_time=4.1,
            rate_func=smooth,
        )
        self.play(
            css_x1.animate.set_value(0.42),
            css_y1.animate.set_value(0.0),
            css_x2.animate.set_value(0.58),
            css_y2.animate.set_value(1.0),
            svg_c1x.animate.set_value(110),
            svg_c1y.animate.set_value(20),
            svg_c2x.animate.set_value(210),
            svg_c2y.animate.set_value(20),
            sample_t.animate.set_value(1.0),
            run_time=4.0,
            rate_func=smooth,
        )
        self.play(sample_t.animate.set_value(0.0), run_time=1.2, rate_func=smooth)
        finish_to(self, TARGET_DURATIONS["ProgrammingLinks"])


class ProgrammingLinksHybridShell(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("编程里的贝塞尔曲线", "程序通常存控制点，再按公式算路径")
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)

        formula_box = panel(10.5, 1.38).to_edge(DOWN, buff=0.35)
        formula = MathTex(
            r"B(t)=(1-t)^3P_0+3(1-t)^2tP_1+3(1-t)t^2P_2+t^3P_3",
            color=INK,
        ).scale(0.50).move_to(formula_box).shift(UP * 0.28)
        note = cn("存下控制点，运行时按公式算出曲线上的位置。", 0.25, MUTED).next_to(formula, DOWN, buff=0.08)
        payoff = cn("CSS 缓动、SVG 路径、Canvas 和交互动画，背后用的是同一种控制点规则。", 0.25, AMBER)
        payoff.next_to(note, DOWN, buff=0.08)

        if self.time < 21.5:
            self.wait(21.5 - self.time)
        self.play(FadeIn(formula_box), Write(formula), FadeIn(note), run_time=1.3)
        self.play(FadeIn(payoff, shift=UP * 0.08), run_time=1.0)
        finish_to(self, TARGET_DURATIONS["ProgrammingLinks"])
