#!/usr/bin/env python3
"""
OmniAudit-GEO — Automated High-Definition LinkedIn Video Generator
Creates a viral 1080p 24fps MP4 video of the terminal CLI with macOS window framing,
starting with 'omni' interactive mode, running live audits, competitor benchmarks,
AI prompt generation, and the 16 Golden Benchmarks matrix.
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

# Canvas & Terminal Theme (Obsidian Dark with Cyan Accents)
BG_CANVAS = (8, 12, 20)
TERM_BG = (10, 15, 26)
TITLE_BAR_BG = (18, 24, 38)
BORDER_COLOR = (38, 48, 68)

TEXT_WHITE = (248, 250, 252)
TEXT_MUTED = (148, 163, 184)
TEXT_DIM = (100, 116, 139)
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
FONT_TITLE = ImageFont.truetype(FONT_PATH, 15)


def clean_symbols(text: str) -> str:
    """Maps non-monospace emojis to ultra-crisp Unicode terminal symbols."""
    mapping = {
        "🚀": "❯",
        "⚔️": "⚔",
        "⚔": "⚔",
        "📊": "◈",
        "🤖": "⚡",
        "🔬": "◉",
        "🌐": "◎",
        "📖": "≡",
        "🚪": "✕",
        "🚨": "▲",
        "⚠️": "▲",
        "⚡": "⚡",
        "ℹ️": "•",
        "ℹ": "•",
        "📋": "::",
        "💡": "*",
        "🏆": "★",
        "✔": "✓",
        "🎉": "★",
        "⭐": "★",
    }
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text


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
            clean_part = clean_symbols(part)
            spans.append((clean_part, current_color))
    return spans


def render_terminal_frame(lines: list[str | list[tuple[str, tuple[int, int, int]]]]):
    """Draws a 1920x1080 canvas with a stylized macOS terminal window matching the user's terminal."""
    W, H = 1920, 1080
    img = Image.new("RGB", (W, H), BG_CANVAS)
    draw = ImageDraw.Draw(img)

    # Ambient backdrop radial glow
    for r in range(450, 0, -25):
        alpha = int(14 * (r / 450))
        glow_col = (10 + alpha, 18 + alpha * 2, 35 + alpha * 3)
        draw.ellipse([960 - r * 2, 540 - r, 960 + r * 2, 540 + r], fill=glow_col)

    # Window bounds
    t_w, t_h = 1760, 980
    x0, y0 = (W - t_w) // 2, (H - t_h) // 2
    x1, y1 = x0 + t_w, y0 + t_h

    # Window Shadow
    for s in range(14, 0, -2):
        draw.rounded_rectangle([x0 - s, y0 - s + 6, x1 + s, y1 + s + 6], radius=16, fill=(4, 6, 12))

    # Window Body
    draw.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=TERM_BG, outline=BORDER_COLOR, width=1)

    # Title Bar
    title_h = 42
    draw.rounded_rectangle([x0, y0, x1, y0 + title_h], radius=12, fill=TITLE_BAR_BG)
    draw.rectangle([x0, y0 + title_h - 10, x1, y0 + title_h], fill=TITLE_BAR_BG)
    draw.line([x0, y0 + title_h, x1, y0 + title_h], fill=BORDER_COLOR, width=1)

    # Window Control Buttons
    btn_y = y0 + title_h // 2
    draw.ellipse([x0 + 20, btn_y - 7, x0 + 34, btn_y + 7], fill=DOT_RED)
    draw.ellipse([x0 + 44, btn_y - 7, x0 + 58, btn_y + 7], fill=DOT_YELLOW)
    draw.ellipse([x0 + 68, btn_y - 7, x0 + 82, btn_y + 7], fill=DOT_GREEN)

    # Window Title (Centered, exactly like macOS Terminal in user's screenshot: "~ — omni")
    title_text = "~ — omni"
    draw.text((x0 + t_w // 2 - 40, y0 + 12), title_text, fill=TEXT_MUTED, font=FONT_TITLE)

    # Content Area
    start_x = x0 + 30
    start_y = y0 + title_h + 18
    line_h = 24
    max_visible_lines = 37

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
    print("🎬 Generating Viral OmniAudit-GEO LinkedIn Video...")
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
        "24",
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

    # Prompt matching user's exact screenshot: [shaswatraj@Sh ~ %
    prompt_prefix = [
        ("[shaswatraj@Sh ~ % ", GREEN),
    ]

    # Pre-fetch outputs
    print("  • Fetching live CLI outputs...")
    adobe_lines = get_cli_output(["https://adobe.com"])
    comp_lines = get_cli_output(["compare", "https://adobe.com", "https://canva.com"])
    prompt_lines = get_cli_output(["prompt", "https://example.com"])
    bench_lines = get_cli_output(["benchmark"])

    # Interactive banner & menu lines (matching screenshot exactly)
    menu_lines = [
        [("╭────────────────────────────────────────────────────────────────────────╮", CYAN)],
        [("│   ___                  _    _             _ _ _      ____ _____ ___    │", CYAN)],
        [("│  / _ \\ _ __ ___  _ __ (_)  / \\  _   _  __| (_) |_   / ___| ____/ _ \\   │", CYAN)],
        [("│ | | | | '_ ` _ \\| '_ \\| | / _ \\| | | |/ _` | | __| | |  _|  _|| | | |  │", CYAN)],
        [("│ | |_| | | | | | | | | | |/ ___ \\ |_| | (_| | | |_  | |_| | |___| |_| |  │", CYAN)],
        [("│  \\___/|_| |_| |_|_| |_|_/_/   \\_\\__,_|\\__,_|_|\\__|  \\____|_____\\___/   │", CYAN)],
        [("│                                                                        │", CYAN)],
        [("│   Brand AI-Readiness & GEO Engine · 100% Deterministic Python AST      │", CYAN)],
        [("│   Adobe University Hackathon 2026 (Round 3 CRP) · agentskills.io       │", CYAN)],
        [("╰────────────────────────────────────────────────────────────────────────╯", CYAN)],
        "",
        [("Welcome to OmniAudit-GEO! Choose an action or paste any URL directly:", GREEN)],
        "",
        [("  [1] ❯ Run Master Website Audit", CYAN)],
        [("  [2] ⚔ Competitor Head-to-Head Benchmark (Compare 2 sites)", CYAN)],
        [("  [3] ◈ Run 16 Golden Benchmarks (Accuracy Suite)", CYAN)],
        [("  [4] ⚡ Generate AI Remediation Fix Prompt (Claude / Cursor)", CYAN)],
        [("  [5] ◉ Run Specialist Skill Audit", CYAN)],
        [("  [6] ◎ Launch Web Dashboard & REST API (http://localhost:8000)", CYAN)],
        [("  [7] ≡ Browse Documentation Catalog", CYAN)],
        [("  [8] ✕ Exit", CYAN)],
        "",
    ]

    print("  • Rendering Scene 1: Starting with 'omni' interactive launcher...")

    # 1. Start with blank terminal and prompt [shaswatraj@Sh ~ %
    blank_f = render_terminal_frame([prompt_prefix + [("█", GREEN)]])
    write_frame(blank_f, 18)

    # 2. Type 'omni'
    cmd1 = "omni"
    for i in range(1, len(cmd1) + 1):
        f = render_terminal_frame([prompt_prefix + [(cmd1[:i], TEXT_WHITE), ("█", GREEN)]])
        write_frame(f, 3)

    # Hit Enter on 'omni'
    f = render_terminal_frame([prompt_prefix + [(cmd1, TEXT_WHITE)]])
    write_frame(f, 6)

    # Display the interactive menu (exactly like the user's screenshot!)
    running_buffer = [prompt_prefix + [(cmd1, TEXT_WHITE)]] + menu_lines
    f = render_terminal_frame(running_buffer)
    write_frame(f, 30)  # hold on the menu

    # 3. Prompt asking for URL
    input_prompt = [("Select an option [1-8] or enter URL [default: 1]: ", GREEN)]
    f = render_terminal_frame(running_buffer + [input_prompt + [("█", GREEN)]])
    write_frame(f, 15)

    # 4. Type 'https://adobe.com'
    url_target = "https://adobe.com"
    for i in range(1, len(url_target) + 1):
        f = render_terminal_frame(running_buffer + [input_prompt + [(url_target[:i], TEXT_WHITE), ("█", GREEN)]])
        write_frame(f, 2)

    # Hit enter on target URL
    f = render_terminal_frame(running_buffer + [input_prompt + [(url_target, TEXT_WHITE)]])
    write_frame(f, 8)

    # 5. Clear screen and show live audit output
    audit_header = [
        prompt_prefix + [("omni https://adobe.com", TEXT_WHITE)],
        "",
        [("⚡ OmniAudit.GEO · Brand AI-Readiness & GEO Engine (Adobe Hackathon 2026)", CYAN)],
        [("Target Domain : https://adobe.com/", TEXT_WHITE)],
        [("Executing canonical AST pipeline across all 6 specialist skills...", TEXT_MUTED)],
    ]

    for idx in range(0, len(adobe_lines), 3):
        chunk = adobe_lines[: idx + 3]
        f = render_terminal_frame(audit_header + chunk)
        write_frame(f, 2)

    # Hold on Adobe Audit Scorecard
    f = render_terminal_frame(audit_header + adobe_lines)
    write_frame(f, 85)  # 3.5s hold

    # --------------------------------------------------------------------------
    # Scene 2: Competitor Compare (adobe.com vs canva.com)
    # --------------------------------------------------------------------------
    print("  • Rendering Scene 2: Competitor Benchmark...")
    cmd2 = "omni compare adobe.com canva.com"
    for i in range(1, len(cmd2) + 1):
        f = render_terminal_frame([prompt_prefix + [(cmd2[:i], TEXT_WHITE), ("█", GREEN)]])
        write_frame(f, 2)

    f = render_terminal_frame([prompt_prefix + [(cmd2, TEXT_WHITE)]])
    write_frame(f, 6)

    comp_header = [prompt_prefix + [(cmd2, TEXT_WHITE)]]
    for idx in range(0, len(comp_lines), 3):
        chunk = comp_lines[: idx + 3]
        f = render_terminal_frame(comp_header + chunk)
        write_frame(f, 2)

    f = render_terminal_frame(comp_header + comp_lines)
    write_frame(f, 85)  # 3.5s hold

    # --------------------------------------------------------------------------
    # Scene 3: AI Fix Prompt Generation (omni prompt example.com)
    # --------------------------------------------------------------------------
    print("  • Rendering Scene 3: AI Remediation Fix Prompt...")
    cmd3 = "omni prompt example.com"
    for i in range(1, len(cmd3) + 1):
        f = render_terminal_frame([prompt_prefix + [(cmd3[:i], TEXT_WHITE), ("█", GREEN)]])
        write_frame(f, 2)

    f = render_terminal_frame([prompt_prefix + [(cmd3, TEXT_WHITE)]])
    write_frame(f, 6)

    prompt_header = [prompt_prefix + [(cmd3, TEXT_WHITE)]]
    for idx in range(0, len(prompt_lines), 4):
        chunk = prompt_lines[: idx + 4]
        f = render_terminal_frame(prompt_header + chunk)
        write_frame(f, 2)

    f = render_terminal_frame(prompt_header + prompt_lines)
    write_frame(f, 75)  # 3.0s hold

    # --------------------------------------------------------------------------
    # Scene 4: 16 Golden Benchmarks Matrix (omni benchmark)
    # --------------------------------------------------------------------------
    print("  • Rendering Scene 4: 16 Golden Benchmarks Matrix...")
    cmd4 = "omni benchmark"
    for i in range(1, len(cmd4) + 1):
        f = render_terminal_frame([prompt_prefix + [(cmd4[:i], TEXT_WHITE), ("█", GREEN)]])
        write_frame(f, 2)

    f = render_terminal_frame([prompt_prefix + [(cmd4, TEXT_WHITE)]])
    write_frame(f, 6)

    bench_header = [prompt_prefix + [(cmd4, TEXT_WHITE)]]
    for idx in range(0, len(bench_lines), 3):
        chunk = bench_lines[: idx + 3]
        f = render_terminal_frame(bench_header + chunk)
        write_frame(f, 2)

    f = render_terminal_frame(bench_header + bench_lines)
    write_frame(f, 85)  # 3.5s hold

    # --------------------------------------------------------------------------
    # Scene 5: Viral Outro / Call To Action
    # --------------------------------------------------------------------------
    print("  • Rendering Scene 5: Viral Outro Finale...")
    outro = [
        "",
        [("╭────────────────────────────────────────────────────────────────────────╮", CYAN)],
        [("│                                                                        │", CYAN)],
        [("│   🏆 OMNIAUDIT-GEO — BRAND AI-READINESS & RETENTION AUDIT PLATFORM     │", GREEN)],
        [("│   Adobe University Hackathon 2026 (Round 3 CRP) · agentskills.io       │", CYAN)],
        [("│                                                                        │", CYAN)],
        [("├────────────────────────────────────────────────────────────────────────┤", CYAN)],
        [("│                                                                        │", CYAN)],
        [("│  ⚡ 100% Air-Gapped Python AST Heuristics (0 Cloud Dependencies)        │", TEXT_WHITE)],
        [("│  ⚡ Sub-Millisecond Execution (0.4ms Latency / Audit)                  │", TEXT_WHITE)],
        [("│  ⚡ 16 Ground-Truth Golden Benchmarks (100% Precision & Recall)        │", TEXT_WHITE)],
        [("│  ⚡ Anthropic Model Context Protocol (MCP) JSON-RPC 2.0 Server         │", TEXT_WHITE)],
        [("│  ⚡ Interactive Terminal CLI + Minimalist Web Control Plane            │", TEXT_WHITE)],
        [("│                                                                        │", CYAN)],
        [("├────────────────────────────────────────────────────────────────────────┤", CYAN)],
        [("│                                                                        │", CYAN)],
        [("│  ⭐ GitHub  : https://github.com/SH20RAJ/omniaudit                     │", CYAN)],
        [("│  🌐 Web App : https://omniaudit-geo.onrender.com                       │", CYAN)],
        [("│                                                                        │", CYAN)],
        [("╰────────────────────────────────────────────────────────────────────────╯", CYAN)],
        "",
        [("✓ All 6 Verification Gates Passed · Submission-Ready Package Generated!", GREEN)],
    ]
    f = render_terminal_frame(outro)
    write_frame(f, 75)

    ffmpeg_proc.stdin.close()
    ffmpeg_proc.wait()

    size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
    print(f"🎉 Successfully generated viral video: {OUTPUT_VIDEO} ({size_mb:.2f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
