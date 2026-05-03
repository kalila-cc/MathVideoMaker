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

BG = "#07111F"
INK = "#F8F4E3"
MUTED = "#AAB4C2"
BLUE = "#7DD3FC"
AMBER = "#F6B73C"
MINT = "#5EEAD4"
ROSE = "#FF5C7A"
VIOLET = "#A78BFA"
PANEL = "#0D1727"
GRID_COLOR = "#8FA8D8"

PANEL_TITLE_SIZE = 0.42
PANEL_BODY_SIZE = 0.34
PANEL_NOTE_SIZE = 0.34
PANEL_FORMULA_SIZE = 0.66
PANEL_FORMULA_LARGE_SIZE = 0.72
PANEL_FORMULA_SMALL_SIZE = 0.54

LATIN_PATTERN = re.compile(r"[A-Za-z0-9_.:/,+#()-]+")

TIMES_TEX_TEMPLATE = TexTemplate()
TIMES_TEX_TEMPLATE.add_to_preamble(r"\usepackage{mathptmx}")
MathTex.set_default(tex_template=TIMES_TEX_TEMPLATE)

TARGET_DURATIONS = {
    "StoryHook": 11.56,
    "CircleCoordinates": 20.78,
    "ReflectionGeometry": 66.78,
    "RayLineEquation": 57.86,
    "RayFamilyEnvelope": 15.58,
    "EnvelopeCondition": 33.09,
    "NephroidPayoff": 71.78,
    "RealityEcho": 15.55,
}


def latin_font_map(text: str) -> dict[str, str]:
    return {token: LATIN_FONT for token in LATIN_PATTERN.findall(text)}


def cn(text: str, size: float = 0.36, color: str = INK) -> Text:
    with register_font(SMILEY_FONT_FILE):
        return Text(text, font=FONT, slant=OBLIQUE, color=color).scale(size)


def finish_to(scene: Scene, target: float) -> None:
    remaining = target - scene.time
    if remaining > 0:
        scene.wait(remaining)


def notebook_grid(spacing: float = 0.48) -> VGroup:
    width = config.frame_width + spacing
    height = config.frame_height + spacing
    xs = np.arange(-width / 2, width / 2 + spacing, spacing)
    ys = np.arange(-height / 2, height / 2 + spacing, spacing)
    grid = VGroup(
        *[
            Line(DOWN * height / 2 + RIGHT * x, UP * height / 2 + RIGHT * x, color=GRID_COLOR, stroke_width=1.6)
            for x in xs
        ],
        *[
            Line(LEFT * width / 2 + UP * y, RIGHT * width / 2 + UP * y, color=GRID_COLOR, stroke_width=1.6)
            for y in ys
        ],
    )
    grid.set_opacity(0.155)
    grid.set_z_index(-100)
    return grid


def set_scene_background(scene: Scene) -> None:
    scene.camera.background_color = BG
    scene.add(notebook_grid())


def scene_title(title: str, subtitle: str | None = None) -> VGroup:
    heading = cn(title, 0.52).to_edge(UP, buff=0.34)
    if subtitle is None:
        return VGroup(heading)
    sub = cn(subtitle, 0.30, MUTED).next_to(heading, DOWN, buff=0.10)
    return VGroup(heading, sub)


def cup_circle(center: np.ndarray = ORIGIN, radius: float = 2.35, opacity: float = 1.0) -> VGroup:
    rim = Circle(radius=radius, color=BLUE, stroke_width=5, stroke_opacity=opacity)
    water = Circle(radius=radius * 0.97, stroke_width=0, fill_color="#10213A", fill_opacity=0.42 * opacity)
    inner = Circle(radius=radius * 0.83, color="#22344D", stroke_width=2, stroke_opacity=0.46 * opacity)
    return VGroup(water, rim, inner).move_to(center)


def coordinate_axes(
    center: np.ndarray,
    x_left: float,
    x_right: float,
    y_down: float,
    y_up: float,
    opacity: float = 0.78,
) -> VGroup:
    axes = VGroup(
        Line(
            center + LEFT * x_left,
            center + RIGHT * x_right,
            color="#3C5068",
            stroke_width=3,
            stroke_opacity=opacity,
        ),
        Line(
            center + DOWN * y_down,
            center + UP * y_up,
            color="#3C5068",
            stroke_width=3,
            stroke_opacity=opacity,
        ),
    )
    x_label = MathTex("x", color=MUTED).scale(0.42).next_to(axes[0], RIGHT, buff=0.05)
    y_label = MathTex("y", color=MUTED).scale(0.42).next_to(axes[1], UP, buff=0.05)
    group = VGroup(axes, x_label, y_label)
    group.set_opacity(opacity)
    group.set_z_index(-2)
    return group


def p_on_cup(t: float, center: np.ndarray = ORIGIN, radius: float = 2.35) -> np.ndarray:
    return center + radius * np.array([np.cos(t), np.sin(t), 0.0])


def reflected_segment(
    t: float,
    center: np.ndarray = ORIGIN,
    radius: float = 2.35,
    color: str = BLUE,
    width: float = 3.0,
    opacity: float = 0.45,
) -> Line:
    local = radius * np.array([np.cos(t), np.sin(t), 0.0])
    point = center + local
    direction = np.array([-np.cos(2 * t), -np.sin(2 * t), 0.0])
    chord_step = -2 * float(np.dot(local, direction)) * direction
    other = point + chord_step
    return Line(point, other, color=color, stroke_width=width, stroke_opacity=opacity)


def incoming_ray(
    y: float,
    center: np.ndarray = ORIGIN,
    radius: float = 2.35,
    color: str = MINT,
    opacity: float = 0.45,
) -> Line:
    x_hit = center[0] + np.sqrt(max(radius * radius - (y - center[1]) ** 2, 0.0))
    return Line(
        np.array([center[0] - radius - 2.0, y, 0.0]),
        np.array([x_hit, y, 0.0]),
        color=color,
        stroke_width=3,
        stroke_opacity=opacity,
    )


def ray_direction_cue(
    ray: Line,
    color: str,
    proportion: float = 0.62,
    length: float = 0.46,
    width: float = 4.0,
    opacity: float = 1.0,
) -> Arrow:
    start = ray.get_start()
    end = ray.get_end()
    vector = end - start
    norm = np.linalg.norm(vector)
    if norm < 1e-6:
        vector = RIGHT
        norm = 1.0
    unit = vector / norm
    anchor = ray.point_from_proportion(proportion)
    cue = Arrow(
        anchor - unit * length * 0.5,
        anchor + unit * length * 0.5,
        buff=0,
        color=color,
        stroke_width=width,
    )
    cue.set_opacity(opacity)
    cue.set_z_index(4)
    return cue


def caustic_point(t: float, center: np.ndarray = ORIGIN, radius: float = 2.35) -> np.ndarray:
    return center + radius * np.array(
        [1.5 * np.cos(t) - np.cos(t) ** 3, np.sin(t) ** 3, 0.0]
    )


def rolling_center_point(t: float, center: np.ndarray = ORIGIN, radius: float = 2.35) -> np.ndarray:
    return center + (radius * 0.75) * np.array([np.cos(t), np.sin(t), 0.0])


def rolling_trace_point(t: float, center: np.ndarray = ORIGIN, radius: float = 2.35) -> np.ndarray:
    return rolling_center_point(t, center, radius) - (radius * 0.25) * np.array(
        [np.cos(3 * t), np.sin(3 * t), 0.0]
    )


def caustic_curve(
    center: np.ndarray = ORIGIN,
    radius: float = 2.35,
    start: float = -PI / 2,
    end: float = PI / 2,
    color: str = AMBER,
    width: float = 8,
) -> ParametricFunction:
    return ParametricFunction(
        lambda t: caustic_point(t, center, radius),
        t_range=[start, end],
        color=color,
        stroke_width=width,
    )


def reflected_family(ts: Iterable[float], center: np.ndarray, radius: float, opacity: float = 0.22) -> VGroup:
    return VGroup(
        *[
            reflected_segment(t, center=center, radius=radius, color=BLUE, width=2.2, opacity=opacity)
            for t in ts
        ]
    )


def label_box(text: str, color: str = INK) -> VGroup:
    label = cn(text, 0.28, color)
    box = RoundedRectangle(
        width=label.width + 0.34,
        height=label.height + 0.20,
        corner_radius=0.10,
        stroke_color="#314054",
        fill_color=PANEL,
        fill_opacity=0.88,
    ).move_to(label)
    return VGroup(box, label)


def symbol_label_box(symbol: str, desc: str, color: str = INK) -> VGroup:
    symbol_mob = MathTex(symbol, color=color).scale(0.42)
    desc_mob = cn(desc, 0.25, color)
    label = VGroup(symbol_mob, desc_mob).arrange(RIGHT, buff=0.10)
    box = RoundedRectangle(
        width=label.width + 0.34,
        height=label.height + 0.18,
        corner_radius=0.10,
        stroke_color="#314054",
        fill_color=PANEL,
        fill_opacity=0.88,
    ).move_to(label)
    return VGroup(box, label)


def formula_panel(width: float = 5.8, height: float = 5.5) -> RoundedRectangle:
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.18,
        stroke_color="#2A3A50",
        stroke_width=1.4,
        fill_color=PANEL,
        fill_opacity=0.94,
    )


def fit_inside(mobject: Mobject, max_width: float | None = None, max_height: float | None = None) -> Mobject:
    if max_width is not None and mobject.width > max_width:
        mobject.scale_to_fit_width(max_width)
    if max_height is not None and mobject.height > max_height:
        mobject.scale_to_fit_height(max_height)
    return mobject


class CoverFrame(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = cn("杯子里的", 0.90)
        title2 = cn("心形光斑", 1.08, AMBER)
        title_group = VGroup(title, title2).arrange(DOWN, buff=0.04, aligned_edge=LEFT)
        title_group.scale_to_fit_width(6.05).to_corner(UL, buff=0.48).shift(RIGHT * 0.28)

        center = RIGHT * 2.72 + DOWN * 0.10
        cup = cup_circle(center, 2.05)
        rays = VGroup(
            *[
                incoming_ray(y, center=center, radius=2.05, opacity=0.46)
                for y in np.linspace(center[1] - 1.72, center[1] + 1.72, 11)
            ]
        )
        reflected = VGroup(
            *[
                reflected_segment(t, center=center, radius=2.05, color=BLUE, width=2.65, opacity=0.34)
                for t in np.linspace(-PI / 2 + 0.08, PI / 2 - 0.08, 42)
            ]
        )
        incoming_cue = ray_direction_cue(rays[4], MINT, proportion=0.64, length=0.42, width=4, opacity=0.88)
        subtitle = cn("平行光反射后，擦出一条焦散曲线", 0.38, MUTED)
        subtitle.next_to(title_group, DOWN, buff=0.30).align_to(title_group, LEFT)

        self.add(rays, cup, reflected, incoming_cue, title_group, subtitle)
        self.wait(0.75)


class StoryHook(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("杯壁上突然出现的亮线", "它像一颗心，但不是杯子上的花纹")
        center = LEFT * 1.55 + DOWN * 0.25
        cup = cup_circle(center, 2.35)
        rays = VGroup(
            *[
                incoming_ray(y, center=center, radius=2.35, opacity=0.0)
                for y in np.linspace(center[1] - 1.85, center[1] + 1.85, 10)
            ]
        )
        reflected = reflected_family(np.linspace(-PI / 2 + 0.12, PI / 2 - 0.12, 25), center, 2.35, opacity=0.0)
        incoming_cue = ray_direction_cue(rays[5], MINT, proportion=0.64, length=0.44, width=4, opacity=0.92)
        glow = caustic_curve(center, 2.35, width=24).set_stroke(color=AMBER, opacity=0.0)
        glow.set_fill(opacity=0)
        curve = caustic_curve(center, 2.35, width=8).set_stroke(color=AMBER, opacity=0.0)
        curve.set_fill(opacity=0)
        note = cn("亮线来自反射光线的叠加", 0.34, AMBER).to_edge(RIGHT, buff=0.88).shift(DOWN * 1.8)

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)
        self.play(Create(cup), run_time=1.2)
        self.play(rays.animate.set_opacity(0.40), FadeIn(incoming_cue), run_time=1.6)
        self.play(reflected.animate.set_opacity(0.20), run_time=2.2)
        self.play(glow.animate.set_stroke(opacity=0.16), curve.animate.set_stroke(opacity=1.0), run_time=2.4)
        self.play(FadeIn(note, shift=UP * 0.12), run_time=0.8)
        finish_to(self, TARGET_DURATIONS["StoryHook"])


class CircleCoordinates(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("先定位反射点", "圆心、半径和角度都要落到画面上")
        center = LEFT * 2.55 + DOWN * 0.28
        radius = 2.35
        cup = cup_circle(center, radius)
        axes = VGroup(
            Line(center + LEFT * 2.65, center + RIGHT * 2.78, color="#3C5068", stroke_width=3),
            Line(center + DOWN * 2.55, center + UP * 2.65, color="#3C5068", stroke_width=3),
        )
        x_label = MathTex("x", color=MUTED).scale(0.44).next_to(axes[0], RIGHT, buff=0.06)
        y_label = MathTex("y", color=MUTED).scale(0.44).next_to(axes[1], UP, buff=0.06)
        axis_labels = VGroup(x_label, y_label)
        t = 0.82
        point = p_on_cup(t, center, radius)
        normal = Line(center, point, color=ROSE, stroke_width=4)
        radius_label = MathTex("R", color=ROSE).scale(0.55).next_to(normal, DOWN, buff=0.08)
        angle_arc = Arc(radius=0.55, start_angle=0, angle=t, arc_center=center, color=AMBER, stroke_width=4)
        angle_label = MathTex(r"\theta", color=AMBER).scale(0.52).move_to(center + 0.82 * np.array([np.cos(t / 2), np.sin(t / 2), 0.0]))
        hit_dot = Dot(point, color=AMBER, radius=0.08)
        p_label = MathTex(r"P(\theta)", color=AMBER).scale(0.58).next_to(hit_dot, UR, buff=0.08)
        o_dot = Dot(center, color=BLUE, radius=0.06)
        o_label = MathTex("O", color=BLUE).scale(0.55).next_to(o_dot, DL, buff=0.06)
        x_proj = DashedLine(point, np.array([point[0], center[1], 0.0]), color=AMBER, dash_length=0.08)
        y_proj = DashedLine(point, np.array([center[0], point[1], 0.0]), color=MINT, dash_length=0.08)

        panel = formula_panel(5.85, 5.35).to_edge(RIGHT, buff=0.36).shift(DOWN * 0.06)
        p_title = cn("圆周上的反射点", PANEL_TITLE_SIZE, MUTED).move_to(panel.get_top() + DOWN * 0.48)
        p_formula = MathTex(r"P(\theta)=(R\cos\theta,\;R\sin\theta)", color=INK).scale(PANEL_FORMULA_LARGE_SIZE)
        p_formula.next_to(p_title, DOWN, buff=0.30)
        rows = VGroup(
            symbol_label_box("O", "圆心", BLUE),
            symbol_label_box("R", "半径", ROSE),
            symbol_label_box(r"\theta", "角度", AMBER),
            symbol_label_box("OP", "半径线就是法线", ROSE),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        rows.next_to(p_formula, DOWN, buff=0.42).align_to(p_formula, LEFT)
        note = cn("坐标先定位点，反射规则再决定方向。", PANEL_NOTE_SIZE, MUTED).next_to(rows, DOWN, buff=0.34).align_to(rows, LEFT)

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.7)
        self.play(Create(axes), FadeIn(axis_labels), Create(cup), run_time=1.1)
        self.play(FadeIn(o_dot), FadeIn(o_label), Create(normal), FadeIn(radius_label), run_time=1.0)
        self.play(Create(angle_arc), FadeIn(angle_label), FadeIn(hit_dot), FadeIn(p_label), run_time=1.0)
        self.play(Create(x_proj), Create(y_proj), run_time=0.8)
        self.play(FadeIn(panel), FadeIn(p_title), Write(p_formula), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(row, shift=LEFT * 0.10) for row in rows], lag_ratio=0.12), run_time=1.4)
        self.play(FadeIn(note, shift=UP * 0.10), run_time=0.7)
        finish_to(self, TARGET_DURATIONS["CircleCoordinates"])


class ReflectionGeometry(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("反射方向由 θ 决定", "先求方向，下一段再写直线方程")
        center = LEFT * 3.05 + DOWN * 0.22
        radius = 1.92
        cup = cup_circle(center, radius)
        axes = VGroup(
            Line(center + LEFT * 2.35, center + RIGHT * 2.55, color="#3C5068", stroke_width=3),
            Line(center + DOWN * 2.20, center + UP * 2.30, color="#3C5068", stroke_width=3),
        )
        x_axis_label = MathTex("x", color=MUTED).scale(0.42).next_to(axes[0], RIGHT, buff=0.05)
        y_axis_label = MathTex("y", color=MUTED).scale(0.42).next_to(axes[1], UP, buff=0.05)
        axes_group = VGroup(axes, x_axis_label, y_axis_label).set_z_index(-1)
        t = 0.76
        point = p_on_cup(t, center, radius)
        incoming = incoming_ray(point[1], center=center, radius=radius, opacity=0.78)
        reflected = reflected_segment(t, center=center, radius=radius, color=AMBER, width=5, opacity=0.96)
        incoming_arrow = ray_direction_cue(incoming, MINT, proportion=0.72, length=0.48, width=4.5, opacity=0.96)
        reflected_arrow = ray_direction_cue(reflected, AMBER, proportion=0.56, length=0.50, width=5, opacity=0.98)
        normal = Line(center, point, color=ROSE, stroke_width=4)
        normal_direction = (point - center) / np.linalg.norm(point - center)
        tangent_direction = np.array([-np.sin(t), np.cos(t), 0.0])
        tangent = Line(point - tangent_direction * 0.72, point + tangent_direction * 0.72, color=VIOLET, stroke_width=3)
        point_dot = Dot(point, color=AMBER, radius=0.08)
        p_label = MathTex(r"P(\theta)", color=AMBER).scale(0.54).next_to(point_dot, UR, buff=0.06)
        normal_label = cn("法线 OP", 0.25, ROSE).next_to(normal, DOWN, buff=0.05)
        tangent_label = cn("切线", 0.25, VIOLET).next_to(tangent, UP, buff=0.05)
        incoming_label = cn("入射方向", 0.25, MINT).next_to(incoming, UP, buff=0.06)
        reflected_label = cn("反射方向", 0.25, AMBER).next_to(reflected, DOWN, buff=0.05)
        i_vec_label = MathTex(r"\vec{i}", color=MINT).scale(0.54).next_to(incoming_label, RIGHT, buff=0.10)
        n_vec_label = MathTex(r"\vec{n}", color=ROSE).scale(0.54)
        n_vec_label.move_to(center + (point - center) * 0.58 + UP * 0.22 + LEFT * 0.08)
        d_vec_label = MathTex(r"\vec{d}", color=AMBER).scale(0.54).next_to(reflected_label, RIGHT, buff=0.10)

        decomp_anchor = center + LEFT * 1.48 + DOWN * 1.03
        decomp_scale = 1.35
        normal_component = np.cos(t) * normal_direction * decomp_scale
        tangent_component = np.sin(t) * (-tangent_direction) * decomp_scale
        decomp_i = Arrow(decomp_anchor, decomp_anchor + normal_component + tangent_component, buff=0, color=MINT, stroke_width=3)
        decomp_i.set_opacity(0.38)
        perp_arrow = Arrow(decomp_anchor, decomp_anchor + normal_component, buff=0, color=ROSE, stroke_width=4)
        parallel_arrow = Arrow(
            decomp_anchor + normal_component,
            decomp_anchor + normal_component + tangent_component,
            buff=0,
            color=VIOLET,
            stroke_width=4,
        )
        decomp_i_label = MathTex(r"\vec{i}", color=MINT).scale(0.40).next_to(decomp_i, RIGHT, buff=0.04)
        decomp_i_label.set_opacity(0.70)
        perp_part_label = MathTex(r"\vec{i}_{\perp}", color=ROSE).scale(0.42).next_to(perp_arrow, UP, buff=0.03)
        parallel_part_label = MathTex(r"\vec{i}_{\parallel}", color=VIOLET).scale(0.42).next_to(parallel_arrow, RIGHT, buff=0.05)
        decomp_label = cn("方向分解", 0.22, MUTED).next_to(decomp_i, DOWN, buff=0.07)
        decomp_group = VGroup(
            decomp_i,
            decomp_i_label,
            perp_arrow,
            parallel_arrow,
            perp_part_label,
            parallel_part_label,
            decomp_label,
        ).set_z_index(3)

        mirror_hint = VGroup(
            label_box("切线像一小段镜面", VIOLET),
            label_box("方向按法线对称", ROSE),
        ).arrange(DOWN, buff=0.20, aligned_edge=LEFT).next_to(cup, DOWN, buff=0.38).align_to(cup, LEFT)

        panel = formula_panel(6.0, 5.45).to_edge(RIGHT, buff=0.28).shift(DOWN * 0.05)

        def formula_row(tex: str, note: str, color: str = INK, tex_scale: float = PANEL_FORMULA_SIZE) -> VGroup:
            formula = MathTex(tex, color=color).scale(tex_scale)
            label = cn(note, PANEL_BODY_SIZE, MUTED).next_to(formula, RIGHT, buff=0.18)
            row = VGroup(formula, label)
            fit_inside(row, max_width=5.15)
            return row

        def place_step(title_mob: Mobject, *items: Mobject) -> VGroup:
            group = VGroup(title_mob, *items).arrange(DOWN, buff=0.30, aligned_edge=LEFT)
            fit_inside(group, max_width=5.25, max_height=4.60)
            group.move_to(panel.get_center())
            return group

        step1_title = cn("先定局部镜面", PANEL_TITLE_SIZE, MUTED)
        row1 = formula_row(r"\vec{i}=(1,0)", "入射光水平向右", MINT, PANEL_FORMULA_LARGE_SIZE)
        row2 = formula_row(r"\vec{n}=(\cos\theta,\sin\theta)", "法线就是 OP", ROSE, PANEL_FORMULA_SIZE)
        local_note = cn("有了法线和切线，才能谈反射。", PANEL_NOTE_SIZE, MUTED)
        step1 = place_step(step1_title, row1, row2, local_note)

        split_title = cn("把入射方向拆成两块", PANEL_TITLE_SIZE, MUTED)
        row3 = formula_row(r"\vec{i}\cdot\vec{n}=\cos\theta", "投影系数", MUTED, PANEL_FORMULA_SIZE)
        row4 = formula_row(r"\vec{i}_{\perp}=\cos\theta\,\vec{n}", "沿法线", ROSE, PANEL_FORMULA_SIZE)
        row5 = formula_row(r"\vec{i}_{\parallel}=\vec{i}-\vec{i}_{\perp}", "贴切线", VIOLET, PANEL_FORMULA_SIZE)
        step2 = place_step(split_title, row3, row4, row5)

        reflect_title = cn("反射只翻转法线部分", PANEL_TITLE_SIZE, MUTED)
        line6 = MathTex(r"\vec{d}=\vec{i}_{\parallel}-\vec{i}_{\perp}", color=INK).scale(PANEL_FORMULA_LARGE_SIZE)
        line7 = MathTex(r"=\vec{i}-2\cos\theta\,\vec{n}", color=INK).scale(PANEL_FORMULA_LARGE_SIZE)
        reflect_note = cn("这一步只是在求方向。", PANEL_NOTE_SIZE, MUTED)
        step3 = place_step(reflect_title, line6, line7, reflect_note)

        coord_title = cn("再代入法线坐标", PANEL_TITLE_SIZE, MUTED)
        line7b = MathTex(r"\vec{d}=(1,0)-2\cos\theta(\cos\theta,\sin\theta)", color=INK).scale(PANEL_FORMULA_SIZE)
        line8 = MathTex(r"=(1-2\cos^2\theta,\;-2\sin\theta\cos\theta)", color=INK).scale(PANEL_FORMULA_SIZE)
        line9 = MathTex(r"=(-\cos 2\theta,\;-\sin 2\theta)", color=AMBER).scale(PANEL_FORMULA_LARGE_SIZE)
        next_step = cn("方向确定以后，下一段才求直线方程。", PANEL_NOTE_SIZE, MUTED)
        step4 = place_step(coord_title, line7b, line8, line9, next_step)

        tangent_from_base = Arrow(decomp_anchor, decomp_anchor + tangent_component, buff=0, color=VIOLET, stroke_width=4)
        flipped_perp_arrow = Arrow(
            decomp_anchor + tangent_component,
            decomp_anchor + tangent_component - normal_component,
            buff=0,
            color=ROSE,
            stroke_width=4,
        )
        reflected_decomp = Arrow(
            decomp_anchor,
            decomp_anchor + tangent_component - normal_component,
            buff=0,
            color=AMBER,
            stroke_width=4,
        )
        flipped_label = MathTex(r"-\vec{i}_{\perp}", color=ROSE).scale(0.40).next_to(flipped_perp_arrow, LEFT, buff=0.04)
        reflected_decomp_label = MathTex(r"\vec{d}", color=AMBER).scale(0.42).next_to(reflected_decomp, DOWN, buff=0.04)

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=1.0)
        self.play(
            Create(axes_group),
            Create(cup),
            Create(incoming),
            Create(incoming_arrow),
            FadeIn(incoming_label),
            FadeIn(i_vec_label),
            run_time=2.3,
        )
        self.play(FadeIn(point_dot), FadeIn(p_label), Create(normal), FadeIn(normal_label), FadeIn(n_vec_label), run_time=2.3)
        self.play(Create(tangent), FadeIn(tangent_label), FadeIn(mirror_hint[0], shift=UP * 0.10), run_time=2.0)
        self.play(FadeIn(panel), FadeIn(step1, shift=UP * 0.08), run_time=1.7)
        self.play(Indicate(normal, color=ROSE), Indicate(tangent, color=VIOLET), run_time=3.0)
        self.wait(1.5)

        self.play(FadeOut(step1, shift=UP * 0.12), FadeIn(split_title, shift=UP * 0.08), run_time=0.8)
        self.play(Create(decomp_i), FadeIn(decomp_i_label), FadeIn(decomp_label), run_time=2.0)
        self.play(FadeIn(row3, shift=UP * 0.05), Indicate(incoming_arrow, color=MINT), Indicate(normal, color=ROSE), run_time=3.4)
        self.play(Create(perp_arrow), FadeIn(perp_part_label), FadeIn(row4, shift=UP * 0.05), run_time=3.4)
        self.play(Create(parallel_arrow), FadeIn(parallel_part_label), FadeIn(row5, shift=UP * 0.05), run_time=3.0)
        self.play(Indicate(perp_arrow, color=ROSE), Indicate(parallel_arrow, color=VIOLET), run_time=2.0)
        self.wait(1.2)

        self.play(
            FadeOut(VGroup(split_title, row3, row4, row5), shift=UP * 0.12),
            FadeIn(reflect_title, shift=UP * 0.08),
            run_time=0.8,
        )
        self.play(
            Create(reflected),
            Create(reflected_arrow),
            FadeIn(reflected_label),
            FadeIn(d_vec_label),
            FadeIn(mirror_hint[1], shift=UP * 0.10),
            FadeIn(line6, shift=UP * 0.05),
            run_time=3.0,
        )
        self.play(
            perp_arrow.animate.set_opacity(0.25),
            parallel_arrow.animate.set_opacity(0.25),
            Create(tangent_from_base),
            Create(flipped_perp_arrow),
            FadeIn(flipped_label),
            FadeIn(line7, shift=UP * 0.05),
            run_time=3.5,
        )
        self.play(Create(reflected_decomp), FadeIn(reflected_decomp_label), FadeIn(reflect_note), run_time=2.0)
        self.play(Indicate(reflected, color=AMBER), Indicate(reflected_decomp, color=AMBER), run_time=2.0)
        self.wait(1.0)

        self.play(
            FadeOut(VGroup(reflect_title, line6, line7, reflect_note), shift=UP * 0.12),
            FadeIn(coord_title, shift=UP * 0.08),
            run_time=0.8,
        )
        self.play(FadeIn(line7b, shift=UP * 0.05), Indicate(n_vec_label, color=ROSE), run_time=3.0)
        self.play(FadeIn(line8, shift=UP * 0.05), run_time=3.5)
        self.play(FadeIn(line9, shift=UP * 0.05), run_time=3.2)
        self.play(FadeIn(next_step, shift=UP * 0.08), run_time=1.4)
        self.play(Indicate(line9, color=AMBER), Indicate(reflected_arrow, color=AMBER), run_time=2.2)
        self.wait(1.2)
        finish_to(self, TARGET_DURATIONS["ReflectionGeometry"])


class RayLineEquation(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("求反射光线的直线方程", "先把一条光线写成 F(x,y,θ)=0")
        center = LEFT * 3.05 + DOWN * 0.25
        radius = 1.95
        t = 0.70
        cup = cup_circle(center, radius)
        axes_group = coordinate_axes(center, 2.35, 2.45, 2.15, 2.32, opacity=0.74)
        point = p_on_cup(t, center, radius)
        point_dot = Dot(point, color=AMBER, radius=0.08)
        p_label = MathTex(r"P(\theta)", color=AMBER).scale(0.54).next_to(point_dot, UR, buff=0.06)
        incoming = incoming_ray(point[1], center=center, radius=radius, opacity=0.64)
        main_ray = reflected_segment(t, center=center, radius=radius, color=AMBER, width=5, opacity=0.96)
        incoming_arrow = ray_direction_cue(incoming, MINT, proportion=0.72, length=0.48, width=4.5, opacity=0.94)
        main_ray_arrow = ray_direction_cue(main_ray, AMBER, proportion=0.56, length=0.50, width=5, opacity=0.98)
        ray_direction = np.array([-np.cos(2 * t), -np.sin(2 * t), 0.0])
        ray_normal = np.array([np.sin(2 * t), -np.cos(2 * t), 0.0])
        normal_anchor = main_ray.point_from_proportion(0.43)
        ray_normal_arrow = Arrow(normal_anchor, normal_anchor + ray_normal * 0.72, buff=0, color=VIOLET, stroke_width=4)
        ray_normal_label = MathTex(r"\vec{m}", color=VIOLET).scale(0.46).next_to(ray_normal_arrow, RIGHT, buff=0.04)
        d_vec_label = MathTex(r"\vec{d}", color=AMBER).scale(0.52).next_to(main_ray, DOWN, buff=0.04)
        p0_point = main_ray.point_from_proportion(0.50)
        p0_dot = Dot(p0_point, color=INK, radius=0.06)
        p0_label = MathTex(r"P_0\,(x,y)", color=INK).scale(0.34).next_to(p0_dot, LEFT, buff=0.08).shift(DOWN * 0.10)
        displacement = Arrow(
            point,
            p0_point,
            buff=0.08,
            color=INK,
            stroke_width=2.4,
            max_tip_length_to_length_ratio=0.08,
        )
        displacement_label = MathTex(r"P_0-P(\theta)", color=INK).scale(0.32).next_to(displacement, LEFT, buff=0.06)
        nearby = VGroup(
            reflected_segment(t - 0.16, center=center, radius=radius, color=BLUE, width=3, opacity=0.30),
            reflected_segment(t + 0.16, center=center, radius=radius, color=BLUE, width=3, opacity=0.30),
        )
        p_hint = label_box("过 P(θ)", AMBER).next_to(cup, DOWN, buff=0.32).align_to(cup, LEFT)
        d_hint = label_box("沿反射方向", AMBER).next_to(p_hint, RIGHT, buff=0.22)

        panel = formula_panel(6.15, 5.65).to_edge(RIGHT, buff=0.28).shift(DOWN * 0.02)

        def step_group(title_text: str, *items: Mobject) -> VGroup:
            title_mob = cn(title_text, PANEL_TITLE_SIZE, MUTED)
            group = VGroup(title_mob, *items).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
            fit_inside(group, max_width=5.25, max_height=4.80)
            group.move_to(panel.get_center())
            return group

        p_formula = MathTex(r"P(\theta)=(R\cos\theta,\;R\sin\theta)", color=AMBER).scale(PANEL_FORMULA_SIZE)
        d_formula = MathTex(r"\vec{d}=(-\cos 2\theta,\;-\sin 2\theta)", color=AMBER).scale(PANEL_FORMULA_SIZE)
        known_note = cn("这两项来自上一段。", PANEL_NOTE_SIZE, MUTED)
        step1 = step_group("目标：求这条光线的方程", p_formula, d_formula, known_note)

        m_formula = MathTex(r"\vec{m}=(\sin 2\theta,\;-\cos 2\theta)", color=VIOLET).scale(PANEL_FORMULA_SIZE)
        d_dot_m = MathTex(r"\vec d\cdot\vec m=0", color=INK).scale(PANEL_FORMULA_SIZE)
        m_note = cn("m 和 d 垂直，点积为零。", PANEL_NOTE_SIZE, MUTED)
        step2 = step_group("换一个更好写的方向", d_formula.copy(), m_formula, d_dot_m, m_note)

        line_intro = VGroup(
            cn("任意点", PANEL_BODY_SIZE, MUTED),
            cn("在这条光线上", PANEL_BODY_SIZE, MUTED),
        ).arrange(RIGHT, buff=0.06)
        p0_formula = MathTex(r"P_0\,(x,y)", color=INK).scale(PANEL_FORMULA_SIZE)
        point_normal = MathTex(r"\vec{m}\cdot\big(P_0-P(\theta)\big)=0", color=INK).scale(PANEL_FORMULA_SIZE)
        dot_note = cn("位移和 m 垂直，所以点乘为零。", PANEL_NOTE_SIZE, MUTED)
        step3 = step_group("把“在直线上”写成等式", line_intro, p0_formula, point_normal, dot_note)

        point_normal_again = point_normal.copy()
        expanded_step = MathTex(
            r"\begin{aligned}"
            r"&(x-R\cos\theta)\sin 2\theta\\"
            r"&-(y-R\sin\theta)\cos 2\theta=0"
            r"\end{aligned}",
            color=INK,
        ).scale(PANEL_FORMULA_SMALL_SIZE)
        substitute_note = cn("先保留括号，别急着跳到结果。", PANEL_NOTE_SIZE, MUTED)
        step4 = step_group("代入 P 和 m 的坐标", point_normal_again, expanded_step, substitute_note)

        expanded_again = expanded_step.copy()
        line_formula = MathTex(r"x\sin(2\theta)-y\cos(2\theta)=R\sin\theta", color=BLUE).scale(PANEL_FORMULA_SIZE)
        rearrange_note = cn("把只含 R 和 θ 的项移到右边。", PANEL_NOTE_SIZE, MUTED)
        step5 = step_group("整理成直线方程", expanded_again, line_formula, rearrange_note)

        purpose_note = cn("目的：把每条反射光线统一写成", PANEL_NOTE_SIZE, MUTED)
        f_label = MathTex(r"F(x,y,\theta)=0", color=BLUE).scale(PANEL_FORMULA_LARGE_SIZE)
        final_note = cn("θ 连续变化时，下一步才能找包络边界。", PANEL_NOTE_SIZE, MUTED)
        step6 = step_group("为一族光线做准备", line_formula.copy(), purpose_note, f_label, final_note)

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.9)
        self.play(
            Create(axes_group),
            Create(cup),
            Create(incoming),
            Create(incoming_arrow),
            FadeIn(point_dot),
            FadeIn(p_label),
            run_time=1.5,
        )
        self.play(Create(main_ray), Create(main_ray_arrow), FadeIn(d_vec_label), FadeIn(p_hint), FadeIn(d_hint), run_time=2.0)
        self.play(FadeIn(panel), FadeIn(step1, shift=UP * 0.08), run_time=1.6)
        self.play(Indicate(point_dot, color=AMBER), Indicate(main_ray, color=AMBER), run_time=2.5)
        self.wait(1.2)

        self.play(FadeOut(step1, shift=UP * 0.12), FadeIn(step2, shift=UP * 0.08), run_time=0.8)
        self.play(
            Create(ray_normal_arrow),
            FadeIn(ray_normal_label),
            Indicate(main_ray_arrow, color=AMBER),
            run_time=3.5,
        )
        self.play(Indicate(main_ray_arrow, color=AMBER), Indicate(ray_normal_arrow, color=VIOLET), run_time=3.0)
        self.wait(2.0)

        self.play(FadeOut(step2, shift=UP * 0.12), FadeOut(main_ray_arrow), FadeIn(step3, shift=UP * 0.08), run_time=0.8)
        self.play(FadeIn(p0_dot), FadeIn(p0_label), run_time=1.6)
        self.play(Create(displacement), FadeIn(displacement_label), run_time=2.6)
        self.play(Indicate(displacement, color=INK), Indicate(ray_normal_arrow, color=VIOLET), run_time=2.8)
        self.wait(1.7)

        self.play(
            FadeOut(VGroup(step3[0], step3[1], step3[2], step3[4]), shift=UP * 0.10),
            ReplacementTransform(step3[3], step4[1]),
            FadeIn(step4[0], shift=UP * 0.06),
            FadeIn(VGroup(step4[2], step4[3]), shift=UP * 0.06),
            run_time=0.9,
        )
        self.play(Indicate(p_label, color=AMBER), Indicate(ray_normal_label, color=VIOLET), run_time=2.6)
        self.wait(5.2)

        self.play(
            FadeOut(VGroup(step4[0], step4[1], step4[3]), shift=UP * 0.10),
            ReplacementTransform(step4[2], step5[1]),
            FadeIn(step5[0], shift=UP * 0.06),
            FadeIn(VGroup(step5[2], step5[3]), shift=UP * 0.06),
            run_time=0.9,
        )
        self.play(Indicate(line_formula, color=BLUE), run_time=2.8)
        self.wait(3.8)

        self.play(
            FadeOut(VGroup(step5[0], step5[1], step5[3]), shift=UP * 0.10),
            ReplacementTransform(step5[2], step6[1]),
            FadeIn(VGroup(step6[0], step6[2], step6[3], step6[4]), shift=UP * 0.06),
            FadeIn(nearby),
            run_time=1.1,
        )
        self.play(nearby.animate.set_stroke(opacity=0.52), Indicate(f_label, color=BLUE), run_time=2.8)
        self.wait(6.8)
        finish_to(self, TARGET_DURATIONS["RayLineEquation"])


class RayFamilyEnvelope(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("很多反射光线一起叠", "心形不是一条光线，而是一条边界")
        center = LEFT * 1.55 + DOWN * 0.18
        radius = 2.35
        cup = cup_circle(center, radius)
        ts = np.linspace(-PI / 2 + 0.10, PI / 2 - 0.10, 34)
        incoming = VGroup(
            *[
                incoming_ray(p_on_cup(t, center, radius)[1], center=center, radius=radius, opacity=0.18)
                for t in ts[::3]
            ]
        )
        reflected = reflected_family(ts, center, radius, opacity=0.23)
        caustic_glow = caustic_curve(center, radius, width=28).set_stroke(color=AMBER, opacity=0.16)
        caustic = caustic_curve(center, radius, width=8)

        tracker = ValueTracker(-PI / 2 + 0.25)
        def current_incoming_ray() -> Line:
            return incoming_ray(
                p_on_cup(tracker.get_value(), center, radius)[1],
                center=center,
                radius=radius,
                color=MINT,
                opacity=0.95,
            ).set_stroke(width=5)

        def current_reflected_ray() -> Line:
            return reflected_segment(tracker.get_value(), center, radius, AMBER, 5, 0.95)

        moving_point = Dot(color=AMBER, radius=0.075)
        moving_point.add_updater(lambda mob: mob.move_to(p_on_cup(tracker.get_value(), center, radius)))
        moving_incoming = current_incoming_ray()
        moving_incoming.add_updater(lambda mob: mob.become(current_incoming_ray()))
        moving_incoming_arrow = ray_direction_cue(
            current_incoming_ray(), MINT, proportion=0.72, length=0.50, width=5, opacity=0.98
        )
        moving_incoming_arrow.add_updater(
            lambda mob: mob.become(
                ray_direction_cue(current_incoming_ray(), MINT, proportion=0.72, length=0.50, width=5, opacity=0.98)
            )
        )
        moving_ray = current_reflected_ray()
        moving_ray.add_updater(lambda mob: mob.become(current_reflected_ray()))
        moving_ray_arrow = ray_direction_cue(
            current_reflected_ray(), AMBER, proportion=0.56, length=0.52, width=5, opacity=0.98
        )
        moving_ray_arrow.add_updater(
            lambda mob: mob.become(
                ray_direction_cue(current_reflected_ray(), AMBER, proportion=0.56, length=0.52, width=5, opacity=0.98)
            )
        )
        incoming_label = cn("当前入射光线", 0.24, MINT).next_to(cup, LEFT, buff=0.34).shift(UP * 0.95)
        incoming_label.add_updater(
            lambda mob: mob.next_to(
                incoming_ray(
                    p_on_cup(tracker.get_value(), center, radius)[1],
                    center=center,
                    radius=radius,
                    color=MINT,
                    opacity=0.0,
                ),
                UP,
                buff=0.08,
            ).align_to(cup, LEFT)
        )
        edge_label = label_box("最密的边界：焦散曲线", AMBER).to_edge(RIGHT, buff=0.76).shift(DOWN * 1.75)

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.7)
        self.play(Create(cup), FadeIn(incoming), run_time=1.0)
        self.add(moving_incoming, moving_incoming_arrow, moving_ray, moving_ray_arrow, moving_point, incoming_label)
        self.play(tracker.animate.set_value(PI / 2 - 0.25), run_time=4.2, rate_func=smooth)
        self.play(FadeOut(incoming_label), run_time=0.3)
        self.play(LaggedStart(*[Create(line) for line in reflected], lag_ratio=0.018), run_time=3.6)
        self.play(FadeIn(caustic_glow), Create(caustic), FadeIn(edge_label, shift=UP * 0.12), run_time=2.1)
        moving_incoming.clear_updaters()
        moving_incoming_arrow.clear_updaters()
        moving_ray.clear_updaters()
        moving_ray_arrow.clear_updaters()
        moving_point.clear_updaters()
        finish_to(self, TARGET_DURATIONS["RayFamilyEnvelope"])


class EnvelopeCondition(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("这条亮边界怎么找", "找一族光线共同擦过的位置")
        center = LEFT * 3.15 + DOWN * 0.22
        radius = 1.85
        cup = cup_circle(center, radius)
        axes_group = coordinate_axes(center, 2.25, 2.35, 2.08, 2.22, opacity=0.70)
        t0 = 0.76
        ray_a = reflected_segment(t0 - 0.05, center, radius, BLUE, 4, 0.70)
        ray_b = reflected_segment(t0 + 0.05, center, radius, MINT, 4, 0.70)
        ray_a_arrow = ray_direction_cue(ray_a, BLUE, proportion=0.53, length=0.42, width=4, opacity=0.78)
        ray_b_arrow = ray_direction_cue(ray_b, MINT, proportion=0.59, length=0.42, width=4, opacity=0.78)
        touch = Dot(caustic_point(t0, center, radius), color=AMBER, radius=0.085)
        touch_label = MathTex(r"Q", color=AMBER).scale(0.55).next_to(touch, DOWN, buff=0.07)
        family = reflected_family(np.linspace(-PI / 2 + 0.25, PI / 2 - 0.25, 18), center, radius, opacity=0.13)
        curve = caustic_curve(center, radius, start=-PI / 2 + 0.08, end=PI / 2 - 0.08, width=7)

        panel = formula_panel(6.05, 5.75).to_edge(RIGHT, buff=0.30).shift(DOWN * 0.12)
        line_title = cn("包络点的两个条件", PANEL_TITLE_SIZE, MUTED)
        f_line = MathTex(r"F(x,y,\theta)=0", color=INK).scale(PANEL_FORMULA_LARGE_SIZE)
        expanded = MathTex(r"x\sin(2\theta)-y\cos(2\theta)=R\sin\theta", color=BLUE).scale(PANEL_FORMULA_SIZE)
        fixed_title = cn("固定候选亮点 Q=(x,y)，只让 θ 变", PANEL_BODY_SIZE, ROSE)
        cond1 = MathTex(r"F(x,y,\theta)=0", color=AMBER).scale(PANEL_FORMULA_SIZE)
        cond1_note = cn("Q 在某条反射光线上", PANEL_BODY_SIZE, MUTED).next_to(cond1, RIGHT, buff=0.18)
        cond1_row = VGroup(cond1, cond1_note)
        cond2 = MathTex(r"\frac{\partial F}{\partial \theta}(x,y,\theta)=0", color=AMBER).scale(PANEL_FORMULA_SIZE)
        cond2_note = cn("邻近光线也贴着 Q", PANEL_BODY_SIZE, MUTED).next_to(cond2, RIGHT, buff=0.18)
        cond2_row = VGroup(cond2, cond2_note)
        footer = cn("偏导含义：x、y 不动，只看这族光线随 θ 怎么扫过 Q。", PANEL_NOTE_SIZE, MUTED)
        formula_stack = VGroup(
            line_title,
            f_line,
            expanded,
            fixed_title,
            cond1_row,
            cond2_row,
            footer,
        ).arrange(DOWN, buff=0.13, aligned_edge=LEFT)
        fit_inside(formula_stack, max_width=5.15, max_height=4.98)
        formula_stack.move_to(panel.get_center())

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.7)
        self.play(Create(axes_group), Create(cup), FadeIn(family), run_time=1.4)
        self.play(Create(ray_a), Create(ray_b), Create(ray_a_arrow), Create(ray_b_arrow), FadeIn(touch), FadeIn(touch_label), run_time=2.0)
        self.play(Create(curve), run_time=1.8)
        self.play(FadeIn(panel), FadeIn(line_title), FadeIn(f_line), run_time=1.6)
        self.play(Write(expanded), run_time=1.8)
        self.play(FadeIn(fixed_title), run_time=1.4)
        self.play(FadeIn(cond1_row), run_time=1.4)
        self.play(FadeIn(cond2_row), FadeIn(footer), run_time=1.8)
        finish_to(self, TARGET_DURATIONS["EnvelopeCondition"])


class NephroidPayoff(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("解出来是一条肾形线", "理想圆杯里，焦散曲线有明确形状")
        center = LEFT * 2.8 + DOWN * 0.05
        radius = 2.05
        cup = cup_circle(center, radius)
        cartesian_axes = coordinate_axes(center, 2.42, 2.55, 2.32, 2.42, opacity=0.68)
        full_curve = caustic_curve(center, radius, start=0, end=TAU, width=8)
        glow = caustic_curve(center, radius, start=0, end=TAU, width=25).set_stroke(color=AMBER, opacity=0.15)
        cusp_a = Dot(caustic_point(0, center, radius), color=ROSE, radius=0.08)
        cusp_b = Dot(caustic_point(PI, center, radius), color=ROSE, radius=0.08)
        cusp_labels = VGroup(
            cn("尖点", 0.25, ROSE).next_to(cusp_a, RIGHT, buff=0.10),
            cn("尖点", 0.25, ROSE).next_to(cusp_b, LEFT, buff=0.10),
        )
        o_dot = Dot(center, color=BLUE, radius=0.055)
        o_label = MathTex("O", color=BLUE).scale(0.50).next_to(o_dot, DL, buff=0.05)
        polar_axis = Line(center, center + RIGHT * 1.05, color=VIOLET, stroke_width=3, stroke_opacity=0.65)
        polar_axis_label = cn("极轴", 0.21, VIOLET).next_to(polar_axis, DOWN, buff=0.05)
        polar_tracker = ValueTracker(0.0)

        def polar_current_point() -> np.ndarray:
            return caustic_point(polar_tracker.get_value() % TAU, center, radius)

        def polar_current_theta() -> float:
            point = polar_current_point() - center
            angle = float(np.arctan2(point[1], point[0]))
            if polar_tracker.get_value() > PI and angle <= 0:
                angle += TAU
            return min(max(angle, 0.01), TAU)

        def rho_label_position() -> np.ndarray:
            vector = polar_current_point() - center
            length = max(np.linalg.norm(vector), 0.001)
            direction = vector / length
            normal = rotate_vector(direction, PI / 2)
            return center + vector * 0.52 + normal * 0.15

        def theta_label_position() -> np.ndarray:
            angle = polar_current_theta()
            label_angle = angle - 0.34 if angle > PI else max(angle * 0.55, 0.32)
            return center + 0.62 * np.array([np.cos(label_angle), np.sin(label_angle), 0.0])

        polar_marker = always_redraw(lambda: Dot(polar_current_point(), color=BLUE, radius=0.065))
        polar_ray = always_redraw(lambda: Line(center, polar_current_point(), color=BLUE, stroke_width=3))
        rho_label = MathTex(r"\rho", color=BLUE).scale(0.50)
        rho_label.add_updater(lambda mob: mob.move_to(rho_label_position()))
        theta_arc = always_redraw(
            lambda: Arc(
                radius=0.45,
                start_angle=0,
                angle=polar_current_theta(),
                arc_center=center,
                color=VIOLET,
                stroke_width=4,
            )
        )
        theta_label = MathTex(r"\theta", color=VIOLET).scale(0.48)
        theta_label.add_updater(lambda mob: mob.move_to(theta_label_position()))
        polar_geometry = VGroup(
            o_dot,
            o_label,
            polar_axis,
            polar_axis_label,
            polar_ray,
            rho_label,
            theta_arc,
            theta_label,
            polar_marker,
        ).set_z_index(4)

        panel = formula_panel(5.7, 4.8).to_edge(RIGHT, buff=0.42).shift(DOWN * 0.12)
        solve_title = cn("联立求 x、y", PANEL_TITLE_SIZE, MUTED)
        system_eq = MathTex(
            r"\begin{cases}"
            r"x\sin 2\theta-y\cos 2\theta=R\sin\theta\\"
            r"2x\cos 2\theta+2y\sin 2\theta=R\cos\theta"
            r"\end{cases}",
            color=INK,
        ).scale(PANEL_FORMULA_SMALL_SIZE)
        unknown_note = cn("未知量：x、y；参数：R、θ", PANEL_NOTE_SIZE, MUTED)
        solve_stack = VGroup(
            solve_title,
            system_eq,
            unknown_note,
        ).arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        fit_inside(solve_stack, max_width=4.85)
        solve_stack.move_to(panel.get_center())

        middle_title = cn("先解出中间坐标", PANEL_TITLE_SIZE, MUTED)
        middle_eq = MathTex(
            r"\begin{cases}"
            r"x=R\sin\theta\sin 2\theta+\frac{R}{2}\cos\theta\cos 2\theta\\"
            r"y=-R\sin\theta\cos 2\theta+\frac{R}{2}\cos\theta\sin 2\theta"
            r"\end{cases}",
            color=INK,
        ).scale(0.39)
        simplify_note = cn("再用二倍角公式化简。", PANEL_NOTE_SIZE, MUTED)
        middle_stack = VGroup(
            middle_title,
            middle_eq,
            simplify_note,
        ).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        fit_inside(middle_stack, max_width=5.05)
        middle_stack.move_to(panel.get_center())

        param_title = cn("参数式", PANEL_TITLE_SIZE, MUTED).move_to(panel.get_top() + DOWN * 0.48)
        eq1 = MathTex(r"x=R\left(\frac{3}{2}\cos\theta-\cos^3\theta\right)", color=INK).scale(PANEL_FORMULA_LARGE_SIZE)
        eq2 = MathTex(r"y=R\sin^3\theta", color=INK).scale(PANEL_FORMULA_LARGE_SIZE)
        eqs = VGroup(eq1, eq2).arrange(DOWN, buff=0.28, aligned_edge=LEFT).next_to(param_title, DOWN, buff=0.28)
        name = cn("nephroid / 肾形线", PANEL_TITLE_SIZE, AMBER).next_to(eqs, DOWN, buff=0.42).align_to(eqs, LEFT)
        note = cn("名字不像心形，画出来却一眼能认。", PANEL_NOTE_SIZE, MUTED).next_to(name, DOWN, buff=0.20).align_to(name, LEFT)
        param_group = VGroup(param_title, eqs, name, note)

        rolling_title = cn("滚圆生成", PANEL_TITLE_SIZE, MUTED)
        rolling_eq_big = MathTex(r"r_{\mathrm{big}}=\frac{R}{2}", color=VIOLET).scale(PANEL_FORMULA_SIZE)
        rolling_eq_small = MathTex(r"r_{\mathrm{small}}=\frac{R}{4}", color=MINT).scale(PANEL_FORMULA_SIZE)
        rolling_note = cn("小圆上一点扫出同一条肾形线", PANEL_NOTE_SIZE, AMBER)
        rolling_same_note = cn("同一条曲线的另一种生成方式", PANEL_NOTE_SIZE, MUTED)
        rolling_stack = VGroup(
            rolling_title,
            rolling_eq_big,
            rolling_eq_small,
            rolling_note,
            rolling_same_note,
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        fit_inside(rolling_stack, max_width=4.55, max_height=3.65)
        rolling_stack.move_to(panel.get_center())

        helper_circle = Circle(
            radius=radius / 2,
            color=VIOLET,
            stroke_width=3,
            stroke_opacity=0.48,
        ).move_to(center)
        helper_label = cn("辅助大圆 R/2", 0.22, VIOLET).next_to(helper_circle, DL, buff=0.05)
        rolling_tracker = ValueTracker(0)
        rolling_circle = always_redraw(
            lambda: Circle(
                radius=radius / 4,
                color=MINT,
                stroke_width=3,
                stroke_opacity=0.78,
            ).move_to(rolling_center_point(rolling_tracker.get_value(), center, radius))
        )
        rolling_spoke = always_redraw(
            lambda: Line(
                rolling_center_point(rolling_tracker.get_value(), center, radius),
                rolling_trace_point(rolling_tracker.get_value(), center, radius),
                color=MINT,
                stroke_width=3,
            )
        )
        rolling_dot = always_redraw(
            lambda: Dot(
                rolling_trace_point(rolling_tracker.get_value(), center, radius),
                color=ROSE,
                radius=0.07,
            )
        )
        rolling_center_dot = always_redraw(
            lambda: Dot(
                rolling_center_point(rolling_tracker.get_value(), center, radius),
                color=MINT,
                radius=0.04,
            )
        )
        rolling_trace = always_redraw(
            lambda: ParametricFunction(
                lambda u: rolling_trace_point(u, center, radius),
                t_range=[0, max(rolling_tracker.get_value(), 0.02)],
                color=MINT,
                stroke_width=6,
            )
        )
        rolling_label = cn("滚动小圆 R/4", 0.22, MINT).move_to(center + RIGHT * 1.95 + UP * 1.25)
        polar_title = cn("极坐标式", PANEL_TITLE_SIZE, MUTED)
        polar_context = cn("以 O 为极点，向右为极轴", PANEL_BODY_SIZE, MUTED)
        polar_eq = MathTex(
            r"\left(\rho^2-\frac{R^2}{4}\right)^3=\frac{27R^4}{64}\rho^2\sin^2\theta",
            color=BLUE,
        ).scale(PANEL_FORMULA_SMALL_SIZE)
        rho_row = VGroup(
            MathTex(r"\rho", color=BLUE).scale(PANEL_FORMULA_SIZE),
            cn("：到圆心 O 的距离", PANEL_BODY_SIZE, MUTED),
        ).arrange(RIGHT, buff=0.06)
        theta_row = VGroup(
            MathTex(r"\theta", color=VIOLET).scale(PANEL_FORMULA_SIZE),
            cn("：从极轴量起的方向角", PANEL_BODY_SIZE, MUTED),
        ).arrange(RIGHT, buff=0.06)
        same_curve_note = cn("这只是同一条曲线的另一种写法。", PANEL_NOTE_SIZE, AMBER)
        polar_stack = VGroup(
            polar_title,
            polar_context,
            polar_eq,
            rho_row,
            theta_row,
            same_curve_note,
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        fit_inside(polar_stack, max_width=4.95)
        polar_stack.move_to(panel.get_center())

        def wait_until(local_time: float) -> None:
            if self.time < local_time:
                self.wait(local_time - self.time)

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.7)
        self.play(Create(cartesian_axes), Create(cup), run_time=0.8)
        self.play(FadeIn(panel), FadeIn(solve_stack), run_time=1.6)
        wait_until(13.6)
        self.play(FadeOut(solve_stack, shift=UP * 0.08), FadeIn(middle_stack, shift=UP * 0.08), run_time=1.4)
        wait_until(22.6)
        self.play(FadeOut(middle_stack, shift=UP * 0.08), FadeIn(param_title), Write(eq1), Write(eq2), run_time=1.7)
        self.play(FadeIn(glow), Create(full_curve), run_time=2.8)
        self.play(FadeIn(cusp_a), FadeIn(cusp_b), FadeIn(cusp_labels), FadeIn(name), FadeIn(note), run_time=1.1)
        wait_until(33.6)
        self.play(FadeOut(param_group, shift=UP * 0.08), FadeIn(rolling_stack, shift=UP * 0.08), run_time=1.2)
        self.play(Create(helper_circle), FadeIn(helper_label), run_time=0.8)
        wait_until(39.2)
        self.add(rolling_trace, rolling_circle, rolling_spoke, rolling_center_dot, rolling_dot)
        self.play(FadeIn(rolling_label), rolling_tracker.animate.set_value(TAU), run_time=11.2, rate_func=linear)
        wait_until(53.9)
        self.play(
            FadeOut(rolling_circle),
            FadeOut(rolling_spoke),
            FadeOut(rolling_center_dot),
            FadeOut(rolling_dot),
            FadeOut(rolling_label),
            FadeOut(helper_label),
            run_time=0.7,
        )
        wait_until(55.8)
        self.play(Create(polar_geometry), run_time=1.2)
        self.play(
            FadeOut(rolling_stack, shift=UP * 0.08),
            FadeOut(helper_circle),
            FadeOut(rolling_trace),
            FadeIn(polar_stack, shift=UP * 0.08),
            run_time=1.4,
        )
        self.play(polar_tracker.animate.set_value(TAU), run_time=8.0, rate_func=linear)
        finish_to(self, TARGET_DURATIONS["NephroidPayoff"])


class RealityEcho(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("真实杯子会把它拉歪", "但核心机制没有变")
        centers = [LEFT * 4.0 + DOWN * 0.15, ORIGIN + DOWN * 0.15, RIGHT * 4.0 + DOWN * 0.15]
        labels = ["圆杯模型", "斜进来的光", "粗糙杯壁"]
        groups = VGroup()
        for idx, center in enumerate(centers):
            cup = cup_circle(center, 1.35, opacity=0.88)
            curve = caustic_curve(center, 1.35, width=6)
            if idx == 1:
                curve.stretch(0.82, dim=0).rotate(0.20, about_point=center).shift(RIGHT * 0.12 + DOWN * 0.06)
            if idx == 2:
                curve.set_stroke(width=13, opacity=0.18)
                second = caustic_curve(center + RIGHT * 0.04 + UP * 0.02, 1.30, width=7).set_stroke(color=AMBER, opacity=0.42)
                curve = VGroup(curve, second)
            label = cn(labels[idx], 0.30, MUTED).next_to(cup, DOWN, buff=0.28)
            groups.add(VGroup(cup, curve, label))

        flow = VGroup(
            label_box("反射", MINT),
            MathTex(r"\rightarrow", color=MUTED).scale(0.62),
            label_box("一族线", BLUE),
            MathTex(r"\rightarrow", color=MUTED).scale(0.62),
            label_box("包络线", AMBER),
            MathTex(r"\rightarrow", color=MUTED).scale(0.62),
            label_box("焦散曲线", AMBER),
        ).arrange(RIGHT, buff=0.18).to_edge(DOWN, buff=0.55)

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(group, shift=UP * 0.12) for group in groups], lag_ratio=0.18), run_time=1.8)
        self.play(FadeIn(flow, shift=UP * 0.14), run_time=1.2)
        self.play(groups[0][1].animate.set_stroke(color=AMBER, width=9), run_time=0.8)
        finish_to(self, TARGET_DURATIONS["RealityEcho"])
