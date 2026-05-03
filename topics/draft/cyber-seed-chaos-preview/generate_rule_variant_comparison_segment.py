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
FRAME_DIR = ROOT / "exports" / "frames" / "rule_variant_comparison"
OUT_VIDEO = OUT_DIR / "rule_variant_comparison_v1_silent_720p20.mp4"
POSTER = COVER_DIR / "rule_variant_comparison_v1_poster.jpg"

FPS = 20
TOTAL_FRAMES = 360
WHITE = (255, 255, 255)


class RuleWorld(World):
    def __init__(self, turns: tuple[int, int, int], *args, **kwargs):
        self.turns = turns
        super().__init__(*args, **kwargs)

    def step(self, count: int = 1):
        for _ in range(count):
            if self.x < 2 or self.y < 2 or self.x >= self.size - 2 or self.y >= self.size - 2:
                return
            state = self.grid[self.y][self.x]
            turn = self.turns[state]
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


def steps_for_frame(frame: int) -> int:
    if frame < 30:
        return 24
    if frame < 95:
        return 90
    if frame < 220:
        return 190
    return 340


def draw_rule_badge(draw: ImageDraw.ImageDraw, x: int, y: int, title: str, green_turn: str) -> None:
    draw.rounded_rectangle((x, y, x + 430, y + 78), radius=12, fill=(12, 22, 40), outline=(42, 66, 102), width=1)
    draw.text((x + 18, y + 13), title, fill=TEXT, font=FONT_RULE)
    rows = [
        ("暗格", "右转", (44, 58, 84)),
        ("青格", green_turn, CYAN),
        ("紫格", "左转", VIOLET),
    ]
    xx = x + 18
    yy = y + 45
    for label, turn, color in rows:
        draw.rounded_rectangle((xx, yy + 3, xx + 16, yy + 19), radius=4, fill=color)
        draw.text((xx + 22, yy), f"{label}{turn}", fill=MUTED, font=FONT_SMALL)
        xx += 126


def render_frame(frame: int, original: RuleWorld, changed: RuleWorld) -> Image.Image:
    img = Image.new("RGBA", (W, H), (*BG, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    original.step(steps_for_frame(frame))
    changed.step(steps_for_frame(frame))

    draw.text((58, 34), "只改一条，花纹就换了", fill=TEXT, font=FONT_TITLE)
    draw.text((60, 86), "左边青格直走；右边只把青格改成左转。其他处理不变。", fill=MUTED, font=FONT_SUB)

    draw_world(img, original, (64, 154, 604, 560), 96, 72, "规则 A", show_agent=False, grid_every=2)
    draw_world(img, changed, (676, 154, 1216, 560), 96, 72, "规则 B", show_agent=False, grid_every=2)
    draw = ImageDraw.Draw(img, "RGBA")
    draw.text((92, 212), f"{original.steps:,} steps", fill=TEXT, font=FONT_MONO)
    draw.text((704, 212), f"{changed.steps:,} steps", fill=TEXT, font=FONT_MONO)

    draw_rule_badge(draw, 92, 594, "规则 A", "直走")
    draw_rule_badge(draw, 758, 594, "规则 B", "左转")
    draw.line((623, 258, 657, 258), fill=(87, 125, 170), width=2)
    draw.text((585, 282), "只差这一条", fill=MUTED, font=FONT_SMALL)

    return img.convert("RGB")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    if FRAME_DIR.exists():
        shutil.rmtree(FRAME_DIR)
    FRAME_DIR.mkdir(parents=True, exist_ok=True)

    original = RuleWorld((1, 0, -1))
    changed = RuleWorld((1, -1, -1))
    poster = None
    for frame in range(TOTAL_FRAMES):
        image = render_frame(frame, original, changed)
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
