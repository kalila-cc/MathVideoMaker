from __future__ import annotations

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
    scene_title,
    set_scene_background,
    stat_card,
)


TARGET_DURATIONS_V2 = {
    "ThreeProbabilityCurves": 85.0,
    "HardPityRewritesCurves": 70.0,
    "OfficialNumbersDoNotFixCurve": 70.0,
    "UpWaitingHasTwoHumps": 55.0,
}

BASE_Q = 0.006
PULLS_TO_PITY = 90


def distribution_from_q(q_values: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return survival S_0..S_N, first-hit PMF, and CDF for conditional q_n."""

    q = np.asarray(q_values, dtype=float)
    survival = np.empty(len(q) + 1, dtype=float)
    pmf = np.empty(len(q), dtype=float)
    survival[0] = 1.0
    for index, chance in enumerate(q):
        pmf[index] = survival[index] * chance
        survival[index + 1] = survival[index] * (1.0 - chance)
    cdf = np.cumsum(pmf)
    return survival, pmf, cdf


def expected_wait(q_values: np.ndarray) -> float:
    survival, _, _ = distribution_from_q(q_values)
    return float(np.sum(survival[:-1]))


def calibrated_schedule(weights: np.ndarray, target_wait: float = 62.5) -> np.ndarray:
    """Raise a chosen shape just enough to hit E[T], then put hard pity at 90.

    The weights are mathematical illustration knobs, not a claim about the game.
    """

    weights = np.asarray(weights, dtype=float)
    if weights.shape != (PULLS_TO_PITY - 1,) or float(np.max(weights)) <= 0:
        raise ValueError("weights must be a nonzero length-89 array")

    low = 0.0
    high = (1.0 - BASE_Q) / float(np.max(weights))
    for _ in range(100):
        amplitude = (low + high) / 2.0
        candidate = np.concatenate(
            [np.full(PULLS_TO_PITY - 1, BASE_Q) + amplitude * weights, [1.0]]
        )
        if expected_wait(candidate) > target_wait:
            low = amplitude
        else:
            high = amplitude

    amplitude = (low + high) / 2.0
    result = np.concatenate(
        [np.full(PULLS_TO_PITY - 1, BASE_Q) + amplitude * weights, [1.0]]
    )
    if not np.isclose(expected_wait(result), target_wait, atol=1e-9):
        raise AssertionError("illustrative schedule calibration failed")
    return result


def build_illustrative_solutions() -> dict[str, np.ndarray]:
    pulls = np.arange(1, PULLS_TO_PITY)

    pulse_at_50 = np.zeros(PULLS_TO_PITY - 1)
    pulse_at_50[49] = 1.0

    late_plateau = (pulls >= 74).astype(float)
    mid_ramp = np.maximum(0.0, (pulls - 55) / (89 - 55))

    return {
        "A": calibrated_schedule(pulse_at_50),
        "B": calibrated_schedule(late_plateau),
        "C": calibrated_schedule(mid_ramp),
    }


Q_FIXED = np.full(PULLS_TO_PITY, BASE_Q)
Q_HARD_ONLY = np.concatenate([np.full(PULLS_TO_PITY - 1, BASE_Q), [1.0]])
ILLUSTRATIVE_Q = build_illustrative_solutions()

S_FIXED, F_FIXED_PMF, F_FIXED_CDF = distribution_from_q(Q_FIXED)
S_HARD, F_HARD_PMF, F_HARD_CDF = distribution_from_q(Q_HARD_ONLY)


def probability_axes(
    *,
    x_max: int,
    y_max: float,
    width: float,
    height: float,
    center: np.ndarray,
) -> Axes:
    axes = Axes(
        x_range=[1, x_max, 10 if x_max <= 100 else 20],
        y_range=[0, y_max, y_max / 4],
        x_length=width,
        y_length=height,
        tips=False,
        axis_config={
            "include_ticks": False,
            "stroke_color": MUTED,
            "stroke_width": 1.35,
        },
    )
    axes.move_to(center)
    return axes


def x_tick_labels(axes: Axes, values: tuple[int, ...], color: str = MUTED) -> VGroup:
    labels = VGroup()
    for value in values:
        label = cn(str(value), 0.20, color)
        label.next_to(axes.c2p(value, 0), DOWN, buff=0.07)
        labels.add(label)
    return labels


def trend_path(
    axes: Axes,
    values: np.ndarray,
    color: str,
    *,
    x_start: int = 1,
    stroke_width: float = 3.0,
    opacity: float = 1.0,
) -> VMobject:
    points = [axes.c2p(x_start + index, float(value)) for index, value in enumerate(values)]
    path = VMobject()
    path.set_points_as_corners(points)
    path.set_stroke(color=color, width=stroke_width, opacity=opacity)
    return path


def dashed_trend(
    axes: Axes,
    values: np.ndarray,
    color: str,
    *,
    x_start: int = 1,
    num_dashes: int = 52,
) -> DashedVMobject:
    return DashedVMobject(
        trend_path(axes, values, color, x_start=x_start, stroke_width=3.0),
        num_dashes=num_dashes,
        dashed_ratio=0.62,
    )


def sampled_dots(
    axes: Axes,
    values: np.ndarray,
    color: str,
    *,
    x_start: int = 1,
    every: int = 5,
    radius: float = 0.023,
) -> VGroup:
    dots = VGroup()
    last_index = len(values) - 1
    indices = sorted(set([0, last_index, *range(every - 1, len(values), every)]))
    for index in indices:
        dots.add(Dot(axes.c2p(x_start + index, float(values[index])), radius=radius, color=color))
    return dots


def stem_plot(
    axes: Axes,
    values: np.ndarray,
    color: str,
    *,
    x_start: int = 1,
    stroke_width: float = 3.0,
    opacity: float = 1.0,
) -> VGroup:
    return VGroup(
        *[
            Line(
                axes.c2p(x_start + index, 0),
                axes.c2p(x_start + index, float(value)),
                color=color,
                stroke_width=stroke_width,
                stroke_opacity=opacity,
            )
            for index, value in enumerate(values)
            if float(value) > 1e-12
        ]
    )


def stacked_chart_shell(
    center_y: float,
    title: str,
    color: str,
    y_max: float,
) -> tuple[VGroup, Axes, RoundedRectangle]:
    box = panel(13.25, 1.62, fill=PANEL, edge=PANEL_EDGE).move_to([0, center_y, 0])
    title_mob = cn(title, 0.28, color)
    title_mob.move_to(box.get_corner(UL) + RIGHT * (title_mob.width / 2 + 0.30) + DOWN * 0.24)
    axes = probability_axes(
        x_max=90,
        y_max=y_max,
        width=9.55,
        height=0.82,
        center=np.array([-1.20, center_y - 0.16, 0.0]),
    )
    return VGroup(box, title_mob, axes), axes, box


def formula_block(tex: str, meaning: str, color: str, center: np.ndarray) -> VGroup:
    formula = MathTex(tex, color=color).scale(0.47)
    note = cn(meaning, 0.22, MUTED)
    block = VGroup(formula, note).arrange(DOWN, buff=0.12)
    if block.width > 2.65:
        block.scale_to_fit_width(2.65)
    block.move_to(center)
    return block


def legend_item(label: str, color: str) -> VGroup:
    dash = DashedLine(LEFT * 0.28, RIGHT * 0.28, color=color, stroke_width=3.0, dash_length=0.08)
    text = cn(label, 0.22, color)
    return VGroup(dash, text).arrange(RIGHT, buff=0.12)


def flow_card(title: str, formula_tex: str, color: str, width: float = 2.75) -> VGroup:
    box = panel(width, 0.82, fill="#0B1626", edge=color)
    title_mob = cn(title, 0.25, color)
    formula = MathTex(formula_tex, color=color).scale(0.46)
    contents = VGroup(title_mob, formula).arrange(DOWN, buff=0.08).move_to(box)
    if contents.width > width - 0.34:
        contents.scale_to_fit_width(width - 0.34)
    return VGroup(box, contents)


class ThreeProbabilityCurves(Scene):
    """Conditional q, first-hit PMF, and cumulative CDF on one shared scanner."""

    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title(
            "同一个抽数，要看哪一条概率曲线？",
            "T：从零垫开始，第一次出五星所用的抽数",
        )
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=1.2)
        self.wait(3.8)

        q_shell, q_axes, q_box = stacked_chart_shell(1.64, "条件概率 q(n)｜已经走到第 n 抽的人", BLUE, 0.0072)
        f_shell, f_axes, f_box = stacked_chart_shell(-0.12, "PMF f(n)｜最初所有人中，恰好第 n 抽", GOLD, 0.0063)
        cdf_shell, cdf_axes, cdf_box = stacked_chart_shell(-1.88, "CDF F(n)｜到第 n 抽为止，累计已经出金", MINT, 0.46)

        ticks = x_tick_labels(cdf_axes, (1, 50, 90))
        pull_label = cn("抽数 n", 0.22, MUTED).next_to(cdf_axes, RIGHT, buff=0.08).shift(DOWN * 0.34)
        self.play(
            FadeIn(q_shell),
            FadeIn(f_shell),
            FadeIn(cdf_shell),
            FadeIn(ticks),
            FadeIn(pull_label),
            run_time=1.5,
        )
        self.wait(2.5)

        q_formula = formula_block(
            r"q_n=P(T=n\mid T\ge n)",
            "走到门前，再看这一抽",
            BLUE,
            np.array([5.05, 1.52, 0.0]),
        )
        q_path = trend_path(q_axes, Q_FIXED, BLUE)
        q_dots = sampled_dots(q_axes, Q_FIXED, BLUE)
        self.play(Create(q_path), FadeIn(q_dots), FadeIn(q_formula), run_time=1.8)
        self.wait(4.2)

        f_formula = formula_block(
            r"f_n=q_n\prod_{k<n}(1-q_k)",
            "剩余等待者乘上这一道门",
            GOLD,
            np.array([5.05, -0.24, 0.0]),
        )
        f_stems = stem_plot(f_axes, F_FIXED_PMF, GOLD, stroke_width=3.0)
        self.play(
            LaggedStart(*[GrowFromEdge(stem, DOWN) for stem in f_stems], lag_ratio=0.005),
            FadeIn(f_formula),
            run_time=2.4,
        )
        self.wait(4.6)

        cdf_formula = formula_block(
            r"F_n=\sum_{k\le n}f_k=1-\prod_{k\le n}(1-q_k)",
            "把前面的首次出金逐项累加",
            MINT,
            np.array([5.05, -2.00, 0.0]),
        )
        cdf_path = trend_path(cdf_axes, F_FIXED_CDF, MINT, stroke_width=3.4)
        cdf_dots = sampled_dots(cdf_axes, F_FIXED_CDF, MINT)
        self.play(Create(cdf_path), FadeIn(cdf_dots), FadeIn(cdf_formula), run_time=2.2)
        self.wait(4.8)

        relation_note = pill("q(n) 一旦确定，PMF 和 CDF 也随之确定", VIOLET, width=5.55)
        relation_note.move_to([0, -3.18, 0])
        self.play(FadeIn(relation_note, shift=UP * 0.08), run_time=1.0)
        self.wait(4.0)

        tracker = ValueTracker(1)
        scanner = always_redraw(
            lambda: Line(
                [q_axes.c2p(tracker.get_value(), 0)[0], q_box.get_top()[1] - 0.10, 0],
                [cdf_axes.c2p(tracker.get_value(), 0)[0], cdf_box.get_bottom()[1] + 0.10, 0],
                color=PINK,
                stroke_width=3.0,
            ).set_opacity(0.80)
        )
        self.play(FadeIn(scanner), run_time=0.6)
        self.play(tracker.animate.set_value(50), run_time=4.0, rate_func=linear)
        self.wait(3.4)

        q50 = formula_block(r"q_{50}=0.6\%", "分母：已连续 49 抽未出的人", BLUE, q_formula.get_center())
        f50 = formula_block(r"f_{50}\approx0.447\%", "分母：最初所有人", GOLD, f_formula.get_center())
        cdf50 = formula_block(r"F_{50}\approx25.99\%", "分母：最初所有人", MINT, cdf_formula.get_center())
        self.play(
            ReplacementTransform(q_formula, q50),
            ReplacementTransform(f_formula, f50),
            ReplacementTransform(cdf_formula, cdf50),
            run_time=1.4,
        )
        self.wait(5.6)

        self.play(
            Indicate(q_path, color=BLUE, scale_factor=1.01),
            Indicate(f_stems, color=GOLD, scale_factor=1.01),
            run_time=1.6,
        )
        self.wait(3.4)

        self.play(tracker.animate.set_value(90), run_time=4.0, rate_func=linear)
        self.wait(3.8)

        q90 = formula_block(r"q_{90}=0.6\%", "固定概率教学模型", BLUE, q50.get_center())
        f90 = formula_block(r"f_{90}\approx0.351\%", "走到这里的人已经更少", GOLD, f50.get_center())
        cdf90 = formula_block(r"F_{90}\approx41.82\%", "仍有 58.18% 没见到五星", MINT, cdf50.get_center())
        self.play(
            ReplacementTransform(q50, q90),
            ReplacementTransform(f50, f90),
            ReplacementTransform(cdf50, cdf90),
            run_time=1.4,
        )
        self.wait(5.6)

        discrete_note = pill("抽数只能取整数；连线只帮助看趋势", MUTED, width=5.45)
        discrete_note.move_to(relation_note)
        self.play(ReplacementTransform(relation_note, discrete_note), run_time=1.1)
        self.wait(4.4)

        q_end = formula_block(r"q_n", "门在这一抽开多大", BLUE, q90.get_center())
        f_end = formula_block(r"f_n", "这根首次出金柱多高", GOLD, f90.get_center())
        cdf_end = formula_block(r"F_n", "到这里累计了多少", MINT, cdf90.get_center())
        self.play(
            ReplacementTransform(q90, q_end),
            ReplacementTransform(f90, f_end),
            ReplacementTransform(cdf90, cdf_end),
            run_time=1.2,
        )
        self.play(Indicate(q_end, color=BLUE), Indicate(f_end, color=GOLD), run_time=1.2)
        self.play(Indicate(cdf_end, color=MINT), run_time=1.0)
        self.play(tracker.animate.set_value(1), run_time=3.0, rate_func=linear)
        self.play(tracker.animate.set_value(90), run_time=3.0, rate_func=linear)
        finish_to(self, TARGET_DURATIONS_V2["ThreeProbabilityCurves"])


class HardPityRewritesCurves(Scene):
    """Compare fixed 0.6% with a deliberately isolated hard-pity-only model."""

    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title(
            "只加第 90 抽硬保底，三条曲线怎样改写？",
            "比较模型：前 89 抽仍为 0.6%，第 90 抽强制出金",
        )
        warning = pill("仅硬保底的比较模型｜并非官方逐抽规则", RED, width=5.85)
        warning.move_to([0, 2.56, 0])
        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(warning), run_time=1.2)
        self.wait(3.8)

        q_shell, q_axes, q_box = stacked_chart_shell(1.48, "条件概率 q(n)", BLUE, 1.02)
        f_shell, f_axes, f_box = stacked_chart_shell(-0.28, "首次出金 PMF f(n)", GOLD, 0.62)
        cdf_shell, cdf_axes, cdf_box = stacked_chart_shell(-2.04, "累计出金 CDF F(n)", MINT, 1.02)
        ticks = x_tick_labels(cdf_axes, (1, 89, 90))
        self.play(FadeIn(q_shell), FadeIn(f_shell), FadeIn(cdf_shell), FadeIn(ticks), run_time=1.5)
        self.wait(2.5)

        fixed_q = trend_path(q_axes, Q_FIXED, GRAY, stroke_width=2.2, opacity=0.75)
        fixed_pmf = stem_plot(f_axes, F_FIXED_PMF, GRAY, stroke_width=2.0, opacity=0.55)
        fixed_cdf = trend_path(cdf_axes, F_FIXED_CDF, GRAY, stroke_width=2.2, opacity=0.75)
        baseline_label = pill("灰色：没有保底、始终 0.6%", GRAY, width=4.30)
        baseline_label.move_to([5.02, 1.35, 0])
        self.play(
            Create(fixed_q),
            FadeIn(fixed_pmf),
            Create(fixed_cdf),
            FadeIn(baseline_label),
            run_time=2.4,
        )
        self.wait(4.6)

        rule = formula_block(
            r"q_1=\cdots=q_{89}=0.006,\quad q_{90}=1",
            "只隔离硬保底的作用",
            BLUE,
            np.array([5.02, 1.35, 0.0]),
        )
        self.play(ReplacementTransform(baseline_label, rule), run_time=1.2)
        self.wait(4.8)

        hard_q = trend_path(q_axes, Q_HARD_ONLY, BLUE, stroke_width=3.4)
        q90_dot = Dot(q_axes.c2p(90, 1.0), radius=0.06, color=GOLD)
        self.play(Create(hard_q), FadeIn(q90_dot, scale=1.8), run_time=2.2)
        self.wait(3.8)

        tracker = ValueTracker(1)
        scanner = always_redraw(
            lambda: Line(
                [q_axes.c2p(tracker.get_value(), 0)[0], q_box.get_top()[1] - 0.10, 0],
                [cdf_axes.c2p(tracker.get_value(), 0)[0], cdf_box.get_bottom()[1] + 0.10, 0],
                color=PINK,
                stroke_width=3.0,
            ).set_opacity(0.82)
        )
        self.add(scanner)
        self.play(tracker.animate.set_value(89), run_time=3.0, rate_func=linear)
        self.wait(3.0)

        first_89_stems = stem_plot(f_axes, F_HARD_PMF[:89], BLUE, stroke_width=2.6, opacity=0.72)
        last_stem = Line(
            f_axes.c2p(90, 0),
            f_axes.c2p(90, F_HARD_PMF[89]),
            color=GOLD,
            stroke_width=7.0,
        )
        mass_formula = formula_block(
            r"f_{90}=0.994^{89}\approx58.53\%",
            "所有还在等待的人，一次收进第 90 抽",
            GOLD,
            np.array([5.02, -0.40, 0.0]),
        )
        self.play(
            FadeIn(first_89_stems),
            GrowFromEdge(last_stem, DOWN),
            FadeIn(mass_formula),
            run_time=2.6,
        )
        self.wait(5.4)

        hard_cdf = trend_path(cdf_axes, F_HARD_CDF, MINT, stroke_width=3.6)
        jump_formula = formula_block(
            r"F_{89}\approx41.47\%\quad\longrightarrow\quad F_{90}=100\%",
            "硬保底把最后的等待者全部清空",
            MINT,
            np.array([5.02, -2.16, 0.0]),
        )
        self.play(Create(hard_cdf), FadeIn(jump_formula), run_time=2.6)
        self.wait(5.4)

        self.play(tracker.animate.set_value(90), run_time=2.0, rate_func=linear)
        self.wait(4.0)

        summary = pill("保底不是旁注：它直接改变 PMF 和 CDF", GOLD, width=5.70)
        summary.move_to([0, -3.35, 0])
        self.play(FadeIn(summary, shift=UP * 0.08), run_time=1.3)
        self.wait(5.2)
        self.play(
            Indicate(q90_dot, color=GOLD, scale_factor=1.35),
            Indicate(last_stem, color=GOLD, scale_factor=1.04),
            run_time=1.4,
        )
        self.play(Indicate(hard_cdf, color=MINT, scale_factor=1.01), run_time=1.2)
        finish_to(self, TARGET_DURATIONS_V2["HardPityRewritesCurves"])


class OfficialNumbersDoNotFixCurve(Scene):
    """Show three equal-status mathematical solutions to the same public constraints."""

    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title(
            "三个公开数字，为什么定不出唯一曲线？",
            "综合概率约束平均等待，却没有公布第 1 到 90 抽的完整 q(n)",
        )
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=1.2)
        self.wait(3.8)

        hard_card = stat_card(
            "只加硬保底的教学模型",
            r"E[T]\approx69.70\quad\Rightarrow\quad 1/E[T]\approx1.435\%",
            BLUE,
            "不足官方公开的综合概率",
            width=5.15,
            height=1.82,
        ).move_to([-3.10, 0.42, 0])
        official_card = stat_card(
            "综合概率 1.6%",
            r"1/0.016=62.5",
            GOLD,
            "平均每轮等待 62.5 抽",
            width=4.15,
            height=1.82,
        ).move_to([3.45, 0.42, 0])
        arrow = flow_arrow(hard_card.get_right(), official_card.get_left(), GOLD, width=4.0)
        self.play(FadeIn(hard_card), GrowArrow(arrow), FadeIn(official_card), run_time=1.7)
        self.wait(5.3)

        deduction = pill("能推出：第 90 抽前，至少有些位置高于 0.6%", MINT, width=7.25)
        deduction.move_to([0, -1.35, 0])
        cannot = pill("推不出：从哪一抽开始、每抽加多少、是否线性", RED, width=7.35)
        cannot.next_to(deduction, DOWN, buff=0.20)
        self.play(FadeIn(deduction, shift=UP * 0.08), FadeIn(cannot, shift=UP * 0.08), run_time=1.3)
        self.wait(4.7)

        self.play(FadeOut(hard_card), FadeOut(official_card), FadeOut(arrow), FadeOut(deduction), FadeOut(cannot), run_time=1.2)

        q_panel = panel(6.35, 4.72, fill=PANEL, edge=PANEL_EDGE).move_to([-3.35, -0.20, 0])
        cdf_panel = panel(6.35, 4.72, fill=PANEL, edge=PANEL_EDGE).move_to([3.35, -0.20, 0])
        q_heading = cn("条件概率 q(n)（第 90 抽前放大）", 0.29, BLUE)
        q_heading.move_to(q_panel.get_top() + DOWN * 0.34)
        cdf_heading = cn("累计概率 CDF", 0.29, MINT)
        cdf_heading.move_to(cdf_panel.get_top() + DOWN * 0.34)
        q_axes = probability_axes(
            x_max=90,
            y_max=0.30,
            width=5.35,
            height=3.05,
            center=np.array([-3.35, -0.42, 0.0]),
        )
        cdf_axes = probability_axes(
            x_max=90,
            y_max=1.02,
            width=5.35,
            height=3.05,
            center=np.array([3.35, -0.42, 0.0]),
        )
        q_ticks = x_tick_labels(q_axes, (1, 50, 90))
        cdf_ticks = x_tick_labels(cdf_axes, (1, 50, 90))
        disclaimer = pill("三条都是示意解｜非官方逐抽表", RED, width=5.20)
        disclaimer.move_to([0, 2.52, 0])
        self.play(
            FadeIn(q_panel),
            FadeIn(cdf_panel),
            FadeIn(q_heading),
            FadeIn(cdf_heading),
            FadeIn(q_axes),
            FadeIn(cdf_axes),
            FadeIn(q_ticks),
            FadeIn(cdf_ticks),
            FadeIn(disclaimer),
            run_time=1.5,
        )
        self.wait(3.5)

        colors = {"A": BLUE, "B": PINK, "C": MINT}
        labels = {
            "A": "示意 A：第 50 抽单点脉冲",
            "B": "示意 B：第 74 抽后平台",
            "C": "示意 C：第 55 抽后缓升",
        }
        q_curves: dict[str, Mobject] = {}
        cdf_curves: dict[str, Mobject] = {}
        q_dots: dict[str, VGroup] = {}
        cdf_dots: dict[str, VGroup] = {}

        for key in ("A", "B", "C"):
            _, _, cdf_values = distribution_from_q(ILLUSTRATIVE_Q[key])
            q_curves[key] = dashed_trend(q_axes, ILLUSTRATIVE_Q[key][:-1], colors[key], num_dashes=44)
            cdf_curves[key] = dashed_trend(cdf_axes, cdf_values, colors[key], num_dashes=48)
            q_dots[key] = sampled_dots(q_axes, ILLUSTRATIVE_Q[key][:-1], colors[key], every=6, radius=0.025)
            cdf_dots[key] = sampled_dots(cdf_axes, cdf_values, colors[key], every=6, radius=0.025)

        q90_marker = Arrow(
            q_axes.c2p(90, 0.255),
            q_axes.c2p(90, 0.30),
            color=GOLD,
            stroke_width=3.5,
            buff=0,
            max_tip_length_to_length_ratio=0.30,
        )
        q90_label = MathTex(r"q_{90}=100\%", color=GOLD).scale(0.42)
        q90_label.next_to(q90_marker, UP, buff=0.08)
        self.play(GrowArrow(q90_marker), FadeIn(q90_label), run_time=0.8)

        for key in ("A", "B", "C"):
            self.play(
                Create(q_curves[key]),
                FadeIn(q_dots[key]),
                Create(cdf_curves[key]),
                FadeIn(cdf_dots[key]),
                run_time=2.2,
            )
            label = legend_item(labels[key], colors[key])
            label_x = {"A": -4.65, "B": 0.0, "C": 4.65}[key]
            if label.width > 4.05:
                label.scale_to_fit_width(4.05)
            label.move_to([label_x, -2.90, 0])
            self.play(FadeIn(label), run_time=0.4)
            if key == "A":
                legend_a = label
            elif key == "B":
                legend_b = label
            else:
                legend_c = label
            self.wait(3.0)

        common_constraint = MathTex(
            r"q_{90}=1,\qquad E[T]=62.5,\qquad 1/E[T]=1.6\%",
            color=GOLD,
        ).scale(0.58)
        common_box = panel(7.35, 0.72, fill="#0B1626", edge=GOLD).move_to([0, -3.55, 0])
        common_constraint.move_to(common_box)
        common_stamp = VGroup(common_box, common_constraint)
        self.play(FadeIn(common_stamp, shift=UP * 0.08), run_time=1.2)
        self.wait(4.8)

        self.play(
            Indicate(legend_a, color=BLUE, scale_factor=1.03),
            Indicate(legend_b, color=PINK, scale_factor=1.03),
            Indicate(legend_c, color=MINT, scale_factor=1.03),
            run_time=1.5,
        )
        self.wait(3.5)

        tracker = ValueTracker(50)
        q_scan = always_redraw(
            lambda: Line(
                q_axes.c2p(tracker.get_value(), 0),
                q_axes.c2p(tracker.get_value(), 0.30),
                color=GOLD,
                stroke_width=2.4,
            ).set_opacity(0.70)
        )
        cdf_scan = always_redraw(
            lambda: Line(
                cdf_axes.c2p(tracker.get_value(), 0),
                cdf_axes.c2p(tracker.get_value(), 1.0),
                color=GOLD,
                stroke_width=2.4,
            ).set_opacity(0.70)
        )
        checkpoint_50 = cn("第 50 抽累计：A 46.18%｜B 25.99%｜C 25.99%", 0.25, INK)
        checkpoint_50.move_to(common_constraint)
        self.play(FadeIn(q_scan), FadeIn(cdf_scan), ReplacementTransform(common_constraint, checkpoint_50), run_time=1.2)
        self.wait(4.3)

        self.play(tracker.animate.set_value(80), run_time=3.0, rate_func=linear)
        checkpoint_80 = cn("第 80 抽累计：A 55.07%｜B 85.69%｜C 71.70%", 0.25, INK)
        checkpoint_80.move_to(checkpoint_50)
        self.play(ReplacementTransform(checkpoint_50, checkpoint_80), run_time=0.9)
        self.wait(3.5)

        conclusion = cn("平均数只固定总量，不规定概率必须摆在哪几抽", 0.31, GOLD)
        conclusion.move_to(checkpoint_80)
        self.play(ReplacementTransform(checkpoint_80, conclusion), run_time=1.1)
        self.wait(3.0)
        finish_to(self, TARGET_DURATIONS_V2["OfficialNumbersDoNotFixCurve"])


class UpWaitingHasTwoHumps(Scene):
    """Use one illustrative first-five-star PMF to teach mixture and convolution."""

    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title(
            "首次拿到当期 UP，为什么会出现两团概率？",
            "只保留 50/50 与歪后保证；先暂时关闭捕获明光",
        )
        scope = pill("教学示意｜不是官方逐抽曲线｜未计捕获明光", RED, width=6.45)
        scope.move_to([0, 2.54, 0])
        self.play(FadeIn(title, shift=DOWN * 0.12), FadeIn(scope), run_time=1.2)
        self.wait(3.8)

        source = flow_card("一次五星等待", r"f_n", BLUE, width=2.30).move_to([-5.15, 1.30, 0])
        split = VGroup(
            Circle(radius=0.34, color=GOLD, fill_color=GOLD, fill_opacity=0.08),
            MathTex(r"50/50", color=GOLD).scale(0.42),
        )
        split[1].move_to(split[0])
        split.move_to([-2.65, 1.30, 0])
        first_branch = flow_card("第一颗就是 UP", r"\tfrac12 f_n", GOLD, width=2.75).move_to([0.25, 1.73, 0])
        second_branch = flow_card("先歪，再等一颗", r"\tfrac12(f\ast f)_n", VIOLET, width=2.75).move_to([0.25, 0.87, 0])
        arrow_in = flow_arrow(source.get_right(), split.get_left(), MUTED, width=3.5)
        arrow_first = flow_arrow(split.get_right(), first_branch.get_left(), GOLD, width=3.5)
        arrow_first.shift(UP * 0.25)
        arrow_second = flow_arrow(split.get_right(), second_branch.get_left(), VIOLET, width=3.5)
        arrow_second.shift(DOWN * 0.25)
        sum_formula = formula_block(
            r"g_n=\tfrac12 f_n+\tfrac12(f\ast f)_n",
            "两条路径的概率相加",
            MINT,
            np.array([4.55, 1.30, 0.0]),
        )
        self.play(FadeIn(source), GrowArrow(arrow_in), FadeIn(split), run_time=1.5)
        self.wait(4.5)
        self.play(
            GrowArrow(arrow_first),
            GrowArrow(arrow_second),
            FadeIn(first_branch),
            FadeIn(second_branch),
            run_time=1.6,
        )
        self.wait(4.4)

        graph_box = panel(13.20, 3.42, fill=PANEL, edge=PANEL_EDGE).move_to([0, -1.68, 0])
        graph_title = cn("首次拿到当期 UP 的等待分布 g(n)", 0.29, INK)
        graph_title.move_to(graph_box.get_top() + DOWN * 0.30)
        axes = probability_axes(
            x_max=180,
            y_max=0.070,
            width=12.10,
            height=2.35,
            center=np.array([0.0, -1.88, 0.0]),
        )
        ticks = x_tick_labels(axes, (1, 90, 180))
        pull_label = cn("横轴：抽数", 0.22, MUTED).move_to([5.40, -0.64, 0])
        self.play(FadeIn(graph_box), FadeIn(graph_title), FadeIn(axes), FadeIn(ticks), FadeIn(pull_label), run_time=1.5)
        self.wait(3.5)

        _, illustrative_f, _ = distribution_from_q(ILLUSTRATIVE_Q["B"])
        convolution = np.convolve(illustrative_f, illustrative_f)
        first_component = np.zeros(180)
        first_component[:90] = 0.5 * illustrative_f
        second_component = np.zeros(180)
        second_component[1:] = 0.5 * convolution
        mixed = first_component + second_component

        first_stems = stem_plot(axes, first_component, GOLD, stroke_width=3.0, opacity=0.92)
        second_stems = stem_plot(axes, second_component, VIOLET, stroke_width=3.0, opacity=0.92)
        mixed_stems = stem_plot(axes, mixed, MINT, stroke_width=3.3, opacity=0.95)

        first_label = pill("第一颗就中 UP：0.5 f(n)", GOLD, width=3.55)
        first_label.move_to([-3.70, -0.43, 0])
        self.play(
            LaggedStart(*[GrowFromEdge(stem, DOWN) for stem in first_stems], lag_ratio=0.004),
            FadeIn(first_label),
            run_time=3.5,
        )
        self.wait(4.5)

        self.play(FadeIn(sum_formula), run_time=1.0)
        convolution_note = pill("两段等待时间相加 = 离散卷积", VIOLET, width=4.70)
        convolution_note.move_to([2.90, -0.43, 0])
        self.play(
            LaggedStart(*[GrowFromEdge(stem, DOWN) for stem in second_stems], lag_ratio=0.003),
            FadeIn(convolution_note),
            run_time=3.8,
        )
        self.wait(4.2)

        self.play(
            first_stems.animate.set_opacity(0.18),
            second_stems.animate.set_opacity(0.18),
            FadeIn(mixed_stems),
            run_time=2.6,
        )
        self.wait(3.4)

        first_peak = int(np.argmax(mixed[:100])) + 1
        second_peak = int(np.argmax(mixed[100:])) + 101
        first_dot = Dot(axes.c2p(first_peak, mixed[first_peak - 1]), radius=0.06, color=GOLD)
        second_dot = Dot(axes.c2p(second_peak, mixed[second_peak - 1]), radius=0.06, color=VIOLET)
        first_peak_label = cn("第一团：一段等待", 0.24, GOLD).next_to(first_dot, DOWN, buff=0.15)
        second_peak_label = cn("第二团：两段相加", 0.24, VIOLET).next_to(second_dot, UP, buff=0.15)
        self.play(
            FadeIn(first_dot, scale=1.6),
            FadeIn(second_dot, scale=1.6),
            FadeIn(first_peak_label),
            FadeIn(second_peak_label),
            run_time=1.4,
        )
        self.wait(4.1)

        closing = pill("加入捕获明光和账号历史后，分布还会继续被改写", PINK, width=7.25)
        closing.move_to([0, -3.56, 0])
        self.play(FadeIn(closing, shift=UP * 0.08), run_time=1.1)
        self.wait(3.2)
        finish_to(self, TARGET_DURATIONS_V2["UpWaitingHasTwoHumps"])
