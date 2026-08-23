from __future__ import annotations

from pathlib import Path

import numpy as np
from manim import *


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SMILEY_FONT_FILE = PROJECT_ROOT / "assets" / "fonts" / "SmileySans-Oblique.ttf"
FONT = "Smiley Sans"
LATIN_FONT = "Times New Roman"

BG = "#07111F"
INK = "#F8F4E3"
MUTED = "#AAB4C2"
BLUE = "#7DD3FC"
AMBER = "#F6B73C"
MINT = "#5EEAD4"
ROSE = "#FF5C7A"
VIOLET = "#A78BFA"
GREEN = "#8FE388"
PANEL = "#0D1727"
GRID_COLOR = "#8FA8D8"

TIMES_TEX_TEMPLATE = TexTemplate()
TIMES_TEX_TEMPLATE.add_to_preamble(r"\usepackage{mathptmx}")
MathTex.set_default(tex_template=TIMES_TEX_TEMPLATE)

BEAT_ENDS = [19.30, 38.87, 62.20, 83.67, 103.61, 122.71, 145.25, 161.23, 180.60]


def cn(text: str, size: float = 0.36, color: str = INK, line_spacing: float = -1.0) -> Text:
    with register_font(SMILEY_FONT_FILE):
        return Text(
            text,
            font=FONT,
            slant=OBLIQUE,
            color=color,
            line_spacing=line_spacing,
        ).scale(size)


def latin(text: str, size: float = 0.36, color: str = INK) -> Text:
    return Text(text, font=LATIN_FONT, color=color).scale(size)


def set_scene_background(scene: Scene) -> None:
    scene.camera.background_color = BG
    scene.add(notebook_grid())


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


def wait_until(scene: Scene, target: float) -> None:
    remaining = target - scene.time
    if remaining > 0:
        scene.wait(remaining)


def fit_to_width(mob: Mobject, width: float) -> Mobject:
    if mob.width > width:
        mob.scale_to_fit_width(width)
    return mob


def scene_title(title: str, subtitle: str | None = None) -> VGroup:
    head = cn(title, 0.52).to_edge(UP, buff=0.32)
    if subtitle is None:
        return VGroup(head)
    sub = cn(subtitle, 0.30, MUTED).next_to(head, DOWN, buff=0.10)
    return VGroup(head, sub)


def panel_box(width: float, height: float, stroke: str = "#2A3A50") -> RoundedRectangle:
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.16,
        stroke_color=stroke,
        stroke_width=1.5,
        fill_color=PANEL,
        fill_opacity=0.92,
    )


def page_line(start: np.ndarray, end: np.ndarray, sag: float = 0.0, color: str = INK, width: float = 3.0) -> VMobject:
    start = np.array(start)
    end = np.array(end)
    mid = (start + end) / 2 + DOWN * sag
    left_mid = (start + mid) / 2 + UP * sag * 0.20
    right_mid = (mid + end) / 2 + UP * sag * 0.20
    curve = VMobject()
    curve.set_points_smoothly([start, left_mid, mid, right_mid, end])
    curve.set_stroke(color=color, width=width)
    curve.set_fill(opacity=0)
    return curve


def interleaved_books(scale: float = 1.0, pages: int = 9) -> VGroup:
    left_cover = RoundedRectangle(
        width=2.45,
        height=1.92,
        corner_radius=0.06,
        fill_color="#24364F",
        fill_opacity=1,
        stroke_color=BLUE,
        stroke_width=2.0,
    ).shift(LEFT * 1.18)
    right_cover = left_cover.copy().set_fill("#3C2E4D", 1).set_stroke(VIOLET, 2.0).shift(RIGHT * 2.36)
    left_label = cn("书 A", 0.25, BLUE).move_to(left_cover.get_center() + UP * 0.67)
    right_label = cn("书 B", 0.25, VIOLET).move_to(right_cover.get_center() + UP * 0.67)

    page_group = VGroup()
    for index in range(pages):
        y = -0.62 + index * (1.24 / max(1, pages - 1))
        color = BLUE if index % 2 == 0 else VIOLET
        x0 = -1.85 if index % 2 == 0 else -1.45
        x1 = 1.85 if index % 2 == 0 else 1.45
        page = Line([x0, y, 0], [x1, y + 0.04 * np.sin(index), 0], color=color, stroke_width=3.0)
        page_group.add(page)

    covers = VGroup(left_cover, right_cover, left_label, right_label)
    group = VGroup(covers, page_group).scale(scale)
    return group


def pull_arrows(target: Mobject, scale: float = 1.0) -> VGroup:
    y = target.get_center()[1]
    left = Arrow(
        target.get_left() + LEFT * 0.15 * scale + UP * (y - target.get_center()[1]),
        target.get_left() + LEFT * 1.05 * scale + UP * (y - target.get_center()[1]),
        buff=0,
        color=ROSE,
        stroke_width=6,
    )
    right = Arrow(
        target.get_right() + RIGHT * 0.15 * scale + UP * (y - target.get_center()[1]),
        target.get_right() + RIGHT * 1.05 * scale + UP * (y - target.get_center()[1]),
        buff=0,
        color=ROSE,
        stroke_width=6,
    )
    left_label = MathTex("T", color=ROSE).scale(0.58).next_to(left, LEFT, buff=0.08)
    right_label = MathTex("T", color=ROSE).scale(0.58).next_to(right, RIGHT, buff=0.08)
    return VGroup(left, right, left_label, right_label)


def bent_page_diagram() -> VGroup:
    neighbors = VGroup(
        Line(LEFT * 4.0 + UP * 0.74, RIGHT * 4.0 + UP * 0.74, color="#405168", stroke_width=4),
        Line(LEFT * 4.0 + DOWN * 0.80, RIGHT * 4.0 + DOWN * 0.80, color="#405168", stroke_width=4),
    )
    page = page_line(LEFT * 3.85 + DOWN * 0.22, RIGHT * 3.85 + UP * 0.38, sag=0.38, color=AMBER, width=8)
    tangent = Arrow(LEFT * 2.65 + DOWN * 0.42, LEFT * 0.72 + DOWN * 0.13, buff=0, color=ROSE, stroke_width=6)
    turned = Arrow(LEFT * 0.70 + DOWN * 0.12, RIGHT * 1.28 + UP * 0.17, buff=0, color=ROSE, stroke_width=6)
    normal = Arrow(RIGHT * 0.65 + DOWN * 0.78, RIGHT * 0.65 + DOWN * 0.22, buff=0, color=BLUE, stroke_width=6)
    support = Arrow(RIGHT * 0.90 + UP * 0.72, RIGHT * 0.90 + UP * 0.22, buff=0, color=BLUE, stroke_width=6)
    labels = VGroup(
        MathTex("T", color=ROSE).scale(0.60).next_to(tangent, DOWN, buff=0.08),
        cn("方向稍微转弯", 0.28, AMBER).next_to(turned, UP, buff=0.12),
        MathTex("N", color=BLUE).scale(0.62).next_to(normal, RIGHT, buff=0.08),
        cn("相邻纸页顶住", 0.27, BLUE).next_to(support, RIGHT, buff=0.10),
    )
    return VGroup(neighbors, page, tangent, turned, normal, support, labels)


def friction_formula_panel() -> VGroup:
    box = panel_box(5.4, 3.25)
    title = cn("摩擦上限看正压力", 0.36, INK).move_to(box.get_top() + DOWN * 0.42)
    formula = MathTex(r"f\le \mu N", color=INK).scale(1.28).next_to(title, DOWN, buff=0.32)
    under = VGroup(
        cn("N 变大", 0.30, BLUE),
        cn("摩擦上限变大", 0.30, AMBER),
    ).arrange(RIGHT, buff=0.38).next_to(formula, DOWN, buff=0.38)
    arrow = Arrow(under[0].get_right() + RIGHT * 0.05, under[1].get_left() + LEFT * 0.05, buff=0, color=MINT, stroke_width=4)
    warning = cn("主线不是“面积越大”", 0.28, MUTED).next_to(under, DOWN, buff=0.26)
    return VGroup(box, title, formula, under, arrow, warning)


def force_split_visual() -> VGroup:
    base = Line(LEFT * 2.3 + DOWN * 0.4, RIGHT * 2.3 + UP * 0.28, color=AMBER, stroke_width=7)
    pull = Arrow(LEFT * 1.95 + DOWN * 0.35, RIGHT * 0.65 + UP * 0.04, buff=0, color=ROSE, stroke_width=6)
    normal = Arrow(RIGHT * 0.30 + DOWN * 0.70, RIGHT * 0.52 + DOWN * 0.06, buff=0, color=BLUE, stroke_width=6)
    friction = Arrow(RIGHT * 1.72 + UP * 0.18, RIGHT * 0.78 + UP * 0.05, buff=0, color=AMBER, stroke_width=6)
    labels = VGroup(
        MathTex("T", color=ROSE).scale(0.55).next_to(pull, UP, buff=0.10),
        MathTex("N", color=BLUE).scale(0.55).next_to(normal, RIGHT, buff=0.08),
        MathTex("f", color=AMBER).scale(0.55).next_to(friction, UP, buff=0.08),
    )
    return VGroup(base, pull, normal, friction, labels)


def layer_stack(count: int = 9) -> VGroup:
    group = VGroup()
    for index in range(count):
        y = -1.7 + index * 0.38
        color = BLUE if index % 2 == 0 else VIOLET
        group.add(page_line(LEFT * 3.7 + UP * y, RIGHT * 3.7 + UP * (y + 0.04), sag=0.11, color=color, width=3.4))
    return group


def resistance_bar(value: float, label: str) -> VGroup:
    frame = RoundedRectangle(
        width=4.35,
        height=0.34,
        corner_radius=0.08,
        stroke_color="#314054",
        fill_color="#152238",
        fill_opacity=1,
    )
    fill = RoundedRectangle(
        width=max(0.18, 4.35 * value),
        height=0.34,
        corner_radius=0.08,
        stroke_width=0,
        fill_color=AMBER,
        fill_opacity=0.95,
    )
    fill.align_to(frame, LEFT).move_to(frame.get_left() + RIGHT * fill.width / 2)
    text = cn(label, 0.30, INK).next_to(frame, UP, buff=0.14)
    return VGroup(frame, fill, text)


def trend_plot() -> VGroup:
    origin = LEFT * 2.55 + DOWN * 1.55
    x_axis = Arrow(origin, origin + RIGHT * 5.2, buff=0, color="#6D7C91", stroke_width=3)
    y_axis = Arrow(origin, origin + UP * 3.15, buff=0, color="#6D7C91", stroke_width=3)
    x_label = cn("交错页数", 0.26, MUTED).next_to(x_axis, DOWN, buff=0.12)
    y_label = cn("需要的拉力", 0.26, MUTED).next_to(y_axis, LEFT, buff=0.12).rotate(PI / 2)

    points = []
    for t in np.linspace(0, 1, 80):
        x = 5.0 * t
        y = 0.20 + 2.68 * (np.exp(2.35 * t) - 1) / (np.exp(2.35) - 1)
        points.append(origin + RIGHT * x + UP * y)
    curve = VMobject()
    curve.set_points_smoothly(points)
    curve.set_stroke(AMBER, width=7)

    ticks = VGroup()
    for text, t in [("3", 0.10), ("5", 0.20), ("20", 0.55), ("50", 0.92)]:
        point = points[int(t * (len(points) - 1))]
        ticks.add(Dot(point, color=ROSE, radius=0.07))
        ticks.add(latin(text, 0.26, ROSE).next_to(point, UP, buff=0.08))
    note = cn("真实书页很复杂：这里看趋势", 0.29, MUTED).to_edge(DOWN, buff=0.46)
    return VGroup(x_axis, y_axis, x_label, y_label, curve, ticks, note)


def capstan_visual() -> VGroup:
    post = Circle(radius=1.05, color="#52657E", stroke_width=6, fill_color="#1B2A3D", fill_opacity=1)
    top = Circle(radius=0.78, color="#70839C", stroke_width=2, fill_color="#26384F", fill_opacity=0.7).shift(UP * 0.06)
    rope = VGroup(
        Arc(radius=1.35, start_angle=-0.35 * PI, angle=1.88 * PI, color=AMBER, stroke_width=12),
        Line(LEFT * 4.6 + DOWN * 0.62, post.get_center() + LEFT * 1.10 + DOWN * 0.62, color=AMBER, stroke_width=12),
        Line(post.get_center() + RIGHT * 0.36 + UP * 1.30, RIGHT * 4.75 + UP * 1.30, color=AMBER, stroke_width=12),
    )
    light_arrow = Arrow(LEFT * 4.55 + DOWN * 1.05, LEFT * 3.15 + DOWN * 1.05, buff=0, color=ROSE, stroke_width=5)
    heavy_arrow = Arrow(RIGHT * 3.15 + UP * 1.72, RIGHT * 4.55 + UP * 1.72, buff=0, color=ROSE, stroke_width=7)
    labels = VGroup(
        cn("轻拉端", 0.28, ROSE).next_to(light_arrow, DOWN, buff=0.12),
        cn("重载端", 0.28, ROSE).next_to(heavy_arrow, UP, buff=0.12),
        MathTex(r"T_{\rm light}", color=ROSE).scale(0.52).next_to(light_arrow, UP, buff=0.10),
        MathTex(r"T_{\rm heavy}", color=ROSE).scale(0.52).next_to(heavy_arrow, DOWN, buff=0.10),
    )
    segment = Arc(radius=1.60, start_angle=0.25 * PI, angle=0.26 * PI, color=MINT, stroke_width=5)
    dtheta = MathTex(r"d\theta", color=MINT).scale(0.55).next_to(segment, UP, buff=0.05)
    normal = Arrow(UP * 1.78 + LEFT * 0.25, UP * 1.05 + LEFT * 0.08, buff=0, color=BLUE, stroke_width=5)
    n_label = MathTex("dN", color=BLUE).scale(0.52).next_to(normal, LEFT, buff=0.08)
    return VGroup(post, top, rope, light_arrow, heavy_arrow, labels, segment, dtheta, normal, n_label)


def capstan_formula_panel() -> VGroup:
    box = panel_box(6.3, 3.4)
    title = cn("很多小差别，连续累积", 0.36, INK).move_to(box.get_top() + DOWN * 0.42)
    formula = MathTex(r"\frac{T_{\rm heavy}}{T_{\rm light}}=e^{\mu\theta}", color=INK).scale(1.05)
    formula.next_to(title, DOWN, buff=0.30)
    defs = VGroup(
        cn("μ：摩擦系数", 0.28, BLUE),
        cn("θ：绕过的总角度", 0.28, MINT),
        cn("一圈 = 2π", 0.28, AMBER),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).next_to(formula, DOWN, buff=0.34)
    return VGroup(box, title, formula, defs)


def mechanism_chain() -> VGroup:
    items = [("转向", ROSE), ("压紧", BLUE), ("摩擦", AMBER)]
    nodes = VGroup()
    arrows = VGroup()
    for index, (text, color) in enumerate(items):
        node = RoundedRectangle(
            width=1.75,
            height=0.72,
            corner_radius=0.12,
            stroke_color=color,
            fill_color="#122033",
            fill_opacity=0.96,
            stroke_width=2.2,
        )
        label = cn(text, 0.34, color).move_to(node)
        node_group = VGroup(node, label)
        nodes.add(node_group)
        if index:
            arrow = Arrow(LEFT * 0.55, RIGHT * 0.55, buff=0, color=MUTED, stroke_width=4)
            arrows.add(arrow)
    chain = VGroup(nodes[0], arrows[0], nodes[1], arrows[1], nodes[2]).arrange(RIGHT, buff=0.25)
    return chain


def app_icon(kind: str, label: str, color: str) -> VGroup:
    box = panel_box(2.55, 2.22, stroke=color)
    if kind == "belt":
        visual = VGroup(
            Circle(radius=0.34, color=color, stroke_width=5).shift(LEFT * 0.45),
            Circle(radius=0.34, color=color, stroke_width=5).shift(RIGHT * 0.45),
            Line(LEFT * 0.45 + UP * 0.34, RIGHT * 0.45 + UP * 0.34, color=color, stroke_width=5),
            Line(LEFT * 0.45 + DOWN * 0.34, RIGHT * 0.45 + DOWN * 0.34, color=color, stroke_width=5),
        )
    elif kind == "climb":
        visual = VGroup(
            Line(UP * 0.66, DOWN * 0.68, color=color, stroke_width=5),
            Circle(radius=0.33, color=color, stroke_width=4).shift(UP * 0.22),
            Arc(radius=0.54, start_angle=-0.20 * PI, angle=1.32 * PI, color=AMBER, stroke_width=5).shift(DOWN * 0.10),
            Line(RIGHT * 0.24 + UP * 0.54, RIGHT * 0.72 + UP * 0.92, color=AMBER, stroke_width=5),
        )
    else:
        visual = VGroup(
            Arc(radius=0.46, start_angle=0.1 * PI, angle=1.45 * PI, color=color, stroke_width=6).shift(LEFT * 0.25),
            Arc(radius=0.46, start_angle=-0.55 * PI, angle=1.45 * PI, color=color, stroke_width=6).shift(RIGHT * 0.25),
            Line(LEFT * 0.88 + DOWN * 0.42, LEFT * 0.22 + DOWN * 0.05, color=AMBER, stroke_width=5),
            Line(RIGHT * 0.88 + DOWN * 0.42, RIGHT * 0.22 + DOWN * 0.05, color=AMBER, stroke_width=5),
        )
    visual.move_to(box.get_center() + UP * 0.24)
    text = cn(label, 0.29, INK).move_to(box.get_bottom() + UP * 0.35)
    return VGroup(box, visual, text)


class CoverFrame(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        books = interleaved_books(scale=1.35, pages=11).move_to(ORIGIN + DOWN * 0.48)
        arrows = pull_arrows(books, scale=1.0)
        title = VGroup(
            cn("为什么越拉", 0.76, INK),
            cn("反而越拉不开？", 0.76, AMBER),
        ).arrange(DOWN, buff=0.10).to_edge(UP, buff=0.55)
        tag = cn("摩擦放大：转向 -> 压紧 -> 摩擦", 0.34, MUTED).to_edge(DOWN, buff=0.50)
        self.add(books, arrows, title, tag)
        self.wait(0.2)


class FrictionAmplification(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        self.opening_books()
        self.single_page()
        self.normal_force_formula()
        self.many_layers()
        self.page_count_trend()
        self.capstan_setup()
        self.capstan_equation()
        self.same_mechanism()
        self.applications()

    def replace_scene(self, current: Mobject | None, title: Mobject, body: Mobject) -> VGroup:
        group = VGroup(title, body)
        if current is None:
            self.play(FadeIn(title, shift=DOWN * 0.15), FadeIn(body, shift=UP * 0.15), run_time=1.0)
        else:
            self.play(FadeOut(current, shift=LEFT * 0.28), run_time=0.45)
            self.play(FadeIn(title, shift=DOWN * 0.15), FadeIn(body, shift=UP * 0.15), run_time=0.95)
        return group

    def opening_books(self) -> None:
        title = scene_title("两本书，像被锁住一样", "没有胶水，也没有夹子")
        books = interleaved_books(scale=1.35, pages=11).move_to(DOWN * 0.25)
        arrows = pull_arrows(books, scale=1.05)
        question = cn("纸和纸的摩擦，为什么突然这么夸张？", 0.36, AMBER).to_edge(DOWN, buff=0.46)
        badges = VGroup(
            cn("无胶水", 0.26, MINT),
            cn("无夹子", 0.26, MINT),
            cn("只靠纸页接触", 0.26, MINT),
        ).arrange(RIGHT, buff=0.30).next_to(title, DOWN, buff=0.30)
        body = VGroup(books, arrows, question, badges)
        self.current = self.replace_scene(None, title, body)
        self.play(arrows.animate.scale(1.13), rate_func=there_and_back, run_time=1.2)
        self.play(question.animate.set_color(ROSE), run_time=0.7)
        wait_until(self, BEAT_ENDS[0])

    def single_page(self) -> None:
        title = scene_title("先看一张纸怎么受力", "局部弯折让拉力方向发生变化")
        diagram = bent_page_diagram().move_to(DOWN * 0.20)
        cue = cn("力的方向一转，就需要旁边的纸页顶住", 0.34, AMBER).to_edge(DOWN, buff=0.46)
        body = VGroup(diagram, cue)
        self.current = self.replace_scene(self.current, title, body)
        self.play(diagram[2].animate.set_color("#FF8AA0"), diagram[3].animate.set_color("#FF8AA0"), run_time=0.8)
        self.play(Indicate(diagram[4], color=BLUE, scale_factor=1.12), Indicate(diagram[5], color=BLUE, scale_factor=1.12), run_time=1.1)
        wait_until(self, BEAT_ENDS[1])

    def normal_force_formula(self) -> None:
        title = scene_title("拉力变成压紧力", "摩擦上限跟着正压力一起变大")
        split = force_split_visual().shift(LEFT * 3.15 + DOWN * 0.10)
        formula = friction_formula_panel().shift(RIGHT * 2.25 + DOWN * 0.10)
        bridge = Arrow(LEFT * 0.72 + DOWN * 0.05, RIGHT * 0.10 + DOWN * 0.05, buff=0, color=MINT, stroke_width=5)
        body = VGroup(split, bridge, formula)
        self.current = self.replace_scene(self.current, title, body)
        self.play(Indicate(formula[2], color=AMBER, scale_factor=1.08), run_time=1.1)
        self.play(Indicate(split[2], color=BLUE, scale_factor=1.18), run_time=0.9)
        wait_until(self, BEAT_ENDS[2])

    def many_layers(self) -> None:
        title = scene_title("一层不夸张，很多层就夸张", "每层都贡献一点压紧和摩擦")
        stack = layer_stack(11).move_to(LEFT * 2.60 + DOWN * 0.02)
        arrows = VGroup()
        for index, page in enumerate(stack[1::2]):
            x = -1.1 + 0.28 * index
            arrows.add(Arrow([x, page.get_center()[1] + 0.20, 0], [x, page.get_center()[1] - 0.16, 0], buff=0, color=BLUE, stroke_width=3))
            arrows.add(Arrow([x + 0.50, page.get_center()[1], 0], [x + 0.12, page.get_center()[1], 0], buff=0, color=AMBER, stroke_width=3))
        counter = cn("3 层  ->  5 层  ->  20 层  ->  50 层", 0.39, INK).move_to(RIGHT * 2.15 + UP * 1.10)
        bar1 = resistance_bar(0.22, "阻力：刚有点卡").move_to(RIGHT * 2.15 + UP * 0.05)
        bar2 = resistance_bar(0.92, "阻力：像上了锁").move_to(RIGHT * 2.15 + DOWN * 1.05)
        body = VGroup(stack, arrows, counter, bar1, bar2)
        self.current = self.replace_scene(self.current, title, body)
        self.play(LaggedStart(*[FadeIn(mob, scale=1.05) for mob in arrows], lag_ratio=0.05), run_time=1.4)
        self.play(Indicate(bar2[1], color=AMBER, scale_factor=1.04), run_time=1.2)
        wait_until(self, BEAT_ENDS[3])

    def page_count_trend(self) -> None:
        title = scene_title("页数真正要命的地方", "越拉，局部越压紧；越压紧，摩擦上限越大")
        plot = trend_plot().move_to(DOWN * 0.05)
        feedback = VGroup(
            cn("拉力", 0.31, ROSE),
            Arrow(LEFT * 0.30, RIGHT * 0.30, buff=0, color=MUTED, stroke_width=4),
            cn("压紧", 0.31, BLUE),
            Arrow(LEFT * 0.30, RIGHT * 0.30, buff=0, color=MUTED, stroke_width=4),
            cn("摩擦上限", 0.31, AMBER),
        ).arrange(RIGHT, buff=0.16).move_to(UP * 2.15)
        body = VGroup(plot, feedback)
        self.current = self.replace_scene(self.current, title, body)
        self.play(Create(plot[4]), run_time=1.5)
        self.play(LaggedStart(*[FadeIn(item, shift=UP * 0.08) for item in feedback], lag_ratio=0.08), run_time=1.0)
        wait_until(self, BEAT_ENDS[4])

    def capstan_setup(self) -> None:
        title = scene_title("换成更干净的模型", "绳子绕柱：连续的小转向")
        visual = capstan_visual().move_to(DOWN * 0.08)
        callout = cn("每一小段角度都制造一点正压力", 0.35, AMBER).to_edge(DOWN, buff=0.46)
        body = VGroup(visual, callout)
        self.current = self.replace_scene(self.current, title, body)
        self.play(Indicate(visual[-2], color=BLUE, scale_factor=1.12), run_time=1.0)
        self.play(Indicate(visual[-4], color=MINT, scale_factor=1.12), run_time=1.0)
        wait_until(self, BEAT_ENDS[5])

    def capstan_equation(self) -> None:
        title = scene_title("绞盘方程：一点点差别累积", "多绕一圈，放大过程又走一遍")
        capstan = capstan_visual().scale(0.74).shift(LEFT * 3.70 + DOWN * 0.18)
        panel = capstan_formula_panel().shift(RIGHT * 2.05 + DOWN * 0.08)
        chain = VGroup(
            cn("每小段", 0.28, MINT),
            cn("× 一点点", 0.28, AMBER),
            cn("× 很多段", 0.28, ROSE),
            cn("= 指数放大", 0.30, INK),
        ).arrange(RIGHT, buff=0.22).to_edge(DOWN, buff=0.46)
        body = VGroup(capstan, panel, chain)
        self.current = self.replace_scene(self.current, title, body)
        self.play(Indicate(panel[2], color=AMBER, scale_factor=1.05), run_time=1.2)
        self.play(LaggedStart(*[Indicate(item, scale_factor=1.06) for item in chain], lag_ratio=0.14), run_time=1.8)
        wait_until(self, BEAT_ENDS[6])

    def same_mechanism(self) -> None:
        title = scene_title("书页和绕绳在做同一件事", "离散小转向，连续小转向")
        books = layer_stack(8).scale(0.72).move_to(LEFT * 3.30 + DOWN * 0.20)
        book_label = cn("书页夹层", 0.32, BLUE).next_to(books, UP, buff=0.25)
        capstan = capstan_visual().scale(0.55).move_to(RIGHT * 3.35 + DOWN * 0.12)
        capstan_label = cn("绕柱绳子", 0.32, AMBER).next_to(capstan, UP, buff=0.25)
        chain = mechanism_chain().move_to(DOWN * 2.50)
        body = VGroup(books, book_label, capstan, capstan_label, chain)
        self.current = self.replace_scene(self.current, title, body)
        self.play(Indicate(chain, color=MINT, scale_factor=1.02), run_time=1.25)
        wait_until(self, BEAT_ENDS[7])

    def applications(self) -> None:
        title = scene_title("一夹、一绕、一打结，都能放大摩擦", "结构让力不断转向、不断压紧")
        icons = VGroup(
            app_icon("belt", "皮带传动", BLUE),
            app_icon("climb", "登山保护器", MINT),
            app_icon("knot", "绳结 / 鞋带", AMBER),
        ).arrange(RIGHT, buff=0.36).move_to(UP * 0.10)
        final_books = interleaved_books(scale=0.74, pages=9).to_edge(DOWN, buff=0.42).shift(LEFT * 1.70)
        final_chain = mechanism_chain().scale(0.58).next_to(final_books, RIGHT, buff=0.38)
        payoff = VGroup(final_books, final_chain)
        body = VGroup(icons, payoff)
        self.current = self.replace_scene(self.current, title, body)
        self.play(LaggedStart(*[FadeIn(icon, shift=UP * 0.16) for icon in icons], lag_ratio=0.16), run_time=1.1)
        self.play(Indicate(final_chain, color=AMBER, scale_factor=1.03), run_time=1.1)
        wait_until(self, BEAT_ENDS[8])
