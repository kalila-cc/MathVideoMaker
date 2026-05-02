from __future__ import annotations

import re
from pathlib import Path
import numpy as np
from manim import *


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SMILEY_FONT_FILE = PROJECT_ROOT / "assets" / "fonts" / "SmileySans-Oblique.ttf"
FONT = "Smiley Sans"
LATIN_FONT = "Times New Roman"
BG = "#07120F"
PANEL = "#0E1B19"
INK = "#F8F4E3"
MUTED = "#A9B7AE"
AMBER = "#F3B64A"
MINT = "#67D7B0"
CORAL = "#FF6B6B"
BLUE = "#82C7FF"
VIOLET = "#C9A7FF"
GRID = "#24352E"

TIMES_TEX_TEMPLATE = TexTemplate()
TIMES_TEX_TEMPLATE.add_to_preamble(r"\usepackage{mathptmx}")
MathTex.set_default(tex_template=TIMES_TEX_TEMPLATE)

LATIN_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[./+-][A-Za-z0-9]+)*")


def latin_font_map(text: str) -> dict[str, str]:
    return {token: LATIN_FONT for token in LATIN_PATTERN.findall(text)}


def cn(text: str, size: float = 0.36, color: str = INK) -> Text:
    # Keep prose in one font. Pango raises inline Times glyphs inside Chinese Text,
    # so math-like tokens in captions are either plain UI-font text or separate MathTex.
    return Text(text, font=FONT, slant=OBLIQUE, color=color).scale(size)


def smiley_text(text: str, **kwargs) -> Text:
    # Smiley Sans ships as one oblique style; asking Pango for Bold can create
    # an empty SVG on Windows, so keep the original weight.
    kwargs.pop("weight", None)
    kwargs.setdefault("slant", OBLIQUE)
    return Text(text, font=FONT, **kwargs)


def wait_to(scene: Scene, used: float, target: float) -> None:
    scene.wait(max(0.1, target - used))


def make_title(title: str, subtitle: str | None = None) -> VGroup:
    top = cn(title, 0.52, INK).to_edge(UP, buff=0.34)
    if not subtitle:
        return VGroup(top)
    sub = cn(subtitle, 0.30, MUTED).next_to(top, DOWN, buff=0.13)
    return VGroup(top, sub)


def card(width: float, height: float, color: str = PANEL) -> RoundedRectangle:
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.22,
        stroke_color="#2A443A",
        stroke_width=1.4,
        fill_color=color,
        fill_opacity=0.92,
    )


def formula_row(label: str, formula: str, color: str = INK, scale: float = 0.62) -> VGroup:
    label_mob = cn(label, 0.28, MUTED)
    formula_mob = MathTex(formula, color=color).scale(scale)
    return VGroup(label_mob, formula_mob).arrange(RIGHT, buff=0.26, aligned_edge=DOWN)


def math_label_row(label: str, formula: str, color: str = INK, scale: float = 0.62) -> VGroup:
    label_mob = MathTex(label, color=MUTED).scale(scale * 0.86)
    formula_mob = MathTex(formula, color=color).scale(scale)
    return VGroup(label_mob, formula_mob).arrange(RIGHT, buff=0.28, aligned_edge=DOWN)


def tiny_block(width: float, height: float, color: str, label: str | None = None) -> VGroup:
    rect = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.08,
        stroke_color=color,
        stroke_width=1.2,
        fill_color=color,
        fill_opacity=0.34,
    )
    if label is None:
        return VGroup(rect)
    txt = MathTex(label, color=INK).scale(0.42).move_to(rect)
    return VGroup(rect, txt)


def coefficient_chip(text: str, color: str) -> VGroup:
    box = RoundedRectangle(
        width=1.05,
        height=0.48,
        corner_radius=0.12,
        stroke_color=color,
        fill_color=color,
        fill_opacity=0.16,
    )
    label = MathTex(text, color=color).scale(0.48).move_to(box)
    return VGroup(box, label)


class CoverFrame(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG

        watermark = MathTex(r"\sum k^p", color="#12352D").scale(3.9)
        watermark.set_opacity(0.32)
        watermark.move_to(RIGHT * 3.40 + UP * 0.72)

        title_top = smiley_text("幂和公式", weight=BOLD, color=INK)
        title_top.scale_to_fit_width(9.85)
        title_bottom = smiley_text("自己算", weight=BOLD, color=AMBER)
        title_bottom.scale_to_fit_width(9.15)
        title = VGroup(title_top, title_bottom).arrange(DOWN, aligned_edge=LEFT, buff=-0.08)
        title.to_edge(LEFT, buff=0.28).to_edge(UP, buff=0.12)

        underline = Line(LEFT * 4.72, RIGHT * 4.72, color=AMBER, stroke_width=10, stroke_opacity=0.90)
        underline.next_to(title_bottom, DOWN, buff=0.04).align_to(title, LEFT)

        hook = smiley_text("不用背公式", weight=BOLD, color=INK).scale(0.58)
        hook2 = smiley_text("直接解系数", weight=BOLD, color=MINT).scale(0.58)
        hook_group = VGroup(hook, hook2).arrange(RIGHT, buff=0.28)
        hook_group.next_to(underline, DOWN, buff=0.20).align_to(title, LEFT)

        badge = VGroup(
            RoundedRectangle(
                width=3.15,
                height=0.70,
                corner_radius=0.16,
                stroke_color=MINT,
                stroke_width=1.8,
                fill_color=MINT,
                fill_opacity=0.18,
            ),
            smiley_text("待定系数法", weight=BOLD, color=MINT).scale(0.38),
        )
        badge[1].move_to(badge[0])
        badge.next_to(hook_group, RIGHT, buff=0.42).align_to(hook_group, DOWN)

        side_formula = VGroup(
            MathTex(r"\sum k^3", color=CORAL).scale(1.34),
            MathTex(r"=T_n^2", color=AMBER).scale(1.16),
        ).arrange(DOWN, buff=0.06)
        side_formula.move_to(RIGHT * 4.95 + DOWN * 0.35)

        formula_plate = RoundedRectangle(
            width=13.15,
            height=1.42,
            corner_radius=0.18,
            stroke_color="#2A443A",
            stroke_width=1.5,
            fill_color="#0E1B19",
            fill_opacity=0.82,
        ).to_edge(DOWN, buff=0.25)
        formula = MathTex(
            r"\sum_{k=1}^{n} k^3",
            r"=",
            r"\left(\frac{n(n+1)}{2}\right)^2",
            color=INK,
        ).scale(0.96).move_to(formula_plate)
        formula[0].set_color(CORAL)
        formula[2].set_color(AMBER)

        path = smiley_text("从 0/1/2 次方推出 3 次方", color=MUTED).scale(0.34)
        path.next_to(formula_plate, UP, buff=0.22).align_to(formula_plate, RIGHT).shift(LEFT * 0.15)

        self.add(watermark, title, underline, hook_group, badge, side_formula, path, formula_plate, formula)
        self.wait(0.65)


class DesktopCoverFrame(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG

        title_top = smiley_text("幂和公式", weight=BOLD, color=INK)
        title_top.scale_to_fit_width(6.85)
        title_bottom = smiley_text("自己算", weight=BOLD, color=AMBER)
        title_bottom.scale_to_fit_width(5.65)
        title = VGroup(title_top, title_bottom).arrange(DOWN, aligned_edge=LEFT, buff=0.00)
        title.to_edge(LEFT, buff=0.55).to_edge(UP, buff=0.42)

        underline = Line(LEFT * 3.35, RIGHT * 3.35, color=AMBER, stroke_width=7, stroke_opacity=0.88)
        underline.next_to(title, DOWN, buff=0.08).align_to(title, LEFT)

        hook = VGroup(
            cn("不用背公式", 0.36, INK),
            cn("直接解系数", 0.36, MINT),
        ).arrange(RIGHT, buff=0.22)
        hook.next_to(underline, DOWN, buff=0.22).align_to(title, LEFT)

        right_panel = RoundedRectangle(
            width=4.65,
            height=4.55,
            corner_radius=0.24,
            stroke_color="#2A443A",
            stroke_width=1.5,
            fill_color=PANEL,
            fill_opacity=0.78,
        ).to_edge(RIGHT, buff=0.58).shift(UP * 0.26)

        panel_title = cn("从前三个答案里找规律", 0.30, MUTED)
        panel_title.move_to(right_panel.get_top() + DOWN * 0.42)
        stack = VGroup(
            MathTex(r"\sum k^0=n", color=MINT).scale(0.58),
            MathTex(r"\sum k=\frac{n(n+1)}{2}", color=BLUE).scale(0.54),
            MathTex(r"\sum k^2=\frac{n(n+1)(2n+1)}{6}", color=VIOLET).scale(0.42),
            MathTex(r"\sum k^3=?", color=AMBER).scale(0.70),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        stack.next_to(panel_title, DOWN, buff=0.36)
        stack.align_to(right_panel, LEFT).shift(RIGHT * 0.42)

        badge = VGroup(
            RoundedRectangle(
                width=2.80,
                height=0.52,
                corner_radius=0.13,
                stroke_color=MINT,
                stroke_width=1.5,
                fill_color=MINT,
                fill_opacity=0.14,
            ),
            cn("待定系数法", 0.28, MINT),
        )
        badge[1].move_to(badge[0])
        badge.next_to(stack, DOWN, buff=0.30).align_to(stack, LEFT)

        formula_plate = RoundedRectangle(
            width=12.35,
            height=1.35,
            corner_radius=0.18,
            stroke_color="#2A443A",
            stroke_width=1.4,
            fill_color=PANEL,
            fill_opacity=0.82,
        ).to_edge(DOWN, buff=0.36)
        formula = MathTex(
            r"\sum_{k=1}^{n} k^3",
            r"=",
            r"\left(\frac{n(n+1)}{2}\right)^2",
            color=INK,
        ).scale(0.92).move_to(formula_plate)
        formula[0].set_color(CORAL)
        formula[2].set_color(AMBER)

        self.add(title, underline, hook, right_panel, panel_title, stack, badge, formula_plate, formula)
        self.wait(0.65)


class KnownFormulas(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        used = 0.0

        title = make_title("常见求和公式", "先把已经知道的答案放在一起")
        formulas = VGroup(
            formula_row("0 次方", r"\sum_{k=1}^{n} k^0=n", MINT, 0.70),
            formula_row("1 次方", r"\sum_{k=1}^{n} k=\frac{n(n+1)}{2}", BLUE, 0.66),
            formula_row("2 次方", r"\sum_{k=1}^{n} k^2=\frac{n(n+1)(2n+1)}{6}", VIOLET, 0.60),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.42)

        paper = card(6.35, 4.8).to_edge(LEFT, buff=0.48).shift(DOWN * 0.34)
        paper_title = cn("常见答案", 0.34, MUTED).move_to(paper.get_top() + DOWN * 0.34)
        formulas.next_to(paper_title, DOWN, buff=0.48).align_to(paper, LEFT).shift(RIGHT * 0.48)

        thread_card = card(4.6, 4.8).to_edge(RIGHT, buff=0.55).shift(DOWN * 0.34)
        thread_title = cn("下一条呢？", 0.42, INK).move_to(thread_card.get_top() + DOWN * 0.46)
        unknowns = VGroup(
            MathTex(r"\sum_{k=1}^{n} k^3=\ ?", color=AMBER).scale(0.70),
            MathTex(r"\sum_{k=1}^{n} k^4=\ ?", color=CORAL).scale(0.66),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        unknowns.next_to(thread_title, DOWN, buff=0.52).align_to(thread_card, LEFT).shift(RIGHT * 0.56)
        wait_line = cn("如果只靠背公式", 0.29, MUTED)
        wait_line.next_to(unknowns, DOWN, buff=0.50).align_to(unknowns, LEFT)
        wait_line_2 = cn("就只能继续等答案", 0.32, CORAL)
        wait_line_2.next_to(wait_line, DOWN, buff=0.18).align_to(wait_line, LEFT)

        structure_box = RoundedRectangle(
            width=10.55,
            height=0.92,
            corner_radius=0.18,
            stroke_color=MINT,
            stroke_width=1.5,
            fill_color=MINT,
            fill_opacity=0.10,
        ).to_edge(DOWN, buff=0.34)
        structure_question = cn("这些公式背后，会不会有同一套结构？", 0.34, MINT).move_to(structure_box)

        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)
        used += 0.8
        self.play(FadeIn(paper), FadeIn(paper_title), run_time=0.7)
        used += 0.7
        self.play(LaggedStart(*[FadeIn(row, shift=UP * 0.10) for row in formulas], lag_ratio=0.30), run_time=9.0)
        used += 9.0
        self.play(FadeIn(thread_card, shift=LEFT * 0.18), FadeIn(thread_title), run_time=1.0)
        used += 1.0
        self.play(LaggedStart(*[FadeIn(row, shift=UP * 0.08) for row in unknowns], lag_ratio=0.25), run_time=3.0)
        used += 3.0
        self.play(FadeIn(wait_line, shift=UP * 0.08), FadeIn(wait_line_2, shift=UP * 0.08), run_time=2.4)
        used += 2.4
        self.play(FadeIn(structure_box), FadeIn(structure_question, shift=UP * 0.08), run_time=1.6)
        used += 1.6
        wait_to(self, used, 29.71)


class DegreePattern(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        used = 0.0

        title = make_title("幂次和多项式次数", "零次、一次、二次的结果都高一阶")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)
        used += 0.8

        left_panel = card(5.95, 5.25).to_edge(LEFT, buff=0.55).shift(DOWN * 0.18)
        right_panel = card(5.3, 5.25).to_edge(RIGHT, buff=0.55).shift(DOWN * 0.18)

        expanded = VGroup(
            math_label_row(r"k^0", r"S_0(n)=n", MINT, 0.64),
            math_label_row(r"k^1", r"S_1(n)=\frac12n^2+\frac12n", BLUE, 0.56),
            math_label_row(r"k^2", r"S_2(n)=\frac13n^3+\frac12n^2+\frac16n", VIOLET, 0.45),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.52)
        expanded.move_to(left_panel).shift(DOWN * 0.05)

        arrows = VGroup(
            VGroup(MathTex(r"0", color=MINT).scale(0.70), Arrow(LEFT * 0.6, RIGHT * 0.6, color=MUTED), MathTex(r"1", color=MINT).scale(0.70)),
            VGroup(MathTex(r"1", color=BLUE).scale(0.70), Arrow(LEFT * 0.6, RIGHT * 0.6, color=MUTED), MathTex(r"2", color=BLUE).scale(0.70)),
            VGroup(MathTex(r"2", color=VIOLET).scale(0.70), Arrow(LEFT * 0.6, RIGHT * 0.6, color=MUTED), MathTex(r"3", color=VIOLET).scale(0.70)),
        )
        for row in arrows:
            row.arrange(RIGHT, buff=0.26)
        arrows.arrange(DOWN, buff=0.34).move_to(right_panel).shift(UP * 0.72)
        label = cn("幂的次数  →  求和多项式次数", 0.30, MUTED).next_to(arrows, UP, buff=0.34)

        general = VGroup(
            MathTex(r"p", color=AMBER).scale(0.62),
            cn("次方的和", 0.26, MUTED),
            MathTex(r"\rightarrow", color=MUTED).scale(0.52),
            MathTex(r"p+1", color=AMBER).scale(0.62),
            cn("次多项式", 0.26, MUTED),
        ).arrange(RIGHT, buff=0.12)
        general.next_to(arrows, DOWN, buff=0.50)
        question = MathTex(r"p=3\quad\Rightarrow\quad 4", color=AMBER).scale(0.78)
        question.next_to(general, DOWN, buff=0.38)
        question_label = cn("三次方求和，先猜四次多项式", 0.27, AMBER).next_to(question, DOWN, buff=0.22)
        note = cn("真正要算的，是多项式里的系数。", 0.29, INK).next_to(question_label, DOWN, buff=0.30)

        self.play(FadeIn(left_panel), FadeIn(right_panel), run_time=0.7)
        used += 0.7
        self.play(LaggedStart(*[FadeIn(row, shift=UP * 0.08) for row in expanded], lag_ratio=0.20), run_time=5.5)
        used += 5.5
        self.play(FadeIn(label), LaggedStart(*[FadeIn(row, shift=UP * 0.08) for row in arrows], lag_ratio=0.22), run_time=4.6)
        used += 4.6
        self.play(FadeIn(general, shift=UP * 0.08), run_time=2.4)
        used += 2.4
        self.play(FadeIn(question, shift=UP * 0.12), FadeIn(question_label, shift=UP * 0.10), run_time=2.0)
        used += 2.0
        self.play(FadeIn(note, shift=UP * 0.10), run_time=1.0)
        used += 1.0
        wait_to(self, used, 25.70)


class DifferenceIdea(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        used = 0.0

        title = make_title("相邻求和结果的差", "从前 n-1 项到前 n 项，只新增最后一项")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)
        used += 0.8

        previous_terms = VGroup(
            tiny_block(0.46, 0.38, MINT, r"1^p"),
            tiny_block(0.46, 0.38, MINT, r"2^p"),
            tiny_block(0.46, 0.38, MINT, r"3^p"),
            tiny_block(0.46, 0.38, MINT, r"\cdots"),
            tiny_block(0.62, 0.38, MINT, r"(n-1)^p"),
        ).arrange(RIGHT, buff=0.08)
        plus = MathTex(r"+", color=MUTED).scale(0.52).next_to(previous_terms, RIGHT, buff=0.16)
        new_term = tiny_block(0.58, 0.58, AMBER, r"n^p").next_to(plus, RIGHT, buff=0.16)
        term_row = VGroup(previous_terms, plus, new_term).move_to(LEFT * 3.25 + DOWN * 0.10)

        previous_brace = Brace(previous_terms, DOWN, color=MINT, buff=0.12)
        previous_label = MathTex(r"S_p(n-1)", color=MINT).scale(0.52).next_to(previous_brace, DOWN, buff=0.12)
        total_brace = Brace(VGroup(previous_terms, plus, new_term), UP, color=AMBER, buff=0.12)
        total_label = MathTex(r"S_p(n)", color=AMBER).scale(0.56).next_to(total_brace, UP, buff=0.12)
        new_label = cn("新增最后一项", 0.25, AMBER).next_to(new_term, DOWN, buff=0.22)

        eq_panel = card(5.65, 4.6).to_edge(RIGHT, buff=0.6).shift(DOWN * 0.12)
        eq_title = cn("差分", 0.48, AMBER).move_to(eq_panel.get_top() + DOWN * 0.55)
        equation = MathTex(r"S_p(n)-S_p(n-1)=n^p", color=INK).scale(0.78)
        equation.move_to(eq_panel.get_center() + UP * 0.35)
        desc = cn("总量变了多少，就看新来的那一块。", 0.31, MUTED).next_to(equation, DOWN, buff=0.52)
        degree_note = VGroup(
            cn("差分会把次数", 0.29, AMBER),
            MathTex(r"p+1", color=AMBER).scale(0.46),
            cn("降到", 0.29, AMBER),
            MathTex(r"p", color=AMBER).scale(0.46),
        ).arrange(RIGHT, buff=0.12).next_to(desc, DOWN, buff=0.45)

        self.play(FadeIn(previous_terms, shift=UP * 0.08), GrowFromCenter(previous_brace), FadeIn(previous_label), run_time=1.2)
        used += 1.0
        self.play(FadeIn(plus), FadeIn(new_term, shift=RIGHT * 0.16), FadeIn(new_label), run_time=1.2)
        used += 1.4
        self.play(GrowFromCenter(total_brace), FadeIn(total_label), run_time=0.8)
        used += 0.8
        self.play(FadeIn(eq_panel, shift=LEFT * 0.18), FadeIn(eq_title), run_time=0.8)
        used += 0.8
        self.play(Write(equation), run_time=1.4)
        used += 1.4
        self.play(FadeIn(desc, shift=UP * 0.1), run_time=1.0)
        used += 1.0
        self.play(FadeIn(degree_note, shift=UP * 0.1), run_time=1.2)
        used += 1.2
        self.play(new_term.animate.shift(UP * 0.12), rate_func=there_and_back, run_time=1.0)
        used += 1.0
        wait_to(self, used, 18.84)


class CubicSetup(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        used = 0.0

        title = make_title("三次方求和的设定", "用四次多项式表示未知答案")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)
        used += 0.8

        left_panel = card(5.4, 5.35).to_edge(LEFT, buff=0.56).shift(DOWN * 0.12)
        bar_shapes = VGroup()
        values = [1, 8, 27, 64]
        labels = [r"1^3", r"2^3", r"3^3", r"\cdots"]
        for idx, value in enumerate(values):
            h = min(3.2, 0.18 * value + 0.42)
            bar = RoundedRectangle(
                width=0.66,
                height=h,
                corner_radius=0.08,
                stroke_color=AMBER if idx < 3 else MUTED,
                fill_color=AMBER if idx < 3 else MUTED,
                fill_opacity=0.35 if idx < 3 else 0.18,
            )
            bar_shapes.add(bar)
        bar_shapes.arrange(RIGHT, aligned_edge=DOWN, buff=0.38)
        labels_group = VGroup(
            *[
                MathTex(label, color=INK if idx < 3 else MUTED).scale(0.45).next_to(bar_shapes[idx], DOWN, buff=0.16)
                for idx, label in enumerate(labels)
            ]
        )
        bars = VGroup(bar_shapes, labels_group).move_to(left_panel.get_center() + DOWN * 0.05)
        sum_label = MathTex(r"1^3+2^3+\cdots+n^3", color=AMBER).scale(0.66).next_to(bars, UP, buff=0.48)

        right_panel = card(6.35, 5.35).to_edge(RIGHT, buff=0.48).shift(DOWN * 0.12)
        poly_title = cn("待定系数", 0.42, MUTED).move_to(right_panel.get_top() + DOWN * 0.44)
        poly = MathTex(
            r"P(n)=a n^4+b n^3+c n^2+d n+e",
            color=INK,
        ).scale(0.58)
        chips = VGroup(
            coefficient_chip(r"a", MINT),
            coefficient_chip(r"b", BLUE),
            coefficient_chip(r"c", VIOLET),
            coefficient_chip(r"d", CORAL),
            coefficient_chip(r"e", AMBER),
        ).arrange(RIGHT, buff=0.18)
        condition = MathTex(r"P(0)=0\quad\Rightarrow\quad e=0", color=AMBER).scale(0.56)
        target = MathTex(r"P(n)-P(n-1)=n^3", color=MINT).scale(0.62)
        setup_stack = VGroup(poly, chips, condition, target).arrange(DOWN, buff=0.38)
        setup_stack.next_to(poly_title, DOWN, buff=0.45)

        self.play(FadeIn(left_panel), FadeIn(right_panel), run_time=0.8)
        used += 0.8
        self.play(FadeIn(sum_label, shift=UP * 0.1), LaggedStart(*[FadeIn(bar, shift=UP * 0.08) for bar in bar_shapes], lag_ratio=0.18), FadeIn(labels_group), run_time=2.6)
        used += 2.6
        self.play(FadeIn(poly_title), Write(poly), run_time=1.6)
        used += 1.6
        self.play(LaggedStart(*[FadeIn(chip, shift=UP * 0.08) for chip in chips], lag_ratio=0.14), run_time=1.5)
        used += 1.5
        self.play(Write(condition), run_time=1.3)
        used += 1.3
        self.play(Write(target), run_time=1.3)
        used += 1.3
        wait_to(self, used, 25.49)


class DifferenceExpansion(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        used = 0.0

        title = make_title("差分后的同类项", "把每一列系数排齐比较")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)
        used += 0.8

        left_panel = card(6.05, 5.7).to_edge(LEFT, buff=0.45).shift(DOWN * 0.08)
        basis_title = cn("基础差分", 0.38, MUTED).move_to(left_panel.get_top() + DOWN * 0.42)
        basis = VGroup(
            MathTex(r"\Delta n^4=4n^3-6n^2+4n-1", color=MINT).scale(0.48),
            MathTex(r"\Delta n^3=3n^2-3n+1", color=BLUE).scale(0.50),
            MathTex(r"\Delta n^2=2n-1", color=VIOLET).scale(0.52),
            MathTex(r"\Delta n=1", color=CORAL).scale(0.54),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        basis.next_to(basis_title, DOWN, buff=0.45).align_to(left_panel, LEFT).shift(RIGHT * 0.42)

        right_panel = card(6.25, 5.7).to_edge(RIGHT, buff=0.45).shift(DOWN * 0.08)
        combine_title = cn("组合成 P(n) 的差分", 0.38, MUTED).move_to(right_panel.get_top() + DOWN * 0.42)
        delta_p = VGroup(
            MathTex(r"\Delta P", color=INK).scale(0.60),
            MathTex(r"=4a\,n^3", color=MINT).scale(0.52),
            MathTex(r"+(-6a+3b)n^2", color=BLUE).scale(0.52),
            MathTex(r"+(4a-3b+2c)n", color=VIOLET).scale(0.52),
            MathTex(r"+(-a+b-c+d)", color=CORAL).scale(0.52),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        delta_p.next_to(combine_title, DOWN, buff=0.42).align_to(right_panel, LEFT).shift(RIGHT * 0.42)
        target = MathTex(r"\Delta P=n^3", color=AMBER).scale(0.72).next_to(delta_p, DOWN, buff=0.46)
        note = cn("右边只有 n 的三次方，其他列都要变成 0。", 0.26, MUTED)
        note.next_to(target, DOWN, buff=0.28).align_to(delta_p, LEFT)

        self.play(FadeIn(left_panel), FadeIn(right_panel), FadeIn(basis_title), FadeIn(combine_title), run_time=0.9)
        used += 0.9
        self.play(LaggedStart(*[FadeIn(row, shift=UP * 0.08) for row in basis], lag_ratio=0.18), run_time=4.0)
        used += 4.0
        self.play(LaggedStart(*[FadeIn(row, shift=UP * 0.08) for row in delta_p], lag_ratio=0.16), run_time=4.0)
        used += 4.0
        self.play(Write(target), FadeIn(note, shift=UP * 0.08), run_time=1.5)
        used += 1.5
        wait_to(self, used, 27.15)


class SolveCoefficients(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        used = 0.0

        title = make_title("解出四个待定系数", "三次项留下，其他次数都为 0")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)
        used += 0.8

        panel = card(11.6, 5.9).shift(DOWN * 0.18)
        self.play(FadeIn(panel), run_time=0.6)
        used += 0.6

        equations = VGroup(
            VGroup(MathTex(r"4a=1", color=MINT).scale(0.58), MathTex(r"a=\frac14", color=MINT).scale(0.58)),
            VGroup(MathTex(r"-6a+3b=0", color=BLUE).scale(0.58), MathTex(r"b=\frac12", color=BLUE).scale(0.58)),
            VGroup(MathTex(r"4a-3b+2c=0", color=VIOLET).scale(0.58), MathTex(r"c=\frac14", color=VIOLET).scale(0.58)),
            VGroup(MathTex(r"-a+b-c+d=0", color=CORAL).scale(0.58), MathTex(r"d=0", color=CORAL).scale(0.58)),
        )
        for row in equations:
            arrow = Arrow(LEFT * 0.32, RIGHT * 0.32, color=MUTED, buff=0.04)
            row.add(arrow)
            row.arrange(RIGHT, buff=0.40)
        equations.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        equations.move_to(panel.get_center() + UP * 0.42).align_to(panel, LEFT).shift(RIGHT * 0.82)

        locks = VGroup()
        for row in equations:
            lock = cn("锁定", 0.24, AMBER).next_to(row, RIGHT, buff=0.55)
            locks.add(lock)

        result = MathTex(
            r"S_3(n)=\frac14n^4+\frac12n^3+\frac14n^2",
            color=AMBER,
        ).scale(0.74)
        result.move_to(panel.get_bottom() + UP * 0.80)

        self.play(LaggedStart(*[FadeIn(row, shift=UP * 0.08) for row in equations], lag_ratio=0.25), run_time=5.2)
        used += 5.2
        self.play(LaggedStart(*[FadeIn(lock, shift=LEFT * 0.08) for lock in locks], lag_ratio=0.18), run_time=1.6)
        used += 1.6
        self.play(Write(result), run_time=1.5)
        used += 1.5
        self.play(result.animate.set_color(INK), rate_func=there_and_back, run_time=1.0)
        used += 1.0
        wait_to(self, used, 24.23)


class BinomialRecurrence(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        used = 0.0

        title = make_title("二项式差分与递推", "把等式两边同时从一加到 n")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)
        used += 0.8

        result_box = RoundedRectangle(
            width=8.9,
            height=0.74,
            corner_radius=0.16,
            stroke_color=AMBER,
            stroke_width=1.4,
            fill_color=AMBER,
            fill_opacity=0.10,
        ).move_to(UP * 2.25)
        result_label = cn("系数法得到", 0.25, MUTED)
        result_formula = MathTex(
            r"S_3(n)=\frac14 n^4+\frac12 n^3+\frac14 n^2",
            color=AMBER,
        ).scale(0.46)
        result = VGroup(result_label, result_formula).arrange(RIGHT, buff=0.34).move_to(result_box)
        look_back = cn("现在回头看差分本身。", 0.28, MINT).next_to(result_box, DOWN, buff=0.18)

        self.play(FadeIn(result_box, shift=UP * 0.08), FadeIn(result, shift=UP * 0.08), run_time=1.4)
        used += 1.4
        self.play(FadeIn(look_back, shift=UP * 0.08), run_time=1.0)
        used += 1.0
        wait_to(self, used, 5.82)
        used = 5.82

        self.play(FadeOut(result_box), FadeOut(result), FadeOut(look_back), run_time=0.6)
        used += 0.6

        proof_panel = card(11.65, 5.45).shift(DOWN * 0.43)
        proof_title = cn("先展开，再相减", 0.38, MUTED).move_to(proof_panel.get_top() + DOWN * 0.42)
        raw_delta = MathTex(r"(k+1)^4-k^4", color=INK).scale(0.62)
        raw_delta.next_to(proof_title, DOWN, buff=0.26)
        base_power = MathTex(r"(k+1)^4", color=INK).scale(0.58)
        base_power.next_to(raw_delta, DOWN, buff=0.26).align_to(raw_delta, LEFT)
        factor = MathTex(
            r"=",
            r"(k+1)(k+1)(k+1)(k+1)",
            color=INK,
        ).scale(0.58)
        factor[0].set_color(MUTED)
        factor.next_to(base_power, DOWN, buff=0.24).align_to(base_power, LEFT)
        expanded = MathTex(
            r"=",
            r"k^4+4k^3+6k^2+4k+1",
            color=INK,
        ).scale(0.58)
        expanded[0].set_color(MUTED)
        expanded.next_to(factor, DOWN, buff=0.30).align_to(factor, LEFT)
        subtract_note = cn("再减去 k 的四次方，左边回到同一个差分", 0.23, MUTED)
        subtract_note.next_to(expanded, DOWN, buff=0.30).align_to(factor, LEFT)
        leaves = MathTex(
            r"=",
            r"4k^3+6k^2+4k+1",
            color=AMBER,
        ).scale(0.64)
        leaves.next_to(subtract_note, DOWN, buff=0.18).align_to(factor, LEFT)
        choose_note = cn("这些系数来自：四个括号里选几个 1", 0.25, MUTED)
        choose_note.next_to(leaves, DOWN, buff=0.32)
        proof_rows = VGroup(
            MathTex(r"\binom{4}{1}=4", color=MINT).scale(0.40),
            MathTex(r"\binom{4}{2}=6", color=BLUE).scale(0.40),
            MathTex(r"\binom{4}{3}=4", color=VIOLET).scale(0.40),
            MathTex(r"\binom{4}{4}=1", color=AMBER).scale(0.40),
        ).arrange(RIGHT, buff=0.42)
        proof_rows.next_to(choose_note, DOWN, buff=0.24)

        sum_panel = card(11.65, 5.35).shift(DOWN * 0.43)
        sum_title = cn("因为对每个 k 都成立，所以两边同时求和", 0.34, MUTED).move_to(sum_panel.get_top() + DOWN * 0.42)
        sum_both = MathTex(
            r"\sum_{k=1}^{n}\big((k+1)^4-k^4\big)"
            r"="
            r"\sum_{k=1}^{n}\big(4k^3+6k^2+4k+1\big)",
            color=INK,
        )
        sum_both.scale_to_fit_width(9.35)
        sum_both.next_to(sum_title, DOWN, buff=0.44)
        cancel_demo = MathTex(
            r"(2^4-1^4)+(3^4-2^4)+\cdots+((n+1)^4-n^4)",
            color=MUTED,
        )
        cancel_demo.scale_to_fit_width(8.95)
        cancel_demo.next_to(sum_both, DOWN, buff=0.50)
        cancel_result = MathTex(
            r"\sum_{k=1}^{n}\big((k+1)^4-k^4\big)=(n+1)^4-1",
            color=MINT,
        )
        cancel_result.scale_to_fit_width(7.40)
        cancel_result.next_to(cancel_demo, DOWN, buff=0.44)

        s_panel = card(11.65, 5.35).shift(DOWN * 0.43)
        s_title = cn("右边按幂和定义改写", 0.38, MUTED).move_to(s_panel.get_top() + DOWN * 0.42)
        right_raw = MathTex(
            r"\sum_{k=1}^{n}\big(4k^3+6k^2+4k+1\big)"
            r"="
            r"4\sum k^3+6\sum k^2+4\sum k+\sum 1",
            color=INK,
        )
        right_raw.scale_to_fit_width(9.45)
        right_raw.next_to(s_title, DOWN, buff=0.42)
        definition_line = MathTex(
            r"S_3(n)=\sum k^3,\quad S_2(n)=\sum k^2,\quad S_1(n)=\sum k,\quad S_0(n)=\sum 1",
            color=MUTED,
        )
        definition_line.scale_to_fit_width(9.20)
        definition_line.next_to(right_raw, DOWN, buff=0.36)
        sum_line = MathTex(
            r"(n+1)^4-1=4S_3(n)+6S_2(n)+4S_1(n)+S_0(n)",
            color=MINT,
        )
        sum_line.scale_to_fit_width(8.60)
        sum_line.next_to(definition_line, DOWN, buff=0.42)
        solve_line = MathTex(
            r"S_3(n)=\frac{(n+1)^4-1-6S_2(n)-4S_1(n)-S_0(n)}{4}",
            color=AMBER,
        )
        solve_line.scale_to_fit_width(8.35)
        solve_line.next_to(sum_line, DOWN, buff=0.36)
        known_title = cn("这一步之后，S_3 就能借用低次幂和来算。", 0.25, MUTED).next_to(solve_line, DOWN, buff=0.30)

        self.play(FadeIn(proof_panel), FadeIn(proof_title), FadeIn(raw_delta), run_time=1.4)
        used += 1.4
        self.play(Write(base_power), Write(factor), run_time=2.4)
        used += 2.4
        wait_to(self, used, 13.02)
        used = 13.02
        self.play(Write(expanded), run_time=3.0)
        used += 3.0
        self.play(FadeIn(subtract_note, shift=UP * 0.08), Write(leaves), run_time=3.0)
        used += 3.0
        wait_to(self, used, 30.44)
        used = 30.44
        self.play(FadeIn(choose_note, shift=UP * 0.08), LaggedStart(*[FadeIn(row, shift=UP * 0.08) for row in proof_rows], lag_ratio=0.12), run_time=5.4)
        used += 5.4
        wait_to(self, used, 51.73)
        used = 51.73

        self.play(
            FadeOut(proof_panel),
            FadeOut(proof_title),
            FadeOut(raw_delta),
            FadeOut(base_power),
            FadeOut(factor),
            FadeOut(expanded),
            FadeOut(subtract_note),
            FadeOut(leaves),
            FadeOut(choose_note),
            FadeOut(proof_rows),
            run_time=0.8,
        )
        used += 0.8

        self.play(FadeIn(sum_panel), FadeIn(sum_title), run_time=0.9)
        used += 0.9
        self.play(Write(sum_both), run_time=3.4)
        used += 3.4
        self.play(Write(cancel_demo), run_time=3.0)
        used += 3.0
        self.play(Write(cancel_result), run_time=2.0)
        used += 2.0
        wait_to(self, used, 65.51)
        used = 65.51

        self.play(
            FadeOut(sum_panel),
            FadeOut(sum_title),
            FadeOut(sum_both),
            FadeOut(cancel_demo),
            FadeOut(cancel_result),
            run_time=0.8,
        )
        used += 0.8
        self.play(FadeIn(s_panel), FadeIn(s_title), run_time=0.9)
        used += 0.9
        self.play(Write(right_raw), run_time=3.8)
        used += 3.8
        self.play(FadeIn(definition_line, shift=UP * 0.08), run_time=2.0)
        used += 2.0
        self.play(Write(sum_line), run_time=3.0)
        used += 3.0
        self.play(Write(solve_line), run_time=3.0)
        used += 3.0
        self.play(FadeIn(known_title, shift=UP * 0.08), run_time=1.3)
        used += 1.3
        wait_to(self, used, 95.40)
        used = 95.40

        general_panel = card(11.9, 5.55).shift(DOWN * 0.15)
        general_title = cn("换成 p 次方，也一样", 0.40, MUTED).move_to(general_panel.get_top() + DOWN * 0.46)
        general_sum = MathTex(
            r"(n+1)^{p+1}-1="
            r"\sum_{r=0}^{p}\binom{p+1}{r}S_r(n)",
            color=MINT,
        ).scale(0.56)
        general_sum.next_to(general_title, DOWN, buff=0.44)
        recurrence = MathTex(
            r"S_p(n)="
            r"\frac{(n+1)^{p+1}-1-\sum_{r=0}^{p-1}\binom{p+1}{r}S_r(n)}{p+1}",
            color=AMBER,
        )
        recurrence.scale_to_fit_width(10.55)
        recurrence.next_to(general_sum, DOWN, buff=0.48)

        flow_label = cn("低次幂和一步一步推出高次幂和", 0.27, MUTED).next_to(recurrence, DOWN, buff=0.42)
        flow = VGroup()
        flow_colors = [MINT, BLUE, VIOLET, AMBER]
        for idx, name in enumerate([r"S_0", r"S_1", r"S_2", r"S_3"]):
            chip = coefficient_chip(name, flow_colors[idx]).scale(0.72)
            flow.add(chip)
            if idx < 3:
                flow.add(Arrow(LEFT * 0.20, RIGHT * 0.20, color=MUTED, stroke_width=2.0, buff=0.02))
        flow.arrange(RIGHT, buff=0.18)
        flow.next_to(flow_label, DOWN, buff=0.25)

        bernoulli_bridge = VGroup(
            coefficient_chip(r"B_0,B_1,B_2,\ldots", AMBER).scale(0.64),
            cn("伯努利数：整理固定系数的一串有理数", 0.23, MUTED),
        ).arrange(RIGHT, buff=0.22)
        bernoulli_bridge.next_to(general_title, RIGHT, buff=0.52)

        self.play(
            FadeOut(s_panel),
            FadeOut(s_title),
            FadeOut(right_raw),
            FadeOut(definition_line),
            FadeOut(sum_line),
            FadeOut(solve_line),
            FadeOut(known_title),
            run_time=1.0,
        )
        used += 1.0
        self.play(FadeIn(general_panel), FadeIn(general_title), run_time=0.9)
        used += 0.9
        self.play(Write(general_sum), run_time=2.7)
        used += 2.7
        self.play(Write(recurrence), run_time=3.1)
        used += 3.1
        self.play(FadeIn(flow_label, shift=UP * 0.08), LaggedStart(*[FadeIn(item, shift=UP * 0.05) for item in flow], lag_ratio=0.10), run_time=2.5)
        used += 2.5
        self.play(FadeIn(bernoulli_bridge, shift=UP * 0.08), run_time=1.6)
        used += 1.6
        wait_to(self, used, 125.39)


class SquarePayoff(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        used = 0.0

        title = make_title("三次方求和的另一种写法", "它也可以写成三角数的平方")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)
        used += 0.8

        tri_panel = card(5.1, 5.1).to_edge(LEFT, buff=0.75).shift(DOWN * 0.20)
        tri_title = cn("括号里这部分", 0.36, MUTED).move_to(tri_panel.get_top() + DOWN * 0.42)

        tri_dots = VGroup()
        n = 5
        for row in range(n):
            for col in range(row + 1):
                dot = Dot(radius=0.052, color=AMBER)
                dot.move_to(np.array([col * 0.28 - row * 0.14, -row * 0.26, 0.0]))
                tri_dots.add(dot)
        tri_dots.next_to(tri_title, DOWN, buff=0.48)
        tri_label = MathTex(r"T_n=1+2+\cdots+n", color=AMBER).scale(0.50).next_to(tri_dots, DOWN, buff=0.36)
        tri_formula = MathTex(r"T_n=\frac{n(n+1)}{2}", color=AMBER).scale(0.58).next_to(tri_label, DOWN, buff=0.30)
        bracket_name = MathTex(r"\frac{n(n+1)}{2}=T_n", color=MINT).scale(0.62).next_to(tri_formula, DOWN, buff=0.42)
        tri_group = VGroup(tri_dots, tri_label, tri_formula, bracket_name)

        formula_panel = card(6.1, 5.1).to_edge(RIGHT, buff=0.52).shift(DOWN * 0.20)
        step0 = MathTex(r"S_3(n)=\frac14n^4+\frac12n^3+\frac14n^2", color=INK).scale(0.52)
        step1 = MathTex(r"=\frac{n^2(n+1)^2}{4}", color=BLUE).scale(0.68)
        step2 = MathTex(r"=", r"\left(", r"\frac{n(n+1)}{2}", r"\right)^2", color=AMBER).scale(0.72)
        conclusion = MathTex(r"S_3(n)=T_n^2", color=MINT).scale(0.76)
        steps = VGroup(step0, step1, step2, conclusion).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        steps.move_to(formula_panel).shift(UP * 0.08)
        bracket_box = SurroundingRectangle(step2[2], color=MINT, buff=0.08, stroke_width=2.4)
        bracket_tag = MathTex(r"T_n", color=MINT).scale(0.45).next_to(bracket_box, DOWN, buff=0.08)

        self.play(FadeIn(tri_panel), FadeIn(tri_title), FadeIn(tri_dots, shift=UP * 0.08), run_time=1.2)
        used += 1.5
        self.play(FadeIn(formula_panel), run_time=0.6)
        used += 0.6
        self.play(FadeIn(tri_label, shift=UP * 0.08), FadeIn(tri_formula, shift=UP * 0.08), Write(step0), run_time=1.4)
        used += 1.4
        self.play(FadeIn(step1, shift=UP * 0.08), run_time=1.1)
        used += 1.1
        self.play(FadeIn(step2, shift=UP * 0.08), FadeIn(bracket_name, shift=UP * 0.08), run_time=1.1)
        used += 1.1
        self.play(Create(bracket_box), FadeIn(bracket_tag), run_time=0.8)
        used += 0.8
        self.play(FadeIn(conclusion, shift=UP * 0.08), run_time=1.0)
        used += 1.5
        wait_to(self, used, 17.63)


class BernoulliDoor(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        used = 0.0

        title = make_title("伯努利数的出现", "它整理高次幂和里的固定系数")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)
        used += 0.8

        definition_panel = card(11.30, 0.88).shift(UP * 1.48)
        definition_title = cn("可以先把它理解成一组校正系数", 0.27, MUTED)
        b_grid = VGroup()
        grid_colors = [MINT, BLUE, AMBER, VIOLET]
        grid_values = [r"B_0=1", r"B_1=-\frac12", r"B_2=\frac16", r"B_4=-\frac1{30}"]
        for value, color in zip(grid_values, grid_colors):
            cell = RoundedRectangle(
                width=1.60,
                height=0.48,
                corner_radius=0.10,
                stroke_color=color,
                stroke_width=1.4,
                fill_color=color,
                fill_opacity=0.12,
            )
            cell_label = MathTex(value, color=color).scale(0.31).move_to(cell)
            b_grid.add(VGroup(cell, cell_label))
        b_grid.arrange(RIGHT, buff=0.22)
        definition_stack = VGroup(definition_title, b_grid).arrange(RIGHT, buff=0.52).move_to(definition_panel)

        left_panel = card(5.45, 3.45).to_edge(LEFT, buff=0.64).shift(DOWN * 0.96)
        left_title = cn("从幂和出发", 0.34, MUTED).move_to(left_panel.get_top() + DOWN * 0.36)
        power_sum = MathTex(r"\sum_{k=1}^{n}k^p", color=AMBER).scale(0.78)
        power_note = cn("它最早就和系统研究幂和有关", 0.27, INK)
        recurrence_note = cn("前面的递推，只是其中一个入口", 0.25, MUTED)
        left_stack = VGroup(power_sum, power_note, recurrence_note).arrange(DOWN, buff=0.32)
        left_stack.next_to(left_title, DOWN, buff=0.42)

        right_panel = card(6.10, 3.45).to_edge(RIGHT, buff=0.64).shift(DOWN * 0.96)
        right_title = cn("还会在这些地方出现", 0.34, MUTED).move_to(right_panel.get_top() + DOWN * 0.36)

        def use_case(label: str, formula: str, color: str) -> VGroup:
            box = RoundedRectangle(
                width=5.12,
                height=0.62,
                corner_radius=0.12,
                stroke_color=color,
                stroke_width=1.4,
                fill_color=color,
                fill_opacity=0.10,
            )
            text = cn(label, 0.23, INK)
            math = MathTex(formula, color=color).scale(0.33)
            row = VGroup(text, math).arrange(RIGHT, buff=0.34)
            row.move_to(box)
            return VGroup(box, row)

        taylor = use_case("泰勒展开", r"\frac{x}{e^x-1}", MINT)
        euler = use_case("欧拉麦克劳林求和", r"\sum f(k)\leftrightarrow\int f(x)\,dx", BLUE)
        zeta = use_case("黎曼泽塔函数", r"\zeta(2m)", VIOLET)
        use_cases = VGroup(taylor, euler, zeta).arrange(DOWN, buff=0.22)
        use_cases.next_to(right_title, DOWN, buff=0.38)

        bottom_note = cn("今天只从三次方求和这里，看见它为什么值得单独命名。", 0.29, MUTED)
        bottom_note.next_to(VGroup(left_panel, right_panel), DOWN, buff=0.22)

        self.play(FadeIn(definition_panel), FadeIn(definition_stack, shift=UP * 0.08), run_time=1.4)
        used += 1.4
        self.play(FadeIn(left_panel), FadeIn(right_panel), FadeIn(left_title), FadeIn(right_title), run_time=1.0)
        used += 1.0
        self.play(FadeIn(power_sum, shift=UP * 0.08), FadeIn(power_note, shift=UP * 0.08), run_time=1.7)
        used += 1.7
        self.play(FadeIn(recurrence_note, shift=UP * 0.08), run_time=1.1)
        used += 1.1
        self.play(FadeIn(taylor, shift=UP * 0.08), run_time=1.4)
        used += 1.4
        self.play(FadeIn(euler, shift=UP * 0.08), run_time=1.4)
        used += 1.4
        self.play(FadeIn(zeta, shift=UP * 0.08), run_time=1.4)
        used += 1.4
        self.play(FadeIn(bottom_note, shift=UP * 0.08), run_time=1.3)
        used += 1.3
        wait_to(self, used, 31.20)
