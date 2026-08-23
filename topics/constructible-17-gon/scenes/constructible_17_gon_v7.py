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


class ChoiceRevealV7(StyledScene):
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
        intuition = pill("直觉：七条边应该更简单", BLUE, 4.40).move_to(DOWN * 2.80)
        verdict7 = pill("不能精确构造", CORAL, 3.20).next_to(left_circle, DOWN, buff=0.22)
        verdict17 = pill("能够精确构造", MINT, 3.20).next_to(right_circle, DOWN, buff=0.22)
        rule = VGroup(
            cn("精确 =", 0.30, MUTED),
            pill("直线", BLUE, 1.18),
            pill("圆", AMBER, 1.02),
            pill("交点", MINT, 1.18),
            cn("有限次", 0.30, MUTED),
        ).arrange(RIGHT, buff=0.16).move_to(DOWN * 2.78)
        question = pill("七边形卡在哪个方程？十七边形怎样拆成尺规步骤？", VIOLET, 7.35).move_to(DOWN * 2.78)

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
        finish(self, 33.246)


class CoordinateTaskV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("先把整张多边形缩成一个坐标", "固定右端起点，只找上半圆的相邻顶点 P")
        center = LEFT * 3.45 + DOWN * 0.22
        radius = 2.05
        alpha = TAU / 17
        circle = Circle(radius=radius, color=BLUE, stroke_width=2.0).move_to(center)
        x_axis = Arrow(
            center + LEFT * 2.62,
            center + RIGHT * 2.62,
            buff=0,
            color=MUTED,
            stroke_width=1.35,
            tip_length=0.13,
            max_tip_length_to_length_ratio=0.025,
        )
        y_axis = Arrow(
            center + DOWN * 2.52,
            center + UP * 2.52,
            buff=0,
            color=MUTED,
            stroke_width=1.35,
            tip_length=0.13,
            max_tip_length_to_length_ratio=0.025,
        )
        axis_labels = VGroup(
            MathTex("x", color=MUTED).scale(0.42).next_to(x_axis.get_end(), DOWN, buff=0.08),
            MathTex("y", color=MUTED).scale(0.42).next_to(y_axis.get_end(), LEFT, buff=0.08),
        )
        start = center + RIGHT * radius
        point = center + radius * np.array([np.cos(alpha), np.sin(alpha), 0.0])
        foot = np.array([point[0], center[1], 0.0])
        start_dot = Dot(start, radius=0.09, color=INK)
        start_label = cn("已知起点", 0.23, INK).next_to(start_dot, DR, buff=0.12)
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
        self.play(Create(x_axis), Create(y_axis), FadeIn(axis_labels), Create(circle), FadeIn(start_dot), FadeIn(start_label), run_time=1.2)
        self.play(FadeIn(p_dot, scale=1.5), FadeIn(p_label), FadeIn(steps[0], shift=RIGHT * 0.14), run_time=1.0)
        self.play(Create(x_seg), Create(vertical), FadeIn(x_label), FadeIn(steps[1], shift=RIGHT * 0.14), run_time=1.1)
        self.play(FadeIn(steps[2], shift=RIGHT * 0.14), Indicate(vertical, color=MINT), run_time=1.0)
        self.wait(1.4)
        self.play(FadeIn(conclusion, shift=UP * 0.10), Circumscribe(p_dot, color=AMBER), run_time=1.0)
        finish(self, 29.299)


class AddSubtractConstructionV7(AddSubtractConstructionV3):
    def construct(self) -> None:
        super().construct()
        finish(self, 11.666)


class ProductQuotientConstructionV7(ProductQuotientConstructionV3):
    def construct(self) -> None:
        super().construct()
        finish(self, 9.715)


class SquareRootIntersectionV7(SquareRootIntersectionV3):
    def construct(self) -> None:
        super().construct()
        finish(self, 13.103)


class WhyIntersectionsV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("尺规究竟怎样产生一个新点？", "前面证明了几种运算能做；现在检查它们是不是全部能力")
        left = panel(5.55, 4.65).to_edge(LEFT, buff=0.48).shift(DOWN * 0.34)
        right = panel(6.05, 4.65).to_edge(RIGHT, buff=0.48).shift(DOWN * 0.34)
        lt = card_heading(left, "已经证明：这些运算能做")
        rt = card_heading(right, "新点只能来自三类交点")
        operations = VGroup(
            tiny_op("+", "加减", BLUE),
            tiny_op(r"\times", "乘除", VIOLET),
            tiny_op(r"\sqrt{\ }", "开平方", AMBER),
        ).arrange(RIGHT, buff=0.70).next_to(lt, DOWN, buff=0.72)
        proof_gap = VGroup(
            cn("这只说明：它们做得到", 0.31, MUTED),
            pill("还要检查：新点坐标会不会超出这些运算", CORAL, 4.85),
        ).arrange(DOWN, buff=0.32).move_to(left.get_bottom() + UP * 1.12)

        row_y = [1.05, -0.15, -1.35]
        cases = VGroup()

        c1 = np.array([3.35, row_y[0], 0.0])
        ll_lines = VGroup(
            Line(c1 + LEFT * 1.00 + DOWN * 0.30, c1 + RIGHT * 1.00 + UP * 0.30, color=BLUE, stroke_width=2.1),
            Line(c1 + LEFT * 0.90 + UP * 0.34, c1 + RIGHT * 0.90 + DOWN * 0.34, color=VIOLET, stroke_width=2.1),
        )
        ll_hit = Dot(c1, radius=0.075, color=MINT)
        cases.add(VGroup(ll_lines, ll_hit, cn("两条直线", 0.25, INK).move_to([5.38, row_y[0], 0])))

        c2 = np.array([3.35, row_y[1], 0.0])
        lc_circle = Circle(radius=0.55, color=AMBER, stroke_width=2.0).move_to(c2)
        lc_line = Line(c2 + LEFT * 0.95 + DOWN * 0.20, c2 + RIGHT * 0.95 + UP * 0.20, color=BLUE, stroke_width=2.1)
        lc_hits = VGroup(Dot(c2 + np.array([-0.52, -0.11, 0]), radius=0.065, color=MINT), Dot(c2 + np.array([0.52, 0.11, 0]), radius=0.065, color=MINT))
        cases.add(VGroup(lc_circle, lc_line, lc_hits, cn("直线与圆", 0.25, INK).move_to([5.38, row_y[1], 0])))

        c3 = np.array([3.18, row_y[2], 0.0])
        cc = VGroup(
            Circle(radius=0.56, color=AMBER, stroke_width=2.0).move_to(c3 + LEFT * 0.28),
            Circle(radius=0.56, color=VIOLET, stroke_width=2.0).move_to(c3 + RIGHT * 0.28),
        )
        cc_hits = VGroup(Dot(c3 + UP * 0.48, radius=0.065, color=MINT), Dot(c3 + DOWN * 0.48, radius=0.065, color=MINT))
        cases.add(VGroup(cc, cc_hits, cn("两个圆", 0.25, INK).move_to([5.38, row_y[2], 0])))

        answer = pill("接下来检查：三类交点的坐标最高到几次方程？", MINT, 7.05).move_to(DOWN * 2.92)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(left), FadeIn(right), FadeIn(lt), FadeIn(rt), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(op, shift=UP * 0.10) for op in operations], lag_ratio=0.18), run_time=1.2)
        wait_until(self, 6.8)
        self.play(FadeIn(proof_gap[0]), run_time=0.7)
        self.play(FadeIn(proof_gap[1], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 12.5)
        for case in cases:
            self.play(Create(case[0]), FadeIn(case[1:]), run_time=0.85)
        wait_until(self, 22.4)
        self.play(FadeIn(answer, shift=UP * 0.10), run_time=0.9)
        finish(self, 29.978)


class ConstructionBoundaryV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("三类交点最高需要解几次方程？", "先从直线 x=C 与单位圆的真实交点开始")
        left = panel(5.70, 5.05).to_edge(LEFT, buff=0.40).shift(DOWN * 0.26)
        right = panel(5.92, 5.05).to_edge(RIGHT, buff=0.40).shift(DOWN * 0.26)
        lt = card_heading(left, "先回到顶点 P")
        rt = card_heading(right, "已知横坐标 C，怎样找到 P？")

        center = np.array([-3.52, -0.35, 0.0])
        radius = 1.72
        c_value = 0.70
        foot = center + RIGHT * radius * c_value
        hit_y = radius * np.sqrt(1 - c_value**2)
        top_hit = foot + UP * hit_y
        bottom_hit = foot + DOWN * hit_y
        circle = Circle(radius=radius, color=BLUE, stroke_width=2.1).move_to(center)
        x_axis = Line(center + LEFT * 2.02, center + RIGHT * 2.02, color=MUTED, stroke_width=1.25)
        y_axis = Line(center + DOWN * 2.02, center + UP * 2.02, color=MUTED, stroke_width=1.25)
        c_segment = Line(center, foot, color=AMBER, stroke_width=5.0)
        c_label = MathTex("C", color=AMBER).scale(0.56).next_to(c_segment, DOWN, buff=0.10)
        vertical = Line(foot + DOWN * 1.88, foot + UP * 1.88, color=MINT, stroke_width=2.7)
        vertical_label = MathTex("x=C", color=MINT).scale(0.56).next_to(vertical, RIGHT, buff=0.10).shift(DOWN * 0.42)
        hits = VGroup(Dot(top_hit, radius=0.085, color=AMBER), Dot(bottom_hit, radius=0.072, color=MUTED))
        p_label = MathTex("P", color=AMBER).scale(0.58).next_to(hits[0], UR, buff=0.08)

        steps = VGroup(
            equation_card(r"x^2+y^2=1", BLUE, 4.72, 0.66),
            equation_card(r"x=C", MINT, 4.72, 0.66),
            equation_card(r"C^2+y^2=1", AMBER, 4.72, 0.66),
            equation_card(r"y=\pm\sqrt{1-C^2}", VIOLET, 4.72, 0.68),
        ).arrange(DOWN, buff=0.20).next_to(rt, DOWN, buff=0.34)
        upper = label_card("P 在上半圆：取正号 y=+√(1−C²)", AMBER, 4.72, 0.27).move_to(steps[3])

        general = VGroup(
            label_card("一般直线与圆：把 y=mx+b 代入圆方程", BLUE, 8.65, 0.34),
            equation_card(r"ax^2+bx+c=0", MINT, 6.20, 0.86),
            label_card("两个圆：方程相减，平方项消掉，先化成一条直线", VIOLET, 8.65, 0.34),
            pill("每个新交点：最多再解一个二次方程", MINT, 7.20),
        ).arrange(DOWN, buff=0.30).move_to(DOWN * 0.12)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(left), FadeIn(right), FadeIn(lt), FadeIn(rt), run_time=0.9)
        self.play(Create(x_axis), Create(y_axis), Create(circle), run_time=1.0)
        self.play(Create(c_segment), FadeIn(c_label), Create(vertical), FadeIn(vertical_label), run_time=1.0)
        self.play(FadeIn(hits, scale=1.5), FadeIn(p_label), run_time=0.8)
        for step in steps:
            self.play(FadeIn(step, shift=RIGHT * 0.12), run_time=0.75)
            self.wait(1.15)
        self.play(ReplacementTransform(steps[3], upper), Indicate(hits[0], color=AMBER), run_time=0.9)
        wait_until(self, 17.8)
        specific = VGroup(left, right, lt, rt, circle, x_axis, y_axis, c_segment, c_label, vertical, vertical_label, hits, p_label, steps, upper)
        self.play(FadeOut(specific), run_time=0.7)
        wait_until(self, 19.0)
        self.play(FadeIn(general[0], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 23.8)
        self.play(FadeIn(general[1], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 29.3)
        self.play(FadeIn(general[2], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 35.6)
        self.play(FadeIn(general[3], shift=UP * 0.10), run_time=0.9)
        finish(self, 41.535)


class MinimalDegreeV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("怎样用方程次数检查一个坐标？", "尺规每步至多二次，目标数的最低次数因此受限")
        left = panel(5.75, 4.95).to_edge(LEFT, buff=0.42).shift(DOWN * 0.28)
        right = panel(5.90, 4.95).to_edge(RIGHT, buff=0.42).shift(DOWN * 0.28)
        lt = card_heading(left, "先找到次数最低、不能再拆的方程")
        rt = card_heading(right, "连续二次求解会留下什么次数？")

        target = VGroup(
            pill("目标横坐标 x", AMBER, 2.85),
            MathTex(r"\longrightarrow", color=MUTED).scale(0.48),
            pill("代入后等于 0 的有理系数方程", BLUE, 4.05),
        ).arrange(RIGHT, buff=0.22).move_to(UP * 0.22)

        sqrt2 = VGroup(
            MathTex(r"\sqrt2", color=BLUE).scale(0.76),
            MathTex(r"\longrightarrow", color=MUTED).scale(0.48),
            equation_card(r"x^2-2=0", BLUE, 2.70, 0.60),
        ).arrange(RIGHT, buff=0.24).move_to(left.get_center() + UP * 0.78)
        sqrt2_degree = pill("最低次数 = 2", BLUE, 3.05).move_to(left.get_center() + UP * 0.03)
        nested = VGroup(
            MathTex(r"\sqrt{1+\sqrt2}", color=VIOLET).scale(0.68),
            MathTex(r"\longrightarrow", color=MUTED).scale(0.48),
            equation_card(r"x^4-2x^2-1=0", VIOLET, 3.05, 0.55),
        ).arrange(RIGHT, buff=0.20).move_to(left.get_center() + DOWN * 0.82)
        nested_degree = pill("再套一层根号：次数 = 4", VIOLET, 4.05).move_to(left.get_center() + DOWN * 1.58)

        definition_left = VGroup(
            label_card("把目标数字代入，结果等于 0", BLUE, 4.85, 0.31),
            label_card("同一个数字可以满足很多方程", VIOLET, 4.85, 0.31),
        ).arrange(DOWN, buff=0.34).move_to(left)
        definition_right = VGroup(
            label_card("先挑次数最低的方程", AMBER, 4.85, 0.31),
            label_card("它不能再分出含目标数字的低次因式", MINT, 4.85, 0.28),
            pill("这个次数 = 最小多项式的次数", MINT, 4.85),
        ).arrange(DOWN, buff=0.28).move_to(right)

        tower = VGroup(
            label_card("从有理数出发", INK, 2.45, 0.29),
            label_card("解一个二次方程", BLUE, 2.72, 0.29),
            label_card("再解一个二次方程", VIOLET, 3.08, 0.29),
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
        note = pill("最低次数只能落在 1、2、4、8……这条序列里", AMBER, 6.15).move_to(DOWN * 3.08)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(target, shift=DOWN * 0.10), run_time=0.9)
        self.wait(1.2)
        self.play(FadeOut(target), run_time=0.5)
        self.play(FadeIn(left), FadeIn(right), FadeIn(lt), FadeIn(rt), run_time=0.8)
        self.play(FadeIn(definition_left[0], shift=RIGHT * 0.10), FadeIn(definition_right[0], shift=LEFT * 0.10), run_time=0.8)
        self.play(FadeIn(definition_left[1], shift=RIGHT * 0.10), FadeIn(definition_right[1], shift=LEFT * 0.10), run_time=0.8)
        self.play(FadeIn(definition_right[2], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 17.2)
        self.play(FadeOut(definition_left), FadeOut(definition_right), run_time=0.6)
        self.play(FadeIn(sqrt2, shift=RIGHT * 0.12), run_time=1.0)
        self.play(FadeIn(sqrt2_degree, shift=UP * 0.10), run_time=0.7)
        wait_until(self, 25.0)
        self.play(FadeIn(nested, shift=RIGHT * 0.12), run_time=1.0)
        self.play(FadeIn(nested_degree, shift=UP * 0.10), run_time=0.7)
        wait_until(self, 33.2)
        self.play(FadeIn(tower[0]), run_time=0.6)
        for i in range(2):
            self.play(GrowArrow(arrows[i]), FadeIn(mult[i]), FadeIn(tower[i + 1], shift=DOWN * 0.10), run_time=0.9)
            self.wait(0.8)
        self.play(FadeIn(chain, shift=UP * 0.10), run_time=0.8)
        wait_until(self, 47.0)
        self.play(FadeIn(note, shift=UP * 0.10), Indicate(chain, color=MINT), run_time=0.9)
        finish(self, 54.090)


class NecessaryNotSufficientV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("次数条件只能先排除，不能自动证明成功", "不是 2 的幂一定失败；是 2 的幂仍要给出实际求解步骤")
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
        finish(self, 13.663)


class HeptagonSetupV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("正七边形：c_k 到底表示什么？", "先把一对上下对称箭头的两个横向分量相加")
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
        pair_visuals = VGroup()
        pair_labels = VGroup()
        projection_segments = VGroup()
        for k in range(1, 4):
            upper, lower = pts[k], pts[7 - k]
            color = pair_colors[k - 1]
            foot = np.array([upper[0], center[1], 0.0])
            guides = VGroup(
                DashedLine(upper, foot, color=color, stroke_width=1.4, dash_length=0.09),
                DashedLine(lower, foot, color=color, stroke_width=1.4, dash_length=0.09),
            )
            projections = VGroup(
                Line(center + UP * 0.09, foot + UP * 0.09, color=color, stroke_width=4.0),
                Line(center + DOWN * 0.09, foot + DOWN * 0.09, color=color, stroke_width=4.0),
            )
            projection_segments.add(projections)
            pair_visuals.add(VGroup(guides, projections))
            direction = DOWN if k == 1 else UP
            pair_labels.add(MathTex(rf"c_{k}", color=color).scale(0.49).next_to(foot, direction, buff=0.14))

        info = panel(5.55, 5.08).to_edge(RIGHT, buff=0.42).shift(DOWN * 0.25)
        heading = card_heading(info, "先慢看相邻的这一对")
        component_note = VGroup(
            MathTex(r"\cos\theta", color=MINT).scale(0.55),
            cn("上方箭头的横向分量", 0.27, MUTED),
            MathTex(r"\cos(-\theta)=\cos\theta", color=MINT).scale(0.53),
            cn("下方箭头的横向分量相同", 0.27, MUTED),
        ).arrange(DOWN, buff=0.15).next_to(heading, DOWN, buff=0.34)
        pair_formula = equation_card(r"c_1=\cos\theta+\cos(-\theta)=2\cos\theta", MINT, 4.78, 0.56).next_to(component_note, DOWN, buff=0.30)
        definition = equation_card(r"c_k=2\cos\frac{2\pi k}{7}", BLUE, 4.65, 0.63).next_to(pair_formula, DOWN, buff=0.24)
        target = pill("相邻这一对：u=c1", CORAL, 3.60).move_to(info.get_bottom() + UP * 0.48)

        sum_heading = card_heading(info, "七支箭头的横向分量相加")
        contributions = VGroup(
            equation_card(r"1", INK, 0.92, 0.55),
            equation_card(r"c_1", MINT, 1.00, 0.52),
            equation_card(r"c_2", AMBER, 1.00, 0.52),
            equation_card(r"c_3", VIOLET, 1.00, 0.52),
        ).arrange(RIGHT, buff=0.16).next_to(sum_heading, DOWN, buff=0.52)
        vector_note = VGroup(
            cn("七支单位箭头完全对称，向量和为 0", 0.29, MUTED),
            cn("竖直分量成对抵消，横向分量保留下来", 0.29, INK),
        ).arrange(DOWN, buff=0.20).next_to(contributions, DOWN, buff=0.42)
        sum_card = equation_card(r"1+c_1+c_2+c_3=0", AMBER, 4.75, 0.70).next_to(vector_note, DOWN, buff=0.38)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(info), FadeIn(heading), run_time=0.9)
        self.play(Create(circle), Create(x_axis), FadeIn(dots), FadeIn(fixed), FadeIn(arrows), run_time=1.0)
        wait_until(self, 4.2)
        self.play(arrows[1].animate.set_color(MINT).set_stroke(width=3.0), arrows[6].animate.set_color(MINT).set_stroke(width=3.0), run_time=0.8)
        self.play(Create(pair_visuals[0][0]), Create(pair_visuals[0][1]), run_time=1.0)
        self.play(FadeIn(component_note[0]), FadeIn(component_note[1]), run_time=0.7)
        self.play(FadeIn(component_note[2]), FadeIn(component_note[3]), run_time=0.7)
        wait_until(self, 11.0)
        self.play(TransformFromCopy(projection_segments[0], pair_formula), FadeIn(pair_labels[0]), run_time=0.9)
        wait_until(self, 16.7)
        self.play(FadeIn(definition, shift=RIGHT * 0.12), run_time=0.8)
        wait_until(self, 21.0)
        self.play(FadeIn(target, shift=UP * 0.10), run_time=0.7)

        wait_until(self, 25.4)
        first_content = VGroup(heading, component_note, pair_formula, definition, target)
        self.play(FadeOut(first_content), FadeIn(sum_heading), run_time=0.7)
        self.play(arrows[0].animate.set_color(INK).set_stroke(width=3.0), TransformFromCopy(arrows[0], contributions[0]), run_time=0.8)
        self.play(TransformFromCopy(pair_labels[0], contributions[1]), run_time=0.65)
        for i in range(1, 3):
            k = i + 1
            self.play(
                arrows[k].animate.set_color(pair_colors[i]).set_stroke(width=2.7),
                arrows[7 - k].animate.set_color(pair_colors[i]).set_stroke(width=2.7),
                Create(pair_visuals[i][0]),
                Create(pair_visuals[i][1]),
                FadeIn(pair_labels[i]),
                run_time=0.9,
            )
            self.play(TransformFromCopy(pair_labels[i], contributions[i + 1]), run_time=0.6)
        wait_until(self, 35.8)
        self.play(FadeIn(vector_note[0]), run_time=0.7)
        self.play(FadeIn(vector_note[1]), Indicate(projection_segments, color=MINT), run_time=0.8)
        wait_until(self, 40.2)
        self.play(FadeIn(sum_card, shift=UP * 0.10), run_time=0.9)
        finish(self, 44.879)


class HeptagonIdentityV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("为什么要把两个 c 的乘积改写成和？", "目标是把 c2、c3 改写成只含 u 的式子")
        purpose = VGroup(
            equation_card(r"1+u+c_2+c_3=0", AMBER, 4.85, 0.68),
            Arrow(LEFT * 0.36, RIGHT * 0.36, color=MUTED, stroke_width=2.1),
            VGroup(c_chip(2, BLUE, 1.05), c_chip(3, VIOLET, 1.05)).arrange(RIGHT, buff=0.18),
        ).arrange(RIGHT, buff=0.32).move_to(UP * 0.55)
        purpose_note = VGroup(
            cn("要让圆周关系里只剩 u，就要算出 c2、c3", 0.34, INK),
            pill("计算会出现 c 的乘积：先把乘积变回 c 的和", MINT, 6.35),
        ).arrange(DOWN, buff=0.38).move_to(DOWN * 1.15)

        derivation_title = title_group("积化和差从哪里来？", "把和角、差角公式相加，让符号相反的正弦项抵消")
        derivation_box = panel(11.75, 3.65).move_to(UP * 0.25)
        sum_formula = MathTex(
            r"\cos(a+b)", "=", r"\cos a\cos b", "-", r"\sin a\sin b",
            color=INK,
        ).scale(0.66).move_to(UP * 1.05)
        diff_formula = MathTex(
            r"\cos(a-b)", "=", r"\cos a\cos b", "+", r"\sin a\sin b",
            color=INK,
        ).scale(0.66).move_to(UP * 0.10)
        sum_formula[4].set_color(CORAL)
        diff_formula[4].set_color(MINT)
        add_mark = MathTex("+", color=AMBER).scale(0.72).next_to(diff_formula, LEFT, buff=0.28)
        divider = Line(LEFT * 4.45, RIGHT * 4.45, color=MUTED, stroke_width=1.2).move_to(DOWN * 0.42)
        trig_result = MathTex(r"\cos(a+b)+\cos(a-b)=2\cos a\cos b", color=AMBER).scale(0.72).move_to(DOWN * 1.02)
        cancel_marks = VGroup(Cross(sum_formula[4], stroke_color=CORAL, stroke_width=2.3), Cross(diff_formula[4], stroke_color=MINT, stroke_width=2.3))
        c_substitution = equation_card(r"a=i\theta,\quad b=j\theta", BLUE, 4.30, 0.60).move_to(LEFT * 3.0 + DOWN * 2.34)
        c_identity = equation_card(r"\boxed{c_i c_j=c_{i+j}+c_{i-j}}", MINT, 5.65, 0.68).move_to(RIGHT * 3.0 + DOWN * 2.34)

        example_title = title_group("先用一个具体例子核对下标", "c1×c2 会落到 3 和 −1 两个方向")
        ring_center = LEFT * 3.45 + DOWN * 0.48
        ring_radius = 1.58
        slot_points = [
            ring_center + ring_radius * np.array([np.cos(TAU * k / 7), np.sin(TAU * k / 7), 0.0])
            for k in range(7)
        ]
        ring = Circle(radius=ring_radius, color=MUTED, stroke_width=1.4).move_to(ring_center)
        slots = VGroup(*[
            VGroup(
                Circle(radius=0.23, stroke_color=BLUE, fill_color=BLUE, fill_opacity=0.14),
                MathTex("-1" if k == 6 else str(k), color=INK).scale(0.38),
            ).move_to(slot_points[k])
            for k in range(7)
        ])
        input_rays = VGroup(Line(ring_center, slot_points[1], color=MINT, stroke_width=3.0), Line(ring_center, slot_points[2], color=BLUE, stroke_width=3.0))
        output_rays = VGroup(Line(ring_center, slot_points[3], color=VIOLET, stroke_width=3.0), Line(ring_center, slot_points[6], color=AMBER, stroke_width=3.0))
        example_panel = panel(5.72, 4.55).to_edge(RIGHT, buff=0.48).shift(DOWN * 0.43)
        example_heading = card_heading(example_panel, "把乘积送回同一组 c")
        example_steps = VGroup(
            equation_card(r"c_1c_2", BLUE, 4.60, 0.62),
            equation_card(r"=c_3+c_{-1}", VIOLET, 4.60, 0.62),
            equation_card(r"=c_3+c_1", MINT, 4.60, 0.62),
        ).arrange(DOWN, buff=0.18).next_to(example_heading, DOWN, buff=0.24)
        wrap_info = label_card("下标负 1 与 1 关于横轴对称，所以余弦相同", AMBER, 4.85, 0.27).move_to(example_panel.get_bottom() + UP * 0.42)
        symmetry = DashedLine(slot_points[1], slot_points[6], color=MINT, stroke_width=2.0)
        extra_wrap = VGroup(
            equation_card(r"c_8=c_1", AMBER, 2.55, 0.58),
            cn("下标绕圆一周，方向不变", 0.27, MUTED),
        ).arrange(RIGHT, buff=0.28).move_to(DOWN * 2.90)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(purpose, shift=DOWN * 0.10), run_time=0.9)
        self.play(FadeIn(purpose_note[0]), run_time=0.7)
        self.play(FadeIn(purpose_note[1], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 13.6)
        self.play(FadeOut(VGroup(title, purpose, purpose_note)), FadeIn(derivation_title), FadeIn(derivation_box), run_time=0.8)
        self.play(FadeIn(sum_formula, shift=RIGHT * 0.12), run_time=0.8)
        self.play(FadeIn(diff_formula, shift=RIGHT * 0.12), FadeIn(add_mark), run_time=0.8)
        wait_until(self, 24.0)
        self.play(Create(cancel_marks), run_time=0.8)
        self.play(sum_formula[4].animate.set_opacity(0.20), diff_formula[4].animate.set_opacity(0.20), run_time=0.7)
        self.play(Create(divider), FadeIn(trig_result, shift=UP * 0.10), run_time=0.9)
        wait_until(self, 34.2)
        self.play(FadeIn(c_substitution, shift=RIGHT * 0.10), run_time=0.8)
        self.play(TransformFromCopy(trig_result, c_identity), run_time=0.9)

        wait_until(self, 42.0)
        derivation = VGroup(derivation_title, derivation_box, sum_formula, diff_formula, add_mark, divider, trig_result, cancel_marks, c_substitution, c_identity)
        self.play(FadeOut(derivation), FadeIn(example_title), FadeIn(example_panel), FadeIn(example_heading), run_time=0.8)
        self.play(Create(ring), FadeIn(slots), Create(input_rays), FadeIn(example_steps[0], shift=RIGHT * 0.10), run_time=0.9)
        wait_until(self, 47.0)
        self.play(Create(output_rays), FadeIn(example_steps[1], shift=RIGHT * 0.10), Indicate(slots[3], color=VIOLET), Indicate(slots[6], color=AMBER), run_time=0.9)
        self.play(Create(symmetry), FadeIn(example_steps[2], shift=RIGHT * 0.10), run_time=0.8)
        self.play(FadeIn(wrap_info, shift=UP * 0.10), run_time=0.7)
        wait_until(self, 55.0)
        self.play(FadeIn(extra_wrap, shift=UP * 0.10), run_time=0.8)
        finish(self, 59.320)


class HeptagonPowersV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("用刚才的公式计算 u² 和 u³", "每行都能沿着 c 的下标核对")
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
        for row in left_steps:
            self.play(FadeIn(row, shift=RIGHT * 0.14), run_time=0.75)
            self.wait(0.75)
        self.play(GrowArrow(flow), run_time=0.7)
        for row in right_steps:
            self.play(FadeIn(row, shift=RIGHT * 0.14), run_time=0.75)
            self.wait(0.80)
        self.play(Indicate(left_steps[-1], color=BLUE), Indicate(right_steps[-1], color=AMBER), run_time=0.9)
        finish(self, 17.862)


class HeptagonCubicV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("把 c2、c3 换成 u 后得到什么方程？", "逐项代入，先得到一个需要继续检验的三次方程")
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
        finish(self, 15.526)


class HeptagonIrreducibleV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        graph_title = title_group("图像有 3 个零点，为什么还要检查有理根？", "有实数根，不等于其中有有理数")
        graph_panel = panel(7.20, 4.72).to_edge(LEFT, buff=0.40).shift(DOWN * 0.38)
        info_panel = panel(4.72, 4.72).to_edge(RIGHT, buff=0.40).shift(DOWN * 0.38)
        axes = Axes(
            x_range=[-2.2, 1.6, 1],
            y_range=[-2.4, 2.4, 1],
            x_length=5.70,
            y_length=3.28,
            axis_config={"color": MUTED, "stroke_width": 1.25, "include_tip": False},
        ).move_to(graph_panel).shift(DOWN * 0.18)
        curve = axes.plot(lambda x: x**3 + x**2 - 2 * x - 1, x_range=[-2.15, 1.55], color=CORAL, stroke_width=3.0)
        root_values = [-1.801937736, -0.445041868, 1.246979604]
        root_colors = [VIOLET, BLUE, MINT]
        root_dots = VGroup(*[Dot(axes.c2p(value, 0), radius=0.075, color=color) for value, color in zip(root_values, root_colors)])
        root_labels = VGroup(
            MathTex(r"-1.802", color=VIOLET).scale(0.38).next_to(root_dots[0], DOWN, buff=0.12),
            MathTex(r"-0.445", color=BLUE).scale(0.38).next_to(root_dots[1], UP, buff=0.12),
            MathTex(r"u=c_1\approx1.247", color=MINT).scale(0.40).next_to(root_dots[2], DOWN, buff=0.12),
        )
        graph_formula = equation_card(r"f(u)=u^3+u^2-2u-1", CORAL, 4.15, 0.63).move_to(info_panel.get_top() + DOWN * 0.72)
        root_count = pill("图像结论：有 3 个实数根", MINT, 4.05).next_to(graph_formula, DOWN, buff=0.42)
        target_root = pill("右侧正根就是目标 u", BLUE, 3.65).next_to(root_count, DOWN, buff=0.28)
        rational_question = label_card("下一问：其中有没有有理数？", AMBER, 4.08, 0.29).move_to(info_panel.get_bottom() + UP * 0.62)

        factor_title = title_group("为什么有理根决定能否分解？", "讨论范围：因式的系数都必须是有理数")
        factor_panel = panel(11.30, 4.45).move_to(DOWN * 0.42)
        degree_split = VGroup(
            MathTex(r"3=1+2", color=AMBER).scale(0.78),
            cn("三次式如果能分解，只能出现一次因式", 0.30, MUTED),
        ).arrange(DOWN, buff=0.16).move_to(factor_panel.get_top() + DOWN * 0.72)
        factor = equation_card(r"f(u)=(u-r)(u^2+au+b)", BLUE, 5.20, 0.66).move_to(LEFT * 2.75 + DOWN * 0.55)
        factor_note = cn("a、b、r 都是有理数", 0.27, MUTED).next_to(factor, DOWN, buff=0.12)
        role_arrow = Arrow(LEFT * 0.46, RIGHT * 0.46, color=MUTED, stroke_width=2.2).move_to(DOWN * 0.55)
        root = equation_card(r"f(r)=0", MINT, 2.70, 0.70).move_to(RIGHT * 3.15 + DOWN * 0.55)
        factor_result = pill("没有有理根 → 不能在有理数系数范围内分解", CORAL, 6.85).move_to(factor_panel.get_bottom() + UP * 0.55)

        substitute_title = title_group("候选值怎样从这个方程里算出来？", "把最简分数代入，再一次消掉全部分母")
        substitute_panel = panel(11.55, 4.48).move_to(DOWN * 0.42)
        fraction = VGroup(
            equation_card(r"r=\frac pq", BLUE, 2.50, 0.72),
            MathTex(r"\gcd(p,q)=1,\quad q>0", color=MUTED).scale(0.54),
        ).arrange(RIGHT, buff=0.35).move_to(substitute_panel.get_top() + DOWN * 0.62)
        substitution = equation_card(r"f\!\left(\frac pq\right)=0", AMBER, 4.30, 0.69).move_to(UP * 0.20)
        clear_note = pill("两边同乘 q³", MINT, 2.85).move_to(DOWN * 0.72)
        cleared = equation_card(r"p^3+p^2q-2pq^2-q^3=0", INK, 7.25, 0.70).move_to(DOWN * 1.70)

        divide_title = title_group("同一个等式，向两边各整理一次", "互质意味着分子、分母不能再共享任何质因子")
        divide_left = panel(5.70, 4.45, BLUE).to_edge(LEFT, buff=0.48).shift(DOWN * 0.42)
        divide_right = panel(5.70, 4.45, VIOLET).to_edge(RIGHT, buff=0.48).shift(DOWN * 0.42)
        left_steps = VGroup(
            equation_card(r"p^3=q(-p^2+2pq+q^2)", BLUE, 4.90, 0.56),
            equation_card(r"q\mid p^3", BLUE, 3.10, 0.68),
            pill("p、q 互质 → q=1", MINT, 3.65),
        ).arrange(DOWN, buff=0.30).move_to(divide_left)
        right_steps = VGroup(
            equation_card(r"q^3=p(p^2+pq-2q^2)", VIOLET, 4.90, 0.56),
            equation_card(r"p\mid q^3", VIOLET, 3.10, 0.68),
            pill("p、q 互质 → p=±1", AMBER, 3.75),
        ).arrange(DOWN, buff=0.30).move_to(divide_right)
        theorem_note = pill("这就是有理根检验在本题里的推导", INK, 5.55).move_to(DOWN * 3.12)

        final_title = title_group("有 3 个实数根，但没有有理根", "“能不能拆开”必须注明所用系数的范围")
        tests_panel = panel(5.65, 4.55, CORAL).to_edge(LEFT, buff=0.48).shift(DOWN * 0.42)
        range_panel = panel(5.65, 4.55, MINT).to_edge(RIGHT, buff=0.48).shift(DOWN * 0.42)
        tests = VGroup(
            equation_card(r"f(1)=-1\ne0", CORAL, 4.55, 0.62),
            equation_card(r"f(-1)=1\ne0", CORAL, 4.55, 0.62),
            pill("3 个实数根全部是无理数", CORAL, 4.35),
        ).arrange(DOWN, buff=0.30).move_to(tests_panel)
        range_cards = VGroup(
            label_card("实数范围：可写成 3 个一次因式", MINT, 4.80, 0.27),
            label_card("有理数系数：不能分解", CORAL, 4.80, 0.29),
            VGroup(
                pill("最小多项式次数", AMBER, 2.55),
                MathTex(r"3\notin\{1,2,4,8,\ldots\}", color=AMBER).scale(0.62),
            ).arrange(DOWN, buff=0.16),
        ).arrange(DOWN, buff=0.28).move_to(range_panel)

        self.play(FadeIn(graph_title, shift=DOWN * 0.12), FadeIn(graph_panel), FadeIn(info_panel), FadeIn(graph_formula), Create(axes), run_time=0.9)
        self.play(Create(curve), run_time=1.1)
        self.play(LaggedStart(*[FadeIn(dot, scale=1.4) for dot in root_dots], lag_ratio=0.22), FadeIn(root_labels), run_time=1.2)
        self.play(FadeIn(root_count, shift=UP * 0.10), FadeIn(target_root, shift=UP * 0.10), run_time=0.8)
        wait_until(self, 7.2)
        self.play(FadeIn(rational_question, shift=UP * 0.10), run_time=0.8)

        wait_until(self, 12.1)
        graph_group = VGroup(graph_title, graph_panel, info_panel, axes, curve, root_dots, root_labels, graph_formula, root_count, target_root, rational_question)
        self.play(FadeOut(graph_group), FadeIn(factor_title), FadeIn(factor_panel), FadeIn(degree_split), run_time=0.8)
        wait_until(self, 19.9)
        self.play(FadeIn(factor, shift=RIGHT * 0.12), FadeIn(factor_note), run_time=0.8)
        wait_until(self, 27.0)
        self.play(GrowArrow(role_arrow), TransformFromCopy(factor, root), run_time=0.9)
        wait_until(self, 33.0)
        self.play(FadeIn(factor_result, shift=UP * 0.10), run_time=0.8)

        wait_until(self, 33.9)
        factor_group = VGroup(factor_title, factor_panel, degree_split, factor, factor_note, role_arrow, root, factor_result)
        self.play(FadeOut(factor_group), FadeIn(substitute_title), FadeIn(substitute_panel), FadeIn(fraction, shift=RIGHT * 0.10), run_time=0.8)
        wait_until(self, 39.2)
        self.play(FadeIn(substitution, shift=RIGHT * 0.10), run_time=0.8)
        self.play(FadeIn(clear_note, shift=UP * 0.08), FadeIn(cleared, shift=DOWN * 0.08), run_time=0.8)

        wait_until(self, 50.9)
        substitute_group = VGroup(substitute_title, substitute_panel, fraction, substitution, clear_note, cleared)
        self.play(FadeOut(substitute_group), FadeIn(divide_title), FadeIn(divide_left), FadeIn(divide_right), run_time=0.8)
        self.play(FadeIn(left_steps[0], shift=RIGHT * 0.10), run_time=0.8)
        self.play(FadeIn(left_steps[1], shift=UP * 0.08), run_time=0.7)
        wait_until(self, 57.0)
        self.play(FadeIn(left_steps[2], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 59.8)
        self.play(FadeIn(right_steps[0], shift=RIGHT * 0.10), run_time=0.8)
        self.play(FadeIn(right_steps[1], shift=UP * 0.08), run_time=0.7)
        wait_until(self, 65.9)
        self.play(FadeIn(right_steps[2], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 68.8)
        self.play(FadeIn(theorem_note, shift=UP * 0.10), run_time=0.8)

        wait_until(self, 69.1)
        divide_group = VGroup(divide_title, divide_left, divide_right, left_steps, right_steps, theorem_note)
        self.play(FadeOut(divide_group), FadeIn(final_title), FadeIn(tests_panel), FadeIn(range_panel), run_time=0.8)
        self.play(FadeIn(tests[0], shift=RIGHT * 0.10), FadeIn(tests[1], shift=RIGHT * 0.10), run_time=0.9)
        wait_until(self, 76.0)
        self.play(FadeIn(tests[2], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 80.1)
        self.play(FadeIn(range_cards[0], shift=UP * 0.10), run_time=0.8)
        self.play(FadeIn(range_cards[1], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 87.1)
        self.play(FadeIn(range_cards[2], shift=UP * 0.10), run_time=0.9)
        self.play(Indicate(range_cards[2][1], color=AMBER), run_time=0.8)
        finish(self, 95.757)


class SeventeenPairingV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("先纠正：17−1=16 不是构造证明", "16 只是在固定一个顶点以后，用来计算剩余顶点")
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
        heading = card_heading(info, "十六个顶点怎样变成八个数？")
        process = VGroup(
            cn("关于横轴对称的两个顶点配成一对", 0.29, INK),
            cn("竖直分量抵消，只保留横向投影之和", 0.29, MUTED),
            equation_card(r"c_k=2\cos\frac{2\pi k}{17}", MINT, 4.75, 0.64),
            MathTex(r"c_1,c_2,\ldots,c_8", color=AMBER).scale(0.72),
            pill("目标仍然是 c1", CORAL, 2.85),
        ).arrange(DOWN, buff=0.25).next_to(heading, DOWN, buff=0.35).shift(UP * 0.16)

        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.9)
        self.play(FadeIn(counter[0], shift=DOWN * 0.10), FadeIn(counter[1], shift=DOWN * 0.10), run_time=1.0)
        wait_until(self, 15.4)
        self.play(Create(circle), Create(axis), FadeIn(dots), FadeIn(fixed), FadeIn(fixed_label), FadeIn(info), FadeIn(heading), run_time=1.2)
        self.play(dots[0].animate.set_opacity(0), run_time=0.4)
        wait_until(self, 18.8)
        for pair in pairs:
            self.play(FadeIn(pair, scale=1.04), run_time=0.35)
        self.play(FadeIn(process[0]), run_time=0.8)
        self.play(FadeIn(process[1]), Indicate(pairs, color=MINT), run_time=0.9)
        wait_until(self, 24.2)
        self.play(FadeIn(process[2], shift=RIGHT * 0.12), run_time=0.8)
        self.play(FadeIn(process[3], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 29.0)
        self.play(FadeIn(process[4], shift=UP * 0.10), run_time=0.8)
        finish(self, 33.443)


class SumProductBridgeV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("知道两个数的和与积，为什么就能分别求出它们？", "它们正好是一个二次方程的两个根")
        left = panel(5.40, 4.65).to_edge(LEFT, buff=0.48).shift(DOWN * 0.35)
        right = panel(6.10, 4.65).to_edge(RIGHT, buff=0.48).shift(DOWN * 0.35)
        lt = card_heading(left, "假设两个数是 α、β")
        rt = card_heading(right, "和与积 → 二次方程 → 两个根")
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
        wait_until(self, 5.5)
        self.play(FadeIn(givens[0], shift=RIGHT * 0.12), FadeIn(givens[1], shift=RIGHT * 0.12), run_time=0.9)
        self.play(FadeIn(expand, shift=UP * 0.10), run_time=0.8)
        wait_until(self, 12.5)
        self.play(FadeIn(chain[0], shift=RIGHT * 0.12), run_time=0.8)
        self.play(GrowArrow(chain[1]), FadeIn(chain[2], shift=DOWN * 0.10), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(op, shift=UP * 0.10) for op in ops], lag_ratio=0.18), run_time=1.2)
        wait_until(self, 18.2)
        self.play(FadeIn(conclusion, shift=UP * 0.10), run_time=0.9)
        finish(self, 22.698)


class SeventeenGroupsV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("下标乘 2 后为什么正好分成两组？", "结果大于 8 时，沿横轴上下对称折回 c1 到 c8")

        top_panel = panel(12.15, 1.72, MINT).move_to(UP * 0.86)
        bottom_panel = panel(12.15, 1.72, VIOLET).move_to(DOWN * 1.08)
        top_heading = cn("从 c1 出发", 0.28, MINT).move_to(top_panel.get_left() + RIGHT * 0.90)
        bottom_heading = cn("从 c3 出发", 0.28, VIOLET).move_to(bottom_panel.get_left() + RIGHT * 0.90)

        top_texts = [r"c_1", r"c_2", r"c_4", r"c_8", r"c_{16}=c_1"]
        bottom_texts = [r"c_3", r"c_6", r"c_{12}=c_5", r"c_{10}=c_7", r"c_{14}=c_3"]
        top_nodes = VGroup(*[equation_card(t, MINT, 1.72, 0.54) for t in top_texts]).arrange(RIGHT, buff=0.34).shift(RIGHT * 0.35).move_to(top_panel)
        bottom_nodes = VGroup(*[equation_card(t, VIOLET, 1.72, 0.54) for t in bottom_texts]).arrange(RIGHT, buff=0.34).shift(RIGHT * 0.35).move_to(bottom_panel)
        top_arrows = VGroup(*[
            Arrow(top_nodes[i].get_right(), top_nodes[i + 1].get_left(), buff=0.05, color=MINT, stroke_width=1.7, tip_length=0.12)
            for i in range(4)
        ])
        bottom_arrows = VGroup(*[
            Arrow(bottom_nodes[i].get_right(), bottom_nodes[i + 1].get_left(), buff=0.05, color=VIOLET, stroke_width=1.7, tip_length=0.12)
            for i in range(4)
        ])
        top_mults = VGroup(*[cn("×2", 0.22, MUTED).next_to(a, UP, buff=0.05) for a in top_arrows])
        bottom_mults = VGroup(*[cn("×2", 0.22, MUTED).next_to(a, UP, buff=0.05) for a in bottom_arrows])
        fold_notes = VGroup(
            cn("16 折回 1", 0.22, AMBER).next_to(top_nodes[-1], DOWN, buff=0.06),
            cn("12 折回 5", 0.22, AMBER).next_to(bottom_nodes[2], DOWN, buff=0.06),
            cn("10 折回 7", 0.22, AMBER).next_to(bottom_nodes[3], DOWN, buff=0.06),
            cn("14 折回 3", 0.22, AMBER).next_to(bottom_nodes[4], DOWN, buff=0.06),
        )
        labels = VGroup(
            equation_card(r"A=c_1+c_2+c_4+c_8", MINT, 5.45, 0.64),
            equation_card(r"B=c_3+c_5+c_6+c_7", VIOLET, 5.45, 0.64),
        ).arrange(RIGHT, buff=0.55).move_to(DOWN * 2.86)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(top_panel), FadeIn(bottom_panel), FadeIn(top_heading), FadeIn(bottom_heading), run_time=0.9)
        self.play(FadeIn(top_nodes[0]), run_time=0.5)
        for i in range(4):
            self.play(GrowArrow(top_arrows[i]), FadeIn(top_mults[i]), FadeIn(top_nodes[i + 1], shift=RIGHT * 0.08), run_time=0.75)
            if i == 3:
                self.play(FadeIn(fold_notes[0]), Indicate(top_nodes[i + 1], color=AMBER), run_time=0.65)
        self.play(FadeIn(bottom_nodes[0]), run_time=0.5)
        for i in range(4):
            self.play(GrowArrow(bottom_arrows[i]), FadeIn(bottom_mults[i]), FadeIn(bottom_nodes[i + 1], shift=RIGHT * 0.08), run_time=0.75)
            if i >= 1:
                self.play(FadeIn(fold_notes[i]), Indicate(bottom_nodes[i + 1], color=AMBER), run_time=0.55)
        self.play(FadeIn(labels[0], shift=UP * 0.10), FadeIn(labels[1], shift=UP * 0.10), run_time=0.9)
        finish(self, 24.320)


class SeventeenFirstLayerV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("第一层：先从圆周图看懂 A+B=−1", "固定箭头贡献 1；薄荷绿四对贡献 A；紫色四对贡献 B")
        left = panel(6.10, 5.10).to_edge(LEFT, buff=0.40).shift(DOWN * 0.27)
        right = panel(5.60, 5.10).to_edge(RIGHT, buff=0.40).shift(DOWN * 0.27)
        lt = card_heading(left, "十七支单位箭头按 1、A、B 着色")
        rt = card_heading(right, "对应的横向分量")

        center = np.array([-3.70, -0.62, 0.0])
        radius = 1.62
        circle = Circle(radius=radius, color=BLUE, stroke_width=1.7).move_to(center)
        pts = polygon_points(17, radius, center, rotation=0)
        dots = VGroup(*[Dot(p, radius=0.035, color=MUTED) for p in pts])
        fixed_arrow = Arrow(center, pts[0], buff=0.06, color=INK, stroke_width=2.8, max_tip_length_to_length_ratio=0.10)
        fixed_label = MathTex("1", color=INK).scale(0.52).next_to(fixed_arrow, UP, buff=0.05)

        a_indices = [1, 2, 4, 8]
        b_indices = [3, 5, 6, 7]
        a_pairs = VGroup()
        b_pairs = VGroup()
        a_pair_labels = VGroup()
        b_pair_labels = VGroup()
        for k in range(1, 9):
            color = MINT if k in a_indices else VIOLET
            pair = VGroup(
                Arrow(center, pts[k], buff=0.06, color=color, stroke_width=2.2, max_tip_length_to_length_ratio=0.08),
                Arrow(center, pts[17 - k], buff=0.06, color=color, stroke_width=2.2, max_tip_length_to_length_ratio=0.08),
                Line(pts[k], pts[17 - k], color=color, stroke_width=1.5, stroke_opacity=0.70),
            )
            foot = np.array([pts[k][0], center[1], 0.0])
            label = MathTex(rf"c_{k}", color=color).scale(0.40).next_to(foot, UP if k % 2 == 0 else DOWN, buff=0.08)
            if k in a_indices:
                a_pairs.add(pair)
                a_pair_labels.add(label)
            else:
                b_pairs.add(pair)
                b_pair_labels.add(label)

        one_card = equation_card(r"1", INK, 1.05, 0.56)
        a_row = VGroup(cn("A =", 0.27, MINT), *[c_chip(k, MINT, 0.72) for k in a_indices]).arrange(RIGHT, buff=0.10)
        b_row = VGroup(cn("B =", 0.27, VIOLET), *[c_chip(k, VIOLET, 0.72) for k in b_indices]).arrange(RIGHT, buff=0.10)
        contribution_rows = VGroup(one_card, a_row, b_row).arrange(DOWN, aligned_edge=LEFT, buff=0.28).next_to(rt, DOWN, buff=0.42)
        sum_steps = VGroup(
            MathTex(r"1+A+B=0", color=AMBER).scale(0.67),
            MathTex(r"\boxed{A+B=-1}", color=MINT).scale(0.73),
        ).arrange(DOWN, buff=0.24).move_to(right.get_bottom() + UP * 1.00)

        product_title = title_group("接着计算 A×B", "先完整看一个乘积怎样变成两项，再加速处理其余十五个")
        product_lt = card_heading(left, "A×B 展开成十六个乘积")
        product_rt = card_heading(right, "每个乘积贡献哪两个 c？")
        product_a_row = VGroup(cn("A：", 0.24, MINT), *[c_chip(k, MINT, 0.64) for k in a_indices]).arrange(RIGHT, buff=0.10)
        product_b_row = VGroup(cn("B：", 0.24, VIOLET), *[c_chip(k, VIOLET, 0.64) for k in b_indices]).arrange(RIGHT, buff=0.10)
        member_rows = VGroup(product_a_row, product_b_row).arrange(DOWN, aligned_edge=LEFT, buff=0.16).next_to(product_lt, DOWN, buff=0.36)
        product_formula = equation_card(r"c_1c_3=c_4+c_2", AMBER, 4.78, 0.64).next_to(member_rows, DOWN, buff=0.42)
        progress = cn("1 / 16", 0.23, MUTED).next_to(product_formula, DOWN, buff=0.10)
        counter_groups = VGroup(*[
            VGroup(
                c_chip(k, [MINT, BLUE, VIOLET, AMBER][(k - 1) % 4], 0.54),
                MathTex("0", color=INK).scale(0.43),
            ).arrange(DOWN, buff=0.06)
            for k in range(1, 9)
        ]).arrange(RIGHT, buff=0.06).next_to(product_rt, DOWN, buff=0.82)
        counter_note = cn("十六个乘积展开后，c1 到 c8 各出现几次", 0.24, MUTED).next_to(counter_groups, UP, buff=0.12)
        product_result = equation_card(r"AB=4(c_1+\cdots+c_8)=-4", AMBER, 4.72, 0.58).move_to(right.get_bottom() + UP * 0.62)
        final = VGroup(
            equation_card(r"t^2+t-4=0", MINT, 4.10, 0.70),
            equation_card(r"A,B=\frac{-1\pm\sqrt{17}}2", MINT, 5.30, 0.69),
            pill("有向投影和：A>0 向右，B<0 向左", AMBER, 5.20),
        ).arrange(DOWN, buff=0.28).move_to(DOWN * 0.20)
        final_title = title_group("和与积都已知，A、B 就是二次方程的两个根", "有向投影和的正负，可以区分 A 与 B")

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(left), FadeIn(right), FadeIn(lt), FadeIn(rt), run_time=0.9)
        self.play(Create(circle), FadeIn(dots), run_time=0.8)
        self.play(GrowArrow(fixed_arrow), FadeIn(fixed_label), TransformFromCopy(fixed_arrow, one_card), run_time=0.9)
        wait_until(self, 5.5)
        self.play(LaggedStart(*[Create(pair) for pair in a_pairs], lag_ratio=0.12), FadeIn(a_pair_labels), run_time=1.4)
        self.play(TransformFromCopy(VGroup(a_pairs, a_pair_labels), a_row), run_time=0.8)
        wait_until(self, 11.8)
        self.play(LaggedStart(*[Create(pair) for pair in b_pairs], lag_ratio=0.12), FadeIn(b_pair_labels), run_time=1.4)
        self.play(TransformFromCopy(VGroup(b_pairs, b_pair_labels), b_row), run_time=0.8)
        wait_until(self, 18.0)
        self.play(FadeIn(sum_steps[0], shift=RIGHT * 0.12), run_time=0.8)
        self.play(FadeIn(sum_steps[1], shift=UP * 0.10), run_time=0.8)

        wait_until(self, 23.8)
        sum_content = VGroup(title, lt, rt, circle, dots, fixed_arrow, fixed_label, a_pairs, b_pairs, a_pair_labels, b_pair_labels, contribution_rows, sum_steps)
        self.play(FadeOut(sum_content), FadeIn(product_title), FadeIn(product_lt), FadeIn(product_rt), FadeIn(member_rows), FadeIn(counter_note), FadeIn(counter_groups), run_time=0.9)

        def fold_index(value: int) -> int:
            residue = value % 17
            return min(residue, 17 - residue)

        products = []
        for a in a_indices:
            for b in b_indices:
                products.append((a, b, fold_index(a + b), fold_index(a - b)))

        counts = [0] * 9
        current_formula = product_formula
        current_progress = progress
        wait_until(self, 26.0)
        for n, (a, b, plus_index, minus_index) in enumerate(products, start=1):
            if n == 1:
                self.play(FadeIn(current_formula, shift=RIGHT * 0.12), FadeIn(current_progress), run_time=0.9)
                wait_until(self, 32.0)
            else:
                new_formula = equation_card(
                    rf"c_{a}c_{b}=c_{{{plus_index}}}+c_{{{minus_index}}}",
                    AMBER,
                    4.78,
                    0.64,
                ).move_to(current_formula)
                new_progress = cn(f"{n} / 16", 0.23, MUTED).move_to(current_progress)
                self.play(ReplacementTransform(current_formula, new_formula), Transform(current_progress, new_progress), run_time=0.16 if n > 2 else 0.40)
                current_formula = new_formula
            updates = []
            for index in (plus_index, minus_index):
                counts[index] += 1
            for index in sorted({plus_index, minus_index}):
                old_number = counter_groups[index - 1][1]
                new_number = MathTex(str(counts[index]), color=INK).scale(0.43).move_to(old_number)
                updates.append(Transform(old_number, new_number))
            self.play(*updates, Indicate(counter_groups[plus_index - 1][0], color=AMBER), Indicate(counter_groups[minus_index - 1][0], color=AMBER), run_time=0.72 if n == 1 else 0.16)

        wait_until(self, 41.0)
        self.play(FadeIn(product_result, shift=UP * 0.10), run_time=0.9)
        wait_until(self, 48.0)
        old_content = VGroup(left, right, product_title, product_lt, product_rt, member_rows, counter_note, counter_groups, current_formula, current_progress, product_result)
        self.play(FadeOut(old_content), FadeIn(final_title), run_time=0.8)
        self.play(FadeIn(final[0], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 53.2)
        self.play(FadeIn(final[1], shift=UP * 0.10), run_time=0.8)
        wait_until(self, 60.5)
        self.play(FadeIn(final[2], shift=UP * 0.10), run_time=0.7)
        finish(self, 66.812)


class SeventeenSecondLayerV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("第 2 层：把每个四项和再拆成两个两项和", "每个乘积先变成两项，再按 c1 到 c8 归类")
        group_cards = VGroup(
            equation_card(r"C=c_1+c_4", MINT, 2.72, 0.57),
            equation_card(r"D=c_2+c_8", BLUE, 2.72, 0.57),
            equation_card(r"E=c_3+c_5", VIOLET, 2.72, 0.57),
            equation_card(r"F=c_6+c_7", AMBER, 2.72, 0.57),
        ).arrange(RIGHT, buff=0.34).move_to(UP * 1.80)
        left = panel(5.90, 4.05, MINT).to_edge(LEFT, buff=0.38).shift(DOWN * 0.72)
        right = panel(5.90, 4.05, VIOLET).to_edge(RIGHT, buff=0.38).shift(DOWN * 0.72)
        lt = card_heading(left, "C+D=A，下面核对 CD", MINT)
        rt = card_heading(right, "E+F=B，下面核对 EF", VIOLET)
        left_steps = VGroup(
            MathTex(r"c_1c_2=c_3+c_1", color=MINT).scale(0.50),
            MathTex(r"c_1c_8=c_8+c_7", color=MINT).scale(0.50),
            MathTex(r"c_4c_2=c_6+c_2", color=MINT).scale(0.50),
            MathTex(r"c_4c_8=c_5+c_4", color=MINT).scale(0.50),
        ).arrange(DOWN, buff=0.18).next_to(lt, DOWN, buff=0.30)
        right_steps = VGroup(
            MathTex(r"c_3c_6=c_8+c_3", color=VIOLET).scale(0.50),
            MathTex(r"c_3c_7=c_7+c_4", color=VIOLET).scale(0.50),
            MathTex(r"c_5c_6=c_6+c_1", color=VIOLET).scale(0.50),
            MathTex(r"c_5c_7=c_5+c_2", color=VIOLET).scale(0.50),
        ).arrange(DOWN, buff=0.18).next_to(rt, DOWN, buff=0.30)
        left_slots = VGroup(*[c_chip(k, MINT, 0.52).set_opacity(0.18) for k in range(1, 9)]).arrange(RIGHT, buff=0.055).move_to(left.get_bottom() + UP * 0.42)
        right_slots = VGroup(*[c_chip(k, VIOLET, 0.52).set_opacity(0.18) for k in range(1, 9)]).arrange(RIGHT, buff=0.055).move_to(right.get_bottom() + UP * 0.42)
        left_slot_note = cn("展开结果按下标归类", 0.21, MUTED).next_to(left_slots, UP, buff=0.08)
        right_slot_note = cn("展开结果按下标归类", 0.21, MUTED).next_to(right_slots, UP, buff=0.08)
        # The detailed expansions fill most of each card.  Once a side has been
        # checked, replace its working with the conclusion instead of stacking a
        # new strip below the panels.
        cover_note = VGroup(
            pill("c1 到 c8 各出现一次 → CD=−1", AMBER, 4.55).move_to(left.get_center() + DOWN * 0.22),
            pill("c1 到 c8 各出现一次 → EF=−1", AMBER, 4.55).move_to(right.get_center() + DOWN * 0.22),
        )
        result = VGroup(
            equation_card(r"t^2-At-1=0", MINT, 4.55, 0.66),
            equation_card(r"t^2-Bt-1=0", VIOLET, 4.55, 0.66),
            pill("C、D、E、F 都由第 2 层二次方程得到", AMBER, 6.20),
        ).arrange(DOWN, buff=0.32).move_to(DOWN * 0.10)
        result_title = title_group("两组的和与积都已知，第 2 层仍然只需求根", "C、D 解一个二次方程；E、F 再解一个")

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(group_cards, shift=DOWN * 0.10), run_time=1.0)
        self.play(FadeIn(left), FadeIn(right), FadeIn(lt), FadeIn(rt), FadeIn(left_slot_note), FadeIn(right_slot_note), FadeIn(left_slots), FadeIn(right_slots), run_time=0.8)
        wait_until(self, 13.0)
        left_outputs = [(3, 1), (8, 7), (6, 2), (5, 4)]
        right_outputs = [(8, 3), (7, 4), (6, 1), (5, 2)]
        for left_step, outputs in zip(left_steps, left_outputs):
            self.play(FadeIn(left_step, shift=RIGHT * 0.10), left_slots[outputs[0] - 1].animate.set_opacity(1), left_slots[outputs[1] - 1].animate.set_opacity(1), run_time=0.82)
            self.play(Indicate(left_slots[outputs[0] - 1], color=AMBER), Indicate(left_slots[outputs[1] - 1], color=AMBER), run_time=0.34)
        self.play(
            FadeOut(left_steps),
            FadeOut(left_slots),
            FadeOut(left_slot_note),
            FadeIn(cover_note[0], shift=UP * 0.10),
            run_time=0.8,
        )
        for right_step, outputs in zip(right_steps, right_outputs):
            self.play(FadeIn(right_step, shift=RIGHT * 0.10), right_slots[outputs[0] - 1].animate.set_opacity(1), right_slots[outputs[1] - 1].animate.set_opacity(1), run_time=0.62)
            self.play(Indicate(right_slots[outputs[0] - 1], color=AMBER), Indicate(right_slots[outputs[1] - 1], color=AMBER), run_time=0.26)
        wait_until(self, 29.6)
        self.play(
            FadeOut(right_steps),
            FadeOut(right_slots),
            FadeOut(right_slot_note),
            FadeIn(cover_note[1], shift=UP * 0.10),
            run_time=0.8,
        )
        old_content = VGroup(group_cards, left, right, lt, rt, left_steps, right_steps, left_slots, right_slots, left_slot_note, right_slot_note, cover_note)
        wait_until(self, 32.2)
        self.play(FadeOut(old_content), ReplacementTransform(title, result_title), FadeIn(result[0], shift=UP * 0.10), FadeIn(result[1], shift=UP * 0.10), run_time=0.9)
        self.play(FadeIn(result[2], shift=UP * 0.10), run_time=0.8)
        finish(self, 45.087)


class SeventeenThirdLayerV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("第 3 层：终于把目标 c1 单独分出来", "和来自 C，积正好来自已经得到的 E")
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
        wait_until(self, 20.2)
        self.play(FadeIn(root_order[0], shift=UP * 0.10), FadeIn(root_order[1], shift=UP * 0.10), run_time=0.9)
        self.play(FadeIn(root_order[2], shift=UP * 0.10), run_time=0.9)
        finish(self, 31.689)


class CoordinateToVertexV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("三层方程怎样回到真实尺规？", "每层都只使用刚才演示过的四则运算和开平方")
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
        axis = Arrow(
            center + LEFT * 2.04,
            center + RIGHT * 2.08,
            buff=0,
            color=MUTED,
            stroke_width=1.4,
            tip_length=0.12,
            max_tip_length_to_length_ratio=0.03,
        )
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
        self.play(FadeIn(stages[0], shift=DOWN * 0.10), run_time=0.5)
        for i in range(3):
            self.play(GrowArrow(stage_arrows[i]), FadeIn(stages[i + 1], shift=DOWN * 0.10), run_time=0.55)
            self.wait(0.35)
        self.play(LaggedStart(*[FadeIn(tag, shift=LEFT * 0.08) for tag in op_tags], lag_ratio=0.18), run_time=0.7)
        wait_until(self, 7.0)
        self.play(Create(circle), Create(axis), FadeIn(start_dot), run_time=0.7)
        self.play(Create(x_seg), FadeIn(x_label), run_time=0.6)
        wait_until(self, 11.4)
        self.play(Create(vertical), FadeIn(p_dot, scale=1.5), FadeIn(p_label), run_time=0.7)
        wait_until(self, 15.7)
        self.play(Create(edge), FadeIn(edge_note, shift=UP * 0.10), run_time=0.7)
        finish(self, 16.776)


class CopyChordV7(StyledScene):
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
        finish(self, 11.097)


class GeneralCriterionV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("两个具体案例背后，还有一个一般判据", "它概括了哪些边数能够精确尺规作图")
        theorem = equation_card(r"n=2^k p_1p_2\cdots p_m", MINT, 6.10, 0.78).move_to(UP * 1.95)
        theorem_note = cn("p1、p2……是互不重复的费马素数", 0.32, MUTED).next_to(theorem, DOWN, buff=0.16)
        left = panel(5.70, 3.95, AMBER).to_edge(LEFT, buff=0.50).shift(DOWN * 0.78)
        right = panel(5.70, 3.95, VIOLET).to_edge(RIGHT, buff=0.50).shift(DOWN * 0.78)
        lt = card_heading(left, "费马素数是什么意思？", AMBER)
        rt = card_heading(right, "2 的幂为什么出现？", VIOLET)
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
            cn("每次平分，边数乘 2", 0.29, MUTED),
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
        finish(self, 46.677)


class FinalPayoffV7(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("真正的分界，不是边数大小", "而是目标坐标能不能拆成一连串二次方程")
        left = panel(5.55, 4.35, CORAL).to_edge(LEFT, buff=0.58).shift(DOWN * 0.38)
        right = panel(5.55, 4.35, MINT).to_edge(RIGHT, buff=0.58).shift(DOWN * 0.38)
        lt = card_heading(left, "正七边形", CORAL)
        rt = card_heading(right, "正十七边形", MINT)
        seven = VGroup(
            equation_card(r"u^3+u^2-2u-1=0", CORAL, 4.65, 0.63),
            cn("有 3 个实数根，但没有有理根", 0.29, MUTED),
            pill("有理系数最小次数为 3", CORAL, 4.05),
        ).arrange(DOWN, buff=0.33).next_to(lt, DOWN, buff=0.45)
        seventeen = VGroup(
            equation_card(r"A,B", MINT, 2.15, 0.64),
            equation_card(r"C,E", BLUE, 2.15, 0.64),
            equation_card(r"c_1", VIOLET, 2.15, 0.64),
            pill("三层二次求解：尺规能够完成", MINT, 4.50),
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
        finish(self, 24.221)


class Constructible17GonCoverV7(StyledScene):
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
        seven_block = pill("次数为 3 · 尺规跨不过", CORAL, 3.35).move_to([-2.02, -1.03, 0])

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
        seventeen_ok = pill("三层二次 · 尺规能够完成", MINT, 3.65).move_to([2.02, -1.67, 0])

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

