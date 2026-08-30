from __future__ import annotations

from pathlib import Path

import numpy as np
from manim import *


BG = "#07111F"
INK = "#F8F4E3"
MUTED = "#AAB4C2"
MINT = "#5EEAD4"
BLUE = "#7DD3FC"
PANEL = "#0D1727"
PANEL_EDGE = "#2A3A50"
GRID_COLOR = "#8FA8D8"
FONT = "Smiley Sans"
LATIN_FONT = "Times New Roman"

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SMILEY_FONT_FILE = PROJECT_ROOT / "assets" / "fonts" / "SmileySans-Oblique.ttf"
CHATGPT_LINE_LOGO = PROJECT_ROOT / "assets" / "brand" / "chatgpt_logo_line.svg"


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


def scope_chips() -> VGroup:
    chips = VGroup()
    for label, color in (
        ("脚本推导", BLUE),
        ("动画设计", MINT),
        ("配音字幕", BLUE),
        ("后期合成", MINT),
    ):
        text = cn(label, 0.18, INK)
        box = RoundedRectangle(
            width=1.18,
            height=0.38,
            corner_radius=0.12,
            stroke_color=color,
            stroke_width=1.0,
            stroke_opacity=0.52,
            fill_color=color,
            fill_opacity=0.07,
        )
        text.move_to(box)
        chips.add(VGroup(box, text))
    return chips.arrange(RIGHT, buff=0.14)


class ChatGPTOutro(Scene):
    """Silent 7.7 s end slate matching the gacha video's visual system."""

    def construct(self) -> None:
        self.camera.background_color = BG
        self.add(notebook_grid())

        frame = RoundedRectangle(
            width=8.70,
            height=4.85,
            corner_radius=0.28,
            stroke_color=PANEL_EDGE,
            stroke_width=1.4,
            fill_color=PANEL,
            fill_opacity=0.80,
        )

        mark = (
            SVGMobject(str(CHATGPT_LINE_LOGO))
            .set_fill(opacity=0)
            .set_stroke(INK, width=2.8)
            .scale(0.86)
            .move_to(UP * 1.04)
        )
        wordmark = Text("ChatGPT", font=LATIN_FONT, color=INK).scale(0.73)
        wordmark.next_to(mark, DOWN, buff=0.30)

        divider = Line(LEFT * 2.20, RIGHT * 2.20, color=MINT, stroke_width=1.8, stroke_opacity=0.56)
        divider.next_to(wordmark, DOWN, buff=0.28)
        credit = cn("本片制作由 ChatGPT 完成", 0.32, INK).next_to(divider, DOWN, buff=0.28)
        scope = scope_chips().next_to(credit, DOWN, buff=0.25)
        footer = Text("Math Video Maker", font=LATIN_FONT, color=MUTED).scale(0.23)
        footer.move_to(frame.get_bottom() + UP * 0.28)

        slate = VGroup(frame, mark, wordmark, divider, credit, scope, footer)
        self.play(FadeIn(frame, shift=UP * 0.08), run_time=0.9)
        self.play(FadeIn(mark, shift=UP * 0.12), run_time=0.9)
        self.play(Write(wordmark), Create(divider), run_time=0.9)
        self.play(FadeIn(credit, shift=UP * 0.10), run_time=0.55)
        self.play(
            LaggedStart(*[FadeIn(chip, shift=UP * 0.05) for chip in scope], lag_ratio=0.22),
            run_time=0.95,
        )
        self.play(FadeIn(footer), run_time=0.50)
        self.wait(2.20)
        self.play(FadeOut(slate, shift=DOWN * 0.08), run_time=0.80)
