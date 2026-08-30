from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from manim import *


SCENE_DIR = Path(__file__).resolve().parent
if str(SCENE_DIR) not in sys.path:
    sys.path.insert(0, str(SCENE_DIR))

from gacha_pity_probability_v1 import (  # noqa: E402
    BLUE,
    GOLD,
    GRAY,
    INK,
    MINT,
    MUTED,
    PANEL,
    PANEL_EDGE,
    PINK,
    RED,
    VIOLET,
    cn,
    finish_to,
    flow_arrow,
    panel,
    pill,
    result_card,
    scene_title,
    set_scene_background,
    star_icon,
    stat_card,
)
from gacha_pity_probability_v2 import (  # noqa: E402
    BASE_Q,
    F_FIXED_CDF,
    F_FIXED_PMF,
    F_HARD_CDF,
    F_HARD_PMF,
    ILLUSTRATIVE_Q,
    Q_FIXED,
    Q_HARD_ONLY,
    distribution_from_q,
    expected_wait,
    probability_axes,
    sampled_dots,
    stem_plot,
    trend_path,
    x_tick_labels,
)


TARGET_DURATIONS_V4 = {
    "ThreeNumbersHookV4": 23.466667,
    "CohortAfterEachPullV4": 37.183333,
    "PullFiftyThreeViewsV4": 38.666667,
    "ConditionalProbabilityCurveFullV4": 19.000000,
    "FirstGoldPmfCurveFullV4": 31.633333,
    "CumulativeCdfCurveFullV4": 27.666667,
    "CompactCurveRelationshipV4": 28.750000,
    "HardPityCurveDashboardV4": 33.716667,
    "IntegratedRateVsHardPityV4": 29.350000,
    "NonUniquePerPullCurvesV4": 19.866667,
    "CommunitySampleDistributionV4": 58.116667,
    "CommunityFitComparisonV4": 44.433333,
    "FiveStarThenUpIdentityV4": 29.200000,
    "UpWaitingTwoPeaksV4": 35.866667,
    "CapturingRadianceBasicsV4": 31.633333,
    "CapturingRadianceHistoryV4": 25.016667,
    "ProbabilityStateConclusionV4": 38.100000,
}

LEFT_CENTER = np.array([-2.52, -0.22, 0.0])
RIGHT_CENTER = np.array([4.42, -0.22, 0.0])
LEFT_WIDTH = 8.42
RIGHT_WIDTH = 4.42
CONTENT_HEIGHT = 5.60
DIM_GOLD = "#A37B2C"

# A common community fit published with genshin-wishes.com aggregate data:
# 0.6% through pull 73, then +6 percentage points per pull, with hard pity at 90.
# It is a data-informed fit, not an official per-pull probability table.
COMMUNITY_FIT_Q = np.full(90, BASE_Q)
COMMUNITY_FIT_Q[73:89] = BASE_Q + 0.06 * np.arange(1, 17)
COMMUNITY_FIT_Q[89] = 1.0
COMMUNITY_FIT_SURVIVAL, COMMUNITY_FIT_PMF, COMMUNITY_FIT_CDF = distribution_from_q(
    COMMUNITY_FIT_Q
)

COMMUNITY_DATA_PATH = (
    SCENE_DIR.parent / "data" / "paimon_moe_character_event_pity_2025-06-09.json"
)
with COMMUNITY_DATA_PATH.open("r", encoding="utf-8") as community_data_file:
    COMMUNITY_SAMPLE = json.load(community_data_file)

COMMUNITY_SAMPLE_COUNTS = np.asarray(COMMUNITY_SAMPLE["five_star_hit_counts"], dtype=float)
COMMUNITY_SAMPLE_PMF = COMMUNITY_SAMPLE_COUNTS / COMMUNITY_SAMPLE_COUNTS.sum()
COMMUNITY_SAMPLE_Q = np.asarray(COMMUNITY_SAMPLE["estimated_conditional_q"], dtype=float)


def hold_to(scene: Scene, target: float) -> None:
    remaining = target - scene.time
    if remaining > 0:
        scene.wait(remaining)


def scene_title(title: str, subtitle: str | None = None) -> VGroup:
    """Compact title band that returns more height to the visual panels."""

    heading = cn(title, 0.46).move_to([0.0, 3.55, 0.0])
    if subtitle is None:
        return VGroup(heading)
    sub = cn(subtitle, 0.27, MUTED).next_to(heading, DOWN, buff=0.08)
    return VGroup(heading, sub)


def fit_inside(mob: Mobject, width: float, height: float) -> Mobject:
    if mob.width > width:
        mob.scale_to_fit_width(width)
    if mob.height > height:
        mob.scale_to_fit_height(height)
    return mob


def left_panel(edge: str = PANEL_EDGE, fill: str = PANEL) -> RoundedRectangle:
    return panel(LEFT_WIDTH, CONTENT_HEIGHT, fill=fill, edge=edge).move_to(LEFT_CENTER)


def right_panel(edge: str = PANEL_EDGE, fill: str = PANEL) -> RoundedRectangle:
    return panel(RIGHT_WIDTH, CONTENT_HEIGHT, fill=fill, edge=edge).move_to(RIGHT_CENTER)


def info_state(
    heading: str,
    rows: list[tuple[str, str]],
    *,
    accent: str = INK,
    formula: str | None = None,
    note: str | None = None,
) -> VGroup:
    heading_mob = cn(heading, 0.38, accent)
    divider = Line(LEFT * 1.70, RIGHT * 1.70, color=PANEL_EDGE, stroke_width=1.4)
    body = VGroup()
    for text, color in rows:
        line = cn(text, 0.31, color)
        if line.width > 3.55:
            line.scale_to_fit_width(3.55)
        body.add(line)
    body.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    items: list[Mobject] = [heading_mob, divider, body]
    if formula is not None:
        formula_mob = MathTex(formula, color=accent).scale(0.58)
        if formula_mob.width > 3.55:
            formula_mob.scale_to_fit_width(3.55)
        items.append(formula_mob)
    if note is not None:
        note_mob = cn(note, 0.25, MUTED)
        if note_mob.width > 3.55:
            note_mob.scale_to_fit_width(3.55)
        items.append(note_mob)
    state = VGroup(*items).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
    fit_inside(state, 3.62, 4.88)
    state.move_to(RIGHT_CENTER)
    return state


def percent_y_labels(axes: Axes, values: tuple[float, ...], decimals: int = 1) -> VGroup:
    labels = VGroup()
    for value in values:
        percentage = value * 100
        if decimals == 0:
            text = rf"{percentage:.0f}\%"
        else:
            text = rf"{percentage:.{decimals}f}\%"
        label = MathTex(text, color=MUTED).scale(0.30)
        label.next_to(axes.c2p(1, value), LEFT, buff=0.10)
        labels.add(label)
    return labels


def full_chart_shell(
    heading: str,
    color: str,
    *,
    y_max: float,
    y_ticks: tuple[float, ...],
    y_decimals: int = 1,
    x_max: int = 90,
    x_ticks: tuple[int, ...] = (1, 50, 90),
) -> tuple[VGroup, Axes, RoundedRectangle]:
    box = left_panel()
    heading_mob = cn(heading, 0.36, color)
    heading_mob.move_to(box.get_top() + DOWN * 0.35)
    axes = probability_axes(
        x_max=x_max,
        y_max=y_max,
        width=7.12,
        height=4.00,
        center=LEFT_CENTER + DOWN * 0.30 + RIGHT * 0.08,
    )
    x_labels = x_tick_labels(axes, x_ticks)
    y_labels = percent_y_labels(axes, y_ticks, y_decimals)
    pull_label = cn("抽数 n", 0.23, MUTED)
    pull_label.next_to(axes, RIGHT, buff=0.08).shift(DOWN * 0.22)
    return VGroup(box, heading_mob, axes, x_labels, y_labels, pull_label), axes, box


def compact_chart_shell(
    center: np.ndarray,
    heading: str,
    color: str,
    *,
    y_max: float,
    top_label: str,
) -> tuple[VGroup, Axes, RoundedRectangle]:
    box = panel(3.95, 2.46, fill=PANEL, edge=PANEL_EDGE).move_to(center)
    heading_mob = cn(heading, 0.25, color)
    if heading_mob.width > 3.45:
        heading_mob.scale_to_fit_width(3.45)
    heading_mob.move_to(box.get_top() + DOWN * 0.27)
    axes = probability_axes(
        x_max=90,
        y_max=y_max,
        width=3.26,
        height=1.38,
        center=center + DOWN * 0.23 + RIGHT * 0.08,
    )
    x_labels = x_tick_labels(axes, (1, 90))
    y_top = MathTex(top_label, color=MUTED).scale(0.25)
    y_top.next_to(axes.c2p(1, y_max), LEFT, buff=0.06)
    return VGroup(box, heading_mob, axes, x_labels, y_top), axes, box


def compact_text_card(center: np.ndarray, heading: str, rows: list[str], color: str) -> VGroup:
    box = panel(3.95, 2.46, fill=PANEL, edge=PANEL_EDGE).move_to(center)
    title = cn(heading, 0.27, color)
    body = VGroup(*[cn(row, 0.27, INK) for row in rows]).arrange(
        DOWN, aligned_edge=LEFT, buff=0.22
    )
    stack = VGroup(title, body).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
    fit_inside(stack, 3.40, 1.82)
    stack.move_to(box)
    return VGroup(box, stack)


def vertical_scanner(axes: Axes, x_value: float, color: str = PINK) -> Line:
    return Line(
        axes.c2p(x_value, 0),
        axes.c2p(x_value, axes.y_range[1]),
        color=color,
        stroke_width=3.0,
    ).set_opacity(0.78)


def cohort_expected_counts(pull: int, *, hard_pity: bool = False) -> tuple[float, float, float, float]:
    if pull <= 0:
        return 10_000.0, 0.0, 10_000.0, 0.0
    before = 10_000.0 * (1.0 - BASE_Q) ** (pull - 1)
    chance = 1.0 if hard_pity and pull >= 90 else BASE_Q
    first_gold = before * chance
    waiting = before - first_gold
    cumulative = 10_000.0 - waiting
    return before, first_gold, waiting, cumulative


def cohort_grid(center: np.ndarray, count: int = 1000, columns: int = 40) -> VGroup:
    rows = int(np.ceil(count / columns))
    dots = VGroup()
    for index in range(count):
        column = index % columns
        row = index // columns
        point = center + RIGHT * (column - (columns - 1) / 2) * 0.143
        point += UP * ((rows - 1) / 2 - row) * 0.143
        dots.add(Dot(point, radius=0.028, color=BLUE, fill_opacity=0.94))
    return dots


def apply_cohort_state(dots: VGroup, pull: int, *, hard_pity: bool = False) -> None:
    if pull <= 0:
        for dot in dots:
            dot.set_color(BLUE).set_opacity(0.94)
        return
    before, first_gold, waiting, _ = cohort_expected_counts(pull, hard_pity=hard_pity)
    prior_tokens = int(round((10_000.0 - before) / 10.0))
    current_tokens = int(round(first_gold / 10.0))
    current_tokens = max(1, current_tokens) if first_gold > 0 else 0
    current_tokens = min(current_tokens, len(dots) - prior_tokens)
    current_end = prior_tokens + current_tokens
    waiting_tokens = int(round(waiting / 10.0))
    for index, dot in enumerate(dots):
        if index < prior_tokens:
            dot.set_color(DIM_GOLD).set_opacity(0.45)
        elif index < current_end:
            dot.set_color(GOLD).set_opacity(1.0)
        elif index < current_end + waiting_tokens:
            dot.set_color(BLUE).set_opacity(0.94)
        else:
            dot.set_color(BLUE).set_opacity(0.42)


def focus_cohort(dots: VGroup, pull: int, mode: str) -> None:
    before, first_gold, _, _ = cohort_expected_counts(pull)
    prior_tokens = int(round((10_000.0 - before) / 10.0))
    current_tokens = max(1, int(round(first_gold / 10.0)))
    current_end = min(len(dots), prior_tokens + current_tokens)
    for index, dot in enumerate(dots):
        if mode == "conditional":
            if index < prior_tokens:
                dot.set_color(DIM_GOLD).set_opacity(0.10)
            elif index < current_end:
                dot.set_color(GOLD).set_opacity(1.0)
            else:
                dot.set_color(BLUE).set_opacity(0.92)
        elif mode == "pmf":
            if index < current_end and index >= prior_tokens:
                dot.set_color(GOLD).set_opacity(1.0)
            else:
                dot.set_color(MUTED).set_opacity(0.20)
        elif mode == "cdf":
            if index < current_end:
                dot.set_color(GOLD if index >= prior_tokens else DIM_GOLD).set_opacity(0.92)
            else:
                dot.set_color(BLUE).set_opacity(0.12)


def cohort_legend() -> VGroup:
    items = []
    for label, color, opacity in (
        ("此前已出金", DIM_GOLD, 0.55),
        ("本抽首次出金", GOLD, 1.0),
        ("仍在等待", BLUE, 0.95),
    ):
        dot = Dot(radius=0.055, color=color, fill_opacity=opacity)
        items.append(VGroup(dot, cn(label, 0.24, color)).arrange(RIGHT, buff=0.10))
    return VGroup(*items).arrange(RIGHT, buff=0.34)


def live_cohort_metrics() -> tuple[VGroup, dict[str, DecimalNumber | Integer]]:
    pull_number = Integer(0, color=INK).scale(0.80)
    first_gold = DecimalNumber(0, num_decimal_places=1, group_with_commas=True, color=GOLD).scale(0.60)
    waiting = DecimalNumber(10_000, num_decimal_places=1, group_with_commas=True, color=BLUE).scale(0.60)
    cumulative = DecimalNumber(0, num_decimal_places=1, group_with_commas=True, color=MINT).scale(0.60)
    rows = VGroup(
        VGroup(cn("当前抽数", 0.29, MUTED), pull_number).arrange(RIGHT, buff=0.24),
        VGroup(cn("本抽首次出金", 0.29, GOLD), first_gold).arrange(RIGHT, buff=0.24),
        VGroup(cn("仍在等待", 0.29, BLUE), waiting).arrange(RIGHT, buff=0.24),
        VGroup(cn("累计已出金", 0.29, MINT), cumulative).arrange(RIGHT, buff=0.24),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.34)
    fit_inside(rows, 3.55, 2.85)
    return rows, {
        "pull": pull_number,
        "first": first_gold,
        "waiting": waiting,
        "cumulative": cumulative,
    }


def attach_metric_updaters(numbers: dict[str, DecimalNumber | Integer], tracker: ValueTracker) -> None:
    numbers["pull"].add_updater(lambda mob: mob.set_value(int(round(tracker.get_value()))))

    def update_first(mob: DecimalNumber) -> None:
        pull = int(round(tracker.get_value()))
        mob.set_value(cohort_expected_counts(pull)[1])

    def update_waiting(mob: DecimalNumber) -> None:
        pull = int(round(tracker.get_value()))
        mob.set_value(cohort_expected_counts(pull)[2])

    def update_cumulative(mob: DecimalNumber) -> None:
        pull = int(round(tracker.get_value()))
        mob.set_value(cohort_expected_counts(pull)[3])

    numbers["first"].add_updater(update_first)
    numbers["waiting"].add_updater(update_waiting)
    numbers["cumulative"].add_updater(update_cumulative)


def teaching_wait_distribution() -> np.ndarray:
    """Use the previously introduced, publicly constrained example B as f(n)."""

    _, pmf, _ = distribution_from_q(ILLUSTRATIVE_Q["B"])
    return pmf


TEACHING_WAIT_PMF = teaching_wait_distribution()


class ThreeNumbersHookV4(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("0.6%、1.6%与90抽，画的是不同层面")
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        visual_box = left_panel(edge="#36516B", fill="#0A1525")
        wish_card = panel(5.10, 3.78, fill="#0B1626", edge=GOLD).move_to(LEFT_CENTER + LEFT * 0.35)
        wish_heading = cn("角色活动祈愿 · 规则摘要", 0.40, GOLD)
        wish_heading.move_to(wish_card.get_top() + DOWN * 0.42)
        star = star_icon(GOLD, 0.52).move_to(wish_card.get_center() + UP * 0.30)
        wish_button = RoundedRectangle(
            width=2.70,
            height=0.72,
            corner_radius=0.22,
            color=BLUE,
            fill_color=BLUE,
            fill_opacity=0.12,
        ).move_to(wish_card.get_center() + DOWN * 1.08)
        wish_button_text = cn("祈愿一次", 0.36, BLUE).move_to(wish_button)
        scope_note = cn("先判断何时出五星，再判断是否为当期UP", 0.31, MUTED)
        scope_note.next_to(wish_card, DOWN, buff=0.25)
        self.play(FadeIn(visual_box), FadeIn(wish_card), FadeIn(wish_heading), run_time=1.0)
        self.play(GrowFromCenter(star), FadeIn(wish_button), FadeIn(wish_button_text), run_time=1.0)
        hold_to(self, 5.5)

        info_box = right_panel(edge="#36516B", fill="#0A1525")

        def metric_tile(label: str, value: str, color: str, center: np.ndarray) -> VGroup:
            box = panel(1.88, 1.68, fill="#0B1626", edge=color).move_to(center)
            label_mob = cn(label, 0.26, MUTED)
            value_mob = MathTex(value, color=color).scale(0.75)
            stack = VGroup(label_mob, value_mob).arrange(DOWN, buff=0.18).move_to(box)
            fit_inside(stack, 1.58, 1.30)
            return VGroup(box, stack)

        metric_centers = (
            RIGHT_CENTER + LEFT * 1.02 + UP * 1.14,
            RIGHT_CENTER + RIGHT * 1.02 + UP * 1.14,
            RIGHT_CENTER + LEFT * 1.02 + DOWN * 0.84,
        )
        metrics = VGroup(
            metric_tile("五星基础概率", r"0.6\%", BLUE, metric_centers[0]),
            metric_tile("含保底综合概率", r"1.6\%", MINT, metric_centers[1]),
            metric_tile("五星等待上限", r"90", GOLD, metric_centers[2]),
        )
        question_tile = panel(1.88, 1.68, fill="#171329", edge=VIOLET).move_to(
            RIGHT_CENTER + RIGHT * 1.02 + DOWN * 0.84
        )
        question_text = VGroup(
            cn("放进同一批玩家", 0.27, MUTED),
            cn("就能看出差别", 0.36, VIOLET),
        ).arrange(DOWN, buff=0.16).move_to(question_tile)
        self.play(FadeIn(info_box), FadeIn(metrics[0]), FadeIn(metrics[1]), run_time=1.2)
        hold_to(self, 8.7)
        self.play(FadeIn(metrics[2]), run_time=0.8)
        hold_to(self, 12.7)
        self.play(FadeIn(question_tile), FadeIn(question_text), FadeIn(scope_note), run_time=1.0)
        hold_to(self, 15.7)

        three_questions = VGroup(
            pill("这一抽", BLUE, 1.28),
            pill("首金分布", GOLD, 1.58),
            pill("累计出金率", MINT, 1.86),
        ).arrange(RIGHT, buff=0.26)
        three_questions.move_to(LEFT_CENTER + DOWN * 2.14)
        # Peak occupancy: left wish card plus three question labels; right 2x2 metric grid.
        self.play(
            FadeOut(scope_note),
            FadeIn(three_questions, shift=UP * 0.08),
            run_time=1.0,
        )
        self.play(
            Indicate(metrics[0], color=BLUE),
            Indicate(metrics[1], color=MINT),
            Indicate(metrics[2], color=GOLD),
            run_time=1.5,
        )
        finish_to(self, TARGET_DURATIONS_V4["ThreeNumbersHookV4"])


class CohortAfterEachPullV4(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("1万人一起抽：每一抽都会重新分流", "固定0.6%、没有保底的教学对照")
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        visual_box = left_panel(edge="#36516B", fill="#0A1525")
        info_box = right_panel(edge=BLUE, fill="#0A1525")
        visual_heading = cn("只统计第一次出金", 0.35, INK)
        visual_heading.move_to(visual_box.get_top() + DOWN * 0.35)
        model_tag = pill("每抽独立 · 0.6%", BLUE, 2.28)
        model_tag.move_to(visual_box.get_corner(UR) + LEFT * 1.50 + DOWN * 0.34)
        self.play(
            FadeIn(visual_box),
            FadeIn(visual_heading),
            FadeIn(model_tag),
            run_time=1.1,
        )
        hold_to(self, 4.3)

        grid = cohort_grid(LEFT_CENTER + UP * 0.05, count=1000, columns=40)
        legend = cohort_legend().move_to(LEFT_CENTER + DOWN * 2.08)
        sample_note = cn("1000个点按比例表示1万人", 0.25, MUTED)
        sample_note.next_to(legend, DOWN, buff=0.14)
        self.play(FadeIn(grid), FadeIn(legend), FadeIn(sample_note), run_time=1.4)
        hold_to(self, 10.4)

        metrics, numbers = live_cohort_metrics()
        metrics.move_to(RIGHT_CENTER + UP * 0.26)
        expected_note = pill("人数为期望值", VIOLET, 1.92).move_to(RIGHT_CENTER + UP * 1.90)
        formula = VGroup(
            cn("本抽首次出金", 0.25, GOLD),
            MathTex(r"=", color=MUTED).scale(0.46),
            cn("抽前仍在等待", 0.25, BLUE),
            MathTex(r"\times0.6\%", color=INK).scale(0.46),
        ).arrange(RIGHT, buff=0.10)
        formula.move_to(RIGHT_CENTER + DOWN * 1.88)
        fit_inside(formula, 3.72, 0.55)
        tracker = ValueTracker(0)
        attach_metric_updaters(numbers, tracker)
        last_pull = {"value": None}

        def update_grid(mob: VGroup) -> None:
            pull = int(round(tracker.get_value()))
            if pull != last_pull["value"]:
                apply_cohort_state(mob, pull)
                last_pull["value"] = pull

        grid.add_updater(update_grid)
        self.play(
            FadeIn(info_box),
            FadeIn(metrics),
            FadeIn(expected_note),
            FadeIn(formula),
            run_time=1.0,
        )
        hold_to(self, 19.4)

        self.play(tracker.animate.set_value(1), run_time=1.4, rate_func=linear)
        self.play(Flash(grid[0:6], color=GOLD, flash_radius=0.32, line_length=0.08), run_time=0.7)
        hold_to(self, 24.0)
        self.play(tracker.animate.set_value(2), run_time=1.2, rate_func=linear)
        hold_to(self, 27.3)

        self.play(tracker.animate.set_value(50), run_time=3.6, rate_func=linear)
        self.wait(0.8)
        self.play(tracker.animate.set_value(90), run_time=3.0, rate_func=linear)
        hold_to(self, 35.25)

        conclusion = cn("固定0.6%时，90抽后仍约有5818人没出过五星", 0.31, GOLD)
        fit_inside(conclusion, 3.66, 0.62)
        conclusion.move_to(formula)
        # Peak occupancy: 1000-dot cohort at pull 90 plus four live expected-count rows.
        self.play(ReplacementTransform(formula, conclusion), run_time=0.9)
        self.play(Indicate(numbers["waiting"], color=BLUE), run_time=1.0)
        finish_to(self, TARGET_DURATIONS_V4["CohortAfterEachPullV4"])


class PullFiftyThreeViewsV4(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("第50抽：分母一换，比例就变", "同一批玩家的三种统计口径")
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        visual_box = left_panel(edge="#36516B", fill="#0A1525")
        info_box = right_panel(edge=VIOLET, fill="#0A1525")
        visual_heading = cn("第50抽时的1万人", 0.36, INK)
        visual_heading.move_to(visual_box.get_top() + DOWN * 0.35)
        grid = cohort_grid(LEFT_CENTER + UP * 0.02, count=1000, columns=40)
        apply_cohort_state(grid, 50)
        legend = cohort_legend().move_to(LEFT_CENTER + DOWN * 2.08)
        self.play(
            FadeIn(visual_box),
            FadeIn(info_box),
            FadeIn(visual_heading),
            FadeIn(grid),
            FadeIn(legend),
            run_time=1.4,
        )
        hold_to(self, 8.1)

        conditional = info_state(
            "条件概率 q(50)",
            [
                ("分母：第50抽前仍未出金", BLUE),
                ("约44.68人 ÷ 约7446人", INK),
                ("等待者中的本抽比例", MUTED),
            ],
            accent=BLUE,
            formula=r"44.68/7446\approx0.6\%",
        )
        q_target = grid.copy()
        focus_cohort(q_target, 50, "conditional")
        self.play(Transform(grid, q_target), FadeIn(conditional), run_time=1.2)
        hold_to(self, 14.2)

        pmf_state = info_state(
            "PMF f(50)｜首金分布",
            [
                ("分母：最初的1万人", GOLD),
                ("约44.68人在这一抽首次出金", INK),
                ("最初人群中的首金位置", MUTED),
            ],
            accent=GOLD,
            formula=r"44.68/10000\approx0.447\%",
        )
        pmf_target = grid.copy()
        focus_cohort(pmf_target, 50, "pmf")
        self.play(Transform(grid, pmf_target), ReplacementTransform(conditional, pmf_state), run_time=1.2)
        hold_to(self, 22.4)

        cdf_state = info_state(
            "CDF F(50)｜累计出金率",
            [
                ("分母：最初的1万人", MINT),
                ("前50抽约2599人已经出金", INK),
                ("最初人群中的累计比例", MUTED),
            ],
            accent=MINT,
            formula=r"2599/10000\approx25.99\%",
        )
        cdf_target = grid.copy()
        focus_cohort(cdf_target, 50, "cdf")
        self.play(Transform(grid, cdf_target), ReplacementTransform(pmf_state, cdf_state), run_time=1.2)
        hold_to(self, 31.0)

        summary = info_state(
            "第50抽的三种统计口径",
            [
                ("这一抽：44.68 ÷ 7446 ≈ 0.6%", BLUE),
                ("首金分布：44.68 ÷ 10000 ≈ 0.447%", GOLD),
                ("累计出金率：2599 ÷ 10000 ≈ 25.99%", MINT),
            ],
            accent=VIOLET,
            note="分母不同，数值的含义也不同",
        )
        normal_target = cohort_grid(LEFT_CENTER + UP * 0.02, count=1000, columns=40)
        apply_cohort_state(normal_target, 50)
        # Peak occupancy: one full cohort visualization plus a three-row comparison in the right panel.
        self.play(Transform(grid, normal_target), ReplacementTransform(cdf_state, summary), run_time=1.1)
        finish_to(self, TARGET_DURATIONS_V4["PullFiftyThreeViewsV4"])


class ConditionalProbabilityCurveFullV4(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("条件概率：只看仍在等待的人", "从零垫开始，研究第一次出五星要等多少抽")
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        shell, axes, _ = full_chart_shell(
            "条件概率 q(n)｜这一抽",
            BLUE,
            y_max=0.0072,
            y_ticks=(0.0, 0.003, 0.006),
        )
        info_box = right_panel(edge=BLUE, fill="#0A1525")
        definition = info_state(
            "条件概率 q(n)",
            [
                ("只看前面一直没出金的人", BLUE),
                ("这一抽出金的比例", INK),
            ],
            accent=BLUE,
            formula=r"q(n)=P(T=n\mid T\ge n)",
            note="分母会变，但条件概率可以不变",
        )
        self.play(FadeIn(shell), FadeIn(info_box), FadeIn(definition), run_time=1.2)
        hold_to(self, 6.0)

        q_path = trend_path(axes, Q_FIXED, BLUE, stroke_width=4.2)
        q_dots = sampled_dots(axes, Q_FIXED, BLUE, every=10, radius=0.035)
        self.play(Create(q_path), FadeIn(q_dots), run_time=1.8)
        hold_to(self, 10.0)

        tracker = ValueTracker(1)
        scanner = always_redraw(lambda: vertical_scanner(axes, tracker.get_value()))
        self.add(scanner)
        self.play(tracker.animate.set_value(50), run_time=2.2, rate_func=linear)
        at_fifty = info_state(
            "固定0.6%的对照模型",
            [
                ("第1抽：0.6%", BLUE),
                ("第50抽：0.6%", BLUE),
                ("第90抽：0.6%", BLUE),
            ],
            accent=BLUE,
            note="等待人数减少，线仍保持水平",
        )
        self.play(ReplacementTransform(definition, at_fifty), run_time=0.8)
        self.play(tracker.animate.set_value(90), run_time=2.2, rate_func=linear)
        hold_to(self, 17.6)
        # Peak occupancy: one full-height q chart, its scanner, and three fixed-rate checks on the right.
        self.play(Indicate(q_path, color=BLUE, scale_factor=1.01), run_time=1.2)
        finish_to(self, TARGET_DURATIONS_V4["ConditionalProbabilityCurveFullV4"])


class FirstGoldPmfCurveFullV4(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("首金分布：第一次出金落在哪一抽")
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        shell, axes, _ = full_chart_shell(
            "PMF f(n)｜首金分布",
            GOLD,
            y_max=0.0065,
            y_ticks=(0.0, 0.003, 0.006),
        )
        info_box = right_panel(edge=GOLD, fill="#0A1525")
        definition = info_state(
            "概率质量函数 PMF",
            [
                ("简称：首金分布", GOLD),
                ("表示首金落在每个抽数的概率", INK),
            ],
            accent=GOLD,
            note="抽数是整数，所以用一根根柱表示",
        )
        self.play(FadeIn(shell), FadeIn(info_box), FadeIn(definition), run_time=1.2)
        hold_to(self, 8.3)

        formula_state = info_state(
            "要在第 n 抽首次出金",
            [
                ("前 n-1 抽都没有出金", MUTED),
                ("第 n 抽再出金", BLUE),
            ],
            accent=GOLD,
            formula=r"f(n)=0.994^{n-1}\times0.006",
        )
        self.play(ReplacementTransform(definition, formula_state), run_time=0.9)
        hold_to(self, 16.8)

        stems = stem_plot(axes, F_FIXED_PMF, GOLD, stroke_width=3.2, opacity=0.92)
        self.play(
            LaggedStart(*[GrowFromEdge(stem, DOWN) for stem in stems], lag_ratio=0.004),
            run_time=2.6,
        )
        hold_to(self, 22.8)

        bar_50 = Line(axes.c2p(50, 0), axes.c2p(50, F_FIXED_PMF[49]), color=PINK, stroke_width=7.0)
        bar_90 = Line(axes.c2p(90, 0), axes.c2p(90, F_FIXED_PMF[89]), color=MINT, stroke_width=7.0)
        values_state = info_state(
            "等待的人越少，柱子越低",
            [
                ("第1抽：0.600%", GOLD),
                ("第50抽：约0.447%", PINK),
                ("第90抽：约0.351%", MINT),
            ],
            accent=GOLD,
            note="不是这一抽更难，而是走到这里的人更少",
        )
        self.play(
            FadeIn(bar_50),
            FadeIn(bar_90),
            ReplacementTransform(formula_state, values_state),
            run_time=1.2,
        )
        # Peak occupancy: 90 discrete PMF stems, two highlighted pulls, and the three-value summary.
        self.play(Indicate(bar_50, color=PINK), Indicate(bar_90, color=MINT), run_time=1.4)
        finish_to(self, TARGET_DURATIONS_V4["FirstGoldPmfCurveFullV4"])


class CumulativeCdfCurveFullV4(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("累计出金率：到这里已有多少人出金")
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        shell, axes, _ = full_chart_shell(
            "CDF F(n)｜累计出金率",
            MINT,
            y_max=0.45,
            y_ticks=(0.0, 0.20, 0.40),
            y_decimals=0,
        )
        info_box = right_panel(edge=MINT, fill="#0A1525")
        definition = info_state(
            "累积分布函数 CDF",
            [
                ("简称：累计出金率", MINT),
                ("表示到第 n 抽时已经出金的比例", INK),
            ],
            accent=MINT,
            note="分母始终是最初的全部玩家",
        )
        self.play(FadeIn(shell), FadeIn(info_box), FadeIn(definition), run_time=1.2)
        hold_to(self, 8.5)

        cdf_path = trend_path(axes, F_FIXED_CDF, MINT, stroke_width=4.0)
        cdf_dots = sampled_dots(axes, F_FIXED_CDF, MINT, every=10, radius=0.035)
        area_points = [axes.c2p(index + 1, value) for index, value in enumerate(F_FIXED_CDF)]
        area = Polygon(
            axes.c2p(1, 0),
            *area_points,
            axes.c2p(90, 0),
            stroke_opacity=0,
            fill_color=MINT,
            fill_opacity=0.10,
        )
        self.play(FadeIn(area), Create(cdf_path), FadeIn(cdf_dots), run_time=2.2)
        hold_to(self, 14.6)

        formula_state = info_state(
            "两种等价的算法",
            [
                ("合并第1抽到第 n 抽的首金人数", GOLD),
                ("或用100%减去仍未出金的人", BLUE),
            ],
            accent=MINT,
            formula=r"F(n)=\sum_{k=1}^{n}f(k)=1-0.994^n",
        )
        self.play(ReplacementTransform(definition, formula_state), run_time=0.9)
        hold_to(self, 20.8)

        marker_50 = Dot(axes.c2p(50, F_FIXED_CDF[49]), radius=0.075, color=GOLD)
        marker_90 = Dot(axes.c2p(90, F_FIXED_CDF[89]), radius=0.075, color=PINK)
        values_state = info_state(
            "固定0.6%的对照结果",
            [
                ("前50抽：约25.99%", GOLD),
                ("前90抽：约41.82%", PINK),
                ("仍未出金：约58.18%", BLUE),
            ],
            accent=MINT,
        )
        # Peak occupancy: full CDF with filled cumulative area, two checkpoints, and a three-row result state.
        self.play(
            FadeIn(marker_50, scale=1.5),
            FadeIn(marker_90, scale=1.5),
            ReplacementTransform(formula_state, values_state),
            run_time=1.1,
        )
        self.play(Indicate(marker_50, color=GOLD), Indicate(marker_90, color=PINK), run_time=1.3)
        finish_to(self, TARGET_DURATIONS_V4["CumulativeCdfCurveFullV4"])


class CompactCurveRelationshipV4(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("同一批玩家，对应三张概率图")
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        centers = (
            np.array([-4.60, 0.92, 0.0]),
            np.array([-0.44, 0.92, 0.0]),
            np.array([-4.60, -1.56, 0.0]),
            np.array([-0.44, -1.56, 0.0]),
        )
        q_shell, q_axes, _ = compact_chart_shell(
            centers[0], "条件概率 q(n)｜这一抽", BLUE, y_max=0.0072, top_label=r"0.6\%"
        )
        f_shell, f_axes, _ = compact_chart_shell(
            centers[1], "PMF f(n)｜首金分布", GOLD, y_max=0.0065, top_label=r"0.6\%"
        )
        cdf_shell, cdf_axes, _ = compact_chart_shell(
            centers[2], "CDF F(n)｜累计出金率", MINT, y_max=0.45, top_label=r"45\%"
        )
        discrete_card = compact_text_card(
            centers[3],
            "抽数只能取整数",
            ["PMF用一根根柱表示", "连线只用来看变化趋势", "不存在第50.5抽"],
            VIOLET,
        )
        info_box = right_panel(edge=VIOLET, fill="#0A1525")
        self.play(FadeIn(q_shell), FadeIn(info_box), run_time=1.0)
        hold_to(self, 4.5)

        q_path = trend_path(q_axes, Q_FIXED, BLUE, stroke_width=3.2)
        f_stems = stem_plot(f_axes, F_FIXED_PMF, GOLD, stroke_width=2.2, opacity=0.88)
        cdf_path = trend_path(cdf_axes, F_FIXED_CDF, MINT, stroke_width=3.2)
        state_q = info_state(
            "同一批玩家，三个视角",
            [("q(n)：决定这一抽出金多少人", BLUE)],
            accent=BLUE,
        )
        self.play(Create(q_path), FadeIn(state_q), run_time=1.3)
        hold_to(self, 8.0)
        self.play(FadeIn(f_shell), FadeIn(f_stems), run_time=1.4)
        state_f = info_state(
            "同一批玩家，三个视角",
            [
                ("q(n)：等待者中本抽出金的比例", BLUE),
                ("PMF：记录首金落在哪一抽", GOLD),
            ],
            accent=GOLD,
        )
        self.play(ReplacementTransform(state_q, state_f), run_time=0.7)
        hold_to(self, 12.0)
        self.play(FadeIn(cdf_shell), Create(cdf_path), run_time=1.4)
        state_all = info_state(
            "同一批玩家，三个视角",
            [
                ("q(n)：等待者中本抽出金的比例", BLUE),
                ("PMF：记录首金落在哪一抽", GOLD),
                ("CDF：记录目前共有多少人出金", MINT),
            ],
            accent=VIOLET,
            formula=r"q(n)\Longrightarrow f(n)\Longrightarrow F(n)",
        )
        self.play(ReplacementTransform(state_f, state_all), run_time=0.8)
        hold_to(self, 19.7)

        self.play(FadeIn(discrete_card), run_time=0.9)
        tracker = ValueTracker(1)
        scanners = VGroup(
            always_redraw(lambda: vertical_scanner(q_axes, tracker.get_value(), PINK)),
            always_redraw(lambda: vertical_scanner(f_axes, tracker.get_value(), PINK)),
            always_redraw(lambda: vertical_scanner(cdf_axes, tracker.get_value(), PINK)),
        )
        self.add(scanners)
        self.play(tracker.animate.set_value(50), run_time=2.2, rate_func=linear)
        self.play(tracker.animate.set_value(90), run_time=2.2, rate_func=linear)
        # Peak occupancy: left 2x2 recap dashboard and one compact relationship state on the right.
        self.play(Indicate(discrete_card, color=VIOLET), run_time=1.0)
        finish_to(self, TARGET_DURATIONS_V4["CompactCurveRelationshipV4"])


class HardPityCurveDashboardV4(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("90抽硬保底会重画整段等待分布")
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        centers = (
            np.array([-4.60, 0.92, 0.0]),
            np.array([-0.44, 0.92, 0.0]),
            np.array([-4.60, -1.56, 0.0]),
            np.array([-0.44, -1.56, 0.0]),
        )
        q_shell, q_axes, _ = compact_chart_shell(
            centers[0], "条件概率 q(n)｜这一抽", BLUE, y_max=1.02, top_label=r"100\%"
        )
        f_shell, f_axes, _ = compact_chart_shell(
            centers[1], "PMF f(n)｜首金分布", GOLD, y_max=0.62, top_label=r"60\%"
        )
        cdf_shell, cdf_axes, _ = compact_chart_shell(
            centers[2], "CDF F(n)｜累计出金率", MINT, y_max=1.02, top_label=r"100\%"
        )
        cohort_box = panel(3.95, 2.34, fill=PANEL, edge=PANEL_EDGE).move_to(centers[3])
        cohort_title = cn("1万人中的状态", 0.26, VIOLET)
        cohort_title.move_to(cohort_box.get_top() + DOWN * 0.28)
        cohort_dots = VGroup()
        for index in range(100):
            col = index % 20
            row = index // 20
            point = centers[3] + LEFT * 0.56 + RIGHT * (col - 9.5) * 0.128
            point += UP * (2 - row) * 0.16 + DOWN * 0.12
            color = DIM_GOLD if index < 41 else BLUE
            opacity = 0.48 if index < 41 else 0.94
            cohort_dots.add(Dot(point, radius=0.032, color=color, fill_opacity=opacity))
        cohort_value_89 = cn("第89抽后：约5853人仍在等待", 0.23, BLUE)
        cohort_value_89.move_to(cohort_box.get_bottom() + UP * 0.30)
        cohort_shell = VGroup(cohort_box, cohort_title, cohort_dots, cohort_value_89)

        info_box = right_panel(edge=RED, fill="#0A1525")
        rule_state = info_state(
            "只观察硬保底的作用",
            [
                ("第1–89抽：0.6%", BLUE),
                ("第90抽：100%", GOLD),
            ],
            accent=RED,
            formula=r"q_{1}=\cdots=q_{89}=0.006,\quad q_{90}=1",
            note="教学比较模型，不代表官方逐抽概率",
        )
        self.play(
            FadeIn(q_shell),
            FadeIn(f_shell),
            FadeIn(cdf_shell),
            FadeIn(cohort_shell),
            FadeIn(info_box),
            FadeIn(rule_state),
            run_time=1.4,
        )
        hold_to(self, 8.1)

        fixed_q = trend_path(q_axes, Q_FIXED, GRAY, stroke_width=2.0, opacity=0.65)
        fixed_pmf = stem_plot(f_axes, F_FIXED_PMF, GRAY, stroke_width=1.7, opacity=0.48)
        fixed_cdf = trend_path(cdf_axes, F_FIXED_CDF, GRAY, stroke_width=2.0, opacity=0.65)
        self.play(Create(fixed_q), FadeIn(fixed_pmf), Create(fixed_cdf), run_time=1.8)
        hold_to(self, 13.2)

        hard_q = trend_path(q_axes, Q_HARD_ONLY, BLUE, stroke_width=3.2)
        hard_pmf = stem_plot(f_axes, F_HARD_PMF[:89], BLUE, stroke_width=1.9, opacity=0.58)
        last_stem = Line(
            f_axes.c2p(90, 0), f_axes.c2p(90, F_HARD_PMF[89]), color=GOLD, stroke_width=7.0
        )
        hard_cdf = trend_path(cdf_axes, F_HARD_CDF, MINT, stroke_width=3.2)
        q90 = Dot(q_axes.c2p(90, 1), radius=0.055, color=GOLD)
        self.play(Create(hard_q), FadeIn(q90), run_time=1.4)
        hold_to(self, 18.2)

        mass_state = info_state(
            "第90抽前仍在等待",
            [
                ("约5853人全部在第90抽出金", GOLD),
                ("首金分布出现一根高柱", INK),
            ],
            accent=GOLD,
            formula=r"f(90)=0.994^{89}\approx58.53\%",
        )
        target_dots = cohort_dots.copy()
        for index, dot in enumerate(target_dots):
            if index < 41:
                dot.set_color(DIM_GOLD).set_opacity(0.48)
            else:
                dot.set_color(GOLD).set_opacity(0.96)
        cohort_value_90 = cn(
            "此前约4147人｜第90抽约5853人｜剩余0人", 0.20, GOLD
        ).move_to(cohort_value_89)
        fit_inside(cohort_value_90, 3.45, 0.42)
        self.play(
            FadeIn(hard_pmf),
            GrowFromEdge(last_stem, DOWN),
            Transform(cohort_dots, target_dots),
            ReplacementTransform(cohort_value_89, cohort_value_90),
            ReplacementTransform(rule_state, mass_state),
            run_time=1.8,
        )
        hold_to(self, 25.2)

        result_state = info_state(
            "硬保底改变整段等待分布",
            [
                ("q(90)：100%", BLUE),
                ("PMF第90抽：58.53%", GOLD),
                ("CDF：41.47% → 100%", MINT),
                ("仍在等待：5853人 → 0人", VIOLET),
            ],
            accent=GOLD,
        )
        # Peak occupancy: left 2x2 dashboard at pull 90 and four synchronized results on the right.
        self.play(Create(hard_cdf), ReplacementTransform(mass_state, result_state), run_time=1.5)
        self.play(
            Indicate(q90, color=GOLD),
            Indicate(last_stem, color=GOLD),
            Indicate(hard_cdf, color=MINT),
            run_time=1.6,
        )
        finish_to(self, TARGET_DURATIONS_V4["HardPityCurveDashboardV4"])


class IntegratedRateVsHardPityV4(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("1.6%意味着平均62.5抽一颗五星", "与仅有硬保底的对照模型比较")
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        visual_box = left_panel(edge="#36516B", fill="#0A1525")
        info_box = right_panel(edge=GOLD, fill="#0A1525")
        heading = cn("共享刻度：平均多少抽出一颗五星", 0.34, INK)
        heading.move_to(visual_box.get_top() + DOWN * 0.40)
        start_x = -5.85
        full_width = 6.55
        scale_max = 75.0

        def interval_row(y: float, label: str, value: float, color: str) -> VGroup:
            baseline = Line([start_x, y, 0], [start_x + full_width, y, 0], color=PANEL_EDGE, stroke_width=4)
            filled = Line(
                [start_x, y, 0],
                [start_x + full_width * value / scale_max, y, 0],
                color=color,
                stroke_width=10,
            )
            label_mob = cn(label, 0.30, color).next_to(baseline, UP, buff=0.18).align_to(baseline, LEFT)
            value_mob = VGroup(
                MathTex(rf"{value:.1f}", color=color).scale(0.68),
                cn("抽", 0.28, color),
            ).arrange(RIGHT, buff=0.08)
            value_mob.next_to(filled.get_end(), RIGHT, buff=0.14)
            return VGroup(baseline, filled, label_mob, value_mob)

        hard_row = interval_row(0.52, "只加硬保底", 69.7, BLUE)
        public_row = interval_row(-1.28, "综合概率1.6%", 62.5, GOLD)
        ticks = VGroup()
        for value in (0, 25, 50, 75):
            x = start_x + full_width * value / scale_max
            tick = Line([x, -2.08, 0], [x, -1.91, 0], color=MUTED, stroke_width=1.4)
            label = cn(str(value), 0.20, MUTED).next_to(tick, DOWN, buff=0.06)
            ticks.add(tick, label)
        self.play(FadeIn(visual_box), FadeIn(info_box), FadeIn(heading), FadeIn(ticks), run_time=1.1)
        hold_to(self, 4.1)

        hard_state = info_state(
            "只加硬保底",
            [
                ("平均五星间隔：约69.7抽", BLUE),
                ("长期五星率：约1.435%", BLUE),
            ],
            accent=BLUE,
            formula=r"1/69.7\approx1.435\%",
        )
        self.play(FadeIn(hard_row), FadeIn(hard_state), run_time=1.2)
        hold_to(self, 11.7)

        public_state = info_state(
            "游戏详情中的综合概率",
            [
                ("综合概率：1.6%", GOLD),
                ("平均五星间隔：62.5抽", GOLD),
            ],
            accent=GOLD,
            formula=r"1/0.016=62.5",
        )
        self.play(FadeIn(public_row), ReplacementTransform(hard_state, public_state), run_time=1.2)
        hold_to(self, 20.8)

        gap_arrow = DoubleArrow(
            [start_x + full_width * 62.5 / scale_max, -0.36, 0],
            [start_x + full_width * 69.7 / scale_max, -0.36, 0],
            color=MINT,
            stroke_width=3.0,
            buff=0,
            max_tip_length_to_length_ratio=0.24,
        )
        deduction = info_state(
            "公开数字能推出",
            [
                ("第90抽前有些位置高于0.6%", MINT),
                ("但推不出从哪一抽开始", RED),
                ("也推不出每抽提高多少", RED),
                ("是否线性增长同样未知", RED),
            ],
            accent=MINT,
        )
        # Peak occupancy: two shared-scale interval bars and a four-line inference boundary.
        self.play(GrowArrow(gap_arrow), ReplacementTransform(public_state, deduction), run_time=1.2)
        self.play(Indicate(hard_row[1], color=BLUE), Indicate(public_row[1], color=GOLD), run_time=1.5)
        finish_to(self, TARGET_DURATIONS_V4["IntegratedRateVsHardPityV4"])


class NonUniquePerPullCurvesV4(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("公开数字不能唯一还原逐抽曲线")
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        visual_box = left_panel(edge="#36516B", fill="#0A1525")
        info_box = right_panel(edge=RED, fill="#0A1525")
        q_heading = cn("条件概率 q(n)｜这一抽", 0.28, BLUE).move_to([-2.52, 1.93, 0])
        cdf_heading = cn("CDF F(n)｜累计出金率", 0.28, MINT).move_to([-2.52, -0.50, 0])
        q_axes = probability_axes(
            x_max=90, y_max=0.30, width=7.20, height=1.55, center=np.array([-2.52, 0.82, 0])
        )
        cdf_axes = probability_axes(
            x_max=90, y_max=1.02, width=7.20, height=1.55, center=np.array([-2.52, -1.61, 0])
        )
        q_ticks = x_tick_labels(q_axes, (1, 50, 90))
        cdf_ticks = x_tick_labels(cdf_axes, (1, 50, 90))
        q_top = MathTex(r"30\%", color=MUTED).scale(0.27).next_to(q_axes.c2p(1, 0.30), LEFT, buff=0.07)
        cdf_top = MathTex(r"100\%", color=MUTED).scale(0.27).next_to(cdf_axes.c2p(1, 1.0), LEFT, buff=0.07)
        common_state = info_state(
            "三种数学示例",
            [
                ("起点都是0.6%", BLUE),
                ("第90抽都是100%", GOLD),
                ("平均间隔都是62.5抽", MINT),
            ],
            accent=RED,
            note="只用于说明不唯一，不是官方逐抽表",
        )
        self.play(
            FadeIn(visual_box),
            FadeIn(info_box),
            FadeIn(q_heading),
            FadeIn(cdf_heading),
            FadeIn(q_axes),
            FadeIn(cdf_axes),
            FadeIn(q_ticks),
            FadeIn(cdf_ticks),
            FadeIn(q_top),
            FadeIn(cdf_top),
            FadeIn(common_state),
            run_time=1.4,
        )
        hold_to(self, 4.0)

        colors = {"A": BLUE, "B": PINK, "C": MINT}
        q_curves = VGroup()
        cdf_curves = VGroup()
        for key in ("A", "B", "C"):
            _, _, cdf_values = distribution_from_q(ILLUSTRATIVE_Q[key])
            q_curve = DashedVMobject(
                trend_path(q_axes, ILLUSTRATIVE_Q[key][:-1], colors[key], stroke_width=3.0),
                num_dashes=44,
                dashed_ratio=0.62,
            )
            cdf_curve = DashedVMobject(
                trend_path(cdf_axes, cdf_values, colors[key], stroke_width=3.0),
                num_dashes=48,
                dashed_ratio=0.62,
            )
            q_curves.add(q_curve)
            cdf_curves.add(cdf_curve)
            self.play(Create(q_curve), Create(cdf_curve), run_time=1.5)
            self.wait(0.5)
        hold_to(self, 12.0)

        q90_marker = Arrow(
            q_axes.c2p(90, 0.255),
            q_axes.c2p(90, 0.30),
            color=GOLD,
            stroke_width=3.0,
            buff=0,
            max_tip_length_to_length_ratio=0.30,
        )
        q90_label = VGroup(
            cn("第90抽跳到100%", 0.22, GOLD),
            cn("超出这张30%局部图", 0.19, MUTED),
        ).arrange(DOWN, aligned_edge=RIGHT, buff=0.06)
        q90_label.next_to(q90_marker, LEFT, buff=0.12).shift(UP * 0.05)
        legend = VGroup(
            VGroup(Line(LEFT * 0.18, RIGHT * 0.18, color=BLUE), cn("A：单点抬升", 0.24, BLUE)).arrange(RIGHT, buff=0.10),
            VGroup(Line(LEFT * 0.18, RIGHT * 0.18, color=PINK), cn("B：后段平台", 0.24, PINK)).arrange(RIGHT, buff=0.10),
            VGroup(Line(LEFT * 0.18, RIGHT * 0.18, color=MINT), cn("C：逐步抬升", 0.24, MINT)).arrange(RIGHT, buff=0.10),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        legend_state = info_state(
            "中途形状明显不同",
            [
                ("A：单点抬升", BLUE),
                ("B：后段平台", PINK),
                ("C：逐步抬升", MINT),
            ],
            accent=VIOLET,
            note="相同平均等待，不代表逐抽概率相同",
        )
        self.play(
            GrowArrow(q90_marker),
            FadeIn(q90_label),
            ReplacementTransform(common_state, legend_state),
            run_time=1.0,
        )
        hold_to(self, 17.7)

        conclusion = info_state(
            "公开数据只能限制曲线",
            [
                ("不能唯一还原逐抽概率", GOLD),
                ("玩家记录可以用来拟合", INK),
                ("社区起点与增幅不是官方公式", RED),
            ],
            accent=GOLD,
        )
        # Peak occupancy: two compact reused charts with three equal-status examples and one right conclusion.
        self.play(ReplacementTransform(legend_state, conclusion), run_time=0.9)
        self.play(Indicate(q_curves, color=GOLD), Indicate(cdf_curves, color=MINT), run_time=1.3)
        finish_to(self, TARGET_DURATIONS_V4["NonUniquePerPullCurvesV4"])


class CommunitySampleDistributionV4(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title(
            "社区上传记录里，五星集中在第77抽附近",
            "Paimon.moe角色活动祈愿聚合｜截至2025-06-09",
        )
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        chart_shell, axes, chart_box = full_chart_shell(
            "社区样本｜五星落点占全部记录的比例",
            MINT,
            y_max=0.11,
            y_ticks=(0.05, 0.10),
            y_decimals=0,
            x_ticks=(1, 50, 73, 77, 90),
        )
        info_box = right_panel(edge=MINT, fill="#0A1525")
        source_state = info_state(
            "Paimon.moe公开聚合",
            [
                ("74期角色活动祈愿", MINT),
                ("22,047,495条五星落点", INK),
                ("样本截止：2025-06-09", MUTED),
            ],
            accent=MINT,
            note="社区上传记录估计｜不是官方逐抽表",
        )
        self.play(FadeIn(chart_shell), FadeIn(info_box), FadeIn(source_state), run_time=1.2)
        hold_to(self, 5.2)

        soft_region = Polygon(
            axes.c2p(73.5, 0),
            axes.c2p(80.5, 0),
            axes.c2p(80.5, 0.11),
            axes.c2p(73.5, 0.11),
            color=PINK,
            stroke_width=1.2,
            fill_color=PINK,
            fill_opacity=0.07,
        )
        bars = stem_plot(axes, COMMUNITY_SAMPLE_PMF, MINT, stroke_width=3.2, opacity=0.92)
        self.play(FadeIn(soft_region), run_time=0.5)
        self.play(
            LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in bars], lag_ratio=0.002),
            run_time=2.8,
        )
        hold_to(self, 27.0)

        peak_pull = int(np.argmax(COMMUNITY_SAMPLE_PMF)) + 1
        peak_value = float(COMMUNITY_SAMPLE_PMF[peak_pull - 1])
        peak_dot = Dot(axes.c2p(peak_pull, peak_value), radius=0.075, color=GOLD)
        peak_label = VGroup(
            cn("第77抽最高", 0.27, GOLD),
            MathTex(r"9.708\%", color=GOLD).scale(0.48),
        ).arrange(DOWN, buff=0.08).next_to(peak_dot, UP, buff=0.12)
        shape_state = info_state(
            "样本里直接看到的形状",
            [
                ("第74抽以后迅速抬升", PINK),
                ("第77抽记录最多", GOLD),
                ("此后很快回落", MINT),
            ],
            accent=GOLD,
            note="柱高是上传五星落点占比，不是单抽条件概率",
        )
        self.play(
            ReplacementTransform(source_state, shape_state),
            FadeIn(peak_dot, scale=1.4),
            FadeIn(peak_label),
            run_time=1.1,
        )
        hold_to(self, 35.0)

        data_state = info_state(
            "换成仍在等待的人，再估计 q(n)",
            [
                ("q(73) ≈ 0.753%", BLUE),
                ("q(74) ≈ 6.746%", PINK),
                ("q(77) ≈ 24.622%", GOLD),
                ("q(80) ≈ 42.440%", MINT),
            ],
            accent=BLUE,
            note="用户上传与历史缺失会带来样本偏差",
        )
        self.play(ReplacementTransform(shape_state, data_state), run_time=0.9)
        q74_marker = Line(
            axes.c2p(74, 0), axes.c2p(74, 0.11), color=PINK, stroke_width=2.0
        ).set_opacity(0.72)
        self.play(Create(q74_marker), Indicate(peak_dot, color=GOLD), run_time=1.1)
        finish_to(self, TARGET_DURATIONS_V4["CommunitySampleDistributionV4"])


class CommunityFitComparisonV4(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title(
            "社区模型：另一批样本得到的逐抽拟合",
            "Paimon上传样本与Cgg模型分开标注",
        )
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        chart_shell, axes, chart_box = full_chart_shell(
            "Paimon样本落点 + Cgg模型首金曲线",
            GOLD,
            y_max=0.11,
            y_ticks=(0.05, 0.10),
            y_decimals=0,
            x_ticks=(1, 50, 73, 77, 90),
        )
        info_box = right_panel(edge=GOLD, fill="#0A1525")
        sample_bars = stem_plot(axes, COMMUNITY_SAMPLE_PMF, MINT, stroke_width=3.0, opacity=0.48)
        sample_tag = pill("Paimon上传样本", MINT, 1.95)
        sample_tag.move_to(chart_box.get_corner(UR) + LEFT * 1.24 + DOWN * 0.38)
        self.play(
            FadeIn(chart_shell),
            FadeIn(info_box),
            FadeIn(sample_bars),
            FadeIn(sample_tag),
            run_time=1.2,
        )

        fit_state = info_state(
            "Cgg社区拟合｜约2500万抽",
            [
                ("第1–73抽：0.6%", BLUE),
                ("第74抽起：每抽约+6个百分点", PINK),
                ("第90抽：100%", GOLD),
            ],
            accent=GOLD,
            formula=r"q_n=\min\{1,\ 0.006+0.06(n-73)_+\}",
            note="genshin-wishes.com样本分析｜2021",
        )
        self.play(FadeIn(fit_state), run_time=0.8)
        hold_to(self, 12.0)

        fit_curve = DashedVMobject(
            trend_path(axes, COMMUNITY_FIT_PMF, GOLD, stroke_width=3.5),
            num_dashes=64,
            dashed_ratio=0.58,
        )
        fit_tag = pill("Cgg模型首金曲线", GOLD, 2.55)
        fit_tag.move_to(chart_box.get_corner(UL) + RIGHT * 1.60 + DOWN * 0.92)
        self.play(Create(fit_curve), FadeIn(fit_tag), run_time=2.3)
        hold_to(self, 21.5)

        link_state = info_state(
            "由条件概率得到模型首金分布",
            [
                ("Cgg模型给出条件概率 q(n)", BLUE),
                ("由 q(n) 算出模型首金分布", GOLD),
                ("第77抽附近同样形成主峰", MINT),
            ],
            accent=VIOLET,
            formula=r"f_n=q_n\prod_{k<n}(1-q_k)",
        )
        self.play(ReplacementTransform(fit_state, link_state), run_time=0.9)
        self.play(Indicate(fit_curve, color=GOLD), Indicate(sample_bars, color=MINT), run_time=1.3)
        hold_to(self, 29.5)

        caveat_state = info_state(
            "三层信息不能混在一起",
            [
                ("薄荷柱：Paimon上传样本", MINT),
                ("金色虚线：Cgg社区模型", GOLD),
                ("90抽上限：官方规则", BLUE),
                ("逐抽公式：官方未公开", RED),
            ],
            accent=RED,
            note="不完整导入会影响样本均值与前段比例",
        )
        self.play(ReplacementTransform(link_state, caveat_state), run_time=0.9)
        finish_to(self, TARGET_DURATIONS_V4["CommunityFitComparisonV4"])


class FiveStarThenUpIdentityV4(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("五星出现以后，再判断是不是当期UP")
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        visual_box = left_panel(edge=BLUE, fill="#0A1525")
        info_box = right_panel(edge=PINK, fill="#0A1525")
        visual_heading = cn("第一步：什么时候出五星", 0.36, BLUE)
        visual_heading.move_to(visual_box.get_top() + DOWN * 0.38)
        baseline = Line([-5.75, -0.35, 0], [0.45, -0.35, 0], color=PANEL_EDGE, stroke_width=4)
        ticks = VGroup()
        for value, x in ((1, -5.62), (57, -1.15), (90, 0.30)):
            tick = Line([x, -0.55, 0], [x, -0.15, 0], color=BLUE if value == 57 else MUTED, stroke_width=3)
            label = cn(str(value), 0.24, BLUE if value == 57 else MUTED).next_to(tick, DOWN, buff=0.08)
            ticks.add(tick, label)
        counter = VGroup(
            cn("上次五星以后已经抽了", 0.30, MUTED),
            cn("57抽", 0.62, BLUE),
        ).arrange(DOWN, buff=0.16).move_to(LEFT_CENTER + UP * 0.85)
        self.play(
            FadeIn(visual_box),
            FadeIn(info_box),
            FadeIn(visual_heading),
            Create(baseline),
            FadeIn(ticks),
            FadeIn(counter),
            run_time=1.3,
        )
        hold_to(self, 3.5)

        five_star = result_card(
            "五星出现", GOLD, "五星计数归零", 2.20, show_halo=False
        ).scale(0.78)
        five_star.move_to(LEFT_CENTER + DOWN * 1.10)
        identity_heading = cn("第二步：这次五星是不是当期UP", 0.35, PINK)
        identity_heading.move_to(info_box.get_top() + DOWN * 0.40)
        normal_state = pill("小保底｜当期UP基础概率50%", MUTED, 3.46).move_to(
            RIGHT_CENTER + UP * 1.20
        )
        self.play(
            FadeIn(five_star, shift=UP * 0.12),
            FadeIn(identity_heading),
            FadeIn(normal_state),
            run_time=1.0,
        )
        hold_to(self, 6.7)

        fork = Dot(RIGHT_CENTER + LEFT * 1.22 + UP * 0.08, radius=0.075, color=GOLD)
        up = result_card(
            "当期UP", PINK, "基础概率50%", 1.72, show_halo=False
        ).scale(0.58)
        up.move_to(RIGHT_CENTER + RIGHT * 0.92 + UP * 0.18)
        off = result_card(
            "常驻五星", GRAY, "小保底歪了", 1.72, show_halo=False
        ).scale(0.58)
        off.move_to(RIGHT_CENTER + RIGHT * 0.92 + DOWN * 1.32)
        up_arrow = flow_arrow(fork.get_center(), up.get_left(), PINK, 3.8)
        off_arrow = flow_arrow(fork.get_center(), off.get_left(), GRAY, 3.8)
        self.play(
            FadeIn(fork),
            GrowArrow(up_arrow),
            GrowArrow(off_arrow),
            FadeIn(up),
            FadeIn(off),
            run_time=1.4,
        )
        hold_to(self, 13.2)

        guarantee = pill("大保底｜下一颗五星必为当期UP", GOLD, 3.80)
        guarantee.move_to(RIGHT_CENTER + DOWN * 2.30)
        state_note = VGroup(
            pill("记录1：五星计数", BLUE, 2.06),
            pill("当前：小保底 / 大保底", GOLD, 2.75),
        ).arrange(RIGHT, buff=0.22)
        state_note.move_to(LEFT_CENTER + DOWN * 2.35)
        # Peak occupancy: left pity timeline and two state records; right small-pity outcomes plus guarantee state.
        self.play(FadeIn(guarantee), FadeIn(state_note), run_time=1.1)
        self.play(Indicate(counter, color=BLUE), Indicate(guarantee, color=GOLD), run_time=1.4)
        hold_to(self, 24.25)

        warning = cn("不能把两个步骤简化成固定的单抽UP概率", 0.29, INK)
        fit_inside(warning, 3.75, 0.60)
        warning.move_to(RIGHT_CENTER + DOWN * 2.42)
        self.play(FadeOut(guarantee), FadeIn(warning), run_time=0.8)
        finish_to(self, TARGET_DURATIONS_V4["FiveStarThenUpIdentityV4"])


class UpWaitingTwoPeaksV4(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title(
            "小保底与大保底会形成双峰",
            "社区五星拟合 + 小保底 / 大保底简化模型",
        )
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        visual_box = left_panel(edge="#36516B", fill="#0A1525")
        info_box = right_panel(edge=VIOLET, fill="#0A1525")
        first_component = np.zeros(180)
        first_component[:90] = 0.5 * COMMUNITY_FIT_PMF
        convolution = np.convolve(COMMUNITY_FIT_PMF, COMMUNITY_FIT_PMF)
        second_component = np.zeros(180)
        second_component[1:] = 0.5 * convolution
        mixed = first_component + second_component
        y_max = float(np.max(mixed) * 1.18)
        axes = probability_axes(
            x_max=180,
            y_max=y_max,
            width=7.30,
            height=3.82,
            center=LEFT_CENTER + DOWN * 0.25 + RIGHT * 0.10,
        )
        x_labels = x_tick_labels(axes, (1, 90, 180))
        graph_heading = cn("首次拿到当期UP的等待分布", 0.34, INK)
        graph_heading.move_to(visual_box.get_top() + DOWN * 0.37)
        y_top = MathTex(rf"{y_max * 100:.1f}\%", color=MUTED).scale(0.28)
        y_top.next_to(axes.c2p(1, y_max), LEFT, buff=0.08)
        self.play(
            FadeIn(visual_box),
            FadeIn(info_box),
            FadeIn(graph_heading),
            FadeIn(axes),
            FadeIn(x_labels),
            FadeIn(y_top),
            run_time=1.2,
        )
        hold_to(self, 5.6)

        first_state = info_state(
            "小保底：第一颗五星就是UP",
            [
                ("约占一半玩家", GOLD),
                ("只需要等待一颗五星", INK),
            ],
            accent=GOLD,
            formula=r"\frac12 f(n)",
            note="沿用前文社区拟合，不代表官方逐抽公式",
        )
        first_stems = stem_plot(axes, first_component, GOLD, stroke_width=2.6, opacity=0.92)
        self.play(FadeIn(first_state), run_time=0.8)
        self.play(
            LaggedStart(*[GrowFromEdge(stem, DOWN) for stem in first_stems], lag_ratio=0.003),
            run_time=2.5,
        )
        hold_to(self, 12.5)

        second_state = info_state(
            "小保底歪了：下一颗进入大保底",
            [
                ("再等下一颗保证UP", VIOLET),
                ("总等待 = 前后两段间隔之和", INK),
            ],
            accent=VIOLET,
            formula=r"\frac12(f\ast f)(n)",
            note="总等待时间的分布由离散卷积得到",
        )
        second_stems = stem_plot(axes, second_component, VIOLET, stroke_width=2.6, opacity=0.90)
        self.play(ReplacementTransform(first_state, second_state), run_time=0.9)
        self.play(
            LaggedStart(*[GrowFromEdge(stem, DOWN) for stem in second_stems], lag_ratio=0.002),
            run_time=2.7,
        )
        hold_to(self, 21.2)

        mixed_stems = stem_plot(axes, mixed, MINT, stroke_width=3.0, opacity=0.96)
        mix_state = info_state(
            "小保底的两种结果各占50%",
            [
                ("第一组形成靠前的峰", GOLD),
                ("第二组形成靠后的峰", VIOLET),
            ],
            accent=MINT,
            formula=r"g(n)=\frac12 f(n)+\frac12(f\ast f)(n)",
            note="仅计算小保底与大保底，不是官方公布的UP等待分布",
        )
        self.play(
            first_stems.animate.set_opacity(0.18),
            second_stems.animate.set_opacity(0.18),
            FadeIn(mixed_stems),
            ReplacementTransform(second_state, mix_state),
            run_time=1.8,
        )
        hold_to(self, 31.9)

        first_peak = int(np.argmax(mixed[:100])) + 1
        second_peak = int(np.argmax(mixed[100:])) + 101
        first_dot = Dot(axes.c2p(first_peak, mixed[first_peak - 1]), radius=0.065, color=GOLD)
        second_dot = Dot(axes.c2p(second_peak, mixed[second_peak - 1]), radius=0.065, color=VIOLET)
        first_label = cn("第一颗五星就是UP", 0.24, GOLD).next_to(first_dot, UP, buff=0.12)
        second_label = cn("第二颗五星才是UP", 0.24, VIOLET).next_to(second_dot, UP, buff=0.12)
        # Peak occupancy: one full-height two-peak chart and the final two-path mixture formula on the right.
        self.play(
            FadeIn(first_dot, scale=1.5),
            FadeIn(second_dot, scale=1.5),
            FadeIn(first_label),
            FadeIn(second_label),
            run_time=1.2,
        )
        self.play(Indicate(mixed_stems, color=MINT, scale_factor=1.01), run_time=1.2)
        finish_to(self, TARGET_DURATIONS_V4["UpWaitingTwoPeaksV4"])


class CapturingRadianceBasicsV4(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("捕获明光：小保底阶段的额外判定")
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        visual_box = left_panel(edge=PINK, fill="#0A1525")
        info_box = right_panel(edge=PINK, fill="#0A1525")
        entering = result_card(
            "已经出五星", GOLD, "当前处于小保底", 2.18, show_halo=False
        ).scale(0.78)
        entering.move_to(LEFT_CENTER + LEFT * 2.55)
        decision_box = panel(3.10, 2.60, fill="#171329", edge=PINK).move_to(LEFT_CENTER + RIGHT * 0.15)
        decision_title = cn("五星UP判定", 0.35, INK)
        ordinary = pill("小保底｜当期UP基础概率50%", MUTED, 2.86)
        mechanism = pill("捕获明光参与", PINK, 2.08)
        decision_stack = VGroup(decision_title, ordinary, mechanism).arrange(DOWN, buff=0.20).move_to(decision_box)
        up_result = result_card(
            "当期UP", PINK, None, 1.70, show_halo=False
        ).scale(0.64)
        up_result.move_to(LEFT_CENTER + RIGHT * 3.05 + UP * 0.78)
        off_result = result_card(
            "非UP五星", GRAY, None, 1.70, show_halo=False
        ).scale(0.64)
        off_result.move_to(LEFT_CENTER + RIGHT * 3.05 + DOWN * 0.78)
        enter_arrow = flow_arrow(entering.get_right(), decision_box.get_left(), GOLD, 4.0)
        up_arrow = flow_arrow(decision_box.get_right(), up_result.get_left(), PINK, 4.0)
        off_arrow = flow_arrow(decision_box.get_right(), off_result.get_left(), GRAY, 4.0)
        intro_state = info_state(
            "捕获明光",
            [
                ("从5.0版本开始加入", PINK),
                ("只在小保底阶段参与", INK),
                ("一旦触发，这次五星就是当期UP", GOLD),
            ],
            accent=PINK,
        )
        self.play(FadeIn(visual_box), FadeIn(info_box), FadeIn(entering), run_time=1.1)
        hold_to(self, 3.0)
        # First visible use of the term: the mechanism label and its definition appear together.
        self.play(
            GrowArrow(enter_arrow),
            FadeIn(decision_box),
            FadeIn(decision_stack),
            FadeIn(intro_state),
            run_time=1.2,
        )
        hold_to(self, 7.9)
        self.play(
            GrowArrow(up_arrow),
            GrowArrow(off_arrow),
            FadeIn(up_result),
            FadeIn(off_result),
            run_time=1.1,
        )
        hold_to(self, 10.55)

        facts = VGroup(
            stat_card("基础触发概率", r"0.018\%", PINK, "分母：每一次祈愿", 3.82, 1.62),
            stat_card("计入机制后的UP综合概率", r"55\%", MINT, "分母：已出五星且处于小保底", 3.82, 1.62),
        ).arrange(DOWN, buff=0.24).move_to(RIGHT_CENTER + UP * 0.18)
        fact_note = cn("55%合并不同历史状态，并非固定单抽UP率", 0.27, MUTED)
        fit_inside(fact_note, 3.66, 0.60)
        fact_note.move_to(RIGHT_CENTER + DOWN * 2.02)
        self.play(
            FadeOut(intro_state),
            FadeIn(facts),
            FadeIn(fact_note),
            run_time=0.75,
        )
        hold_to(self, 26.6)
        # Peak occupancy: one left decision tree and two denominator-specific fact cards on the right.
        first_fact_outline = facts[0][0].copy()
        first_fact_outline.set_fill(opacity=0.0)
        first_fact_outline.set_stroke(color=PINK, width=2.5, opacity=0.72)
        second_fact_outline = facts[1][0].copy()
        second_fact_outline.set_fill(opacity=0.0)
        second_fact_outline.set_stroke(color=MINT, width=2.5, opacity=0.72)
        self.play(
            ShowPassingFlash(first_fact_outline, time_width=0.55),
            ShowPassingFlash(second_fact_outline, time_width=0.55),
            run_time=1.5,
        )
        finish_to(self, TARGET_DURATIONS_V4["CapturingRadianceBasicsV4"])


class CapturingRadianceHistoryV4(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("捕获明光还会读取账号历史")
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        visual_box = left_panel(edge=PINK, fill="#0A1525")
        info_box = right_panel(edge=PINK, fill="#0A1525")
        visual_heading = cn("连续3轮完整的“歪到UP”过程", 0.34, INK)
        visual_heading.move_to(visual_box.get_top() + DOWN * 0.38)

        def cycle_card(index: int, center: np.ndarray) -> VGroup:
            box = panel(2.40, 2.28, fill="#0B1626", edge=PANEL_EDGE).move_to(center)
            name = pill(f"第{index}轮", BLUE, 1.10)
            off = VGroup(star_icon(GRAY, 0.13), cn("非UP", 0.24, GRAY)).arrange(RIGHT, buff=0.08)
            arrow = MathTex(r"\longrightarrow", color=GOLD).scale(0.48)
            up = VGroup(star_icon(GOLD, 0.13), cn("保证UP", 0.24, GOLD)).arrange(RIGHT, buff=0.08)
            sequence = VGroup(off, arrow, up).arrange(RIGHT, buff=0.10)
            note = cn("一次完整过程", 0.22, MUTED)
            stack = VGroup(name, sequence, note).arrange(DOWN, buff=0.22).move_to(box)
            fit_inside(stack, 2.08, 1.88)
            return VGroup(box, stack)

        cycle_centers = (
            LEFT_CENTER + LEFT * 2.72 + DOWN * 0.10,
            LEFT_CENTER + DOWN * 0.10,
            LEFT_CENTER + RIGHT * 2.72 + DOWN * 0.10,
        )
        cycles = VGroup(*[cycle_card(index + 1, cycle_centers[index]) for index in range(3)])
        counter_state = info_state(
            "账号历史状态",
            [("已完成：0 / 3轮", MUTED), ("记录的是完整“歪到UP”过程", INK)],
            accent=PINK,
            note="三轮共6颗五星：每轮非UP后再保证UP",
        )
        self.play(FadeIn(visual_box), FadeIn(info_box), FadeIn(visual_heading), FadeIn(counter_state), run_time=1.1)
        hold_to(self, 3.6)

        current_state = counter_state
        for index, cycle in enumerate(cycles):
            next_state = info_state(
                "账号历史状态",
                [
                    (f"已完成：{index + 1} / 3轮", PINK),
                    ("每轮都是非UP → 保证UP", GOLD),
                ],
                accent=PINK,
                note="三轮共6颗五星：每轮非UP后再保证UP",
            )
            self.play(
                FadeIn(cycle, shift=RIGHT * 0.12),
                ReplacementTransform(current_state, next_state),
                run_time=0.65,
            )
            current_state = next_state
            self.wait(0.28)
        hold_to(self, 6.4)

        trigger_state = info_state(
            "历史记录达到3 / 3",
            [
                ("下一次获得五星时", INK),
                ("捕获明光必定触发", PINK),
                ("结果为当期UP", GOLD),
            ],
            accent=PINK,
            note="官方未公开中间阶段的完整概率表",
        )
        next_star_box = panel(4.65, 0.74, fill="#171329", edge=GOLD)
        next_star_box.move_to(LEFT_CENTER + DOWN * 2.18)
        next_star_text = VGroup(
            star_icon(GOLD, 0.15),
            cn("下一颗五星：捕获明光必定触发", 0.29, GOLD),
        ).arrange(RIGHT, buff=0.16).move_to(next_star_box)
        fit_inside(next_star_text, 4.25, 0.54)
        next_star = VGroup(next_star_box, next_star_text)
        # Peak occupancy: three cycle cards on the left and the 3/3 trigger result on the right.
        self.play(
            ReplacementTransform(current_state, trigger_state),
            FadeIn(next_star),
            run_time=0.65,
        )
        hold_to(self, 17.25)

        scope_state = info_state(
            "每个账号的UP曲线可能不同",
            [
                ("不同账号的历史状态不同", VIOLET),
                ("中间阶段概率没有完整公开", RED),
                ("忽略账号状态就无法精确描述", INK),
            ],
            accent=VIOLET,
        )
        self.play(ReplacementTransform(trigger_state, scope_state), run_time=0.9)
        self.play(
            *[Circumscribe(cycle, color=PINK, fade_out=True) for cycle in cycles],
            run_time=1.2,
        )
        finish_to(self, TARGET_DURATIONS_V4["CapturingRadianceHistoryV4"])


class ProbabilityStateConclusionV4(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("一张完整抽卡概率图的三个层次")
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        centers = (
            np.array([-4.60, 0.92, 0.0]),
            np.array([-0.44, 0.92, 0.0]),
            np.array([-4.60, -1.56, 0.0]),
            np.array([-0.44, -1.56, 0.0]),
        )
        q_shell, q_axes, _ = compact_chart_shell(
            centers[0], "条件概率 q(n)｜这一抽", BLUE, y_max=0.0072, top_label=r"0.6\%"
        )
        f_shell, f_axes, _ = compact_chart_shell(
            centers[1], "PMF f(n)｜首金分布", GOLD, y_max=0.0065, top_label=r"0.6\%"
        )
        cdf_shell, cdf_axes, _ = compact_chart_shell(
            centers[2], "CDF F(n)｜累计出金率", MINT, y_max=0.45, top_label=r"45\%"
        )
        numbers_card = compact_text_card(
            centers[3],
            "三个公开数字",
            ["0.6%：五星基础概率", "1.6%：含保底综合概率", "90抽：五星等待上限"],
            VIOLET,
        )
        info_box = right_panel(edge=VIOLET, fill="#0A1525")
        self.play(FadeIn(info_box), FadeIn(q_shell), run_time=1.0)
        hold_to(self, 2.8)

        q_path = trend_path(q_axes, Q_FIXED, BLUE, stroke_width=3.0)
        q_state = info_state(
            "同一批玩家的三张图",
            [("q(n)：前面没出时，这一抽的概率", BLUE)],
            accent=BLUE,
        )
        self.play(Create(q_path), FadeIn(q_state), run_time=1.1)
        hold_to(self, 6.4)

        f_stems = stem_plot(f_axes, F_FIXED_PMF, GOLD, stroke_width=2.2, opacity=0.88)
        f_state = info_state(
            "同一批玩家的三张图",
            [
                ("q(n)：前面没出时，这一抽的概率", BLUE),
                ("PMF：第一次出金落在哪一抽", GOLD),
            ],
            accent=GOLD,
        )
        self.play(FadeIn(f_shell), FadeIn(f_stems), ReplacementTransform(q_state, f_state), run_time=1.2)
        hold_to(self, 10.4)

        cdf_path = trend_path(cdf_axes, F_FIXED_CDF, MINT, stroke_width=3.0)
        all_state = info_state(
            "同一批玩家的三张图",
            [
                ("q(n)：前面没出时，这一抽的概率", BLUE),
                ("PMF：第一次出金落在哪一抽", GOLD),
                ("CDF：到这里共有多少人已经出金", MINT),
            ],
            accent=VIOLET,
        )
        self.play(FadeIn(cdf_shell), Create(cdf_path), ReplacementTransform(f_state, all_state), run_time=1.2)
        hold_to(self, 14.0)

        community_card = compact_text_card(
            centers[3],
            "社区样本估计",
            ["上传记录：观察经验分布", "用途：估计真实曲线形状", "限制：不是官方逐抽概率"],
            MINT,
        )
        community_state = info_state(
            "社区记录能补充什么",
            [
                ("上传样本：估计真实分布形状", MINT),
                ("不能替代官方逐抽概率表", RED),
            ],
            accent=MINT,
        )
        self.play(
            FadeIn(community_card),
            ReplacementTransform(all_state, community_state),
            run_time=1.1,
        )
        hold_to(self, 17.65)

        number_state = info_state(
            "三个数字的作用不同",
            [
                ("0.6%：五星基础概率", BLUE),
                ("1.6%：含保底综合概率", MINT),
                ("90抽：五星等待硬上限", GOLD),
            ],
            accent=VIOLET,
        )
        self.play(
            ReplacementTransform(community_card, numbers_card),
            ReplacementTransform(community_state, number_state),
            run_time=1.1,
        )
        hold_to(self, 27.4)

        state_records = info_state(
            "出了五星，还要看账号状态",
            [
                ("五星计数：已经垫了多少抽", BLUE),
                ("大保底：下一颗是否保证UP", GOLD),
                ("历史记录：捕获明光所需状态", PINK),
            ],
            accent=PINK,
            note="小保底、大保底和捕获明光决定是否为当期UP",
        )
        self.play(ReplacementTransform(number_state, state_records), run_time=1.0)
        hold_to(self, 32.2)

        final_state = info_state(
            "完整读法",
            [
                ("第一层：什么时候出五星", BLUE),
                ("第二层：五星是否为当期UP", PINK),
                ("小保底：当期UP基础概率50%", GOLD),
                ("还要看：大保底 / 捕获明光", INK),
            ],
            accent=GOLD,
            note="条件概率 / PMF / CDF 描述第一层的等待过程",
        )
        # Peak occupancy: the complete left 2x2 recap and the two-layer reading on the right.
        self.play(ReplacementTransform(state_records, final_state), run_time=1.0)
        self.play(
            Indicate(q_shell, color=BLUE),
            Indicate(f_shell, color=GOLD),
            Indicate(cdf_shell, color=MINT),
            run_time=1.4,
        )
        finish_to(self, TARGET_DURATIONS_V4["ProbabilityStateConclusionV4"])
