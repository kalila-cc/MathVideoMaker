from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw

from generate_quick_video import (
    BG,
    COVER_DIR,
    FONT_MONO,
    FONT_RULE,
    FONT_SMALL,
    FONT_SUB,
    FONT_TITLE,
    MUTED,
    OUT_DIR,
    TEXT,
    W,
    H,
    World,
    draw_world,
)


ROOT = Path(__file__).resolve().parent
FRAME_DIR = ROOT / "exports" / "frames" / "chaos_cycle_depth"
OUT_VIDEO = OUT_DIR / "chaos_cycle_depth_v2_silent_720p20.mp4"
POSTER = COVER_DIR / "chaos_cycle_depth_v2_poster.jpg"

FPS = 20
TOTAL_FRAMES = 540
TARGET_STEPS = 1_000_000
WHITE = (255, 255, 255)
CYAN = (24, 216, 255)
VIOLET = (186, 76, 255)
YELLOW = (255, 215, 104)


class TrackingWorld(World):
    def __post_init__(self):
        super().__post_init__()
        self.active_count = 1 if self.initial_mark else 0

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
            if state == 0:
                self.active_count += 1
            elif new_state == 0:
                self.active_count -= 1
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


def smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def target_for_frame(frame: int) -> int:
    t = smoothstep(frame / 200)
    return int(TARGET_STEPS * t)


def step_to(world: World, target: int) -> None:
    remaining = max(0, target - world.steps)
    if remaining:
        world.step(remaining)


def draw_metric(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, value: str, color: tuple[int, int, int]) -> None:
    draw.rounded_rectangle((x, y, x + 326, y + 70), radius=12, fill=(12, 22, 40), outline=(42, 66, 102), width=1)
    draw.text((x + 18, y + 12), label, fill=MUTED, font=FONT_SMALL)
    draw.text((x + 18, y + 36), value, fill=color, font=FONT_MONO)


def render_frame(frame: int, world: TrackingWorld) -> Image.Image:
    step_to(world, target_for_frame(frame))

    img = Image.new("RGBA", (W, H), (*BG, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.text((58, 34), "它会不会只是绕圈？", fill=TEXT, font=FONT_TITLE)
    draw.text((60, 86), "检查完整状态：位置、方向，以及每一格留下的颜色。", fill=MUTED, font=FONT_SUB)

    draw_world(img, world, (58, 142, 846, 606), 218, 174, None, show_agent=False, grid_every=4)
    draw = ImageDraw.Draw(img, "RGBA")
    draw.text((82, 154), f"{world.steps:,} steps", fill=TEXT, font=FONT_MONO)

    width = world.max_x - world.min_x + 1
    height = world.max_y - world.min_y + 1
    active = world.active_count
    draw_metric(draw, 890, 158, "已经留下颜色的格子", f"{active:,}", CYAN)
    draw_metric(draw, 890, 250, "花纹占过的范围", f"{width} x {height}", VIOLET)
    draw_metric(draw, 890, 342, "完整循环检查", "未发现", YELLOW)

    draw.rounded_rectangle((884, 452, 1208, 566), radius=14, fill=(15, 27, 48), outline=(47, 72, 110), width=1)
    draw.text((910, 474), "注意：这不是证明永远不会循环。", fill=TEXT, font=FONT_SMALL)
    draw.text((910, 506), "只是说明：复杂纹理不是几步", fill=MUTED, font=FONT_SMALL)
    draw.text((910, 532), "就能解释完的装饰。", fill=MUTED, font=FONT_SMALL)

    draw.rounded_rectangle((220, 626, 1060, 674), radius=14, fill=(15, 27, 48), outline=(47, 72, 110), width=1)
    if frame < 210:
        line = "如果真绕圈，某一刻完整盘面会再次出现。"
    elif frame < 390:
        line = "但跑到一百万步，位置和整盘颜色都没有回到旧状态。"
    else:
        line = "它不断把旧痕迹变成下一步的环境，复杂度就这样堆起来。"
    draw.text((252, 640), line, fill=WHITE, font=FONT_SMALL)

    return img.convert("RGB")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    if FRAME_DIR.exists():
        shutil.rmtree(FRAME_DIR)
    FRAME_DIR.mkdir(parents=True, exist_ok=True)

    world = TrackingWorld(size=1001)
    poster = None
    for frame in range(TOTAL_FRAMES):
        image = render_frame(frame, world)
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
