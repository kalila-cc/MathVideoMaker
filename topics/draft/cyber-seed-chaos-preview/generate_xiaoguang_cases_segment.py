from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw

from generate_light_pairing_adder_preview import (
    BG,
    COVER_DIR,
    CYAN,
    FONT_LABEL,
    FONT_SMALL,
    FONT_SUB,
    FONT_TITLE,
    GRID,
    GRID_BOLD,
    LIME,
    MUTED,
    OUT_DIR,
    TEXT,
    WHITE,
    YELLOW,
    draw_lamp,
    draw_output_cell,
    draw_xiaoguang,
)


ROOT = Path(__file__).resolve().parent
FRAME_DIR = ROOT / "exports" / "frames" / "xiaoguang_cases"
OUT_VIDEO = OUT_DIR / "xiaoguang_three_cases_v2_silent_720p20.mp4"
POSTER = COVER_DIR / "xiaoguang_three_cases_v2_poster.jpg"

W, H = 1280, 720
FPS = 20
TOTAL_FRAMES = 540
CASE_FRAMES = TOTAL_FRAMES // 3


CASES = [
    {
        "number": "1",
        "title": "只亮一盏",
        "tag": "没有同伴",
        "body": "地上留下一点亮痕；肚子保持不亮。",
        "points": ("地上留下一点亮痕", "肚子里的灯不亮"),
        "top": True,
        "bottom": False,
        "incoming": False,
        "trace": 1,
        "belly": False,
        "count": 1,
        "mood": "curious",
    },
    {
        "number": "2",
        "title": "亮着两盏",
        "tag": "刚好成对",
        "body": "地上不留亮痕；肚子里的小灯亮起。",
        "points": ("地上不留亮痕", "肚子里的灯亮起"),
        "top": True,
        "bottom": True,
        "incoming": False,
        "trace": 0,
        "belly": True,
        "count": 2,
        "mood": "focused",
    },
    {
        "number": "3",
        "title": "两盏加一团光",
        "tag": "先配掉一对",
        "body": "先配掉一对；剩下一盏留在地上。",
        "points": ("剩下一盏留在地上", "肚子里的灯继续亮"),
        "top": True,
        "bottom": True,
        "incoming": True,
        "trace": 1,
        "belly": True,
        "count": 2,
        "mood": "happy",
    },
]


def smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def draw_case_tabs(draw: ImageDraw.ImageDraw, active: int) -> None:
    x0 = 690
    y0 = 142
    for index, item in enumerate(CASES):
        y = y0 + index * 116
        fill = (20, 36, 62) if index == active else (10, 17, 31)
        outline = (78, 120, 178) if index == active else (36, 54, 82)
        text_fill = TEXT if index == active else MUTED
        draw.rounded_rectangle((x0, y, x0 + 390, y + 94), radius=12, fill=fill, outline=outline, width=2)
        badge_fill = YELLOW if index == active else (38, 58, 86)
        badge_text = (12, 22, 40) if index == active else MUTED
        draw.ellipse((x0 + 20, y + 20, x0 + 58, y + 58), fill=badge_fill, outline=(120, 158, 205), width=1)
        draw.text((x0 + 32, y + 26), item["number"], fill=badge_text, font=FONT_LABEL)
        draw.text((x0 + 76, y + 16), f"{item['title']}：{item['tag']}", fill=text_fill, font=FONT_LABEL)
        p1, p2 = item["points"]
        draw.text((x0 + 78, y + 45), f"- {p1}", fill=MUTED, font=FONT_SMALL)
        draw.text((x0 + 78, y + 68), f"- {p2}", fill=MUTED, font=FONT_SMALL)


def draw_incoming_light(draw: ImageDraw.ImageDraw, x: float, y: float, alpha: int) -> None:
    draw.rounded_rectangle((x - 48, y - 54, x + 48, y - 28), radius=8, fill=(12, 22, 40), outline=(54, 82, 122), width=1)
    draw.text((x - 34, y - 51), "带来的光", fill=MUTED, font=FONT_SMALL)
    for radius, a in ((24, 24), (16, 55), (9, 118)):
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*YELLOW, int(a * alpha / 255)))
    draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(*YELLOW, alpha), outline=WHITE, width=2)


def render_frame(frame: int) -> Image.Image:
    img = Image.new("RGBA", (W, H), (*BG, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    active = min(2, frame // CASE_FRAMES)
    local = (frame - active * CASE_FRAMES) / CASE_FRAMES
    item = CASES[active]
    reveal_t = smoothstep((local - 0.20) / 0.28)
    carry_t = smoothstep((local - 0.42) / 0.24)

    draw.text((68, 34), "小光先处理三种灯况", fill=TEXT, font=FONT_TITLE)
    draw.text((70, 86), "每一种都只看当前这一格，然后留下结果。", fill=MUTED, font=FONT_SUB)

    board = (88, 132, 640, 590)
    draw.rounded_rectangle(board, radius=10, fill=(10, 17, 31), outline=(27, 40, 61), width=1)
    x0, y0, x1, y1 = board
    for x in range(x0 + 92, x1 - 40, 92):
        draw.line((x, y0 + 42, x, y1 - 42), fill=GRID, width=1)
    for y in (214, 302, 424, 520):
        draw.line((x0 + 44, y, x1 - 44, y), fill=GRID, width=1)

    draw.text((x0 + 34, 202), "第一排灯", fill=MUTED, font=FONT_SMALL)
    draw.text((x0 + 34, 290), "第二排灯", fill=MUTED, font=FONT_SMALL)
    draw.text((x0 + 34, 508), "留下的痕迹", fill=MUTED, font=FONT_SMALL)

    cx = 410
    draw.rounded_rectangle((cx - 68, y0 + 44, cx + 68, y1 - 44), radius=12, fill=(24, 42, 69, 96), outline=(78, 120, 178), width=2)
    draw_lamp(img, cx, 214, item["top"])
    draw_lamp(img, cx, 302, item["bottom"])
    if item["incoming"]:
        draw_incoming_light(draw, cx - 120, 382, int(190 + 65 * carry_t))
        draw.line((cx - 86, 382, cx - 28, 382), fill=(*YELLOW, 150), width=3)
        draw.polygon([(cx - 28, 382), (cx - 42, 373), (cx - 42, 391)], fill=(*YELLOW, 150))

    draw_output_cell(draw, cx, 520, item["trace"] if reveal_t > 0.55 else None)
    if item["trace"] and reveal_t > 0.55:
        draw.ellipse((cx - 38, 520 - 38, cx + 38, 520 + 38), outline=(*LIME, 80), width=3)

    robot_x = 1120
    robot_y = 488
    draw_xiaoguang(
        img,
        robot_x,
        robot_y,
        belly_on=item["belly"] and carry_t > 0.35,
        mood=item["mood"],
        sensed_count=item["count"],
        blink=(frame % 70) / 70,
        scale=0.50,
    )

    draw = ImageDraw.Draw(img, "RGBA")
    draw_case_tabs(draw, active)

    if active == 0:
        line = "第一种：只亮一盏。没有同伴，就把这一盏留在地上。"
    elif active == 1:
        line = "第二种：亮着两盏。刚好成对，地上不留亮痕。"
    else:
        line = "第三种：再加一团带来的光。剩下一盏留在地上，肚子里的灯继续亮。"
    draw.rounded_rectangle((214, 610, 1066, 666), radius=12, fill=(15, 27, 48), outline=(47, 72, 110), width=1)
    draw.text((248, 626), line, fill=WHITE, font=FONT_LABEL)
    return img.convert("RGB")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    if FRAME_DIR.exists():
        shutil.rmtree(FRAME_DIR)
    FRAME_DIR.mkdir(parents=True, exist_ok=True)

    poster = None
    for frame in range(TOTAL_FRAMES):
        image = render_frame(frame)
        image.save(FRAME_DIR / f"frame_{frame:04d}.png")
        if frame == CASE_FRAMES + 80:
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
