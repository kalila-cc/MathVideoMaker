from __future__ import annotations

from pathlib import Path

from manim import *


BG = "#06101A"
INK = "#F4FBFF"
MUTED = "#92A7B4"
ACCENT = "#26D9FF"
FONT = "Microsoft YaHei UI"
LATIN_FONT = "Times New Roman"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
CHATGPT_LINE_LOGO = PROJECT_ROOT / "assets" / "brand" / "chatgpt_logo_line.svg"


def cn(text: str, size: float = 0.36, color: str = INK) -> Text:
    return Text(text, font=FONT, t2f={"ChatGPT": LATIN_FONT}, color=color).scale(size)


class ChatGPTOutro(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG

        frame = RoundedRectangle(
            width=8.7,
            height=4.85,
            corner_radius=0.28,
            stroke_color="#274358",
            stroke_width=1.4,
            fill_color="#081522",
            fill_opacity=0.72,
        )

        mark = SVGMobject(str(CHATGPT_LINE_LOGO)).set_fill(opacity=0).set_stroke(INK, width=2.8).scale(0.92)
        mark.move_to(UP * 0.9)
        wordmark = Text("ChatGPT", font=LATIN_FONT, color=INK).scale(0.76).next_to(mark, DOWN, buff=0.36)

        line = Line(LEFT * 2.15, RIGHT * 2.15, color=ACCENT, stroke_width=1.8, stroke_opacity=0.50)
        line.next_to(wordmark, DOWN, buff=0.32)
        credit = cn("视频完全由 ChatGPT 完成制作", 0.38, INK).next_to(line, DOWN, buff=0.34)
        sub = cn("从选题、推导、动画到配音合成", 0.22, MUTED).next_to(credit, DOWN, buff=0.25)

        content = VGroup(mark, wordmark, line, credit, sub)
        footer = Text("Math Video Maker", font=LATIN_FONT, color=MUTED).scale(0.23)
        footer.move_to(frame.get_bottom() + UP * 0.28)

        self.play(
            FadeIn(frame, shift=UP * 0.08),
            run_time=0.9,
        )
        self.play(FadeIn(mark, shift=UP * 0.12), run_time=0.9)
        self.play(Write(wordmark), Create(line), run_time=0.9)
        self.play(FadeIn(credit, shift=UP * 0.12), FadeIn(sub, shift=UP * 0.1), run_time=1.0)
        self.play(FadeIn(footer), run_time=0.5)
        self.wait(2.7)
        self.play(FadeOut(VGroup(frame, content, footer), shift=DOWN * 0.08), run_time=0.8)
