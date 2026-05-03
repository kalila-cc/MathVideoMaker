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
    FONT_SMALL,
    FONT_SUB,
    FONT_TITLE,
    GRID,
    MUTED,
    OUT_DIR,
    PANEL,
    TEXT,
    VIOLET,
    W,
    H,
    World,
    draw_rules,
    draw_world,
    fast_steps_for_frame,
    fast_view_cells,
)


ROOT = Path(__file__).resolve().parent
FRAME_DIR = ROOT / "exports" / "frames" / "chaos_intro_segment"
OUT_VIDEO = OUT_DIR / "chaos_seed_intro_v6_silent_720p20.mp4"
POSTER = COVER_DIR / "chaos_seed_intro_v6_poster.jpg"

FPS = 20
TOTAL_FRAMES = 600
SLOW_END = 360


def draw_bottom_line(draw: ImageDraw.ImageDraw, text: str) -> None:
    draw.rounded_rectangle((266, 608, 1014, 670), radius=14, fill=(15, 27, 48), outline=(47, 72, 110))
    draw.text((306, 622), text, fill=TEXT, font=FONT_SMALL)


def draw_legend(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.text((x, y), "脚下这一格决定下一步", fill=TEXT, font=FONT_SMALL)
    rows = [("暗", "右转，点亮", (44, 58, 84)), ("青", "直走，升为紫", CYAN), ("紫", "左转，熄灭", VIOLET)]
    yy = y + 34
    for label, body, color in rows:
        draw.rounded_rectangle((x, yy + 3, x + 20, yy + 23), radius=5, fill=color)
        draw.text((x + 32, yy), f"{label}格：{body}", fill=MUTED, font=FONT_SMALL)
        yy += 32


def render_frame(frame: int, world: World) -> Image.Image:
    img = Image.new("RGBA", (W, H), (*BG, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    if frame < SLOW_END:
        if frame % 5 == 0:
            world.step(1)
        draw.text((58, 36), "只按三句规则行动的小家伙", fill=TEXT, font=FONT_TITLE)
        draw.text((60, 88), "看脚下，转向，改变这一格，再走开。", fill=MUTED, font=FONT_SUB)
        draw_world(img, world, (64, 148, 812, 594), 15, 9, None, show_event=True, grid_every=1)
        draw = ImageDraw.Draw(img, "RGBA")
        draw_legend(draw, 900, 160)
        if frame < 120:
            line = "先看脚下这一格，再决定怎么动"
        elif frame < 260:
            line = "暗格右转点亮，青格直走变紫，紫格左转熄掉"
        else:
            line = "处理完这一格，它才往前走一格"
        draw_bottom_line(draw, f"第 {world.steps:,} 步：{line}")
    else:
        world.step(fast_steps_for_frame(frame - SLOW_END + 120))
        cells_w, cells_h = fast_view_cells(world)
        draw.text((58, 36), "同一条规则，织出花纹", fill=TEXT, font=FONT_TITLE)
        draw.text((60, 88), "镜头退远以后，脚步开始留下形状。", fill=MUTED, font=FONT_SUB)
        draw_world(img, world, (74, 146, 1114, 596), cells_w, cells_h, None, show_agent=False, grid_every=1)
        draw = ImageDraw.Draw(img, "RGBA")
        draw.text((74, 152), f"{world.steps:,} steps", fill=TEXT, font=FONT_MONO)
        draw_rules(draw, 930, 34)
        draw_bottom_line(draw, "看着乱，但同一个开头会走出同一片花纹")

    return img.convert("RGB")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    if FRAME_DIR.exists():
        shutil.rmtree(FRAME_DIR)
    FRAME_DIR.mkdir(parents=True, exist_ok=True)

    world = World()
    poster = None
    for frame in range(TOTAL_FRAMES):
        image = render_frame(frame, world)
        image.save(FRAME_DIR / f"frame_{frame:04d}.png")
        if frame == TOTAL_FRAMES - 30:
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
