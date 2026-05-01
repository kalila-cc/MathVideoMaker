from __future__ import annotations

import re
import numpy as np
from manim import *


FONT = "Microsoft YaHei"
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
    return Text(text, font=FONT, color=color).scale(size)


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

        title_top = Text("幂和公式", font=FONT, weight=BOLD, color=INK)
        title_top.scale_to_fit_width(9.85)
        title_bottom = Text("自己算", font=FONT, weight=BOLD, color=AMBER)
        title_bottom.scale_to_fit_width(9.15)
        title = VGroup(title_top, title_bottom).arrange(DOWN, aligned_edge=LEFT, buff=-0.08)
        title.to_edge(LEFT, buff=0.28).to_edge(UP, buff=0.12)

        underline = Line(LEFT * 4.72, RIGHT * 4.72, color=AMBER, stroke_width=10, stroke_opacity=0.90)
        underline.next_to(title_bottom, DOWN, buff=0.04).align_to(title, LEFT)

        hook = Text("不用背公式", font=FONT, weight=BOLD, color=INK).scale(0.58)
        hook2 = Text("直接解系数", font=FONT, weight=BOLD, color=MINT).scale(0.58)
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
            Text("待定系数法", font=FONT, weight=BOLD, color=MINT).scale(0.38),
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

        path = Text("从 0/1/2 次方推出 3 次方", font=FONT, color=MUTED).scale(0.34)
        path.next_to(formula_plate, UP, buff=0.22).align_to(formula_plate, RIGHT).shift(LEFT * 0.15)

        self.add(watermark, title, underline, hook_group, badge, side_formula, path, formula_plate, formula)
        self.wait(0.65)


class KnownFormulas(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        used = 0.0

        title = make_title("把熟悉公式排在一起", "它们像被同一条线索串起来")
        formulas = VGroup(
            formula_row("0 次方", r"\sum_{k=1}^{n} k^0=n", MINT, 0.70),
            formula_row("1 次方", r"\sum_{k=1}^{n} k=\frac{n(n+1)}{2}", BLUE, 0.66),
            formula_row("2 次方", r"\sum_{k=1}^{n} k^2=\frac{n(n+1)(2n+1)}{6}", VIOLET, 0.60),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.42)

        paper = card(6.35, 4.8).to_edge(LEFT, buff=0.48).shift(DOWN * 0.34)
        paper_title = cn("常见答案", 0.34, MUTED).move_to(paper.get_top() + DOWN * 0.34)
        formulas.next_to(paper_title, DOWN, buff=0.48).align_to(paper, LEFT).shift(RIGHT * 0.48)

        thread_card = card(4.6, 4.8).to_edge(RIGHT, buff=0.55).shift(DOWN * 0.34)
        thread_title = cn("共同线索", 0.42, INK).move_to(thread_card.get_top() + DOWN * 0.46)
        nodes = VGroup(
            VGroup(Circle(radius=0.14, color=MINT, stroke_width=3), MathTex(r"k^0", color=MINT).scale(0.48)),
            VGroup(Circle(radius=0.14, color=BLUE, stroke_width=3), MathTex(r"k^1", color=BLUE).scale(0.48)),
            VGroup(Circle(radius=0.14, color=VIOLET, stroke_width=3), MathTex(r"k^2", color=VIOLET).scale(0.48)),
            VGroup(Circle(radius=0.14, color=AMBER, stroke_width=3), MathTex(r"k^3", color=AMBER).scale(0.48)),
        )
        for node in nodes:
            node[1].next_to(node[0], RIGHT, buff=0.22)
        nodes.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        nodes.move_to(thread_card.get_center() + LEFT * 0.35 + UP * 0.10)
        connectors = VGroup(
            *[
                Line(nodes[i][0].get_bottom(), nodes[i + 1][0].get_top(), color=MUTED, stroke_width=2.2)
                for i in range(3)
            ]
        )
        rule = VGroup(
            cn("幂次每升一格", 0.27, MUTED),
            cn("求和多项式也升一阶", 0.27, AMBER),
        ).arrange(DOWN, buff=0.16)
        rule.next_to(nodes, DOWN, buff=0.38).align_to(nodes, LEFT)

        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)
        used += 0.8
        self.play(FadeIn(paper), FadeIn(paper_title), run_time=0.7)
        used += 0.7
        self.play(LaggedStart(*[FadeIn(row, shift=UP * 0.10) for row in formulas], lag_ratio=0.22), run_time=3.0)
        used += 3.0
        self.play(FadeIn(thread_card, shift=LEFT * 0.18), FadeIn(thread_title), run_time=1.0)
        used += 1.4
        self.play(Create(connectors), LaggedStart(*[FadeIn(node, shift=UP * 0.08) for node in nodes], lag_ratio=0.18), run_time=2.4)
        used += 2.2
        self.play(FadeIn(rule, shift=UP * 0.08), run_time=1.2)
        used += 1.2
        wait_to(self, used, 17.90)


class DegreePattern(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        used = 0.0

        title = make_title("展开以后，次数在往上走", "p 次方的和，看起来会高一阶")
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
        arrows.arrange(DOWN, buff=0.42).move_to(right_panel).shift(UP * 0.42)
        label = cn("幂的次数  →  求和多项式次数", 0.30, MUTED).next_to(arrows, UP, buff=0.34)

        question = MathTex(r"3 \rightarrow 4,\quad 4 \rightarrow 5,\quad ?", color=AMBER).scale(0.76)
        question.next_to(arrows, DOWN, buff=0.62)
        note = cn("如果只是多项式，系数就有机会被解出来。", 0.30, INK).next_to(question, DOWN, buff=0.32)

        self.play(FadeIn(left_panel), FadeIn(right_panel), run_time=0.7)
        used += 0.7
        self.play(LaggedStart(*[FadeIn(row, shift=UP * 0.08) for row in expanded], lag_ratio=0.20), run_time=3.2)
        used += 3.2
        self.play(FadeIn(label), LaggedStart(*[FadeIn(row, shift=UP * 0.08) for row in arrows], lag_ratio=0.22), run_time=3.0)
        used += 3.0
        self.play(FadeIn(question, shift=UP * 0.12), run_time=1.1)
        used += 1.1
        self.play(FadeIn(note, shift=UP * 0.10), run_time=1.0)
        used += 1.0
        wait_to(self, used, 20.72)


class DifferenceIdea(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        used = 0.0

        title = make_title("求和只比上一格多一块", "相邻两个结果的差，就是新来的那一项")
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

        title = make_title("用三次方做实验", "能差出三次方，就先猜四次多项式")
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

        title = make_title("把差分展开，再把同类项排齐", "一行一行看，账本就不会乱")
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

        title = make_title("比较系数，四个数依次锁住", "让多余的平方项、一次项、常数项全部消失")
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


class SquarePayoff(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        used = 0.0

        title = make_title("最后，它收成了一个平方", "三次方求和，就是三角数的平方")
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

        title = make_title("伯努利数：更高次的系数地图", "它们统一管理幂和公式里的固定系数")
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)
        used += 0.8

        table_panel = card(5.65, 5.7).to_edge(LEFT, buff=0.55).shift(DOWN * 0.10)
        table_title = cn("继续做同一本系数账", 0.36, MUTED).move_to(table_panel.get_top() + DOWN * 0.40)
        rows = VGroup(
            math_label_row(r"p=0", r"S_0(n)=n", MINT, 0.50),
            math_label_row(r"p=1", r"S_1(n)=\frac12n^2+\frac12n", BLUE, 0.44),
            math_label_row(r"p=2", r"S_2(n)=\frac13n^3+\frac12n^2+\frac16n", VIOLET, 0.36),
            math_label_row(r"p=3", r"S_3(n)=\frac14n^4+\frac12n^3+\frac14n^2", AMBER, 0.36),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        rows.next_to(table_title, DOWN, buff=0.38).align_to(table_panel, LEFT).shift(RIGHT * 0.38)

        map_panel = card(6.15, 5.7).to_edge(RIGHT, buff=0.55).shift(DOWN * 0.10)
        map_title = cn("系数地图的一角", 0.36, MUTED).move_to(map_panel.get_top() + DOWN * 0.40)
        map_grid = VGroup()
        grid_colors = [MINT, BLUE, VIOLET, AMBER]
        grid_values = [r"B_0=1", r"B_1=-\frac12", r"B_2=\frac16", r"B_4=-\frac1{30}"]
        for idx, (value, color) in enumerate(zip(grid_values, grid_colors)):
            cell = RoundedRectangle(
                width=2.16,
                height=0.72,
                corner_radius=0.10,
                stroke_color=color,
                stroke_width=1.4,
                fill_color=color,
                fill_opacity=0.12,
            )
            cell_label = MathTex(value, color=color).scale(0.42).move_to(cell)
            map_grid.add(VGroup(cell, cell_label))
        map_grid.arrange_in_grid(rows=2, cols=2, buff=(0.28, 0.24))
        map_grid.next_to(map_title, DOWN, buff=0.42)
        map_note = cn("这些固定数字，反复出现在不同次数的幂和里。", 0.26, MUTED).next_to(map_grid, DOWN, buff=0.34)
        bernoulli = MathTex(r"B_0,\ B_1,\ B_2,\ B_4,\ldots", color=INK)
        bernoulli.scale(0.48).next_to(map_note, DOWN, buff=0.30)
        general = MathTex(
            r"\sum_{k=1}^{n} k^p="
            r"\frac{1}{p+1}\sum_{j=0}^{p}(-1)^j{p+1\choose j}B_j n^{p+1-j}",
            color=AMBER,
        ).scale(0.34)
        general.next_to(bernoulli, DOWN, buff=0.30)
        note = cn("今天只是看见这张地图的一角。", 0.27, MUTED).next_to(general, DOWN, buff=0.24)

        self.play(FadeIn(table_panel), FadeIn(map_panel), FadeIn(table_title), FadeIn(map_title), run_time=0.9)
        used += 0.9
        self.play(LaggedStart(*[FadeIn(row, shift=UP * 0.08) for row in rows], lag_ratio=0.16), run_time=3.2)
        used += 3.2
        self.play(LaggedStart(*[FadeIn(cell, shift=UP * 0.08) for cell in map_grid], lag_ratio=0.18), FadeIn(map_note, shift=UP * 0.08), run_time=2.3)
        used += 2.3
        self.play(Write(bernoulli), run_time=1.5)
        used += 1.5
        self.play(FadeIn(general, shift=UP * 0.08), run_time=1.4)
        used += 1.4
        self.play(FadeIn(note, shift=UP * 0.08), run_time=1.2)
        used += 1.2
        wait_to(self, used, 24.70)
