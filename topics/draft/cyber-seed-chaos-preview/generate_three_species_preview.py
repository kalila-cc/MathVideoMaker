from __future__ import annotations

import math
import shutil
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "exports" / "final"
COVER_DIR = ROOT / "exports" / "covers"
FRAME_DIR = ROOT / "exports" / "frames" / "three_species_preview"
OUT_VIDEO = OUT_DIR / "three_cyber_species_balance_preview_v3_720p20.mp4"
POSTER = COVER_DIR / "three_cyber_species_balance_preview_v3_poster.jpg"

W, H = 1280, 720
FPS = 20
TOTAL_FRAMES = 300
SIM_STEPS = 220

BG = (7, 11, 20)
PANEL = (10, 17, 31)
GRID = (33, 47, 70)
TEXT = (232, 239, 255)
MUTED = (139, 160, 195)
CYAN = (24, 216, 255)
VIOLET = (190, 72, 255)
AMBER = (255, 173, 64)
WHITE = (255, 255, 255)

COLORS = {
    0: BG,
    1: CYAN,
    2: VIOLET,
    3: AMBER,
}

NAMES = {
    1: "小光",
    2: "小影",
    3: "小焰",
}

# 1 beats 2, 2 beats 3, 3 beats 1.
PREDATOR_OF = {
    1: 3,
    2: 1,
    3: 2,
}

BOARD_BOX = (222, 150, 1058, 652)


def font(size: int, bold: bool = False):
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
FONT_RULE = font(18, True)
FONT_SMALL = font(16)
FONT_MONO = font(18)


def hash01(x: int, y: int, salt: int) -> float:
    value = (x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)
    value ^= value >> 13
    value = (value * 1274126177) & 0xFFFFFFFF
    return value / 0xFFFFFFFF


def make_initial_grid(width: int = 170, height: int = 110) -> np.ndarray:
    grid = np.zeros((height, width), dtype=np.uint8)
    cx = width // 2
    cy = height // 2
    centers = {
        1: (cx - 28, cy - 10),
        2: (cx + 27, cy - 8),
        3: (cx, cy + 23),
    }

    for y in range(height):
        for x in range(width):
            dx = x - cx
            dy = y - cy
            if (dx * dx) / (54 * 54) + (dy * dy) / (35 * 35) > 1.0:
                continue
            distances = {
                state: math.hypot(x - sx, y - sy)
                for state, (sx, sy) in centers.items()
            }
            state = min(distances, key=distances.get)
            if hash01(x, y, 23) < 0.27:
                state = 1 + int(hash01(x, y, 31) * 3) % 3
            grid[y, x] = state
    return grid


def neighbor_counts(grid: np.ndarray) -> dict[int, np.ndarray]:
    padded = np.pad(grid, 1, mode="constant", constant_values=0)
    result: dict[int, np.ndarray] = {}
    for state in (1, 2, 3):
        mask = (padded == state).astype(np.uint8)
        count = (
            mask[:-2, :-2]
            + mask[:-2, 1:-1]
            + mask[:-2, 2:]
            + mask[1:-1, :-2]
            + mask[1:-1, 2:]
            + mask[2:, :-2]
            + mask[2:, 1:-1]
            + mask[2:, 2:]
        )
        result[state] = count
    return result


def step_grid(grid: np.ndarray) -> np.ndarray:
    counts = neighbor_counts(grid)
    next_grid = grid.copy()

    for target in (1, 2, 3):
        predator = PREDATOR_OF[target]
        invaded = (grid == target) & (counts[predator] >= 3)
        next_grid[invaded] = predator

    return next_grid


def precompute_states() -> list[np.ndarray]:
    states = [make_initial_grid()]
    for _ in range(SIM_STEPS):
        states.append(step_grid(states[-1]))
    return states


def frame_to_step(frame_index: int) -> int:
    if frame_index < 40:
        return 0
    t = (frame_index - 40) / max(1, TOTAL_FRAMES - 41)
    eased = t * t * (3 - 2 * t)
    return min(SIM_STEPS, int(eased * SIM_STEPS))


def occupied_bounds(states: list[np.ndarray]) -> tuple[int, int, int, int]:
    ys_all = []
    xs_all = []
    for frame_index in range(TOTAL_FRAMES):
        step = frame_to_step(frame_index)
        ys, xs = np.nonzero(states[step])
        if len(xs):
            xs_all.append(xs)
            ys_all.append(ys)
    xs = np.concatenate(xs_all)
    ys = np.concatenate(ys_all)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def fit_view(bounds: tuple[int, int, int, int], grid_shape: tuple[int, int]) -> tuple[int, int, int, int, int]:
    left, top, right, bottom = bounds
    height, width = grid_shape
    margin = 8
    left = max(0, left - margin)
    top = max(0, top - margin)
    right = min(width - 1, right + margin)
    bottom = min(height - 1, bottom + margin)

    board_w = BOARD_BOX[2] - BOARD_BOX[0] - 32
    board_h = BOARD_BOX[3] - BOARD_BOX[1] - 32
    target_ratio = board_w / board_h
    view_w = right - left + 1
    view_h = bottom - top + 1
    ratio = view_w / view_h

    if ratio < target_ratio:
        wanted_w = math.ceil(view_h * target_ratio)
        extra = wanted_w - view_w
        left = max(0, left - extra // 2)
        right = min(width - 1, right + extra - extra // 2)
    else:
        wanted_h = math.ceil(view_w / target_ratio)
        extra = wanted_h - view_h
        top = max(0, top - extra // 2)
        bottom = min(height - 1, bottom + extra - extra // 2)

    view_w = right - left + 1
    view_h = bottom - top + 1
    cell = max(2, min(board_w // view_w, board_h // view_h))
    return left, top, right, bottom, cell


def draw_header(draw: ImageDraw.ImageDraw, step: int, counts: dict[int, int], view_summary: str) -> None:
    draw.text((46, 34), "三种赛博生命：互相制衡", fill=TEXT, font=FONT_TITLE)
    draw.text((48, 84), "每个格子只看邻居；天敌足够多，就会被改写。", fill=MUTED, font=FONT_SUB)
    draw.text((74, 612), f"{step:,} steps", fill=TEXT, font=FONT_MONO)
    draw.text((190, 612), view_summary, fill=MUTED, font=FONT_SMALL)

    x = 894
    y = 32
    draw.text((x, y), "制衡关系", fill=TEXT, font=FONT_RULE)
    rows = [
        (1, "压制", 2),
        (2, "压制", 3),
        (3, "压制", 1),
    ]
    yy = y + 38
    for a, verb, b in rows:
        draw.rounded_rectangle((x, yy + 4, x + 18, yy + 22), radius=4, fill=COLORS[a])
        draw.text((x + 28, yy), f"{NAMES[a]} {verb} {NAMES[b]}", fill=MUTED, font=FONT_SMALL)
        draw.text((x + 170, yy), f"{counts[a]:4d}", fill=COLORS[a], font=FONT_SMALL)
        yy += 30


def draw_grid(base: Image.Image, grid: np.ndarray, view: tuple[int, int, int, int, int], step: int) -> None:
    draw = ImageDraw.Draw(base)
    x0, y0, x1, y1 = BOARD_BOX
    draw.rounded_rectangle(BOARD_BOX, radius=10, fill=PANEL, outline=(24, 37, 58), width=1)

    left, top, right, bottom, cell = view
    view_w = right - left + 1
    view_h = bottom - top + 1
    board_w = view_w * cell
    board_h = view_h * cell
    gx0 = x0 + (x1 - x0 - board_w) // 2
    gy0 = y0 + (y1 - y0 - board_h) // 2
    draw.rectangle((gx0, gy0, gx0 + board_w, gy0 + board_h), fill=BG)

    crop = grid[top : bottom + 1, left : right + 1]
    for state in (1, 2, 3):
        ys, xs = np.nonzero(crop == state)
        color = COLORS[state]
        for px, py in zip(xs, ys):
            sx = gx0 + int(px) * cell
            sy = gy0 + int(py) * cell
            draw.rectangle((sx, sy, sx + cell - 1, sy + cell - 1), fill=color)

    line_color = GRID
    for xx in range(view_w + 1):
        sx = gx0 + xx * cell
        draw.line((sx, gy0, sx, gy0 + board_h), fill=line_color)
    for yy in range(view_h + 1):
        sy = gy0 + yy * cell
        draw.line((gx0, sy, gx0 + board_w, sy), fill=line_color)

    x0, y0, x1, y1 = BOARD_BOX
    draw.rounded_rectangle((x0 + 18, y1 - 50, x0 + 458, y1 - 10), radius=20, fill=(15, 27, 48), outline=(35, 53, 82))
    draw.text((x0 + 40, y1 - 42), "同一套邻域规则，三种生命互相改写", fill=TEXT, font=FONT_SMALL)


def render_frame(states: list[np.ndarray], view: tuple[int, int, int, int, int], frame_index: int, view_summary: str) -> Image.Image:
    step = frame_to_step(frame_index)
    grid = states[step]
    img = Image.new("RGBA", (W, H), (*BG, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, H), fill=BG)
    counts = {state: int((grid == state).sum()) for state in (1, 2, 3)}
    draw_header(draw, step, counts, view_summary)
    draw_grid(img, grid, view, step)
    return img.convert("RGB")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    if FRAME_DIR.exists():
        shutil.rmtree(FRAME_DIR)
    FRAME_DIR.mkdir(parents=True, exist_ok=True)

    states = precompute_states()
    bounds = occupied_bounds(states)
    view = fit_view(bounds, states[0].shape)
    left, top, right, bottom, cell = view
    view_summary = "三色前线互相追逐"
    print(f"bounds={bounds}")
    print(f"view={view}")

    poster_frame = None
    for frame_index in range(TOTAL_FRAMES):
        frame = render_frame(states, view, frame_index, view_summary)
        frame.save(FRAME_DIR / f"frame_{frame_index:04d}.png")
        if frame_index == 246:
            poster_frame = frame.copy()
    if poster_frame is None:
        poster_frame = frame
    poster_frame.save(POSTER, quality=92)

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
