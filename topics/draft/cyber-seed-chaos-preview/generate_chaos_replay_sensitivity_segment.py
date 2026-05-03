from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw

from generate_quick_video import (
    BG,
    COVER_DIR,
    CYAN,
    FONT_MONO,
    FONT_RULE,
    FONT_SMALL,
    FONT_SUB,
    FONT_TITLE,
    GRID,
    MUTED,
    OUT_DIR,
    TEXT,
    VIOLET,
    W,
    H,
    World,
    draw_world,
)


ROOT = Path(__file__).resolve().parent
FRAME_DIR = ROOT / "exports" / "frames" / "chaos_replay_sensitivity"
OUT_VIDEO = OUT_DIR / "chaos_replay_sensitivity_v2_silent_720p20.mp4"
POSTER = COVER_DIR / "chaos_replay_sensitivity_v2_poster.jpg"

FPS = 20
TOTAL_FRAMES = 440
WHITE = (255, 255, 255)
YELLOW = (255, 215, 104)


def smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def steps_for_frame(frame: int) -> int:
    if frame < 50:
        return 8
    if frame < 140:
        return 36
    if frame < 280:
        return 110
    return 240


def draw_rule_chip(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, color: tuple[int, int, int]) -> None:
    draw.rounded_rectangle((x, y, x + 18, y + 18), radius=4, fill=color)
    draw.text((x + 28, y - 3), label, fill=MUTED, font=FONT_SMALL)


def draw_bottom(draw: ImageDraw.ImageDraw, text: str) -> None:
    draw.rounded_rectangle((216, 608, 1064, 664), radius=14, fill=(15, 27, 48), outline=(47, 72, 110), width=1)
    draw.text((252, 624), text, fill=TEXT, font=FONT_SMALL)


def grid_origin_marker(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    cells_w: int,
    cells_h: int,
    title: str | None,
    label: str,
    frame: int,
) -> None:
    x0, y0, x1, y1 = box
    top_pad = 54 if title else 16
    left_pad = 16
    right_pad = 16
    bottom_pad = 16
    area_x = x0 + left_pad
    area_y = y0 + top_pad
    area_w = x1 - x0 - left_pad - right_pad
    area_h = y1 - y0 - top_pad - bottom_pad
    cell = max(2, min(area_w // cells_w, area_h // cells_h))
    grid_w = cells_w * cell
    grid_h = cells_h * cell
    gx0 = area_x + (area_w - grid_w) // 2
    gy0 = area_y + (area_h - grid_h) // 2
    cx = gx0 + (cells_w // 2) * cell + cell / 2
    cy = gy0 + (cells_h // 2) * cell + cell / 2
    pulse = 0.5 + 0.5 * smoothstep((frame % 56) / 55)
    radius = int(15 + 8 * pulse)
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=YELLOW, width=3)
    draw.line((cx + radius + 8, cy - 2, cx + radius + 64, cy - 28), fill=YELLOW, width=2)
    draw.rounded_rectangle((cx + radius + 66, cy - 49, cx + radius + 210, cy - 16), radius=16, fill=(39, 31, 42), outline=YELLOW, width=1)
    draw.text((cx + radius + 82, cy - 44), label, fill=YELLOW, font=FONT_SMALL)


def draw_start_patch(draw: ImageDraw.ImageDraw, x: int, y: int, title: str, marked: bool) -> None:
    draw.rounded_rectangle((x, y, x + 188, y + 132), radius=12, fill=(11, 21, 38), outline=(44, 67, 102), width=1)
    draw.text((x + 16, y + 12), title, fill=TEXT, font=FONT_SMALL)
    cell = 18
    gx = x + 44
    gy = y + 48
    for yy in range(3):
        for xx in range(3):
            fill = BG
            if marked and xx == 1 and yy == 1:
                fill = YELLOW
            draw.rectangle(
                (gx + xx * cell, gy + yy * cell, gx + (xx + 1) * cell - 2, gy + (yy + 1) * cell - 2),
                fill=fill,
                outline=GRID,
                width=1,
            )
    if marked:
        draw.ellipse((gx + cell - 5, gy + cell - 5, gx + 2 * cell + 3, gy + 2 * cell + 3), outline=WHITE, width=2)
        draw.text((x + 112, y + 64), "多这一格", fill=YELLOW, font=FONT_SMALL)
    else:
        draw.text((x + 112, y + 64), "全暗", fill=MUTED, font=FONT_SMALL)


def render_frame(frame: int, replay: World, changed: World) -> Image.Image:
    img = Image.new("RGBA", (W, H), (*BG, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    replay.step(steps_for_frame(frame))
    changed.step(steps_for_frame(frame))
    pulse = smoothstep((frame - 80) / 100)

    draw.text((58, 34), "它不是随机，但会分岔", fill=TEXT, font=FONT_TITLE)
    draw.text((60, 86), "同一个开头会完整重放；只差一个初始小痕迹，后面就长成另一片。", fill=MUTED, font=FONT_SUB)

    draw_world(img, replay, (58, 150, 600, 560), 112, 84, "同一起点：重跑一次", show_agent=False, grid_every=2)
    draw_world(img, changed, (680, 150, 1222, 560), 112, 84, "出生格先亮一下", show_agent=False, grid_every=2)
    draw = ImageDraw.Draw(img, "RGBA")

    draw.text((86, 210), f"{replay.steps:,} steps", fill=TEXT, font=FONT_MONO)
    draw.text((708, 210), f"{changed.steps:,} steps", fill=TEXT, font=FONT_MONO)
    draw.rounded_rectangle((86, 512, 372, 546), radius=17, fill=(18, 36, 55), outline=(60, 118, 145), width=1)
    draw.text((108, 518), "重跑误差：0 格", fill=CYAN, font=FONT_SMALL)
    draw.rounded_rectangle((708, 512, 1074, 546), radius=17, fill=(36, 24, 52), outline=(104, 76, 154), width=1)
    draw.text((730, 518), "开头盘面：只多一个亮格", fill=YELLOW, font=FONT_SMALL)
    grid_origin_marker(draw, (680, 150, 1222, 560), 112, 84, "出生格先亮一下", "多出的亮格", frame)
    if frame < 190:
        draw_start_patch(draw, 90, 360, "左边开头", marked=False)
        draw_start_patch(draw, 710, 360, "右边开头", marked=True)

    draw_rule_chip(draw, 86, 588, "暗格右转", (44, 58, 84))
    draw_rule_chip(draw, 226, 588, "青格直走", CYAN)
    draw_rule_chip(draw, 366, 588, "紫格左转", VIOLET)
    draw.text((708, 588), "规则没有变，变的是历史的第一笔。", fill=(*WHITE, int(155 + 100 * pulse)), font=FONT_SMALL)

    if frame < 150:
        draw_bottom(draw, "同样的开头，不会掷骰子；它会一步不差地重来。")
    elif frame < 300:
        draw_bottom(draw, "但右边开头只多出标出的那一格，之后踩到的旧痕迹就不同了。")
    else:
        draw_bottom(draw, "混沌感来自这里：规则很短，历史却越攒越厚。")

    return img.convert("RGB")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    if FRAME_DIR.exists():
        shutil.rmtree(FRAME_DIR)
    FRAME_DIR.mkdir(parents=True, exist_ok=True)

    replay = World()
    changed = World(initial_mark=True)
    poster = None
    for frame in range(TOTAL_FRAMES):
        image = render_frame(frame, replay, changed)
        image.save(FRAME_DIR / f"frame_{frame:04d}.png")
        if frame == TOTAL_FRAMES - 20:
            poster = image.copy()

    if poster is None:
        poster = image
    poster.save(POSTER, quality=92)

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
    print(POSTER)


if __name__ == "__main__":
    main()
