from __future__ import annotations

from pathlib import Path
import numpy as np

from manim import *


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SMILEY_FONT_FILE = PROJECT_ROOT / "assets" / "fonts" / "SmileySans-Oblique.ttf"
FONT = "Smiley Sans"

BG = "#07121C"
PANEL = "#0D1D2A"
PANEL_EDGE = "#29465D"
INK = "#F7F3E8"
MUTED = "#A9BBCB"
GRID_COLOR = "#8FA8D8"
CORAL = "#FF6B6B"
AMBER = "#F4B942"
MINT = "#63D7B0"
BLUE = "#79C7FF"
VIOLET = "#C9A7FF"

TIMES_TEX_TEMPLATE = TexTemplate()
TIMES_TEX_TEMPLATE.add_to_preamble(r"\usepackage{mathptmx}")
MathTex.set_default(tex_template=TIMES_TEX_TEMPLATE)


def cn(text: str, size: float = 0.36, color: str = INK) -> Text:
    return Text(text, font=FONT, slant=OBLIQUE, color=color).scale(size)


def make_grid() -> VGroup:
    lines = VGroup()
    spacing = 0.48
    x = -config.frame_width / 2
    while x <= config.frame_width / 2 + 0.01:
        lines.add(
            Line(
                [x, -config.frame_height / 2, 0],
                [x, config.frame_height / 2, 0],
                color=GRID_COLOR,
                stroke_width=1.6,
                stroke_opacity=0.155,
            )
        )
        x += spacing
    y = -config.frame_height / 2
    while y <= config.frame_height / 2 + 0.01:
        lines.add(
            Line(
                [-config.frame_width / 2, y, 0],
                [config.frame_width / 2, y, 0],
                color=GRID_COLOR,
                stroke_width=1.6,
                stroke_opacity=0.155,
            )
        )
        y += spacing
    lines.set_z_index(-10)
    return lines


def title_group(title: str, subtitle: str | None = None) -> VGroup:
    main = cn(title, 0.52, INK).to_edge(UP, buff=0.28)
    if subtitle is None:
        return VGroup(main)
    sub = cn(subtitle, 0.29, MUTED).next_to(main, DOWN, buff=0.10)
    return VGroup(main, sub)


def panel(width: float, height: float, edge: str = PANEL_EDGE) -> RoundedRectangle:
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.22,
        stroke_color=edge,
        stroke_width=1.5,
        fill_color=PANEL,
        fill_opacity=0.94,
    )


def pill(text: str, color: str, width: float | None = None) -> VGroup:
    label = cn(text, 0.31, color)
    box_width = width if width is not None else max(1.55, label.width + 0.48)
    box = RoundedRectangle(
        width=box_width,
        height=0.58,
        corner_radius=0.18,
        stroke_color=color,
        stroke_width=1.5,
        fill_color=color,
        fill_opacity=0.12,
    )
    label.move_to(box)
    return VGroup(box, label)


def polygon_points(n: int, radius: float, center: np.ndarray, rotation: float = PI / 2) -> list[np.ndarray]:
    return [
        center + radius * np.array([np.cos(rotation + TAU * k / n), np.sin(rotation + TAU * k / n), 0.0])
        for k in range(n)
    ]


def polygon_group(
    n: int,
    radius: float,
    center: np.ndarray,
    color: str,
    rotation: float = PI / 2,
    stroke_width: float = 2.4,
    dot_radius: float = 0.045,
) -> VGroup:
    points = polygon_points(n, radius, center, rotation)
    outline = Polygon(*points, color=color, stroke_width=stroke_width, fill_opacity=0)
    dots = VGroup(*[Dot(point, radius=dot_radius, color=color) for point in points])
    return VGroup(outline, dots)


def mini_polygon(n: int, status: bool, center: np.ndarray) -> VGroup:
    color = MINT if status else CORAL
    circle = Circle(radius=0.58, color=MUTED, stroke_width=1.2, stroke_opacity=0.45).move_to(center)
    poly = polygon_group(n, 0.54, center, color, stroke_width=1.8, dot_radius=0.025)
    label = MathTex(str(n), color=INK).scale(0.52).next_to(circle, DOWN, buff=0.13)
    badge = cn("可构造" if status else "不可构造", 0.23, color).next_to(label, DOWN, buff=0.06)
    return VGroup(circle, poly, label, badge)


class StyledScene(Scene):
    def begin_scene(self) -> None:
        self.camera.background_color = BG
        self.add(make_grid())


class ChoiceReveal(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("哪一个更容易精确画出？", "只允许无刻度直尺和圆规")

        left_center = LEFT * 3.45 + DOWN * 0.35
        right_center = RIGHT * 3.45 + DOWN * 0.35
        left_circle = Circle(radius=1.78, color=MUTED, stroke_width=2.0).move_to(left_center)
        right_circle = Circle(radius=1.78, color=MUTED, stroke_width=2.0).move_to(right_center)
        seven = polygon_group(7, 1.69, left_center, CORAL, rotation=PI / 2)
        seventeen = polygon_group(17, 1.69, right_center, AMBER, rotation=PI / 2)
        seven_name = cn("正七边形", 0.42, INK).next_to(left_circle, DOWN, buff=0.24)
        seventeen_name = cn("正十七边形", 0.42, INK).next_to(right_circle, DOWN, buff=0.24)

        intuition = pill("直觉：边少，应该更容易", BLUE, 4.35).move_to(DOWN * 3.15)
        left_result = pill("不能精确构造", CORAL, 3.25).next_to(left_circle, DOWN, buff=0.18)
        right_result = pill("可以精确构造", MINT, 3.25).next_to(right_circle, DOWN, buff=0.18)

        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.7)
        self.play(Create(left_circle), Create(right_circle), run_time=0.8)
        self.play(
            LaggedStart(Create(seven[0]), FadeIn(seven[1]), lag_ratio=0.25),
            LaggedStart(Create(seventeen[0]), FadeIn(seventeen[1]), lag_ratio=0.25),
            run_time=1.4,
        )
        self.play(FadeIn(seven_name), FadeIn(seventeen_name), run_time=0.6)
        self.play(FadeIn(intuition, shift=UP * 0.12), run_time=0.7)
        self.play(
            FadeOut(intuition),
            FadeOut(seven_name),
            FadeOut(seventeen_name),
            seven[0].animate.set_stroke(opacity=0.42),
            seventeen[0].animate.set_stroke(width=4.0),
            run_time=0.7,
        )
        self.play(FadeIn(left_result, shift=UP * 0.14), FadeIn(right_result, shift=UP * 0.14), run_time=1.0)
        self.play(Indicate(right_result, color=MINT, scale_factor=1.04), run_time=0.7)
        self.wait(0.45)


class ExactVsApproximate(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("差一点，也不算精确", "近似方法能画得很像，但误差不会消失")

        center = LEFT * 2.45 + DOWN * 0.35
        radius = 2.28
        circle = Circle(radius=radius, color=MUTED, stroke_width=2.0).move_to(center)
        start_angle = PI / 2
        step = -51 * DEGREES
        approx_points = [
            center + radius * np.array([np.cos(start_angle + k * step), np.sin(start_angle + k * step), 0.0])
            for k in range(8)
        ]
        edges = VGroup(
            *[
                Line(approx_points[k], approx_points[k + 1], color=CORAL, stroke_width=3.0)
                for k in range(7)
            ]
        )
        dots = VGroup(*[Dot(point, radius=0.055, color=CORAL) for point in approx_points])
        gap_arc = Arc(
            radius=radius,
            start_angle=start_angle + 7 * step,
            angle=-3 * DEGREES,
            arc_center=center,
            color=AMBER,
            stroke_width=8,
        )
        gap_label = cn("还差 3°", 0.32, AMBER).next_to(circle, UP, buff=0.05).shift(RIGHT * 0.62)

        info = panel(4.65, 4.65).to_edge(RIGHT, buff=0.48).shift(DOWN * 0.20)
        info_title = cn("复制同一个 51° 角", 0.38, INK).move_to(info.get_top() + DOWN * 0.48)
        rows = VGroup(
            MathTex(r"7\times 51^\circ=357^\circ", color=CORAL).scale(0.72),
            MathTex(r"\frac{360^\circ}{7}\approx51.428571^\circ", color=AMBER).scale(0.60),
        ).arrange(DOWN, buff=0.52)
        rows.next_to(info_title, DOWN, buff=0.58)
        divider = Line(LEFT * 1.75, RIGHT * 1.75, color=PANEL_EDGE, stroke_width=1.5).next_to(rows, DOWN, buff=0.48)
        note = VGroup(
            cn("现实绘图：可以近似", 0.31, MINT),
            cn("古典尺规：要求严格闭合", 0.31, CORAL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).next_to(divider, DOWN, buff=0.36)
        handoff = Arrow(
            circle.get_right() + RIGHT * 0.10,
            info.get_left() + LEFT * 0.10,
            buff=0.08,
            color=AMBER,
            stroke_width=2.2,
            max_tip_length_to_length_ratio=0.18,
        )

        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.6)
        self.play(Create(circle), FadeIn(info), FadeIn(info_title), run_time=0.8)
        self.play(LaggedStart(*[Create(edge) for edge in edges], lag_ratio=0.14), FadeIn(dots), run_time=2.6)
        self.play(Create(gap_arc), FadeIn(gap_label, shift=DOWN * 0.10), run_time=0.8)
        self.play(GrowArrow(handoff), FadeIn(rows[0], shift=RIGHT * 0.32), run_time=0.9)
        self.play(FadeIn(rows[1], shift=RIGHT * 0.32), run_time=0.6)
        self.play(FadeOut(handoff), Create(divider), FadeIn(note, shift=RIGHT * 0.24), run_time=1.0)
        self.play(Indicate(gap_arc, color=AMBER, scale_factor=1.03), run_time=0.7)
        self.wait(0.4)


class ToolArithmetic(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("尺规交点，最多带来二次方程", "真正的限制不是手巧，而是允许出现哪类数字")

        left_card = panel(5.6, 4.8).to_edge(LEFT, buff=0.45).shift(DOWN * 0.25)
        right_card = panel(6.25, 4.8).to_edge(RIGHT, buff=0.45).shift(DOWN * 0.25)

        left_title = cn("每次新增一个交点", 0.38, INK).move_to(left_card.get_top() + DOWN * 0.44)
        l1 = Line(LEFT * 2.0, RIGHT * 2.0, color=BLUE, stroke_width=2.4).rotate(18 * DEGREES)
        l2 = Line(LEFT * 1.8, RIGHT * 1.8, color=MINT, stroke_width=2.4).rotate(-25 * DEGREES)
        lines = VGroup(l1, l2).scale(0.75).move_to(left_card.get_center() + LEFT * 1.25 + UP * 0.35)
        intersection = Dot(lines.get_center(), radius=0.075, color=INK)
        linear_label = pill("一次关系", BLUE, 1.75).next_to(lines, DOWN, buff=0.26)

        small_circle = Circle(radius=0.98, color=AMBER, stroke_width=2.4).move_to(left_card.get_center() + RIGHT * 1.42 + UP * 0.35)
        secant = Line(LEFT * 1.25, RIGHT * 1.25, color=VIOLET, stroke_width=2.4).move_to(small_circle).shift(UP * 0.20)
        dx = np.sqrt(0.98**2 - 0.20**2)
        hit_y = small_circle.get_center()[1] + 0.20
        hits = VGroup(
            Dot([small_circle.get_center()[0] - dx, hit_y, 0], radius=0.07, color=INK),
            Dot([small_circle.get_center()[0] + dx, hit_y, 0], radius=0.07, color=INK),
        )
        quadratic_label = pill("二次关系", AMBER, 1.75).next_to(small_circle, DOWN, buff=0.26)

        right_title = cn("可构造长度的运算表", 0.38, INK).move_to(right_card.get_top() + DOWN * 0.44)
        operation_specs = [
            ("+", BLUE),
            ("-", BLUE),
            (r"\times", MINT),
            (r"\div", MINT),
            (r"\sqrt{\phantom{x}}", AMBER),
        ]
        operations = VGroup(
            *[
                VGroup(
                    RoundedRectangle(
                        width=0.78,
                        height=0.68,
                        corner_radius=0.14,
                        stroke_color=color,
                        fill_color=color,
                        fill_opacity=0.12,
                    ),
                    MathTex(symbol, color=color).scale(0.68),
                )
                for symbol, color in operation_specs
            ]
        ).arrange(RIGHT, buff=0.24)
        for chip in operations:
            chip[1].move_to(chip[0])
        operations.next_to(right_title, DOWN, buff=0.48)

        ladder = VGroup(
            MathTex(r"a", color=BLUE).scale(0.72),
            MathTex(r"\sqrt{a}", color=MINT).scale(0.72),
            MathTex(r"\sqrt{b+\sqrt a}", color=AMBER).scale(0.72),
        ).arrange(RIGHT, buff=0.65)
        ladder.next_to(operations, DOWN, buff=0.62)
        arrows = VGroup(
            Arrow(ladder[0].get_right(), ladder[1].get_left(), buff=0.10, color=MUTED, stroke_width=2.0),
            Arrow(ladder[1].get_right(), ladder[2].get_left(), buff=0.10, color=MUTED, stroke_width=2.0),
        )
        degree_line = MathTex(r"1\ \longrightarrow\ 2\ \longrightarrow\ 4\ \longrightarrow\ 8\ \longrightarrow\ \cdots", color=VIOLET).scale(0.68)
        degree_line.next_to(ladder, DOWN, buff=0.54)
        summary = pill("代数次数只能不断乘 2", VIOLET, 4.65).next_to(degree_line, DOWN, buff=0.36)
        handoff = Arrow(
            left_card.get_right() + RIGHT * 0.08,
            right_card.get_left() + LEFT * 0.08,
            buff=0.06,
            color=MINT,
            stroke_width=2.2,
            max_tip_length_to_length_ratio=0.20,
        )

        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(left_card), FadeIn(right_card), run_time=0.7)
        self.play(FadeIn(left_title), FadeIn(right_title), run_time=0.5)
        self.play(Create(lines), run_time=0.8)
        self.play(FadeIn(intersection, scale=1.6), FadeIn(linear_label), run_time=0.5)
        self.play(Create(small_circle), Create(secant), run_time=0.8)
        self.play(FadeIn(hits, scale=1.6), FadeIn(quadratic_label), run_time=0.5)
        self.play(GrowArrow(handoff), LaggedStart(*[FadeIn(chip, shift=RIGHT * 0.30) for chip in operations], lag_ratio=0.16), run_time=1.2)
        self.play(FadeOut(handoff), LaggedStart(FadeIn(ladder[0]), GrowArrow(arrows[0]), FadeIn(ladder[1]), GrowArrow(arrows[1]), FadeIn(ladder[2]), lag_ratio=0.20), run_time=1.5)
        self.play(FadeIn(degree_line, shift=RIGHT * 0.28), FadeIn(summary, shift=RIGHT * 0.28), run_time=1.0)
        self.wait(0.45)


class PolygonToNumber(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("把正多边形变成一个坐标", "只要锁定第一个顶点，其余顶点就能按相同圆心角复制")

        center = LEFT * 2.75 + DOWN * 0.35
        radius = 2.25
        axes = Axes(
            x_range=[-1.35, 1.35, 0.5],
            y_range=[-1.35, 1.35, 0.5],
            x_length=4.95,
            y_length=4.95,
            axis_config={"color": MUTED, "stroke_width": 1.6, "include_ticks": False, "include_tip": True},
        ).move_to(center)
        circle = Circle(radius=radius, color=BLUE, stroke_width=2.2).move_to(center)
        theta = TAU / 7
        point = center + radius * np.array([np.cos(theta), np.sin(theta), 0.0])
        p_dot = Dot(point, radius=0.08, color=AMBER)
        radius_line = Line(center, point, color=AMBER, stroke_width=3.0)
        projection = DashedLine(point, [point[0], center[1], 0], color=MINT, stroke_width=2.0)
        x_segment = Line(center, [point[0], center[1], 0], color=MINT, stroke_width=5.0)
        arc = Arc(radius=0.62, start_angle=0, angle=theta, arc_center=center, color=VIOLET, stroke_width=3.0)
        p_label = MathTex(r"P_n", color=AMBER).scale(0.58).next_to(p_dot, UR, buff=0.10)
        theta_label = MathTex(r"\frac{2\pi}{n}", color=VIOLET).scale(0.54).next_to(arc, RIGHT, buff=0.06)

        info = panel(5.2, 4.75).to_edge(RIGHT, buff=0.48).shift(DOWN * 0.22)
        info_title = cn("当前任务：构造第一个顶点", 0.37, INK).move_to(info.get_top() + DOWN * 0.45)
        formula = MathTex(
            r"P_n=\left(\cos\frac{2\pi}{n},\ \sin\frac{2\pi}{n}\right)",
            color=INK,
        ).scale(0.65).next_to(info_title, DOWN, buff=0.56)
        formula.set_color_by_tex(r"\cos", MINT)
        formula.set_color_by_tex(r"\sin", BLUE)
        focus = VGroup(
            cn("先问横坐标能否构造", 0.32, MUTED),
            MathTex(r"x_n=\cos\frac{2\pi}{n}", color=MINT).scale(0.82),
        ).arrange(DOWN, buff=0.28).next_to(formula, DOWN, buff=0.60)
        bottom = pill("几何问题  →  数字问题", VIOLET, 4.20).next_to(focus, DOWN, buff=0.56)
        handoff = Arrow(
            circle.get_right() + RIGHT * 0.08,
            info.get_left() + LEFT * 0.08,
            buff=0.06,
            color=MINT,
            stroke_width=2.2,
            max_tip_length_to_length_ratio=0.20,
        )

        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.6)
        self.play(Create(axes), Create(circle), FadeIn(info), FadeIn(info_title), run_time=0.9)
        self.play(Create(radius_line), Create(arc), FadeIn(theta_label), FadeIn(p_dot), FadeIn(p_label), run_time=1.0)
        self.play(Create(projection), Create(x_segment), run_time=0.8)
        self.play(GrowArrow(handoff), FadeIn(formula, shift=RIGHT * 0.32), run_time=0.9)
        self.play(FadeOut(handoff), FadeIn(focus, shift=RIGHT * 0.28), Indicate(x_segment, color=MINT), run_time=1.0)
        self.play(FadeIn(bottom, shift=RIGHT * 0.28), run_time=0.7)
        self.wait(0.45)


class SevenBarrier(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("正七边形卡在一个三次问题", "这里直接使用代数结论，观察它和尺规规则是否匹配")

        center = LEFT * 3.15 + DOWN * 0.28
        radius = 2.15
        circle = Circle(radius=radius, color=MUTED, stroke_width=1.8).move_to(center)
        poly = polygon_group(7, radius, center, CORAL, rotation=0, stroke_width=2.6, dot_radius=0.06)
        x_axis = NumberLine(
            x_range=[-2.5, 2.5, 1],
            length=4.9,
            include_numbers=False,
            include_tip=True,
            color=MUTED,
            stroke_width=1.6,
        ).move_to(center + DOWN * 2.45)

        conjugate_angles = [TAU / 7, 2 * TAU / 7, 3 * TAU / 7]
        projection_lines = VGroup()
        projection_dots = VGroup()
        colors = [AMBER, BLUE, VIOLET]
        for angle, color in zip(conjugate_angles, colors):
            point = center + radius * np.array([np.cos(angle), np.sin(angle), 0.0])
            axis_point = [point[0], x_axis.get_center()[1], 0]
            projection_lines.add(DashedLine(point, axis_point, color=color, stroke_width=1.8))
            projection_dots.add(Dot(axis_point, radius=0.07, color=color))

        info = panel(5.55, 4.9).to_edge(RIGHT, buff=0.42).shift(DOWN * 0.20)
        direct = pill("直接使用的结论", VIOLET, 2.65).move_to(info.get_top() + DOWN * 0.46)
        x_formula = MathTex(r"x=2\cos\frac{2\pi}{7}", color=MINT).scale(0.76).next_to(direct, DOWN, buff=0.38)
        cubic = MathTex(r"x^3+x^2-2x-1=0", color=CORAL).scale(0.78).next_to(x_formula, DOWN, buff=0.34)
        explanation = VGroup(
            cn("这个三次方程不能拆成", 0.31, MUTED),
            cn("有理的一次、二次问题", 0.34, CORAL),
        ).arrange(DOWN, buff=0.14).next_to(cubic, DOWN, buff=0.38)

        three_group = VGroup(*[Dot(radius=0.12, color=color) for color in colors]).arrange(RIGHT, buff=0.46)
        three_group.next_to(explanation, DOWN, buff=0.36)
        split_arrow = Arrow(LEFT * 0.55, RIGHT * 0.55, color=MUTED, stroke_width=2.0).next_to(three_group, RIGHT, buff=0.25)
        blocked = VGroup(
            MathTex(r"2\times ?", color=CORAL).scale(0.66),
            Cross(MathTex(r"2\times ?", color=CORAL).scale(0.66), stroke_color=CORAL, stroke_width=3.0),
        )
        blocked[1].move_to(blocked[0])
        blocked.next_to(split_arrow, RIGHT, buff=0.24)
        handoff = Arrow(
            circle.get_right() + RIGHT * 0.08,
            info.get_left() + LEFT * 0.08,
            buff=0.06,
            color=MINT,
            stroke_width=2.2,
            max_tip_length_to_length_ratio=0.20,
        )

        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.6)
        self.play(Create(circle), Create(x_axis), FadeIn(info), run_time=0.8)
        self.play(Create(poly[0]), FadeIn(poly[1]), run_time=1.0)
        self.play(LaggedStart(*[Create(line) for line in projection_lines], lag_ratio=0.22), FadeIn(projection_dots), run_time=1.1)
        self.play(GrowArrow(handoff), FadeIn(direct, shift=RIGHT * 0.24), FadeIn(x_formula, shift=RIGHT * 0.32), run_time=0.8)
        self.play(FadeOut(handoff), FadeIn(cubic, shift=RIGHT * 0.28), run_time=0.8)
        self.play(FadeIn(explanation, shift=RIGHT * 0.24), run_time=0.8)
        self.play(FadeIn(three_group), GrowArrow(split_arrow), FadeIn(blocked), run_time=0.8)
        self.play(Indicate(cubic, color=CORAL, scale_factor=1.04), run_time=0.7)
        self.wait(0.45)


class SeventeenHalves(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("正十七边形能被连续二分锁定", "相关代数结构有 16 个方向，每一层只需处理二次问题")

        center = LEFT * 3.15 + DOWN * 0.28
        radius = 2.20
        circle = Circle(radius=radius, color=MUTED, stroke_width=1.8).move_to(center)
        points = polygon_points(17, radius, center, rotation=PI / 2)
        dots = VGroup(*[Dot(point, radius=0.055, color=AMBER) for point in points])
        spokes = VGroup(*[Line(center, point, color=BLUE, stroke_width=1.0, stroke_opacity=0.22) for point in points])
        edges = VGroup(*[Line(points[k], points[(k + 1) % 17], color=AMBER, stroke_width=2.7) for k in range(17)])

        info = panel(5.4, 4.95).to_edge(RIGHT, buff=0.44).shift(DOWN * 0.20)
        equation = MathTex(r"16=2^4", color=MINT).scale(0.96).move_to(info.get_top() + DOWN * 0.58)
        numbers = [16, 8, 4, 2, 1]
        colors = [BLUE, VIOLET, AMBER, MINT, INK]
        level_boxes = VGroup()
        for number, color in zip(numbers, colors):
            box = RoundedRectangle(
                width=2.72,
                height=0.55,
                corner_radius=0.14,
                stroke_color=color,
                fill_color=color,
                fill_opacity=0.10,
            )
            label = cn(
                f"{number} 个方向" if number > 1 else "1 个目标坐标",
                0.28,
                color,
            ).move_to(box)
            level_boxes.add(VGroup(box, label))
        level_boxes.arrange(DOWN, buff=0.17).next_to(equation, DOWN, buff=0.34)
        arrows = VGroup(
            *[
                Arrow(
                    level_boxes[k].get_bottom(),
                    level_boxes[k + 1].get_top(),
                    buff=0.05,
                    color=MUTED,
                    stroke_width=1.8,
                    max_tip_length_to_length_ratio=0.22,
                )
                for k in range(len(level_boxes) - 1)
            ]
        )
        note = pill("每一层：一次二次求解", MINT, 4.25).next_to(level_boxes, DOWN, buff=0.28)
        handoff = Arrow(
            circle.get_right() + RIGHT * 0.08,
            info.get_left() + LEFT * 0.08,
            buff=0.06,
            color=MINT,
            stroke_width=2.2,
            max_tip_length_to_length_ratio=0.20,
        )

        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.6)
        self.play(Create(circle), FadeIn(info), run_time=0.8)
        self.play(LaggedStart(*[Create(spoke) for spoke in spokes], lag_ratio=0.03), FadeIn(dots), run_time=1.2)
        for index, level in enumerate(level_boxes):
            animations = [FadeIn(level, shift=UP * 0.08)]
            if index == 0:
                animations.insert(0, GrowArrow(handoff))
                animations.insert(1, FadeIn(equation, shift=RIGHT * 0.30))
            if index > 0:
                animations.insert(0, GrowArrow(arrows[index - 1]))
            if index == 1:
                animations.insert(0, FadeOut(handoff))
            self.play(*animations, run_time=0.55)
            if index < 4:
                active_indices = [k for k in range(17) if k % (2 ** (index + 1)) == 0]
                self.play(
                    *[dots[k].animate.set_color(colors[min(index + 1, len(colors) - 1)]).scale(1.22) for k in active_indices],
                    run_time=0.35,
                )
        self.play(FadeIn(note, shift=UP * 0.10), run_time=0.6)
        self.play(LaggedStart(*[Create(edge) for edge in edges], lag_ratio=0.035), run_time=1.8)
        self.play(Indicate(VGroup(edges, dots), color=AMBER, scale_factor=1.02), run_time=0.7)
        self.wait(0.45)


class RuleAndPayoff(StyledScene):
    def construct(self) -> None:
        self.begin_scene()
        title = title_group("边数，不是尺规难度表", "能否连续拆成二次步骤，才是决定因素")

        specs = [(3, True), (5, True), (7, False), (9, False), (15, True), (17, True)]
        positions = [
            LEFT * 5.0 + UP * 1.0,
            LEFT * 3.1 + UP * 1.0,
            LEFT * 1.2 + UP * 1.0,
            LEFT * 5.0 + DOWN * 1.35,
            LEFT * 3.1 + DOWN * 1.35,
            LEFT * 1.2 + DOWN * 1.35,
        ]
        minis = VGroup(*[mini_polygon(n, status, pos) for (n, status), pos in zip(specs, positions)])

        theorem = panel(5.65, 4.95).to_edge(RIGHT, buff=0.40).shift(DOWN * 0.20)
        theorem_title = cn("高斯—旺策尔判据", 0.38, INK).move_to(theorem.get_top() + DOWN * 0.44)
        theorem_formula = MathTex(r"n=2^k p_1p_2\cdots p_m", color=MINT).scale(0.78).next_to(theorem_title, DOWN, buff=0.48)
        description = VGroup(
            cn("每个 p 都是互不相同的", 0.30, MUTED),
            cn("费马素数", 0.37, AMBER),
        ).arrange(DOWN, buff=0.12).next_to(theorem_formula, DOWN, buff=0.38)
        primes = MathTex(r"3,\ 5,\ 17,\ 257,\ 65537,\ldots", color=AMBER).scale(0.64).next_to(description, DOWN, buff=0.34)
        comparison = VGroup(
            pill("7  不符合", CORAL, 2.20),
            pill("17  符合", MINT, 2.20),
        ).arrange(RIGHT, buff=0.30).next_to(primes, DOWN, buff=0.45)
        handoff = Arrow(
            minis.get_right() + RIGHT * 0.08,
            theorem.get_left() + LEFT * 0.08,
            buff=0.06,
            color=MINT,
            stroke_width=2.2,
            max_tip_length_to_length_ratio=0.20,
        )

        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(item, shift=UP * 0.10) for item in minis], lag_ratio=0.16), run_time=2.0)
        self.play(FadeIn(theorem), FadeIn(theorem_title), run_time=0.6)
        self.play(GrowArrow(handoff), FadeIn(theorem_formula, shift=RIGHT * 0.30), run_time=0.7)
        self.play(FadeOut(handoff), FadeIn(description, shift=RIGHT * 0.24), FadeIn(primes, shift=RIGHT * 0.24), run_time=0.8)
        self.play(FadeIn(comparison, shift=UP * 0.10), run_time=0.7)
        self.play(Indicate(minis[-1], color=MINT, scale_factor=1.07), run_time=0.7)

        payoff_center = ORIGIN + DOWN * 0.10
        payoff_circle = Circle(radius=2.55, color=BLUE, stroke_width=2.0).move_to(payoff_center)
        payoff_poly = polygon_group(17, 2.46, payoff_center, AMBER, stroke_width=3.1, dot_radius=0.055)
        payoff_title = cn("17 条边，全部精确落位", 0.56, INK).to_edge(UP, buff=0.40)
        payoff_sub = MathTex(r"17=2^{2^2}+1", color=MINT).scale(0.82)
        payoff_sub.move_to(payoff_center + DOWN * 1.72)

        title_swap = Succession(
            FadeOut(title, shift=LEFT * 0.18),
            FadeIn(payoff_title, shift=RIGHT * 0.18),
        )
        formula_swap = Succession(
            FadeOut(theorem_formula, shift=LEFT * 0.18),
            FadeIn(payoff_sub, shift=RIGHT * 0.18),
        )
        self.play(
            FadeOut(minis),
            FadeOut(theorem),
            FadeOut(theorem_title),
            FadeOut(description),
            FadeOut(primes),
            FadeOut(comparison),
            title_swap,
            formula_swap,
            Create(payoff_circle),
            run_time=0.8,
        )
        self.play(FadeIn(payoff_poly[1]), run_time=0.8)
        self.play(Create(payoff_poly[0]), run_time=1.6)
        self.play(payoff_poly.animate.scale(1.03), run_time=0.6, rate_func=there_and_back)
        self.wait(0.65)
