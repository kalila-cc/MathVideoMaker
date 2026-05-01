from manim import *


class NoLatexSmokeTest(Scene):
    def construct(self):
        title = Text("中文数学动画工作流测试", font="Microsoft YaHei", color=WHITE)
        title.scale(0.65).to_edge(UP)

        equation = Text("a² + b² = c²", font="Microsoft YaHei", color="#FFD166")
        equation.scale(1.2)

        square_a = Square(side_length=1.4, color="#FF9F1C", fill_opacity=0.35)
        square_b = Square(side_length=1.9, color="#2EC4B6", fill_opacity=0.35)
        square_c = Square(side_length=2.4, color="#E71D36", fill_opacity=0.22)

        squares = VGroup(square_a, square_b, square_c).arrange(RIGHT, buff=0.7).shift(DOWN * 0.6)
        labels = VGroup(
            Text("a²", font="Microsoft YaHei", color="#FFBF69").scale(0.45).move_to(square_a),
            Text("b²", font="Microsoft YaHei", color="#9FFFE0").scale(0.45).move_to(square_b),
            Text("c²", font="Microsoft YaHei", color="#FF8FA3").scale(0.45).move_to(square_c),
        )

        caption = Text("如果面积能重新拼合，公式就不只是符号。", font="Microsoft YaHei", color=GREY_B)
        caption.scale(0.45).to_edge(DOWN)

        self.play(FadeIn(title, shift=DOWN * 0.2))
        self.play(Write(equation))
        self.play(LaggedStart(*[GrowFromCenter(s) for s in squares], lag_ratio=0.15))
        self.play(FadeIn(labels), FadeIn(caption, shift=UP * 0.2))
        self.wait(1.2)
