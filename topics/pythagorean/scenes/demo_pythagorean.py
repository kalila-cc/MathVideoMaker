from manim import *


class PythagoreanDemo(Scene):
    def construct(self):
        title = Text("勾股定理：面积为什么相等？", font="Microsoft YaHei", color=WHITE)
        title.scale(0.7).to_edge(UP)

        axes = NumberPlane(
            x_range=[-1, 5, 1],
            y_range=[-1, 4, 1],
            background_line_style={"stroke_color": BLUE_E, "stroke_width": 1, "stroke_opacity": 0.35},
        ).scale(0.8).shift(DOWN * 0.3)

        a = 4
        b = 3
        triangle = Polygon(
            axes.c2p(0, 0),
            axes.c2p(a, 0),
            axes.c2p(a, b),
            color=WHITE,
            fill_color="#2EC4B6",
            fill_opacity=0.28,
        )

        right_angle = RightAngle(
            Line(axes.c2p(a, 0), axes.c2p(0, 0)),
            Line(axes.c2p(a, 0), axes.c2p(a, b)),
            length=0.25,
            color=YELLOW,
        )

        labels = VGroup(
            Text("a", font="Microsoft YaHei", color="#FFBF69").scale(0.55).next_to(
                Line(axes.c2p(0, 0), axes.c2p(a, 0)), DOWN
            ),
            Text("b", font="Microsoft YaHei", color="#FFBF69").scale(0.55).next_to(
                Line(axes.c2p(a, 0), axes.c2p(a, b)), RIGHT
            ),
            Text("c", font="Microsoft YaHei", color="#FFBF69").scale(0.55).next_to(
                Line(axes.c2p(0, 0), axes.c2p(a, b)), LEFT
            ),
        )

        formula = MathTex(r"a^2+b^2=c^2", color="#FFD166").scale(1.25).to_edge(DOWN)
        note = Text("把两条直角边的面积贡献合起来，正好等于斜边的平方。", font="Microsoft YaHei", color=GREY_B)
        note.scale(0.45).next_to(formula, UP)

        self.play(FadeIn(title, shift=DOWN * 0.2))
        self.play(Create(axes), run_time=1.2)
        self.play(DrawBorderThenFill(triangle), Create(right_angle), FadeIn(labels), run_time=1.5)
        self.play(Write(formula), FadeIn(note, shift=UP * 0.2))
        self.play(Circumscribe(formula, color=YELLOW), run_time=1.2)
        self.wait(1.5)
