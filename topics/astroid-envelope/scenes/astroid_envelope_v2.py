from __future__ import annotations

import numpy as np
from manim import *


FONT = "Microsoft YaHei"
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


def p(x: float, y: float) -> np.ndarray:
    return ORIGIN + SCALE * np.array([x, y, 0.0])


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
    return VGroup(floor, wall)


def panel(width: float = 5.9, height: float = 6.2) -> RoundedRectangle:
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.22,
        stroke_color="#314054",
        fill_color=PANEL,
        fill_opacity=0.94,
    ).to_edge(RIGHT, buff=0.28).shift(DOWN * 0.12)


def cn(text: str, size: float = 0.36, color: str = INK) -> Text:
    return Text(text, font=FONT, color=color).scale(size)


def formula_card(*items: Mobject, buff: float = 0.24, width: float = 5.3) -> VGroup:
    group = VGroup(*items).arrange(DOWN, aligned_edge=LEFT, buff=buff)
    bg = RoundedRectangle(
        width=width,
        height=group.height + 0.48,
        corner_radius=0.16,
        stroke_color="#26394D",
        fill_color="#101D2E",
        fill_opacity=0.94,
    )
    bg.move_to(group)
    return VGroup(bg, group)


def legend_row(math: str, desc: str, color: str = INK) -> VGroup:
    return VGroup(
        MathTex(math, color=color).scale(0.62),
        cn(desc, 0.29, MUTED),
    ).arrange(RIGHT, buff=0.18)


class Chapter01Variables(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title = cn("第 1 章：先把变量绑回真实的棍子", 0.52).to_edge(UP)
        hook = cn("别急着看公式：先认清每个字母在画面里指什么。", 0.36, AMBER)
        hook.next_to(title, DOWN, buff=0.18)

        self.play(FadeIn(title, shift=DOWN * 0.18), FadeIn(hook, shift=DOWN * 0.18))
        self.play(Create(corner()), run_time=1.0)

        theta = ValueTracker(1.28)
        stick = always_redraw(lambda: ladder(theta.get_value(), width=8))
        a_dot = always_redraw(lambda: Dot(p(LENGTH * np.cos(theta.get_value()), 0), color=AMBER, radius=0.07))
        b_dot = always_redraw(lambda: Dot(p(0, LENGTH * np.sin(theta.get_value())), color=MINT, radius=0.07))
        theta_arc = always_redraw(
            lambda: Arc(
                radius=0.55,
                start_angle=0,
                angle=theta.get_value(),
                arc_center=p(0, 0),
                color=ROSE,
                stroke_width=4,
            )
        )
        theta_label = always_redraw(lambda: MathTex(r"\theta", color=ROSE).scale(0.62).move_to(p(0.78, 0.42)))
        l_label = always_redraw(lambda: cn("棍长 L", 0.32, INK).move_to(stick.get_center() + UP * 0.18))

        self.play(FadeIn(stick), FadeIn(a_dot), FadeIn(b_dot), Create(theta_arc), FadeIn(theta_label), FadeIn(l_label))
        self.play(theta.animate.set_value(0.52), run_time=4.8, rate_func=smooth)
        self.play(theta.animate.set_value(0.94), run_time=2.0, rate_func=smooth)

        fixed_theta = 0.94
        a = LENGTH * np.cos(fixed_theta)
        b = LENGTH * np.sin(fixed_theta)
        point = p(a * 0.48, b * 0.52)
        x_line = DashedLine(p(0, 0), p(a * 0.48, 0), color=AMBER, dash_length=0.08)
        y_line = DashedLine(p(a * 0.48, 0), point, color=MINT, dash_length=0.08)
        p_dot = Dot(point, color=ROSE, radius=0.07)
        p_label = MathTex(r"P=(x,y)", color=ROSE).scale(0.58).next_to(p_dot, UR, buff=0.06)
        x_label = MathTex("x", color=AMBER).scale(0.58).next_to(x_line, DOWN, buff=0.06)
        y_label = MathTex("y", color=MINT).scale(0.58).next_to(y_line, RIGHT, buff=0.06)

        legend = panel(width=5.7, height=5.6)
        legend_title = cn("画面里的量", 0.46).move_to(legend.get_top() + DOWN * 0.38)
        rows = VGroup(
            legend_row(r"L", "棍子的固定长度", INK),
            legend_row(r"\theta", "棍子和地面的夹角", ROSE),
            legend_row(r"a=L\cos\theta", "地面截距", AMBER),
            legend_row(r"b=L\sin\theta", "墙上截距", MINT),
            legend_row(r"(x,y)", "棍子上的一个点", ROSE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        rows.next_to(legend_title, DOWN, buff=0.45).align_to(legend, LEFT).shift(RIGHT * 0.42)

        self.play(FadeIn(legend, shift=LEFT * 0.2), FadeIn(legend_title), LaggedStart(*[FadeIn(row) for row in rows], lag_ratio=0.15))
        self.play(Create(x_line), Create(y_line), FadeIn(p_dot), FadeIn(p_label), FadeIn(x_label), FadeIn(y_label))
        self.wait(13.0)


class Chapter02LineEquation(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title = cn("第 2 章：secθ 不是魔法，是截距式换了个写法", 0.48).to_edge(UP)
        self.play(FadeIn(title, shift=DOWN * 0.18))
        self.play(Create(corner()), run_time=0.8)

        theta = 0.88
        a = LENGTH * np.cos(theta)
        b = LENGTH * np.sin(theta)
        stick = ladder(theta, width=8)
        a_dot = Dot(p(a, 0), color=AMBER, radius=0.075)
        b_dot = Dot(p(0, b), color=MINT, radius=0.075)
        a_label = MathTex(r"a=L\cos\theta", color=AMBER).scale(0.55).next_to(a_dot, DOWN, buff=0.08)
        b_label = MathTex(r"b=L\sin\theta", color=MINT).scale(0.55).next_to(b_dot, LEFT, buff=0.08)
        point = p(a * 0.55, b * 0.45)
        p_dot = Dot(point, color=ROSE, radius=0.07)
        p_label = MathTex(r"P=(x,y)", color=ROSE).scale(0.55).next_to(p_dot, UR, buff=0.06)
        x_part = Line(p(0, 0), p(a * 0.55, 0), color=AMBER, stroke_width=5)
        y_part = Line(p(a * 0.55, 0), point, color=MINT, stroke_width=5)

        self.play(FadeIn(stick), FadeIn(a_dot), FadeIn(b_dot), FadeIn(a_label), FadeIn(b_label))
        self.play(FadeIn(p_dot), FadeIn(p_label), Create(x_part), Create(y_part))

        box = panel(width=6.1, height=6.3)
        box_title = cn("从“截距”自然得到直线方程", 0.42).move_to(box.get_top() + DOWN * 0.36)
        f1 = MathTex(r"\frac{x}{a}+\frac{y}{b}=1", color=INK).scale(0.86)
        note1 = cn("点 P 在这根棍子上：横向占比 + 纵向占比 = 1", 0.27, MUTED)
        f2 = MathTex(r"a=L\cos\theta,\qquad b=L\sin\theta", color=INK).scale(0.66)
        f3 = MathTex(r"\frac{x}{L\cos\theta}+\frac{y}{L\sin\theta}=1", color=INK).scale(0.7)
        f4 = MathTex(r"x\sec\theta+y\csc\theta=L", color=AMBER).scale(0.82)
        note2 = MathTex(r"\sec\theta=\frac{1}{\cos\theta},\qquad \csc\theta=\frac{1}{\sin\theta}", color=MUTED).scale(0.52)
        stack = VGroup(f1, note1, f2, f3, f4, note2).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        stack.next_to(box_title, DOWN, buff=0.42).align_to(box, LEFT).shift(RIGHT * 0.42)

        self.play(FadeIn(box, shift=LEFT * 0.2), FadeIn(box_title))
        for item in stack:
            self.play(FadeIn(item, shift=UP * 0.08), run_time=0.9)
        self.play(Circumscribe(f4, color=AMBER, time_width=0.75), run_time=1.1)
        self.wait(18.0)


class Chapter03EnvelopeCondition(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title = cn("第 3 章：边界不是某一根棍子画的，而是所有位置共同擦出来的", 0.44).to_edge(UP)
        self.play(FadeIn(title, shift=DOWN * 0.18))
        self.play(Create(corner()), run_time=0.8)

        trace_thetas = np.linspace(0.18, 1.38, 42)
        trace_lines = VGroup(*[ladder(t, color=BLUE, opacity=0.14, width=2.4) for t in trace_thetas])
        self.play(LaggedStart(*[Create(line) for line in trace_lines], lag_ratio=0.025), run_time=3.2)

        t0 = 0.78
        close_lines = VGroup(
            ladder(t0 - 0.055, color=ROSE, opacity=0.55, width=4),
            ladder(t0, color=INK, opacity=1.0, width=6),
            ladder(t0 + 0.055, color=ROSE, opacity=0.55, width=4),
        )
        touch = Dot(p(LENGTH * np.cos(t0) ** 3, LENGTH * np.sin(t0) ** 3), color=AMBER, radius=0.08)
        touch_label = cn("边界点：相邻位置几乎贴着它擦过", 0.31, AMBER).next_to(touch, UR, buff=0.1)
        astroid = ParametricFunction(
            lambda t: p(LENGTH * np.cos(t) ** 3, LENGTH * np.sin(t) ** 3),
            t_range=[0, PI / 2],
            color=AMBER,
            stroke_width=8,
        )

        self.play(FadeIn(close_lines), FadeIn(touch), FadeIn(touch_label))
        self.play(Create(astroid), run_time=2.0)

        box = panel(width=6.0, height=5.7)
        box_title = cn("翻译成微分条件", 0.42).move_to(box.get_top() + DOWN * 0.36)
        f = MathTex(r"F(x,y,\theta)=x\sec\theta+y\csc\theta-L", color=INK).scale(0.58)
        c1 = MathTex(r"F=0", color=MINT).scale(0.78)
        c1_note = cn("点在某一根棍子上", 0.28, MUTED)
        c2 = MathTex(r"\frac{\partial F}{\partial\theta}=0", color=AMBER).scale(0.78)
        c2_note = cn("θ 轻轻变动，边界点一阶不动", 0.28, MUTED)
        derivative = MathTex(
            r"x\sec\theta\tan\theta-y\csc\theta\cot\theta=0",
            color=INK,
        ).scale(0.55)
        stack = VGroup(
            f,
            VGroup(c1, c1_note).arrange(RIGHT, buff=0.25),
            VGroup(c2, c2_note).arrange(RIGHT, buff=0.25),
            derivative,
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        stack.next_to(box_title, DOWN, buff=0.48).align_to(box, LEFT).shift(RIGHT * 0.4)

        self.play(FadeIn(box, shift=LEFT * 0.2), FadeIn(box_title))
        for item in stack:
            self.play(FadeIn(item, shift=UP * 0.08), run_time=1.0)
        self.play(Circumscribe(c2, color=AMBER, time_width=0.75), run_time=1.1)
        self.wait(14.0)


class Chapter04AstroidAndWhere(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        title = cn("第 4 章：消去 θ，星形线就浮出来了", 0.5).to_edge(UP)
        self.play(FadeIn(title, shift=DOWN * 0.18))
        self.play(Create(corner()), run_time=0.8)

        trace_lines = VGroup(*[ladder(t, color=BLUE, opacity=0.10, width=2) for t in np.linspace(0.18, 1.38, 34)])
        astroid = ParametricFunction(
            lambda t: p(LENGTH * np.cos(t) ** 3, LENGTH * np.sin(t) ** 3),
            t_range=[0, PI / 2],
            color=AMBER,
            stroke_width=9,
        )
        self.play(FadeIn(trace_lines), Create(astroid), run_time=2.3)

        box = panel(width=6.1, height=6.25)
        box_title = cn("从参数式到方程", 0.42).move_to(box.get_top() + DOWN * 0.36)
        param = MathTex(r"x=L\cos^3\theta,\qquad y=L\sin^3\theta", color=MINT).scale(0.66)
        power1 = MathTex(
            r"\left(\frac{x}{L}\right)^{\frac{2}{3}}=\cos^2\theta,\qquad"
            r"\left(\frac{y}{L}\right)^{\frac{2}{3}}=\sin^2\theta",
            color=INK,
        ).scale(0.52)
        identity = MathTex(r"\cos^2\theta+\sin^2\theta=1", color=INK).scale(0.64)
        final = MathTex(
            r"x^{\frac{2}{3}}+y^{\frac{2}{3}}=L^{\frac{2}{3}}",
            color=AMBER,
        ).scale(0.86)
        first_quadrant = cn("这是第一象限里的星形线。", 0.3, AMBER)
        stack = VGroup(param, power1, identity, final, first_quadrant).arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        stack.next_to(box_title, DOWN, buff=0.42).align_to(box, LEFT).shift(RIGHT * 0.42)

        self.play(FadeIn(box, shift=LEFT * 0.2), FadeIn(box_title))
        self.play(Write(param), run_time=1.2)
        self.play(FadeIn(power1, shift=UP * 0.08), run_time=1.1)
        self.play(FadeIn(identity, shift=UP * 0.08), run_time=1.0)
        self.play(TransformFromCopy(identity, final), FadeIn(first_quadrant), run_time=1.7)
        self.play(Circumscribe(final, color=AMBER, time_width=0.8), run_time=1.1)

        examples = VGroup(
            cn("现实里的同类影子：", 0.34, INK),
            cn("机械臂或扫地机器人：运动范围的边界", 0.29, MUTED),
            cn("光线与反射：很多光线共同形成焦散曲线", 0.29, MUTED),
            cn("工程里的安全包络：所有姿态的外轮廓", 0.29, MUTED),
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
        self.wait(20.0)
