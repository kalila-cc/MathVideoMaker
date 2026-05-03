from __future__ import annotations

import argparse
import time
from dataclasses import dataclass


TURNS = (1, 0, -1)
VECTORS = ((0, -1), (1, 0), (0, 1), (-1, 0))
MASK = (1 << 64) - 1


def splitmix64(value: int) -> int:
    value = (value + 0x9E3779B97F4A7C15) & MASK
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK
    return (value ^ (value >> 31)) & MASK


def pack_signed(x: int, y: int, tag: int) -> int:
    return ((x & 0xFFFFFFFF) << 33) ^ ((y & 0xFFFFFFFF) << 1) ^ tag


def cell_key(x: int, y: int, state: int) -> int:
    return splitmix64(pack_signed(x, y, state * 17 + 3))


def agent_key(x: int, y: int, direction: int) -> int:
    return splitmix64(pack_signed(x, y, direction * 17 + 101))


@dataclass
class Stats:
    step: int
    x: int
    y: int
    direction: int
    active: int
    width: int
    height: int
    dark_hits: int
    cyan_hits: int
    violet_hits: int


class CyberSeed:
    def __init__(self) -> None:
        self.grid: dict[tuple[int, int], int] = {}
        self.x = 0
        self.y = 0
        self.direction = 0
        self.step_count = 0
        self.min_x = self.max_x = self.x
        self.min_y = self.max_y = self.y
        self.hits = [0, 0, 0]
        self.hash_value = agent_key(self.x, self.y, self.direction)

    def step(self) -> None:
        old_agent_key = agent_key(self.x, self.y, self.direction)
        old_state = self.grid.get((self.x, self.y), 0)
        self.hits[old_state] += 1

        if old_state:
            self.hash_value ^= cell_key(self.x, self.y, old_state)
        new_state = (old_state + 1) % 3
        if new_state:
            self.grid[(self.x, self.y)] = new_state
            self.hash_value ^= cell_key(self.x, self.y, new_state)
        else:
            self.grid.pop((self.x, self.y), None)

        self.direction = (self.direction + TURNS[old_state]) % 4
        dx, dy = VECTORS[self.direction]
        self.x += dx
        self.y += dy
        self.step_count += 1
        self.min_x = min(self.min_x, self.x)
        self.max_x = max(self.max_x, self.x)
        self.min_y = min(self.min_y, self.y)
        self.max_y = max(self.max_y, self.y)

        self.hash_value ^= old_agent_key
        self.hash_value ^= agent_key(self.x, self.y, self.direction)

    def stats(self) -> Stats:
        return Stats(
            step=self.step_count,
            x=self.x,
            y=self.y,
            direction=self.direction,
            active=len(self.grid),
            width=self.max_x - self.min_x + 1,
            height=self.max_y - self.min_y + 1,
            dark_hits=self.hits[0],
            cyan_hits=self.hits[1],
            violet_hits=self.hits[2],
        )


def find_exact_cycle(max_steps: int, report_every: int) -> tuple[int | None, int | None, list[Stats]]:
    seed = CyberSeed()
    seen: dict[tuple[int, int, int, int, int], int] = {
        (seed.hash_value, len(seed.grid), seed.x, seed.y, seed.direction): 0
    }
    reports: list[Stats] = []
    for _ in range(max_steps):
        seed.step()
        key = (seed.hash_value, len(seed.grid), seed.x, seed.y, seed.direction)
        previous = seen.get(key)
        if previous is not None:
            return previous, seed.step_count, reports
        seen[key] = seed.step_count
        if report_every and seed.step_count % report_every == 0:
            reports.append(seed.stats())
    return None, None, reports


def run_stats(max_steps: int, report_every: int) -> list[Stats]:
    seed = CyberSeed()
    reports: list[Stats] = []
    for _ in range(max_steps):
        seed.step()
        if report_every and seed.step_count % report_every == 0:
            reports.append(seed.stats())
    if not reports or reports[-1].step != max_steps:
        reports.append(seed.stats())
    return reports


def print_reports(reports: list[Stats]) -> None:
    print("step,active,width,height,x,y,dir,dark_hits,cyan_hits,violet_hits")
    for item in reports:
        print(
            f"{item.step},{item.active},{item.width},{item.height},"
            f"{item.x},{item.y},{item.direction},"
            f"{item.dark_hits},{item.cyan_hits},{item.violet_hits}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=1_000_000)
    parser.add_argument("--report-every", type=int, default=100_000)
    parser.add_argument("--no-cycle-check", action="store_true")
    args = parser.parse_args()

    start = time.perf_counter()
    if args.no_cycle_check:
        reports = run_stats(args.steps, args.report_every)
        print("exact_cycle_check=false")
        print_reports(reports)
    else:
        cycle_start, cycle_end, reports = find_exact_cycle(args.steps, args.report_every)
        print("exact_cycle_check=true")
        if cycle_start is None:
            print(f"exact_cycle_found=false up_to={args.steps}")
        else:
            print(
                "exact_cycle_found=true "
                f"start={cycle_start} end={cycle_end} period={cycle_end - cycle_start}"
            )
        print_reports(reports)
    elapsed = time.perf_counter() - start
    print(f"elapsed_seconds={elapsed:.3f}")


if __name__ == "__main__":
    main()
