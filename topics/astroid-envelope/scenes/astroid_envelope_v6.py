from __future__ import annotations

import re
import numpy as np
from manim import *


FONT = "Microsoft YaHei"
LATIN_FONT = "Times New Roman"
BG = "#08111F"
INK = "#F8F4E3"
MUTED = "#A7B0BE"
AMBER = "#F6B73C"
MINT = "#5EEAD4"
ROSE = "#FF5C7A"
BLUE = "#7DD3FC"
PANEL = "#0D1727"

LENGTH = 4.4
SCALE = 1.12
ORIGIN = LEFT * 5.35 + DOWN * 2.55

TIMES_TEX_TEMPLATE = TexTemplate()
TIMES_TEX_TEMPLATE.add_to_preamble(r"\usepackage{mathptmx}")
MathTex.set_default(tex_template=TIMES_TEX_TEMPLATE)

LATIN_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[./+-][A-Za-z0-9]+)*")


def p(x: float, y: float) -> np.ndarray:
    return ORIGIN + SCALE * np.array([x, y, 0.0])


def latin_font_map(text: str) -> dict[str, str]:
    return {token: LATIN_FONT for token in LATIN_PATTERN.findall(text)}


def cn(text: str, size: float = 0.36, color: str = INK) -> Text:
    return Text(text, font=FONT, t2f=latin_font_map(text), color=color).scale(size)


def ladder(theta: float, color: str = INK, opacity: float = 1.0, width: float = 7) -> Line:
    return Line(
        p(LENGTH * np.cos(theta), 0),
        p(0, LENGTH * np.sin(theta)),
        color=color,
        stroke_width=width,
        stroke_opacity=opacity,
    )


def corner() -> VGroup:
    floor = Line(p(0, 0), p(LENGTH * 1.08, 0), color=BLUE, stroke_width=5)
    wall = Line(p(0, 0), p(0, LENGTH * 1.08), color=BLUE, stroke_width=5)
    floor_label = cn("地面", 0.32, MUTED).next_to(floor, DOWN)
    wall_label = cn("墙", 0.32, MUTED).next_to(wall, LEFT)
    return VGroup(floor, wall, floor_label, wall_label)


def panel(width: float = 5.9, height: float = 6.2) -> RoundedRectangle:
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.22,
        stroke_color="#314054",
        fill_color=PANEL,
        fill_opacity=0.94,
    ).to_edge(RIGHT, buff=0.28).shift(DOWN * 0.12)


def theta_marker(theta_tracker: ValueTracker) -> VGroup:
    def marker() -> VGroup:
        theta = theta_tracker.get_value()
        center = p(LENGTH * np.cos(theta), 0)
        arc = Arc(
            radius=0.46,
            start_angle=PI,
            angle=-theta,
            arc_center=center,
            color=ROSE,
            stroke_width=4,
        )
        mid = PI - theta / 2
        label = MathTex(r"\theta", color=ROSE).scale(0.55)
        label.move_to(center + 0.68 * np.array([np.cos(mid), np.sin(mid), 0.0]))
        return VGroup(arc, label)

    return always_redraw(marker)


def stick_with_trackers(theta: ValueTracker) -> VGroup:
    stick = always_redraw(lambda: ladder(theta.get_value(), width=8))
    a_dot = always_redraw(lambda: Dot(p(LENGTH * np.cos(theta.get_value()), 0), color=AMBER, radius=0.07))
    b_dot = always_redraw(lambda: Dot(p(0, LENGTH * np.sin(theta.get_value())), color=MINT, radius=0.07))
    a_label = always_redraw(lambda: MathTex(r"A", color=AMBER).scale(0.55).next_to(a_dot, DOWN, buff=0.06))
    b_label = always_redraw(lambda: MathTex(r"B", color=MINT).scale(0.55).next_to(b_dot, LEFT, buff=0.06))
    return VGroup(stick, a_dot, b_dot, a_label, b_label, theta_marker(theta))


def legend_row(math: str, desc: str, color: str = INK) -> VGroup:
    return VGroup(
        MathTex(math, color=color).scale(0.62),
        cn(desc, 0.29, MUTED),
    ).arrange(RIGHT, buff=0.18)


def astroid_point(t: float, center: np.ndarray = LEFT * 3.55 + DOWN * 0.05, radius: float = 2.05) -> np.ndarray:
    return center + radius * np.array([np.cos(t) ** 3, np.sin(t) ** 3, 0.0])


def full_astroid(center: np.ndarray = LEFT * 3.55 + DOWN * 0.05, radius: float = 2.05, width: float = 8) -> ParametricFunction:
    return ParametricFunction(
        lambda t: astroid_point(t, center, radius),
        t_range=[0, TAU],
        color=AMBER,
        stroke_width=width,
    )


def astroid_axes(center: np.ndarray = LEFT * 3.55 + DOWN * 0.05, radius: float = 2.05) -> VGroup:
    x_axis = Line(center + LEFT * (radius + 0.45), center + RIGHT * (radius + 0.45), color=BLUE, stroke_width=3)
    y_axis = Line(center + DOWN * (radius + 0.45), center + UP * (radius + 0.45), color=BLUE, stroke_width=3)
    x_label = MathTex("x", color=BLUE).scale(0.42).next_to(x_axis, RIGHT, buff=0.06)
    y_label = MathTex("y", color=BLUE).scale(0.42).next_to(y_axis, UP, buff=0.06)
    return VGroup(x_axis, y_axis, x_label, y_label)


class CoverFrame(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title_top = cn("一根滑落的棍子", 0.76).to_edge(UP, buff=0.42)
        title_bottom = cn("为什么会画出星形线？", 0.72, AMBER).next_to(title_top, DOWN, buff=0.08)
        subtitle = cn("从墙角里的日常动作，看见一条四尖角的包络线", 0.31, MUTED).next_to(
            title_bottom, DOWN, buff=0.18
        )

        center = LEFT * 3.55 + DOWN * 0.55
        axes = astroid_axes(center=center, radius=1.62).set_opacity(0.72)
        curve = full_astroid(center=center, radius=1.62, width=12)
        glow = full_astroid(center=center, radius=1.62, width=26).set_stroke(color=AMBER, opacity=0.16)
        stars = VGroup(*[Dot(astroid_point(t, center, 1.62), color=AMBER, radius=0.07) for t in [0, PI / 2, PI, 3 * PI / 2]])

        mini_origin = RIGHT * 2.05 + DOWN * 2.05
        floor = Line(mini_origin + LEFT * 0.15, mini_origin + RIGHT * 3.2, color=BLUE, stroke_width=5)
        wall = Line(mini_origin + LEFT * 0.15, mini_origin + LEFT * 0.15 + UP * 3.1, color=BLUE, stroke_width=5)
        stick = Line(mini_origin + RIGHT * 2.55, mini_origin + LEFT * 0.15 + UP * 2.35, color=INK, stroke_width=9)
        traces = VGroup(
            *[
                Line(
                    mini_origin + RIGHT * (2.85 * np.cos(t)),
                    mini_origin + LEFT * 0.15 + UP * (2.85 * np.sin(t)),
                    color=BLUE,
                    stroke_width=2,
                    stroke_opacity=0.16,
                )
                for t in np.linspace(0.25, 1.25, 14)
            ]
        )
        scenario = VGroup(traces, floor, wall, stick)

        formula = MathTex(r"x^{\frac{2}{3}}+y^{\frac{2}{3}}=L^{\frac{2}{3}}", color=AMBER).scale(0.74)
        formula.next_to(scenario, UP, buff=0.35).align_to(scenario, LEFT)
        card = RoundedRectangle(
            width=12.4,
            height=5.25,
            corner_radius=0.32,
            stroke_color="#314054",
            fill_color="#0B1626",
            fill_opacity=0.86,
        ).shift(DOWN * 0.55)

        self.add(card, title_top, title_bottom, subtitle, glow, axes, curve, stars, scenario, formula)
        self.wait(0.65)


class StoryHook(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title = cn("墙角里的一根棍子", 0.56).to_edge(UP)
        question = cn("它慢慢滑落时，外轮廓会是什么形状？", 0.42, AMBER).next_to(title, DOWN, buff=0.18)
        self.play(FadeIn(title, shift=DOWN * 0.18), FadeIn(question, shift=DOWN * 0.18), run_time=1.0)
        self.play(Create(corner()), run_time=0.9)

        theta = ValueTracker(1.35)
        stick_group = stick_with_trackers(theta)
        self.play(FadeIn(stick_group), run_time=0.8)
        self.play(theta.animate.set_value(0.22), run_time=5.0, rate_func=smooth)

        trace_lines = VGroup(*[ladder(t, color=BLUE, opacity=0.14, width=2.4) for t in np.linspace(0.18, 1.36, 34)])
        astroid = ParametricFunction(
            lambda t: p(LENGTH * np.cos(t) ** 3, LENGTH * np.sin(t) ** 3),
            t_range=[0, PI / 2],
            color=AMBER,
            stroke_width=8,
        )
        note = cn("许多瞬间叠在一起，看不见的外轮廓开始显形。", 0.34, MUTED).to_edge(DOWN)
        self.play(FadeIn(note, shift=UP * 0.1), run_time=1.0)
        self.play(LaggedStart(*[Create(line) for line in trace_lines], lag_ratio=0.025), run_time=3.2)
        self.play(Create(astroid), run_time=2.0)
        self.wait(6.25)


class VariablesMatter(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title = cn("给变量找位置", 0.52).to_edge(UP)
        subtitle = cn("先把长度、角度和点的位置看清楚", 0.34, MUTED).next_to(title, DOWN, buff=0.14)
        self.play(FadeIn(title, shift=DOWN * 0.18), FadeIn(subtitle, shift=DOWN * 0.12), run_time=0.8)
        self.play(Create(corner()), run_time=0.8)

        theta = ValueTracker(0.92)
        stick_group = stick_with_trackers(theta)
        self.play(FadeIn(stick_group), run_time=0.8)

        a = LENGTH * np.cos(theta.get_value())
        b = LENGTH * np.sin(theta.get_value())
        point = p(a * 0.55, b * 0.45)
        p_dot = Dot(point, color=ROSE, radius=0.07)
        p_label = MathTex(r"P=(x,y)", color=ROSE).scale(0.58).next_to(p_dot, UR, buff=0.06)
        x_line = DashedLine(p(0, 0), p(a * 0.55, 0), color=AMBER, dash_length=0.08)
        y_line = DashedLine(p(a * 0.55, 0), point, color=MINT, dash_length=0.08)
        x_label = MathTex(r"x", color=AMBER).scale(0.58).next_to(x_line, DOWN, buff=0.06)
        y_label = MathTex(r"y", color=MINT).scale(0.58).next_to(y_line, RIGHT, buff=0.06)

        box = panel(width=5.75, height=5.7)
        box_title = cn("符号和真实量的对应", 0.42).move_to(box.get_top() + DOWN * 0.36)
        rows = VGroup(
            legend_row(r"L", "棍子的固定长度", INK),
            legend_row(r"\theta", "棍子与地面的夹角，在端点 A 处测量", ROSE),
            legend_row(r"a=L\cos\theta", "地面截距：端点 A 到墙的距离", AMBER),
            legend_row(r"b=L\sin\theta", "墙上截距：端点 B 到地面的高度", MINT),
            legend_row(r"P=(x,y)", "棍子上的一个点", ROSE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        rows.next_to(box_title, DOWN, buff=0.38).align_to(box, LEFT).shift(RIGHT * 0.38)

        self.play(FadeIn(box, shift=LEFT * 0.2), FadeIn(box_title))
        self.play(LaggedStart(*[FadeIn(row, shift=UP * 0.08) for row in rows], lag_ratio=0.16), run_time=2.2)
        self.play(Create(x_line), Create(y_line), FadeIn(x_label), FadeIn(y_label), FadeIn(p_dot), FadeIn(p_label), run_time=1.0)
        self.wait(15.35)


class LineEquationNatural(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title = cn("这一瞬间就是一条直线", 0.5).to_edge(UP)
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)
        self.play(Create(corner()), run_time=0.8)

        theta = 0.86
        a = LENGTH * np.cos(theta)
        b = LENGTH * np.sin(theta)
        stick = ladder(theta, width=8)
        a_dot = Dot(p(a, 0), color=AMBER, radius=0.075)
        b_dot = Dot(p(0, b), color=MINT, radius=0.075)
        a_label = MathTex(r"a=L\cos\theta", color=AMBER).scale(0.55).next_to(a_dot, DOWN, buff=0.08)
        b_label = MathTex(r"b=L\sin\theta", color=MINT).scale(0.55).next_to(b_dot, LEFT, buff=0.08)
        self.play(FadeIn(stick), FadeIn(a_dot), FadeIn(b_dot), FadeIn(a_label), FadeIn(b_label), run_time=1.0)

        box = panel(width=6.15, height=6.35)
        box_title = cn("截距式整理成倒数记号", 0.42).move_to(box.get_top() + DOWN * 0.36)
        f1 = MathTex(r"\frac{x}{a}+\frac{y}{b}=1", color=INK).scale(0.86)
        note1 = cn("横向占比 + 纵向占比 = 1", 0.29, MUTED)
        f2 = MathTex(r"a=L\cos\theta,\qquad b=L\sin\theta", color=INK).scale(0.66)
        f3 = MathTex(r"\frac{x}{L\cos\theta}+\frac{y}{L\sin\theta}=1", color=INK).scale(0.7)
        f4 = MathTex(r"x\sec\theta+y\csc\theta=L", color=AMBER).scale(0.82)
        note2 = VGroup(
            MathTex(r"\sec\theta=\frac{1}{\cos\theta}", color=MUTED).scale(0.54),
            MathTex(r"\csc\theta=\frac{1}{\sin\theta}", color=MUTED).scale(0.54),
        ).arrange(RIGHT, buff=0.42)
        stack = VGroup(f1, note1, f2, f3, f4, note2).arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        stack.next_to(box_title, DOWN, buff=0.42).align_to(box, LEFT).shift(RIGHT * 0.42)

        self.play(FadeIn(box, shift=LEFT * 0.2), FadeIn(box_title))
        for item in stack:
            self.play(FadeIn(item, shift=UP * 0.08), run_time=0.95)
        self.wait(1.0)
        self.wait(14.95)


class EnvelopeIdea(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title = cn("外轮廓由相邻棍子一起擦出", 0.48).to_edge(UP)
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)
        self.play(Create(corner()), run_time=0.8)

        trace_lines = VGroup(*[ladder(t, color=BLUE, opacity=0.13, width=2.2) for t in np.linspace(0.18, 1.38, 42)])
        self.play(LaggedStart(*[Create(line) for line in trace_lines], lag_ratio=0.025), run_time=3.1)

        t0 = 0.78
        close_lines = VGroup(
            ladder(t0 - 0.055, color=ROSE, opacity=0.52, width=4),
            ladder(t0, color=INK, opacity=1.0, width=6),
            ladder(t0 + 0.055, color=ROSE, opacity=0.52, width=4),
        )
        touch = Dot(p(LENGTH * np.cos(t0) ** 3, LENGTH * np.sin(t0) ** 3), color=AMBER, radius=0.08)
        touch_label = cn("相邻位置几乎贴着同一个点擦过", 0.31, AMBER).next_to(touch, UR, buff=0.1)
        astroid = ParametricFunction(
            lambda t: p(LENGTH * np.cos(t) ** 3, LENGTH * np.sin(t) ** 3),
            t_range=[0, PI / 2],
            color=AMBER,
            stroke_width=8,
        )
        self.play(FadeIn(close_lines), FadeIn(touch), FadeIn(touch_label), run_time=1.0)
        self.play(Create(astroid), run_time=1.6)

        box = panel(width=6.05, height=5.75)
        box_title = cn("把“擦过边界”翻译成条件", 0.4).move_to(box.get_top() + DOWN * 0.36)
        f = MathTex(r"F(x,y,\theta)=x\sec\theta+y\csc\theta-L", color=INK).scale(0.58)
        c1 = VGroup(MathTex(r"F=0", color=MINT).scale(0.78), cn("点在这根棍子上", 0.28, MUTED)).arrange(RIGHT, buff=0.25)
        c2 = VGroup(MathTex(r"\frac{\partial F}{\partial\theta}=0", color=AMBER).scale(0.78), cn("固定 x、y，只让角度轻轻变化", 0.28, MUTED)).arrange(RIGHT, buff=0.25)
        note = cn("相邻的一小族棍子，共同夹出同一个边界点。", 0.3, AMBER)
        stack = VGroup(f, c1, c2, note).arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        stack.next_to(box_title, DOWN, buff=0.48).align_to(box, LEFT).shift(RIGHT * 0.38)
        self.play(FadeIn(box, shift=LEFT * 0.2), FadeIn(box_title))
        for item in stack:
            self.play(FadeIn(item, shift=UP * 0.08), run_time=0.95)
        self.wait(1.0)
        self.wait(9.85)


class DerivativeStep(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title = cn("固定这个点，只让角度变化", 0.5).to_edge(UP)
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)
        self.play(Create(corner()), run_time=0.8)

        t0 = 0.78
        close_lines = VGroup(
            ladder(t0 - 0.05, color=ROSE, opacity=0.34, width=4),
            ladder(t0, color=INK, opacity=1.0, width=6),
            ladder(t0 + 0.05, color=ROSE, opacity=0.34, width=4),
        )
        touch = Dot(p(LENGTH * np.cos(t0) ** 3, LENGTH * np.sin(t0) ** 3), color=AMBER, radius=0.08)
        self.play(FadeIn(close_lines), FadeIn(touch), run_time=1.0)

        box = panel(width=6.12, height=6.2)
        box_title = cn("固定 x、y，对 θ 求导", 0.42).move_to(box.get_top() + DOWN * 0.36)
        f = MathTex(r"F=x\sec\theta+y\csc\theta-L", color=INK).scale(0.62)
        d1 = MathTex(r"\frac{d}{d\theta}\sec\theta=\sec\theta\tan\theta", color=MINT).scale(0.58)
        d2 = MathTex(r"\frac{d}{d\theta}\csc\theta=-\csc\theta\cot\theta", color=MINT).scale(0.58)
        derivative = MathTex(
            r"\frac{\partial F}{\partial\theta}"
            r"=x\sec\theta\tan\theta-y\csc\theta\cot\theta",
            color=INK,
        ).scale(0.52)
        result = MathTex(r"x\sec\theta\tan\theta-y\csc\theta\cot\theta=0", color=AMBER).scale(0.62)
        note = cn("这不是新假设，只是把“擦边”条件写成导数。", 0.29, MUTED)
        stack = VGroup(f, d1, d2, derivative, result, note).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        stack.next_to(box_title, DOWN, buff=0.42).align_to(box, LEFT).shift(RIGHT * 0.42)
        self.play(FadeIn(box, shift=LEFT * 0.2), FadeIn(box_title), run_time=0.8)
        for item in stack:
            self.play(FadeIn(item, shift=UP * 0.08), run_time=0.8)
        self.wait(1.0)
        self.wait(14.9)


class SolveParameter(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title = cn("把两条条件合在一起", 0.5).to_edge(UP)
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)
        self.play(Create(corner()), run_time=0.7)

        t0 = 0.84
        self.play(FadeIn(ladder(t0, width=7)), run_time=0.8)

        box = panel(width=6.12, height=6.25)
        box_title = cn("从导数条件解出 x 和 y", 0.42).move_to(box.get_top() + DOWN * 0.36)
        eq1 = MathTex(r"x\sec\theta+y\csc\theta=L", color=MINT).scale(0.58)
        eq2 = MathTex(r"x\sec\theta\tan\theta=y\csc\theta\cot\theta", color=AMBER).scale(0.56)
        expand = MathTex(r"\frac{x\sin\theta}{\cos^2\theta}=\frac{y\cos\theta}{\sin^2\theta}", color=INK).scale(0.56)
        cube = MathTex(r"x\sin^3\theta=y\cos^3\theta", color=INK).scale(0.62)
        ratio = MathTex(r"\frac{x}{\cos^3\theta}=\frac{y}{\sin^3\theta}=k", color=INK).scale(0.62)
        plug = MathTex(r"k(\cos^2\theta+\sin^2\theta)=L\Rightarrow k=L", color=INK).scale(0.58)
        param = MathTex(r"x=L\cos^3\theta,\qquad y=L\sin^3\theta", color=MINT).scale(0.66)
        stack = VGroup(eq1, eq2, expand, cube, ratio, plug, param).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        stack.next_to(box_title, DOWN, buff=0.36).align_to(box, LEFT).shift(RIGHT * 0.4)
        self.play(FadeIn(box, shift=LEFT * 0.2), FadeIn(box_title), run_time=0.8)
        for item in stack:
            self.play(FadeIn(item, shift=UP * 0.08), run_time=0.85)
        self.wait(1.0)
        self.wait(23.5)


class FourQuadrantAstroid(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title = cn("完整画出来，它就像一颗圆润的星", 0.48).to_edge(UP)
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)

        axes = astroid_axes()
        curve = full_astroid()
        cusps = VGroup(*[Dot(astroid_point(t), color=AMBER, radius=0.07) for t in [0, PI / 2, PI, 3 * PI / 2]])
        cusp_label = cn("四个尖角", 0.32, AMBER).next_to(curve, DOWN, buff=0.28)

        self.play(Create(axes), run_time=0.8)
        self.play(Create(curve), run_time=3.2)
        self.play(FadeIn(cusps), FadeIn(cusp_label), run_time=0.8)

        box = panel(width=6.12, height=5.5)
        box_title = cn("从参数式到普通方程", 0.42).move_to(box.get_top() + DOWN * 0.36)
        param = MathTex(r"x=L\cos^3\theta,\qquad y=L\sin^3\theta", color=MINT).scale(0.62)
        power1 = MathTex(
            r"\left(\frac{x}{L}\right)^{\frac{2}{3}}=\cos^2\theta,\qquad"
            r"\left(\frac{y}{L}\right)^{\frac{2}{3}}=\sin^2\theta",
            color=INK,
        ).scale(0.52)
        identity = MathTex(r"\cos^2\theta+\sin^2\theta=1", color=INK).scale(0.64)
        final = MathTex(r"x^{\frac{2}{3}}+y^{\frac{2}{3}}=L^{\frac{2}{3}}", color=AMBER).scale(0.86)
        name = cn("这条曲线叫：星形线", 0.34, AMBER)
        stack = VGroup(param, power1, identity, final, name).arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        stack.next_to(box_title, DOWN, buff=0.42).align_to(box, LEFT).shift(RIGHT * 0.42)
        self.play(FadeIn(box, shift=LEFT * 0.2), FadeIn(box_title), run_time=0.8)
        self.play(Write(param), run_time=1.0)
        self.play(FadeIn(power1, shift=UP * 0.08), run_time=1.0)
        self.play(FadeIn(identity, shift=UP * 0.08), run_time=0.9)
        self.play(TransformFromCopy(identity, final), FadeIn(name), run_time=1.6)
        self.wait(1.0)
        self.wait(11.25)


class RealityExamples(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title = cn("它不只是一条课本曲线", 0.5).to_edge(UP)
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)

        axes = astroid_axes()
        curve = full_astroid(width=10)
        halo = full_astroid(width=18).set_stroke(color=AMBER, opacity=0.16)
        self.play(FadeIn(axes), Create(curve), FadeIn(halo), run_time=1.6)

        box = panel(width=6.1, height=5.6)
        box_title = cn("哪里会遇到类似的包络线？", 0.42).move_to(box.get_top() + DOWN * 0.36)
        examples = VGroup(
            cn("机械臂能到达的运动边界", 0.32, INK),
            cn("光线聚成的焦散曲线", 0.32, INK),
            cn("工程里描述安全范围的外包络", 0.32, INK),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        examples.next_to(box_title, DOWN, buff=0.55).align_to(box, LEFT).shift(RIGHT * 0.55)
        self.play(FadeIn(box, shift=LEFT * 0.2), FadeIn(box_title), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(item, shift=UP * 0.1) for item in examples], lag_ratio=0.22), run_time=1.6)
        self.play(curve.animate.set_stroke(width=13), halo.animate.set_stroke(width=24, opacity=0.22), run_time=1.0)
        self.wait(12.9)
