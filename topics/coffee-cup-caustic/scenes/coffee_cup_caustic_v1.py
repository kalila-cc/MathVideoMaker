from __future__ import annotations

import re
from typing import Iterable

import numpy as np
from manim import *


FONT = "Microsoft YaHei"
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

LATIN_PATTERN = re.compile(r"[A-Za-z0-9_.:/,+#()-]+")

TIMES_TEX_TEMPLATE = TexTemplate()
TIMES_TEX_TEMPLATE.add_to_preamble(r"\usepackage{mathptmx}")
MathTex.set_default(tex_template=TIMES_TEX_TEMPLATE)

TARGET_DURATIONS = {
    "StoryHook": 11.56,
    "ReflectionModel": 16.20,
    "RayFamilyEnvelope": 15.58,
    "EnvelopeCondition": 18.47,
    "NephroidPayoff": 12.07,
    "RealityEcho": 15.52,
}


def latin_font_map(text: str) -> dict[str, str]:
    return {token: LATIN_FONT for token in LATIN_PATTERN.findall(text)}


def cn(text: str, size: float = 0.36, color: str = INK) -> Text:
    return Text(text, font=FONT, t2f=latin_font_map(text), color=color).scale(size)


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
    x_hit = center[0] - np.sqrt(max(radius * radius - (y - center[1]) ** 2, 0.0))
    return Line(
        np.array([center[0] - radius - 2.0, y, 0.0]),
        np.array([x_hit, y, 0.0]),
        color=color,
        stroke_width=3,
        stroke_opacity=opacity,
    )


def caustic_point(t: float, center: np.ndarray = ORIGIN, radius: float = 2.35) -> np.ndarray:
    return center + radius * np.array(
        [1.5 * np.cos(t) - np.cos(t) ** 3, np.sin(t) ** 3, 0.0]
    )


def caustic_curve(
    center: np.ndarray = ORIGIN,
    radius: float = 2.35,
    start: float = PI / 2,
    end: float = 3 * PI / 2,
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


class CoverFrame(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = cn("杯子里的", 0.82)
        title2 = cn("心形光斑", 0.98, AMBER)
        title_group = VGroup(title, title2).arrange(DOWN, buff=0.04, aligned_edge=LEFT)
        title_group.scale_to_fit_width(5.45).to_corner(UL, buff=0.55)

        center = RIGHT * 2.35 + DOWN * 0.10
        cup = cup_circle(center, 2.05)
        rays = VGroup(
            *[
                incoming_ray(y, center=center, radius=2.05, opacity=0.34)
                for y in np.linspace(center[1] - 1.65, center[1] + 1.65, 9)
            ]
        )
        reflected = reflected_family(np.linspace(PI / 2 + 0.13, 3 * PI / 2 - 0.13, 26), center, 2.05, opacity=0.20)
        glow = caustic_curve(center, 2.05, width=25).set_stroke(color=AMBER, opacity=0.16)
        curve = caustic_curve(center, 2.05, width=10)
        subtitle = cn("平行光反射后，擦出一条焦散线", 0.33, MUTED)
        subtitle.next_to(title_group, DOWN, buff=0.34).align_to(title_group, LEFT)

        self.add(rays, cup, reflected, glow, curve, title_group, subtitle)
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
        reflected = reflected_family(np.linspace(PI / 2 + 0.12, 3 * PI / 2 - 0.12, 25), center, 2.35, opacity=0.0)
        glow = caustic_curve(center, 2.35, width=24).set_stroke(color=AMBER, opacity=0.0)
        glow.set_fill(opacity=0)
        curve = caustic_curve(center, 2.35, width=8).set_stroke(color=AMBER, opacity=0.0)
        curve.set_fill(opacity=0)
        note = cn("亮线来自反射光线的叠加", 0.34, AMBER).to_edge(RIGHT, buff=0.88).shift(DOWN * 1.8)

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)
        self.play(Create(cup), run_time=1.2)
        self.play(rays.animate.set_opacity(0.40), run_time=1.6)
        self.play(reflected.animate.set_opacity(0.20), run_time=2.2)
        self.play(glow.animate.set_stroke(opacity=0.16), curve.animate.set_stroke(opacity=1.0), run_time=2.4)
        self.play(FadeIn(note, shift=UP * 0.12), run_time=0.8)
        finish_to(self, TARGET_DURATIONS["StoryHook"])


class ReflectionModel(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("把杯口看成一个圆", "保留圆形杯壁和平行阳光")
        center = LEFT * 2.2 + DOWN * 0.15
        radius = 2.35
        cup = cup_circle(center, radius)
        t = 2.28
        point = p_on_cup(t, center, radius)
        normal = Line(center, point, color=ROSE, stroke_width=4)
        tangent_direction = np.array([-np.sin(t), np.cos(t), 0.0])
        tangent = Line(point - tangent_direction * 0.82, point + tangent_direction * 0.82, color=VIOLET, stroke_width=3)
        incoming = incoming_ray(point[1], center=center, radius=radius, opacity=0.72)
        reflected = reflected_segment(t, center=center, radius=radius, color=AMBER, width=5, opacity=0.95)
        hit_dot = Dot(point, color=AMBER, radius=0.08)
        p_label = MathTex(r"P(\theta)", color=AMBER).scale(0.58).next_to(hit_dot, UL, buff=0.08)
        normal_label = cn("法线", 0.28, ROSE).next_to(normal, DOWN, buff=0.08)
        incoming_label = cn("入射光", 0.28, MINT).next_to(incoming, UP, buff=0.08)
        reflected_label = cn("反射光", 0.28, AMBER).next_to(reflected, DOWN, buff=0.08)

        rule1 = label_box("圆形杯壁", BLUE).to_edge(RIGHT, buff=1.12).shift(UP * 0.85)
        rule2 = label_box("入射角 = 反射角", AMBER).next_to(rule1, DOWN, buff=0.26).align_to(rule1, LEFT)
        rule3 = cn("这两个规则，就足够生成那条亮线。", 0.31, MUTED).next_to(rule2, DOWN, buff=0.42).align_to(rule1, LEFT)

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.7)
        self.play(Create(cup), run_time=0.9)
        self.play(Create(incoming), FadeIn(incoming_label), run_time=1.0)
        self.play(FadeIn(hit_dot), FadeIn(p_label), Create(normal), Create(tangent), FadeIn(normal_label), run_time=1.2)
        self.play(Create(reflected), FadeIn(reflected_label), run_time=1.1)
        self.play(FadeIn(rule1, shift=LEFT * 0.12), FadeIn(rule2, shift=LEFT * 0.12), run_time=0.9)
        self.play(FadeIn(rule3, shift=UP * 0.10), run_time=0.8)
        finish_to(self, TARGET_DURATIONS["ReflectionModel"])


class RayFamilyEnvelope(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("很多反射光线一起叠", "心形不是一条光线，而是一条边界")
        center = LEFT * 1.55 + DOWN * 0.18
        radius = 2.35
        cup = cup_circle(center, radius)
        ts = np.linspace(PI / 2 + 0.10, 3 * PI / 2 - 0.10, 34)
        incoming = VGroup(
            *[
                incoming_ray(p_on_cup(t, center, radius)[1], center=center, radius=radius, opacity=0.30)
                for t in ts[::3]
            ]
        )
        reflected = reflected_family(ts, center, radius, opacity=0.23)
        caustic_glow = caustic_curve(center, radius, width=28).set_stroke(color=AMBER, opacity=0.16)
        caustic = caustic_curve(center, radius, width=8)

        tracker = ValueTracker(PI / 2 + 0.25)
        moving_point = Dot(color=AMBER, radius=0.075)
        moving_point.add_updater(lambda mob: mob.move_to(p_on_cup(tracker.get_value(), center, radius)))
        moving_ray = reflected_segment(tracker.get_value(), center, radius, AMBER, 5, 0.95)
        moving_ray.add_updater(
            lambda mob: mob.become(reflected_segment(tracker.get_value(), center, radius, AMBER, 5, 0.95))
        )
        edge_label = label_box("最密的边界：焦散线", AMBER).to_edge(RIGHT, buff=0.76).shift(DOWN * 1.75)

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.7)
        self.play(Create(cup), FadeIn(incoming), run_time=1.0)
        self.add(moving_ray, moving_point)
        self.play(tracker.animate.set_value(3 * PI / 2 - 0.25), run_time=4.2, rate_func=smooth)
        self.play(LaggedStart(*[Create(line) for line in reflected], lag_ratio=0.018), run_time=3.6)
        self.play(FadeIn(caustic_glow), Create(caustic), FadeIn(edge_label, shift=UP * 0.12), run_time=2.1)
        moving_ray.clear_updaters()
        moving_point.clear_updaters()
        finish_to(self, TARGET_DURATIONS["RayFamilyEnvelope"])


class EnvelopeCondition(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("这条亮边界怎么找", "找一族光线共同擦过的位置")
        center = LEFT * 3.15 + DOWN * 0.22
        radius = 1.85
        cup = cup_circle(center, radius)
        t0 = 2.83
        ray_a = reflected_segment(t0 - 0.05, center, radius, BLUE, 4, 0.70)
        ray_b = reflected_segment(t0 + 0.05, center, radius, MINT, 4, 0.70)
        touch = Dot(caustic_point(t0, center, radius), color=AMBER, radius=0.085)
        touch_label = MathTex(r"Q", color=AMBER).scale(0.55).next_to(touch, DOWN, buff=0.07)
        family = reflected_family(np.linspace(PI / 2 + 0.25, 3 * PI / 2 - 0.25, 18), center, radius, opacity=0.13)
        curve = caustic_curve(center, radius, start=PI / 2 + 0.08, end=3 * PI / 2 - 0.08, width=7)

        panel = formula_panel(5.9, 5.6).to_edge(RIGHT, buff=0.34).shift(DOWN * 0.15)
        line_title = cn("反射光线写成一族方程", 0.30, MUTED).move_to(panel.get_top() + DOWN * 0.45)
        f_line = MathTex(r"F(x,y,\theta)=0", color=INK).scale(0.72).next_to(line_title, DOWN, buff=0.26)
        expanded = MathTex(r"x\sin(2\theta)-y\cos(2\theta)=R\sin\theta", color=BLUE).scale(0.55)
        expanded.next_to(f_line, DOWN, buff=0.28)
        cond_title = cn("亮边界上的点 Q 同时满足", 0.30, MUTED).next_to(expanded, DOWN, buff=0.48)
        cond1 = MathTex(r"F(x,y,\theta)=0", color=AMBER).scale(0.62).next_to(cond_title, DOWN, buff=0.20)
        cond1_note = cn("在某条反射光线上", 0.26, MUTED).next_to(cond1, RIGHT, buff=0.22)
        cond2 = MathTex(r"\frac{\partial F}{\partial\theta}(x,y,\theta)=0", color=AMBER).scale(0.62)
        cond2.next_to(cond1, DOWN, buff=0.23).align_to(cond1, LEFT)
        cond2_note = cn("旁边光线也擦过它", 0.26, MUTED).next_to(cond2, RIGHT, buff=0.22)
        footer = cn("求导时，屏幕上的 x 和 y 先固定不动。", 0.27, ROSE)
        footer.next_to(cond2, DOWN, buff=0.36).align_to(cond1, LEFT)

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.7)
        self.play(Create(cup), FadeIn(family), run_time=1.0)
        self.play(Create(ray_a), Create(ray_b), FadeIn(touch), FadeIn(touch_label), run_time=1.3)
        self.play(Create(curve), run_time=1.2)
        self.play(FadeIn(panel), FadeIn(line_title), FadeIn(f_line), run_time=0.9)
        self.play(Write(expanded), run_time=1.1)
        self.play(FadeIn(cond_title), FadeIn(cond1), FadeIn(cond1_note), run_time=0.9)
        self.play(FadeIn(cond2), FadeIn(cond2_note), FadeIn(footer), run_time=1.1)
        finish_to(self, TARGET_DURATIONS["EnvelopeCondition"])


class NephroidPayoff(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("解出来是一条肾形线", "理想圆杯里，焦散线有明确形状")
        center = LEFT * 2.8 + DOWN * 0.05
        radius = 2.05
        cup = cup_circle(center, radius)
        full_curve = caustic_curve(center, radius, start=0, end=TAU, width=8)
        glow = caustic_curve(center, radius, start=0, end=TAU, width=25).set_stroke(color=AMBER, opacity=0.15)
        cusp_a = Dot(caustic_point(0, center, radius), color=ROSE, radius=0.08)
        cusp_b = Dot(caustic_point(PI, center, radius), color=ROSE, radius=0.08)
        cusp_labels = VGroup(
            cn("尖点", 0.25, ROSE).next_to(cusp_a, RIGHT, buff=0.10),
            cn("尖点", 0.25, ROSE).next_to(cusp_b, LEFT, buff=0.10),
        )

        panel = formula_panel(5.7, 4.8).to_edge(RIGHT, buff=0.42).shift(DOWN * 0.12)
        param_title = cn("参数式", 0.31, MUTED).move_to(panel.get_top() + DOWN * 0.48)
        eq1 = MathTex(r"x=R\left(\frac{3}{2}\cos\theta-\cos^3\theta\right)", color=INK).scale(0.56)
        eq2 = MathTex(r"y=R\sin^3\theta", color=INK).scale(0.62)
        eqs = VGroup(eq1, eq2).arrange(DOWN, buff=0.28, aligned_edge=LEFT).next_to(param_title, DOWN, buff=0.28)
        name = cn("nephroid / 肾形线", 0.38, AMBER).next_to(eqs, DOWN, buff=0.46).align_to(eqs, LEFT)
        note = cn("名字不像心形，画出来却一眼能认。", 0.28, MUTED).next_to(name, DOWN, buff=0.20).align_to(name, LEFT)

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.7)
        self.play(Create(cup), run_time=0.8)
        self.play(FadeIn(panel), FadeIn(param_title), Write(eq1), Write(eq2), run_time=1.6)
        self.play(FadeIn(glow), Create(full_curve), run_time=2.8)
        self.play(FadeIn(cusp_a), FadeIn(cusp_b), FadeIn(cusp_labels), FadeIn(name), FadeIn(note), run_time=1.1)
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
            label_box("焦散线", AMBER),
        ).arrange(RIGHT, buff=0.18).to_edge(DOWN, buff=0.55)

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(group, shift=UP * 0.12) for group in groups], lag_ratio=0.18), run_time=1.8)
        self.play(FadeIn(flow, shift=UP * 0.14), run_time=1.2)
        self.play(groups[0][1].animate.set_stroke(color=AMBER, width=9), run_time=0.8)
        finish_to(self, TARGET_DURATIONS["RealityEcho"])
