from __future__ import annotations

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


def p(x: float, y: float) -> np.ndarray:
    return ORIGIN + SCALE * np.array([x, y, 0.0])


def cn(text: str, size: float = 0.36, color: str = INK) -> Text:
    return Text(text, font=FONT, color=color).scale(size)


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


class StoryHook(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title = cn("墙角里，一根棍子慢慢滑落", 0.56).to_edge(UP)
        question = cn("它扫过的外边界，真的会是圆弧吗？", 0.42, AMBER).next_to(title, DOWN, buff=0.18)
        self.play(FadeIn(title, shift=DOWN * 0.18), FadeIn(question, shift=DOWN * 0.18))
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
        note = cn("许多瞬间叠在一起，边界开始显形。", 0.34, MUTED).to_edge(DOWN)
        self.play(FadeIn(note, shift=UP * 0.1))
        self.play(LaggedStart(*[Create(line) for line in trace_lines], lag_ratio=0.025), run_time=2.4)
        self.play(Create(astroid), run_time=1.6)
        self.wait(2.85)


class VariablesMatter(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title = cn("先把字母绑回画面", 0.52).to_edge(UP)
        self.play(FadeIn(title, shift=DOWN * 0.18))
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
        box_title = cn("图例：每个符号对应什么？", 0.42).move_to(box.get_top() + DOWN * 0.36)
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
        self.wait(14.45)


class LineEquationNatural(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title = cn("那条直线，先用截距来写", 0.5).to_edge(UP)
        self.play(FadeIn(title, shift=DOWN * 0.18))
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
        box_title = cn("从截距式到 sec、csc", 0.42).move_to(box.get_top() + DOWN * 0.36)
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
        self.play(Circumscribe(f4, color=AMBER, time_width=0.75), run_time=1.0)
        self.wait(13.7)


class EnvelopeIdea(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title = cn("边界，是很多瞬间共同擦出来的", 0.5).to_edge(UP)
        self.play(FadeIn(title, shift=DOWN * 0.18))
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
        c2 = VGroup(MathTex(r"\frac{\partial F}{\partial\theta}=0", color=AMBER).scale(0.78), cn("角度轻轻变，边界点一阶不动", 0.28, MUTED)).arrange(RIGHT, buff=0.25)
        derivative = MathTex(r"x\sec\theta\tan\theta-y\csc\theta\cot\theta=0", color=INK).scale(0.55)
        stack = VGroup(f, c1, c2, derivative).arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        stack.next_to(box_title, DOWN, buff=0.48).align_to(box, LEFT).shift(RIGHT * 0.38)
        self.play(FadeIn(box, shift=LEFT * 0.2), FadeIn(box_title))
        for item in stack:
            self.play(FadeIn(item, shift=UP * 0.08), run_time=0.95)
        self.play(Circumscribe(c2, color=AMBER, time_width=0.75), run_time=1.0)
        self.wait(10.0)


class AstroidAndReality(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title = cn("最后，边界有了自己的名字", 0.5).to_edge(UP)
        self.play(FadeIn(title, shift=DOWN * 0.18))
        self.play(Create(corner()), run_time=0.8)

        trace_lines = VGroup(*[ladder(t, color=BLUE, opacity=0.10, width=2) for t in np.linspace(0.18, 1.38, 34)])
        astroid = ParametricFunction(
            lambda t: p(LENGTH * np.cos(t) ** 3, LENGTH * np.sin(t) ** 3),
            t_range=[0, PI / 2],
            color=AMBER,
            stroke_width=9,
        )
        self.play(FadeIn(trace_lines), Create(astroid), run_time=2.2)

        box = panel(width=6.12, height=6.25)
        box_title = cn("从参数式到星形线", 0.42).move_to(box.get_top() + DOWN * 0.36)
        param = MathTex(r"x=L\cos^3\theta,\qquad y=L\sin^3\theta", color=MINT).scale(0.66)
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
        self.play(FadeIn(box, shift=LEFT * 0.2), FadeIn(box_title))
        self.play(Write(param), run_time=1.1)
        self.play(FadeIn(power1, shift=UP * 0.08), run_time=1.0)
        self.play(FadeIn(identity, shift=UP * 0.08), run_time=0.9)
        self.play(TransformFromCopy(identity, final), FadeIn(name), run_time=1.6)
        self.play(Circumscribe(final, color=AMBER, time_width=0.8), run_time=1.0)

        examples = VGroup(
            cn("类似的“外轮廓”还会出现在：", 0.34, INK),
            cn("机械臂能到达的运动边界", 0.29, MUTED),
            cn("光线聚成的焦散曲线", 0.29, MUTED),
            cn("工程里描述风险范围的安全包络", 0.29, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        examples_bg = RoundedRectangle(
            width=6.3,
            height=2.0,
            corner_radius=0.18,
            stroke_color="#314054",
            fill_color="#101D2E",
            fill_opacity=0.94,
        )
        examples_group = VGroup(examples_bg, examples).to_edge(DOWN, buff=0.32).shift(RIGHT * 0.1)
        examples.move_to(examples_bg).align_to(examples_bg, LEFT).shift(RIGHT * 0.35)
        self.play(FadeIn(examples_group, shift=UP * 0.2), astroid.animate.set_stroke(width=12), run_time=1.2)
        self.wait(24.1)
