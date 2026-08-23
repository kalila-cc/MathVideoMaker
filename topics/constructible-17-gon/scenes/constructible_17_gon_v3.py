from __future__ import annotations

from pathlib import Path
import sys
import numpy as np

from manim import *


SCENE_DIR = Path(__file__).resolve().parent
if str(SCENE_DIR) not in sys.path:
    sys.path.insert(0, str(SCENE_DIR))

from constructible_17_gon_v2 import (  # noqa: E402
    AMBER,
    BLUE,
    CORAL,
    INK,
    MINT,
    MUTED,
    PANEL,
    PANEL_EDGE,
    VIOLET,
    AddSubtractConstruction,
    ChoiceRevealV2,
    ConsequencesAndPayoff,
    CriterionWorkedExamples,
    ProductQuotientConstruction,
    RichmondConstruction,
    SquareRootIntersection,
    StyledScene,
    WhySixteenDirections,
    card_heading,
    cn,
    panel,
    pill,
    polygon_group,
    polygon_points,
    title_group,
)


def need_icon(kind: str, color: str) -> VGroup:
    if kind == "join":
        left = Line(LEFT * 0.42, ORIGIN, color=BLUE, stroke_width=5.0)
        right = Line(ORIGIN, RIGHT * 0.46, color=AMBER, stroke_width=5.0)
        dots = VGroup(Dot(LEFT * 0.42, radius=0.045, color=INK), Dot(ORIGIN, radius=0.045, color=INK), Dot(RIGHT * 0.46, radius=0.045, color=INK))
        return VGroup(left, right, dots)
    if kind == "scale":
        small = Polygon(LEFT * 0.42 + DOWN * 0.24, LEFT * 0.05 + DOWN * 0.24, LEFT * 0.42 + UP * 0.06, color=BLUE, stroke_width=2.0)
        large = Polygon(LEFT * 0.05 + DOWN * 0.24, RIGHT * 0.44 + DOWN * 0.24, LEFT * 0.05 + UP * 0.20, color=MINT, stroke_width=2.0)
        return VGroup(small, large)
    circle = Circle(radius=0.26, color=AMBER, stroke_width=2.2)
    line = Line(LEFT * 0.42, RIGHT * 0.42, color=BLUE, stroke_width=2.2).shift(UP * 0.07)
    hits = VGroup(Dot(LEFT * 0.25 + UP * 0.07, radius=0.042, color=color), Dot(RIGHT * 0.25 + UP * 0.07, radius=0.042, color=color))
    return VGroup(circle, line, hits)


def need_row(text: str, operation: str, color: str, icon_kind: str) -> VGroup:
    box = RoundedRectangle(
        width=4.72,
        height=0.74,
        corner_radius=0.15,
        stroke_color=PANEL_EDGE,
        fill_color=PANEL,
        fill_opacity=0.88,
    )
    icon = need_icon(icon_kind, color).move_to(box.get_left() + RIGHT * 0.56)
    label = cn(text, 0.31, INK).move_to(box.get_left() + RIGHT * 2.05)
    arrow = Arrow(
        box.get_left() + RIGHT * 3.05,
        box.get_left() + RIGHT * 3.36,
        buff=0.03,
        color=MUTED,
        stroke_width=1.8,
        max_tip_length_to_length_ratio=0.30,
    )
    result = pill(operation, color, 1.16 if operation != "开平方" else 1.38)
    result.scale(0.88).move_to(box.get_left() + RIGHT * 4.02)
    return VGroup(box, icon, label, arrow, result)


class ChoiceRevealV3(ChoiceRevealV2):
    pass


class PolygonToOperationsBridge(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("要解释这次反转，先锁定一个顶点", "从正多边形真正需要的长度出发")

        center = np.array([-3.50, -0.38, 0.0])
        radius = 2.10
        alpha = TAU / 17
        circle = Circle(radius=radius, color=BLUE, stroke_width=2.0).move_to(center)
        polygon = polygon_group(17, radius, center, AMBER, rotation=0, stroke_width=2.1, dot_radius=0.035)
        x_axis = Arrow(center + LEFT * 2.42, center + RIGHT * 2.48, buff=0, color=MUTED, stroke_width=1.5, max_tip_length_to_length_ratio=0.07)
        y_axis = Arrow(center + DOWN * 2.32, center + UP * 2.36, buff=0, color=MUTED, stroke_width=1.5, max_tip_length_to_length_ratio=0.07)
        points = polygon_points(17, radius, center, rotation=0)
        fixed = Dot(points[0], radius=0.09, color=INK)
        fixed_label = cn("已知起点", 0.25, INK).next_to(fixed, RIGHT, buff=0.10)
        target = points[1]
        target_dot = Dot(target, radius=0.095, color=AMBER)
        radius_line = Line(center, target, color=AMBER, stroke_width=3.0)
        projection = DashedLine(target, [target[0], center[1], 0], color=MINT, stroke_width=2.2)
        x_segment = Line(center, [target[0], center[1], 0], color=MINT, stroke_width=5.0)
        target_label = MathTex("P", color=AMBER).scale(0.55).next_to(target_dot, UR, buff=0.08)
        x_label = MathTex("x", color=MINT).scale(0.58).next_to(x_segment, DOWN, buff=0.12)

        info = panel(5.45, 5.12).to_edge(RIGHT, buff=0.42).shift(DOWN * 0.28)
        first_heading = card_heading(info, "把图形任务变成长度任务")
        point_formula = MathTex(r"P=\left(\cos\frac{2\pi}{n},\ \sin\frac{2\pi}{n}\right)", color=INK).scale(0.63)
        point_formula.next_to(first_heading, DOWN, buff=0.50)
        x_formula = MathTex(r"x=\cos\frac{2\pi}{n}", color=MINT).scale(0.82).next_to(point_formula, DOWN, buff=0.40)
        goal = pill("先精确构造这段长度 x", MINT, 4.20).next_to(x_formula, DOWN, buff=0.48)
        handoff = Arrow(circle.get_right() + RIGHT * 0.08, info.get_left() + LEFT * 0.08, buff=0.06, color=MINT, stroke_width=2.2)

        second_heading = card_heading(info, "为了得到 x，会遇到三种几何需求")
        rows = VGroup(
            need_row("已有长度要拼接", "加、减", BLUE, "join"),
            need_row("长度要按比例缩放", "乘、除", VIOLET, "scale"),
            need_row("圆线交点给出新长度", "开平方", AMBER, "intersect"),
        ).arrange(DOWN, buff=0.18)
        rows.next_to(second_heading, DOWN, buff=0.40)
        summary = pill("这些运算不是清单，而是顶点坐标提出的需求", MINT, 4.82)
        summary.move_to(info.get_bottom() + UP * 0.44)

        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)
        self.play(Create(x_axis), Create(y_axis), Create(circle), FadeIn(polygon), FadeIn(info), FadeIn(first_heading), run_time=0.9)
        self.play(
            polygon[0].animate.set_stroke(opacity=0.18).set_fill(opacity=0),
            polygon[1].animate.set_opacity(0.18),
            FadeIn(fixed, scale=1.4),
            FadeIn(fixed_label),
            Create(radius_line),
            FadeIn(target_dot, scale=1.5),
            FadeIn(target_label),
            run_time=1.0,
        )
        self.play(Create(projection), Create(x_segment), FadeIn(x_label), GrowArrow(handoff), run_time=0.8)
        self.play(FadeOut(handoff), FadeIn(point_formula, shift=RIGHT * 0.22), FadeIn(x_formula, shift=RIGHT * 0.22), FadeIn(goal, shift=RIGHT * 0.22), run_time=0.9)
        self.wait(0.45)
        self.play(
            FadeOut(point_formula),
            FadeOut(x_formula),
            FadeOut(goal),
            ReplacementTransform(first_heading, second_heading),
            run_time=0.7,
        )

        for row in rows:
            self.play(FadeIn(row[0]), FadeIn(row[1]), FadeIn(row[2], shift=RIGHT * 0.16), run_time=0.7)
            self.wait(0.35)
            self.play(GrowArrow(row[3]), FadeIn(row[4], shift=RIGHT * 0.14), run_time=0.6)
            self.wait(0.50)

        self.play(FadeIn(summary, shift=UP * 0.10), Indicate(x_segment, color=MINT), run_time=0.8)
        self.wait(0.65)


class AddSubtractConstructionV3(AddSubtractConstruction):
    pass


class ProductQuotientConstructionV3(ProductQuotientConstruction):
    pass


class SquareRootIntersectionV3(SquareRootIntersection):
    pass


class WhySixteenDirectionsV3(WhySixteenDirections):
    pass


class CriterionWorkedExamplesV3(CriterionWorkedExamples):
    pass


class RichmondConstructionV3(RichmondConstruction):
    pass


class ConsequencesAndPayoffV3(ConsequencesAndPayoff):
    pass
