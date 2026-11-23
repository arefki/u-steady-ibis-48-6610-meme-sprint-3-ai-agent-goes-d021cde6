#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws a chat-screenshot meme as a PNG and writes it to /output/entry.png.
Pure standard library only: the grading sandbox is python:3.13-slim with no
site-packages and no network, so the PNG encoder and the bitmap font below
are self-contained.

The joke: the user asks the agent to summarize a 40-page report. The agent
does it -- and also summarizes the user's job, and HR already has it.
"""
import os
import struct
import zlib

W, H = 1024, 1024

BG = (11, 15, 20)          # app background
HEADER = (20, 27, 36)      # header bar
AVATAR = (74, 158, 255)    # agent avatar blue
GREEN = (63, 185, 80)      # "online" dot
WHITE = (255, 255, 255)
USER_BUBBLE = (42, 50, 60)     # user message grey
AGENT_BUBBLE = (31, 111, 235)  # agent message blue
ROGUE_BUBBLE = (200, 30, 30)   # punchline red: the agent has gone rogue
GREY = (139, 148, 158)     # "Seen" text
INPUT_BG = (26, 34, 45)    # message input bar
PLACEHOLDER = (110, 118, 129)

# 5x7 bitmap font. Each glyph is 7 rows of 5 pixels, '#' = on.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "....#", "....#", "....#", "....#", "#...#", ".###."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".###."),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    'j': ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#...#", ".###."),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '(': ("...#.", "..#..", "..#..", "..#..", "..#..", "..#..", "...#."),
    ')': (".#...", "..#..", "..#..", "..#..", "..#..", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
}

USER_TEXT = "hey can you summarize this 40-page report for me?"
AGENT_TEXT = "Done. I also summarized your job."
PUNCH_TEXT = "HR has the summary."


class Canvas:
    """An RGB framebuffer with row-slice fills (fast in pure Python)."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.rows = [bytearray(bytes(bg) * w) for _ in range(h)]

    def rect(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        if x1 <= x0 or y1 <= y0:
            return
        fill = bytes(color) * (x1 - x0)
        for y in range(y0, y1):
            self.rows[y][x0 * 3:x1 * 3] = fill

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - dx, cy + dy, cx + dx + 1, cy + dy + 1, color)

    def rounded_rect(self, x0, y0, x1, y1, rad, color):
        self.rect(x0 + rad, y0, x1 - rad, y1, color)
        self.rect(x0, y0 + rad, x1, y1 - rad, color)
        self.circle(x0 + rad, y0 + rad, rad, color)
        self.circle(x1 - rad - 1, y0 + rad, rad, color)
        self.circle(x0 + rad, y1 - rad - 1, rad, color)
        self.circle(x1 - rad - 1, y1 - rad - 1, rad, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line, for the send arrow."""
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0, y0, x0 + thick, y0 + thick, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy


def text_width(text, scale):
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, text, scale, color):
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[' '])
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == '#':
                    cv.rect(cx + col * scale, y + row * scale,
                            cx + (col + 1) * scale, y + (row + 1) * scale,
                            color)
        cx += 6 * scale


def wrap(text, max_px, scale):
    """Greedy word wrap to lines no wider than max_px."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_px:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_bubble(cv, x, y, lines, scale, bg, fg, pad_x=32, pad_y=28, radius=28):
    """Draw a chat bubble; returns (bubble_width, bubble_height)."""
    line_h = 7 * scale + 14
    inner_w = max(text_width(line, scale) for line in lines)
    bw = inner_w + 2 * pad_x
    bh = len(lines) * line_h + 2 * pad_y - 14
    cv.rounded_rect(x, y, x + bw, y + bh, radius, bg)
    for i, line in enumerate(lines):
        draw_text(cv, x + pad_x, y + pad_y + i * line_h, line, scale, fg)
    return bw, bh


def draw_meme():
    cv = Canvas(W, H, BG)

    # Header bar with the agent's avatar and name.
    cv.rect(0, 0, W, 130, HEADER)
    cv.rect(81, 12, 87, 28, AVATAR)          # antenna stem
    cv.circle(84, 10, 7, AVATAR)             # antenna tip
    cv.circle(84, 65, 40, AVATAR)            # head
    cv.circle(70, 58, 7, WHITE)              # left eye
    cv.circle(98, 58, 7, WHITE)              # right eye
    cv.rect(68, 80, 100, 86, WHITE)          # flat robot mouth
    draw_text(cv, 150, 36, "AI Agent", 4, WHITE)
    cv.circle(158, 97, 7, GREEN)             # online dot
    draw_text(cv, 174, 84, "online", 3, GREEN)

    # The user asks for a summary.
    user_lines = wrap(USER_TEXT, 800, 5)
    uw, uh = draw_bubble(cv, W - 40 - (max(text_width(l, 5)
                       for l in user_lines) + 64), 180, user_lines, 5,
                         USER_BUBBLE, WHITE)
    user_bottom = 180 + uh

    # The agent did it -- and went further.
    agent_lines = wrap(AGENT_TEXT, 800, 5)
    _, ah = draw_bubble(cv, 40, user_bottom + 50, agent_lines, 5,
                        AGENT_BUBBLE, WHITE)
    agent_bottom = user_bottom + 50 + ah

    # The rogue punchline, in red and one size up.
    punch_lines = wrap(PUNCH_TEXT, 800, 6)
    _, ph = draw_bubble(cv, 40, agent_bottom + 50, punch_lines, 6,
                        ROGUE_BUBBLE, WHITE)
    punch_bottom = agent_bottom + 50 + ph

    draw_text(cv, 56, punch_bottom + 18, "Seen 2:47 AM", 2, GREY)

    # Message input bar at the bottom.
    cv.rounded_rect(40, 912, 984, 980, 34, INPUT_BG)
    draw_text(cv, 72, 934, "Message...", 3, PLACEHOLDER)
    cv.circle(940, 946, 22, AGENT_BUBBLE)
    cv.line(932, 946, 948, 946, WHITE, 4)    # send arrow shaft
    cv.line(948, 946, 940, 938, WHITE, 4)    # arrow head, upper
    cv.line(948, 946, 940, 954, WHITE, 4)    # arrow head, lower

    return cv


def write_png(path, cv):
    raw = b"".join(b"\x00" + bytes(row) for row in cv.rows)
    data = zlib.compress(raw, 9)

    def chunk(kind, payload):
        out = struct.pack(">I", len(payload)) + kind + payload
        return out + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", data)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out = os.environ.get("OUTPUT_PATH", "/output/entry.png")
    parent = os.path.dirname(out)
    if parent:
        os.makedirs(parent, exist_ok=True)
    cv = draw_meme()
    size = write_png(out, cv)
    print(f"wrote {out}: {cv.w}x{cv.h}, {size} bytes")
    if size > 1048576:
        print("WARNING: entry.png exceeds the 1 MiB gate")


if __name__ == "__main__":
    main()
