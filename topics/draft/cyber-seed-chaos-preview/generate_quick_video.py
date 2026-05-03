from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "exports" / "final"
COVER_DIR = ROOT / "exports" / "covers"
FRAME_DIR = ROOT / "exports" / "frames" / "cyber_seed_quick_preview"
OUT_VIDEO = OUT_DIR / "cyber_seed_pulse_board_fit_preview_v10_720p20.mp4"
POSTER = COVER_DIR / "cyber_seed_pulse_board_fit_preview_v10_poster.jpg"

W, H = 1280, 720
FPS = 20
TOTAL_FRAMES = 300
SLOW_END = 120
SLOW_HOLD = 6

BG = (7, 11, 20)
PANEL = (10, 17, 31)
GRID = (31, 45, 68)
TEXT = (232, 239, 255)
MUTED = (139, 160, 195)
CYAN = (24, 216, 255)
VIOLET = (186, 76, 255)
AGENT = (255, 238, 115)
WHITE = (255, 255, 255)
AGENT_EDGE = (255, 252, 195)
AGENT_SHADOW = (152, 104, 255)


@dataclass
class World:
    size: int = 901
    initial_mark: bool = False

    def __post_init__(self):
        self.grid = [[0] * self.size for _ in range(self.size)]
        self.x = self.size // 2
        self.y = self.size // 2
        self.direction = 0
        self.steps = 0
        self.last_event = None
        self.min_x = self.x
        self.max_x = self.x
        self.min_y = self.y
        self.max_y = self.y
        if self.initial_mark:
            self.grid[self.y][self.x] = 1

    def step(self, count: int = 1):
        for _ in range(count):
            if self.x < 2 or self.y < 2 or self.x >= self.size - 2 or self.y >= self.size - 2:
                return
            state = self.grid[self.y][self.x]
            turn = (1, 0, -1)[state]
            old_x = self.x
            old_y = self.y
            old_direction = self.direction
            self.direction = (self.direction + turn) % 4
            new_state = (state + 1) % 3
            self.grid[self.y][self.x] = new_state
            if self.direction == 0:
                self.y -= 1
            elif self.direction == 1:
                self.x += 1
            elif self.direction == 2:
                self.y += 1
            else:
                self.x -= 1
            self.steps += 1
            self.min_x = min(self.min_x, old_x, self.x)
            self.max_x = max(self.max_x, old_x, self.x)
            self.min_y = min(self.min_y, old_y, self.y)
            self.max_y = max(self.max_y, old_y, self.y)
            self.last_event = {
                "x": old_x,
                "y": old_y,
                "from_state": state,
                "to_state": new_state,
                "turn": turn,
                "old_direction": old_direction,
                "new_direction": self.direction,
                "next_x": self.x,
                "next_y": self.y,
            }


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


FONT_TITLE = font(36, True)
FONT_SUB = font(20)
FONT_SMALL = font(17)
FONT_RULE = font(19, True)
FONT_MONO = font(19)


def draw_glow(draw_img: Image.Image, xy: tuple[float, float], radius: int, color: tuple[int, int, int]):
    glow = Image.new("RGBA", draw_img.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    cx, cy = xy
    for scale, alpha in ((3.4, 35), (2.2, 55), (1.35, 95)):
        r = radius * scale
        g.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*color, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.55))
    draw_img.alpha_composite(glow)


@lru_cache(maxsize=128)
def cyber_life_sprite(size: int, direction: int) -> Image.Image:
    size = max(8, int(size))
    cx = size / 2
    cy = size / 2
    sprite = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)

    unit = size / 100
    leg_w = max(2, int(size * 0.055))
    outline_w = max(2, int(size * 0.045))
    body = [
        (cx, cy - 34 * unit),
        (cx + 26 * unit, cy - 15 * unit),
        (cx + 18 * unit, cy + 29 * unit),
        (cx, cy + 41 * unit),
        (cx - 18 * unit, cy + 29 * unit),
        (cx - 26 * unit, cy - 15 * unit),
    ]

    # "Xiao Guang": a small cyber lifeform constrained inside one grid square.
    draw.line((cx - 14 * unit, cy - 26 * unit, cx - 31 * unit, cy - 43 * unit), fill=CYAN, width=leg_w)
    draw.line((cx + 14 * unit, cy - 26 * unit, cx + 31 * unit, cy - 43 * unit), fill=CYAN, width=leg_w)
    draw.ellipse((cx - 35 * unit, cy - 47 * unit, cx - 27 * unit, cy - 39 * unit), fill=CYAN)
    draw.ellipse((cx + 27 * unit, cy - 47 * unit, cx + 35 * unit, cy - 39 * unit), fill=CYAN)
    draw.line((cx - 21 * unit, cy + 2 * unit, cx - 38 * unit, cy + 10 * unit), fill=CYAN, width=leg_w)
    draw.line((cx + 21 * unit, cy + 2 * unit, cx + 38 * unit, cy + 10 * unit), fill=CYAN, width=leg_w)
    draw.line((cx - 15 * unit, cy + 27 * unit, cx - 30 * unit, cy + 39 * unit), fill=VIOLET, width=leg_w)
    draw.line((cx + 15 * unit, cy + 27 * unit, cx + 30 * unit, cy + 39 * unit), fill=VIOLET, width=leg_w)

    draw.polygon(body, fill=AGENT, outline=AGENT_EDGE)
    draw.line(body + [body[0]], fill=AGENT_EDGE, width=outline_w, joint="curve")
    draw.rounded_rectangle(
        (cx - 18 * unit, cy - 22 * unit, cx + 18 * unit, cy - 4 * unit),
        radius=max(2, int(size * 0.08)),
        fill=(11, 32, 50),
        outline=CYAN,
        width=max(1, int(size * 0.025)),
    )
    eye_r = max(2, int(size * 0.035))
    draw.ellipse((cx - 8 * unit - eye_r, cy - 13 * unit - eye_r, cx - 8 * unit + eye_r, cy - 13 * unit + eye_r), fill=CYAN)
    draw.ellipse((cx + 8 * unit - eye_r, cy - 13 * unit - eye_r, cx + 8 * unit + eye_r, cy - 13 * unit + eye_r), fill=CYAN)
    draw.line((cx, cy + 3 * unit, cx, cy + 28 * unit), fill=AGENT_SHADOW, width=max(2, int(size * 0.055)))
    draw.line((cx, cy + 12 * unit, cx + 12 * unit, cy + 12 * unit), fill=AGENT_SHADOW, width=max(1, int(size * 0.03)))
    draw.line((cx, cy + 22 * unit, cx - 11 * unit, cy + 22 * unit), fill=AGENT_SHADOW, width=max(1, int(size * 0.03)))
    draw.polygon(
        [(cx, cy - 41 * unit), (cx - 7 * unit, cy - 31 * unit), (cx + 7 * unit, cy - 31 * unit)],
        fill=WHITE,
    )

    if direction:
        sprite = sprite.rotate(-90 * direction, resample=Image.Resampling.BICUBIC, expand=True)
    return sprite


def draw_cyber_life(base: Image.Image, x: float, y: float, cell_size: int, direction: int):
    glow_radius = max(5, int(cell_size * 0.33))
    draw_glow(base, (x, y), glow_radius, AGENT)
    draw_glow(base, (x, y), max(4, int(cell_size * 0.18)), CYAN)
    sprite_size = max(8, int(cell_size * 0.92))
    sprite = cyber_life_sprite(sprite_size, direction)
    base.alpha_composite(sprite, (int(x - sprite.width / 2), int(y - sprite.height / 2)))


def draw_panel_background(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str | None = None):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=10, fill=PANEL, outline=(24, 37, 58), width=1)
    if title:
        draw.text((x0 + 18, y0 + 14), title, fill=TEXT, font=FONT_RULE)


def draw_rules(draw: ImageDraw.ImageDraw, x: int, y: int):
    draw.text((x, y), "本能规则", fill=TEXT, font=FONT_RULE)
    rows = [
        ("暗格", "右转", "点亮青色", (44, 58, 84)),
        ("青格", "直走", "升为紫色", CYAN),
        ("紫格", "左转", "熄灭回暗", VIOLET),
    ]
    yy = y + 34
    for label, turn, result, color in rows:
        draw.rounded_rectangle((x, yy + 3, x + 18, yy + 21), radius=4, fill=color)
        draw.text((x + 30, yy), f"{label}  ->  {turn}  ->  {result}", fill=MUTED, font=FONT_SMALL)
        yy += 30


def state_name(state: int) -> str:
    return ("暗格", "青格", "紫格")[state]


def state_result(state: int) -> str:
    return ("点亮青色", "升为紫色", "熄灭回暗")[state]


def state_color(state: int) -> tuple[int, int, int]:
    return ((44, 58, 84), CYAN, VIOLET)[state]


def turn_name(turn: int) -> str:
    return {1: "右转", 0: "直走", -1: "左转"}[turn]


def direction_name(direction: int) -> str:
    return ("向上", "向右", "向下", "向左")[direction]


def draw_step_card(draw: ImageDraw.ImageDraw, world: World, box: tuple[int, int, int, int]):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=12, fill=(12, 22, 40), outline=(36, 56, 88), width=1)
    draw.text((x0 + 20, y0 + 18), f"第 {world.steps:,} 步", fill=TEXT, font=FONT_RULE)
    if not world.last_event:
        draw.text((x0 + 20, y0 + 56), "种子还没有移动。", fill=MUTED, font=FONT_SMALL)
        return

    event = world.last_event
    row_y = y0 + 58
    draw.rounded_rectangle((x0 + 20, row_y + 2, x0 + 42, row_y + 24), radius=5, fill=state_color(event["from_state"]))
    draw.text((x0 + 54, row_y), f"脚下是 {state_name(event['from_state'])}", fill=TEXT, font=FONT_SMALL)
    draw.text((x0 + 20, row_y + 36), f"{turn_name(event['turn'])}，{state_result(event['from_state'])}", fill=TEXT, font=FONT_SMALL)
    draw.text((x0 + 20, row_y + 72), f"方向：{direction_name(event['old_direction'])} -> {direction_name(event['new_direction'])}", fill=MUTED, font=FONT_SMALL)


def draw_world(
    base: Image.Image,
    world: World,
    box: tuple[int, int, int, int],
    cells_w: int,
    cells_h: int,
    title: str | None = None,
    show_agent: bool = True,
    show_event: bool = False,
    grid_every: int = 8,
):
    draw = ImageDraw.Draw(base)
    draw_panel_background(draw, box, title)
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

    cx = world.size // 2
    cy = world.size // 2
    left = cx - cells_w // 2
    top = cy - cells_h // 2

    draw.rectangle((gx0, gy0, gx0 + grid_w, gy0 + grid_h), fill=BG)

    for yy in range(cells_h):
        row = world.grid[top + yy]
        py = gy0 + yy * cell
        for xx in range(cells_w):
            state = row[left + xx]
            if state:
                color = CYAN if state == 1 else VIOLET
                px = gx0 + xx * cell
                draw.rectangle((px, py, px + cell - 1, py + cell - 1), fill=color)

    grid_every = max(1, grid_every)
    for xx in range(0, cells_w + 1, grid_every):
        px = gx0 + xx * cell
        draw.line((px, gy0, px, gy0 + grid_h), fill=GRID, width=1)
    for yy in range(0, cells_h + 1, grid_every):
        py = gy0 + yy * cell
        draw.line((gx0, py, gx0 + grid_w, py), fill=GRID, width=1)

    if show_event and world.last_event:
        event = world.last_event
        sx = event["x"]
        sy = event["y"]
        if left <= sx < left + cells_w and top <= sy < top + cells_h:
            px = gx0 + (sx - left) * cell
            py = gy0 + (sy - top) * cell
            draw.rectangle((px, py, px + cell - 1, py + cell - 1), outline=AGENT, width=max(2, cell // 8))

    if show_agent and left <= world.x < left + cells_w and top <= world.y < top + cells_h:
        cell_x = gx0 + (world.x - left) * cell
        cell_y = gy0 + (world.y - top) * cell
        ax = cell_x + cell / 2
        ay = cell_y + cell / 2
        if cell >= 14:
            draw.rounded_rectangle(
                (cell_x + 2, cell_y + 2, cell_x + cell - 3, cell_y + cell - 3),
                radius=max(2, cell // 6),
                outline=AGENT,
                width=max(2, cell // 12),
            )
            draw_cyber_life(base, ax, ay, cell, world.direction)
        else:
            inset = max(1, cell // 4)
            draw.rectangle(
                (cell_x + inset, cell_y + inset, cell_x + cell - inset, cell_y + cell - inset),
                fill=AGENT,
                outline=CYAN,
            )


def fast_steps_for_frame(i: int) -> int:
    local = i - SLOW_END
    if local < 20:
        return 8
    if local < 55:
        return 32
    if local < 110:
        return 120
    if local < 190:
        return 260
    return 560


FAST_VIEW_STAGES = (
    (120, 68),
    (180, 102),
)


def fast_view_cells(world: World) -> tuple[int, int]:
    center = world.size // 2
    half_w = max(abs(world.min_x - center), abs(world.max_x - center))
    half_h = max(abs(world.min_y - center), abs(world.max_y - center))
    margin = 12
    for cells_w, cells_h in FAST_VIEW_STAGES:
        if half_w + margin <= cells_w // 2 and half_h + margin <= cells_h // 2:
            return cells_w, cells_h
    return FAST_VIEW_STAGES[-1]


def render_frame(i: int, single: World):
    img = Image.new("RGBA", (W, H), (*BG, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, H), fill=BG)

    if i < SLOW_END:
        if i % SLOW_HOLD == 0:
            single.step(1)
        draw.text((46, 34), "第一阶段：小光一步一步像在乱走", fill=TEXT, font=FONT_TITLE)
        draw.text((48, 84), "其实没有随机数。小光只读取脚下颜色，转向，改写颜色，再前进一步。", fill=MUTED, font=FONT_SUB)
        draw_world(img, single, (54, 150, 804, 654), 15, 9, None, show_event=True, grid_every=1)
        draw = ImageDraw.Draw(img)
        draw_rules(draw, 900, 138)
        draw_step_card(draw, single, (892, 318, 1238, 474))
        draw.rounded_rectangle((892, 508, 1238, 616), radius=12, fill=(12, 22, 40), outline=(36, 56, 88), width=1)
        draw.text((912, 528), "为什么会像随机？", fill=TEXT, font=FONT_RULE)
        draw.text((912, 566), "它不断踩回自己的旧痕迹，", fill=MUTED, font=FONT_SMALL)
        draw.text((912, 592), "环境记忆会反过来改变下一步。", fill=MUTED, font=FONT_SMALL)
    else:
        single.step(fast_steps_for_frame(i))
        cells_w, cells_h = fast_view_cells(single)
        draw.text((46, 34), "第二阶段：拉远视野，高速迭代", fill=TEXT, font=FONT_TITLE)
        draw.text((48, 84), "同一个小光、同一套规则，每帧推进几十到几百步，整体纹理开始长出来。", fill=MUTED, font=FONT_SUB)
        draw_rules(draw, 930, 34)
        draw_world(img, single, (74, 150, 1114, 596), cells_w, cells_h, None, grid_every=1)
        draw = ImageDraw.Draw(img)
        draw.text((70, 150), f"{single.steps:,} steps", fill=TEXT, font=FONT_MONO)
        draw.rounded_rectangle((96, 604, 486, 644), radius=20, fill=(15, 27, 48), outline=(35, 53, 82))
        draw.text((118, 612), "看起来乱，但每一步都可重放", fill=TEXT, font=FONT_SMALL)

    return img.convert("RGB")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    if FRAME_DIR.exists():
        shutil.rmtree(FRAME_DIR)
    FRAME_DIR.mkdir(parents=True, exist_ok=True)

    single = World()

    poster_frame = None
    for i in range(TOTAL_FRAMES):
        frame = render_frame(i, single)
        frame.save(FRAME_DIR / f"frame_{i:04d}.png")
        if i == 252:
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
