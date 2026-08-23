from __future__ import annotations

from pathlib import Path
import sys
import numpy as np

from manim import *


SCENE_DIR = Path(__file__).resolve().parent
if str(SCENE_DIR) not in sys.path:
    sys.path.insert(0, str(SCENE_DIR))

from constructible_17_gon_v3 import (  # noqa: E402
    AMBER,
    BLUE,
    CORAL,
    INK,
    MINT,
    MUTED,
    PANEL,
    PANEL_EDGE,
    VIOLET,
    AddSubtractConstructionV3,
    ProductQuotientConstructionV3,
    SquareRootIntersectionV3,
    StyledScene,
    card_heading,
    cn,
    panel,
    pill,
    polygon_group,
    polygon_points,
    title_group,
)


def finish(scene: Scene, target: float) -> None:
    remaining = target - float(scene.time)
    if remaining > 0:
        scene.wait(remaining)


def wait_until(scene: Scene, target: float) -> None:
    remaining = target - float(scene.time)
    if remaining > 0:
        scene.wait(remaining)


def equation_card(tex: str, color: str = INK, width: float = 4.8, scale: float = 0.68) -> VGroup:
    box = RoundedRectangle(
        width=width,
        height=0.84,
        corner_radius=0.16,
        stroke_color=color,
        stroke_width=1.5,
        fill_color=color,
        fill_opacity=0.09,
    )
    formula = MathTex(tex, color=color).scale(scale).move_to(box)
    return VGroup(box, formula)


def label_card(text: str, color: str = INK, width: float = 4.8, size: float = 0.30) -> VGroup:
    box = RoundedRectangle(
        width=width,
        height=0.84,
        corner_radius=0.16,
        stroke_color=color,
        stroke_width=1.5,
        fill_color=color,
        fill_opacity=0.09,
    )
    label = cn(text, size, color).move_to(box)
    return VGroup(box, label)


def tiny_op(symbol: str, label: str, color: str) -> VGroup:
    icon = Circle(radius=0.26, stroke_color=color, fill_color=color, fill_opacity=0.13)
    glyph = MathTex(symbol, color=color).scale(0.55).move_to(icon)
    caption = cn(label, 0.25, color).next_to(icon, DOWN, buff=0.08)
    return VGroup(icon, glyph, caption)


def c_chip(index: int, color: str, width: float = 0.86) -> VGroup:
    box = RoundedRectangle(
        width=width,
        height=0.62,
        corner_radius=0.13,
        stroke_color=color,
        fill_color=color,
        fill_opacity=0.13,
    )
    label = MathTex(rf"c_{{{index}}}", color=color).scale(0.49).move_to(box)
    return VGroup(box, label)


def pair_projection_groups(n: int, radius: float, center: np.ndarray, colors: list[str]) -> VGroup:
    points = polygon_points(n, radius, center, rotation=0)
    groups = VGroup()
    for k in range(1, (n + 1) // 2):
        upper = points[k]
        lower = points[n - k]
        color = colors[(k - 1) % len(colors)]
        chord = Line(lower, upper, color=color, stroke_width=1.8, stroke_opacity=0.76)
        dots = VGroup(Dot(upper, radius=0.045, color=color), Dot(lower, radius=0.045, color=color))
        projection = Dot([upper[0], center[1], 0], radius=0.038, color=color)
        groups.add(VGroup(chord, dots, projection))
    return groups


class ChoiceRevealV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("边更少，反而画不出来？", "只允许无刻度直尺、圆规和有限次交点")
        left_center = LEFT * 3.45 + DOWN * 0.28
        right_center = RIGHT * 3.45 + DOWN * 0.28
        left_circle = Circle(radius=1.72, color=MUTED, stroke_width=1.8).move_to(left_center)
        right_circle = Circle(radius=1.72, color=MUTED, stroke_width=1.8).move_to(right_center)
        seven = polygon_group(7, 1.64, left_center, CORAL, rotation=PI / 2, stroke_width=2.6, dot_radius=0.052)
        seventeen = polygon_group(17, 1.64, right_center, MINT, rotation=PI / 2, stroke_width=2.3, dot_radius=0.034)
        labels = VGroup(cn("正七边形", 0.42), cn("正十七边形", 0.42))
        labels[0].next_to(left_circle, DOWN, buff=0.22)
        labels[1].next_to(right_circle, DOWN, buff=0.22)
        intuition = pill("直觉：7 条边应该更简单", BLUE, 4.40).move_to(DOWN * 2.80)
        verdict7 = pill("不能精确构造", CORAL, 3.20).next_to(left_circle, DOWN, buff=0.22)
        verdict17 = pill("能够精确构造", MINT, 3.20).next_to(right_circle, DOWN, buff=0.22)
        rule = VGroup(
            cn("精确 =", 0.30, MUTED),
            pill("直线", BLUE, 1.18),
            pill("圆", AMBER, 1.02),
            pill("交点", MINT, 1.18),
            cn("有限次", 0.30, MUTED),
        ).arrange(RIGHT, buff=0.16).move_to(DOWN * 2.78)
        question = pill("7 卡在哪个方程？17 怎样拆成可执行步骤？", VIOLET, 6.45).move_to(DOWN * 2.78)

        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.9)
        self.play(Create(left_circle), Create(right_circle), run_time=1.0)
        self.play(Create(seven[0]), FadeIn(seven[1]), Create(seventeen[0]), FadeIn(seventeen[1]), FadeIn(labels), run_time=1.8)
        self.play(FadeIn(intuition, shift=UP * 0.12), run_time=0.8)
        self.wait(1.4)
        self.play(FadeOut(intuition), FadeOut(labels), FadeIn(verdict7), FadeIn(verdict17), run_time=1.0)
        self.play(Indicate(verdict17, color=MINT), run_time=0.8)
        self.wait(1.2)
        self.play(FadeOut(verdict7), FadeOut(verdict17), FadeIn(rule, shift=UP * 0.10), run_time=1.0)
        self.wait(1.4)
        self.play(FadeOut(rule), FadeIn(question, shift=UP * 0.10), run_time=0.9)
        finish(self, 28.475)


class CoordinateTaskV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("先把整张多边形缩成一个坐标", "固定右端起点，只找上半圆的相邻顶点 P")
        center = LEFT * 3.45 + DOWN * 0.22
        radius = 2.05
        alpha = TAU / 17
        circle = Circle(radius=radius, color=BLUE, stroke_width=2.0).move_to(center)
        x_axis = Arrow(center + LEFT * 2.32, center + RIGHT * 2.40, buff=0, color=MUTED, stroke_width=1.5)
        y_axis = Arrow(center + DOWN * 2.26, center + UP * 2.30, buff=0, color=MUTED, stroke_width=1.5)
        start = center + RIGHT * radius
        point = center + radius * np.array([np.cos(alpha), np.sin(alpha), 0.0])
        foot = np.array([point[0], center[1], 0.0])
        start_dot = Dot(start, radius=0.09, color=INK)
        start_label = cn("已知起点", 0.25, INK).next_to(start_dot, RIGHT, buff=0.10)
        p_dot = Dot(point, radius=0.10, color=AMBER)
        p_label = MathTex("P", color=AMBER).scale(0.60).next_to(p_dot, UR, buff=0.08)
        vertical = DashedLine(foot, point, color=MINT, stroke_width=2.5)
        x_seg = Line(center, foot, color=MINT, stroke_width=5.0)
        x_label = MathTex("x", color=MINT).scale(0.62).next_to(x_seg, DOWN, buff=0.12)

        info = panel(5.55, 5.20).to_edge(RIGHT, buff=0.42).shift(DOWN * 0.22)
        heading = card_heading(info, "为什么只构造 x 就够？")
        steps = VGroup(
            equation_card(r"P=(x,y)", AMBER, 4.45, 0.72),
            equation_card(r"x^2+y^2=1", BLUE, 4.45, 0.72),
            equation_card(r"y=+\sqrt{1-x^2}", MINT, 4.45, 0.72),
        ).arrange(DOWN, buff=0.24).next_to(heading, DOWN, buff=0.42)
        conclusion = pill("x → 垂线 → 上半圆交点 P", MINT, 4.60).move_to(info.get_bottom() + UP * 0.48)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(info), FadeIn(heading), run_time=0.9)
        self.play(Create(x_axis), Create(y_axis), Create(circle), FadeIn(start_dot), FadeIn(start_label), run_time=1.2)
        self.play(FadeIn(p_dot, scale=1.5), FadeIn(p_label), FadeIn(steps[0], shift=RIGHT * 0.14), run_time=1.0)
        self.play(Create(x_seg), Create(vertical), FadeIn(x_label), FadeIn(steps[1], shift=RIGHT * 0.14), run_time=1.1)
        self.play(FadeIn(steps[2], shift=RIGHT * 0.14), Indicate(vertical, color=MINT), run_time=1.0)
        self.wait(1.4)
        self.play(FadeIn(conclusion, shift=UP * 0.10), Circumscribe(p_dot, color=AMBER), run_time=1.0)
        finish(self, 28.816)


class AddSubtractConstructionV5(AddSubtractConstructionV3):
    def construct(self) -> None:
        super().construct()
        finish(self, 11.162)


class ProductQuotientConstructionV5(ProductQuotientConstructionV3):
    def construct(self) -> None:
        super().construct()
        finish(self, 9.354)


class SquareRootIntersectionV5(SquareRootIntersectionV3):
    def construct(self) -> None:
        super().construct()
        finish(self, 13.103)


class ConstructionBoundaryV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("为什么这些运算正好就是尺规边界？", "每个新点，都来自两条已知曲线的交点")
        left = panel(5.55, 4.95).to_edge(LEFT, buff=0.42).shift(DOWN * 0.28)
        right = panel(6.05, 4.95).to_edge(RIGHT, buff=0.42).shift(DOWN * 0.28)
        lt = card_heading(left, "交点对应什么方程？")
        rt = card_heading(right, "消元以后最高到哪？")

        cross_center = np.array([-3.55, 0.65, 0.0])
        cross = VGroup(
            Line(cross_center + LEFT * 1.45 + DOWN * 0.48, cross_center + RIGHT * 1.45 + UP * 0.48, color=BLUE, stroke_width=2.7),
            Line(cross_center + LEFT * 1.45 + UP * 0.48, cross_center + RIGHT * 1.45 + DOWN * 0.48, color=MINT, stroke_width=2.7),
            Dot(cross_center, radius=0.075, color=INK),
        )
        line_label = pill("直线 × 直线", BLUE, 2.65).move_to(cross_center + DOWN * 0.90)
        circle_center = np.array([-3.55, -1.30, 0.0])
        circle = Circle(radius=0.78, color=AMBER, stroke_width=2.5).move_to(circle_center)
        secant = Line(circle_center + LEFT * 1.45, circle_center + RIGHT * 1.45, color=BLUE, stroke_width=2.5)
        hits = VGroup(Dot(circle_center + LEFT * 0.78, radius=0.075, color=MINT), Dot(circle_center + RIGHT * 0.78, radius=0.075, color=MINT))
        circle_label = pill("圆 × 直线", AMBER, 2.65).move_to(circle_center + DOWN * 1.05)

        equations = VGroup(
            label_card("两条一次式  →  一次方程", BLUE, 5.10, 0.30),
            equation_card(r"x^2+y^2=r^2,\quad y=mx+b", AMBER, 5.10, 0.54),
            equation_card(r"ax^2+bx+c=0", MINT, 5.10, 0.68),
        ).arrange(DOWN, buff=0.25).next_to(rt, DOWN, buff=0.38)
        ops = VGroup(
            tiny_op("+", "加减", BLUE),
            tiny_op(r"\times", "乘除", VIOLET),
            tiny_op(r"\sqrt{\ }", "开平方", AMBER),
        ).arrange(RIGHT, buff=0.60).move_to(right.get_bottom() + UP * 0.64)
        summary = pill("每个新交点：最多再解一次二次方程", MINT, 5.40).move_to(DOWN * 2.78)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(left), FadeIn(right), FadeIn(lt), FadeIn(rt), run_time=0.9)
        self.play(Create(cross[:2]), FadeIn(cross[2], scale=1.5), FadeIn(line_label), FadeIn(equations[0], shift=RIGHT * 0.14), run_time=1.2)
        wait_until(self, 4.8)
        self.play(Create(circle), Create(secant), FadeIn(hits, scale=1.5), FadeIn(circle_label), FadeIn(equations[1], shift=RIGHT * 0.14), run_time=1.3)
        self.play(FadeIn(equations[2], shift=RIGHT * 0.14), Indicate(hits, color=MINT), run_time=1.0)
        wait_until(self, 14.7)
        self.play(LaggedStart(*[FadeIn(op, shift=UP * 0.10) for op in ops], lag_ratio=0.18), run_time=1.2)
        wait_until(self, 19.2)
        self.play(FadeIn(summary, shift=UP * 0.10), run_time=0.8)
        finish(self, 25.877)


class MinimalDegreeV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("给这条边界一个可检查的标签", "最简方程次数：次数最低、且不能继续拆开的有理系数方程")
        left = panel(5.75, 4.95).to_edge(LEFT, buff=0.42).shift(DOWN * 0.28)
        right = panel(5.90, 4.95).to_edge(RIGHT, buff=0.42).shift(DOWN * 0.28)
        lt = card_heading(left, "先看两个具体数")
        rt = card_heading(right, "连续二次求解会怎样？")

        sqrt2 = VGroup(
            MathTex(r"\sqrt2", color=BLUE).scale(0.76),
            MathTex(r"\longrightarrow", color=MUTED).scale(0.48),
            equation_card(r"x^2-2=0", BLUE, 2.70, 0.60),
        ).arrange(RIGHT, buff=0.24).move_to(left.get_center() + UP * 0.78)
        sqrt2_degree = pill("最简次数 = 2", BLUE, 3.05).move_to(left.get_center() + UP * 0.03)
        nested = VGroup(
            MathTex(r"\sqrt{1+\sqrt2}", color=VIOLET).scale(0.68),
            MathTex(r"\longrightarrow", color=MUTED).scale(0.48),
            equation_card(r"x^4-2x^2-1=0", VIOLET, 3.05, 0.55),
        ).arrange(RIGHT, buff=0.20).move_to(left.get_center() + DOWN * 0.82)
        nested_degree = pill("再一层：次数 = 4", VIOLET, 3.15).move_to(left.get_center() + DOWN * 1.58)

        tower = VGroup(
            equation_card(r"\mathbb{Q}", INK, 1.15, 0.62),
            label_card("一次二次求解", BLUE, 2.72, 0.29),
            label_card("再一次二次求解", VIOLET, 3.08, 0.29),
        ).arrange(DOWN, buff=0.34).next_to(rt, DOWN, buff=0.42)
        arrows = VGroup(*[
            Arrow(tower[i].get_bottom(), tower[i + 1].get_top(), buff=0.06, color=MUTED, stroke_width=1.8)
            for i in range(2)
        ])
        mult = VGroup(
            cn("× 1 或 2", 0.25, BLUE),
            cn("× 1 或 2", 0.25, VIOLET),
            cn("× 1 或 2", 0.25, MINT),
        )
        for i in range(2):
            mult[i].next_to(arrows[i], RIGHT, buff=0.12)
        chain = MathTex(r"1,\ 2,\ 4,\ 8,\ \ldots", color=MINT).scale(0.83).move_to(right.get_bottom() + UP * 0.58)
        note = pill("最简次数必须整除总次数", AMBER, 4.15).move_to(DOWN * 2.50)
        definition_left = label_card("一个数可以满足很多方程", BLUE, 4.65, 0.29).move_to(left.get_center())
        definition_right = label_card("只看次数最低且不能再拆的", MINT, 4.65, 0.29).move_to(right.get_center())

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(left), FadeIn(right), FadeIn(lt), FadeIn(rt), run_time=0.9)
        self.play(FadeIn(definition_left, shift=UP * 0.08), FadeIn(definition_right, shift=UP * 0.08), run_time=0.9)
        wait_until(self, 14.6)
        self.play(FadeOut(definition_left), FadeOut(definition_right), run_time=0.5)
        self.play(FadeIn(sqrt2, shift=RIGHT * 0.12), run_time=1.0)
        self.play(FadeIn(sqrt2_degree, shift=UP * 0.10), run_time=0.7)
        wait_until(self, 19.5)
        self.play(FadeIn(nested, shift=RIGHT * 0.12), run_time=1.0)
        self.play(FadeIn(nested_degree, shift=UP * 0.10), run_time=0.7)
        wait_until(self, 25.8)
        self.play(FadeIn(tower[0]), run_time=0.6)
        for i in range(2):
            self.play(GrowArrow(arrows[i]), FadeIn(mult[i]), FadeIn(tower[i + 1], shift=DOWN * 0.10), run_time=0.9)
            self.wait(0.8)
        wait_until(self, 37.0)
        self.play(FadeIn(chain, shift=UP * 0.10), run_time=0.8)
        self.play(FadeIn(note, shift=UP * 0.10), Indicate(chain, color=MINT), run_time=0.9)
        finish(self, 44.671)


class NecessaryNotSufficientV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("先分清：这是必要门槛，不是成功证明", "非二次幂一定失败；二次幂仍要给出实际二次链")
        left = panel(5.55, 3.65, CORAL).to_edge(LEFT, buff=0.58).shift(DOWN * 0.32)
        right = panel(5.55, 3.65, MINT).to_edge(RIGHT, buff=0.58).shift(DOWN * 0.32)
        litems = VGroup(
            MathTex("3", color=CORAL).scale(1.25),
            cn("不是 2 的幂", 0.34, CORAL),
            pill("一定过不了尺规", CORAL, 3.35),
        ).arrange(DOWN, buff=0.30).move_to(left)
        ritems = VGroup(
            MathTex("8", color=MINT).scale(1.25),
            cn("虽然是 2 的幂", 0.34, MINT),
            pill("仍需真的拆成二次步骤", AMBER, 3.95),
        ).arrange(DOWN, buff=0.30).move_to(right)
        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(left), FadeIn(right), run_time=0.8)
        self.play(FadeIn(litems[0]), FadeIn(ritems[0]), run_time=0.6)
        self.play(FadeIn(litems[1]), FadeIn(ritems[1]), run_time=0.6)
        self.play(FadeIn(litems[2], shift=UP * 0.10), run_time=0.7)
        self.play(FadeIn(ritems[2], shift=UP * 0.10), Circumscribe(ritems[2][0], color=AMBER), run_time=0.8)
        finish(self, 12.993)


class HeptagonSetupV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("正七边形：先把顶点变成横向投影", "目标 u=c1，正好是相邻顶点横坐标的两倍")
        center = LEFT * 3.45 + DOWN * 0.25
        radius = 2.05
        pts = polygon_points(7, radius, center, rotation=0)
        circle = Circle(radius=radius, color=BLUE, stroke_width=1.9).move_to(center)
        arrows = VGroup(*[
            Arrow(center, p, buff=0.08, color=MUTED, stroke_width=1.45, max_tip_length_to_length_ratio=0.08)
            for p in pts
        ])
        dots = VGroup(*[Dot(p, radius=0.065, color=CORAL) for p in pts])
        fixed = Dot(pts[0], radius=0.095, color=INK)
        x_axis = Line(center + LEFT * 2.28, center + RIGHT * 2.28, color=MUTED, stroke_width=1.4)
        pair_colors = [MINT, AMBER, VIOLET]
        pair_lines = VGroup()
        projections = VGroup()
        pair_labels = VGroup()
        for k in range(1, 4):
            upper, lower = pts[k], pts[7 - k]
            color = pair_colors[k - 1]
            pair_lines.add(Line(lower, upper, color=color, stroke_width=2.3))
            foot = np.array([upper[0], center[1], 0.0])
            projections.add(Dot(foot, radius=0.055, color=color))
            pair_labels.add(MathTex(rf"c_{k}", color=color).scale(0.48).next_to(foot, DOWN, buff=0.10))

        info = panel(5.55, 5.08).to_edge(RIGHT, buff=0.42).shift(DOWN * 0.25)
        heading = card_heading(info, "每一对上下顶点")
        definition = equation_card(r"c_k=2\cos\frac{2\pi k}{7}", MINT, 4.65, 0.66).next_to(heading, DOWN, buff=0.40)
        vector_note = VGroup(
            cn("竖直分量：上下抵消", 0.31, MUTED),
            cn("横向投影：相加保留", 0.31, INK),
        ).arrange(DOWN, buff=0.18).next_to(definition, DOWN, buff=0.38)
        sum_card = equation_card(r"1+c_1+c_2+c_3=0", AMBER, 4.75, 0.70).next_to(vector_note, DOWN, buff=0.40)
        target = pill("目标：u=c1", CORAL, 3.00).move_to(info.get_bottom() + UP * 0.75)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(info), FadeIn(heading), run_time=0.9)
        self.play(Create(circle), Create(x_axis), FadeIn(dots), FadeIn(fixed), run_time=1.0)
        self.play(FadeIn(definition, shift=RIGHT * 0.14), run_time=0.8)
        wait_until(self, 9.4)
        self.play(FadeIn(target, shift=UP * 0.10), run_time=0.7)
        wait_until(self, 13.5)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.10), run_time=1.4)
        wait_until(self, 21.3)
        for i in range(3):
            self.play(Create(pair_lines[i]), FadeIn(projections[i]), FadeIn(pair_labels[i]), run_time=0.75)
            self.wait(0.55)
        self.play(FadeIn(vector_note[0]), arrows[1].animate.set_opacity(0.28), arrows[6].animate.set_opacity(0.28), run_time=0.8)
        self.play(FadeIn(vector_note[1]), Indicate(projections, color=MINT), run_time=0.8)
        wait_until(self, 31.9)
        self.play(FadeIn(sum_card, shift=UP * 0.10), run_time=0.9)
        self.play(Circumscribe(pair_labels[0], color=CORAL), run_time=0.8)
        finish(self, 36.459)


class HeptagonIdentityV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("用同一个积化和差公式，追踪 u² 和 u³", "下标绕 7 循环；正负下标表示同一个横向投影")
        identity = equation_card(r"c_i c_j=c_{i+j}+c_{i-j}", VIOLET, 6.05, 0.76).move_to(UP * 1.85)
        left = panel(5.65, 3.70, BLUE).to_edge(LEFT, buff=0.55).shift(DOWN * 0.60)
        right = panel(5.65, 3.70, AMBER).to_edge(RIGHT, buff=0.55).shift(DOWN * 0.60)
        lt = card_heading(left, "先算 u²", BLUE)
        rt = card_heading(right, "再算 u³", AMBER)
        left_steps = VGroup(
            MathTex(r"u^2=c_1c_1", color=INK).scale(0.66),
            MathTex(r"=c_2+c_0", color=BLUE).scale(0.66),
            MathTex(r"c_0=2\cos0=2", color=MUTED).scale(0.56),
            MathTex(r"\boxed{u^2=c_2+2}", color=BLUE).scale(0.72),
        ).arrange(DOWN, buff=0.23).next_to(lt, DOWN, buff=0.38)
        right_steps = VGroup(
            MathTex(r"u^3=u(c_2+2)", color=INK).scale(0.62),
            MathTex(r"c_1c_2=c_3+c_1", color=AMBER).scale(0.62),
            MathTex(r"u^3=(c_3+u)+2u", color=MUTED).scale(0.59),
            MathTex(r"\boxed{u^3=c_3+3u}", color=AMBER).scale(0.70),
        ).arrange(DOWN, buff=0.23).next_to(rt, DOWN, buff=0.38)
        flow = Arrow(left.get_right(), right.get_left(), buff=0.10, color=MINT, stroke_width=2.2)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(identity, shift=DOWN * 0.10), run_time=0.9)
        self.play(FadeIn(left), FadeIn(right), FadeIn(lt), FadeIn(rt), run_time=0.8)
        wait_until(self, 13.2)
        for row in left_steps:
            self.play(FadeIn(row, shift=RIGHT * 0.14), run_time=0.75)
            self.wait(0.75)
        wait_until(self, 23.4)
        self.play(GrowArrow(flow), run_time=0.7)
        for row in right_steps:
            self.play(FadeIn(row, shift=RIGHT * 0.14), run_time=0.75)
            self.wait(0.80)
        self.play(Indicate(left_steps[-1], color=BLUE), Indicate(right_steps[-1], color=AMBER), run_time=0.9)
        finish(self, 32.236)


class HeptagonCubicV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("把 c2、c3 消掉，三次障碍就出现了", "每一行只使用上一屏已经得到的关系")
        source = VGroup(
            equation_card(r"1+u+c_2+c_3=0", AMBER, 4.65, 0.66),
            equation_card(r"c_2=u^2-2", BLUE, 3.55, 0.64),
            equation_card(r"c_3=u^3-3u", VIOLET, 3.75, 0.64),
        ).arrange(RIGHT, buff=0.34).move_to(UP * 1.35)
        arrow = Arrow(UP * 0.55, DOWN * 0.18, color=MUTED, stroke_width=2.3)
        substitution = MathTex(r"1+u+(u^2-2)+(u^3-3u)=0", color=INK).scale(0.73).move_to(DOWN * 0.52)
        result = equation_card(r"\boxed{u^3+u^2-2u-1=0}", CORAL, 6.65, 0.82).move_to(DOWN * 1.72)
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)
        self.play(FadeIn(source[0], shift=DOWN * 0.10), run_time=0.7)
        self.play(FadeIn(source[1], shift=DOWN * 0.10), FadeIn(source[2], shift=DOWN * 0.10), run_time=0.8)
        self.play(GrowArrow(arrow), FadeIn(substitution, shift=DOWN * 0.10), run_time=0.9)
        self.wait(1.0)
        self.play(FadeIn(result, shift=UP * 0.12), Circumscribe(result[0], color=CORAL), run_time=1.0)
        finish(self, 13.707)


class HeptagonIrreducibleV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("这个三次式能不能拆成“一次 × 二次”？", "如果能拆，它一定会暴露一个有理数根")
        top = equation_card(r"f(u)=u^3+u^2-2u-1", CORAL, 6.25, 0.76).move_to(UP * 1.90)
        rule = panel(5.70, 3.20).to_edge(LEFT, buff=0.55).shift(DOWN * 0.58)
        test = panel(5.70, 3.20).to_edge(RIGHT, buff=0.55).shift(DOWN * 0.58)
        rt = card_heading(rule, "可能的有理根从哪里来？")
        tt = card_heading(test, "只需代入两个数")
        fraction = VGroup(
            cn("最简分数的分母整除首项系数 1", 0.28, MUTED),
            cn("分子整除常数项 −1", 0.28, MUTED),
            MathTex(r"u\in\{1,-1\}", color=AMBER).scale(0.76),
        ).arrange(DOWN, buff=0.25).next_to(rt, DOWN, buff=0.38)
        tests = VGroup(
            equation_card(r"f(1)=-1\ne0", CORAL, 4.55, 0.63),
            equation_card(r"f(-1)=1\ne0", CORAL, 4.55, 0.63),
            pill("没有有理根 → 三次式拆不开", CORAL, 4.70),
        ).arrange(DOWN, buff=0.27).next_to(tt, DOWN, buff=0.36)
        degree_axis = VGroup(
            pill("尺规链", MINT, 1.65),
            MathTex(r"1\to2\to4\to8\to\cdots", color=MINT).scale(0.65),
            pill("七边形", CORAL, 1.65),
            MathTex("3", color=CORAL).scale(0.88),
        ).arrange(RIGHT, buff=0.28).move_to(DOWN * 2.20)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(top, shift=DOWN * 0.10), run_time=0.9)
        self.play(FadeIn(rule), FadeIn(test), FadeIn(rt), FadeIn(tt), run_time=0.8)
        wait_until(self, 7.5)
        self.play(FadeIn(fraction[0]), run_time=0.7)
        self.play(FadeIn(fraction[1]), run_time=0.7)
        self.play(FadeIn(fraction[2], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 17.8)
        self.play(FadeIn(tests[0], shift=RIGHT * 0.12), run_time=0.8)
        self.play(FadeIn(tests[1], shift=RIGHT * 0.12), run_time=0.8)
        wait_until(self, 24.0)
        self.play(FadeIn(tests[2], shift=UP * 0.10), run_time=0.9)
        wait_until(self, 30.5)
        self.play(FadeIn(degree_axis, shift=UP * 0.10), run_time=0.9)
        self.play(Indicate(degree_axis[3], color=CORAL), run_time=0.8)
        finish(self, 45.291)


class SeventeenPairingV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("先纠正：17−1=16 不是构造证明", "16 只是在固定一个顶点以后，剩余顶点的数量")
        counter = VGroup(
            label_card("9−1=8，但正九边形不可作", CORAL, 5.65, 0.29),
            label_card("15−1=14，但正十五边形可作", MINT, 5.65, 0.29),
        ).arrange(RIGHT, buff=0.46).move_to(UP * 1.90)
        center = LEFT * 3.35 + DOWN * 0.62
        radius = 1.78
        circle = Circle(radius=radius, color=BLUE, stroke_width=1.8).move_to(center)
        pts = polygon_points(17, radius, center, rotation=0)
        dots = VGroup(*[Dot(p, radius=0.040, color=MINT) for p in pts])
        fixed = Dot(pts[0], radius=0.085, color=INK)
        fixed_label = cn("先固定", 0.24, INK).next_to(fixed, RIGHT, buff=0.08)
        axis = Line(center + LEFT * 1.98, center + RIGHT * 1.98, color=MUTED, stroke_width=1.3)
        pairs = pair_projection_groups(17, radius, center, [MINT, BLUE, VIOLET, AMBER])

        info = panel(5.65, 4.42).to_edge(RIGHT, buff=0.48).shift(DOWN * 0.62)
        heading = card_heading(info, "16 个顶点怎样变成 8 个数？")
        process = VGroup(
            cn("关于横轴对称的两个顶点配成一对", 0.29, INK),
            cn("竖直分量抵消，只保留横向投影之和", 0.29, MUTED),
            equation_card(r"c_k=2\cos\frac{2\pi k}{17}", MINT, 4.75, 0.64),
            MathTex(r"c_1,c_2,\ldots,c_8", color=AMBER).scale(0.72),
            pill("目标仍然是 c1", CORAL, 2.85),
        ).arrange(DOWN, buff=0.25).next_to(heading, DOWN, buff=0.35).shift(UP * 0.16)

        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.9)
        self.play(FadeIn(counter[0], shift=DOWN * 0.10), FadeIn(counter[1], shift=DOWN * 0.10), run_time=1.0)
        wait_until(self, 17.4)
        self.play(Create(circle), Create(axis), FadeIn(dots), FadeIn(fixed), FadeIn(fixed_label), FadeIn(info), FadeIn(heading), run_time=1.2)
        self.play(dots[0].animate.set_opacity(0), run_time=0.4)
        wait_until(self, 23.8)
        for pair in pairs:
            self.play(FadeIn(pair, scale=1.04), run_time=0.35)
        self.play(FadeIn(process[0]), run_time=0.8)
        self.play(FadeIn(process[1]), Indicate(pairs, color=MINT), run_time=0.9)
        wait_until(self, 33.4)
        self.play(FadeIn(process[2], shift=RIGHT * 0.12), run_time=0.8)
        self.play(FadeIn(process[3], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 40.3)
        self.play(FadeIn(process[4], shift=UP * 0.10), run_time=0.8)
        finish(self, 41.820)


class SumProductBridgeV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("分组为什么能变成尺规步骤？", "不是看组数，而是要算出每两组的和与积")
        left = panel(5.40, 4.65).to_edge(LEFT, buff=0.48).shift(DOWN * 0.35)
        right = panel(6.10, 4.65).to_edge(RIGHT, buff=0.48).shift(DOWN * 0.35)
        lt = card_heading(left, "假设两数是 α、β")
        rt = card_heading(right, "和与积 → 二次方程 → 求根")
        givens = VGroup(
            equation_card(r"\alpha+\beta=s", BLUE, 4.45, 0.66),
            equation_card(r"\alpha\beta=p", AMBER, 4.45, 0.66),
        ).arrange(DOWN, buff=0.34).next_to(lt, DOWN, buff=0.55)
        expand = MathTex(r"(t-\alpha)(t-\beta)=t^2-st+p", color=INK).scale(0.64).next_to(givens, DOWN, buff=0.44)
        chain = VGroup(
            equation_card(r"t^2-st+p=0", VIOLET, 5.10, 0.72),
            Arrow(UP * 0.28, DOWN * 0.28, color=MUTED, stroke_width=2.0),
            equation_card(r"t=\frac{s\pm\sqrt{s^2-4p}}{2}", MINT, 5.10, 0.72),
        ).arrange(DOWN, buff=0.22).next_to(rt, DOWN, buff=0.42)
        ops = VGroup(
            tiny_op("+", "加减", BLUE),
            tiny_op(r"\times", "乘除", VIOLET),
            tiny_op(r"\sqrt{\ }", "开平方", AMBER),
        ).arrange(RIGHT, buff=0.62).move_to(right.get_bottom() + UP * 0.62)
        conclusion = pill("能算出和与积，才能真的用尺规把两根分开", MINT, 6.25).move_to(DOWN * 2.32)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(left), FadeIn(right), FadeIn(lt), FadeIn(rt), run_time=0.9)
        wait_until(self, 7.2)
        self.play(FadeIn(givens[0], shift=RIGHT * 0.12), FadeIn(givens[1], shift=RIGHT * 0.12), run_time=0.9)
        self.play(FadeIn(expand, shift=UP * 0.10), run_time=0.8)
        wait_until(self, 15.5)
        self.play(FadeIn(chain[0], shift=RIGHT * 0.12), run_time=0.8)
        self.play(GrowArrow(chain[1]), FadeIn(chain[2], shift=DOWN * 0.10), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(op, shift=UP * 0.10) for op in ops], lag_ratio=0.18), run_time=1.2)
        wait_until(self, 24.0)
        self.play(FadeIn(conclusion, shift=UP * 0.10), run_time=0.9)
        finish(self, 28.476)


class SeventeenGroupsV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("第一层分组从哪里来？", "下标不断乘 2，并把 k 与 17−k 视为同一对")
        chips = VGroup(*[c_chip(k, INK, 0.92) for k in range(1, 9)]).arrange(RIGHT, buff=0.30).move_to(UP * 1.70)
        top_cycle = VGroup(c_chip(1, MINT), c_chip(2, MINT), c_chip(4, MINT), c_chip(8, MINT)).arrange(RIGHT, buff=0.62).move_to(UP * 0.35)
        bottom_cycle = VGroup(c_chip(3, VIOLET), c_chip(6, VIOLET), c_chip(5, VIOLET), c_chip(7, VIOLET)).arrange(RIGHT, buff=0.62).move_to(DOWN * 1.05)
        top_arrows = VGroup(*[
            Arrow(top_cycle[i].get_right(), top_cycle[(i + 1) % 4].get_left(), buff=0.06, color=MINT, stroke_width=1.8)
            for i in range(3)
        ])
        bottom_arrows = VGroup(*[
            Arrow(bottom_cycle[i].get_right(), bottom_cycle[(i + 1) % 4].get_left(), buff=0.06, color=VIOLET, stroke_width=1.8)
            for i in range(3)
        ])
        top_loop = CurvedArrow(top_cycle[-1].get_top(), top_cycle[0].get_top(), angle=-TAU / 4, color=MINT, stroke_width=1.8)
        bottom_loop = CurvedArrow(bottom_cycle[-1].get_bottom(), bottom_cycle[0].get_bottom(), angle=TAU / 4, color=VIOLET, stroke_width=1.8)
        labels = VGroup(
            equation_card(r"A=c_1+c_2+c_4+c_8", MINT, 5.35, 0.64),
            equation_card(r"B=c_3+c_5+c_6+c_7", VIOLET, 5.35, 0.64),
        ).arrange(RIGHT, buff=0.55).move_to(DOWN * 2.16)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(chips, shift=DOWN * 0.10), run_time=0.9)
        wait_until(self, 10.5)
        self.play(TransformFromCopy(VGroup(chips[0], chips[1], chips[3], chips[7]), top_cycle), run_time=1.1)
        for arrow in top_arrows:
            self.play(GrowArrow(arrow), run_time=0.45)
        self.play(Create(top_loop), run_time=0.6)
        self.wait(1.0)
        self.play(TransformFromCopy(VGroup(chips[2], chips[5], chips[4], chips[6]), bottom_cycle), run_time=1.1)
        for arrow in bottom_arrows:
            self.play(GrowArrow(arrow), run_time=0.45)
        self.play(Create(bottom_loop), run_time=0.6)
        wait_until(self, 22.0)
        self.play(FadeIn(labels[0], shift=UP * 0.10), FadeIn(labels[1], shift=UP * 0.10), run_time=0.9)
        finish(self, 25.592)


class SeventeenFirstLayerV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("第一层：算出 A、B 的和与积", "每一个等号都可以从圆周对称或积化和差核对")
        left = panel(5.55, 4.95).to_edge(LEFT, buff=0.43).shift(DOWN * 0.28)
        right = panel(6.10, 4.95).to_edge(RIGHT, buff=0.43).shift(DOWN * 0.28)
        lt = card_heading(left, "先算和")
        rt = card_heading(right, "再算积")

        center = np.array([-3.55, -0.40, 0.0])
        radius = 1.50
        circle = Circle(radius=radius, color=BLUE, stroke_width=1.7).move_to(center)
        pts = polygon_points(17, radius, center, rotation=0)
        vectors = VGroup(*[
            Line(center, p, color=MUTED, stroke_width=1.0, stroke_opacity=0.55)
            for p in pts
        ])
        fixed = Dot(pts[0], radius=0.08, color=INK)
        sum_steps = VGroup(
            MathTex(r"1+A+B=0", color=AMBER).scale(0.67),
            MathTex(r"\boxed{A+B=-1}", color=MINT).scale(0.73),
        ).arrange(DOWN, buff=0.22).move_to(left.get_bottom() + UP * 0.75)

        identity = equation_card(r"c_i c_j=c_{i+j}+c_{i-j}", VIOLET, 5.20, 0.61).next_to(rt, DOWN, buff=0.36)
        product_tiles = VGroup(*[
            RoundedRectangle(width=0.48, height=0.34, corner_radius=0.06, stroke_color=MUTED, fill_color=MUTED, fill_opacity=0.10)
            for _ in range(16)
        ]).arrange_in_grid(rows=4, cols=4, buff=0.11).next_to(identity, DOWN, buff=0.30)
        product_label = cn("A×B 展开：16 个乘积", 0.27, MUTED).next_to(product_tiles, LEFT, buff=0.24)
        tallies = VGroup(*[
            VGroup(c_chip(k, [MINT, BLUE, VIOLET, AMBER][(k - 1) % 4], 0.55), MathTex(r"\times4", color=MUTED).scale(0.31)).arrange(DOWN, buff=0.05)
            for k in range(1, 9)
        ]).arrange(RIGHT, buff=0.08).move_to(right.get_bottom() + UP * 1.05)
        product_result = equation_card(r"AB=4(c_1+\cdots+c_8)=-4", AMBER, 5.35, 0.62).move_to(right.get_bottom() + UP * 0.36)
        final = VGroup(
            equation_card(r"t^2+t-4=0", MINT, 4.10, 0.70),
            equation_card(r"A,B=\frac{-1\pm\sqrt{17}}2", MINT, 5.30, 0.69),
            pill("两个根都能构造，并全部保留", AMBER, 4.35),
        ).arrange(DOWN, buff=0.28).move_to(DOWN * 0.20)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(left), FadeIn(right), FadeIn(lt), FadeIn(rt), run_time=0.9)
        self.play(Create(circle), FadeIn(vectors), FadeIn(fixed), run_time=1.1)
        self.play(FadeIn(sum_steps[0], shift=RIGHT * 0.12), run_time=0.8)
        self.play(FadeIn(sum_steps[1], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 13.6)
        self.play(FadeIn(identity, shift=RIGHT * 0.12), run_time=0.8)
        self.play(FadeIn(product_label), LaggedStart(*[FadeIn(tile) for tile in product_tiles], lag_ratio=0.04), run_time=1.2)
        self.wait(1.2)
        self.play(LaggedStart(*[FadeIn(tally, shift=UP * 0.08) for tally in tallies], lag_ratio=0.08), run_time=1.4)
        wait_until(self, 23.1)
        self.play(FadeIn(product_result, shift=UP * 0.10), run_time=0.9)
        wait_until(self, 27.8)
        old_content = VGroup(left, right, lt, rt, circle, vectors, fixed, sum_steps, identity, product_tiles, product_label, tallies, product_result)
        self.play(FadeOut(old_content), run_time=0.8)
        self.play(FadeIn(final[0], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 35.8)
        self.play(FadeIn(final[1], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 39.3)
        self.play(FadeIn(final[2], shift=UP * 0.10), run_time=0.7)
        finish(self, 49.144)


class SeventeenSecondLayerV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("第二层：每个四项组再拆成两个二项和", "仍然不是按外观切半，而是继续核对和与积")
        group_cards = VGroup(
            equation_card(r"C=c_1+c_4", MINT, 2.72, 0.57),
            equation_card(r"D=c_2+c_8", BLUE, 2.72, 0.57),
            equation_card(r"E=c_3+c_5", VIOLET, 2.72, 0.57),
            equation_card(r"F=c_6+c_7", AMBER, 2.72, 0.57),
        ).arrange(RIGHT, buff=0.34).move_to(UP * 1.80)
        left = panel(5.65, 3.95, MINT).to_edge(LEFT, buff=0.52).shift(DOWN * 0.70)
        right = panel(5.65, 3.95, VIOLET).to_edge(RIGHT, buff=0.52).shift(DOWN * 0.70)
        lt = card_heading(left, "A 这一组：C 与 D", MINT)
        rt = card_heading(right, "B 这一组：E 与 F", VIOLET)
        left_steps = VGroup(
            equation_card(r"C+D=A", MINT, 4.65, 0.60),
            equation_card(r"CD=-1", AMBER, 4.65, 0.60),
            cn("展开后 c1 到 c8 各出现一次", 0.27, MUTED),
            equation_card(r"t^2-At-1=0", MINT, 4.65, 0.66),
        ).arrange(DOWN, buff=0.22).next_to(lt, DOWN, buff=0.34)
        right_steps = VGroup(
            equation_card(r"E+F=B", VIOLET, 4.65, 0.60),
            equation_card(r"EF=-1", AMBER, 4.65, 0.60),
            cn("同样展开，八项各出现一次", 0.27, MUTED),
            equation_card(r"t^2-Bt-1=0", VIOLET, 4.65, 0.66),
        ).arrange(DOWN, buff=0.22).next_to(rt, DOWN, buff=0.34)
        result = pill("C、D、E、F 全部由第二层二次方程得到", MINT, 6.25).move_to(DOWN * 2.82)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(group_cards, shift=DOWN * 0.10), run_time=1.0)
        self.play(FadeIn(left), FadeIn(right), FadeIn(lt), FadeIn(rt), run_time=0.8)
        wait_until(self, 10.6)
        self.play(FadeIn(left_steps[0], shift=RIGHT * 0.10), FadeIn(right_steps[0], shift=RIGHT * 0.10), run_time=0.9)
        wait_until(self, 17.3)
        self.play(FadeIn(left_steps[1], shift=RIGHT * 0.10), FadeIn(right_steps[1], shift=RIGHT * 0.10), run_time=0.9)
        self.play(FadeIn(left_steps[2]), FadeIn(right_steps[2]), run_time=0.8)
        wait_until(self, 28.9)
        self.play(FadeIn(left_steps[3], shift=UP * 0.10), FadeIn(right_steps[3], shift=UP * 0.10), run_time=1.0)
        wait_until(self, 39.1)
        old_content = VGroup(group_cards, left, right, lt, rt, left_steps, right_steps)
        result.move_to(ORIGIN + DOWN * 0.10)
        self.play(FadeOut(old_content), FadeIn(result, shift=UP * 0.10), run_time=0.8)
        finish(self, 42.084)


class SeventeenThirdLayerV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("第三层：终于把目标 c1 单独分出来", "这一层的和来自 C，积正好来自已经得到的 E")
        known = VGroup(
            equation_card(r"C=c_1+c_4", MINT, 4.55, 0.68),
            equation_card(r"c_1c_4=c_5+c_3=E", VIOLET, 5.25, 0.66),
        ).arrange(DOWN, buff=0.35).move_to(LEFT * 3.25 + UP * 0.55)
        arrow = Arrow(LEFT * 0.38, RIGHT * 0.38, color=MUTED, stroke_width=2.3).move_to(ORIGIN + UP * 0.40)
        equation = VGroup(
            equation_card(r"t^2-Ct+E=0", AMBER, 4.70, 0.74),
            cn("两个根：c1 与 c4", 0.31, MUTED),
        ).arrange(DOWN, buff=0.28).move_to(RIGHT * 3.25 + UP * 0.50)
        root_order = VGroup(
            MathTex(r"0<\frac{2\pi}{17}<\frac{8\pi}{17}<\pi", color=INK).scale(0.64),
            cn("0 到 π 之间，cosine 随角度增大而减小", 0.30, MUTED),
            equation_card(r"\boxed{c_1=2\cos\frac{2\pi}{17}}", MINT, 5.50, 0.72),
        ).arrange(DOWN, buff=0.28).move_to(DOWN * 1.20)

        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)
        self.play(FadeIn(known[0], shift=RIGHT * 0.12), run_time=0.8)
        wait_until(self, 3.9)
        self.play(FadeIn(known[1], shift=RIGHT * 0.12), run_time=0.9)
        wait_until(self, 10.6)
        self.play(GrowArrow(arrow), FadeIn(equation[0], shift=RIGHT * 0.12), run_time=1.0)
        self.play(FadeIn(equation[1]), run_time=0.7)
        wait_until(self, 18.7)
        self.play(FadeIn(root_order[0], shift=UP * 0.10), FadeIn(root_order[1], shift=UP * 0.10), run_time=0.9)
        self.play(FadeIn(root_order[2], shift=UP * 0.10), run_time=0.9)
        finish(self, 29.539)


class CoordinateToVertexV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("三层方程怎样回到真实尺规？", "每一层都调用同一套四则运算与开平方构造")
        left = panel(5.65, 5.00).to_edge(LEFT, buff=0.42).shift(DOWN * 0.27)
        right = panel(5.95, 5.00).to_edge(RIGHT, buff=0.42).shift(DOWN * 0.27)
        lt = card_heading(left, "已知量逐层进入下一步")
        rt = card_heading(right, "最后把横坐标送回单位圆")
        stages = VGroup(
            equation_card(r"A,B", MINT, 2.25, 0.68),
            equation_card(r"C,E", BLUE, 2.25, 0.68),
            equation_card(r"c_1", VIOLET, 2.25, 0.68),
            equation_card(r"x=c_1/2", AMBER, 2.65, 0.66),
        ).arrange(DOWN, buff=0.27).next_to(lt, DOWN, buff=0.35)
        stage_arrows = VGroup(*[
            Arrow(stages[i].get_bottom(), stages[i + 1].get_top(), buff=0.05, color=MUTED, stroke_width=1.7)
            for i in range(3)
        ])
        op_tags = VGroup(
            MathTex(r"+,-,\times,\div,\sqrt{\ }", color=AMBER).scale(0.44).next_to(stage_arrows[0], RIGHT, buff=0.18),
            MathTex(r"+,-,\times,\div,\sqrt{\ }", color=AMBER).scale(0.44).next_to(stage_arrows[1], RIGHT, buff=0.18),
            MathTex(r"\div2", color=AMBER).scale(0.48).next_to(stage_arrows[2], RIGHT, buff=0.18),
        )

        center = np.array([3.55, -0.42, 0.0])
        radius = 1.78
        xvalue = np.cos(TAU / 17)
        point = center + radius * np.array([xvalue, np.sqrt(1 - xvalue**2), 0.0])
        foot = np.array([point[0], center[1], 0.0])
        circle = Circle(radius=radius, color=BLUE, stroke_width=2.0).move_to(center)
        axis = Arrow(center + LEFT * 2.04, center + RIGHT * 2.08, buff=0, color=MUTED, stroke_width=1.4)
        x_seg = Line(center, foot, color=AMBER, stroke_width=5.0)
        x_label = MathTex(r"x=c_1/2", color=AMBER).scale(0.56).next_to(x_seg, DOWN, buff=0.12)
        vertical = Line(foot, point, color=MINT, stroke_width=2.8)
        p_dot = Dot(point, radius=0.09, color=MINT)
        p_label = MathTex("P", color=MINT).scale(0.58).next_to(p_dot, UR, buff=0.08)
        start = center + RIGHT * radius
        start_dot = Dot(start, radius=0.085, color=INK)
        edge = Line(start, point, color=AMBER, stroke_width=5.0)
        edge_note = pill("这条弦就是一条精确边长", AMBER, 4.10).move_to(right.get_bottom() + UP * 0.50)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(left), FadeIn(right), FadeIn(lt), FadeIn(rt), run_time=0.9)
        self.play(FadeIn(stages[0], shift=DOWN * 0.10), run_time=0.7)
        for i in range(3):
            self.play(GrowArrow(stage_arrows[i]), FadeIn(stages[i + 1], shift=DOWN * 0.10), run_time=0.8)
            self.wait(0.75)
        self.play(LaggedStart(*[FadeIn(tag, shift=LEFT * 0.08) for tag in op_tags], lag_ratio=0.18), run_time=1.1)
        wait_until(self, 17.9)
        self.play(Create(circle), Create(axis), FadeIn(start_dot), run_time=1.0)
        self.play(Create(x_seg), FadeIn(x_label), run_time=0.8)
        wait_until(self, 22.4)
        self.play(Create(vertical), FadeIn(p_dot, scale=1.5), FadeIn(p_label), run_time=1.0)
        wait_until(self, 29.8)
        self.play(Create(edge), FadeIn(edge_note, shift=UP * 0.10), run_time=0.9)
        finish(self, 36.158)


class CopyChordV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("固定圆规开口，把同一条弦沿圆周复制", "首尾慢，中间加速；最后一个交点必须回到起点")
        center = DOWN * 0.30
        radius = 2.32
        alpha = TAU / 17
        points = polygon_points(17, radius, center, rotation=0)
        circle = Circle(radius=radius, color=BLUE, stroke_width=2.0).move_to(center)
        edge_len = np.linalg.norm(points[1] - points[0])
        compass = Circle(radius=edge_len, color=AMBER, stroke_width=2.0, stroke_opacity=0.62).move_to(points[0])
        edges = VGroup()
        dots = VGroup(Dot(points[0], radius=0.055, color=AMBER))
        chord_label = pill("圆规开口 = 已构造的弦长", AMBER, 4.25).move_to(DOWN * 2.92)
        self.play(FadeIn(title, shift=DOWN * 0.12), Create(circle), FadeIn(chord_label), run_time=0.8)
        self.play(Create(compass), FadeIn(dots[0]), run_time=0.55)
        for k in range(17):
            start = points[k]
            end = points[(k + 1) % 17]
            edge = Line(start, end, color=AMBER, stroke_width=3.0)
            dot = Dot(end, radius=0.055, color=AMBER)
            edges.add(edge)
            dots.add(dot)
            if k < 2 or k >= 15:
                rt = 0.42
            else:
                rt = 0.095
            self.play(compass.animate.move_to(start), Create(edge), FadeIn(dot, scale=1.35), run_time=rt, rate_func=linear)
        self.play(FadeOut(compass), Indicate(edges, color=AMBER, scale_factor=1.01), run_time=0.7)
        finish(self, 11.096)


class GeneralCriterionV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("最后再把两个案例推广成一般定理", "高斯—旺策尔判据放在这里，而不是拿来替代前面的推理")
        theorem = equation_card(r"n=2^k p_1p_2\cdots p_m", MINT, 6.10, 0.78).move_to(UP * 1.95)
        theorem_note = cn("p1、p2……是互不重复的费马素数", 0.32, MUTED).next_to(theorem, DOWN, buff=0.16)
        left = panel(5.70, 3.95, AMBER).to_edge(LEFT, buff=0.50).shift(DOWN * 0.78)
        right = panel(5.70, 3.95, VIOLET).to_edge(RIGHT, buff=0.50).shift(DOWN * 0.78)
        lt = card_heading(left, "费马素数是什么意思？", AMBER)
        rt = card_heading(right, "二的幂为什么出现？", VIOLET)
        fermat = VGroup(
            MathTex(r"p=2^{2^r}+1", color=AMBER).scale(0.72),
            cn("指数本身也是 2 的幂，结果还必须是素数", 0.27, MUTED),
            MathTex(r"3,\ 5,\ 17,\ 257,\ 65537", color=MINT).scale(0.62),
            pill("是否还有更多？目前未知", AMBER, 3.75),
        ).arrange(DOWN, buff=0.24).next_to(lt, DOWN, buff=0.35)

        c = np.array([3.55, -0.65, 0.0])
        radius = 1.28
        circle = Circle(radius=radius, color=BLUE, stroke_width=1.6).move_to(c)
        poly17 = polygon_group(17, radius * 0.96, c, AMBER, rotation=0, stroke_width=2.0, dot_radius=0.025)
        poly34 = polygon_group(34, radius * 0.96, c, MINT, rotation=0, stroke_width=1.7, dot_radius=0.017)
        bisection = VGroup(
            VGroup(MathTex(r"17\longrightarrow34", color=MINT).scale(0.60), cn("平分圆心角", 0.22, MUTED)).arrange(DOWN, buff=0.05),
            cn("每平分一次，边数乘 2", 0.29, MUTED),
        ).arrange(DOWN, buff=0.16).move_to(right.get_bottom() + UP * 0.62)
        scope = pill("一般必要性的完整证明还需要更多代数", CORAL, 5.75).move_to(DOWN * 0.10)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(theorem, shift=DOWN * 0.10), FadeIn(theorem_note), run_time=1.0)
        self.play(FadeIn(left), FadeIn(right), FadeIn(lt), FadeIn(rt), run_time=0.8)
        wait_until(self, 9.2)
        self.play(FadeIn(fermat[0], shift=RIGHT * 0.12), run_time=0.8)
        self.play(FadeIn(fermat[1]), run_time=0.7)
        wait_until(self, 17.9)
        self.play(FadeIn(fermat[2], shift=RIGHT * 0.12), run_time=0.9)
        wait_until(self, 25.5)
        self.play(FadeIn(fermat[3], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 28.8)
        self.play(Create(circle), FadeIn(poly17), run_time=1.0)
        self.play(ReplacementTransform(poly17, poly34), FadeIn(bisection, shift=UP * 0.10), run_time=1.2)
        wait_until(self, 36.7)
        old_content = VGroup(theorem, theorem_note, left, right, lt, rt, fermat, circle, poly34, bisection)
        self.play(FadeOut(old_content), run_time=0.7)
        self.play(FadeIn(scope, shift=UP * 0.10), run_time=0.9)
        finish(self, 50.285)


class FinalPayoffV5(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("真正的分界，不是边数大小", "而是目标坐标能不能一步步降到二次求解")
        left = panel(5.55, 4.35, CORAL).to_edge(LEFT, buff=0.58).shift(DOWN * 0.38)
        right = panel(5.55, 4.35, MINT).to_edge(RIGHT, buff=0.58).shift(DOWN * 0.38)
        lt = card_heading(left, "正七边形", CORAL)
        rt = card_heading(right, "正十七边形", MINT)
        seven = VGroup(
            equation_card(r"u^3+u^2-2u-1=0", CORAL, 4.65, 0.63),
            cn("没有有理根，三次式拆不开", 0.30, MUTED),
            pill("次数 3：尺规无法跨过", CORAL, 4.05),
        ).arrange(DOWN, buff=0.33).next_to(lt, DOWN, buff=0.45)
        seventeen = VGroup(
            equation_card(r"A,B", MINT, 2.15, 0.64),
            equation_card(r"C,E", BLUE, 2.15, 0.64),
            equation_card(r"c_1", VIOLET, 2.15, 0.64),
            pill("三层二次求解：尺规可执行", MINT, 4.25),
        ).arrange(DOWN, buff=0.20).next_to(rt, DOWN, buff=0.36)
        arrows = VGroup(*[
            Arrow(seventeen[i].get_bottom(), seventeen[i + 1].get_top(), buff=0.04, color=MUTED, stroke_width=1.6)
            for i in range(2)
        ])
        close = pill("难度由方程结构决定，不由边数决定", VIOLET, 5.75).move_to(DOWN * 0.10)
        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(left), FadeIn(right), FadeIn(lt), FadeIn(rt), run_time=0.9)
        self.play(FadeIn(seven[0], shift=RIGHT * 0.10), FadeIn(seventeen[0], shift=DOWN * 0.10), run_time=0.9)
        self.play(FadeIn(seven[1]), run_time=0.7)
        for i in range(2):
            self.play(GrowArrow(arrows[i]), FadeIn(seventeen[i + 1], shift=DOWN * 0.10), run_time=0.75)
        self.play(FadeIn(seven[2], shift=UP * 0.10), FadeIn(seventeen[3], shift=UP * 0.10), run_time=0.9)
        wait_until(self, 11.0)
        old_content = VGroup(left, right, lt, rt, seven, seventeen, arrows)
        self.play(FadeOut(old_content), run_time=0.7)
        self.play(FadeIn(close, shift=UP * 0.10), run_time=0.8)
        finish(self, 17.577)


class Constructible17GonCoverV5(StyledScene):
    """Standalone cover artwork; intentionally not sampled from the video timeline."""

    def construct(self) -> None:
        self.begin_scene()

        eyebrow = pill("尺规作图的真正门槛", VIOLET, 3.55).move_to(UP * 3.25)
        headline = cn("为什么正七边形比正十七边形更难画？", 0.69, INK).move_to(UP * 2.50)
        subhead = cn("边数更少，不代表方程更容易", 0.33, MUTED).move_to(UP * 1.91)

        left = panel(6.25, 4.22, CORAL).move_to(LEFT * 3.45 + DOWN * 0.45)
        right = panel(6.25, 4.22, MINT).move_to(RIGHT * 3.45 + DOWN * 0.45)

        left_center = np.array([-5.05, -0.34, 0.0])
        right_center = np.array([5.05, -0.34, 0.0])
        seven_circle = Circle(radius=1.30, color=MUTED, stroke_width=1.5, stroke_opacity=0.55).move_to(left_center)
        seven = polygon_group(7, 1.22, left_center, CORAL, rotation=PI / 2, stroke_width=3.4, dot_radius=0.055)
        seventeen_circle = Circle(radius=1.30, color=MUTED, stroke_width=1.5, stroke_opacity=0.55).move_to(right_center)
        seventeen = polygon_group(17, 1.22, right_center, MINT, rotation=PI / 2, stroke_width=2.6, dot_radius=0.030)

        seven_label = cn("正七边形", 0.39, CORAL).move_to([-2.02, 0.90, 0])
        seven_eq = equation_card(r"u^3+u^2-2u-1=0", CORAL, 3.25, 0.54).move_to([-2.02, 0.05, 0])
        seven_block = pill("次数 3 · 尺规跨不过", CORAL, 3.35).move_to([-2.02, -1.03, 0])

        seventeen_label = cn("正十七边形", 0.39, MINT).move_to([2.02, 1.31, 0])
        chain = VGroup(
            equation_card(r"A,B", MINT, 1.52, 0.54),
            equation_card(r"C,E", BLUE, 1.52, 0.54),
            equation_card(r"c_1", VIOLET, 1.52, 0.54),
        ).arrange(DOWN, buff=0.14).scale(0.82).move_to([1.93, -0.31, 0])
        chain_arrows = VGroup(*[
            Arrow(
                chain[i].get_bottom(),
                chain[i + 1].get_top(),
                buff=0.025,
                color=MUTED,
                stroke_width=1.7,
                max_tip_length_to_length_ratio=0.24,
            )
            for i in range(2)
        ])
        seventeen_ok = pill("三层二次 · 尺规可执行", MINT, 3.35).move_to([2.02, -1.67, 0])

        payoff = pill("难度由方程结构决定，不由边数决定", AMBER, 5.85).move_to(DOWN * 3.20)

        self.add(
            eyebrow,
            headline,
            subhead,
            left,
            right,
            seven_circle,
            seven,
            seventeen_circle,
            seventeen,
            seven_label,
            seven_eq,
            seven_block,
            seventeen_label,
            chain,
            chain_arrows,
            seventeen_ok,
            payoff,
        )
