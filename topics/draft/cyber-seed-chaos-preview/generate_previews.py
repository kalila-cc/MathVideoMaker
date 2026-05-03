from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Rule:
    name: str
    slug: str
    turns: tuple[int, int, int]
    steps: int
    note: str


RULES = [
    Rule("Pulse seed", "pulse_seed", (1, 0, -1), 45000, "dark:right, cyan:straight, violet:left"),
    Rule("Glitch seed", "glitch_seed", (1, -1, 0), 45000, "dark:right, cyan:left, violet:straight"),
    Rule("Drift seed", "drift_seed", (0, 1, -1), 45000, "dark:straight, cyan:right, violet:left"),
    Rule("Reflex seed", "reflex_seed", (1, -1, -1), 45000, "dark:right, cyan:left, violet:left"),
    Rule("Orbit seed", "orbit_seed", (1, 1, -1), 45000, "dark:right, cyan:right, violet:left"),
    Rule("Backlash seed", "backlash_seed", (1, 2, -1), 45000, "dark:right, cyan:back, violet:left"),
]


PALETTE = [
    (9, 13, 22),
    (30, 210, 255),
    (182, 88, 255),
]
AGENT = (255, 239, 122)
GRID = (24, 35, 54)
TEXT = (223, 232, 255)
MUTED = (126, 146, 181)


def simulate(
    rule: Rule,
    size: int = 601,
    start_offset: tuple[int, int] = (0, 0),
    start_dir: int = 0,
    initial_marks: tuple[tuple[int, int, int], ...] = (),
):
    grid = [[0] * size for _ in range(size)]
    x = size // 2 + start_offset[0]
    y = size // 2 + start_offset[1]
    for dx, dy, state in initial_marks:
        grid[y + dy][x + dx] = state
    direction = start_dir
    bounds = [x, y, x, y]
    trace: list[tuple[int, int, int]] = []

    for step in range(rule.steps):
        state = grid[y][x]
        direction = (direction + rule.turns[state]) % 4
        grid[y][x] = (state + 1) % 3
        trace.append((x, y, grid[y][x]))

        if direction == 0:
            y -= 1
        elif direction == 1:
            x += 1
        elif direction == 2:
            y += 1
        else:
            x -= 1

        if x < 2 or y < 2 or x >= size - 2 or y >= size - 2:
            break
        if x < bounds[0]:
            bounds[0] = x
        if y < bounds[1]:
            bounds[1] = y
        if x > bounds[2]:
            bounds[2] = x
        if y > bounds[3]:
            bounds[3] = y

    return grid, trace, (x, y, direction), tuple(bounds)


def crop_bounds(bounds, pad: int, size: int):
    left, top, right, bottom = bounds
    left = max(0, left - pad)
    top = max(0, top - pad)
    right = min(size - 1, right + pad)
    bottom = min(size - 1, bottom + pad)
    width = right - left + 1
    height = bottom - top + 1
    if width > height:
        diff = width - height
        top = max(0, top - diff // 2)
        bottom = min(size - 1, bottom + diff - diff // 2)
    elif height > width:
        diff = height - width
        left = max(0, left - diff // 2)
        right = min(size - 1, right + diff - diff // 2)
    return left, top, right, bottom


def render_grid(grid, agent_state, bounds, title: str, subtitle: str, out: Path, scale_to: int = 900):
    size = len(grid)
    left, top, right, bottom = crop_bounds(bounds, 20, size)
    crop_w = right - left + 1
    crop_h = bottom - top + 1
    cell = max(1, min(scale_to // crop_w, scale_to // crop_h))
    image_w = crop_w * cell
    image_h = crop_h * cell
    header_h = 110
    img = Image.new("RGB", (image_w, image_h + header_h), PALETTE[0])
    draw = ImageDraw.Draw(img)

    for gy in range(top, bottom + 1):
        row = grid[gy]
        for gx in range(left, right + 1):
            state = row[gx]
            if state:
                x0 = (gx - left) * cell
                y0 = header_h + (gy - top) * cell
                draw.rectangle((x0, y0, x0 + cell - 1, y0 + cell - 1), fill=PALETTE[state])

    for gx in range(left, right + 1, 12):
        x0 = (gx - left) * cell
        draw.line((x0, header_h, x0, header_h + image_h), fill=GRID)
    for gy in range(top, bottom + 1, 12):
        y0 = header_h + (gy - top) * cell
        draw.line((0, y0, image_w, y0), fill=GRID)

    ax, ay, direction = agent_state
    if left <= ax <= right and top <= ay <= bottom:
        cx = (ax - left + 0.5) * cell
        cy = header_h + (ay - top + 0.5) * cell
        r = max(3, cell * 2)
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=AGENT)
        vecs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        vx, vy = vecs[direction]
        draw.line((cx, cy, cx + vx * r * 2.2, cy + vy * r * 2.2), fill=(255, 255, 255), width=max(1, cell // 2))

    draw.rectangle((0, 0, image_w, header_h), fill=(10, 16, 28))
    try:
        font_title = ImageFont.truetype("arial.ttf", 34)
        font_sub = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
    draw.text((24, 20), title, fill=TEXT, font=font_title)
    draw.text((24, 66), subtitle, fill=MUTED, font=font_sub)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


def render_comparison(rule: Rule, out: Path):
    size = 601
    a_grid, _, a_agent, a_bounds = simulate(rule, size=size, start_offset=(0, 0), start_dir=0)
    b_grid, _, b_agent, b_bounds = simulate(rule, size=size, start_offset=(1, 0), start_dir=0)
    union = (
        min(a_bounds[0], b_bounds[0]),
        min(a_bounds[1], b_bounds[1]),
        max(a_bounds[2], b_bounds[2]),
        max(a_bounds[3], b_bounds[3]),
    )
    left = render_grid(a_grid, a_agent, union, f"{rule.name}: seed A", "same rule, start at center", ROOT / "_tmp_a.png", 520)
    right = render_grid(b_grid, b_agent, union, f"{rule.name}: seed B", "same rule, start one cell to the right", ROOT / "_tmp_b.png", 520)
    a = Image.open(left)
    b = Image.open(right)
    gap = 18
    img = Image.new("RGB", (a.width + b.width + gap, max(a.height, b.height)), (8, 12, 20))
    img.paste(a, (0, 0))
    img.paste(b, (a.width + gap, 0))
    img.save(out)
    left.unlink(missing_ok=True)
    right.unlink(missing_ok=True)
    return out


def render_perturbation_comparison(rule: Rule, out: Path):
    size = 601
    a_grid, _, a_agent, a_bounds = simulate(rule, size=size, start_offset=(0, 0), start_dir=0)
    b_grid, _, b_agent, b_bounds = simulate(
        rule,
        size=size,
        start_offset=(0, 0),
        start_dir=0,
        initial_marks=((0, 0, 1),),
    )
    union = (
        min(a_bounds[0], b_bounds[0]),
        min(a_bounds[1], b_bounds[1]),
        max(a_bounds[2], b_bounds[2]),
        max(a_bounds[3], b_bounds[3]),
    )
    left = render_grid(a_grid, a_agent, union, f"{rule.name}: clean world", "same seed, blank first cell", ROOT / "_tmp_clean.png", 520)
    right = render_grid(b_grid, b_agent, union, f"{rule.name}: one-pixel memory", "same seed, first cell starts cyan", ROOT / "_tmp_marked.png", 520)
    a = Image.open(left)
    b = Image.open(right)
    gap = 18
    img = Image.new("RGB", (a.width + b.width + gap, max(a.height, b.height)), (8, 12, 20))
    img.paste(a, (0, 0))
    img.paste(b, (a.width + gap, 0))
    img.save(out)
    left.unlink(missing_ok=True)
    right.unlink(missing_ok=True)
    return out


def render_animation(rule: Rule, out: Path, size: int = 901):
    frame_steps = [20, 50, 100, 200, 400, 800, 1400, 2200, 3500, 5500, 8500, 13000, 20000, 30000]
    frames = []
    max_steps = max(frame_steps)
    grid = [[0] * size for _ in range(size)]
    x = size // 2
    y = size // 2
    direction = 0
    bounds = [x, y, x, y]
    frame_index = 0
    for step in range(1, max_steps + 1):
        if x < 2 or y < 2 or x >= size - 2 or y >= size - 2:
            break
        state = grid[y][x]
        direction = (direction + rule.turns[state]) % 4
        grid[y][x] = (state + 1) % 3
        if direction == 0:
            y -= 1
        elif direction == 1:
            x += 1
        elif direction == 2:
            y += 1
        else:
            x -= 1
        bounds[0] = min(bounds[0], x)
        bounds[1] = min(bounds[1], y)
        bounds[2] = max(bounds[2], x)
        bounds[3] = max(bounds[3], y)
        if step == frame_steps[frame_index]:
            tmp = ROOT / f"_anim_{frame_index:02d}.png"
            render_grid(
                grid,
                (x, y, direction),
                tuple(bounds),
                f"{rule.name}: {step:,} steps",
                rule.note,
                tmp,
                640,
            )
            frames.append(Image.open(tmp).convert("P", palette=Image.Palette.ADAPTIVE))
            tmp.unlink(missing_ok=True)
            frame_index += 1
            if frame_index >= len(frame_steps):
                break
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=360, loop=0)
    return out


def make_contact_sheet(paths: list[Path], out: Path):
    images = [Image.open(p) for p in paths]
    thumb_w = 430
    thumbs = []
    for img in images:
        ratio = thumb_w / img.width
        thumb = img.resize((thumb_w, int(img.height * ratio)), Image.Resampling.LANCZOS)
        thumbs.append(thumb)
    cols = 3
    gap = 18
    rows = (len(thumbs) + cols - 1) // cols
    h = max(t.height for t in thumbs)
    sheet = Image.new("RGB", (cols * thumb_w + (cols - 1) * gap, rows * h + (rows - 1) * gap), (8, 12, 20))
    for i, thumb in enumerate(thumbs):
        x = (i % cols) * (thumb_w + gap)
        y = (i // cols) * (h + gap)
        sheet.paste(thumb, (x, y))
    sheet.save(out)


def main():
    preview_paths = []
    for rule in RULES:
        grid, _, agent, bounds = simulate(rule)
        path = ROOT / f"{rule.slug}_{rule.steps}_steps.png"
        render_grid(grid, agent, bounds, f"{rule.name}: {rule.steps:,} steps", rule.note, path)
        preview_paths.append(path)
    make_contact_sheet(preview_paths, ROOT / "rule_contact_sheet.png")
    chosen = next(rule for rule in RULES if rule.slug == "pulse_seed")
    render_comparison(chosen, ROOT / "pulse_seed_one_cell_apart.png")
    render_perturbation_comparison(chosen, ROOT / "pulse_seed_one_pixel_memory.png")
    render_animation(chosen, ROOT / "pulse_seed_growth.gif")


if __name__ == "__main__":
    main()
