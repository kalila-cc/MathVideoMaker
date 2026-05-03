from __future__ import annotations

import math
import random
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "exports" / "final"
COVER_DIR = ROOT / "exports" / "covers"
FRAME_DIR = ROOT / "exports" / "frames" / "three_species_agents_preview"
OUT_VIDEO = OUT_DIR / "three_cyber_species_agents_preview_v11_720p20.mp4"
POSTER = COVER_DIR / "three_cyber_species_agents_preview_v11_poster.jpg"
EARLY_FRAME = COVER_DIR / "three_cyber_species_agents_preview_v11_early.jpg"

W, H = 1280, 720
FPS = 20
TOTAL_FRAMES = 300
SIM_STEPS = 174
SEED = 20260503
HOLD_FRAMES = 24
STAGE2_FRAME = 140
SLOW_END_STEP = 13
FINAL_HOLD_FRAMES = 24

WORLD_W, WORLD_H = 38, 22
INIT_COUNT_PER_SPECIES = 1
HABITAT_W, HABITAT_H = 24, 12
INIT_ZONE_W, INIT_ZONE_H = HABITAT_W, HABITAT_H
HABITAT_LEFT = (WORLD_W - HABITAT_W) // 2
HABITAT_TOP = (WORLD_H - HABITAT_H) // 2
HABITAT_RIGHT = HABITAT_LEFT + HABITAT_W - 1
HABITAT_BOTTOM = HABITAT_TOP + HABITAT_H - 1

BOARD_BOX = (182, 150, 1098, 622)
BOARD_PAD = 14

BG = (7, 11, 20)
PANEL = (10, 17, 31)
GRID = (30, 43, 64)
GRID_BOLD = (47, 66, 96)
TEXT = (232, 239, 255)
MUTED = (139, 160, 195)
WHITE = (255, 255, 255)
CYAN = (24, 216, 255)
VIOLET = (190, 72, 255)
AMBER = (255, 173, 64)
RED = (255, 92, 92)

COLORS = {
    1: CYAN,
    2: VIOLET,
    3: AMBER,
}

NAMES = {
    1: "小光",
    2: "小影",
    3: "小焰",
}

# 1 eats 2, 2 eats 3, 3 eats 1.
PREY_OF = {
    1: 2,
    2: 3,
    3: 1,
}

PREDATOR_OF = {
    1: 3,
    2: 1,
    3: 2,
}

DIRS = [
    (0, -1),
    (1, 0),
    (0, 1),
    (-1, 0),
]


@dataclass
class Agent:
    id: int
    species: int
    x: int
    y: int
    direction: int
    energy: float
    age: int = 0
    cooldown: int = 0
    alive: bool = True


@dataclass(frozen=True)
class AgentView:
    id: int
    species: int
    x: int
    y: int
    energy: float
    age: int


@dataclass(frozen=True)
class Event:
    kind: str
    species: int
    x: int
    y: int
    other_species: int = 0


@dataclass(frozen=True)
class Snapshot:
    agents: tuple[AgentView, ...]
    events: tuple[Event, ...]


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
FONT_LABEL = font(18, True)
FONT_SMALL = font(16)
FONT_MONO = font(18)


def stable_hash(*values: int) -> int:
    h = 2166136261
    for value in values:
        h ^= value & 0xFFFFFFFF
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def beats(a: int, b: int) -> bool:
    return PREY_OF[a] == b


def in_world(x: int, y: int) -> bool:
    return HABITAT_LEFT <= x <= HABITAT_RIGHT and HABITAT_TOP <= y <= HABITAT_BOTTOM


def initial_agents() -> list[Agent]:
    rng = random.Random(SEED)
    agents: list[Agent] = []
    occupied: set[tuple[int, int]] = set()
    next_id = 1
    spawn_centers = {
        1: (HABITAT_LEFT + HABITAT_W // 3, HABITAT_TOP + HABITAT_H // 2),
        2: (HABITAT_LEFT + HABITAT_W * 2 // 3, HABITAT_TOP + HABITAT_H // 2 - 3),
        3: (HABITAT_LEFT + HABITAT_W // 2, HABITAT_TOP + HABITAT_H // 2 + 5),
    }

    for species in (1, 2, 3):
        placed = 0
        while placed < INIT_COUNT_PER_SPECIES:
            if INIT_COUNT_PER_SPECIES == 1:
                base_x, base_y = spawn_centers[species]
                x = min(HABITAT_RIGHT - 3, max(HABITAT_LEFT + 3, base_x + rng.randint(-3, 3)))
                y = min(HABITAT_BOTTOM - 3, max(HABITAT_TOP + 3, base_y + rng.randint(-2, 2)))
            else:
                x = rng.randint(HABITAT_LEFT, HABITAT_RIGHT)
                y = rng.randint(HABITAT_TOP, HABITAT_BOTTOM)
            if (x, y) in occupied:
                continue
            occupied.add((x, y))
            agents.append(
                Agent(
                    id=next_id,
                    species=species,
                    x=x,
                    y=y,
                    direction=rng.randrange(4),
                    energy=10.8 + rng.random() * 1.2,
                    cooldown=0 if INIT_COUNT_PER_SPECIES == 1 else rng.randrange(2, 11),
                )
            )
            next_id += 1
            placed += 1

    return agents


def snapshot(agents: list[Agent], events: list[Event] | None = None) -> Snapshot:
    live = [
        AgentView(a.id, a.species, a.x, a.y, a.energy, a.age)
        for a in agents
        if a.alive
    ]
    live.sort(key=lambda item: item.id)
    return Snapshot(tuple(live), tuple(events or ()))


def nearest_agent(
    agent: Agent,
    agents: list[Agent],
    species: int,
    radius: int,
) -> Agent | None:
    best: Agent | None = None
    best_dist = radius + 1
    for other in agents:
        if not other.alive or other.species != species or other.id == agent.id:
            continue
        dist = abs(other.x - agent.x) + abs(other.y - agent.y)
        if dist <= radius and dist < best_dist:
            best = other
            best_dist = dist
    return best


def vector_to_direction(dx: int, dy: int, fallback: int, salt: int) -> int:
    if dx == 0 and dy == 0:
        return fallback
    if abs(dx) > abs(dy):
        return 1 if dx > 0 else 3
    if abs(dy) > abs(dx):
        return 2 if dy > 0 else 0
    if stable_hash(dx, dy, salt) & 1:
        return 1 if dx > 0 else 3
    return 2 if dy > 0 else 0


def desired_direction(agent: Agent, agents: list[Agent], step: int) -> int:
    cx = (HABITAT_LEFT + HABITAT_RIGHT) // 2
    cy = (HABITAT_TOP + HABITAT_BOTTOM) // 2
    near_boundary = (
        agent.x <= HABITAT_LEFT + 2
        or agent.x >= HABITAT_RIGHT - 2
        or agent.y <= HABITAT_TOP + 2
        or agent.y >= HABITAT_BOTTOM - 2
    )
    if near_boundary and stable_hash(agent.id, step, agent.x, agent.y) % 7 != 0:
        return vector_to_direction(cx - agent.x, cy - agent.y, agent.direction, agent.id + step)

    predator = nearest_agent(agent, agents, PREDATOR_OF[agent.species], radius=10)
    prey = nearest_agent(agent, agents, PREY_OF[agent.species], radius=13)

    if predator is not None:
        predator_dist = abs(predator.x - agent.x) + abs(predator.y - agent.y)
    else:
        predator_dist = 99

    if prey is not None:
        prey_dist = abs(prey.x - agent.x) + abs(prey.y - agent.y)
    else:
        prey_dist = 99

    if predator is not None and predator_dist <= min(6, prey_dist + 2):
        dx = agent.x - predator.x
        dy = agent.y - predator.y
        return vector_to_direction(dx, dy, agent.direction, agent.id + step)

    if prey is not None:
        dx = prey.x - agent.x
        dy = prey.y - agent.y
        return vector_to_direction(dx, dy, agent.direction, agent.id + step)

    if abs(agent.x - cx) > WORLD_W // 4 or abs(agent.y - cy) > WORLD_H // 4:
        if stable_hash(agent.id, step, agent.x, agent.y) % 4 != 0:
            return vector_to_direction(cx - agent.x, cy - agent.y, agent.direction, agent.id + step)

    turn_signal = stable_hash(agent.id, agent.x, agent.y, step) % 11
    if turn_signal == 0:
        return (agent.direction + 1) % 4
    if turn_signal == 1:
        return (agent.direction + 3) % 4
    return agent.direction


def empty_neighbors(
    x: int,
    y: int,
    occupied: dict[tuple[int, int], Agent],
    step: int,
    salt: int,
) -> list[tuple[int, int]]:
    cells: list[tuple[int, int]] = []
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)):
        nx, ny = x + dx, y + dy
        if in_world(nx, ny) and (nx, ny) not in occupied:
            cells.append((nx, ny))
    cells.sort(key=lambda p: stable_hash(p[0], p[1], step, salt))
    return cells


def advance(agents: list[Agent], step: int, next_id: int) -> tuple[list[Agent], list[Event], int]:
    events: list[Event] = []
    occupied: dict[tuple[int, int], Agent] = {
        (a.x, a.y): a for a in agents if a.alive
    }
    order = [a for a in agents if a.alive]
    order.sort(key=lambda a: stable_hash(a.id, step, a.x, a.y))
    newborns: list[Agent] = []

    for agent in order:
        if not agent.alive:
            continue

        occupied.pop((agent.x, agent.y), None)
        agent.age += 1
        agent.cooldown = max(0, agent.cooldown - 1)
        agent.energy -= 0.012

        if agent.energy <= 0 or agent.age > 520:
            agent.alive = False
            events.append(Event("death", agent.species, agent.x, agent.y))
            continue

        desired = desired_direction(agent, agents, step)
        candidates = [desired, (desired + 1) % 4, (desired + 3) % 4, (desired + 2) % 4]
        moved = False

        for direction in candidates:
            dx, dy = DIRS[direction]
            tx, ty = agent.x + dx, agent.y + dy
            if not in_world(tx, ty):
                continue
            target = occupied.get((tx, ty))
            if target is None:
                agent.x, agent.y = tx, ty
                agent.direction = direction
                occupied[(tx, ty)] = agent
                moved = True
                break
            if beats(agent.species, target.species):
                target.alive = False
                occupied.pop((tx, ty), None)
                agent.x, agent.y = tx, ty
                agent.direction = direction
                agent.energy = min(13.0, agent.energy + 2.7)
                occupied[(tx, ty)] = agent
                events.append(Event("eat", agent.species, tx, ty, target.species))
                moved = True
                break

        if not moved:
            agent.direction = (agent.direction + 1) % 4
            occupied[(agent.x, agent.y)] = agent

        if agent.energy >= 5.6 and agent.cooldown == 0:
            choices = empty_neighbors(agent.x, agent.y, occupied, step, agent.id)
            if choices:
                nx, ny = choices[0]
                child = Agent(
                    id=next_id,
                    species=agent.species,
                    x=nx,
                    y=ny,
                    direction=stable_hash(agent.id, step, nx, ny) % 4,
                    energy=6.2,
                    cooldown=5,
                )
                next_id += 1
                newborns.append(child)
                occupied[(nx, ny)] = child
                agent.energy -= 1.9
                agent.cooldown = 7 + stable_hash(agent.id, step) % 4
                events.append(Event("birth", agent.species, nx, ny))

    agents.extend(newborns)

    if len([a for a in agents if a.alive]) > 320:
        live = [a for a in agents if a.alive]
        live.sort(key=lambda a: (a.energy, -a.age))
        for agent in live[: len(live) - 320]:
            agent.alive = False
            events.append(Event("death", agent.species, agent.x, agent.y))

    agents = [a for a in agents if a.alive]
    return agents, events, next_id


def precompute_states() -> list[Snapshot]:
    agents = initial_agents()
    next_id = max(a.id for a in agents) + 1
    states = [snapshot(agents)]
    for step in range(1, SIM_STEPS + 1):
        agents, events, next_id = advance(agents, step, next_id)
        states.append(snapshot(agents, events))
    return states


def frame_to_step(frame_index: int) -> int:
    if frame_index < HOLD_FRAMES:
        return 0
    if frame_index < STAGE2_FRAME:
        return min(SLOW_END_STEP, 1 + (frame_index - HOLD_FRAMES) // 8)
    if frame_index >= TOTAL_FRAMES - FINAL_HOLD_FRAMES:
        return SIM_STEPS
    fast_frames = TOTAL_FRAMES - FINAL_HOLD_FRAMES - STAGE2_FRAME - 1
    t = (frame_index - STAGE2_FRAME) / max(1, fast_frames)
    eased = t * t * (3 - 2 * t)
    return min(SIM_STEPS, SLOW_END_STEP + int(eased * (SIM_STEPS - SLOW_END_STEP)))


def phase_label(frame_index: int) -> str:
    if frame_index < HOLD_FRAMES:
        return "随机投放"
    if frame_index < STAGE2_FRAME:
        return "阶段一：慢速繁衍"
    if frame_index >= TOTAL_FRAMES - FINAL_HOLD_FRAMES:
        return "阶段二：铺满棋盘"
    return "阶段二：快速演化"


def state_bounds(
    states: list[Snapshot],
    start_step: int,
    end_step: int,
    include_habitat: bool,
) -> tuple[int, int, int, int]:
    xs: list[int] = []
    ys: list[int] = []
    for step in range(start_step, min(end_step, len(states) - 1) + 1):
        state = states[step]
        for agent in state.agents:
            xs.append(agent.x)
            ys.append(agent.y)
        for event in state.events:
            xs.append(event.x)
            ys.append(event.y)

    if include_habitat:
        xs.extend([HABITAT_LEFT, HABITAT_RIGHT])
        ys.extend([HABITAT_TOP, HABITAT_BOTTOM])
    return min(xs), min(ys), max(xs), max(ys)


def fit_view(bounds: tuple[int, int, int, int], margin: int = 2) -> tuple[int, int, int, int, int]:
    left, top, right, bottom = bounds
    left = max(0, left - margin)
    top = max(0, top - margin)
    right = min(WORLD_W - 1, right + margin)
    bottom = min(WORLD_H - 1, bottom + margin)

    board_w = BOARD_BOX[2] - BOARD_BOX[0] - BOARD_PAD * 2
    board_h = BOARD_BOX[3] - BOARD_BOX[1] - BOARD_PAD * 2
    target_ratio = board_w / board_h

    def expand_range(start: int, end: int, wanted: int, limit: int) -> tuple[int, int]:
        current = end - start + 1
        if wanted <= current:
            return start, end
        extra = wanted - current
        start -= extra // 2
        end += extra - extra // 2
        if start < 0:
            end = min(limit - 1, end - start)
            start = 0
        if end >= limit:
            shift = end - limit + 1
            start = max(0, start - shift)
            end = limit - 1
        return start, end

    view_w = right - left + 1
    view_h = bottom - top + 1
    ratio = view_w / view_h
    if ratio < target_ratio:
        left, right = expand_range(left, right, min(WORLD_W, math.ceil(view_h * target_ratio)), WORLD_W)
    elif ratio > target_ratio:
        top, bottom = expand_range(top, bottom, min(WORLD_H, math.ceil(view_w / target_ratio)), WORLD_H)

    view_w = right - left + 1
    view_h = bottom - top + 1
    cell = max(5, min(board_w // view_w, board_h // view_h))
    return left, top, right, bottom, cell


def count_species(state: Snapshot) -> dict[int, int]:
    counts = {1: 0, 2: 0, 3: 0}
    for agent in state.agents:
        counts[agent.species] += 1
    return counts


def view_for_frame(
    views: tuple[tuple[int, int, int, int, int], tuple[int, int, int, int, int]],
    frame_index: int,
) -> tuple[int, int, int, int, int]:
    if frame_index < STAGE2_FRAME:
        return views[0]
    return views[1]


def draw_symbol(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    cell: int,
    species: int,
    alpha: int = 255,
) -> None:
    color = COLORS[species]
    fill = (*color, alpha)
    outline = (*WHITE, min(220, alpha))
    r = max(5, int(cell * 0.36))
    if species == 1:
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=outline, width=2)
    elif species == 2:
        points = [(cx, cy - r - 2), (cx + r + 2, cy + r), (cx - r - 2, cy + r)]
        draw.polygon(points, fill=fill)
        draw.line((points[0], points[1], points[2], points[0]), fill=outline, width=2)
    else:
        draw.rectangle((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=outline, width=2)


def grid_origin(view: tuple[int, int, int, int, int]) -> tuple[int, int, int, int]:
    left, top, right, bottom, cell = view
    view_w = right - left + 1
    view_h = bottom - top + 1
    x0, y0, x1, y1 = BOARD_BOX
    board_w = view_w * cell
    board_h = view_h * cell
    gx0 = x0 + (x1 - x0 - board_w) // 2
    gy0 = y0 + (y1 - y0 - board_h) // 2
    return gx0, gy0, board_w, board_h


def cell_center(view: tuple[int, int, int, int, int], x: int, y: int) -> tuple[int, int]:
    left, top, _right, _bottom, cell = view
    gx0, gy0, _board_w, _board_h = grid_origin(view)
    return gx0 + (x - left) * cell + cell // 2, gy0 + (y - top) * cell + cell // 2


def draw_seed_zone(draw: ImageDraw.ImageDraw, view: tuple[int, int, int, int, int]) -> None:
    left, top, right, bottom, cell = view
    sx0 = HABITAT_LEFT
    sy0 = HABITAT_TOP
    sx1 = HABITAT_RIGHT
    sy1 = HABITAT_BOTTOM
    if sx1 < left or sx0 > right or sy1 < top or sy0 > bottom:
        return

    px0, py0 = cell_center(view, max(left, sx0), max(top, sy0))
    px1, py1 = cell_center(view, min(right, sx1), min(bottom, sy1))
    box = (
        px0 - cell // 2,
        py0 - cell // 2,
        px1 + cell // 2,
        py1 + cell // 2,
    )
    draw.rectangle(box, outline=(68, 91, 128, 180), width=2)

    dash = 10
    x0, y0, x1, y1 = box
    for x in range(x0, x1, dash * 2):
        draw.line((x, y0, min(x + dash, x1), y0), fill=(111, 138, 180, 130), width=1)
        draw.line((x, y1, min(x + dash, x1), y1), fill=(111, 138, 180, 130), width=1)
    for y in range(y0, y1, dash * 2):
        draw.line((x0, y, x0, min(y + dash, y1)), fill=(111, 138, 180, 130), width=1)
        draw.line((x1, y, x1, min(y + dash, y1)), fill=(111, 138, 180, 130), width=1)


def draw_board(draw: ImageDraw.ImageDraw, state: Snapshot, view: tuple[int, int, int, int, int], frame_index: int) -> None:
    x0, y0, x1, y1 = BOARD_BOX
    draw.rounded_rectangle(BOARD_BOX, radius=8, fill=PANEL, outline=(24, 37, 58), width=1)

    left, top, right, bottom, cell = view
    view_w = right - left + 1
    view_h = bottom - top + 1
    gx0, gy0, board_w, board_h = grid_origin(view)
    draw.rectangle((gx0, gy0, gx0 + board_w, gy0 + board_h), fill=BG)

    for xx in range(view_w + 1):
        sx = gx0 + xx * cell
        line = GRID_BOLD if (left + xx) % 8 == 0 else GRID
        draw.line((sx, gy0, sx, gy0 + board_h), fill=line)
    for yy in range(view_h + 1):
        sy = gy0 + yy * cell
        line = GRID_BOLD if (top + yy) % 8 == 0 else GRID
        draw.line((gx0, sy, gx0 + board_w, sy), fill=line)

    draw_seed_zone(draw, view)

    for event in state.events:
        if not (left <= event.x <= right and top <= event.y <= bottom):
            continue
        cx, cy = cell_center(view, event.x, event.y)
        if event.kind == "eat":
            draw.line((cx - cell, cy, cx + cell, cy), fill=(*WHITE, 220), width=2)
            draw.line((cx, cy - cell, cx, cy + cell), fill=(*WHITE, 220), width=2)
        elif event.kind == "death":
            draw.line((cx - 4, cy - 4, cx + 4, cy + 4), fill=(*RED, 170), width=1)
            draw.line((cx - 4, cy + 4, cx + 4, cy - 4), fill=(*RED, 170), width=1)

    for agent in state.agents:
        if not (left <= agent.x <= right and top <= agent.y <= bottom):
            continue
        cx, cy = cell_center(view, agent.x, agent.y)
        draw_symbol(draw, cx, cy, cell, agent.species)

    draw.rounded_rectangle((x0 + 16, y1 + 12, x0 + 520, y1 + 46), radius=7, fill=(15, 27, 48), outline=(35, 53, 82))
    draw.text((x0 + 32, y1 + 19), "个体只用形状和颜色标识；新增个体会直接出现在空格", fill=MUTED, font=FONT_SMALL)


def draw_header(draw: ImageDraw.ImageDraw, state: Snapshot, step: int, frame_index: int, view: tuple[int, int, int, int, int]) -> None:
    counts = count_species(state)
    phase = phase_label(frame_index)
    draw.text((46, 30), "三种赛博生命：一族一个起点", fill=TEXT, font=FONT_TITLE)
    draw.text((48, 78), "每族只投放一个初始个体；后续数量只来自行动、捕食与繁衍。", fill=MUTED, font=FONT_SUB)

    draw.rounded_rectangle((48, 104, 286, 132), radius=6, fill=(15, 27, 48), outline=(39, 58, 88))
    draw.text((62, 108), f"{phase}   step {step:03d}", fill=TEXT, font=FONT_SMALL)

    left, top, right, bottom, cell = view
    view_name = "近景" if frame_index < STAGE2_FRAME else "全景"
    view_text = f"{view_name} {right-left+1}x{bottom-top+1} 格 / cell {cell}px"
    draw.text((310, 109), view_text, fill=MUTED, font=FONT_SMALL)

    x = 860
    y = 28
    draw.text((x, y), "制衡关系", fill=TEXT, font=FONT_LABEL)
    y += 34
    rows = [(1, 2), (2, 3), (3, 1)]
    for predator, prey in rows:
        draw_symbol(draw, x + 11, y + 11, 18, predator)
        draw.text((x + 32, y + 2), f"{NAMES[predator]} 压制 {NAMES[prey]}", fill=MUTED, font=FONT_SMALL)
        draw.text((x + 174, y + 2), f"{counts[predator]:3d}", fill=COLORS[predator], font=FONT_SMALL)
        y += 28


def render_frame(
    states: list[Snapshot],
    views: tuple[tuple[int, int, int, int, int], tuple[int, int, int, int, int]],
    frame_index: int,
) -> Image.Image:
    step = frame_to_step(frame_index)
    state = states[step]
    view = view_for_frame(views, frame_index)
    img = Image.new("RGBA", (W, H), (*BG, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle((0, 0, W, H), fill=(*BG, 255))
    draw_header(draw, state, step, frame_index, view)
    draw_board(draw, state, view, frame_index)
    return img.convert("RGB")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    if FRAME_DIR.exists():
        shutil.rmtree(FRAME_DIR)
    FRAME_DIR.mkdir(parents=True, exist_ok=True)

    states = precompute_states()
    close_bounds = state_bounds(states, 0, SLOW_END_STEP, include_habitat=False)
    full_bounds = state_bounds(states, 0, SIM_STEPS, include_habitat=True)
    close_view = fit_view(close_bounds, margin=1)
    full_view = fit_view(full_bounds, margin=0)
    views = (close_view, full_view)
    print(f"seed={SEED}")
    print(f"close_bounds={close_bounds}")
    print(f"full_bounds={full_bounds}")
    print(f"close_view={close_view}")
    print(f"full_view={full_view}")
    print(f"final_counts={count_species(states[-1])}")

    poster_frame = None
    early_frame = None
    for frame_index in range(TOTAL_FRAMES):
        frame = render_frame(states, views, frame_index)
        frame.save(FRAME_DIR / f"frame_{frame_index:04d}.png")
        if frame_index == 88:
            early_frame = frame.copy()
        if frame_index == TOTAL_FRAMES - 1:
            poster_frame = frame.copy()

    if early_frame is None:
        early_frame = render_frame(states, views, 88)
    if poster_frame is None:
        poster_frame = render_frame(states, views, TOTAL_FRAMES - 1)
    early_frame.save(EARLY_FRAME, quality=92)
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
    print(EARLY_FRAME)
    print(POSTER)


if __name__ == "__main__":
    main()
