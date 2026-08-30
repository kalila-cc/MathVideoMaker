from __future__ import annotations

from pathlib import Path

import numpy as np
from manim import *


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SMILEY_FONT_FILE = PROJECT_ROOT / "assets" / "fonts" / "SmileySans-Oblique.ttf"
FONT = "Smiley Sans"

BG = "#07111F"
INK = "#F8F4E3"
MUTED = "#AAB4C2"
BLUE = "#7DD3FC"
GOLD = "#F6B73C"
MINT = "#5EEAD4"
PINK = "#FF5C9A"
GRAY = "#7C8798"
VIOLET = "#A78BFA"
PANEL = "#0D1727"
PANEL_EDGE = "#2A3A50"
GRID_COLOR = "#8FA8D8"
RED = "#FB7185"


TIMES_TEX_TEMPLATE = TexTemplate()
TIMES_TEX_TEMPLATE.add_to_preamble(r"\usepackage{mathptmx}")
MathTex.set_default(tex_template=TIMES_TEX_TEMPLATE)


TARGET_DURATIONS = {
    "ThreeNumbersHook": 28.0,
    "ConstantChanceCorridor": 38.0,
    "ThreeQuestionsAtFifty": 42.0,
    "GuaranteeReshapesWaiting": 43.0,
    "UpIdentityLayer": 36.0,
    "CapturingRadiance": 58.0,
    "StateMemoryConclusion": 34.0,
}


def cn(text: str, size: float = 0.36, color: str = INK) -> Text:
    with register_font(SMILEY_FONT_FILE):
        return Text(text, font=FONT, slant=OBLIQUE, color=color).scale(size)


def notebook_grid(spacing: float = 0.48) -> VGroup:
    width = config.frame_width + spacing
    height = config.frame_height + spacing
    x_values = np.arange(-width / 2, width / 2 + spacing, spacing)
    y_values = np.arange(-height / 2, height / 2 + spacing, spacing)
    grid = VGroup(
        *[
            Line(
                DOWN * height / 2 + RIGHT * x,
                UP * height / 2 + RIGHT * x,
                color=GRID_COLOR,
                stroke_width=1.6,
            )
            for x in x_values
        ],
        *[
            Line(
                LEFT * width / 2 + UP * y,
                RIGHT * width / 2 + UP * y,
                color=GRID_COLOR,
                stroke_width=1.6,
            )
            for y in y_values
        ],
    )
    grid.set_opacity(0.155)
    grid.set_z_index(-100)
    return grid


def set_scene_background(scene: Scene) -> None:
    scene.camera.background_color = BG
    scene.add(notebook_grid())


def finish_to(scene: Scene, target: float) -> None:
    remaining = target - scene.time
    if remaining > 0:
        scene.wait(remaining)


def scene_title(title: str, subtitle: str | None = None) -> VGroup:
    heading = cn(title, 0.52).to_edge(UP, buff=0.30)
    if subtitle is None:
        return VGroup(heading)
    sub = cn(subtitle, 0.31, MUTED).next_to(heading, DOWN, buff=0.10)
    return VGroup(heading, sub)


def panel(width: float, height: float, fill: str = PANEL, edge: str = PANEL_EDGE) -> RoundedRectangle:
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.18,
        stroke_color=edge,
        stroke_width=1.5,
        fill_color=fill,
        fill_opacity=0.95,
    )


def pill(text: str, color: str = BLUE, width: float | None = None) -> VGroup:
    label = cn(text, 0.27, color)
    box_width = width if width is not None else label.width + 0.46
    box = RoundedRectangle(
        width=box_width,
        height=0.48,
        corner_radius=0.22,
        stroke_color=color,
        stroke_width=1.4,
        fill_color=color,
        fill_opacity=0.09,
    )
    label.move_to(box)
    return VGroup(box, label)


def stat_card(
    label: str,
    value_tex: str,
    color: str,
    note: str | None = None,
    width: float = 3.55,
    height: float = 2.05,
) -> VGroup:
    box = panel(width, height, fill="#0B1626", edge=color)
    label_mob = cn(label, 0.31, MUTED)
    value = MathTex(value_tex, color=color).scale(0.88)
    contents: list[Mobject] = [label_mob, value]
    if note:
        contents.append(cn(note, 0.25, MUTED))
    stack = VGroup(*contents).arrange(DOWN, buff=0.18)
    max_width = width - 0.46
    if stack.width > max_width:
        stack.scale_to_fit_width(max_width)
    max_height = height - 0.35
    if stack.height > max_height:
        stack.scale_to_fit_height(max_height)
    stack.move_to(box)
    return VGroup(box, stack)


def star_icon(color: str = GOLD, radius: float = 0.25) -> Star:
    return Star(
        n=5,
        outer_radius=radius,
        inner_radius=radius * 0.43,
        color=color,
        fill_color=color,
        fill_opacity=1,
        stroke_width=0,
    )


def result_card(
    label: str,
    color: str,
    subtitle: str | None = None,
    width: float = 2.15,
    *,
    show_halo: bool = True,
) -> VGroup:
    card_height = 2.55 if show_halo else (1.64 if subtitle else 1.38)
    box = RoundedRectangle(
        width=width,
        height=card_height,
        corner_radius=0.18,
        stroke_color=color,
        stroke_width=2.0,
        fill_color="#101C2D",
        fill_opacity=0.98,
    )
    halo = Circle(radius=0.52, color=color, fill_color=color, fill_opacity=0.08, stroke_opacity=0.25)
    star = star_icon(color, 0.33)
    title = cn(label, 0.33, color)
    items: list[Mobject] = [star, title]
    if show_halo:
        items.insert(0, halo)
    if subtitle:
        items.append(cn(subtitle, 0.23, MUTED))
    group = VGroup(*items).arrange(DOWN, buff=0.15).move_to(box)
    if not show_halo:
        if group.width > width - 0.30:
            group.scale_to_fit_width(width - 0.30)
        if group.height > card_height - 0.28:
            group.scale_to_fit_height(card_height - 0.28)
        group.move_to(box)
    return VGroup(box, group)


def flow_arrow(start: np.ndarray, end: np.ndarray, color: str = MUTED, width: float = 4.0) -> Arrow:
    return Arrow(
        start,
        end,
        color=color,
        stroke_width=width,
        buff=0.06,
        max_tip_length_to_length_ratio=0.18,
    )


def gate(
    center: np.ndarray,
    height: float = 1.8,
    opening: float = 0.18,
    color: str = BLUE,
    label: str | None = None,
) -> VGroup:
    opening = float(np.clip(opening, 0.08, 0.92))
    half = height / 2
    gap = height * opening / 2
    upper = Line(center + UP * gap, center + UP * half, color=color, stroke_width=5)
    lower = Line(center + DOWN * gap, center + DOWN * half, color=color, stroke_width=5)
    cap_top = Line(center + LEFT * 0.10 + UP * half, center + RIGHT * 0.10 + UP * half, color=color, stroke_width=3)
    cap_bottom = Line(center + LEFT * 0.10 + DOWN * half, center + RIGHT * 0.10 + DOWN * half, color=color, stroke_width=3)
    pieces: list[Mobject] = [upper, lower, cap_top, cap_bottom]
    if label is not None:
        pieces.append(cn(label, 0.24, color).next_to(lower, DOWN, buff=0.12))
    return VGroup(*pieces)


def particle_cloud(count: int, center: np.ndarray, columns: int = 10, color: str = BLUE) -> VGroup:
    rows = int(np.ceil(count / columns))
    dots = VGroup()
    for index in range(count):
        col = index % columns
        row = index // columns
        point = center + RIGHT * (col - (columns - 1) / 2) * 0.105 + UP * ((rows - 1) / 2 - row) * 0.105
        dots.add(Dot(point, radius=0.026, color=color, fill_opacity=0.95))
    return dots


def question_card(
    question: str,
    denominator: str,
    value_tex: str,
    color: str,
    formula_tex: str,
) -> VGroup:
    box = panel(3.72, 2.08, fill="#0B1626", edge=color)
    q = cn(question, 0.30, INK)
    denominator_mob = cn(denominator, 0.25, color)
    value = MathTex(value_tex, color=color).scale(0.72)
    formula = MathTex(formula_tex, color=MUTED).scale(0.40)
    stack = VGroup(q, denominator_mob, value, formula).arrange(DOWN, buff=0.09).move_to(box)
    if stack.width > 3.34:
        stack.scale_to_fit_width(3.34)
    if stack.height > 1.74:
        stack.scale_to_fit_height(1.74)
    return VGroup(box, stack)


class CoverFrame(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        self.add(notebook_grid())

        glow = Circle(radius=2.55, color=GOLD, fill_color=GOLD, fill_opacity=0.035, stroke_opacity=0)
        glow.shift(RIGHT * 3.75 + DOWN * 0.25)
        self.add(glow)

        badge = pill("原神抽卡概率", GOLD, 2.32).move_to(LEFT * 4.72 + UP * 2.78)
        title = VGroup(
            cn("三个数字", 0.98, INK),
            cn("为什么都对？", 0.98, INK),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        title.scale_to_fit_width(5.55).move_to(LEFT * 3.35 + UP * 0.72)

        numbers = VGroup(
            MathTex(r"0.6\%", color=BLUE).scale(1.33),
            MathTex(r"1.6\%", color=MINT).scale(1.33),
            cn("90抽必出", 0.60, GOLD),
        ).arrange(DOWN, buff=0.42)
        number_box = panel(4.45, 5.20, fill="#0B1626", edge=GOLD).move_to(RIGHT * 3.75 + DOWN * 0.10)
        numbers.move_to(number_box).shift(UP * 0.12)
        divider_1 = Line(LEFT * 1.40, RIGHT * 1.40, color=PANEL_EDGE, stroke_width=1.5).move_to(numbers[0].get_bottom() + DOWN * 0.23)
        divider_2 = divider_1.copy().move_to(numbers[1].get_bottom() + DOWN * 0.25)

        path = VGroup(
            pill("先等五星", BLUE, 1.62),
            flow_arrow(ORIGIN, RIGHT * 0.55, GOLD, 3.2),
            pill("再判定UP", PINK, 1.72),
        ).arrange(RIGHT, buff=0.20).move_to(LEFT * 3.42 + DOWN * 2.33)

        self.add(badge, title, number_box, numbers, divider_1, divider_2, path)


class ThreeNumbersHook(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("三个数字，问的不是一件事", "先看五星什么时候来，再看这颗五星是谁")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)

        wish_panel = panel(4.25, 4.72, fill="#0A1525", edge="#36516B")
        wish_panel.to_edge(LEFT, buff=0.62).shift(DOWN * 0.32)
        wish_title = cn("角色活动祈愿 · 规则摘要", 0.34, GOLD).next_to(wish_panel.get_top(), DOWN, buff=0.35)
        wish_note = cn("原创示意界面", 0.22, MUTED).next_to(wish_panel.get_bottom(), UP, buff=0.22)
        star = star_icon(GOLD, 0.42).move_to(wish_panel.get_center() + UP * 0.72)
        wish_button = RoundedRectangle(
            width=2.65,
            height=0.70,
            corner_radius=0.22,
            color=BLUE,
            fill_color=BLUE,
            fill_opacity=0.12,
        ).move_to(wish_panel.get_center() + DOWN * 0.88)
        wish_button_text = cn("祈愿一次", 0.34, BLUE).move_to(wish_button)
        self.play(FadeIn(wish_panel), FadeIn(wish_title), GrowFromCenter(star), run_time=1.4)
        self.play(FadeIn(wish_button), FadeIn(wish_button_text), FadeIn(wish_note), run_time=0.8)
        self.wait(1.2)

        cards = VGroup(
            stat_card("五星基础概率", r"0.6\%", BLUE, "五星的基础数字", 2.63, 2.00),
            stat_card("含保底综合概率", r"1.6\%", MINT, "很多轮合起来的长期平均", 2.63, 2.00),
            stat_card("五星最长等待", r"\le 90", GOLD, "最晚到第 90 抽", 2.63, 2.00),
        ).arrange(RIGHT, buff=0.22)
        cards.to_edge(RIGHT, buff=0.45).shift(UP * 0.66)
        self.play(LaggedStart(*[FadeIn(card, shift=UP * 0.18) for card in cards], lag_ratio=0.18), run_time=2.0)
        self.wait(2.6)

        question = cn("哪一个才是“下一抽”的概率？", 0.42, INK)
        question.next_to(cards, DOWN, buff=0.38)
        underline = Line(question.get_left(), question.get_right(), color=GOLD, stroke_width=4).next_to(question, DOWN, buff=0.10)
        self.play(FadeIn(question, shift=UP * 0.10), Create(underline), run_time=1.1)
        self.wait(2.2)

        five_star = result_card("五星", GOLD, "第一层：什么时候来", 1.88)
        up_card = result_card("当期UP", PINK, "第二层：它是谁", 2.10)
        VGroup(five_star, up_card).arrange(RIGHT, buff=0.82)
        branch = flow_arrow(five_star.get_right(), up_card.get_left(), PINK, 4.5)
        path = VGroup(five_star, branch, up_card)
        path.scale(0.55).next_to(question, DOWN, buff=0.25)
        path_label = cn("出了五星，还要过一次身份判定", 0.29, MUTED).next_to(path, DOWN, buff=0.15)
        self.play(FadeIn(five_star, shift=RIGHT * 0.15), GrowArrow(branch), FadeIn(up_card, shift=RIGHT * 0.15), run_time=1.5)
        self.wait(2.0)
        self.play(FadeIn(path_label), run_time=0.7)
        self.wait(1.2)

        two_layers = VGroup(
            pill("五星何时出现", BLUE, 2.10),
            pill("是不是当期UP", PINK, 2.25),
        ).arrange(RIGHT, buff=0.30).next_to(path_label, DOWN, buff=0.24)
        self.play(FadeIn(two_layers, shift=UP * 0.10), run_time=0.9)
        self.wait(2.4)
        self.play(Indicate(cards[0], color=BLUE), Indicate(cards[1], color=MINT), Indicate(cards[2], color=GOLD), run_time=1.8)
        self.wait(1.2)
        finish_to(self, TARGET_DURATIONS["ThreeNumbersHook"])


class ConstantChanceCorridor(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("假设每抽都只有 0.6%", "先造一个没有保底的对照卡池")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)

        model_tag = pill("教学对照 · 不是真实规则", RED, 2.85).to_edge(LEFT, buff=0.55).shift(UP * 2.25)
        formula = MathTex(r"p=0.006", color=BLUE).scale(0.72)
        independent = cn("每抽独立", 0.28, BLUE)
        model_formula = VGroup(formula, independent).arrange(RIGHT, buff=0.24)
        model_formula.to_edge(RIGHT, buff=0.66).shift(UP * 2.28)
        self.play(FadeIn(model_tag), FadeIn(model_formula), run_time=1.0)
        self.wait(2.0)

        corridor = panel(12.75, 3.25, fill="#091525", edge="#31455F").shift(DOWN * 0.40)
        rail_top = Line(corridor.get_left() + RIGHT * 0.50 + UP * 0.57, corridor.get_right() + LEFT * 0.50 + UP * 0.57, color="#304259", stroke_width=2)
        rail_bottom = rail_top.copy().shift(DOWN * 1.15)
        self.play(FadeIn(corridor), Create(rail_top), Create(rail_bottom), run_time=1.1)
        self.wait(1.2)

        x_positions = [-4.75, -3.25, -1.75, -0.25, 1.25, 3.35, 5.20]
        labels = ["1", "2", "3", "…", "50", "…", "90"]
        gates = VGroup(
            *[
                gate(np.array([x, -0.40, 0.0]), 1.72, 0.18, BLUE, label)
                for x, label in zip(x_positions, labels)
            ]
        )
        self.play(LaggedStart(*[Create(g) for g in gates], lag_ratio=0.10), run_time=1.8)
        self.wait(1.5)

        players = particle_cloud(60, LEFT * 5.75 + DOWN * 0.40, columns=10, color=BLUE)
        players_label = cn("60 个点代表 1 万名玩家", 0.26, MUTED).next_to(corridor, DOWN, buff=0.18).align_to(corridor, LEFT).shift(RIGHT * 0.38)
        self.play(FadeIn(players), FadeIn(players_label), run_time=0.8)
        self.wait(1.5)

        survivor_positions = []
        for index in range(35):
            col = index % 7
            row = index // 7
            survivor_positions.append(RIGHT * 5.73 + DOWN * 0.40 + LEFT * col * 0.095 + UP * (row - 2) * 0.10)
        exit_positions = []
        for index in range(25):
            col = index % 5
            row = index // 5
            exit_positions.append(LEFT * 1.20 + UP * 1.56 + RIGHT * col * 0.105 + UP * row * 0.10)

        move_anims = []
        for index, dot in enumerate(players):
            if index < 35:
                move_anims.append(dot.animate.move_to(survivor_positions[index]))
            else:
                move_anims.append(dot.animate.set_color(GOLD).move_to(exit_positions[index - 35]))
        self.play(LaggedStart(*move_anims, lag_ratio=0.015), run_time=5.2, rate_func=smooth)
        self.wait(3.0)

        survived_box = stat_card("90 抽后仍没见到五星", r"58.2\%", RED, "在这个固定概率模型里", 3.88, 2.08)
        survived_box.to_edge(RIGHT, buff=0.58).shift(DOWN * 2.26)
        survived_formula = MathTex(r"(1-0.006)^{90}=0.994^{90}\approx58.2\%", color=INK).scale(0.60)
        survived_formula.to_edge(LEFT, buff=0.64).shift(DOWN * 2.18)
        self.play(
            FadeOut(players_label),
            FadeIn(survived_formula, shift=UP * 0.10),
            FadeIn(survived_box, shift=LEFT * 0.15),
            run_time=1.3,
        )
        self.wait(3.5)

        contradiction = cn("所以：固定 0.6% 不能同时解释“90 抽必出”", 0.39, GOLD)
        contradiction.to_edge(DOWN, buff=0.26)
        self.play(FadeIn(contradiction, shift=UP * 0.10), run_time=1.0)
        self.wait(3.2)
        self.play(Indicate(gates[-1], color=GOLD), Indicate(survived_box, color=RED), run_time=1.7)
        self.wait(2.5)
        finish_to(self, TARGET_DURATIONS["ConstantChanceCorridor"])


class ThreeQuestionsAtFifty(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("“第 50 抽的概率”有三个答案", "先把问题补完整")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)

        population_box = panel(3.20, 4.42, fill="#0A1525", edge="#36516B")
        population_box.to_edge(LEFT, buff=0.62).shift(DOWN * 0.26)
        population_title = cn("先看分母是谁", 0.35, INK).next_to(population_box.get_top(), DOWN, buff=0.30)
        all_players = particle_cloud(42, LEFT * 4.95 + UP * 0.50, columns=7, color=MINT)
        all_label = cn("最初全部玩家", 0.28, MINT).next_to(all_players, UP, buff=0.16)
        filter_arrow = MathTex(r"\Downarrow", color=MUTED).scale(0.68).move_to(LEFT * 4.95 + DOWN * 0.16)
        filter_note = cn("先经过 49 抽", 0.23, MUTED).next_to(filter_arrow, RIGHT, buff=0.16)
        survivors = particle_cloud(31, LEFT * 5.12 + DOWN * 1.02, columns=7, color=BLUE)
        survivors_label = cn("连续 49 抽仍没出的人", 0.27, BLUE).next_to(survivors, DOWN, buff=0.25)
        gate_50 = gate(LEFT * 3.90 + DOWN * 1.02, height=1.22, opening=0.18, color=BLUE, label="第 50 抽")
        self.play(FadeIn(population_box), FadeIn(population_title), run_time=0.8)
        self.play(FadeIn(all_players), FadeIn(all_label), run_time=0.7)
        self.play(FadeIn(filter_arrow), FadeIn(filter_note), FadeIn(survivors), FadeIn(survivors_label), Create(gate_50), run_time=1.1)
        self.wait(3.5)

        questions = VGroup(
            question_card(
                "前 49 抽没出，下一抽？",
                "分母：走到第50抽的人",
                r"0.6\%",
                BLUE,
                r"p=0.006",
            ),
            question_card(
                "正好第 50 抽首次出金？",
                "分母：最初全部玩家",
                r"\approx0.447\%",
                GOLD,
                r"0.994^{49}\times0.006",
            ),
            question_card(
                "前 50 抽内至少一次？",
                "分母：最初全部玩家",
                r"\approx25.99\%",
                MINT,
                r"1-0.994^{50}",
            ),
        ).arrange(DOWN, buff=0.17)
        questions.to_edge(RIGHT, buff=0.55).shift(DOWN * 0.55)

        for index, card in enumerate(questions):
            self.play(FadeIn(card, shift=LEFT * 0.18), run_time=1.0)
            self.play(Indicate(card[1][2], color=[BLUE, GOLD, MINT][index]), run_time=1.0)
            self.wait(4.2)

        denominator_note = pill("不能把三种问法当成同一批人的三种去向", RED, 3.42)
        denominator_note.scale(0.88).next_to(population_box, DOWN, buff=0.18)
        self.play(FadeIn(denominator_note, shift=UP * 0.08), run_time=1.0)
        self.wait(3.5)

        summary = cn("不是数字打架，是三个问题被说成了一句话。", 0.34, INK)
        if summary.width > 3.12:
            summary.scale_to_fit_width(3.12)
        summary.move_to(denominator_note)
        self.play(ReplacementTransform(denominator_note, summary), run_time=1.0)
        self.wait(3.5)
        self.play(
            Indicate(questions[0], color=BLUE),
            Indicate(questions[1], color=GOLD),
            Indicate(questions[2], color=MINT),
            run_time=2.0,
        )
        self.wait(3.0)
        finish_to(self, TARGET_DURATIONS["ThreeQuestionsAtFifty"])


class GuaranteeReshapesWaiting(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("第 90 道门必须完全打开", "公开的是边界，不是每一抽的完整曲线")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)

        top_box = panel(12.15, 1.46, fill="#091525", edge="#31455F").shift(UP * 1.44)
        bottom_box = panel(12.15, 1.86, fill="#091525", edge=GOLD).shift(DOWN * 0.52)
        top_label = pill("固定 0.6% 对照", BLUE, 2.12).move_to(top_box.get_left() + RIGHT * 1.35)
        bottom_label = pill("真实规则的公开边界", GOLD, 2.72).move_to(bottom_box.get_left() + RIGHT * 1.67)
        self.play(FadeIn(top_box), FadeIn(bottom_box), FadeIn(top_label), FadeIn(bottom_label), run_time=1.1)
        self.wait(1.5)

        top_xs = np.linspace(-2.98, 5.38, 9)
        top_gates = VGroup(*[gate(np.array([x, 1.44, 0]), 0.95, 0.18, BLUE) for x in top_xs])
        top_nums = VGroup(
            cn("1", 0.21, MUTED).next_to(top_gates[0], DOWN, buff=0.07),
            cn("…", 0.21, MUTED).next_to(top_gates[4], DOWN, buff=0.07),
            cn("90", 0.21, MUTED).next_to(top_gates[-1], DOWN, buff=0.07),
        )
        self.play(LaggedStart(*[Create(item) for item in top_gates], lag_ratio=0.07), FadeIn(top_nums), run_time=1.6)
        self.wait(2.5)

        known_start = gate(LEFT * 2.95 + DOWN * 0.48, 1.18, 0.18, BLUE, "基础 0.6%")
        unknown_gates = VGroup(
            *[
                VGroup(
                    RoundedRectangle(
                        width=0.30,
                        height=1.18,
                        corner_radius=0.08,
                        stroke_color=VIOLET,
                        stroke_width=2.0,
                        fill_color=VIOLET,
                        fill_opacity=0.16,
                    ).move_to(np.array([x, -0.48, 0])),
                    cn("?", 0.34, VIOLET).move_to(np.array([x, -0.48, 0])),
                )
                for x in [-1.25, 0.0, 1.25]
            ]
        )
        final_gate = gate(RIGHT * 3.35 + DOWN * 0.48, 1.32, 0.92, GOLD, "90 抽内必出")
        unknown_note = cn("中间每一道门多宽：官方未公开", 0.28, MUTED).next_to(unknown_gates, DOWN, buff=0.18)
        self.play(Create(known_start), run_time=0.8)
        self.wait(1.2)
        self.play(LaggedStart(*[FadeIn(item, shift=UP * 0.08) for item in unknown_gates], lag_ratio=0.15), FadeIn(unknown_note), run_time=1.5)
        self.wait(3.0)
        self.play(Create(final_gate), run_time=1.1)
        self.play(Indicate(final_gate, color=GOLD), run_time=1.2)
        self.wait(3.0)

        formula = cn("门有多宽：看走到门前的人里，这一抽有多少出金", 0.34, INK)
        formula.to_edge(LEFT, buff=0.66).shift(DOWN * 2.28)
        q_note = cn("这里的问号，是“没公开”，不是“固定不变”。", 0.28, MUTED)
        q_note.next_to(formula, DOWN, buff=0.14).align_to(formula, LEFT)
        self.play(FadeIn(formula, shift=UP * 0.08), FadeIn(q_note), run_time=1.2)
        self.wait(3.5)

        long_run = stat_card("含保底的长期综合比例", r"1.6\%", MINT, "1000 抽平均约 16 个五星", 3.83, 1.92)
        long_run.to_edge(RIGHT, buff=0.54).shift(DOWN * 2.35)
        self.play(FadeIn(long_run, shift=LEFT * 0.15), run_time=1.0)
        self.wait(3.0)

        meaning = VGroup(
            pill("0.6%：基础概率", BLUE, 2.40),
            pill("1.6%：长期综合", MINT, 2.54),
            pill("90：等待上限", GOLD, 2.35),
        ).arrange(RIGHT, buff=0.24).to_edge(DOWN, buff=0.20)
        self.play(FadeOut(VGroup(formula, q_note, long_run), shift=DOWN * 0.10), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(item, shift=UP * 0.10) for item in meaning], lag_ratio=0.18), run_time=1.5)
        self.wait(3.0)
        self.play(Indicate(unknown_gates, color=VIOLET), Indicate(meaning, color=GOLD), run_time=1.8)
        self.wait(3.0)
        finish_to(self, TARGET_DURATIONS["GuaranteeReshapesWaiting"])


class UpIdentityLayer(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("出了五星以后，还要判断是不是 UP", "五星计数和大保底，是两份不同的记录")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)

        first_panel = panel(3.62, 4.62, fill="#0A1525", edge=BLUE).to_edge(LEFT, buff=0.58).shift(DOWN * 0.28)
        second_panel = panel(7.55, 4.62, fill="#0A1525", edge=PINK).to_edge(RIGHT, buff=0.58).shift(DOWN * 0.28)
        first_title = cn("第一关：五星什么时候来", 0.35, BLUE).next_to(first_panel.get_top(), DOWN, buff=0.32)
        second_title = cn("第二关：这个五星是谁", 0.35, PINK).next_to(second_panel.get_top(), DOWN, buff=0.32)
        self.play(FadeIn(first_panel), FadeIn(second_panel), FadeIn(first_title), FadeIn(second_title), run_time=1.1)
        self.wait(1.5)

        counter = VGroup(
            cn("上次五星以后", 0.30, MUTED),
            cn("已经抽了 57 次", 0.46, BLUE),
            cn("五星出现后归零", 0.26, MUTED),
        ).arrange(DOWN, buff=0.25).move_to(first_panel).shift(DOWN * 0.10)
        gold_result = result_card("五星出现", GOLD, None, 1.80).scale(0.70)
        gold_result.move_to(first_panel.get_right() + RIGHT * 0.54 + DOWN * 0.10)
        arrow_to_identity = flow_arrow(first_panel.get_right() + RIGHT * 0.04 + DOWN * 0.10, second_panel.get_left() + LEFT * 0.04 + DOWN * 0.10, GOLD, 4.5)
        self.play(FadeIn(counter), run_time=1.0)
        self.wait(2.0)
        self.play(GrowArrow(arrow_to_identity), FadeIn(gold_result, shift=RIGHT * 0.15), run_time=1.0)
        self.wait(1.5)

        normal_state = pill("当前：不是保证状态", MUTED, 2.70).move_to(second_panel.get_top() + DOWN * 1.05 + LEFT * 1.75)
        fork_point = Dot(second_panel.get_center() + LEFT * 2.05 + UP * 0.12, radius=0.075, color=GOLD)
        up = result_card("当期UP", PINK, "基础 50%", 2.0).scale(0.64).move_to(second_panel.get_center() + RIGHT * 1.65 + UP * 0.82)
        off = result_card("非UP五星", GRAY, "俗称：歪了", 2.0).scale(0.64).move_to(second_panel.get_center() + RIGHT * 1.65 + DOWN * 0.72)
        up_arrow = flow_arrow(fork_point.get_center(), up.get_left(), PINK, 4.0)
        off_arrow = flow_arrow(fork_point.get_center(), off.get_left(), GRAY, 4.0)
        self.play(FadeIn(normal_state), FadeIn(fork_point), GrowArrow(up_arrow), GrowArrow(off_arrow), run_time=1.2)
        self.wait(2.5)
        self.play(FadeIn(up, shift=RIGHT * 0.12), FadeIn(off, shift=RIGHT * 0.12), run_time=1.0)
        self.wait(3.0)

        guarantee_state = pill("歪了  →  下个五星保证是当期UP", GOLD, 4.38)
        guarantee_state.move_to(second_panel.get_center() + DOWN * 1.78)
        self.play(FadeIn(guarantee_state, shift=UP * 0.08), run_time=1.1)
        self.wait(6.5)

        rule = cn("50% 和歪后保证，说的是“五星身份”，不是每一抽。", 0.36, INK)
        rule.to_edge(DOWN, buff=0.26)
        self.play(FadeIn(rule, shift=UP * 0.10), run_time=1.0)
        self.wait(3.0)
        self.play(Indicate(counter, color=BLUE), Indicate(guarantee_state, color=GOLD), run_time=1.8)
        self.wait(2.5)
        finish_to(self, TARGET_DURATIONS["UpIdentityLayer"])


class CapturingRadiance(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("非保证五星，多了一条 UP 路径", "捕获明光只在本来不保证是 UP 时参与")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)

        entering = result_card("已经出五星", GOLD, "当前非保证UP", 2.24).move_to(LEFT * 4.65 + UP * 0.90).scale(0.86)
        decision_box = panel(3.28, 2.55, fill="#141329", edge=PINK).move_to(LEFT * 0.65 + UP * 0.90)
        decision_title = cn("五星身份判定", 0.34, INK)
        ordinary = pill("普通UP判定", MUTED, 1.82)
        radiance_path = pill("捕获明光可能触发", PINK, 2.28)
        internal_note = cn("内部先后没有公开", 0.22, MUTED)
        decision_stack = VGroup(decision_title, ordinary, radiance_path, internal_note).arrange(DOWN, buff=0.13).move_to(decision_box)
        up_result = result_card("当期UP", PINK, None, 1.88).move_to(RIGHT * 4.80 + UP * 1.72).scale(0.70)
        off_result = result_card("非UP五星", GRAY, None, 1.88).move_to(RIGHT * 4.80 + UP * 0.02).scale(0.70)
        enter_arrow = flow_arrow(entering.get_right(), decision_box.get_left(), GOLD, 4.5)
        up_arrow = flow_arrow(decision_box.get_right(), up_result.get_left(), PINK, 4.5)
        off_arrow = flow_arrow(decision_box.get_right(), off_result.get_left(), GRAY, 4.5)
        self.play(FadeIn(entering, shift=RIGHT * 0.12), run_time=0.9)
        self.wait(1.5)
        self.play(GrowArrow(enter_arrow), FadeIn(decision_box), FadeIn(decision_stack), run_time=1.1)
        self.wait(2.0)
        self.play(GrowArrow(up_arrow), GrowArrow(off_arrow), FadeIn(up_result), FadeIn(off_result), run_time=1.1)
        self.wait(2.0)
        self.play(Flash(radiance_path, color=PINK, flash_radius=0.78, line_length=0.20, num_lines=10), run_time=1.0)

        facts = VGroup(
            stat_card("基础触发概率", r"0.018\%", PINK, "按每一次祈愿来数", 3.42, 1.82),
            stat_card("计入捕获明光后", r"55\%", MINT, "已出五星且当前非保证UP", 4.10, 1.82),
        ).arrange(RIGHT, buff=0.32).move_to(DOWN * 1.20)
        self.play(LaggedStart(*[FadeIn(card, shift=UP * 0.12) for card in facts], lag_ratio=0.22), run_time=1.5)
        self.wait(3.0)

        scope = pill("这两个数字都不是“每抽直接出UP”的概率", MUTED, 4.82)
        scope.next_to(facts, DOWN, buff=0.20)
        self.play(FadeIn(scope), run_time=0.7)
        self.wait(2.0)
        self.play(Indicate(facts[0], color=PINK), Indicate(facts[1], color=MINT), run_time=1.7)

        first_beat = VGroup(
            entering,
            decision_box,
            decision_stack,
            up_result,
            off_result,
            enter_arrow,
            up_arrow,
            off_arrow,
            facts,
            scope,
        )
        self.play(FadeOut(first_beat, shift=UP * 0.16), run_time=0.8)

        timeline_title = cn("连续三轮都是：先歪一次，再靠保证拿到UP", 0.40, INK).move_to(UP * 2.12)
        self.play(FadeIn(timeline_title, shift=DOWN * 0.10), run_time=0.8)
        self.wait(2.0)

        cycle_groups = VGroup()
        for index in range(3):
            cycle_box = panel(3.38, 2.05, fill="#0B1626", edge=PANEL_EDGE)
            cycle_name = pill(f"第 {index + 1} 轮", BLUE, 1.12)
            off_chip = VGroup(star_icon(GRAY, 0.15), cn("非UP", 0.26, GRAY)).arrange(RIGHT, buff=0.10)
            arr = MathTex(r"\longrightarrow", color=GOLD).scale(0.58)
            up_chip = VGroup(star_icon(GOLD, 0.15), cn("保证UP", 0.26, GOLD)).arrange(RIGHT, buff=0.10)
            sequence = VGroup(off_chip, arr, up_chip).arrange(RIGHT, buff=0.14)
            note = cn("两次五星组成一轮", 0.22, MUTED)
            stack = VGroup(cycle_name, sequence, note).arrange(DOWN, buff=0.20).move_to(cycle_box)
            cycle_groups.add(VGroup(cycle_box, stack))
        cycle_groups.arrange(RIGHT, buff=0.24).move_to(UP * 0.50)

        for cycle in cycle_groups:
            self.play(FadeIn(cycle, shift=RIGHT * 0.14), run_time=1.1)
            self.play(Indicate(cycle[1][1][0], color=GRAY), Indicate(cycle[1][1][2], color=GOLD), run_time=0.9)
            self.wait(1.2)

        clarification = cn("不是连续六个五星都歪，而是“歪 → 保证UP”重复三次。", 0.34, MUTED)
        clarification.next_to(cycle_groups, DOWN, buff=0.30)
        self.play(FadeIn(clarification), run_time=0.8)
        self.wait(2.2)

        next_box = panel(9.45, 1.38, fill="#171329", edge=PINK).to_edge(DOWN, buff=0.27)
        next_flow = VGroup(
            cn("再下一次得到五星", 0.32, INK),
            MathTex(r"\Longrightarrow", color=PINK).scale(0.78),
            cn("捕获明光必定触发", 0.34, PINK),
            MathTex(r"\Longrightarrow", color=PINK).scale(0.78),
            cn("当期UP", 0.34, GOLD),
        ).arrange(RIGHT, buff=0.24).move_to(next_box)
        if next_flow.width > next_box.width - 0.45:
            next_flow.scale_to_fit_width(next_box.width - 0.45)
        self.play(FadeIn(next_box, shift=UP * 0.10), FadeIn(next_flow, shift=UP * 0.10), run_time=1.2)
        self.play(Flash(next_flow[2], color=PINK, flash_radius=1.15, line_length=0.22, num_lines=12), run_time=1.2)
        self.wait(3.0)

        disclosure = VGroup(
            pill("已公开：三轮后必触发", GOLD, 2.80),
            pill("未公开：中间各阶段概率", MUTED, 3.24),
        ).arrange(RIGHT, buff=0.26).move_to(clarification)
        self.play(ReplacementTransform(clarification, disclosure), run_time=1.0)
        self.wait(2.5)
        self.play(Indicate(cycle_groups, color=PINK), Indicate(next_box, color=GOLD), run_time=2.0)
        self.wait(1.0)
        finish_to(self, TARGET_DURATIONS["CapturingRadiance"])


class StateMemoryConclusion(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("先问清楚，你算的是哪一种概率", "同一个账号里，有三份记录同时在变")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)

        memory = panel(3.25, 4.75, fill="#0A1525", edge=VIOLET).to_edge(LEFT, buff=0.58).shift(DOWN * 0.28)
        memory_title = cn("卡池记住三件事", 0.39, VIOLET).next_to(memory.get_top(), DOWN, buff=0.34)
        memory_rows = VGroup(
            VGroup(MathTex(r"1", color=BLUE).scale(0.58), cn("五星计数", 0.33, INK)).arrange(RIGHT, buff=0.20),
            VGroup(MathTex(r"2", color=GOLD).scale(0.58), cn("是否保证UP", 0.33, INK)).arrange(RIGHT, buff=0.20),
            VGroup(MathTex(r"3", color=PINK).scale(0.58), cn("连歪记录", 0.33, INK)).arrange(RIGHT, buff=0.20),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.50).move_to(memory).shift(DOWN * 0.18)
        self.play(FadeIn(memory), FadeIn(memory_title), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(row, shift=RIGHT * 0.12) for row in memory_rows], lag_ratio=0.22), run_time=1.5)
        self.wait(2.5)

        flow_panel = panel(8.60, 4.75, fill="#0A1525", edge="#36516B").to_edge(RIGHT, buff=0.58).shift(DOWN * 0.28)
        flow_title = cn("一次完整的判断路径", 0.39, INK).next_to(flow_panel.get_top(), DOWN, buff=0.34)
        self.play(FadeIn(flow_panel), FadeIn(flow_title), run_time=0.9)

        first_row = VGroup(
            pill("五星计数 · 五星规则", BLUE, 2.54),
            MathTex(r"\longrightarrow", color=MUTED).scale(0.62),
            pill("这一抽出五星吗？", BLUE, 2.42),
            MathTex(r"\longrightarrow", color=MUTED).scale(0.62),
            pill("五星 / 继续抽", GOLD, 1.84),
        ).arrange(RIGHT, buff=0.18)
        if first_row.width > flow_panel.width - 0.44:
            first_row.scale_to_fit_width(flow_panel.width - 0.44)
        first_row.move_to(flow_panel.get_center() + UP * 1.15)
        self.play(LaggedStart(*[FadeIn(item, shift=RIGHT * 0.08) for item in first_row], lag_ratio=0.12), run_time=1.6)
        self.wait(2.5)

        first_rules = VGroup(
            pill("0.6% 基础", BLUE, 1.65),
            pill("1.6% 长期综合", MINT, 2.05),
            pill("90 抽内必出", GOLD, 1.88),
        ).arrange(RIGHT, buff=0.15).next_to(first_row, DOWN, buff=0.22)
        self.play(LaggedStart(*[FadeIn(item, shift=UP * 0.06) for item in first_rules], lag_ratio=0.14), run_time=1.1)
        self.wait(1.8)

        down_arrow = MathTex(r"\Downarrow", color=GOLD).scale(0.64).next_to(first_rules, DOWN, buff=0.08)
        second_row = VGroup(
            pill("大保底 · 连歪记录", PINK, 2.42),
            MathTex(r"\longrightarrow", color=MUTED).scale(0.62),
            pill("这个五星是UP吗？", PINK, 2.48),
            MathTex(r"\longrightarrow", color=MUTED).scale(0.62),
            pill("UP / 非UP", GOLD, 1.74),
        ).arrange(RIGHT, buff=0.18)
        if second_row.width > flow_panel.width - 0.44:
            second_row.scale_to_fit_width(flow_panel.width - 0.44)
        second_row.next_to(down_arrow, DOWN, buff=0.10)
        self.play(FadeIn(down_arrow), LaggedStart(*[FadeIn(item, shift=RIGHT * 0.08) for item in second_row], lag_ratio=0.12), run_time=1.6)
        self.wait(2.5)

        second_rules = VGroup(
            pill("50% 基础判定", PINK, 1.96),
            pill("歪后大保底", GOLD, 1.82),
            pill("捕获明光", VIOLET, 1.62),
        ).arrange(RIGHT, buff=0.15).next_to(second_row, DOWN, buff=0.22)
        self.play(LaggedStart(*[FadeIn(item, shift=UP * 0.08) for item in second_rules], lag_ratio=0.16), run_time=1.3)
        self.wait(2.0)

        final_question = cn("“第 80 抽概率多大？”——先说清楚你真正想问什么。", 0.43, INK)
        final_question.to_edge(DOWN, buff=0.24)
        self.play(FadeIn(final_question, shift=UP * 0.12), run_time=1.1)
        self.wait(2.5)
        self.play(
            Indicate(memory_rows[0], color=BLUE),
            Indicate(memory_rows[1], color=GOLD),
            Indicate(memory_rows[2], color=PINK),
            run_time=1.8,
        )
        self.play(Indicate(first_rules, color=BLUE), Indicate(second_rules, color=PINK), run_time=1.8)
        self.wait(1.5)
        finish_to(self, TARGET_DURATIONS["StateMemoryConclusion"])
