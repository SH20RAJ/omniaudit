#!/usr/bin/env python3
"""
OmniAudit-GEO — Automated LinkedIn Video Generator
Renders a 1080p 30fps MP4 video of the terminal CLI with macOS window framing,
typing animations, and real deterministic AST engine outputs.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_VIDEO = REPO_ROOT / "omniaudit_terminal_demo.mp4"

# Colors (Nord / Modern Dark Theme)
BG_CANVAS = (11, 15, 25)
TERM_BG = (15, 23, 42)
TITLE_BAR_BG = (22, 30, 49)
BORDER_COLOR = (45, 55, 75)
TEXT_WHITE = (248, 250, 252)
TEXT_MUTED = (148, 163, 184)
CYAN = (56, 189, 248)
GREEN = (34, 197, 94)
YELLOW = (234, 179, 8)
RED = (239, 68, 68)
MAGENTA = (168, 85, 247)

DOT_RED = (255, 95, 86)
DOT_YELLOW = (255, 189, 46)
DOT_GREEN = (39, 201, 63)

# Fonts
FONT_PATH = "/System/Library/Fonts/Menlo.ttc"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "/System/Library/Fonts/SFNSMono.ttf"

FONT_SIZE = 19
FONT = ImageFont.truetype(FONT_PATH, FONT_SIZE)
FONT_BOLD = ImageFont.truetype(FONT_PATH, FONT_SIZE)
FONT_TITLE = ImageFont.truetype(FONT_PATH, 16)


def strip_ansi(text: str) -> str:
    ansi_regex = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_regex.sub("", text)


def parse_ansi_to_spans(line: str) -> list[tuple[str, tuple[int, int, int]]]:
    """Basic ANSI parser to colorize lines."""
    pattern = re.compile(r"(\x1b\[[0-9;]*m)")
    parts = pattern.split(line)
    spans = []
    current_color = TEXT_WHITE
    for part in parts:
        if not part:
            continue
        if part.startswith("\x1b["):
            code = part[2:-1]
            if "36" in code:
                current_color = CYAN
            elif "32" in code:
                current_color = GREEN
            elif "33" in code:
                current_color = YELLOW
            elif "31" in code:
                current_color = RED
            elif "35" in code:
                current_color = MAGENTA
            elif "90" in code or "2" in code:
                current_color = TEXT_MUTED
            elif "0" in code:
                current_color = TEXT_WHITE
        else:
            spans.append((part, current_color))
    return spans


def render_terminal_frame(lines: list[str | list[tuple[str, tuple[int, int, int]]]]):
    """Draws a 1920x1080 canvas with a stylized macOS terminal window."""
    W, H = 1920, 1080
    img = Image.new("RGB", (W, H), BG_CANVAS)
    draw = ImageDraw.Draw(img)

    # Ambient backdrop gradient glow
    for r in range(400, 0, -20):
        alpha = int(12 * (r / 400))
        glow_col = (15 + alpha, 23 + alpha * 2, 42 + alpha * 3)
        draw.ellipse([960 - r * 2, 540 - r, 960 + r * 2, 540 + r], fill=glow_col)

    # Window bounds
    t_w, t_h = 1760, 960
    x0, y0 = (W - t_w) // 2, (H - t_h) // 2
    x1, y1 = x0 + t_w, y0 + t_h

    # Window Shadow
    for s in range(12, 0, -2):
        draw.rounded_rectangle([x0 - s, y0 - s + 6, x1 + s, y1 + s + 6], radius=16, fill=(5, 8, 15))

    # Window Body
    draw.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=TERM_BG, outline=BORDER_COLOR, width=1)

    # Title Bar
    title_h = 44
    draw.rounded_rectangle([x0, y0, x1, y0 + title_h], radius=12, fill=TITLE_BAR_BG)
    draw.rectangle([x0, y0 + title_h - 10, x1, y0 + title_h], fill=TITLE_BAR_BG)
    draw.line([x0, y0 + title_h, x1, y0 + title_h], fill=BORDER_COLOR, width=1)

    # Window Control Buttons
    btn_y = y0 + title_h // 2
    draw.ellipse([x0 + 20, btn_y - 7, x0 + 34, btn_y + 7], fill=DOT_RED)
    draw.ellipse([x0 + 44, btn_y - 7, x0 + 58, btn_y + 7], fill=DOT_YELLOW)
    draw.ellipse([x0 + 68, btn_y - 7, x0 + 82, btn_y + 7], fill=DOT_GREEN)

    # Window Title
    title_text = "shaswatraj@macOS — omni (Brand AI-Readiness & GEO Engine)"
    draw.text((x0 + t_w // 2 - 240, y0 + 12), title_text, fill=TEXT_MUTED, font=FONT_TITLE)

    # Content Area
    start_x = x0 + 32
    start_y = y0 + title_h + 20
    line_h = 24
    max_visible_lines = 36

    display_lines = lines[-max_visible_lines:] if len(lines) > max_visible_lines else lines

    curr_y = start_y
    for item in display_lines:
        if isinstance(item, str):
            spans = parse_ansi_to_spans(item)
        else:
            spans = item

        curr_x = start_x
        for txt, col in spans:
            draw.text((curr_x, curr_y), txt, fill=col, font=FONT)
            # Monospace advance
            bbox = FONT.getbbox(txt)
            curr_x += bbox[2] - bbox[0]
        curr_y += line_h

    return img


def get_cli_output(cmd_args: list[str]) -> list[str]:
    """Runs a command and returns raw lines with ANSI."""
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    p = subprocess.run(
        [sys.executable, str(REPO_ROOT / "cli.py")] + cmd_args,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
    )
    output = p.stdout
    return output.splitlines()


def main():
    print("🎬 Generating OmniAudit-GEO LinkedIn Video Showcase...")
    FFMPEG = "/opt/homebrew/bin/ffmpeg"
    if not os.path.exists(FFMPEG):
        FFMPEG = "ffmpeg"

    pipe_cmd = [
        FFMPEG,
        "-y",
        "-f",
        "image2pipe",
        "-vcodec",
        "png",
        "-r",
        "20",
        "-i",
        "-",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "18",
        "-preset",
        "fast",
        str(OUTPUT_VIDEO),
    ]

    ffmpeg_proc = subprocess.Popen(pipe_cmd, stdin=subprocess.PIPE)

    def write_frame(frame: Image.Image, count: int = 1):
        for _ in range(count):
            frame.save(ffmpeg_proc.stdin, format="PNG")

    # Scripted Scenes
    prompt_prefix = [
        ("shaswatraj@macOS", GREEN),
        (":", TEXT_MUTED),
        ("~", CYAN),
        ("$ ", TEXT_WHITE),
    ]

    # Pre-fetch outputs
    print("  • Capturing live audit output for adobe.com...")
    adobe_lines = get_cli_output(["https://adobe.com"])

    print("  • Capturing live comparison for adobe.com vs canva.com...")
    comp_lines = get_cli_output(["compare", "https://adobe.com", "https://canva.com"])

    print("  • Capturing prompt output for example.com...")
    prompt_lines = get_cli_output(["prompt", "https://example.com"])

    print("  • Capturing benchmark output...")
    bench_lines = get_cli_output(["benchmark"])

    scenes = [
        # Scene 1: Audit
        {
            "cmd": "omni https://adobe.com",
            "lines": adobe_lines,
            "hold_frames": 70,  # 3.5s
        },
        # Scene 2: Competitor compare
        {
            "cmd": "omni compare adobe.com canva.com",
            "lines": comp_lines,
            "hold_frames": 70,
        },
        # Scene 3: Prompt generation
        {
            "cmd": "omni prompt example.com",
            "lines": prompt_lines,
            "hold_frames": 60,
        },
        # Scene 4: Benchmarks
        {
            "cmd": "omni benchmark",
            "lines": bench_lines,
            "hold_frames": 70,
        },
    ]

    print("  • Encoding frames into MP4 video...")
    current_buffer: list[str | list[tuple[str, tuple[int, int, int]]]] = []

    # Intro frame
    intro_lines = [
        [("OmniAudit-GEO — Terminal CLI Demo (Round 3 CRP)", CYAN)],
        [("Deterministic Brand AI-Readiness & Visitor Retention Engine", TEXT_MUTED)],
        "",
    ]
    frame = render_terminal_frame(intro_lines)
    write_frame(frame, 25)

    current_buffer = list(intro_lines)

    for scene in scenes:
        cmd_text = scene["cmd"]
        # Typewriter effect for command
        for i in range(1, len(cmd_text) + 1):
            typing_line = prompt_prefix + [(cmd_text[:i], TEXT_WHITE), ("█", CYAN)]
            f = render_terminal_frame(current_buffer + [typing_line])
            write_frame(f, 2)  # fast typing

        # Hit enter (replace cursor)
        typed_line = prompt_prefix + [(cmd_text, TEXT_WHITE)]
        f = render_terminal_frame(current_buffer + [typed_line])
        write_frame(f, 6)

        # Clear buffer to show clean command output
        current_buffer = [typed_line]

        # Progressive display of command output
        raw_output = scene["lines"]
        chunk_size = 4
        for idx in range(0, len(raw_output), chunk_size):
            chunk = raw_output[: idx + chunk_size]
            f = render_terminal_frame(current_buffer + chunk)
            write_frame(f, 2)

        # Hold on final output
        f = render_terminal_frame(current_buffer + raw_output)
        write_frame(f, scene["hold_frames"])

        # Reset screen for next scene with small pause
        current_buffer = []

    # Final outro celebration frame
    outro = [
        "",
        [("════════════════════════════════════════════════════════════════════════════", CYAN)],
        [("  🎉 OmniAudit-GEO Unified CLI — Deterministic Python AST Engine", GREEN)],
        [("  Adobe University Hackathon 2026 · agentskills.io · Anthropic MCP 2.0", TEXT_WHITE)],
        [("  GitHub: https://github.com/SH20RAJ/omniaudit", CYAN)],
        [("  Live Control Plane: https://omniaudit-geo.onrender.com", TEXT_MUTED)],
        [("════════════════════════════════════════════════════════════════════════════", CYAN)],
    ]
    f = render_terminal_frame(outro)
    write_frame(f, 50)

    ffmpeg_proc.stdin.close()
    ffmpeg_proc.wait()

    size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
    print(f"✓ Successfully generated video: {OUTPUT_VIDEO} ({size_mb:.2f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
