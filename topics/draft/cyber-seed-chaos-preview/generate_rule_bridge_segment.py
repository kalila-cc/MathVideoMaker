from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw

from generate_quick_video import BG, COVER_DIR, CYAN, FONT_SMALL, FONT_SUB, FONT_TITLE, MUTED, OUT_DIR, PANEL, TEXT, VIOLET, W, H


ROOT = Path(__file__).resolve().parent
FRAME_DIR = ROOT / "exports" / "frames" / "rule_bridge_segment"
OUT_VIDEO = OUT_DIR / "rule_skeleton_bridge_v10_silent_720p20.mp4"
POSTER = COVER_DIR / "rule_skeleton_bridge_v10_poster.jpg"

FPS = 20
TOTAL_FRAMES = 460
WHITE = (255, 255, 255)
YELLOW = (255, 215, 104)
LIME = (112, 255, 178)
GRID = (35, 49, 73)
WALL = (16, 28, 48)
ROOM_EDGE = (54, 88, 132)
TRACE_GREEN = (104, 244, 172)


def smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def draw_card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, body: str, color: tuple[int, int, int]) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=12, fill=(12, 22, 40), outline=(50, 78, 118), width=2)
    draw.rounded_rectangle((x0 + 18, y0 + 18, x0 + 48, y0 + 48), radius=8, fill=color)
    draw.text((x0 + 64, y0 + 16), title, fill=TEXT, font=FONT_SUB)
    draw.text((x0 + 64, y0 + 54), body, fill=MUTED, font=FONT_SMALL)


def draw_arrow(draw: ImageDraw.ImageDraw, x0: int, y: int, x1: int) -> None:
    draw.line((x0, y, x1, y), fill=(105, 145, 190), width=3)
    draw.polygon([(x1, y), (x1 - 12, y - 7), (x1 - 12, y + 7)], fill=(105, 145, 190))


def draw_rule_triplet(draw: ImageDraw.ImageDraw, y: int, mode: str) -> None:
    if mode == "chaos":
        cards = [
            ("看一格", "只看脚下颜色", (44, 58, 84)),
            ("改一格", "把这一格换色", CYAN),
            ("走一步", "方向跟着改变", VIOLET),
        ]
    elif mode == "xiaoguang":
        cards = [
            ("看见光", "只看当前这一格", YELLOW),
            ("留痕迹", "或者把光带走", LIME),
            ("去隔壁", "照样处理", CYAN),
        ]
    else:
        cards = [
            ("看眼前", "只看这一小块", (44, 58, 84)),
            ("动一下", "只动当前位置", LIME),
            ("留下变化", "下一步会碰见它", YELLOW),
        ]

    boxes = [(116, y, 376, y + 112), (510, y, 770, y + 112), (904, y, 1164, y + 112)]
    for box, (title, body, color) in zip(boxes, cards):
        draw_card(draw, box, title, body, color)
    draw_arrow(draw, 392, y + 56, 494)
    draw_arrow(draw, 786, y + 56, 888)


def draw_soft_grid(draw: ImageDraw.ImageDraw) -> None:
    for x in range(96, 1185, 54):
        draw.line((x, 150, x, 570), fill=(*GRID, 62), width=1)
    for y in range(150, 571, 54):
        draw.line((96, y, 1184, y), fill=(*GRID, 62), width=1)


def draw_bulb(base: Image.Image, cx: int, cy: int, on: bool, alpha: int = 255, scale: float = 1.0) -> None:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(overlay, "RGBA")
    r = int(14 * scale)
    glow = int(42 * scale)
    if on:
        for radius, factor in ((glow, 0.16), (int(glow * 0.65), 0.24), (int(glow * 0.38), 0.36)):
            glow_draw.ellipse(
                (cx - radius, cy - radius, cx + radius, cy + radius),
                fill=(*YELLOW, int(alpha * factor)),
            )
        fill = (255, 244, 184, alpha)
        outline = (255, 255, 242, alpha)
    else:
        fill = (31, 47, 68, int(alpha * 0.82))
        outline = (86, 113, 143, int(alpha * 0.72))
    glow_draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=outline, width=max(1, int(2 * scale)))
    glow_draw.rectangle(
        (cx - int(6 * scale), cy + r - 1, cx + int(6 * scale), cy + r + int(8 * scale)),
        fill=(72, 92, 116, int(alpha * 0.75)),
    )
    base.alpha_composite(overlay)


def draw_lamp_room(base: Image.Image, draw: ImageDraw.ImageDraw, t: float, close: bool = False) -> None:
    alpha = int(255 * smoothstep(t))
    room = (116, 148, 1164, 586)
    x0, y0, x1, y1 = room
    center = ((x0 + x1) // 2, y0 + 92)

    draw.rounded_rectangle(room, radius=16, fill=(*WALL, int(alpha * 0.82)), outline=(*ROOM_EDGE, int(alpha * 0.92)), width=2)
    draw.line((x0 + 30, y0 + 42, x1 - 30, y0 + 42), fill=(*ROOM_EDGE, int(alpha * 0.44)), width=1)
    for x in range(x0 + 70, x1 - 50, 76):
        draw.line((x, y0 + 42, center[0], center[1]), fill=(*GRID, int(alpha * 0.36)), width=1)
    for y in range(y0 + 86, y1 - 24, 62):
        draw.line((x0 + 28, y, x1 - 28, y), fill=(*GRID, int(alpha * 0.38)), width=1)
    for x in range(x0 + 70, x1 - 50, 76):
        draw.line((x, y0 + 42, x - 38, y1 - 30), fill=(*GRID, int(alpha * 0.28)), width=1)

    panel = (204, 198, 1076, 494) if close else (254, 214, 1026, 478)
    draw.rounded_rectangle(panel, radius=18, fill=(8, 16, 31, int(alpha * 0.92)), outline=(62, 102, 150, alpha), width=2)

    label_x = panel[0] + 34
    row_a = panel[1] + 76
    row_b = panel[1] + 152
    row_trace = panel[1] + 226
    draw.text((label_x, row_a - 12), "第一排灯", fill=(*MUTED, alpha), font=FONT_SMALL)
    draw.text((label_x, row_b - 12), "第二排灯", fill=(*MUTED, alpha), font=FONT_SMALL)
    draw.text((label_x, row_trace - 12), "留下的痕迹", fill=(*MUTED, int(alpha * 0.78)), font=FONT_SMALL)

    xs = [panel[0] + 238 + i * 78 for i in range(7)]
    top_bits = [1, 0, 1, 1, 0, 1, 0]
    bottom_bits = [0, 1, 1, 0, 1, 0, 1]
    for y in (row_a, row_b):
        draw.line((xs[0] - 36, y + 26, xs[-1] + 36, y + 26), fill=(78, 112, 154, int(alpha * 0.42)), width=2)
    draw.line((xs[0] - 36, row_trace, xs[-1] + 36, row_trace), fill=(*TRACE_GREEN, int(alpha * 0.24)), width=2)

    for i, x in enumerate(xs):
        col_alpha = int(alpha * smoothstep((t * 1.25) - i * 0.07))
        draw.rounded_rectangle(
            (x - 29, panel[1] + 38, x + 29, panel[3] - 34),
            radius=9,
            fill=(24, 43, 70, int(col_alpha * 0.45)),
            outline=(74, 111, 160, int(col_alpha * 0.46)),
            width=1,
        )
        draw_bulb(base, x, row_a, bool(top_bits[i]), col_alpha, 0.88)
        draw_bulb(base, x, row_b, bool(bottom_bits[i]), col_alpha, 0.88)
        draw.ellipse((x - 10, row_trace - 10, x + 10, row_trace + 10), fill=(28, 46, 62, int(col_alpha * 0.62)), outline=(*TRACE_GREEN, int(col_alpha * 0.35)))

    if close:
        draw.rounded_rectangle((386, 606, 894, 660), radius=14, fill=(15, 27, 48, int(alpha * 0.96)), outline=(47, 72, 110, alpha))
        draw.text((436, 622), "下一幕，从这两排灯开始", fill=(*WHITE, alpha), font=FONT_SUB)
    else:
        door_alpha = int(alpha * 0.72)
        draw.rounded_rectangle((96, 226, 170, 510), radius=20, outline=(87, 133, 190, door_alpha), width=2)
        draw.line((170, 236, 226, 272), fill=(87, 133, 190, int(door_alpha * 0.6)), width=2)
        draw.line((170, 500, 226, 456), fill=(87, 133, 190, int(door_alpha * 0.6)), width=2)


def render_frame(frame: int) -> Image.Image:
    img = Image.new("RGBA", (W, H), (*BG, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    draw_soft_grid(draw)

    seconds = frame / FPS
    if seconds < 7.5:
        fade = smoothstep(seconds / 7.5)
        draw.text((68, 42), "刚才的花纹不一样", fill=TEXT, font=FONT_TITLE)
        draw.text((70, 96), "只改一条处理方式，最后就长成另一片形状。", fill=MUTED, font=FONT_SUB)
        draw_rule_triplet(draw, 286, "chaos")
        draw.rounded_rectangle((312, 600, 968, 660), radius=14, fill=(15, 27, 48), outline=(47, 72, 110))
        draw.text((350, 618), "看一格，改一格，走一步", fill=(*WHITE, int(170 + 85 * fade)), font=FONT_SUB)
    elif seconds < 13.5:
        t = smoothstep((seconds - 7.5) / 6)
        draw.text((68, 42), "但它们都只是在照做", fill=TEXT, font=FONT_TITLE)
        draw.text((70, 96), "看脚下，动一下，留个变化，然后走开。", fill=MUTED, font=FONT_SUB)
        draw_rule_triplet(draw, 286, "skeleton")
        draw.rounded_rectangle((356, 600, 924, 660), radius=14, fill=(15, 27, 48), outline=(47, 72, 110))
        draw.text((398, 618), "留下的变化，会等在下一步", fill=(*WHITE, int(160 + 95 * t)), font=FONT_SUB)
    elif seconds < 18:
        t = smoothstep((seconds - 13.5) / 4.5)
        draw.text((68, 42), "接着，换一间房间", fill=TEXT, font=FONT_TITLE)
        draw.text((70, 96), "下一段里，房间变成两排小灯泡。", fill=MUTED, font=FONT_SUB)
        draw_lamp_room(img, draw, t, close=False)
    else:
        t = smoothstep((seconds - 18) / 5)
        draw.text((68, 42), "先进入这间灯泡房", fill=TEXT, font=FONT_TITLE)
        draw.text((70, 96), "只看灯怎么亮，痕迹怎么留下。", fill=MUTED, font=FONT_SUB)
        draw_lamp_room(img, draw, 1.0, close=True)

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
        if frame == TOTAL_FRAMES - 40:
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
