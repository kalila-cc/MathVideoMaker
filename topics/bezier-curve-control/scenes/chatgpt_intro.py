from __future__ import annotations

from pathlib import Path

import numpy as np
from manim import *


BG = "#07120F"
INK = "#F8F4E3"
MUTED = "#A9B7AE"
ACCENT = "#67D7B0"
FONT = "Smiley Sans"
LATIN_FONT = "Times New Roman"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
SMILEY_FONT_FILE = PROJECT_ROOT / "assets" / "fonts" / "SmileySans-Oblique.ttf"
CHATGPT_LINE_LOGO = PROJECT_ROOT / "assets" / "brand" / "chatgpt_logo_line.svg"


def cn(text: str, size: float = 0.36, color: str = INK) -> Text:
    return Text(text, font=FONT, slant=OBLIQUE, color=color).scale(size)


def chatgpt_word(size: float = 0.42, color: str = INK) -> Text:
    return Text("ChatGPT", font=LATIN_FONT, color=color).scale(size)


def credit_row(size: float = 0.34, color: str = INK) -> VGroup:
    prefix = cn("其余制作由", size, color)
    mark = chatgpt_word(size * 1.25, color)
    suffix = cn("完成", size, color)
    return VGroup(prefix, mark, suffix).arrange(RIGHT, buff=0.12, aligned_edge=DOWN)


def production_scope(size: float = 0.20) -> VGroup:
    labels = ["推导脚本", "动画设计", "配音字幕", "后期合成"]
    chips = []
    for label in labels:
        text = cn(label, size, INK)
        box = RoundedRectangle(
            width=max(1.08, text.width + 0.34),
            height=0.34,
            corner_radius=0.10,
            stroke_color=ACCENT,
            stroke_width=1.0,
            stroke_opacity=0.52,
            fill_color="#0A211D",
            fill_opacity=0.58,
        )
        text.move_to(box)
        chips.append(VGroup(box, text))
    return VGroup(*chips).arrange(RIGHT, buff=0.12)


def notebook_grid(spacing: float = 0.48) -> VGroup:
    width = config.frame_width + spacing
    height = config.frame_height + spacing
    x_values = np.arange(-width / 2, width / 2 + spacing, spacing)
    y_values = np.arange(-height / 2, height / 2 + spacing, spacing)
    grid = VGroup(
        *[Line(DOWN * height / 2 + RIGHT * x, UP * height / 2 + RIGHT * x, color="#8FA8D8", stroke_width=1.6) for x in x_values],
        *[Line(LEFT * width / 2 + UP * y, RIGHT * width / 2 + UP * y, color="#8FA8D8", stroke_width=1.6) for y in y_values],
    )
    grid.set_opacity(0.155)
    grid.set_z_index(-100)
    return grid


def set_scene_background(scene: Scene) -> None:
    scene.camera.background_color = BG
    scene.add(notebook_grid())


class ChatGPTIntro(Scene):
    def construct(self) -> None:
        set_scene_background(self)

        frame = RoundedRectangle(
            width=7.6,
            height=3.95,
            corner_radius=0.24,
            stroke_color="#2A443A",
            stroke_width=1.25,
            fill_color="#0E1B19",
            fill_opacity=0.66,
        )

        mark = SVGMobject(str(CHATGPT_LINE_LOGO)).set_fill(opacity=0).set_stroke(INK, width=2.7).scale(0.74)
        mark.move_to(UP * 0.82)
        wordmark = chatgpt_word(0.62).next_to(mark, DOWN, buff=0.26)

        line = Line(LEFT * 2.05, RIGHT * 2.05, color=ACCENT, stroke_width=1.6, stroke_opacity=0.54)
        line.next_to(wordmark, DOWN, buff=0.27)
        credit = cn("本视频制作完全由 ChatGPT 完成", 0.24, INK).next_to(line, DOWN, buff=0.28)
        scope = production_scope(0.18).next_to(credit, DOWN, buff=0.25)

        content = VGroup(mark, wordmark, line, credit, scope)
        self.play(FadeIn(frame, shift=UP * 0.08), run_time=0.55)
        self.play(FadeIn(mark, shift=UP * 0.12), run_time=0.55)
        self.play(Write(wordmark), Create(line), run_time=0.65)
        self.play(FadeIn(credit, shift=UP * 0.10), run_time=0.45)
        self.play(LaggedStart(*[FadeIn(item, shift=UP * 0.05) for item in scope], lag_ratio=0.28), run_time=1.15)
        self.wait(1.25)
        self.play(FadeOut(VGroup(frame, content), shift=DOWN * 0.06), run_time=0.45)


class ChatGPTOutro(Scene):
    def construct(self) -> None:
        set_scene_background(self)

        frame = RoundedRectangle(
            width=8.7,
            height=4.85,
            corner_radius=0.28,
            stroke_color="#2A443A",
            stroke_width=1.4,
            fill_color="#0E1B19",
            fill_opacity=0.72,
        )

        mark = SVGMobject(str(CHATGPT_LINE_LOGO)).set_fill(opacity=0).set_stroke(INK, width=2.8).scale(0.92)
        mark.move_to(UP * 0.9)
        wordmark = Text("ChatGPT", font=LATIN_FONT, color=INK).scale(0.76).next_to(mark, DOWN, buff=0.36)

        line = Line(LEFT * 2.15, RIGHT * 2.15, color=ACCENT, stroke_width=1.8, stroke_opacity=0.54)
        line.next_to(wordmark, DOWN, buff=0.32)
        topic = cn("选题由创作者确定", 0.24, MUTED).next_to(line, DOWN, buff=0.30)
        credit = credit_row(0.36, INK).next_to(topic, DOWN, buff=0.22)
        sub = cn("推导、动画、配音与合成", 0.22, MUTED).next_to(credit, DOWN, buff=0.25)

        content = VGroup(mark, wordmark, line, topic, credit, sub)
        footer = Text("Math Video Maker", font=LATIN_FONT, color=MUTED).scale(0.23)
        footer.move_to(frame.get_bottom() + UP * 0.28)

        self.play(FadeIn(frame, shift=UP * 0.08), run_time=0.9)
        self.play(FadeIn(mark, shift=UP * 0.12), run_time=0.9)
        self.play(Write(wordmark), Create(line), run_time=0.9)
        self.play(FadeIn(credit, shift=UP * 0.12), FadeIn(sub, shift=UP * 0.1), run_time=1.0)
        self.play(FadeIn(footer), run_time=0.5)
        self.wait(2.7)
        self.play(FadeOut(VGroup(frame, content, footer), shift=DOWN * 0.08), run_time=0.8)
