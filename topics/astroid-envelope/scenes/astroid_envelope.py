from __future__ import annotations

import numpy as np
from manim import *


FONT = "Microsoft YaHei"
BG = "#08111F"
INK = "#F8F4E3"
MUTED = "#A7B0BE"
AMBER = "#F6B73C"
MINT = "#5EEAD4"
ROSE = "#FF5C7A"
BLUE = "#7DD3FC"


class LadderAstroidEnvelope(Scene):
    def construct(self) -> None:
        self.camera.background_color = BG
        length = 4.6
        scale = 1.15
        origin = LEFT * 5.25 + DOWN * 2.55

        def p(x: float, y: float) -> np.ndarray:
            return origin + scale * np.array([x, y, 0.0])

        def ladder(theta: float, color: str = INK, opacity: float = 1.0, width: float = 6) -> Line:
            return Line(
                p(length * np.cos(theta), 0),
                p(0, length * np.sin(theta)),
                color=color,
                stroke_width=width,
                stroke_opacity=opacity,
            )

        floor = Line(p(0, 0), p(length * 1.08, 0), color=BLUE, stroke_width=5)
        wall = Line(p(0, 0), p(0, length * 1.08), color=BLUE, stroke_width=5)
        corner = VGroup(floor, wall)
        floor_label = Text("地面", font=FONT, color=MUTED).scale(0.34).next_to(floor, DOWN)
        wall_label = Text("墙", font=FONT, color=MUTED).scale(0.34).next_to(wall, LEFT)

        title = Text("一根靠墙滑落的棍子，会扫出什么边界？", font=FONT, color=INK)
        title.scale(0.55).to_edge(UP)
        hook = Text("答案不是圆弧，而是一条星形线。", font=FONT, color=AMBER)
        hook.scale(0.5).next_to(title, DOWN, buff=0.18)

        self.play(FadeIn(title, shift=DOWN * 0.2), FadeIn(hook, shift=DOWN * 0.2))
        self.play(Create(corner), FadeIn(floor_label), FadeIn(wall_label), run_time=1.2)

        theta = ValueTracker(1.42)
        moving_ladder = always_redraw(lambda: ladder(theta.get_value(), color=INK, width=8))
        end_a = always_redraw(
            lambda: Dot(p(length * np.cos(theta.get_value()), 0), color=AMBER, radius=0.07)
        )
        end_b = always_redraw(
            lambda: Dot(p(0, length * np.sin(theta.get_value())), color=MINT, radius=0.07)
        )
        end_labels = always_redraw(
            lambda: VGroup(
                Text("A", font=FONT, color=AMBER).scale(0.35).next_to(end_a, DOWN, buff=0.06),
                Text("B", font=FONT, color=MINT).scale(0.35).next_to(end_b, LEFT, buff=0.06),
            )
        )

        self.play(FadeIn(moving_ladder), FadeIn(end_a), FadeIn(end_b), FadeIn(end_labels))
        self.play(theta.animate.set_value(0.15), run_time=5.2, rate_func=smooth)
        self.wait(0.6)

        trace_thetas = np.linspace(0.18, 1.40, 36)
        trace_lines = VGroup(
            *[ladder(t, color=BLUE, opacity=0.16, width=2.4) for t in trace_thetas]
        )
        sweep_note = Text("每一根浅蓝线，都是棍子某一瞬间的位置。", font=FONT, color=MUTED)
        sweep_note.scale(0.36).to_edge(DOWN).shift(RIGHT * 0.5)
        self.play(FadeOut(hook), FadeIn(sweep_note, shift=UP * 0.2))
        self.play(LaggedStart(*[Create(line) for line in trace_lines], lag_ratio=0.035), run_time=2.8)

        astroid = ParametricFunction(
            lambda t: p(length * np.cos(t) ** 3, length * np.sin(t) ** 3),
            t_range=[0, PI / 2],
            color=AMBER,
            stroke_width=8,
        )
        astroid_label = Text("所有位置共同“擦”出来的边界", font=FONT, color=AMBER)
        astroid_label.scale(0.38).next_to(astroid, UR, buff=0.18)
        self.play(Create(astroid), FadeIn(astroid_label, shift=LEFT * 0.2), run_time=2.2)
        self.play(Circumscribe(astroid, color=AMBER, time_width=0.8), run_time=1.3)
        self.wait(1.6)

        formula_panel = RoundedRectangle(
            width=5.7,
            height=6.25,
            corner_radius=0.22,
            stroke_color="#314054",
            fill_color="#0D1727",
            fill_opacity=0.92,
        ).to_edge(RIGHT, buff=0.34).shift(DOWN * 0.2)
        panel_title = Text("把画面翻译成微分", font=FONT, color=INK)
        panel_title.scale(0.46).move_to(formula_panel.get_top() + DOWN * 0.38)

        self.play(FadeIn(formula_panel, shift=LEFT * 0.25), FadeIn(panel_title))

        step1 = Text("1. 固定棍长 L，用角度 θ 表示位置", font=FONT, color=MUTED).scale(0.31)
        step1.next_to(panel_title, DOWN, buff=0.32).align_to(formula_panel, LEFT).shift(RIGHT * 0.35)
        endpoints = MathTex(
            r"A=(L\cos\theta,0),\quad B=(0,L\sin\theta)",
            color=INK,
        ).scale(0.58).next_to(step1, DOWN, buff=0.22).align_to(step1, LEFT)
        line_eq = MathTex(
            r"F(x,y,\theta)=x\sec\theta+y\csc\theta-L=0",
            color=INK,
        ).scale(0.58).next_to(endpoints, DOWN, buff=0.28).align_to(step1, LEFT)

        self.play(FadeIn(step1), Write(endpoints), run_time=1.8)
        self.play(Write(line_eq), run_time=1.7)
        self.wait(3.0)

        step2 = Text("2. 边界点：这一瞬间刚好被“擦到”", font=FONT, color=MUTED).scale(0.31)
        step2.next_to(line_eq, DOWN, buff=0.42).align_to(step1, LEFT)
        derivative = MathTex(
            r"\frac{\partial F}{\partial\theta}=x\sec\theta\tan\theta-y\csc\theta\cot\theta=0",
            color=INK,
        ).scale(0.49).next_to(step2, DOWN, buff=0.22).align_to(step1, LEFT)
        condition_note = Text("直觉：相邻两根棍子在这里几乎重合，边界才会留下来。", font=FONT, color=AMBER)
        condition_note.scale(0.28).next_to(derivative, DOWN, buff=0.2).align_to(step1, LEFT)

        tangent_dot = Dot(p(length * np.cos(0.78) ** 3, length * np.sin(0.78) ** 3), color=ROSE)
        tangent_line = ladder(0.78, color=ROSE, opacity=0.95, width=5)
        self.play(FadeIn(step2), Create(tangent_line), FadeIn(tangent_dot), run_time=1.2)
        self.play(Write(derivative), FadeIn(condition_note), run_time=2.2)
        self.wait(3.0)

        step3 = Text("3. 联立两条条件，得到边界参数式", font=FONT, color=MUTED).scale(0.31)
        step3.next_to(condition_note, DOWN, buff=0.4).align_to(step1, LEFT)
        param_eq = MathTex(
            r"x=L\cos^3\theta,\qquad y=L\sin^3\theta",
            color=MINT,
        ).scale(0.64).next_to(step3, DOWN, buff=0.22).align_to(step1, LEFT)
        eliminate = MathTex(
            r"x^{2/3}+y^{2/3}=L^{2/3}",
            color=AMBER,
        ).scale(0.78).next_to(param_eq, DOWN, buff=0.28).align_to(step1, LEFT)
        full_note = Text("这就是第一象限里的星形线。", font=FONT, color=AMBER)
        full_note.scale(0.32).next_to(eliminate, DOWN, buff=0.18).align_to(step1, LEFT)

        self.play(FadeIn(step3), Write(param_eq), run_time=1.8)
        self.play(TransformFromCopy(param_eq, eliminate), FadeIn(full_note), run_time=2.0)
        self.play(Circumscribe(eliminate, color=AMBER, time_width=0.75), run_time=1.2)
        self.wait(3.0)

        recap = VGroup(
            Text("一根棍子滑落：看起来是普通运动", font=FONT, color=INK).scale(0.38),
            Text("很多位置叠在一起：出现一条包络线", font=FONT, color=INK).scale(0.38),
            Text("用微分找“刚好擦过”的点：星形线出现", font=FONT, color=INK).scale(0.38),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        recap_bg = RoundedRectangle(
            width=6.1,
            height=2.0,
            corner_radius=0.2,
            stroke_color=AMBER,
            fill_color="#101D2E",
            fill_opacity=0.95,
        )
        recap_group = VGroup(recap_bg, recap).to_edge(DOWN, buff=0.35).shift(RIGHT * 0.2)
        recap.move_to(recap_bg).shift(RIGHT * 0.06)

        self.play(FadeOut(sweep_note), FadeIn(recap_group, shift=UP * 0.25), run_time=1.2)
        self.play(
            astroid.animate.set_stroke(width=11),
            tangent_line.animate.set_opacity(0.25),
            run_time=1.0,
        )
        self.wait(22.0)
