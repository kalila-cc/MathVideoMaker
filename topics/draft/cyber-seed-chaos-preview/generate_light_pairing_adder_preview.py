from __future__ import annotations

import math
import shutil
import subprocess
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "exports" / "final"
COVER_DIR = ROOT / "exports" / "covers"
FRAME_DIR = ROOT / "exports" / "frames" / "light_pairing_adder"
OUT_VIDEO = OUT_DIR / "xiaoguang_light_pairing_adder_chapter_v8_silent_720p20.mp4"
EARLY_FRAME = COVER_DIR / "xiaoguang_light_pairing_adder_chapter_v8_behavior.jpg"
REVEAL_FRAME = COVER_DIR / "xiaoguang_light_pairing_adder_chapter_v8_reveal.jpg"

W, H = 1280, 720
FPS = 20
TOTAL_FRAMES = 1200

BG = (7, 11, 20)
PANEL = (10, 17, 31)
GRID = (35, 49, 73)
GRID_BOLD = (58, 76, 108)
TEXT = (235, 242, 255)
MUTED = (140, 162, 196)
DIM = (25, 34, 52)
WHITE = (255, 255, 255)
YELLOW = (255, 215, 104)
LIME = (112, 255, 178)
CYAN = (24, 216, 255)
CYAN_DARK = (17, 96, 124)
PINK = (255, 103, 202)

A_BITS = [0, 1, 0, 0, 1, 1, 0, 1]
B_BITS = [0, 0, 1, 0, 1, 0, 0, 1]
COLS = len(A_BITS)

BOARD = (136, 140, 1144, 594)
TRACK_LEFT = 276
TRACK_RIGHT = 1004
PITCH = (TRACK_RIGHT - TRACK_LEFT) / (COLS - 1)
Y_A = 204
Y_B = 274
Y_XG = 410
Y_OUT = 528
STEP_START = 180
STEP_FRAMES = 85
REVEAL_START = STEP_START + COLS * STEP_FRAMES


@dataclass(frozen=True)
class StepInfo:
    col: int
    before: int
    seen: int
    out: int
    after: int


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for item in candidates:
        try:
            return ImageFont.truetype(item, size)
        except OSError:
            continue
    return ImageFont.load_default()


FONT_TITLE = font(34, True)
FONT_SUB = font(19)
FONT_LABEL = font(17, True)
FONT_SMALL = font(16)
FONT_MONO = font(26, True)
FONT_BIG = font(38, True)


def bit_string(bits: list[int]) -> str:
    return "".join(str(bit) for bit in bits)


def compute_steps() -> tuple[list[StepInfo], list[int]]:
    glow = 0
    outputs = [0] * COLS
    steps: list[StepInfo] = []
    for col in range(COLS - 1, -1, -1):
        seen = A_BITS[col] + B_BITS[col] + glow
        out = seen % 2
        next_glow = 1 if seen >= 2 else 0
        outputs[col] = out
        steps.append(StepInfo(col=col, before=glow, seen=seen, out=out, after=next_glow))
        glow = next_glow
    return steps, outputs


STEPS, OUT_BITS = compute_steps()


def x_for_col(col: int) -> float:
    return TRACK_LEFT + col * PITCH


def smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def current_motion(frame: int) -> tuple[int, float, float]:
    if frame < STEP_START:
        return 0, x_for_col(COLS - 1) + 80, 0.0
    index = min(COLS - 1, max(0, (frame - STEP_START) // STEP_FRAMES))
    local = ((frame - STEP_START) % STEP_FRAMES) / STEP_FRAMES
    step = STEPS[index]
    target_x = x_for_col(step.col)
    if index == 0:
        prev_x = x_for_col(COLS - 1) + 80
    else:
        prev_x = x_for_col(STEPS[index - 1].col)
    move_t = smoothstep(min(1.0, local / 0.28))
    x = prev_x + (target_x - prev_x) * move_t
    return index, x, local


def output_for_frame(frame: int) -> list[int | None]:
    out: list[int | None] = [None] * COLS
    if frame >= REVEAL_START:
        return OUT_BITS[:]
    if frame < STEP_START:
        return out
    index = min(COLS - 1, max(0, (frame - STEP_START) // STEP_FRAMES))
    local = ((frame - STEP_START) % STEP_FRAMES) / STEP_FRAMES
    for done in range(index):
        out[STEPS[done].col] = STEPS[done].out
    if local >= 0.46:
        out[STEPS[index].col] = STEPS[index].out
    return out


def mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def draw_radial_ellipse(
    draw: ImageDraw.ImageDraw,
    box: tuple[float, float, float, float],
    inner: tuple[int, int, int],
    outer: tuple[int, int, int],
    alpha: int = 255,
    steps: int = 9,
) -> None:
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    rx = (x1 - x0) / 2
    ry = (y1 - y0) / 2
    for index in range(steps, 0, -1):
        t = index / steps
        color = mix(inner, outer, t)
        current_alpha = int(alpha * (0.72 + 0.28 * (1 - t)))
        draw.ellipse(
            (
                cx - rx * t,
                cy - ry * t,
                cx + rx * t,
                cy + ry * t,
            ),
            fill=(*color, current_alpha),
        )
    draw.ellipse((cx - rx * 0.28, cy - ry * 0.34, cx + rx * 0.28, cy + ry * 0.20), fill=(*inner, alpha))


@lru_cache(maxsize=4)
def lamp_sprite(on: bool) -> Image.Image:
    size = 104
    sprite = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pixels = sprite.load()
    cx, cy = 52.0, 44.0
    radius = 23.0
    glow_radius = 50.0
    inner = (255, 255, 236)
    warm = (255, 220, 104)
    edge = (236, 165, 56)
    off_glass = (23, 35, 55)

    for y in range(size):
        for x in range(size):
            dist = math.hypot(x - cx, y - cy)
            if on:
                if dist <= glow_radius:
                    glow_t = max(0.0, 1.0 - dist / glow_radius)
                    alpha = int((glow_t**2.0) * 138)
                    color = mix(edge, warm, min(1.0, glow_t * 1.4))
                    pixels[x, y] = (*color, alpha)
                if dist <= radius:
                    d = dist / radius
                    hot = max(0.0, 1.0 - d)
                    color = mix(edge, warm, max(0.0, 1.0 - d * 0.42))
                    color = mix(color, inner, hot ** 0.78)
                    alpha = int(220 + 35 * hot)
                    pixels[x, y] = (*color, alpha)
            elif dist <= radius:
                shade = max(0.0, 1.0 - dist / radius)
                color = mix(off_glass, (42, 56, 82), shade)
                pixels[x, y] = (*color, 230)

    draw = ImageDraw.Draw(sprite, "RGBA")
    glass = (cx - radius, cy - radius, cx + radius, cy + radius)
    neck = (40, 67, 64, 86)
    if on:
        draw.ellipse((cx - 15, cy - 15, cx + 15, cy + 15), fill=(255, 244, 150, 118))
        draw.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=(255, 255, 230, 238))
        draw.ellipse(glass, outline=(255, 245, 188, 230), width=2)
        base_fill = (76, 83, 96)
    else:
        draw.ellipse(glass, outline=(*GRID_BOLD, 255), width=2)
        draw.arc((cx - 10, cy + 4, cx + 10, cy + 18), start=205, end=335, fill=(58, 72, 96), width=2)
        base_fill = (32, 43, 62)

    draw.rounded_rectangle(neck, radius=3, fill=base_fill, outline=(*GRID_BOLD, 255), width=1)
    draw.line((39, 73, 65, 73), fill=(122, 139, 162), width=1)
    draw.line((40, 79, 64, 79), fill=(122, 139, 162), width=1)
    return sprite


def draw_lamp(base: Image.Image, cx: float, cy: float, on: bool) -> None:
    sprite = lamp_sprite(on)
    base.alpha_composite(sprite, (int(cx - sprite.width / 2), int(cy - 44)))


def draw_output_cell(draw: ImageDraw.ImageDraw, cx: float, cy: float, value: int | None) -> None:
    r = 22
    if value is None:
        fill = (12, 19, 33)
        outline = GRID_BOLD
    elif value:
        fill = LIME
        outline = WHITE
    else:
        fill = (15, 24, 39)
        outline = (76, 95, 126)
    draw.rounded_rectangle((cx - r, cy - r, cx + r, cy + r), radius=7, fill=fill, outline=outline, width=2)


def cubic_points(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    samples: int = 14,
) -> list[tuple[float, float]]:
    points = []
    for index in range(samples):
        t = index / samples
        mt = 1 - t
        x = mt**3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t**3 * p3[0]
        y = mt**3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t**3 * p3[1]
        points.append((x, y))
    return points


def draw_blob(
    draw: ImageDraw.ImageDraw,
    segments: list[
        tuple[
            tuple[float, float],
            tuple[float, float],
            tuple[float, float],
            tuple[float, float],
        ]
    ],
    fill: tuple[int, int, int],
    outline: tuple[int, int, int] = WHITE,
    width: int = 2,
) -> None:
    points: list[tuple[float, float]] = []
    for segment in segments:
        points.extend(cubic_points(*segment))
    draw.polygon(points, fill=fill)
    draw.line(points + [points[0]], fill=outline, width=width, joint="curve")


def draw_xiaoguang_shape(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    belly_on: bool,
    mood: str,
    sensed_count: int = 0,
    blink: float = 0.0,
) -> None:
    shell = (91, 213, 248)
    shell_dark = (48, 117, 165)
    visor = (2, 10, 28)
    visor_edge = (142, 236, 255)
    glow = (145, 247, 255)
    metal = (132, 158, 190)
    metal_dark = (41, 57, 82)

    def draw_sensor_ball(bx: float, by: float, active: bool) -> None:
        if active:
            draw_radial_ellipse(draw, (bx - 18, by - 18, bx + 18, by + 18), inner=(255, 253, 225), outer=YELLOW, alpha=82, steps=8)
            draw.ellipse((bx - 8, by - 8, bx + 8, by + 8), fill=(255, 247, 182), outline=WHITE, width=2)
            draw.ellipse((bx - 3, by - 4, bx + 3, by + 2), fill=(255, 255, 241, 225))
        else:
            draw.ellipse((bx - 8, by - 8, bx + 8, by + 8), fill=(31, 49, 76), outline=(112, 145, 184), width=2)
            draw.arc((bx - 6, by - 6, bx + 6, by + 5), start=210, end=330, fill=(94, 122, 154), width=1)

    # Legs, arms, and side ear pods sit behind the main body.
    for sign in (-1, 1):
        draw.rounded_rectangle((cx + sign * 17 - 20, cy + 76, cx + sign * 17 + 20, cy + 110), radius=15, fill=shell_dark, outline=WHITE, width=2)
        upper = (cx + sign * 50, cy + 24, cx + sign * 74, cy + 66)
        lower = (cx + sign * 57, cy + 61, cx + sign * 77, cy + 99)
        draw.rounded_rectangle((min(upper[0], upper[2]), upper[1], max(upper[0], upper[2]), upper[3]), radius=13, fill=shell, outline=WHITE, width=2)
        draw.rounded_rectangle((min(lower[0], lower[2]), lower[1], max(lower[0], lower[2]), lower[3]), radius=12, fill=shell_dark, outline=WHITE, width=2)
        hand_x = cx + sign * 71
        draw.ellipse((hand_x - 6, cy + 97, hand_x + 6, cy + 109), fill=shell, outline=WHITE, width=2)
        draw.line((cx + sign * 57, cy + 64, cx + sign * 77, cy + 59), fill=(6, 18, 35), width=3)

        antenna = cubic_points(
            (cx + sign * 45, cy - 70),
            (cx + sign * 54, cy - 98),
            (cx + sign * 62, cy - 111),
            (cx + sign * 73, cy - 118),
            samples=18,
        )
        draw.line(antenna, fill=WHITE, width=6, joint="curve")
        draw.line(antenna, fill=(113, 223, 255), width=3, joint="curve")
        draw_sensor_ball(cx + sign * 74, cy - 120, sensed_count >= (2 if sign > 0 else 1))

        pod = (cx + sign * 59, cy - 54, cx + sign * 78, cy - 14)
        draw.rounded_rectangle((min(pod[0], pod[2]), pod[1], max(pod[0], pod[2]), pod[3]), radius=11, fill=shell_dark, outline=WHITE, width=2)
        draw.ellipse((cx + sign * 66 - 7, cy - 43, cx + sign * 66 + 7, cy - 22), fill=(126, 238, 255, 92))

    body_segments = [
        ((cx - 49, cy + 8), (cx - 62, cy + 24), (cx - 59, cy + 68), (cx - 36, cy + 84)),
        ((cx - 36, cy + 84), (cx - 18, cy + 95), (cx + 18, cy + 95), (cx + 36, cy + 84)),
        ((cx + 36, cy + 84), (cx + 59, cy + 68), (cx + 62, cy + 24), (cx + 49, cy + 8)),
        ((cx + 49, cy + 8), (cx + 26, cy - 2), (cx - 26, cy - 2), (cx - 49, cy + 8)),
    ]
    draw_blob(draw, body_segments, fill=(58, 153, 196), outline=WHITE, width=2)
    for sign in (-1, 1):
        foot_x = cx + sign * 21
        draw.rounded_rectangle((foot_x - 22, cy + 82, foot_x + 22, cy + 110), radius=13, fill=shell_dark, outline=WHITE, width=2)
        draw.arc((foot_x - 17, cy + 86, foot_x + 17, cy + 108), start=195, end=340, fill=(133, 233, 255, 110), width=2)
    head_box = (cx - 68, cy - 92, cx + 68, cy + 12)
    draw.rounded_rectangle(head_box, radius=30, fill=shell, outline=WHITE, width=2)
    draw.line((cx - 34, cy - 92, cx + 34, cy - 92), fill=(224, 254, 255, 130), width=2)
    draw.line((cx - 68, cy - 53, cx - 68, cy - 22), fill=(224, 254, 255, 90), width=2)
    draw.line((cx + 68, cy - 53, cx + 68, cy - 22), fill=(232, 148, 255, 80), width=2)

    draw.arc((cx - 58, cy - 87, cx - 4, cy - 24), start=196, end=276, fill=(214, 252, 255, 150), width=4)
    draw.arc((cx + 4, cy - 87, cx + 58, cy - 24), start=264, end=344, fill=(232, 148, 255, 115), width=4)
    for seam_x in (cx - 24, cx + 24):
        draw.line(cubic_points((seam_x, cy - 91), (seam_x - (cx - seam_x) * 0.1, cy - 67), (seam_x - (cx - seam_x) * 0.1, cy - 47), (seam_x, cy - 30), samples=14), fill=(32, 101, 153), width=2)

    visor_box = (cx - 58, cy - 65, cx + 58, cy - 12)
    draw.rounded_rectangle((visor_box[0] - 3, visor_box[1] - 3, visor_box[2] + 3, visor_box[3] + 3), radius=24, fill=(136, 224, 255), outline=None)
    draw.rounded_rectangle(visor_box, radius=21, fill=visor, outline=(16, 42, 76), width=2)
    draw.arc((cx - 54, cy - 63, cx - 18, cy - 27), start=188, end=266, fill=(222, 246, 255, 130), width=3)

    eye_h = 3 if blink > 0.88 and mood not in {"surprised", "thinking"} else 18
    for sign in (-1, 1):
        ex = cx + sign * 29
        if mood == "surprised":
            draw.ellipse((ex - 8, cy - 47, ex + 8, cy - 31), fill=glow)
        else:
            draw.rounded_rectangle((ex - 7, cy - 47, ex + 7, cy - 47 + eye_h), radius=7, fill=glow)
            for line_y in range(int(cy - 44), int(cy - 31), 4):
                draw.line((ex - 7, line_y, ex + 7, line_y), fill=visor, width=1)
        circuit_x = ex + sign * 18
        draw.line((ex + sign * 10, cy - 40, circuit_x, cy - 40, circuit_x + sign * 8, cy - 48), fill=glow, width=2)
        draw.line((ex + sign * 10, cy - 32, circuit_x + sign * 4, cy - 32), fill=glow, width=2)

    if mood == "happy":
        draw.arc((cx - 13, cy - 31, cx + 13, cy - 19), start=18, end=162, fill=glow, width=2)
    elif mood == "focused":
        draw.line((cx - 13, cy - 25, cx + 13, cy - 25), fill=glow, width=2)
    elif mood == "surprised":
        draw.ellipse((cx - 5, cy - 31, cx + 5, cy - 21), outline=glow, width=2)
    else:
        draw.arc((cx - 12, cy - 31, cx + 12, cy - 20), start=25, end=155, fill=glow, width=2)

    body_axis_x = cx
    panel_w = 60
    panel_h = 53
    panel_box = (
        body_axis_x - panel_w / 2,
        cy + 28,
        body_axis_x + panel_w / 2,
        cy + 28 + panel_h,
    )
    if belly_on:
        draw_radial_ellipse(draw, (body_axis_x - 43, cy + 15, body_axis_x + 43, cy + 90), inner=(236, 255, 255), outer=CYAN, alpha=142, steps=9)
    outer_fill = (159, 244, 255, 124) if belly_on else (44, 67, 87, 45)
    outer_outline = WHITE if belly_on else (82, 112, 142)
    panel_outline = (99, 202, 237) if belly_on else (47, 76, 98)
    draw.rounded_rectangle((panel_box[0] - 5, panel_box[1] - 5, panel_box[2] + 5, panel_box[3] + 5), radius=12, fill=outer_fill, outline=outer_outline, width=2)
    draw.rounded_rectangle(panel_box, radius=8, fill=(8, 25, 43), outline=panel_outline, width=2)
    cell = 7
    gap = 2
    grid_w = 5 * cell + 4 * gap
    grid_h = 5 * cell + 4 * gap
    grid_left = body_axis_x - grid_w / 2
    grid_top = (panel_box[1] + panel_box[3]) / 2 - grid_h / 2
    lit_cells = 25 if belly_on else 0
    for row in range(5):
        for col in range(5):
            idx = row * 5 + col
            x0 = grid_left + col * (cell + gap)
            y0 = grid_top + row * (cell + gap)
            active = belly_on or idx < lit_cells
            fill = (235, 255, 255) if active else (18, 39, 55)
            draw.rounded_rectangle((x0, y0, x0 + cell, y0 + cell), radius=2, fill=fill)


def draw_xiaoguang(
    base: Image.Image,
    cx: float,
    cy: float,
    belly_on: bool,
    mood: str,
    sensed_count: int = 0,
    blink: float = 0.0,
    scale: float = 0.58,
) -> None:
    sprite_w, sprite_h = 260, 300
    origin_x, origin_y = 130, 155
    sprite = Image.new("RGBA", (sprite_w, sprite_h), (0, 0, 0, 0))
    sprite_draw = ImageDraw.Draw(sprite, "RGBA")
    draw_xiaoguang_shape(sprite_draw, origin_x, origin_y, belly_on, mood, sensed_count, blink)
    scaled = sprite.resize((int(sprite_w * scale), int(sprite_h * scale)), Image.Resampling.LANCZOS)
    base.alpha_composite(scaled, (int(cx - origin_x * scale), int(cy - origin_y * scale)))


def draw_panel(draw: ImageDraw.ImageDraw) -> None:
    draw.rounded_rectangle(BOARD, radius=10, fill=PANEL, outline=(27, 40, 61), width=1)
    x0, y0, x1, y1 = BOARD
    for col in range(COLS):
        x = x_for_col(col)
        color = GRID_BOLD if col % 2 == 0 else GRID
        draw.line((x, y0 + 38, x, y1 - 38), fill=color, width=1)
    for y in (Y_A, Y_B, Y_XG, Y_OUT):
        draw.line((x0 + 42, y, x1 - 42, y), fill=GRID, width=1)


def draw_rows(base: Image.Image, draw: ImageDraw.ImageDraw, outputs: list[int | None], current_col: int | None, reveal: bool) -> None:
    labels = [("第一排灯", Y_A), ("第二排灯", Y_B), ("留下的痕迹", Y_OUT)]
    for text, y in labels:
        draw.text((BOARD[0] + 28, y - 12), text, fill=MUTED, font=FONT_SMALL)

    for col in range(COLS):
        x = x_for_col(col)
        if current_col == col:
            draw.rounded_rectangle((x - 34, BOARD[1] + 46, x + 34, BOARD[3] - 46), radius=8, fill=(28, 48, 78, 88), outline=(80, 122, 180, 150))
        draw_lamp(base, x, Y_A, bool(A_BITS[col]))
        draw_lamp(base, x, Y_B, bool(B_BITS[col]))
        draw_output_cell(draw, x, Y_OUT, outputs[col])
        if reveal:
            bit_y = Y_OUT + 45
            draw.text((x - 8, Y_A - 50), str(A_BITS[col]), fill=TEXT, font=FONT_SMALL)
            draw.text((x - 8, Y_B - 50), str(B_BITS[col]), fill=TEXT, font=FONT_SMALL)
            draw.text((x - 8, bit_y), str(OUT_BITS[col]), fill=LIME, font=FONT_SMALL)


def draw_behavior_text(draw: ImageDraw.ImageDraw, step: StepInfo, local: float, reveal: bool, frame: int) -> None:
    if reveal:
        draw.text((68, 32), "小光留下的，竟然是答案", fill=TEXT, font=FONT_TITLE)
        draw.text((70, 84), "亮着的是 1，暗着的是 0；小光只是一路巡灯。", fill=MUTED, font=FONT_SUB)
        equation = f"{bit_string(A_BITS)} + {bit_string(B_BITS)} = {bit_string(OUT_BITS)}"
        draw.rounded_rectangle((256, 608, 1024, 670), radius=12, fill=(15, 27, 48), outline=(47, 72, 110))
        draw.text((314, 619), equation, fill=WHITE, font=FONT_BIG)
        return

    if frame < STEP_START:
        title = "把规则连成一排"
        subtitle = "小光从右往左，把刚才的处理方式重复下去。"
        bottom = "每一格都只看眼前的灯和肚子里的光。"
    elif frame < 420:
        title = "小光的行为规则"
        subtitle = "成对的灯被收走；落单的灯留下一点亮痕。"
        bottom = None
    elif frame < 650:
        title = "肚子里的小灯"
        subtitle = "一格处理不完时，它会先把那团光揣着。"
        bottom = None
    else:
        title = "一路向左的处理规则"
        subtitle = "成对的收走，单着的留下，多出来的带去隔壁。"
        bottom = None

    draw.text((68, 32), title, fill=TEXT, font=FONT_TITLE)
    draw.text((70, 84), subtitle, fill=MUTED, font=FONT_SUB)

    if frame < STEP_START:
        draw.rounded_rectangle((286, 608, 994, 670), radius=12, fill=(15, 27, 48), outline=(47, 72, 110))
        draw.text((322, 622), bottom, fill=TEXT, font=FONT_LABEL)
        return

    if local < 0.42:
        line = f"这一格，小光数到 {step.seen} 盏灯"
    elif step.out:
        line = "配完还剩一盏没伴，地上留下一点亮痕"
    else:
        line = "灯刚好配成一对，地面安静地暗着"

    tail = "多出来的光带去下一格" if step.after else "肚子里没有多余的光"
    draw.rounded_rectangle((286, 608, 994, 670), radius=12, fill=(15, 27, 48), outline=(47, 72, 110))
    draw.text((322, 622), f"{line}；{tail}", fill=TEXT, font=FONT_LABEL)


def mood_for_step(step: StepInfo, local: float) -> str:
    if local < 0.24:
        return "curious"
    if local < 0.48:
        return "thinking"
    if local < 0.72:
        return "happy" if step.out else "focused"
    if step.after:
        return "focused"
    return "happy" if step.out else "curious"


def render_frame(frame: int) -> Image.Image:
    img = Image.new("RGBA", (W, H), (*BG, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    reveal = frame >= REVEAL_START
    step_index, xg_x, local = current_motion(frame)
    step = STEPS[step_index]
    outputs = output_for_frame(frame)
    current_col = None if reveal else step.col

    draw_panel(draw)
    draw_rows(img, draw, outputs, current_col, reveal)

    if not reveal:
        belly = step.before if local < 0.72 else step.after
        sensed_count = step.seen if local >= 0.18 else 0
        draw_xiaoguang(img, xg_x, Y_XG, bool(belly), mood_for_step(step, local), sensed_count=sensed_count, blink=(frame % 73) / 73)
        if local > 0.28:
            lit = []
            if A_BITS[step.col]:
                lit.append((x_for_col(step.col), Y_A))
            if B_BITS[step.col]:
                lit.append((x_for_col(step.col), Y_B))
            if step.before:
                lit.append((xg_x, Y_XG + 24))
            for lx, ly in lit:
                draw.line((lx, ly, xg_x, Y_XG - 12), fill=(*YELLOW, 130), width=2)
    else:
        draw_xiaoguang(img, x_for_col(0) - 82, Y_XG, False, "surprised", sensed_count=0, blink=0.0)

    draw_behavior_text(draw, step, local, reveal, frame)
    return img.convert("RGB")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    if FRAME_DIR.exists():
        shutil.rmtree(FRAME_DIR)
    FRAME_DIR.mkdir(parents=True, exist_ok=True)

    early = None
    reveal = None
    for frame in range(TOTAL_FRAMES):
        image = render_frame(frame)
        image.save(FRAME_DIR / f"frame_{frame:04d}.png")
        if frame == STEP_START + STEP_FRAMES * 2 + 12:
            early = image.copy()
        if frame == TOTAL_FRAMES - 18:
            reveal = image.copy()

    if early is None:
        early = render_frame(STEP_START + STEP_FRAMES * 2 + 12)
    if reveal is None:
        reveal = render_frame(TOTAL_FRAMES - 18)
    early.save(EARLY_FRAME, quality=92)
    reveal.save(REVEAL_FRAME, quality=92)

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-framerate",
        str(FPS),
        "-i",
        str(FRAME_DIR / "frame_%04d.png"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-crf",
        "18",
        str(OUT_VIDEO),
    ]
    subprocess.run(cmd, check=True)
    shutil.rmtree(FRAME_DIR)
    print(OUT_VIDEO)
    print(EARLY_FRAME)
    print(REVEAL_FRAME)


if __name__ == "__main__":
    main()
