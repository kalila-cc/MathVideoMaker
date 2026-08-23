from __future__ import annotations

from pathlib import Path
import sys
import numpy as np

from manim import *


SCENE_DIR = Path(__file__).resolve().parent
if str(SCENE_DIR) not in sys.path:
    sys.path.insert(0, str(SCENE_DIR))

from constructible_17_gon_v1 import (  # noqa: E402
    AMBER,
    BG,
    BLUE,
    CORAL,
    FONT,
    GRID_COLOR,
    INK,
    MINT,
    MUTED,
    PANEL,
    PANEL_EDGE,
    VIOLET,
    ChoiceReveal,
    ExactVsApproximate,
    StyledScene,
    cn,
    panel,
    pill,
    polygon_group,
    polygon_points,
    title_group,
)


def labeled_dot(point: np.ndarray, label: str, color: str, direction=UP, radius: float = 0.065) -> VGroup:
    dot = Dot(point, radius=radius, color=color)
    text = MathTex(label, color=color).scale(0.46).next_to(dot, direction, buff=0.08)
    return VGroup(dot, text)


def segment_label(start: np.ndarray, end: np.ndarray, text: str, color: str, direction=UP) -> MathTex:
    label = MathTex(text, color=color).scale(0.52)
    label.move_to((start + end) / 2 + np.array(direction) * 0.28)
    return label


def card_heading(card: Mobject, text: str, color: str = INK) -> Text:
    return cn(text, 0.42, color).move_to(card.get_top() + DOWN * 0.42)


def operation_badge(symbol: str, text: str, color: str) -> VGroup:
    icon = Circle(radius=0.27, stroke_color=color, fill_color=color, fill_opacity=0.14)
    glyph = MathTex(symbol, color=color).scale(0.58).move_to(icon)
    label = cn(text, 0.28, color).next_to(icon, RIGHT, buff=0.12)
    return VGroup(icon, glyph, label)


class ChoiceRevealV2(ChoiceReveal):
    pass


class ExactVsApproximateV2(ExactVsApproximate):
    pass


class AddSubtractConstruction(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("加减法：圆规把长度搬到数轴上", "不读刻度，只复制已经存在的长度")

        y = -0.35
        O = np.array([-5.35, y, 0.0])
        A = np.array([-0.65, y, 0.0])
        b_len = 1.75
        D = A + LEFT * b_len
        C = A + RIGHT * b_len
        baseline = Line(O + LEFT * 0.25, C + RIGHT * 1.10, color=MUTED, stroke_width=2.0)

        known_a = Line(O, A, color=BLUE, stroke_width=6.0)
        source_b_start = np.array([2.65, 1.30, 0.0])
        source_b_end = source_b_start + RIGHT * b_len
        source_b = Line(source_b_start, source_b_end, color=AMBER, stroke_width=6.0)
        b_brace = BraceBetweenPoints(source_b_start, source_b_end, direction=UP, color=AMBER)
        b_label = MathTex("b", color=AMBER).scale(0.60).next_to(b_brace, UP, buff=0.08)

        points = VGroup(
            labeled_dot(O, "0", INK, DOWN),
            labeled_dot(A, "a", BLUE, DOWN),
        )
        compass_circle = Circle(radius=b_len, color=AMBER, stroke_width=2.4, stroke_opacity=0.78).move_to(A)
        result_points = VGroup(
            labeled_dot(D, "a-b", CORAL, DOWN),
            labeled_dot(C, "a+b", MINT, DOWN),
        )
        minus_seg = Line(O, D, color=CORAL, stroke_width=5.0).shift(DOWN * 0.08)
        plus_seg = Line(O, C, color=MINT, stroke_width=5.0).shift(UP * 0.08)

        ruler_badge = operation_badge(r"\rule{0.58cm}{0.6pt}", "直尺：建立同一条数轴", BLUE)
        compass_badge = operation_badge(r"\bigcirc", "圆规：把 b 搬到 a 的两侧", AMBER)
        tools = VGroup(ruler_badge, compass_badge).arrange(DOWN, aligned_edge=LEFT, buff=0.20)
        tools.to_corner(UR, buff=0.52).shift(DOWN * 0.80)

        minus_result = pill("左交点：a - b", CORAL, 3.00)
        plus_result = pill("右交点：a + b", MINT, 3.00)
        results = VGroup(minus_result, plus_result).arrange(RIGHT, buff=0.45).move_to(DOWN * 2.35)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(ruler_badge), run_time=0.7)
        self.play(Create(baseline), Create(known_a), FadeIn(points), run_time=1.0)
        self.wait(0.25)
        self.play(Create(source_b), GrowFromCenter(b_brace), FadeIn(b_label), FadeIn(compass_badge), run_time=0.9)
        self.wait(0.30)
        self.play(TransformFromCopy(source_b, compass_circle), run_time=1.1)
        self.play(FadeIn(result_points, scale=1.5), Create(minus_seg), Create(plus_seg), run_time=0.9)
        self.wait(0.35)
        self.play(FadeIn(results, shift=UP * 0.12), run_time=0.8)
        self.play(Indicate(result_points[0], color=CORAL), Indicate(result_points[1], color=MINT), run_time=0.8)
        self.wait(0.55)


class ProductQuotientConstruction(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("乘除法：相似三角形就是几何计算器", "平行线保持比例，目标长度出现在交点上")

        left_card = panel(6.15, 4.85).to_edge(LEFT, buff=0.42).shift(DOWN * 0.28)
        right_card = panel(6.15, 4.85).to_edge(RIGHT, buff=0.42).shift(DOWN * 0.28)
        left_title = card_heading(left_card, "乘法：已知 a、b，构造 ab")
        right_title = card_heading(right_card, "除法：已知 a、b，构造 a ÷ b")

        theta = 54 * DEGREES
        u = np.array([1.05, 0.0, 0.0])
        v = 1.05 * np.array([np.cos(theta), np.sin(theta), 0.0])
        a, b = 2.0, 1.35

        O1 = np.array([-5.75, -1.22, 0.0])
        U1, A1, B1, P1 = O1 + u, O1 + a * u, O1 + b * v, O1 + a * b * v
        rays1 = VGroup(
            Line(O1, O1 + RIGHT * 3.25, color=MUTED, stroke_width=1.8),
            Line(O1, O1 + v * 3.00, color=MUTED, stroke_width=1.8),
        )
        connector1 = Line(U1, B1, color=BLUE, stroke_width=2.4)
        parallel1 = Line(A1, P1, color=MINT, stroke_width=2.8)
        tri1_small = Polygon(O1, U1, B1, fill_color=BLUE, fill_opacity=0.08, stroke_opacity=0)
        tri1_big = Polygon(O1, A1, P1, fill_color=MINT, fill_opacity=0.08, stroke_opacity=0)
        labels1 = VGroup(
            labeled_dot(O1, "O", INK, DL),
            labeled_dot(U1, "1", BLUE, DOWN),
            labeled_dot(A1, "a", BLUE, DOWN),
            labeled_dot(B1, "b", AMBER, LEFT),
            labeled_dot(P1, "ab", MINT, UP),
        )
        ratio1 = MathTex(r"\frac{OP}{OB}=\frac{OA}{OU}=a\quad\Rightarrow\quad OP=ab", color=MINT).scale(0.57)
        ratio1.move_to(left_card.get_bottom() + UP * 0.47)

        O2 = np.array([1.02, -1.22, 0.0])
        A2, B2, U2 = O2 + a * u, O2 + b * v, O2 + v
        Q2 = O2 + (a / b) * u
        rays2 = VGroup(
            Line(O2, O2 + RIGHT * 3.55, color=MUTED, stroke_width=1.8),
            Line(O2, O2 + v * 2.25, color=MUTED, stroke_width=1.8),
        )
        connector2 = Line(B2, A2, color=VIOLET, stroke_width=2.4)
        parallel2 = Line(U2, Q2, color=AMBER, stroke_width=2.8)
        tri2_big = Polygon(O2, B2, A2, fill_color=VIOLET, fill_opacity=0.08, stroke_opacity=0)
        tri2_small = Polygon(O2, U2, Q2, fill_color=AMBER, fill_opacity=0.08, stroke_opacity=0)
        labels2 = VGroup(
            labeled_dot(O2, "O", INK, DL),
            labeled_dot(A2, "a", BLUE, DOWN),
            labeled_dot(B2, "b", VIOLET, LEFT),
            labeled_dot(U2, "1", AMBER, LEFT),
            labeled_dot(Q2, r"a/b", MINT, DOWN),
        )
        ratio2 = MathTex(r"\frac{OQ}{OA}=\frac{OU}{OB}=\frac1b\quad\Rightarrow\quad OQ=\frac ab", color=MINT).scale(0.57)
        ratio2.move_to(right_card.get_bottom() + UP * 0.47)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(left_card), FadeIn(right_card), run_time=0.7)
        self.play(FadeIn(left_title), FadeIn(right_title), Create(rays1), Create(rays2), run_time=0.8)
        self.play(FadeIn(labels1[:4]), FadeIn(labels2[:4]), run_time=0.6)
        self.play(Create(connector1), FadeIn(tri1_small), Create(connector2), FadeIn(tri2_big), run_time=0.9)
        self.wait(0.35)
        self.play(Create(parallel1), FadeIn(tri1_big), Create(parallel2), FadeIn(tri2_small), run_time=1.0)
        self.wait(0.45)
        self.play(FadeIn(labels1[4], scale=1.4), FadeIn(labels2[4], scale=1.4), run_time=0.6)
        self.wait(0.35)
        self.play(FadeIn(ratio1, shift=RIGHT * 0.22), FadeIn(ratio2, shift=RIGHT * 0.22), run_time=0.9)
        self.wait(0.45)
        self.play(Indicate(parallel1, color=MINT), Indicate(parallel2, color=AMBER), run_time=0.8)
        self.wait(0.55)


class SquareRootIntersection(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("开平方：根号就藏在圆与直线的交点里", "先实际构造 √a，再看它为什么必然出现")

        left_card = panel(6.25, 4.9).to_edge(LEFT, buff=0.40).shift(DOWN * 0.27)
        right_card = panel(5.95, 4.9).to_edge(RIGHT, buff=0.40).shift(DOWN * 0.27)
        left_title = card_heading(left_card, "半圆里的几何平均")
        right_title = card_heading(right_card, "同一个交点，用坐标看")

        A = np.array([-5.82, -1.25, 0.0])
        unit = 1.20
        aval = 2.0
        B = A + RIGHT * unit
        C = B + RIGHT * (aval * unit)
        midpoint = (A + C) / 2
        radius = np.linalg.norm(C - A) / 2
        height = np.sqrt(unit * aval * unit)
        H = B + UP * height
        baseline = Line(A + LEFT * 0.18, C + RIGHT * 0.18, color=MUTED, stroke_width=2.0)
        semicircle = Arc(radius=radius, start_angle=0, angle=PI, arc_center=midpoint, color=AMBER, stroke_width=2.7)
        vertical = Line(B, H, color=MINT, stroke_width=4.0)
        right_mark = RightAngle(Line(B, C), vertical, length=0.22, quadrant=(-1, 1), color=MUTED)
        geom_labels = VGroup(
            labeled_dot(A, "A", INK, DOWN),
            labeled_dot(B, "B", BLUE, DOWN),
            labeled_dot(C, "C", INK, DOWN),
            labeled_dot(H, "H", MINT, UP),
            segment_label(A, B, "1", BLUE, UP),
            segment_label(B, C, "a", AMBER, UP),
        )
        geom_formula = VGroup(
            MathTex(r"BH^2=AB\cdot BC=1\cdot a", color=INK).scale(0.62),
            MathTex(r"BH=\sqrt a", color=MINT).scale(0.76),
        ).arrange(DOWN, buff=0.18).move_to(left_card.get_bottom() + UP * 0.62)

        circle_center = np.array([3.28, 0.20, 0.0])
        r = 1.20
        t = 0.48
        coord_circle = Circle(radius=r, color=AMBER, stroke_width=2.5).move_to(circle_center)
        vertical_x = circle_center[0] + t
        yoff = np.sqrt(r**2 - t**2)
        secant = Line([vertical_x, circle_center[1] - 1.55, 0], [vertical_x, circle_center[1] + 1.55, 0], color=BLUE, stroke_width=2.5)
        hits = VGroup(
            Dot([vertical_x, circle_center[1] + yoff, 0], radius=0.075, color=MINT),
            Dot([vertical_x, circle_center[1] - yoff, 0], radius=0.075, color=MINT),
        )
        axis_x = Arrow(circle_center + LEFT * 1.55, circle_center + RIGHT * 1.58, buff=0, color=MUTED, stroke_width=1.4, max_tip_length_to_length_ratio=0.08)
        axis_y = Arrow(circle_center + DOWN * 1.48, circle_center + UP * 1.52, buff=0, color=MUTED, stroke_width=1.4, max_tip_length_to_length_ratio=0.08)
        eqs = VGroup(
            MathTex(r"x^2+y^2=r^2", color=AMBER).scale(0.56),
            MathTex(r"x=t", color=BLUE).scale(0.56),
            MathTex(r"y=\pm\sqrt{r^2-t^2}", color=MINT).scale(0.66),
        ).arrange(DOWN, buff=0.15).move_to(right_card.get_bottom() + UP * 0.70)
        handoff = Arrow(left_card.get_right() + RIGHT * 0.06, right_card.get_left() + LEFT * 0.06, buff=0.05, color=MINT, stroke_width=2.3)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(left_card), FadeIn(right_card), FadeIn(left_title), FadeIn(right_title), run_time=0.8)
        self.play(Create(baseline), Create(semicircle), FadeIn(geom_labels[:3]), run_time=1.0)
        self.play(Create(vertical), FadeIn(right_mark), FadeIn(geom_labels[3:]), run_time=0.9)
        self.play(FadeIn(geom_formula[0], shift=UP * 0.10), run_time=0.7)
        self.wait(0.35)
        self.play(FadeIn(geom_formula[1], shift=UP * 0.10), Indicate(vertical, color=MINT), run_time=0.7)
        self.wait(0.45)
        self.play(Create(axis_x), Create(axis_y), Create(coord_circle), Create(secant), run_time=0.9)
        self.play(FadeIn(hits, scale=1.5), GrowArrow(handoff), run_time=0.6)
        self.wait(0.35)
        self.play(FadeOut(handoff), FadeIn(eqs[0], shift=RIGHT * 0.18), FadeIn(eqs[1], shift=RIGHT * 0.18), run_time=0.7)
        self.wait(0.35)
        self.play(FadeIn(eqs[2], shift=RIGHT * 0.18), Indicate(hits, color=MINT), run_time=0.8)
        self.wait(0.45)
        self.wait(0.55)


class WhySixteenDirections(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("为什么谈十七边形，却先出现 16？", "因为单位圆上先固定了一个已知顶点")

        left_card = panel(6.05, 4.95).to_edge(LEFT, buff=0.43).shift(DOWN * 0.27)
        right_card = panel(6.05, 4.95).to_edge(RIGHT, buff=0.43).shift(DOWN * 0.27)
        left_title = card_heading(left_card, "正七边形")
        right_title = card_heading(right_card, "正十七边形")
        c7 = np.array([-3.65, -0.22, 0.0])
        c17 = np.array([3.65, -0.22, 0.0])
        radius = 1.42
        circle7 = Circle(radius=radius, color=MUTED, stroke_width=1.7).move_to(c7)
        circle17 = Circle(radius=radius, color=MUTED, stroke_width=1.7).move_to(c17)
        pts7 = polygon_points(7, radius, c7, rotation=0)
        pts17 = polygon_points(17, radius, c17, rotation=0)
        dots7 = VGroup(*[Dot(p, radius=0.065, color=CORAL) for p in pts7])
        dots17 = VGroup(*[Dot(p, radius=0.052, color=MINT) for p in pts17])
        fixed7 = VGroup(Dot(pts7[0], radius=0.105, color=INK), MathTex("1", color=INK).scale(0.42).next_to(pts7[0], RIGHT, buff=0.10))
        fixed17 = VGroup(Dot(pts17[0], radius=0.105, color=INK), MathTex("1", color=INK).scale(0.42).next_to(pts17[0], RIGHT, buff=0.10))
        fixed_note7 = pill("先固定 1 个顶点", INK, 2.45).move_to(left_card.get_top() + DOWN * 0.70)
        fixed_note17 = pill("先固定 1 个顶点", INK, 2.45).move_to(right_card.get_top() + DOWN * 0.70)
        count7 = MathTex(r"7-1=6=2\times3", color=CORAL).scale(0.72).move_to(left_card.get_bottom() + UP * 0.40)
        count17 = MathTex(r"17-1=16=2^4", color=MINT).scale(0.72).move_to(right_card.get_bottom() + UP * 0.40)
        issue7 = cn("6 个方向里还留下因子 3", 0.30, CORAL).next_to(circle7, DOWN, buff=0.12)
        hope17 = cn("16 个方向可以连续二分", 0.30, MINT).next_to(circle17, DOWN, buff=0.12)
        scope_note = pill("这只是结构线索；完整结论由判据确认", VIOLET, 5.10).move_to(UP * 2.28)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(left_card), FadeIn(right_card), FadeIn(left_title), FadeIn(right_title), run_time=0.8)
        self.play(Create(circle7), Create(circle17), FadeIn(dots7), FadeIn(dots17), run_time=0.9)
        self.play(
            dots7[0].animate.set_opacity(0),
            dots17[0].animate.set_opacity(0),
            FadeIn(fixed7, scale=1.5),
            FadeIn(fixed17, scale=1.5),
            FadeIn(fixed_note7),
            FadeIn(fixed_note17),
            run_time=0.9,
        )
        self.wait(0.45)
        self.play(LaggedStart(*[Indicate(dot, color=CORAL, scale_factor=1.20) for dot in dots7[1:]], lag_ratio=0.08), run_time=0.9)
        self.play(FadeIn(count7, shift=RIGHT * 0.20), FadeIn(issue7, shift=UP * 0.10), run_time=0.7)
        self.wait(0.40)
        self.play(LaggedStart(*[Indicate(dot, color=MINT, scale_factor=1.18) for dot in dots17[1:]], lag_ratio=0.035), run_time=1.0)
        self.play(FadeIn(count17, shift=RIGHT * 0.20), FadeIn(hope17, shift=UP * 0.10), run_time=0.7)
        self.wait(0.40)
        self.play(FadeIn(scope_note, shift=DOWN * 0.10), run_time=0.7)
        self.wait(0.40)
        self.wait(0.55)


class CriterionWorkedExamples(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("现在现场代入判据", "不是看数字大小，而是检查它由哪些因子组成")
        theorem_box = RoundedRectangle(width=8.35, height=0.76, corner_radius=0.18, stroke_color=VIOLET, fill_color=VIOLET, fill_opacity=0.11)
        theorem_formula = MathTex(r"n=2^k p_1p_2\cdots p_m", color=MINT).scale(0.68)
        theorem_text = cn("每个 p 都是互不相同的费马素数", 0.32, INK)
        theorem_content = VGroup(theorem_formula, theorem_text).arrange(RIGHT, buff=0.42).move_to(theorem_box)
        theorem = VGroup(theorem_box, theorem_content).move_to(UP * 2.34)

        left_card = panel(5.95, 4.35, CORAL).to_edge(LEFT, buff=0.50).shift(DOWN * 0.70)
        right_card = panel(5.95, 4.35, MINT).to_edge(RIGHT, buff=0.50).shift(DOWN * 0.70)
        left_title = card_heading(left_card, "检查 7", CORAL)
        right_title = card_heading(right_card, "检查 17", MINT)

        left_factor = VGroup(cn("奇数因子", 0.34, AMBER), MathTex("=7", color=AMBER).scale(0.64)).arrange(RIGHT, buff=0.12)
        right_prime = VGroup(MathTex("17", color=MINT).scale(0.64), cn("是素数", 0.34, MINT)).arrange(RIGHT, buff=0.12)
        left_rows = VGroup(
            MathTex(r"7=2^0\times7", color=INK).scale(0.70),
            left_factor,
            MathTex(r"7\notin\{3,5,17,257,\ldots\}", color=CORAL).scale(0.60),
            pill("失败点：7 不是费马素数", CORAL, 4.20),
        ).arrange(DOWN, buff=0.28).next_to(left_title, DOWN, buff=0.40)
        right_rows = VGroup(
            MathTex(r"17=2^0\times17", color=INK).scale(0.70),
            MathTex(r"17=2^{2^2}+1", color=AMBER).scale(0.70),
            right_prime,
            pill("通过：17 本身就是费马素数", MINT, 4.30),
        ).arrange(DOWN, buff=0.28).next_to(right_title, DOWN, buff=0.40)

        arrows_left = VGroup(*[
            Arrow(left_rows[i].get_bottom(), left_rows[i + 1].get_top(), buff=0.06, color=MUTED, stroke_width=1.6)
            for i in range(2)
        ])
        arrows_right = VGroup(*[
            Arrow(right_rows[i].get_bottom(), right_rows[i + 1].get_top(), buff=0.06, color=MUTED, stroke_width=1.6)
            for i in range(2)
        ])

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(theorem), run_time=0.8)
        self.play(FadeIn(left_card), FadeIn(right_card), FadeIn(left_title), FadeIn(right_title), run_time=0.6)
        for i in range(3):
            anims = [FadeIn(left_rows[i], shift=RIGHT * 0.20), FadeIn(right_rows[i], shift=RIGHT * 0.20)]
            if i > 0:
                anims += [GrowArrow(arrows_left[i - 1]), GrowArrow(arrows_right[i - 1])]
            self.play(*anims, run_time=0.75)
            self.wait(0.35 if i == 0 else 0.45)
        self.play(FadeIn(left_rows[3], shift=UP * 0.10), FadeIn(right_rows[3], shift=UP * 0.10), run_time=0.8)
        self.wait(0.55)
        self.play(Indicate(left_rows[2], color=CORAL), Indicate(right_rows[1], color=MINT), run_time=0.8)
        self.wait(0.55)


class RichmondConstruction(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("真正画一次正十七边形", "经典作法先精确得到 P3、P5，再得到一条真实边长")

        steps_panel = panel(4.35, 5.35).to_edge(RIGHT, buff=0.38).shift(DOWN * 0.28)
        steps_title = card_heading(steps_panel, "当前尺规步骤")
        step_texts = [
            "取 OI = 半径的四分之一",
            "连续平分 ∠OIA 两次",
            "平分直角，射线落到 F",
            "两个辅助圆得到 N3、N5",
            "作垂线，得到 P3、P5",
            "平分夹角并复制边长",
        ]
        step_rows = VGroup()
        for idx, text in enumerate(step_texts, start=1):
            box = RoundedRectangle(width=3.72, height=0.55, corner_radius=0.13, stroke_color=PANEL_EDGE, fill_color=PANEL, fill_opacity=0.82)
            number = Circle(radius=0.18, stroke_color=MUTED, fill_color=MUTED, fill_opacity=0.10)
            number_text = MathTex(str(idx), color=MUTED).scale(0.38).move_to(number)
            label = cn(text, 0.27, MUTED)
            row = VGroup(box, number, number_text, label)
            number.move_to(box.get_left() + RIGHT * 0.34)
            number_text.move_to(number)
            label.move_to(box.get_left() + RIGHT * 2.08)
            step_rows.add(row)
        step_rows.arrange(DOWN, buff=0.09).next_to(steps_title, DOWN, buff=0.34)
        speed_note = pill("首尾慢 · 中段加速", AMBER, 3.35).move_to(steps_panel.get_bottom() + UP * 0.32)

        O = np.array([-2.72, -0.52, 0.0])
        R = 2.35
        A = O + RIGHT * R
        B = O + UP * R
        Cang = np.arctan(4.0) / 4.0
        e0 = 0.25 * np.tan(Cang)
        f0 = 0.25 * np.tan(Cang - PI / 4)
        E = O + RIGHT * (R * e0)
        F = O + RIGHT * (R * f0)
        I = O + UP * (R / 4)
        J = O + RIGHT * (R * 0.25 * np.tan(2 * Cang))
        K = O + UP * (R * np.sqrt(-f0))
        e_radius = R * np.sqrt(e0**2 - f0)
        N3 = O + RIGHT * (R * (e0 + e_radius / R))
        N5 = O + RIGHT * (R * (e0 - e_radius / R))
        alpha = TAU / 17
        P3 = O + R * np.array([np.cos(3 * alpha), np.sin(3 * alpha), 0.0])
        P4 = O + R * np.array([np.cos(4 * alpha), np.sin(4 * alpha), 0.0])
        P5 = O + R * np.array([np.cos(5 * alpha), np.sin(5 * alpha), 0.0])

        base_circle = Circle(radius=R, color=BLUE, stroke_width=2.0).move_to(O)
        horizontal = Line(O + LEFT * R * 0.62, A + RIGHT * 0.10, color=MUTED, stroke_width=1.9)
        vertical_radius = Line(O, B, color=MUTED, stroke_width=1.9)
        right_angle = RightAngle(horizontal, vertical_radius, length=0.26, quadrant=(1, 1), color=MUTED)
        base_labels = VGroup(labeled_dot(O, "O", INK, DL), labeled_dot(A, "A", INK, DR), labeled_dot(B, "B", INK, UR))

        oi = Line(O, I, color=AMBER, stroke_width=4.0)
        oi_brace = BraceBetweenPoints(O, I, direction=LEFT, color=AMBER)
        oi_label = MathTex(r"R/4", color=AMBER).scale(0.45).next_to(oi_brace, LEFT, buff=0.06)
        i_label = labeled_dot(I, "I", AMBER, UL)
        ia = Line(I, A, color=MUTED, stroke_width=1.6)

        ray_2c = Line(I, J, color=VIOLET, stroke_width=2.0)
        ray_c = Line(I, E, color=MINT, stroke_width=2.6)
        e_label = labeled_dot(E, "E", MINT, DR)
        full_angle = Arc(radius=0.40, start_angle=-PI / 2, angle=4 * Cang, arc_center=I, color=MUTED, stroke_width=1.8)
        quarter_angle = Arc(radius=0.29, start_angle=-PI / 2, angle=Cang, arc_center=I, color=MINT, stroke_width=2.6)

        ray_f = Line(I, F, color=AMBER, stroke_width=2.5)
        f_label = labeled_dot(F, "F", AMBER, DL)
        angle_45 = Arc(radius=0.35, start_angle=np.arctan2((F - I)[1], (F - I)[0]), angle=PI / 4, arc_center=I, color=AMBER, stroke_width=2.2)
        angle_45_label = MathTex(r"45^\circ", color=AMBER).scale(0.38).next_to(angle_45, LEFT, buff=0.05)

        af_circle = Circle(radius=np.linalg.norm(A - F) / 2, color=VIOLET, stroke_width=2.0, stroke_opacity=0.80).move_to((A + F) / 2)
        k_label = labeled_dot(K, "K", VIOLET, UL)
        ek = Line(E, K, color=MINT, stroke_width=2.0)
        e_circle = Circle(radius=e_radius, color=MINT, stroke_width=2.2, stroke_opacity=0.88).move_to(E)
        n3_label = labeled_dot(N3, r"N_3", MINT, DR)
        n5_label = labeled_dot(N5, r"N_5", MINT, DL)

        v3 = Line(N3, P3, color=MINT, stroke_width=2.3)
        v5 = Line(N5, P5, color=MINT, stroke_width=2.3)
        p3_label = labeled_dot(P3, r"P_3", MINT, UR)
        p5_label = labeled_dot(P5, r"P_5", MINT, UL)
        r3 = Line(O, P3, color=MINT, stroke_width=2.0)
        r5 = Line(O, P5, color=MINT, stroke_width=2.0)
        r4 = Line(O, P4, color=AMBER, stroke_width=2.7)
        p4_label = labeled_dot(P4, r"P_4", AMBER, UP)
        side = Line(P3, P4, color=AMBER, stroke_width=5.0)
        side_badge = pill("P3P4 就是一条边", AMBER, 3.05).move_to(steps_panel.get_bottom() + UP * 0.32)

        def activate_step(index: int, previous: int | None = None, run_time: float = 0.35):
            animations = []
            if previous is not None:
                animations += [
                    step_rows[previous][0].animate.set_stroke(PANEL_EDGE).set_fill(PANEL, opacity=0.82),
                    step_rows[previous][1].animate.set_stroke(MUTED).set_fill(MUTED, opacity=0.10),
                    step_rows[previous][2].animate.set_color(MUTED),
                    step_rows[previous][3].animate.set_color(MUTED),
                ]
            animations += [
                step_rows[index][0].animate.set_stroke(MINT).set_fill(MINT, opacity=0.14),
                step_rows[index][1].animate.set_stroke(MINT).set_fill(MINT, opacity=0.18),
                step_rows[index][2].animate.set_color(MINT),
                step_rows[index][3].animate.set_color(INK),
            ]
            self.play(*animations, run_time=run_time)

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(steps_panel), FadeIn(steps_title), FadeIn(step_rows), run_time=0.8)
        self.play(Create(base_circle), Create(horizontal), Create(vertical_radius), FadeIn(right_angle), FadeIn(base_labels), run_time=1.1)

        activate_step(0)
        self.play(Create(oi), GrowFromCenter(oi_brace), FadeIn(oi_label), FadeIn(i_label), Create(ia), run_time=1.1)
        self.wait(0.35)

        activate_step(1, 0)
        self.play(Create(full_angle), Create(ray_2c), run_time=0.8)
        self.play(Create(ray_c), Create(quarter_angle), FadeIn(e_label, scale=1.4), run_time=0.9)
        self.wait(0.35)

        activate_step(2, 1)
        self.play(Create(ray_f), Create(angle_45), FadeIn(angle_45_label), FadeIn(f_label, scale=1.4), run_time=1.0)
        self.wait(0.35)

        activate_step(3, 2)
        self.play(Create(af_circle), FadeIn(k_label, scale=1.4), run_time=0.9)
        self.play(Create(ek), Create(e_circle), FadeIn(n3_label, scale=1.3), FadeIn(n5_label, scale=1.3), run_time=1.0)
        self.wait(0.40)

        activate_step(4, 3)
        self.play(Create(v3), Create(v5), FadeIn(p3_label, scale=1.3), FadeIn(p5_label, scale=1.3), run_time=1.0)
        self.play(Create(r3), Create(r5), run_time=0.6)
        self.wait(0.35)

        activate_step(5, 4)
        self.play(Create(r4), FadeIn(p4_label, scale=1.3), run_time=0.7)
        self.play(Create(side), FadeOut(speed_note), FadeIn(side_badge, shift=UP * 0.08), run_time=0.8)
        self.wait(0.65)

        helpers = VGroup(horizontal, vertical_radius, right_angle, oi, oi_brace, oi_label, ia, ray_2c, ray_c, full_angle, quarter_angle, ray_f, angle_45, angle_45_label, af_circle, ek, e_circle, v3, v5, r3, r4, r5)
        point_labels = VGroup(i_label, e_label, f_label, k_label, n3_label, n5_label, p3_label, p4_label, p5_label)
        self.play(helpers.animate.set_opacity(0.18), point_labels.animate.set_opacity(0.32), FadeOut(side_badge), FadeIn(speed_note), run_time=0.7)

        vertices = [O + R * np.array([np.cos((3 + k) * alpha), np.sin((3 + k) * alpha), 0.0]) for k in range(17)]
        side_len = np.linalg.norm(vertices[1] - vertices[0])
        compass_circle = Circle(radius=side_len, color=AMBER, stroke_width=2.0, stroke_opacity=0.60).move_to(vertices[0])
        vertex_dots = VGroup(Dot(vertices[0], radius=0.055, color=AMBER))
        edges = VGroup()
        self.play(Create(compass_circle), FadeIn(vertex_dots), run_time=0.6)
        for k in range(17):
            start = vertices[k]
            end = vertices[(k + 1) % 17]
            edge = Line(start, end, color=AMBER, stroke_width=3.0)
            edges.add(edge)
            new_dot = Dot(end, radius=0.055, color=AMBER)
            vertex_dots.add(new_dot)
            if k < 2 or k >= 14:
                rt = 0.46
            else:
                rt = 0.11
            self.play(compass_circle.animate.move_to(start), Create(edge), FadeIn(new_dot, scale=1.4), run_time=rt, rate_func=linear)
        self.play(FadeOut(compass_circle), helpers.animate.set_opacity(0.06), point_labels.animate.set_opacity(0.12), Indicate(edges, color=AMBER, scale_factor=1.015), run_time=0.9)
        self.wait(0.65)


class ConsequencesAndPayoff(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("边数从来不是尺规难度表", "判据还能给出一些很反直觉的结论")

        center = LEFT * 3.55 + DOWN * 0.35
        radius = 2.10
        circle = Circle(radius=radius, color=BLUE, stroke_width=2.0).move_to(center)
        poly17 = polygon_group(17, radius * 0.97, center, AMBER, rotation=0, stroke_width=2.8, dot_radius=0.045)
        poly34 = polygon_group(34, radius * 0.97, center, MINT, rotation=0, stroke_width=2.2, dot_radius=0.028)
        poly68 = polygon_group(68, radius * 0.97, center, VIOLET, rotation=0, stroke_width=1.8, dot_radius=0.018)
        n_label = MathTex("17", color=AMBER).scale(0.84).next_to(circle, DOWN, buff=0.18)
        double_arrow1 = Arrow(LEFT * 0.45, RIGHT * 0.45, color=MINT, stroke_width=2.0)
        double_arrow2 = Arrow(LEFT * 0.45, RIGHT * 0.45, color=VIOLET, stroke_width=2.0)
        chain = VGroup(
            MathTex("17", color=AMBER).scale(0.72),
            double_arrow1,
            MathTex("34", color=MINT).scale(0.72),
            double_arrow2,
            MathTex("68", color=VIOLET).scale(0.72),
        ).arrange(RIGHT, buff=0.20).move_to(UP * 2.25 + LEFT * 3.55)
        chain_note = cn("每次平分圆心角，边数翻倍", 0.31, MUTED).next_to(chain, DOWN, buff=0.10)

        info = panel(5.75, 4.95).to_edge(RIGHT, buff=0.42).shift(DOWN * 0.27)
        info_title = card_heading(info, "三个轻量结论")
        row1 = VGroup(
            pill("9 不行", CORAL, 1.65),
            MathTex(r"9=3^2", color=CORAL).scale(0.62),
            cn("费马素数重复了", 0.29, MUTED),
        ).arrange(RIGHT, buff=0.24)
        row2 = VGroup(
            pill("15 可以", MINT, 1.65),
            MathTex(r"15=3\times5", color=MINT).scale(0.62),
            cn("两个因子互不相同", 0.29, MUTED),
        ).arrange(RIGHT, buff=0.24)
        row3 = VGroup(
            cn("257、65537", 0.38, AMBER),
            cn("理论上也能精确构造，只是边会非常密", 0.29, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        divider1 = Line(LEFT * 2.25, RIGHT * 2.25, color=PANEL_EDGE, stroke_width=1.3)
        divider2 = divider1.copy()
        rows = VGroup(row1, divider1, row2, divider2, row3).arrange(DOWN, buff=0.30, aligned_edge=LEFT)
        rows.next_to(info_title, DOWN, buff=0.46)
        closing = pill("能否精确构造，看因子结构，不看边数多少", VIOLET, 5.05).move_to(info.get_bottom() + UP * 0.48)

        self.play(FadeIn(title, shift=DOWN * 0.12), Create(circle), FadeIn(poly17), FadeIn(n_label), FadeIn(info), FadeIn(info_title), run_time=0.9)
        self.play(FadeIn(chain[0]), FadeIn(chain_note), run_time=0.5)
        self.play(GrowArrow(chain[1]), ReplacementTransform(poly17, poly34), Transform(n_label, MathTex("34", color=MINT).scale(0.84).move_to(n_label)), FadeIn(chain[2]), run_time=1.0)
        self.play(GrowArrow(chain[3]), ReplacementTransform(poly34, poly68), Transform(n_label, MathTex("68", color=VIOLET).scale(0.84).move_to(n_label)), FadeIn(chain[4]), run_time=1.0)
        self.play(FadeIn(row1, shift=RIGHT * 0.18), run_time=0.7)
        self.wait(0.35)
        self.play(Create(divider1), FadeIn(row2, shift=RIGHT * 0.18), run_time=0.7)
        self.wait(0.35)
        self.play(Create(divider2), FadeIn(row3, shift=RIGHT * 0.18), run_time=0.7)
        self.wait(0.40)
        self.play(FadeIn(closing, shift=UP * 0.10), Indicate(poly68, color=VIOLET, scale_factor=1.02), run_time=0.9)
        self.wait(0.65)
