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
    ChoiceRevealV3,
    ConsequencesAndPayoffV3,
    PolygonToOperationsBridge,
    ProductQuotientConstructionV3,
    RichmondConstructionV3,
    SquareRootIntersectionV3,
    StyledScene,
    card_heading,
    cn,
    panel,
    pill,
    polygon_points,
    title_group,
)


def count_box(number: str, color: str, caption: str) -> VGroup:
    box = RoundedRectangle(
        width=1.18,
        height=1.04,
        corner_radius=0.16,
        stroke_color=color,
        fill_color=color,
        fill_opacity=0.12,
    )
    value = MathTex(number, color=color).scale(0.76).move_to(box.get_center() + UP * 0.13)
    label = cn(caption, 0.23, color).move_to(box.get_center() + DOWN * 0.29)
    return VGroup(box, value, label)


def flow_card(width: float, color: str, title: str, lines: list[str]) -> VGroup:
    box = RoundedRectangle(
        width=width,
        height=2.18,
        corner_radius=0.20,
        stroke_color=color,
        fill_color=PANEL,
        fill_opacity=0.94,
    )
    heading = cn(title, 0.34, color).move_to(box.get_top() + DOWN * 0.43)
    body = VGroup(*[cn(line, 0.27, INK) for line in lines]).arrange(DOWN, buff=0.13)
    body.move_to(box.get_center() + DOWN * 0.23)
    return VGroup(box, heading, body)


def coordinate_pair_groups(n: int, radius: float, center: np.ndarray, colors: list[str]) -> VGroup:
    points = polygon_points(n, radius, center, rotation=0)
    groups = VGroup()
    for k in range(1, (n + 1) // 2):
        upper = points[k]
        lower = points[n - k]
        color = colors[(k - 1) % len(colors)]
        chord = Line(lower, upper, color=color, stroke_width=2.0 if n == 7 else 1.35, stroke_opacity=0.72)
        dots = VGroup(
            Dot(upper, radius=0.060 if n == 7 else 0.040, color=color),
            Dot(lower, radius=0.060 if n == 7 else 0.040, color=color),
        )
        x_dot = Dot([upper[0], center[1], 0], radius=0.052 if n == 7 else 0.035, color=color)
        groups.add(VGroup(chord, dots, x_dot))
    return groups


class ChoiceRevealV4(ChoiceRevealV3):
    pass


class PolygonToOperationsBridgeV4(PolygonToOperationsBridge):
    pass


class AddSubtractConstructionV4(AddSubtractConstructionV3):
    pass


class ProductQuotientConstructionV4(ProductQuotientConstructionV3):
    pass


class SquareRootIntersectionV4(SquareRootIntersectionV3):
    pass


class QuadraticChoiceMechanism(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("尺规为什么总带来“二次层级”？", "先数交点，再谈判据")

        left_card = panel(5.35, 4.85).to_edge(LEFT, buff=0.45).shift(DOWN * 0.30)
        right_card = panel(6.30, 4.85).to_edge(RIGHT, buff=0.45).shift(DOWN * 0.30)
        left_title = card_heading(left_card, "每一步能产生几个新位置？")
        right_title = card_heading(right_card, "候选总数只能一层层乘 2")

        cross_center = np.array([-3.70, 0.72, 0.0])
        cross = VGroup(
            Line(cross_center + LEFT * 1.40 + DOWN * 0.52, cross_center + RIGHT * 1.40 + UP * 0.52, color=BLUE, stroke_width=2.5),
            Line(cross_center + LEFT * 1.40 + UP * 0.52, cross_center + RIGHT * 1.40 + DOWN * 0.52, color=MINT, stroke_width=2.5),
        )
        cross_hit = Dot(cross_center, radius=0.080, color=INK)
        one_label = pill("直线 × 直线：1 个交点", BLUE, 3.75).move_to(cross_center + DOWN * 0.93)

        circle_center = np.array([-3.70, -1.25, 0.0])
        circle = Circle(radius=0.76, color=AMBER, stroke_width=2.5).move_to(circle_center)
        secant = Line(circle_center + LEFT * 1.38, circle_center + RIGHT * 1.38, color=BLUE, stroke_width=2.5)
        two_hits = VGroup(
            Dot(circle_center + LEFT * 0.76, radius=0.080, color=MINT),
            Dot(circle_center + RIGHT * 0.76, radius=0.080, color=MINT),
        )
        two_label = pill("圆 × 直线：最多 2 个交点", AMBER, 4.05).move_to(circle_center + DOWN * 1.03)

        counts = VGroup(
            count_box("1", INK, "已知"),
            count_box("2", BLUE, "一层"),
            count_box("4", VIOLET, "两层"),
            count_box("8", MINT, "三层"),
        ).arrange(RIGHT, buff=0.48).move_to(right_card.get_center() + UP * 0.22)
        arrows = VGroup(*[
            Arrow(counts[i].get_right(), counts[i + 1].get_left(), buff=0.08, color=MUTED, stroke_width=1.8)
            for i in range(3)
        ])
        root_labels = VGroup(*[
            MathTex(r"+\sqrt{\phantom{x}}", color=AMBER).scale(0.42).next_to(arrows[i], UP, buff=0.05)
            for i in range(3)
        ])
        formula = MathTex(r"1\ \longrightarrow\ 2\ \longrightarrow\ 4\ \longrightarrow\ 8\ \longrightarrow\cdots", color=MINT).scale(0.66)
        formula.move_to(right_card.get_bottom() + UP * 1.03)
        summary = pill("四则运算不添新分支；每个根号最多让候选翻倍", VIOLET, 5.42)
        summary.move_to(right_card.get_bottom() + UP * 0.42)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(left_card), FadeIn(right_card), FadeIn(left_title), FadeIn(right_title), run_time=0.8)
        self.play(Create(cross), FadeIn(cross_hit, scale=1.5), run_time=0.8)
        self.play(FadeIn(one_label, shift=UP * 0.10), run_time=0.6)
        self.play(Create(circle), Create(secant), FadeIn(two_hits, scale=1.5), run_time=0.9)
        self.play(FadeIn(two_label, shift=UP * 0.10), run_time=0.6)
        self.play(FadeIn(counts[0]), run_time=0.4)
        for i in range(3):
            self.play(GrowArrow(arrows[i]), FadeIn(root_labels[i]), FadeIn(counts[i + 1], shift=RIGHT * 0.10), run_time=0.65)
            self.wait(0.18)
        self.play(FadeIn(formula, shift=UP * 0.10), run_time=0.55)
        self.play(FadeIn(summary, shift=UP * 0.10), Indicate(two_hits, color=MINT), run_time=0.75)
        self.wait(0.55)


class CoordinateSiblingComparison(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("目标横坐标有多少个“同类候选”？", "上下成对的顶点共用同一个 x；数的是坐标，不是圆周等分")

        left_card = panel(6.05, 4.95, CORAL).to_edge(LEFT, buff=0.43).shift(DOWN * 0.30)
        right_card = panel(6.05, 4.95, MINT).to_edge(RIGHT, buff=0.43).shift(DOWN * 0.30)
        left_title = card_heading(left_card, "正七边形：3 个横坐标候选", CORAL)
        right_title = card_heading(right_card, "正十七边形：8 个横坐标候选", MINT)

        c7 = np.array([-3.65, 0.08, 0.0])
        c17 = np.array([3.65, 0.08, 0.0])
        radius = 1.27
        circle7 = Circle(radius=radius, color=MUTED, stroke_width=1.7).move_to(c7)
        circle17 = Circle(radius=radius, color=MUTED, stroke_width=1.7).move_to(c17)
        axis7 = Line(c7 + LEFT * 1.42, c7 + RIGHT * 1.42, color=MUTED, stroke_width=1.4)
        axis17 = Line(c17 + LEFT * 1.42, c17 + RIGHT * 1.42, color=MUTED, stroke_width=1.4)
        fixed7 = VGroup(Dot(c7 + RIGHT * radius, radius=0.085, color=INK), cn("已知 x=1", 0.23, INK).next_to(c7 + RIGHT * radius, RIGHT, buff=0.08))
        fixed17 = VGroup(Dot(c17 + RIGHT * radius, radius=0.085, color=INK), cn("已知 x=1", 0.23, INK).next_to(c17 + RIGHT * radius, RIGHT, buff=0.08))

        pairs7 = coordinate_pair_groups(7, radius, c7, [CORAL, AMBER, VIOLET])
        pairs17 = coordinate_pair_groups(17, radius, c17, [MINT, BLUE, VIOLET, AMBER])
        count7 = MathTex(r"(7-1)\div2=3", color=CORAL).scale(0.70).move_to(left_card.get_bottom() + UP * 0.92)
        count17 = MathTex(r"(17-1)\div2=8=2^3", color=MINT).scale(0.70).move_to(right_card.get_bottom() + UP * 0.92)
        result7 = pill("3 不是 2 的幂：撞上障碍", CORAL, 4.55).move_to(left_card.get_bottom() + UP * 0.35)
        result17 = pill("8 可沿二次层级得到", MINT, 4.30).move_to(right_card.get_bottom() + UP * 0.35)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(left_card), FadeIn(right_card), FadeIn(left_title), FadeIn(right_title), run_time=0.8)
        self.play(Create(circle7), Create(circle17), Create(axis7), Create(axis17), FadeIn(fixed7), FadeIn(fixed17), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(pair, scale=1.05) for pair in pairs7], lag_ratio=0.16), run_time=1.35)
        self.play(FadeIn(count7, shift=RIGHT * 0.16), FadeIn(result7, shift=UP * 0.10), run_time=0.8)
        self.wait(0.35)
        self.play(LaggedStart(*[FadeIn(pair, scale=1.04) for pair in pairs17], lag_ratio=0.08), run_time=1.70)
        self.play(FadeIn(count17, shift=RIGHT * 0.16), FadeIn(result17, shift=UP * 0.10), run_time=0.8)
        self.wait(0.45)
        self.play(Indicate(count7, color=CORAL), Indicate(count17, color=MINT), run_time=0.85)
        self.wait(1.15)


class OddPartExplained(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("“奇数部分”只是反复除 2 后剩下的数", "倒着恢复每个 2，只需把已经得到的圆心角再平分一次")

        strip = panel(12.25, 2.10).move_to(UP * 0.88)
        strip_title = cn("例：40 的核心从哪里来？", 0.35, INK).move_to(strip.get_top() + DOWN * 0.38)
        values = VGroup(*[
            pill(value, color, 1.34)
            for value, color in [("40", BLUE), ("20", BLUE), ("10", VIOLET), ("5", MINT)]
        ]).arrange(RIGHT, buff=0.72).move_to(strip.get_center() + DOWN * 0.15)
        divide_arrows = VGroup(*[
            Arrow(values[i].get_right(), values[i + 1].get_left(), buff=0.08, color=MUTED, stroke_width=1.8)
            for i in range(3)
        ])
        divide_labels = VGroup(*[
            MathTex(r"\div2", color=AMBER).scale(0.46).next_to(divide_arrows[i], UP, buff=0.04)
            for i in range(3)
        ])
        core_label = cn("不能再除 2：5 就是奇数部分", 0.28, MINT).next_to(values[-1], DOWN, buff=0.13)

        left_card = panel(5.90, 2.95, CORAL).to_edge(LEFT, buff=0.48).shift(DOWN * 2.02)
        right_card = panel(5.90, 2.95, MINT).to_edge(RIGHT, buff=0.48).shift(DOWN * 2.02)
        left_title = card_heading(left_card, "7 已经是奇数，所以奇数部分仍是 7", CORAL)
        right_title = card_heading(right_card, "17 已经是奇数，所以奇数部分仍是 17", MINT)
        left_math = VGroup(
            MathTex(r"p=7", color=INK).scale(0.62),
            MathTex(r"(p-1)/2=3", color=CORAL).scale(0.72),
            pill("3 不是 2 的幂", CORAL, 3.30),
        ).arrange(DOWN, buff=0.20).next_to(left_title, DOWN, buff=0.30)
        right_math = VGroup(
            MathTex(r"p=17", color=INK).scale(0.62),
            MathTex(r"(p-1)/2=8=2^3", color=MINT).scale(0.72),
            pill("8 符合二次层级", MINT, 3.30),
        ).arrange(DOWN, buff=0.20).next_to(right_title, DOWN, buff=0.30)
        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(strip), FadeIn(strip_title), run_time=0.8)
        self.play(FadeIn(values[0]), run_time=0.35)
        for i in range(3):
            self.play(GrowArrow(divide_arrows[i]), FadeIn(divide_labels[i]), FadeIn(values[i + 1], shift=RIGHT * 0.10), run_time=0.65)
        self.play(FadeIn(core_label, shift=UP * 0.08), Indicate(values[-1], color=MINT), run_time=0.7)
        self.play(FadeIn(left_card), FadeIn(right_card), FadeIn(left_title), FadeIn(right_title), run_time=0.7)
        for i in range(3):
            self.play(FadeIn(left_math[i], shift=RIGHT * 0.12), FadeIn(right_math[i], shift=RIGHT * 0.12), run_time=0.65)
            self.wait(0.18)
        self.play(Indicate(left_math[1], color=CORAL), Indicate(right_math[1], color=MINT), run_time=0.75)
        self.wait(1.15)


class CriterionToConstructionBridge(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("满足二次层级的奇素数，有一个名字", "3、5、17、257、65537……叫费马素数")

        fermat_list = pill("完整判据：2 的幂 × 互不重复的费马素数", VIOLET, 6.15).move_to(UP * 1.75)

        cards = VGroup(
            flow_card(2.35, MINT, "17 通过判据", ["候选层级", "是 2 的幂"]),
            flow_card(3.05, VIOLET, "坐标表达式", ["有限次四则运算", "加上嵌套平方根"]),
            flow_card(3.15, AMBER, "翻译成几何", ["搬长度、相似比例", "半圆与圆线交点"]),
            flow_card(2.35, MINT, "得到施工图", ["每一步都是", "直线、圆、交点"]),
        ).arrange(RIGHT, buff=0.48).move_to(DOWN * 0.25)
        arrows = VGroup(*[
            Arrow(cards[i].get_right(), cards[i + 1].get_left(), buff=0.08, color=MUTED, stroke_width=2.0)
            for i in range(3)
        ])
        existence = pill("判据：保证“存在一套有限步骤”", VIOLET, 4.45).move_to(DOWN * 2.38 + LEFT * 3.05)
        recipe = pill("下一场：把这套步骤真的画出来", MINT, 4.45).move_to(DOWN * 2.38 + RIGHT * 3.05)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(fermat_list, shift=DOWN * 0.10), run_time=0.8)
        self.play(FadeIn(cards[0], shift=UP * 0.10), run_time=0.55)
        for i in range(3):
            self.play(GrowArrow(arrows[i]), FadeIn(cards[i + 1], shift=RIGHT * 0.12), run_time=0.8)
            self.wait(0.24)
        self.play(FadeIn(existence, shift=UP * 0.10), run_time=0.6)
        self.play(FadeIn(recipe, shift=UP * 0.10), Circumscribe(cards[-1][0], color=MINT), run_time=0.7)
        self.wait(1.50)


class RichmondConstructionV4(RichmondConstructionV3):
    pass


class ConsequencesAndPayoffV4(ConsequencesAndPayoffV3):
    pass
