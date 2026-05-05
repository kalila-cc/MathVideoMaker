from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import numpy as np
from manim import *


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SMILEY_FONT_FILE = PROJECT_ROOT / "assets" / "fonts" / "SmileySans-Oblique.ttf"
FONT = "Smiley Sans"
LATIN_FONT = "Times New Roman"

BG = "#07111F"
INK = "#F8F4E3"
MUTED = "#AAB4C2"
BLUE = "#7DD3FC"
AMBER = "#F6B73C"
MINT = "#5EEAD4"
ROSE = "#FF5C7A"
VIOLET = "#A78BFA"
PANEL = "#0D1727"
GRID_COLOR = "#8FA8D8"

PANEL_TITLE_SIZE = 0.42
PANEL_BODY_SIZE = 0.34
PANEL_NOTE_SIZE = 0.34
PANEL_FORMULA_SIZE = 0.66
PANEL_FORMULA_LARGE_SIZE = 0.72
PANEL_FORMULA_SMALL_SIZE = 0.54

LATIN_PATTERN = re.compile(r"[A-Za-z0-9_.:/,+#()-]+")

TIMES_TEX_TEMPLATE = TexTemplate()
TIMES_TEX_TEMPLATE.add_to_preamble(r"\usepackage{mathptmx}")
MathTex.set_default(tex_template=TIMES_TEX_TEMPLATE)

TARGET_DURATIONS = {
    "StoryHook": 33.18,
    "AreaLaw": 117.60,
    "OrbitEquation": 76.23,
    "ConstantsEllipse": 103.65,
    "VelocityLab": 38.69,
    "PlanetaryPayoff": 31.41,
}


def cn(text: str, size: float = 0.36, color: str = INK) -> Text:
    with register_font(SMILEY_FONT_FILE):
        return Text(text, font=FONT, slant=OBLIQUE, color=color).scale(size)


def latin_font_map(text: str) -> dict[str, str]:
    return {token: LATIN_FONT for token in LATIN_PATTERN.findall(text)}


def finish_to(scene: Scene, target: float) -> None:
    remaining = target - scene.time
    if remaining > 0:
        scene.wait(remaining)


def notebook_grid(spacing: float = 0.48) -> VGroup:
    width = config.frame_width + spacing
    height = config.frame_height + spacing
    xs = np.arange(-width / 2, width / 2 + spacing, spacing)
    ys = np.arange(-height / 2, height / 2 + spacing, spacing)
    grid = VGroup(
        *[
            Line(DOWN * height / 2 + RIGHT * x, UP * height / 2 + RIGHT * x, color=GRID_COLOR, stroke_width=1.6)
            for x in xs
        ],
        *[
            Line(LEFT * width / 2 + UP * y, RIGHT * width / 2 + UP * y, color=GRID_COLOR, stroke_width=1.6)
            for y in ys
        ],
    )
    grid.set_opacity(0.155)
    grid.set_z_index(-100)
    return grid


def set_scene_background(scene: Scene) -> None:
    scene.camera.background_color = BG
    scene.add(notebook_grid())


def scene_title(title: str, subtitle: str | None = None) -> VGroup:
    heading = cn(title, 0.52).to_edge(UP, buff=0.34)
    if subtitle is None:
        return VGroup(heading)
    sub = cn(subtitle, 0.30, MUTED).next_to(heading, DOWN, buff=0.10)
    return VGroup(heading, sub)


def formula_panel(width: float = 5.9, height: float = 5.3) -> RoundedRectangle:
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.18,
        stroke_color="#2A3A50",
        stroke_width=1.4,
        fill_color=PANEL,
        fill_opacity=0.94,
    )


def fit_inside(mobject: Mobject, max_width: float | None = None, max_height: float | None = None) -> Mobject:
    if max_width is not None and mobject.width > max_width:
        mobject.scale_to_fit_width(max_width)
    if max_height is not None and mobject.height > max_height:
        mobject.scale_to_fit_height(max_height)
    return mobject


def label_box(text: str, color: str = INK, size: float = 0.28) -> VGroup:
    label = cn(text, size, color)
    box = RoundedRectangle(
        width=label.width + 0.34,
        height=label.height + 0.20,
        corner_radius=0.10,
        stroke_color="#314054",
        fill_color=PANEL,
        fill_opacity=0.88,
    ).move_to(label)
    return VGroup(box, label)


def symbol_row(symbol: str, desc: str, color: str = INK) -> VGroup:
    sym = MathTex(symbol, color=color).scale(0.48)
    text = cn(desc, PANEL_BODY_SIZE, MUTED)
    row = VGroup(sym, text).arrange(RIGHT, buff=0.12)
    return row


def sun(center: np.ndarray, radius: float = 0.16) -> VGroup:
    glow2 = Circle(radius=radius * 2.8, stroke_width=0, fill_color=AMBER, fill_opacity=0.08).move_to(center)
    glow1 = Circle(radius=radius * 1.8, stroke_width=0, fill_color=AMBER, fill_opacity=0.18).move_to(center)
    body = Dot(center, radius=radius, color=AMBER)
    return VGroup(glow2, glow1, body).set_z_index(4)


def planet(center: np.ndarray, radius: float = 0.07, color: str = BLUE) -> Dot:
    return Dot(center, radius=radius, color=color).set_z_index(5)


def rot2(vec: np.ndarray, angle: float) -> np.ndarray:
    c = np.cos(angle)
    s = np.sin(angle)
    return np.array([c * vec[0] - s * vec[1], s * vec[0] + c * vec[1], 0.0])


def orbit_point(theta: float, e: float = 0.55, p: float = 2.20, focus: np.ndarray = ORIGIN, scale: float = 0.85, rot: float = 0.0) -> np.ndarray:
    r = p / (1 + e * np.cos(theta))
    point = np.array([r * np.cos(theta), r * np.sin(theta), 0.0])
    return focus + scale * rot2(point, rot)


def gravity_geometry(
    point: np.ndarray,
    focus: np.ndarray,
    base: float = 0.28,
    amplitude: float = 0.70,
    reference: float = 1.25,
) -> tuple[np.ndarray, np.ndarray, float]:
    direction = focus - point
    distance = max(np.linalg.norm(direction), 1e-6)
    unit = direction / distance
    length = base + amplitude * np.clip((reference / distance) ** 2, 0.0, 1.0)
    return point, unit, length


def orbit_curve(
    e: float = 0.55,
    p: float = 2.20,
    focus: np.ndarray = ORIGIN,
    scale: float = 0.85,
    rot: float = 0.0,
    start: float = 0.0,
    end: float = TAU,
    color: str = AMBER,
    width: float = 5.0,
    opacity: float = 1.0,
    samples: int = 260,
) -> VMobject:
    values = np.linspace(start, end, samples)
    points = [orbit_point(t, e=e, p=p, focus=focus, scale=scale, rot=rot) for t in values]
    curve = VMobject()
    curve.set_points_smoothly(points)
    curve.set_fill(opacity=0)
    curve.set_stroke(color=color, width=width, opacity=opacity)
    return curve


def path_from_points(points: Iterable[np.ndarray], color: str, width: float = 4.0, opacity: float = 1.0) -> VMobject:
    pts = list(points)
    curve = VMobject()
    if len(pts) >= 3:
        curve.set_points_smoothly(pts)
    else:
        curve.set_points_as_corners(pts)
    curve.set_fill(opacity=0)
    curve.set_stroke(color=color, width=width, opacity=opacity)
    return curve


def sector_between(
    theta1: float,
    theta2: float,
    focus: np.ndarray,
    e: float = 0.55,
    p: float = 2.20,
    scale: float = 0.85,
    rot: float = 0.0,
    color: str = BLUE,
    opacity: float = 0.22,
) -> Polygon:
    values = np.linspace(theta1, theta2, 26)
    points = [focus] + [orbit_point(t, e=e, p=p, focus=focus, scale=scale, rot=rot) for t in values]
    sector = Polygon(*points, stroke_width=1.2, stroke_color=color, fill_color=color, fill_opacity=opacity)
    sector.set_z_index(0)
    return sector


def eccentric_anomaly_from_mean(mean_anomaly: float, e: float) -> float:
    m = mean_anomaly
    estimate = m if e < 0.8 else PI
    for _ in range(12):
        estimate -= (estimate - e * np.sin(estimate) - m) / (1 - e * np.cos(estimate))
    return estimate


def true_anomaly_from_mean(mean_anomaly: float, e: float) -> float:
    e_anom = eccentric_anomaly_from_mean(mean_anomaly, e)
    return 2 * np.arctan2(np.sqrt(1 + e) * np.sin(e_anom / 2), np.sqrt(1 - e) * np.cos(e_anom / 2))


def simulate_orbit(vy: float, r0: float = 2.0, k: float = 1.0, dt: float = 0.018, steps: int = 1600) -> list[np.ndarray]:
    pos = np.array([r0, 0.0], dtype=float)
    vel = np.array([0.0, vy], dtype=float)
    pts: list[np.ndarray] = []
    for _ in range(steps):
        radius = float(np.linalg.norm(pos))
        if radius < 0.18:
            pts.append(np.array([pos[0], pos[1], 0.0]))
            break
        pts.append(np.array([pos[0], pos[1], 0.0]))
        acc = -k * pos / radius**3
        vel_half = vel + 0.5 * dt * acc
        pos = pos + dt * vel_half
        radius_new = float(np.linalg.norm(pos))
        acc_new = -k * pos / max(radius_new, 1e-6) ** 3
        vel = vel_half + 0.5 * dt * acc_new
        if np.linalg.norm(pos) > 5.4 and len(pts) > 160:
            break
    return pts


def transform_sim_points(points: list[np.ndarray], focus: np.ndarray, scale: float = 1.05, rot: float = 0.0) -> list[np.ndarray]:
    return [focus + scale * rot2(point, rot) for point in points]


def polar_axes(focus: np.ndarray, length: float = 4.6) -> VGroup:
    axis = Line(focus + LEFT * 0.15, focus + RIGHT * length, color="#3C5068", stroke_width=3)
    axis_label = cn("起始方向", 0.23, MUTED).next_to(axis, DOWN, buff=0.08).align_to(axis, RIGHT)
    pole_label = MathTex("S", color=AMBER).scale(0.52).next_to(focus, DOWN + LEFT, buff=0.08)
    return VGroup(axis, axis_label, pole_label)


def cover_title(lines: list[str], target_width: float) -> VGroup:
    group = VGroup(*[cn(line, 1.0, INK) for line in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
    group.scale_to_fit_width(target_width)
    return group


class CoverFrame(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        focus = RIGHT * 4.35 + DOWN * 0.42
        e = 0.56
        p = 2.0
        scale = 0.84
        orbit = orbit_curve(focus=focus, e=e, p=p, scale=scale, width=10, color=AMBER)
        orbit_glow = orbit.copy().set_stroke(width=30, opacity=0.14)
        sun_obj = sun(focus, 0.19)

        marker_theta = 1.16
        marker = orbit_point(marker_theta, focus=focus, e=e, p=p, scale=scale)
        marker_next = orbit_point(marker_theta + 0.05, focus=focus, e=e, p=p, scale=scale)
        tangent = marker_next - marker
        tangent = tangent / np.linalg.norm(tangent)
        radius_line = DashedLine(focus, marker, color=BLUE, stroke_width=3.4, dash_length=0.11).set_opacity(0.62)
        velocity = Arrow(
            marker - tangent * 0.08,
            marker + tangent * 0.95,
            buff=0.03,
            color=MINT,
            stroke_width=7,
            max_tip_length_to_length_ratio=0.17,
        ).set_z_index(6)
        body = planet(marker, 0.095, BLUE)
        velocity_label = MathTex(r"\vec v_0", color=MINT).scale(0.58).next_to(velocity, UP, buff=0.08)

        title = cover_title(["行星轨道", "为什么偏偏", "是椭圆？"], 6.15).to_corner(UL, buff=0.44).shift(RIGHT * 0.10)
        subtitle = cn("位置 + 速度 + 太阳引力", 0.46, MUTED).next_to(title, DOWN, buff=0.20).align_to(title, LEFT)
        focus_note = label_box("太阳在焦点", AMBER, 0.30).next_to(sun_obj, DOWN, buff=0.30)
        self.add(orbit_glow, orbit, radius_line, sun_obj, body, velocity, velocity_label, title, subtitle, focus_note)
        self.wait(0.75)


class StoryHook(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("只给初始信息，轨道会怎样？", "已知：太阳、行星、初速度、指向太阳的加速度")
        focus = LEFT * 2.15 + DOWN * 0.22
        e = 0.45
        p = 2.20
        orbit = orbit_curve(focus=focus, e=e, p=p, scale=0.86, color=AMBER, width=6, opacity=0.95)
        ghost = orbit.copy().set_stroke(width=18, opacity=0.12)
        start = orbit_point(0.0, e=e, p=p, focus=focus, scale=0.86)
        tracker = ValueTracker(0.0)

        def current_story_point() -> np.ndarray:
            return orbit_point(tracker.get_value(), e=e, p=p, focus=focus, scale=0.86)

        def story_gravity_geometry() -> tuple[np.ndarray, np.ndarray, float]:
            point = current_story_point()
            to_sun = focus - point
            distance = max(np.linalg.norm(to_sun), 1e-6)
            direction = to_sun / distance
            length = 0.38 + 0.86 * np.clip((1.34 / distance) ** 2, 0.0, 1.0)
            return point, direction, length

        sun_obj = sun(focus)
        body = planet(start, 0.085, BLUE)
        s_label = MathTex("S", color=AMBER).scale(0.58).next_to(sun_obj, DOWN + LEFT, buff=0.08)
        p_label = MathTex("P", color=BLUE).scale(0.58).next_to(body, RIGHT, buff=0.08)
        sun_name = cn("太阳", 0.22, AMBER).move_to(focus + DOWN * 0.50 + RIGHT * 0.10)
        planet_name = cn("行星", 0.22, BLUE).set_z_index(7)
        planet_name.add_updater(lambda mob: mob.next_to(current_story_point(), DOWN + RIGHT, buff=0.08))
        radial_unit = (start - focus) / np.linalg.norm(start - focus)
        radial_normal = rotate_vector(radial_unit, PI / 2)
        r_line = DashedLine(
            focus - radial_normal * 0.15,
            start - radial_normal * 0.15,
            color=BLUE,
            stroke_width=3.2,
            stroke_opacity=0.68,
            dash_length=0.08,
        )
        r_label = MathTex(r"r_0", color=BLUE).scale(0.50).next_to(r_line, DOWN, buff=0.10)
        v_arrow = Arrow(start, start + UP * 1.25, buff=0.10, color=MINT, stroke_width=6, max_tip_length_to_length_ratio=0.18)
        v_label = MathTex(r"\vec v_0", color=MINT).scale(0.58).next_to(v_arrow, RIGHT, buff=0.08)
        f_arrow = Arrow(
            start + radial_normal * 0.16,
            focus + radial_normal * 0.16,
            buff=0.22,
            color=ROSE,
            stroke_width=5,
            max_tip_length_to_length_ratio=0.14,
        )
        f_label = cn("引力加速度", 0.25, ROSE).next_to(f_arrow, UP, buff=0.08)

        panel = formula_panel(5.55, 4.72).to_edge(RIGHT, buff=0.45).shift(DOWN * 0.25)
        panel_title = cn("当前已知信息", PANEL_TITLE_SIZE, MUTED)
        rows = VGroup(
            symbol_row("S", "太阳的位置", AMBER),
            symbol_row("P", "行星的位置", BLUE),
            symbol_row(r"\vec v_0", "初速度：方向和快慢", MINT),
            symbol_row(r"\vec a", "加速度：指向太阳", ROSE),
        ).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        note = cn("初速度一变，后面的轨道也会变。", PANEL_NOTE_SIZE, AMBER)
        stack = VGroup(panel_title, rows, note).arrange(DOWN, buff=0.34, aligned_edge=LEFT)
        fit_inside(stack, max_width=4.90, max_height=3.80)
        stack.move_to(panel)

        mover = always_redraw(lambda: planet(orbit_point(tracker.get_value(), e=e, p=p, focus=focus, scale=0.86), 0.075, BLUE))
        trail = always_redraw(
            lambda: orbit_curve(
                focus=focus,
                e=e,
                p=p,
                scale=0.86,
                start=0,
                end=max(0.02, tracker.get_value()),
                color=BLUE,
                width=5,
                opacity=0.88,
                samples=90,
            )
        )
        dynamic_force_arrow = always_redraw(
            lambda: Arrow(
                story_gravity_geometry()[0],
                story_gravity_geometry()[0] + story_gravity_geometry()[1] * story_gravity_geometry()[2],
                buff=0.09,
                color=ROSE,
                stroke_width=5,
                max_tip_length_to_length_ratio=0.18,
            ).set_z_index(6)
        )
        dynamic_force_label = cn("加速度", 0.20, ROSE).set_z_index(7)
        dynamic_force_label.add_updater(
            lambda mob: mob.next_to(
                story_gravity_geometry()[0] + story_gravity_geometry()[1] * story_gravity_geometry()[2],
                UP,
                buff=0.04,
            )
        )

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.9)
        self.play(FadeIn(sun_obj), FadeIn(s_label), FadeIn(sun_name), FadeIn(body), FadeIn(p_label), FadeIn(planet_name), Create(r_line), FadeIn(r_label), run_time=1.5)
        self.play(GrowArrow(v_arrow), FadeIn(v_label), GrowArrow(f_arrow), FadeIn(f_label), run_time=1.4)
        self.play(FadeIn(panel), FadeIn(stack, shift=LEFT * 0.12), run_time=1.2)
        self.add(trail, mover, dynamic_force_arrow, dynamic_force_label)
        self.remove(body, p_label, f_arrow, f_label)
        self.play(tracker.animate.set_value(TAU * 0.82), run_time=22.6, rate_func=smooth)
        warning = label_box("初速度一变，轨道也会变", ROSE, 0.30).to_edge(DOWN, buff=0.50)
        self.play(FadeIn(warning, shift=UP * 0.12), run_time=0.8)
        self.play(tracker.animate.set_value(TAU), run_time=4.2, rate_func=smooth)
        finish_to(self, TARGET_DURATIONS["StoryHook"])


class AreaLaw(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("先推出面积变化率恒定", "先看加速度方向，暂不使用反平方大小")
        focus = LEFT * 1.85 + DOWN * 0.12
        e = 0.45
        p = 2.22
        scale = 0.82
        orbit = orbit_curve(focus=focus, e=e, p=p, scale=scale, width=5, opacity=0.88)
        orbit.set_z_index(2)
        sun_obj = sun(focus, 0.15)
        s_label = MathTex("S", color=AMBER).scale(0.52).next_to(sun_obj, DOWN + LEFT, buff=0.08)
        sun_name = cn("太阳", 0.21, AMBER).move_to(focus + DOWN * 0.45 + RIGHT * 0.08)

        mean_values = np.linspace(0.10, TAU + 0.10, 6)
        theta_values = list(np.unwrap([true_anomaly_from_mean(m, e) for m in mean_values]))
        sweep_run_times = (19.4, 12.2, 6.2)
        sweep_mean_rate = float((mean_values[4] - mean_values[0]) / sum(sweep_run_times))
        motion_mean_1 = float(mean_values[0] + sweep_mean_rate * sweep_run_times[0])
        motion_mean_2 = float(mean_values[0] + sweep_mean_rate * (sweep_run_times[0] + sweep_run_times[1]))
        sectors = VGroup(
            *[
                sector_between(theta_values[i], theta_values[i + 1], focus, e=e, p=p, scale=scale, color=[BLUE, MINT, VIOLET, ROSE, BLUE][i], opacity=0.18)
                for i in range(5)
            ]
        )
        radius_lines = VGroup(
            *[
                Line(focus, orbit_point(theta, e=e, p=p, focus=focus, scale=scale), color="#3C5068", stroke_width=2.4, stroke_opacity=0.55)
                for theta in theta_values[:-1]
            ]
        )
        radius_lines.set_z_index(1)
        sweep_mean = ValueTracker(float(mean_values[0]))

        def sweep_theta() -> float:
            mean = sweep_mean.get_value()
            turns = np.floor((mean - mean_values[0]) / TAU)
            local_mean = mean - turns * TAU
            theta = true_anomaly_from_mean(local_mean, e)
            if theta < theta_values[0] - 0.10:
                theta += TAU
            return theta + turns * TAU

        def tangent_unit(theta: float) -> np.ndarray:
            eps = 0.015
            tangent = orbit_point(theta + eps, e=e, p=p, focus=focus, scale=scale) - orbit_point(theta - eps, e=e, p=p, focus=focus, scale=scale)
            return tangent / max(np.linalg.norm(tangent), 1e-6)

        def velocity_arrow_geometry() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
            theta = sweep_theta()
            point = orbit_point(theta, e=e, p=p, focus=focus, scale=scale)
            tangent = tangent_unit(theta)
            radial = point - focus
            distance = max(np.linalg.norm(radial), 1e-6)
            radial = radial / distance
            length = 0.56 + 0.66 * np.clip((1.35 / distance) ** 1.2, 0.0, 1.0)
            start = point + radial * 0.18 - tangent * 0.15
            end = start + tangent * length
            return point, tangent, radial, end

        def transverse_arrow_geometry() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
            theta = sweep_theta()
            point = orbit_point(theta, e=e, p=p, focus=focus, scale=scale)
            radial = point - focus
            radial_unit = radial / max(np.linalg.norm(radial), 1e-6)
            transverse = rotate_vector(radial_unit, PI / 2)
            if np.dot(transverse, tangent_unit(theta)) < 0:
                transverse = -transverse
            start = point - radial_unit * 0.42 - transverse * 0.10
            end = start + transverse * 0.78
            return start, end, transverse

        def sweep_gravity_geometry() -> tuple[np.ndarray, np.ndarray, float]:
            point = orbit_point(sweep_theta(), e=e, p=p, focus=focus, scale=scale)
            to_sun = focus - point
            distance = max(np.linalg.norm(to_sun), 1e-6)
            direction = to_sun / distance
            length = 0.34 + 0.82 * np.clip((1.26 / distance) ** 2, 0.0, 1.0)
            return point, direction, length

        def sweep_point() -> np.ndarray:
            return orbit_point(sweep_theta(), e=e, p=p, focus=focus, scale=scale)

        def sweep_r_label_position() -> np.ndarray:
            radial = sweep_point() - focus
            unit = radial / max(np.linalg.norm(radial), 1e-6)
            normal = rotate_vector(unit, PI / 2)
            return focus + radial * 0.54 + normal * 0.18

        sweep_sector = always_redraw(
            lambda: sector_between(
                theta_values[0],
                max(theta_values[0] + 0.01, sweep_theta()),
                focus,
                e=e,
                p=p,
                scale=scale,
                color=MINT,
                opacity=0.16,
            )
        )
        sweep_radius = always_redraw(
            lambda: Line(
                focus,
                sweep_point(),
                color=BLUE,
                stroke_width=3.3,
                stroke_opacity=0.88,
            ).set_z_index(3)
        )
        sweep_r_label = MathTex(r"\vec r", color=BLUE).scale(0.58).set_z_index(7)
        sweep_r_label.add_background_rectangle(color=BG, opacity=0.78, buff=0.035)
        sweep_r_label.add_updater(lambda mob: mob.move_to(sweep_r_label_position()))
        sweep_planet = always_redraw(lambda: planet(sweep_point(), 0.065, MINT))
        sweep_planet_name = cn("行星", 0.21, MINT).set_z_index(7)
        sweep_planet_name.add_updater(
            lambda mob: mob.next_to(sweep_point(), DOWN + RIGHT, buff=0.07)
        )
        sweep_gravity_arrow = always_redraw(
            lambda: Arrow(
                sweep_gravity_geometry()[0],
                sweep_gravity_geometry()[0] + sweep_gravity_geometry()[1] * sweep_gravity_geometry()[2],
                buff=0.08,
                color=ROSE,
                stroke_width=5,
                max_tip_length_to_length_ratio=0.18,
            ).set_z_index(6)
        )
        sweep_gravity_label = MathTex(r"\vec a", color=ROSE).scale(0.48).set_z_index(7)
        sweep_gravity_label.add_updater(
            lambda mob: mob.move_to(
                sweep_gravity_geometry()[0] + sweep_gravity_geometry()[1] * sweep_gravity_geometry()[2] + UP * 0.12
            )
        )
        v_arrow = always_redraw(
            lambda: Arrow(
                velocity_arrow_geometry()[0] + velocity_arrow_geometry()[2] * 0.18 - velocity_arrow_geometry()[1] * 0.15,
                velocity_arrow_geometry()[3],
                buff=0.03,
                color=MINT,
                stroke_width=5,
                max_tip_length_to_length_ratio=0.18,
            ).set_z_index(6)
        )
        v_label = MathTex(r"\vec v", color=MINT).scale(0.52).set_z_index(7)
        v_label.add_updater(
            lambda mob: mob.move_to(
                velocity_arrow_geometry()[3] + velocity_arrow_geometry()[1] * 0.15 + velocity_arrow_geometry()[2] * 0.14
            )
        )
        vt_arrow = always_redraw(
            lambda: Arrow(
                transverse_arrow_geometry()[0],
                transverse_arrow_geometry()[1],
                buff=0.03,
                color=VIOLET,
                stroke_width=4.6,
                max_tip_length_to_length_ratio=0.18,
            ).set_z_index(7)
        )
        vt_label = MathTex(r"v_t", color=VIOLET).scale(0.46).set_z_index(8)
        vt_label.add_background_rectangle(color=BG, opacity=0.78, buff=0.035)
        vt_label.add_updater(
            lambda mob: mob.move_to(transverse_arrow_geometry()[1] + transverse_arrow_geometry()[2] * 0.17 + UP * 0.18)
        )
        dt_labels = VGroup(
            *[
                cn(r"同样的 Δt", 0.21, MUTED).move_to(
                    (focus + orbit_point((theta_values[i] + theta_values[i + 1]) / 2, e=e, p=p, focus=focus, scale=scale)) / 2
                )
                for i in range(3)
            ]
        )

        panel = formula_panel(5.85, 5.55).to_edge(RIGHT, buff=0.34).shift(DOWN * 0.06)

        step1_title = cn("同线方向让叉积为零", PANEL_TITLE_SIZE, MUTED)
        step1_formula = MathTex(r"\vec r \times \vec a = 0", color=AMBER).scale(PANEL_FORMULA_LARGE_SIZE)
        step1_note = cn("这里只需要加速度指向太阳", PANEL_NOTE_SIZE, MUTED)
        step1 = VGroup(step1_title, step1_formula, step1_note).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        fit_inside(step1, max_width=4.80)
        step1.move_to(panel)

        key_label = cn("已得到", 0.23, MUTED)
        step2_prev = MathTex(r"\vec r \times \vec a = 0", color=AMBER).scale(0.50)
        key_strip = VGroup(key_label, step2_prev).arrange(RIGHT, buff=0.14)
        key_strip.move_to(panel.get_top() + DOWN * 0.48)

        work_center = panel.get_center() + DOWN * 0.34

        step2_title = cn("检查半径×速度是否变化", PANEL_TITLE_SIZE, MUTED)
        step2_main = MathTex(
            r"\frac{d}{dt}(\vec r\times\vec v)"
            r"=\frac{d\vec r}{dt}\times\vec v"
            r"+\vec r\times\frac{d\vec v}{dt}",
            color=INK,
        ).scale(0.46)
        step2_sub = MathTex(
            r"\frac{d\vec r}{dt}=\vec v,\qquad \frac{d\vec v}{dt}=\vec a",
            color=BLUE,
        ).scale(PANEL_FORMULA_SMALL_SIZE)
        step2_note = cn("这是乘积求导法则", PANEL_NOTE_SIZE, MUTED)
        step2 = VGroup(step2_title, step2_main, step2_sub, step2_note).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        fit_inside(step2, max_width=5.08, max_height=4.05)
        step2.move_to(work_center)

        step3_title = cn("代入速度和加速度", PANEL_TITLE_SIZE, MUTED)
        step3_prev = MathTex(
            r"\frac{d}{dt}(\vec r\times\vec v)"
            r"=\frac{d\vec r}{dt}\times\vec v"
            r"+\vec r\times\frac{d\vec v}{dt}",
            color=INK,
        ).scale(0.40)
        step3_mid = MathTex(
            r"=\vec v\times\vec v+\vec r\times\vec a",
            color=BLUE,
        ).scale(PANEL_FORMULA_SIZE)
        step3_final = MathTex(
            r"\frac{d}{dt}(\vec r\times\vec v)=\vec r\times\vec a=0",
            color=AMBER,
        ).scale(PANEL_FORMULA_SMALL_SIZE)
        step3_note = cn("因此这个量保持不变", PANEL_NOTE_SIZE, AMBER)
        step3 = VGroup(step3_title, step3_prev, step3_mid, step3_final, step3_note).arrange(DOWN, buff=0.20, aligned_edge=LEFT)
        fit_inside(step3, max_width=5.06, max_height=4.10)
        step3.move_to(work_center)

        bridge_title = cn("同一个守恒量，换成极坐标", PANEL_TITLE_SIZE, MUTED)
        bridge_prev = MathTex(r"\vec r\times\vec v=\mathrm{constant}", color=AMBER).scale(PANEL_FORMULA_SMALL_SIZE)
        bridge_mag = MathTex(r"|\vec r\times\vec v|=r\,v_t", color=INK).scale(PANEL_FORMULA_SIZE)
        bridge_vt = MathTex(r"v_t=r\left(\frac{d\theta}{dt}\right)", color=BLUE).scale(PANEL_FORMULA_SMALL_SIZE)
        bridge_result = MathTex(
            r"|\vec r\times\vec v|=r^2\frac{d\theta}{dt}=\mathrm{constant}",
            color=AMBER,
        ).scale(0.48)
        bridge_note = cn("v_t：速度中垂直于半径的部分", PANEL_NOTE_SIZE, VIOLET)
        bridge = VGroup(bridge_title, bridge_prev, bridge_mag, bridge_vt, bridge_result, bridge_note).arrange(
            DOWN, buff=0.18, aligned_edge=LEFT
        )
        fit_inside(bridge, max_width=5.04, max_height=4.10)
        bridge.move_to(work_center)

        step4_title = cn("小扇形给出面积变化率", PANEL_TITLE_SIZE, MUTED)
        step4_prev = MathTex(r"r^2\frac{d\theta}{dt}=\mathrm{constant}", color=AMBER).scale(PANEL_FORMULA_SMALL_SIZE)
        step4_area = MathTex(r"dA\approx\frac12 r^2\,d\theta", color=INK).scale(PANEL_FORMULA_SIZE)
        step4_speed = MathTex(r"2\frac{dA}{dt}=r^2\frac{d\theta}{dt}", color=BLUE).scale(PANEL_FORMULA_SMALL_SIZE)
        step4_h = MathTex(r"h\equiv 2\frac{dA}{dt}=r^2\frac{d\theta}{dt}=\mathrm{constant}", color=AMBER).scale(0.50)
        step4_note = cn("h：两倍面积变化率，不是新的物理规则", PANEL_NOTE_SIZE, AMBER)
        step4 = VGroup(step4_title, step4_prev, step4_area, step4_speed, step4_h, step4_note).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        fit_inside(step4, max_width=5.04, max_height=4.10)
        step4.move_to(work_center)
        bottom_badge_spot = LEFT * 4.95 + DOWN * 3.18
        law_badge = label_box("开普勒第二定律：面积定律", AMBER, 0.27)
        law_badge_note = cn("这里由加速度方向推出", 0.21, MUTED).next_to(law_badge, DOWN, buff=0.06)
        law_badge_group = VGroup(law_badge, law_badge_note).arrange(DOWN, buff=0.06).move_to(bottom_badge_spot)

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)
        self.play(FadeIn(sun_obj), FadeIn(s_label), FadeIn(sun_name), Create(orbit), run_time=1.1)
        self.play(
            FadeIn(sweep_sector),
            FadeIn(sweep_radius),
            FadeIn(sweep_r_label),
            FadeIn(sweep_planet),
            FadeIn(sweep_planet_name),
            FadeIn(sweep_gravity_arrow),
            FadeIn(sweep_gravity_label),
            FadeIn(v_arrow),
            FadeIn(v_label),
            run_time=1.4,
        )
        self.play(FadeIn(panel), FadeIn(step1), run_time=1.4)
        self.wait(0.6)
        self.play(
            sweep_mean.animate.set_value(motion_mean_1),
            run_time=sweep_run_times[0],
            rate_func=linear,
        )
        self.play(
            FadeOut(step1_title, shift=UP * 0.06),
            FadeOut(step1_note, shift=UP * 0.06),
            ReplacementTransform(step1_formula, step2_prev),
            FadeIn(key_label, shift=UP * 0.04),
            FadeIn(step2_title, shift=UP * 0.06),
            FadeIn(step2_main, shift=UP * 0.06),
            FadeIn(step2_sub, shift=UP * 0.06),
            FadeIn(step2_note, shift=UP * 0.06),
            run_time=1.3,
        )
        self.play(sweep_mean.animate.set_value(motion_mean_2), run_time=sweep_run_times[1], rate_func=linear)
        self.play(
            FadeOut(step2_title, shift=UP * 0.06),
            ReplacementTransform(step2_main, step3_prev),
            FadeOut(step2_sub, shift=UP * 0.06),
            FadeOut(step2_note, shift=UP * 0.06),
            FadeIn(step3_title, shift=UP * 0.06),
            FadeIn(step3_mid, shift=UP * 0.06),
            FadeIn(step3_final, shift=UP * 0.06),
            FadeIn(step3_note, shift=UP * 0.06),
            run_time=1.3,
        )
        self.play(sweep_mean.animate.set_value(float(mean_values[4])), run_time=sweep_run_times[2], rate_func=linear)
        self.play(
            FadeOut(step3_title, shift=UP * 0.06),
            FadeOut(step3_prev, shift=UP * 0.06),
            FadeOut(step3_mid, shift=UP * 0.06),
            ReplacementTransform(step3_final, bridge_prev),
            FadeOut(step3_note, shift=UP * 0.06),
            FadeOut(key_label, shift=UP * 0.04),
            FadeOut(step2_prev, shift=UP * 0.04),
            FadeIn(bridge_title, shift=UP * 0.06),
            FadeIn(bridge_mag, shift=UP * 0.06),
            FadeIn(bridge_note, shift=UP * 0.06),
            FadeIn(vt_arrow),
            FadeIn(vt_label),
            run_time=1.3,
        )
        self.wait(7.8)
        self.play(FadeIn(bridge_vt, shift=UP * 0.06), run_time=0.8)
        self.wait(10.0)
        self.play(FadeIn(bridge_result, shift=UP * 0.06), run_time=0.8)
        self.wait(4.2)
        self.play(
            FadeOut(bridge_title, shift=UP * 0.06),
            ReplacementTransform(bridge_result, step4_prev),
            FadeOut(bridge_prev, shift=UP * 0.06),
            FadeOut(bridge_mag, shift=UP * 0.06),
            FadeOut(bridge_vt, shift=UP * 0.06),
            FadeOut(bridge_note, shift=UP * 0.06),
            FadeOut(vt_arrow),
            FadeOut(vt_label),
            FadeIn(step4_title, shift=UP * 0.06),
            FadeIn(step4_area, shift=UP * 0.06),
            FadeIn(step4_speed, shift=UP * 0.06),
            FadeIn(dt_labels),
            run_time=1.3,
        )
        self.play(
            FadeOut(sweep_sector),
            FadeOut(sweep_radius),
            LaggedStart(*[FadeIn(sector) for sector in sectors], lag_ratio=0.12),
            Create(radius_lines),
            run_time=3.2,
        )
        self.play(sectors.animate.set_opacity(0.26), orbit.animate.set_stroke(width=7), run_time=1.1)
        self.wait(11.4)
        self.play(FadeIn(step4_h, shift=UP * 0.06), FadeIn(step4_note, shift=UP * 0.06), run_time=0.8)
        self.wait(13.7)
        self.play(FadeIn(law_badge_group, shift=UP * 0.12), run_time=0.8)
        self.wait(9.7)
        fast_label = label_box("近太阳：半径短，速度快", AMBER, 0.27).move_to(bottom_badge_spot + UP * 0.08)
        self.play(FadeOut(law_badge_group), FadeIn(fast_label, shift=UP * 0.12), run_time=0.8)
        finish_to(self, TARGET_DURATIONS["AreaLaw"])


class OrbitEquation(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("改问轨道形状", "加入平方反比大小，求 r 随 θ 的变化")
        focus = LEFT * 3.05 + DOWN * 0.18
        e = 0.45
        p = 2.20
        scale = 0.78
        sun_obj = sun(focus, 0.15)
        sun_name = cn("太阳", 0.22, AMBER).move_to(focus + DOWN * 0.46 + RIGHT * 0.08)
        axes = polar_axes(focus, 2.65)
        orbit = orbit_curve(focus=focus, e=e, p=p, scale=scale, width=5, opacity=0.90)
        tracker = ValueTracker(0.82)

        def current_point() -> np.ndarray:
            return orbit_point(tracker.get_value(), e=e, p=p, focus=focus, scale=scale)

        def orbit_gravity_geometry() -> tuple[np.ndarray, np.ndarray, float]:
            return gravity_geometry(current_point(), focus, base=0.32, amplitude=0.74, reference=1.30)

        radial = always_redraw(lambda: Line(focus, current_point(), color=BLUE, stroke_width=4))
        moving = always_redraw(lambda: planet(current_point(), 0.075, BLUE))
        planet_name = cn("行星", 0.21, BLUE).set_z_index(7)
        planet_name.add_updater(lambda mob: mob.next_to(current_point(), DOWN + RIGHT, buff=0.08))
        r_label = MathTex("r", color=BLUE).scale(0.55)
        r_label.add_updater(lambda mob: mob.move_to(focus + (current_point() - focus) * 0.55 + UP * 0.18))
        gravity_arrow = always_redraw(
            lambda: Arrow(
                orbit_gravity_geometry()[0],
                orbit_gravity_geometry()[0] + orbit_gravity_geometry()[1] * orbit_gravity_geometry()[2],
                buff=0.08,
                color=ROSE,
                stroke_width=4.4,
                max_tip_length_to_length_ratio=0.22,
            ).set_z_index(6)
        )
        gravity_label = MathTex(r"\vec a", color=ROSE).scale(0.42).set_z_index(7)
        gravity_label.add_updater(
            lambda mob: mob.move_to(orbit_gravity_geometry()[0] + orbit_gravity_geometry()[1] * orbit_gravity_geometry()[2] + UP * 0.12)
        )
        theta_arc = always_redraw(lambda: Arc(radius=0.58, start_angle=0, angle=tracker.get_value(), arc_center=focus, color=VIOLET, stroke_width=4))
        theta_label = MathTex(r"\theta", color=VIOLET).scale(0.55)
        theta_label.add_updater(
            lambda mob: mob.move_to(focus + 0.88 * np.array([np.cos(tracker.get_value() * 0.52), np.sin(tracker.get_value() * 0.52), 0.0]))
        )

        panel = formula_panel(6.00, 5.76).to_edge(RIGHT, buff=0.28).shift(DOWN * 0.12)

        key_title = cn("接下来要用的两条关系", 0.33, MUTED)
        key_h1 = MathTex(r"h=2\frac{dA}{dt}", color=AMBER).scale(0.58)
        key_h2 = MathTex(r"=r^2\frac{d\theta}{dt}", color=AMBER).scale(0.58)
        key_h_note = cn("两倍面积变化率，守恒", 0.24, MUTED)
        key_a = MathTex(r"|\vec a|=\frac{k}{r^2}", color=ROSE).scale(0.58)
        key_a_note = cn("k：平方反比关系的强度系数", 0.24, MUTED)
        key_h_col = VGroup(key_h1, key_h2, key_h_note).arrange(DOWN, buff=0.035, aligned_edge=LEFT)
        key_a_col = VGroup(key_a, key_a_note).arrange(DOWN, buff=0.05)
        key_group = VGroup(key_title, VGroup(key_h_col, key_a_col).arrange(RIGHT, buff=0.62, aligned_edge=UP)).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        fit_inside(key_group, max_width=5.20, max_height=1.72)
        key_group.move_to(panel.get_top() + DOWN * 0.94)

        step2_title = cn("直接使用径向加速度公式", PANEL_TITLE_SIZE, MUTED)
        step2a = MathTex(
            r"a_r=\frac{d^2r}{dt^2}-r\left(\frac{d\theta}{dt}\right)^2",
            color=INK,
        ).scale(PANEL_FORMULA_SMALL_SIZE)
        step2_note = cn("径向加速度公式；推导较长，此处不展开", PANEL_NOTE_SIZE, MUTED)
        step2_group = VGroup(step2_title, step2a, step2_note).arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        fit_inside(step2_group, max_width=5.00, max_height=4.60)
        step2_group.move_to(panel.get_center() + DOWN * 0.80)

        step3_title = cn("把两条关系代入径向公式", PANEL_TITLE_SIZE, MUTED)
        step3_source = MathTex(
            r"a_r=\frac{d^2r}{dt^2}-r\left(\frac{d\theta}{dt}\right)^2",
            color=INK,
        ).scale(0.46)
        step3a = MathTex(r"a_r=-\frac{k}{r^2}", color=ROSE).scale(PANEL_FORMULA_SIZE)
        step3b = MathTex(r"h=r^2\frac{d\theta}{dt}", color=AMBER).scale(PANEL_FORMULA_SMALL_SIZE)
        step3_inputs = VGroup(step3a, step3b).arrange(RIGHT, buff=0.42, aligned_edge=DOWN)
        step3c = MathTex(r"\left(\frac1r\right)''+\frac1r=\frac{k}{h^2}", color=BLUE).scale(PANEL_FORMULA_SMALL_SIZE)
        step3_note = cn("代数整理较长；撇号表示对 θ 求导", PANEL_NOTE_SIZE, MUTED)
        step3_group = VGroup(step3_title, step3_source, step3_inputs, step3c, step3_note).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        fit_inside(step3_group, max_width=5.15, max_height=3.72)
        step3_group.move_to(panel.get_center() + DOWN * 0.78)

        final_title = cn("把 1/r 记成 u", PANEL_TITLE_SIZE, MUTED)
        final_prev = MathTex(r"\left(\frac1r\right)''+\frac1r=\frac{k}{h^2}", color=BLUE).scale(PANEL_FORMULA_SMALL_SIZE)
        final_eq = MathTex(r"u=\frac1r", color=AMBER).scale(0.66)
        final_arrow = MathTex(r"\Downarrow", color=MUTED).scale(0.42)
        final_ode = MathTex(r"u''+u=\frac{k}{h^2}", color=BLUE).scale(0.72)
        final_note = cn("目的：改成标准微分方程形式", PANEL_NOTE_SIZE, MUTED)
        final_group = VGroup(final_title, final_prev, final_eq, final_arrow, final_ode, final_note).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        fit_inside(final_group, max_width=5.05, max_height=3.48)
        final_group.move_to(panel.get_center() + DOWN * 0.80)
        final_rest = VGroup(final_title, final_eq, final_arrow, final_ode, final_note)

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)
        self.play(FadeIn(sun_obj), FadeIn(sun_name), Create(axes), Create(orbit), run_time=1.2)
        self.add(radial, moving, r_label, theta_arc, theta_label, planet_name, gravity_arrow, gravity_label)
        self.play(tracker.animate.set_value(2.35), run_time=14.6, rate_func=smooth)
        self.play(FadeIn(panel), FadeIn(key_group), run_time=1.0)
        self.play(tracker.animate.set_value(4.55), run_time=17.2, rate_func=smooth)
        self.play(
            FadeIn(step2_group, shift=UP * 0.08),
            run_time=1.2,
        )
        self.play(tracker.animate.set_value(5.72), run_time=13.8, rate_func=smooth)
        self.play(FadeOut(step2_group, shift=UP * 0.08), FadeIn(step3_group, shift=UP * 0.08), run_time=1.2)
        self.play(tracker.animate.set_value(TAU + 0.82), run_time=14.4, rate_func=smooth)
        self.play(
            FadeOut(VGroup(step3_title, step3_source, step3_inputs, step3_note), shift=UP * 0.08),
            ReplacementTransform(step3c, final_prev),
            FadeIn(final_rest, shift=UP * 0.08),
            orbit.animate.set_stroke(width=7, color=AMBER),
            run_time=1.2,
        )
        finish_to(self, TARGET_DURATIONS["OrbitEquation"])


class ConstantsEllipse(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("从形状方程读出椭圆", "e 表示偏离圆的程度，由初速度决定")
        focus = LEFT * 3.00 + DOWN * 0.18
        e = 0.45
        p = 2.20
        scale = 0.78
        orbit = orbit_curve(focus=focus, e=e, p=p, scale=scale, width=5, opacity=0.86)
        glow = orbit.copy().set_stroke(width=18, opacity=0.10)
        sun_obj = sun(focus, 0.15)
        sun_name = cn("太阳", 0.22, AMBER).move_to(focus + DOWN * 0.46 + RIGHT * 0.08)
        start = orbit_point(0, e=e, p=p, focus=focus, scale=scale)
        body = planet(start, 0.075, BLUE)
        body_name = cn("行星", 0.22, BLUE).next_to(body, DOWN + RIGHT, buff=0.08)
        v_arrow = Arrow(start, start + UP * 1.05, buff=0.10, color=MINT, stroke_width=5, max_tip_length_to_length_ratio=0.18)

        center = focus + LEFT * (e * p / (1 - e**2) * scale)
        empty_focus = focus + LEFT * (2 * e * p / (1 - e**2) * scale)
        center_dot = Dot(center, color=VIOLET, radius=0.052)
        center_label = cn("椭圆中心", 0.22, VIOLET).next_to(center_dot, DOWN, buff=0.08)
        focus_dot = Dot(empty_focus, color=MUTED, radius=0.052)
        focus_label = cn("另一个焦点", 0.22, MUTED).next_to(focus_dot, DOWN, buff=0.08)
        sun_focus_label = cn("太阳在焦点", 0.24, AMBER).next_to(sun_obj, UP, buff=0.10)
        major_axis = DashedLine(empty_focus, start, color="#3C5068", stroke_width=2.2, dash_length=0.08)

        panel = formula_panel(6.05, 5.72).to_edge(RIGHT, buff=0.28).shift(DOWN * 0.11)
        g1_title = cn("从形状方程继续", PANEL_TITLE_SIZE, MUTED)
        g1_eq = MathTex(r"u''+u=\frac{k}{h^2}", color=AMBER).scale(0.72)
        g1_note = cn("微分方程结论：常数项 + 正弦/余弦项", PANEL_NOTE_SIZE, MUTED)
        g1 = VGroup(g1_title, g1_eq, g1_note).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        fit_inside(g1, max_width=5.16, max_height=1.45)
        g1.move_to(panel.get_top() + DOWN * 0.82)

        g2_title = cn("整理振荡项", PANEL_TITLE_SIZE, MUTED)
        g2a = MathTex(r"u=\frac{k}{h^2}+C\cos\theta+D\sin\theta", color=INK).scale(PANEL_FORMULA_SMALL_SIZE)
        g2b = MathTex(r"C\cos\theta+D\sin\theta=A\cos(\theta-\phi)", color=INK).scale(PANEL_FORMULA_SMALL_SIZE)
        g2_mid = cn("把 θ=0 选在近日点，相位并入角度零点", PANEL_NOTE_SIZE, MUTED)
        g2c = MathTex(r"u=\frac{k}{h^2}+A\cos\theta=\frac{k}{h^2}(1+e\cos\theta)", color=AMBER).scale(PANEL_FORMULA_SMALL_SIZE)
        g2_note = cn("e：控制偏离圆的程度", PANEL_NOTE_SIZE, AMBER)
        g2 = VGroup(g2_title, g2a, g2b, g2_mid, g2c, g2_note).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        fit_inside(g2, max_width=5.20, max_height=3.70)
        g2.move_to(panel.get_center() + DOWN * 0.72)

        g3_title = cn("回到 r(θ)", PANEL_TITLE_SIZE, MUTED)
        g3b = MathTex(r"r=\frac{h^2/k}{1+e\cos\theta}", color=AMBER).scale(PANEL_FORMULA_LARGE_SIZE)
        g3_polar_note = cn("椭圆的极坐标形式", PANEL_NOTE_SIZE, AMBER)
        g3_focus_note = cn("极点：太阳所在焦点", PANEL_NOTE_SIZE, MUTED)
        g3_theta_note = cn("θ：从近日点方向算起", PANEL_NOTE_SIZE, MUTED)
        g3c = MathTex(r"r=\frac{h^2/(GM_{\odot})}{1+e\cos\theta}", color=AMBER).scale(PANEL_FORMULA_SIZE)
        g3_phys_k = MathTex(r"k=GM_{\odot}", color=BLUE).scale(0.54)
        g3_common_note = cn("常用轨道元素：半长轴 a_orb 与偏心率 e", PANEL_NOTE_SIZE, MUTED)
        g3_period_note = cn("周期可推得半长轴；仍需要偏心率", PANEL_NOTE_SIZE, MUTED)
        g3d = MathTex(r"r=\frac{a_{\rm orb}(1-e^2)}{1+e\cos\theta}", color=AMBER).scale(PANEL_FORMULA_SIZE)
        g3_note = cn("a_orb：轨道半长轴；e：偏心率", PANEL_NOTE_SIZE, AMBER)
        g3_note2 = cn("θ：从近日点方向算起", PANEL_NOTE_SIZE, MUTED)
        g3_title_final = cn("换成常用轨道元素", PANEL_TITLE_SIZE, MUTED)
        content_left = panel.get_left() + RIGHT * 0.72
        g3_title.move_to(panel.get_top() + DOWN * 0.82).align_to(content_left, LEFT)
        g3b.next_to(g3_title, DOWN, buff=0.34).align_to(g3_title, LEFT)
        g3_polar_note.next_to(g3b, DOWN, buff=0.34).align_to(g3_title, LEFT)
        g3_focus_note.next_to(g3_polar_note, DOWN, buff=0.20).align_to(g3_title, LEFT)
        g3_theta_note.next_to(g3_focus_note, DOWN, buff=0.20).align_to(g3_title, LEFT)
        g3c.move_to(g3b).align_to(g3b, LEFT)
        g3_phys_k.next_to(g3c, DOWN, buff=0.36).align_to(g3_title, LEFT)
        g3_common_note.next_to(g3_phys_k, DOWN, buff=0.30).align_to(g3_title, LEFT)
        g3_title_final.move_to(g3_title).align_to(g3_title, LEFT)
        g3d.move_to(g3b).align_to(g3b, LEFT)
        g3_period_note.next_to(g3d, DOWN, buff=0.38).align_to(g3_title, LEFT)
        g3_note.next_to(g3_period_note, DOWN, buff=0.22).align_to(g3_title, LEFT)
        g3_note2.next_to(g3_note, DOWN, buff=0.22).align_to(g3_title, LEFT)

        g4_title = cn("e 决定椭圆有多扁", PANEL_TITLE_SIZE, AMBER)
        g4_row0 = VGroup(
            MathTex(r"e=0", color=INK).scale(0.54),
            cn("圆", PANEL_NOTE_SIZE, MUTED),
        ).arrange(RIGHT, buff=0.42, aligned_edge=DOWN)
        g4_row1 = VGroup(
            MathTex(r"0<e<1", color=AMBER).scale(0.54),
            cn("椭圆", PANEL_NOTE_SIZE, AMBER),
        ).arrange(RIGHT, buff=0.42, aligned_edge=DOWN)
        g4_row2 = VGroup(
            cn("e 接近 1", PANEL_NOTE_SIZE, INK),
            cn("越扁", PANEL_NOTE_SIZE, MUTED),
        ).arrange(RIGHT, buff=0.42, aligned_edge=DOWN)
        g4a = VGroup(g4_row0, g4_row1, g4_row2).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        g4b = cn("太阳在焦点，不在中心。", PANEL_BODY_SIZE, MUTED)
        g4c = cn("近日点更快；远日点更慢。", PANEL_BODY_SIZE, MUTED)
        g4 = VGroup(g4_title, g4a, g4b, g4c).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        fit_inside(g4, max_width=4.78, max_height=3.78)
        g4.move_to(panel.get_center() + DOWN * 0.64)

        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.7)
        self.play(FadeIn(sun_obj), FadeIn(sun_name), Create(glow), Create(orbit), FadeIn(body), FadeIn(body_name), GrowArrow(v_arrow), run_time=1.1)
        self.play(FadeIn(panel), FadeIn(g1), run_time=0.8)
        self.wait(0.4)
        self.play(FadeIn(g2_title, shift=UP * 0.08), FadeIn(g2a, shift=UP * 0.08), run_time=0.8)
        self.wait(12.7)
        self.play(FadeIn(g2b, shift=UP * 0.08), FadeIn(g2_mid, shift=UP * 0.08), run_time=0.8)
        self.wait(8.6)
        self.play(FadeIn(g2c, shift=UP * 0.08), FadeIn(g2_note, shift=UP * 0.08), run_time=0.8)
        self.play(v_arrow.animate.set_stroke(width=8), orbit.animate.set_stroke(width=6), run_time=0.9)
        self.wait(2.4)
        self.play(FadeOut(g1, shift=UP * 0.08), FadeOut(g2, shift=UP * 0.08), FadeIn(g3_title, shift=UP * 0.08), run_time=1.1)
        self.play(FadeIn(g3b, shift=UP * 0.08), run_time=1.0)
        self.wait(7.1)
        self.play(
            FadeIn(g3_polar_note, shift=UP * 0.08),
            FadeIn(g3_focus_note, shift=UP * 0.08),
            FadeIn(g3_theta_note, shift=UP * 0.08),
            run_time=0.7,
        )
        self.wait(6.25)
        self.play(
            ReplacementTransform(g3b, g3c),
            FadeOut(g3_polar_note, shift=UP * 0.08),
            FadeOut(g3_focus_note, shift=UP * 0.08),
            FadeOut(g3_theta_note, shift=UP * 0.08),
            FadeIn(g3_phys_k, shift=UP * 0.08),
            run_time=1.1,
        )
        self.wait(10.5)
        self.play(FadeIn(g3_common_note, shift=UP * 0.08), run_time=0.8)
        self.wait(8.5)
        self.play(
            Transform(g3_title, g3_title_final),
            ReplacementTransform(g3c, g3d),
            FadeOut(g3_phys_k, shift=UP * 0.08),
            FadeOut(g3_common_note, shift=UP * 0.08),
            run_time=1.0,
        )
        self.wait(7.65)
        self.play(
            FadeIn(g3_period_note, shift=UP * 0.08),
            FadeIn(g3_note, shift=UP * 0.08),
            FadeIn(g3_note2, shift=UP * 0.08),
            run_time=0.8,
        )
        self.wait(7.75)
        self.play(
            FadeOut(g3_title, shift=UP * 0.08),
            FadeOut(g3d, shift=UP * 0.08),
            FadeOut(g3_period_note, shift=UP * 0.08),
            FadeOut(g3_note, shift=UP * 0.08),
            FadeOut(g3_note2, shift=UP * 0.08),
            FadeIn(g4_title, shift=UP * 0.08),
            FadeIn(g4a, shift=UP * 0.08),
            orbit.animate.set_stroke(width=8, color=AMBER),
            run_time=1.2,
        )
        self.wait(7.5)
        self.play(Create(major_axis), FadeIn(center_dot), FadeIn(center_label), FadeIn(focus_dot), FadeIn(focus_label), FadeIn(sun_focus_label), FadeIn(g4b), run_time=1.3)
        self.wait(2.3)
        self.play(FadeIn(g4c, shift=UP * 0.08), orbit.animate.set_stroke(width=9), run_time=1.2)
        finish_to(self, TARGET_DURATIONS["ConstantsEllipse"])


class VelocityLab(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("换初速度，轨道会变成什么？", "同一起点，对比坠落、椭圆、抛物线和双曲线")
        focus = LEFT * 2.30 + DOWN * 0.90
        scale = 0.72
        rot = -0.18
        sun_obj = sun(focus, 0.15)
        sun_name = cn("太阳", 0.22, AMBER).move_to(focus + DOWN * 0.44 + RIGHT * 0.08)
        start = focus + scale * rot2(np.array([2.0, 0.0, 0.0]), rot)
        start_dot = planet(start, 0.072, BLUE)
        start_label = cn("行星起点", 0.23, BLUE).next_to(start_dot, DOWN, buff=0.08)
        base_line = DashedLine(focus, start, color="#3C5068", stroke_width=2.2, dash_length=0.08)

        panel = formula_panel(5.55, 5.20).to_edge(RIGHT, buff=0.45).shift(DOWN * 0.18)
        panel_title = cn("速度刻度", PANEL_TITLE_SIZE, MUTED)
        vc = MathTex(r"v_c=\sqrt{k/r_0}", color=MINT).scale(PANEL_FORMULA_SIZE)
        vesc = MathTex(r"v_{esc}=\sqrt{2k/r_0}", color=ROSE).scale(PANEL_FORMULA_SIZE)
        rule = cn("低于逃逸速度：闭合；超过：飞离", PANEL_NOTE_SIZE, MUTED)
        stack = VGroup(panel_title, vc, vesc, rule).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        fit_inside(stack, max_width=4.80)
        stack.move_to(panel.get_center() + UP * 0.55)

        case_anchor = panel.get_bottom() + UP * 0.88
        case_label = cn("改变初速度", 0.34, AMBER).move_to(case_anchor)

        cases = [
            ("横向太小：坠向太阳", 0.28, ROSE, 520),
            ("偏小但闭合：很扁的椭圆", 0.55, VIOLET, 1050),
            ("刚好圆轨道速度", np.sqrt(0.5), MINT, 1180),
            ("仍低于逃逸速度：椭圆变大", 0.90, BLUE, 1200),
            ("到达逃逸速度：抛物线", 1.00, AMBER, 720),
            ("超过逃逸速度：双曲线", 1.18, ROSE, 560),
        ]
        # Relative to this scene's narration: each curve settles just before its spoken case is named.
        case_starts = [7.80, 11.25, 15.55, 19.10, 26.60, 30.80]

        def velocity_arrow(vy: float, color: str) -> Arrow:
            length = 0.70 + 0.84 * vy
            direction = rot2(UP, rot)
            return Arrow(start, start + direction * length, buff=0.10, color=color, stroke_width=6, max_tip_length_to_length_ratio=0.18)

        def wait_until(time_mark: float) -> None:
            remaining = time_mark - self.time
            if remaining > 0:
                self.wait(remaining)

        arrow = velocity_arrow(cases[0][1], cases[0][2])
        v_label = MathTex(r"\vec v_0", color=cases[0][2]).scale(0.54).next_to(arrow, RIGHT, buff=0.08)

        current_curve: Mobject | None = None
        current_arrow: Mobject = arrow
        current_v_label: Mobject = v_label
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)
        self.play(FadeIn(sun_obj), FadeIn(sun_name), FadeIn(start_dot), FadeIn(start_label), Create(base_line), FadeIn(panel), FadeIn(stack), run_time=1.3)
        self.play(GrowArrow(arrow), FadeIn(v_label), FadeIn(case_label), run_time=0.8)

        for index, (label, vy, color, steps) in enumerate(cases):
            wait_until(case_starts[index])
            points = transform_sim_points(simulate_orbit(float(vy), steps=steps), focus, scale=scale, rot=rot)
            curve = path_from_points(points, color=color, width=5.5 if index != 0 else 5.0, opacity=0.94)
            next_arrow = velocity_arrow(float(vy), color)
            next_label = MathTex(r"\vec v_0", color=color).scale(0.54).next_to(next_arrow, RIGHT, buff=0.08)
            next_case_label = cn(label, 0.34, color).move_to(case_anchor)
            anims = [
                Transform(current_arrow, next_arrow),
                Transform(current_v_label, next_label),
                Transform(case_label, next_case_label),
            ]
            if current_curve is None:
                anims.append(Create(curve))
                self.play(*anims, run_time=0.75)
                current_curve = curve
            else:
                anims.append(ReplacementTransform(current_curve, curve))
                self.play(*anims, run_time=0.75)
                current_curve = curve

        finish_to(self, TARGET_DURATIONS["VelocityLab"])


class PlanetaryPayoff(Scene):
    def construct(self) -> None:
        set_scene_background(self)
        title = scene_title("回到真实行星轨道", "偏心率不同，太阳仍在焦点附近")
        focus = LEFT * 1.25 + DOWN * 0.10
        sun_obj = sun(focus, 0.16)
        sun_name = cn("太阳", 0.22, AMBER).move_to(focus + UP * 0.34 + RIGHT * 0.28)
        orbit_specs = [
            ("水星", 0.42, 1.35, AMBER, 0.66, 0.15),
            ("地球", 0.06, 2.05, BLUE, 0.68, -0.05),
            ("火星", 0.13, 2.62, ROSE, 0.68, 0.06),
            ("木星", 0.05, 3.25, MINT, 0.66, -0.10),
        ]
        groups = VGroup()
        movers = VGroup()
        for name, ecc, p_val, color, scale, rot in orbit_specs:
            curve = orbit_curve(e=ecc, p=p_val, focus=focus, scale=scale, rot=rot, color=color, width=3.2, opacity=0.70, samples=220)
            dot = planet(orbit_point(0.72, e=ecc, p=p_val, focus=focus, scale=scale, rot=rot), 0.052, color)
            label = cn(name, 0.24, color).next_to(dot, UP, buff=0.06)
            groups.add(curve)
            movers.add(VGroup(dot, label))

        focus_label = cn("太阳位于共同焦点附近", 0.28, AMBER).next_to(sun_obj, DOWN, buff=0.24)
        panel = formula_panel(4.65, 2.25).to_edge(RIGHT, buff=0.62).shift(DOWN * 1.78)
        panel_title = cn("真实行星：椭圆轨道", PANEL_TITLE_SIZE, AMBER)
        eq = MathTex(r"0<e<1", color=AMBER).scale(0.62)
        note1 = cn("e 越大，轨道越扁", PANEL_NOTE_SIZE, MUTED)
        note2 = cn("太阳在焦点；面积定律仍成立", PANEL_NOTE_SIZE, MUTED)
        stack = VGroup(panel_title, eq, note1, note2).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        fit_inside(stack, max_width=4.00, max_height=1.72)
        stack.move_to(panel)

        tracker = ValueTracker(0.72)

        def moving_planets() -> VGroup:
            dots = VGroup()
            for name, ecc, p_val, color, scale, rot in orbit_specs:
                t = tracker.get_value() * (1.0 + 0.16 * orbit_specs.index((name, ecc, p_val, color, scale, rot)))
                point = orbit_point(t, e=ecc, p=p_val, focus=focus, scale=scale, rot=rot)
                dot = planet(point, 0.052, color)
                label = cn(name, 0.23, color).next_to(dot, UP, buff=0.06)
                dots.add(VGroup(dot, label))
            return dots

        def payoff_gravity_geometry() -> tuple[np.ndarray, np.ndarray, float]:
            _, ecc, p_val, _, scale, rot = orbit_specs[0]
            point = orbit_point(tracker.get_value(), e=ecc, p=p_val, focus=focus, scale=scale, rot=rot)
            return gravity_geometry(point, focus, base=0.18, amplitude=0.44, reference=0.92)

        live_planets = always_redraw(moving_planets)
        gravity_arrow = always_redraw(
            lambda: Arrow(
                payoff_gravity_geometry()[0],
                payoff_gravity_geometry()[0] + payoff_gravity_geometry()[1] * payoff_gravity_geometry()[2],
                buff=0.06,
                color=ROSE,
                stroke_width=3.6,
                max_tip_length_to_length_ratio=0.24,
            ).set_z_index(6)
        )
        gravity_label = MathTex(r"\vec a", color=ROSE).scale(0.36).set_z_index(7)
        gravity_label.add_updater(
            lambda mob: mob.move_to(payoff_gravity_geometry()[0] + payoff_gravity_geometry()[1] * payoff_gravity_geometry()[2] + UP * 0.10)
        )
        self.play(FadeIn(title, shift=DOWN * 0.18), run_time=0.8)
        self.play(FadeIn(sun_obj), FadeIn(sun_name), FadeIn(focus_label), LaggedStart(*[Create(c) for c in groups], lag_ratio=0.14), run_time=2.4)
        self.add(live_planets, gravity_arrow, gravity_label)
        self.play(tracker.animate.set_value(TAU + 0.72), run_time=7.2, rate_func=linear)
        self.play(FadeIn(panel), FadeIn(stack, shift=UP * 0.08), run_time=1.2)
        self.play(tracker.animate.set_value(1.75 * TAU + 0.72), run_time=6.2, rate_func=linear)
        finish_to(self, TARGET_DURATIONS["PlanetaryPayoff"])
