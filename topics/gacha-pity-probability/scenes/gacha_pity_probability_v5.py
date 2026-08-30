from __future__ import annotations

import numpy as np
from manim import *

from gacha_pity_probability_v4 import *  # noqa: F403


PREVIEW_DURATIONS_V5 = {
    "CommunitySampleDistributionV5": 34.666667,
    "CommunityFitComparisonV5": 25.716667,
    "FinalEstimatedCurvesV5": 42.45,
    "ProbabilityStateConclusionV5": 38.683333,
}


def card_border_flash(card: VGroup, color: str) -> Animation:
    """Highlight a compact card without scaling or tinting its contents."""

    outline = card[0].copy()
    outline.set_fill(opacity=0.0)
    outline.set_stroke(color=color, width=2.5, opacity=0.72)
    return ShowPassingFlash(outline, time_width=0.55)


class CommunitySampleDistributionV5(Scene):
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
                ("筛出74期角色活动祈愿", MINT),
                ("约2205万条五星落点", INK),
                ("样本截止：2025-06-09", MUTED),
            ],
            accent=MINT,
            note="玩家上传样本",
        )
        self.play(FadeIn(chart_shell), FadeIn(info_box), FadeIn(source_state), run_time=1.2)
        hold_to(self, 9.4)

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
            run_time=2.5,
        )
        peak_pull = int(np.argmax(COMMUNITY_SAMPLE_PMF)) + 1
        peak_value = float(COMMUNITY_SAMPLE_PMF[peak_pull - 1])
        peak_dot = Dot(axes.c2p(peak_pull, peak_value), radius=0.075, color=GOLD)
        peak_label = VGroup(
            cn("第77抽最高", 0.27, GOLD),
            MathTex(r"9.708\%", color=GOLD).scale(0.48),
        ).arrange(DOWN, buff=0.08).next_to(peak_dot, UP, buff=0.12)
        peak_state = info_state(
            "样本峰值",
            [
                ("第77抽记录最多", GOLD),
                ("占全部五星落点9.708%", MINT),
                ("第74抽以后快速抬升", PINK),
            ],
            accent=GOLD,
            note="柱高：上传五星落点占比",
        )
        self.play(FadeIn(peak_dot, scale=1.4), FadeIn(peak_label), run_time=0.8)
        hold_to(self, 17.25)
        self.play(ReplacementTransform(source_state, peak_state), run_time=1.0)
        hold_to(self, 20.8)

        q_state = info_state(
            "改用仍在等待的人作分母",
            [
                ("q(74) ≈ 6.746%", PINK),
                ("q(77) ≈ 24.622%", GOLD),
                ("q(80) ≈ 42.440%", MINT),
            ],
            accent=BLUE,
            note="得到样本中的条件概率估计",
        )
        q74_marker = Line(
            axes.c2p(74, 0), axes.c2p(74, 0.11), color=PINK, stroke_width=2.0
        ).set_opacity(0.72)
        self.play(ReplacementTransform(peak_state, q_state), Create(q74_marker), run_time=1.1)
        self.play(Indicate(peak_dot, color=GOLD), run_time=0.9)
        finish_to(self, PREVIEW_DURATIONS_V5["CommunitySampleDistributionV5"])


class CommunityFitComparisonV5(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title(
            "另一批社区样本给出的条件概率拟合",
            "约2500万抽｜genshin-wishes.com样本分析｜2021",
        )
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        chart_shell, axes, chart_box = full_chart_shell(
            "Paimon上传落点 + 社区模型首金曲线",
            GOLD,
            y_max=0.12,
            y_ticks=(0.06, 0.12),
            y_decimals=0,
            x_ticks=(1, 50, 73, 77, 90),
        )
        info_box = right_panel(edge=GOLD, fill="#0A1525")
        sample_bars = stem_plot(axes, COMMUNITY_SAMPLE_PMF, MINT, stroke_width=3.0, opacity=0.46)
        sample_tag = pill("Paimon上传样本", MINT, 1.95)
        sample_tag.move_to(chart_box.get_corner(UR) + LEFT * 1.24 + DOWN * 0.38)
        fit_state = info_state(
            "社区条件概率拟合",
            [
                ("样本量：约2500万抽", INK),
                ("第1–73抽：0.6%", BLUE),
                ("第74抽起：每抽约+6个百分点", PINK),
                ("第90抽：100%", GOLD),
            ],
            accent=GOLD,
            formula=r"q_n=\min\{1,\ 0.006+0.06(n-73)_+\}",
        )
        self.play(
            FadeIn(chart_shell),
            FadeIn(info_box),
            FadeIn(sample_bars),
            FadeIn(sample_tag),
            FadeIn(fit_state),
            run_time=1.3,
        )
        hold_to(self, 4.0)

        fit_curve = DashedVMobject(
            trend_path(axes, COMMUNITY_FIT_PMF, GOLD, stroke_width=3.5),
            num_dashes=64,
            dashed_ratio=0.58,
        )
        fit_tag = pill("模型首金曲线", GOLD, 2.10)
        fit_tag.move_to(chart_box.get_corner(UL) + RIGHT * 1.88 + DOWN * 0.92)
        self.play(Create(fit_curve), FadeIn(fit_tag), run_time=2.1)
        hold_to(self, 15.3)

        comparison_state = info_state(
            "两批样本呈现相近形状",
            [
                ("薄荷柱：Paimon上传落点", MINT),
                ("金色虚线：另一批样本的拟合", GOLD),
                ("主峰都在第77抽附近", PINK),
            ],
            accent=VIOLET,
            formula=r"f_n=q_n\prod_{k<n}(1-q_k)",
        )
        self.play(ReplacementTransform(fit_state, comparison_state), run_time=0.9)
        self.play(Indicate(fit_curve, color=GOLD), Indicate(sample_bars, color=MINT), run_time=1.2)
        finish_to(self, PREVIEW_DURATIONS_V5["CommunityFitComparisonV5"])


class FinalEstimatedCurvesV5(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title(
            "把软保底放回三种曲线",
            "官方0.6% / 1.6% / 90抽边界 + 社区条件概率拟合",
        )
        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8)

        centers = (
            np.array([-4.60, 0.92, 0.0]),
            np.array([-0.44, 0.92, 0.0]),
            np.array([-4.60, -1.56, 0.0]),
            np.array([-0.44, -1.56, 0.0]),
        )
        q_shell, q_axes, _ = compact_chart_shell(
            centers[0], "条件概率 q(n)｜这一抽", BLUE, y_max=1.05, top_label=r"100\%"
        )
        q_shell.scale(0.94)
        f_shell, f_axes, _ = compact_chart_shell(
            centers[1], "PMF f(n)｜首金分布", GOLD, y_max=0.12, top_label=r"12\%"
        )
        f_shell.scale(0.94)
        cdf_shell, cdf_axes, _ = compact_chart_shell(
            centers[2], "CDF F(n)｜累计出金率", MINT, y_max=1.05, top_label=r"100\%"
        )
        cdf_shell.scale(0.94)
        stats_card = compact_text_card(
            centers[3],
            "这套估计的整体结果",
            ["平均等待：约62.30抽", "长期五星率：约1.605%", "官方综合概率：1.6%"],
            VIOLET,
        ).scale(0.94)
        info_box = right_panel(edge=VIOLET, fill="#0A1525")
        self.play(
            FadeIn(q_shell),
            FadeIn(f_shell),
            FadeIn(cdf_shell),
            FadeIn(info_box),
            run_time=1.2,
        )

        q_path = trend_path(q_axes, COMMUNITY_FIT_Q, BLUE, stroke_width=3.2)
        q74 = Dot(q_axes.c2p(74, COMMUNITY_FIT_Q[73]), radius=0.050, color=PINK)
        q90 = Dot(q_axes.c2p(90, 1.0), radius=0.055, color=GOLD)
        q_state = info_state(
            "条件概率：软保底开始抬升",
            [
                ("第1–73抽：0.6%", BLUE),
                ("第74抽：6.6%", PINK),
                ("第89抽：96.6%", VIOLET),
                ("第90抽：100%", GOLD),
            ],
            accent=BLUE,
        )
        self.play(Create(q_path), FadeIn(q74), FadeIn(q90), FadeIn(q_state), run_time=1.6)
        hold_to(self, 16.5)

        f_stems = stem_plot(f_axes, COMMUNITY_FIT_PMF, GOLD, stroke_width=2.3, opacity=0.90)
        f_peak = Dot(f_axes.c2p(77, COMMUNITY_FIT_PMF[76]), radius=0.055, color=PINK)
        f_state = info_state(
            "首金分布：主峰落在第77抽",
            [
                ("第77抽：约10.535%", GOLD),
                ("前面没出 × 本抽出金", MUTED),
            ],
            accent=GOLD,
            formula=r"f_n=q_n\prod_{k<n}(1-q_k)",
        )
        self.play(
            LaggedStart(*[GrowFromEdge(stem, DOWN) for stem in f_stems], lag_ratio=0.0015),
            FadeIn(f_peak),
            ReplacementTransform(q_state, f_state),
            run_time=1.8,
        )
        hold_to(self, 21.55)

        cdf_path = trend_path(cdf_axes, COMMUNITY_FIT_CDF, MINT, stroke_width=3.2)
        cdf73 = Dot(cdf_axes.c2p(73, COMMUNITY_FIT_CDF[72]), radius=0.050, color=BLUE)
        cdf80 = Dot(cdf_axes.c2p(80, COMMUNITY_FIT_CDF[79]), radius=0.050, color=PINK)
        cdf90 = Dot(cdf_axes.c2p(90, 1.0), radius=0.055, color=GOLD)
        cdf_state = info_state(
            "累计出金率：等待者快速减少",
            [
                ("第73抽：约35.55%", BLUE),
                ("第80抽：约91.85%", PINK),
                ("第90抽：100%", GOLD),
            ],
            accent=MINT,
        )
        self.play(
            Create(cdf_path),
            FadeIn(cdf73),
            FadeIn(cdf80),
            FadeIn(cdf90),
            ReplacementTransform(f_state, cdf_state),
            run_time=1.7,
        )
        hold_to(self, 28.45)

        result_state = info_state(
            "三条曲线描述同一段五星等待",
            [
                ("q(n)：这一抽出金的概率", BLUE),
                ("PMF：首金落在哪一抽", GOLD),
                ("CDF：到这里已有多少人出金", MINT),
            ],
            accent=VIOLET,
            note="社区数据估计趋势｜不是官方逐抽表",
        )
        self.play(FadeIn(stats_card), run_time=1.0)
        hold_to(self, 34.6)
        self.play(ReplacementTransform(cdf_state, result_state), run_time=1.0)
        hold_to(self, 39.0)
        self.play(
            card_border_flash(q_shell, BLUE),
            card_border_flash(f_shell, GOLD),
            card_border_flash(cdf_shell, MINT),
            run_time=1.3,
        )
        finish_to(self, PREVIEW_DURATIONS_V5["FinalEstimatedCurvesV5"])


class ProbabilityStateConclusionV5(Scene):
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
            centers[0], "条件概率 q(n)｜这一抽", BLUE, y_max=1.05, top_label=r"100\%"
        )
        q_shell.scale(0.94)
        f_shell, f_axes, _ = compact_chart_shell(
            centers[1], "PMF f(n)｜首金分布", GOLD, y_max=0.12, top_label=r"12\%"
        )
        f_shell.scale(0.94)
        cdf_shell, cdf_axes, _ = compact_chart_shell(
            centers[2], "CDF F(n)｜累计出金率", MINT, y_max=1.05, top_label=r"100\%"
        )
        cdf_shell.scale(0.94)
        fitted_card = compact_text_card(
            centers[3],
            "软保底后的估计形状",
            ["q(n)：第74抽起抬升", "PMF：第77抽形成主峰", "CDF：第90抽达到100%"],
            VIOLET,
        ).scale(0.94)
        info_box = right_panel(edge=VIOLET, fill="#0A1525")
        self.play(FadeIn(info_box), FadeIn(q_shell), run_time=1.0)
        hold_to(self, 2.8)

        q_path = trend_path(q_axes, COMMUNITY_FIT_Q, BLUE, stroke_width=3.0)
        q_state = info_state(
            "同一批玩家的三张图",
            [("q(n)：前面没出时，这一抽的概率", BLUE)],
            accent=BLUE,
        )
        self.play(Create(q_path), FadeIn(q_state), run_time=1.1)
        hold_to(self, 6.4)

        f_stems = stem_plot(f_axes, COMMUNITY_FIT_PMF, GOLD, stroke_width=2.2, opacity=0.88)
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

        cdf_path = trend_path(cdf_axes, COMMUNITY_FIT_CDF, MINT, stroke_width=3.0)
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

        fit_state = info_state(
            "软保底后的三条估计曲线",
            [
                ("条件概率：第74抽起快速抬升", BLUE),
                ("首金分布：第77抽附近形成主峰", GOLD),
                ("累计出金率：第90抽达到100%", MINT),
            ],
            accent=VIOLET,
        )
        self.play(FadeIn(fitted_card), ReplacementTransform(all_state, fit_state), run_time=1.1)
        hold_to(self, 19.4)

        numbers_card = compact_text_card(
            centers[3],
            "三个公开数字",
            ["0.6%：五星基础概率", "1.6%：含保底综合概率", "90抽：五星等待上限"],
            VIOLET,
        ).scale(0.94)
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
            ReplacementTransform(fitted_card, numbers_card),
            ReplacementTransform(fit_state, number_state),
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
        self.play(ReplacementTransform(state_records, final_state), run_time=1.0)
        self.play(
            card_border_flash(q_shell, BLUE),
            card_border_flash(f_shell, GOLD),
            card_border_flash(cdf_shell, MINT),
            run_time=1.4,
        )
        finish_to(self, PREVIEW_DURATIONS_V5["ProbabilityStateConclusionV5"])
