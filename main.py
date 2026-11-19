# news-image-20261119 — "The World in One Day"
#
# A program that draws one image summing up the world news of
# Thursday 19 November 2026 and writes it to /output/entry.png.
#
# Pure Python 3 standard library: no network, no external files, no
# fonts on disk. The picture is drawn pixel by pixel with an embedded
# 5x7 bitmap font, and encoded as PNG by hand (zlib + struct).
# Deterministic: the same input always produces the same bytes.
#
# Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# The grader runs it with no network and /output as the target dir.

import os
import struct
import zlib

# ---------------------------------------------------------------- font
# 5x7 pixel font, one glyph per character: 7 rows of 5 pixels each.
# '#' is ink, '.' is empty. Only the characters the picture needs.

FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10011", "10101", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00010", "00100", "00100", "00100"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "01100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '&': ("01100", "10010", "10010", "01000", "10101", "10010", "01101"),
    '*': ("00000", "01010", "00100", "11111", "00100", "01010", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    # bullet, drawn as a solid block
    '\u2022': ("00000", "00000", "01110", "01110", "01110", "00000", "00000"),
}

CHAR_W, CHAR_H = 5, 7


def text_width(text, scale):
    """Pixel width of text at the given scale (1px gap between chars)."""
    return len(text) * (CHAR_W + 1) * scale - scale


# ---------------------------------------------------------------- png
def png_bytes(width, height, pixels):
    """Encode an RGB bytearray (row-major, 3 bytes/px) as a PNG."""
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)  # filter: none
        raw += pixels[y * stride:(y + 1) * stride]
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bg * (width * height))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:(yy * self.w + x1) * 3] = bytes(color) * (x1 - x0)

    def rect(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            self.fill_rect(cx - dx, yy, 2 * dx + 1, 1, color)

    def circle(self, cx, cy, r, color, t=1):
        for k in range(t):
            rr = r - k
            x, y, d = 0, rr, 3 - 2 * rr
            while x <= y:
                for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                               (cx + x, cy - y), (cx - x, cy - y),
                               (cx + y, cy + x), (cx - y, cy + x),
                               (cx + y, cy - x), (cx - y, cy - x)):
                    self.set(px, py, color)
                if d < 0:
                    d += 4 * x + 6
                else:
                    d += 4 * (x - y) + 10
                    y -= 1
                x += 1

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        # Filled triangle by scanline.
        pts = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        def edge(xa, ya, xb, yb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)
        for y in range(ay, cy + 1):
            if y < by:
                xa = edge(ax, ay, bx, by, y)
                xb = edge(ax, ay, cx, cy, y)
            else:
                xa = edge(bx, by, cx, cy, y)
                xb = edge(ax, ay, cx, cy, y)
            if xa > xb:
                xa, xb = xb, xa
            self.fill_rect(int(xa), y, int(xb) - int(xa) + 1, 1, color)

    # -- text -------------------------------------------------------
    def glyph(self, x, y, ch, scale, color):
        rows = FONT.get(ch.upper(), FONT['?'])
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == '1':
                    self.fill_rect(x + c * scale, y + r * scale,
                                   scale, scale, color)

    def text(self, x, y, s, scale, color, align="left"):
        s = s.upper()
        if align == "center":
            x -= text_width(s, scale) // 2
        elif align == "right":
            x -= text_width(s, scale)
        for ch in s:
            self.glyph(x, y, ch, scale, color)
            x += (CHAR_W + 1) * scale
        return x

    def wrap(self, s, scale, max_w):
        """Greedy word wrap; returns list of lines fitting max_w pixels."""
        max_chars = max(1, max_w // ((CHAR_W + 1) * scale))
        lines, cur = [], ""
        for word in s.upper().split(" "):
            trial = (cur + " " + word).strip()
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


# ---------------------------------------------------------------- palette
PAPER = (246, 241, 231)
CARD = (255, 255, 255)
INK = (22, 22, 28)
RED = (192, 57, 43)
NAVY = (31, 56, 100)
GOLD = (201, 149, 20)
BLUE = (41, 98, 168)
LIGHTBLUE = (178, 208, 235)
SKY = (214, 232, 246)
GREEN = (46, 125, 50)
ORANGE = (230, 126, 34)
YELLOW = (241, 196, 15)
GREY = (96, 94, 88)
LIGHT = (233, 226, 212)
DARKRED = (140, 30, 20)

# ---------------------------------------------------------------- pictures
# Every picture is drawn from flat shapes: no photos, no copied art.

def draw_flag_us(cv, x, y, w, h):
    for i in range(7):
        cv.fill_rect(x, y + i * h // 7, w, h // 7 + 1,
                     (178, 34, 52) if i % 2 == 0 else (255, 255, 255))
    cv.fill_rect(x, y, w * 2 // 5, h * 4 // 7, NAVY)
    for r in range(4):
        for c in range(5):
            cv.fill_rect(x + 3 + c * 7, y + 3 + r * 6, 2, 2, (255, 255, 255))


def draw_flag_cn(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (222, 41, 16))
    cv.fill_circle(x + 9, y + 9, 4, YELLOW)
    for sx, sy in ((24, 4), (28, 9), (28, 15), (24, 19)):
        cv.fill_circle(x + sx, y + sy, 2, YELLOW)


def draw_flag_ru(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h // 3, (255, 255, 255))
    cv.fill_rect(x, y + h // 3, w, h // 3, (0, 57, 166))
    cv.fill_rect(x, y + 2 * h // 3, w, h // 3, (213, 0, 50))


def draw_hero(cv, x, y, w, h):
    """Shenzhen skyline, three flags, three leaders at a table."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_circle(x + w - 90, y + 34, 26, YELLOW)
    # skyline silhouette: (x offset, height above ground, width)
    towers = [(0, 46, 46), (52, 66, 40), (98, 36, 52), (156, 76, 38),
              (200, 50, 60), (266, 84, 34), (306, 40, 44), (356, 62, 40),
              (402, 34, 46), (454, 72, 38), (498, 44, 48), (552, 58, 40),
              (598, 36, 52), (656, 78, 36), (698, 48, 46), (750, 64, 40),
              (796, 34, 48), (850, 56, 40), (896, 36, 52), (954, 52, 44)]
    base = y + h - 78
    for tx, th, tw in towers:
        cv.fill_rect(x + tx, base - th, tw, th + 38, NAVY)
    cv.fill_rect(x, y + h - 78, w, 78, (58, 74, 92))
    # three flags on poles above the table
    pole_y = y + 22
    for i, fn in enumerate((draw_flag_us, draw_flag_cn, draw_flag_ru)):
        fx = x + 150 + i * 330
        cv.fill_rect(fx, pole_y, 3, 96, INK)
        fn(cv, fx + 3, pole_y + 4, 44, 28)
    # round table
    table_y = y + h - 44
    cv.fill_rect(x + w // 2 - 190, table_y, 380, 10, (122, 72, 40))
    cv.fill_rect(x + w // 2 - 14, table_y + 10, 28, 34, (94, 54, 28))
    # three seated figures: head + shoulders, labelled
    suits = (NAVY, DARKRED, (40, 40, 46))
    names = ("TRUMP", "XI", "PUTIN")
    for i in range(3):
        cx = x + w // 2 - 130 + i * 130
        cv.fill_circle(cx, table_y - 52, 17, (232, 190, 160))   # head
        cv.triangle(cx - 34, table_y - 8, cx + 34, table_y - 8,
                    cx, table_y - 44, suits[i])                # shoulders
        cv.text(cx, table_y + 16, names[i], 2, INK, align="center")


def draw_scales(cv, x, y, w, h):
    """Scales of justice + gavel: the world court."""
    cv.fill_rect(x, y, w, h, (232, 240, 248))
    cx, top = x + w // 2, y + 14
    cv.fill_rect(cx - 2, top, 4, h - 44, NAVY)
    cv.fill_rect(x + 22, top + 8, w - 44, 4, NAVY)
    cv.fill_rect(cx - 16, y + h - 26, 32, 6, NAVY)
    for sgn in (-1, 1):
        px = cx + sgn * (w // 2 - 34)
        cv.line(cx, top + 8, px, top + 34, NAVY, 2)
        cv.line(cx - 2, top + 8, px, top + 34, NAVY, 2)
        cv.triangle(px - 26, top + 34, px + 26, top + 34, px, top + 52, GOLD)
        cv.fill_rect(px - 26, top + 34, 52, 3, GOLD)


def draw_bridge(cv, x, y, w, h):
    """Crimean bridge under attack: deck, towers, blast, smoke."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_circle(x + w - 40, y + 26, 18, YELLOW)
    deck_y = y + h - 34
    for tx in (x + 60, x + w - 110):
        cv.fill_rect(tx, y + 22, 16, deck_y - y - 18, (90, 96, 110))
    cv.fill_rect(x, deck_y, w, 8, (70, 76, 90))
    cv.line(x + 68, y + 24, x + w // 2, deck_y, (120, 126, 140), 2)
    cv.line(x + w - 102, y + 24, x + w // 2, deck_y, (120, 126, 140), 2)
    # blast starburst over the middle of the deck
    bx, by = x + w // 2, deck_y - 16
    for ang in range(0, 360, 30):
        import math
        r1, r2 = 10, 30
        a = math.radians(ang)
        cv.triangle(bx, by,
                    int(bx + r1 * math.cos(a - 0.18)),
                    int(by + r1 * math.sin(a - 0.18)),
                    int(bx + r2 * math.cos(a)),
                    int(by + r2 * math.sin(a)), ORANGE)
    cv.fill_circle(bx, by, 12, YELLOW)
    cv.fill_circle(bx - 26, by - 26, 12, (150, 150, 150))
    cv.fill_circle(bx + 30, by - 30, 10, (170, 170, 170))
    cv.fill_rect(x, y + h - 26, w, 26, BLUE)


def draw_missile(cv, x, y, w, h):
    """Missile over the Gulf: sea, sky, rocket and flame."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_circle(x + 36, y + 24, 16, YELLOW)
    cv.fill_rect(x, y + h - 30, w, 30, BLUE)
    for wx in range(0, w, 34):
        cv.fill_rect(x + wx, y + h - 30, 18, 4, (255, 255, 255))
    # rocket, diagonal up-right (kept inside the picture)
    rx, ry = x + 60, y + h - 44
    cv.line(rx, ry, rx + 100, ry - 30, (200, 200, 205), 6)
    cv.triangle(rx + 100, ry - 30, rx + 116, ry - 24, rx + 102, ry - 14, RED)
    cv.triangle(rx, ry, rx - 14, ry + 10, rx - 3, ry - 10, ORANGE)
    cv.fill_circle(rx - 16, ry + 12, 6, YELLOW)
    # distant tanker silhouette
    cv.fill_rect(x + w - 96, y + h - 46, 76, 14, (60, 60, 66))
    cv.fill_rect(x + w - 78, y + h - 58, 12, 12, (60, 60, 66))


def draw_climate(cv, x, y, w, h):
    """Globe with a leaf: COP31 climate talks."""
    cv.fill_rect(x, y, w, h, (226, 240, 226))
    cx, cy, r = x + w // 2 - 20, y + 40, 34
    cv.fill_circle(cx, cy, r, BLUE)
    cv.fill_circle(cx - 11, cy - 8, 9, GREEN)
    cv.fill_circle(cx + 12, cy + 9, 8, GREEN)
    cv.fill_circle(cx + 14, cy - 12, 5, GREEN)
    cv.circle(cx, cy, r, NAVY, 2)
    # leaf sprouting from the globe: two angled leaves on a stem
    lx, ly = x + w - 56, y + 40
    cv.line(lx, ly, lx + 10, ly - 22, (30, 90, 35), 3)
    cv.triangle(lx + 10, ly - 22, lx - 8, ly - 30, lx - 2, ly - 12, GREEN)
    cv.triangle(lx + 10, ly - 22, lx + 28, ly - 28, lx + 22, ly - 10, GREEN)
    # sun rays
    sx, sy = x + 34, y + 26
    cv.fill_circle(sx, sy, 10, YELLOW)
    for dx, dy in ((-16, 0), (16, 0), (0, -16), (0, 16), (-11, -11), (11, -11)):
        cv.line(sx, sy, sx + dx, sy + dy, YELLOW, 3)


def draw_fire(cv, x, y, w, h):
    """Burning building: Bangladesh unrest."""
    cv.fill_rect(x, y, w, h, (250, 232, 210))
    bx, by, bw, bh = x + 40, y + h - 52, 150, 52
    cv.fill_rect(bx, by, bw, bh, (120, 96, 74))
    for wy in range(3):
        for wx in range(4):
            cv.fill_rect(bx + 14 + wx * 34, by + 12 + wy * 14, 18, 10, YELLOW)
    cv.fill_rect(bx - 6, by - 8, bw + 12, 8, DARKRED)
    # flames on the roof (kept inside the picture)
    fx = bx + bw // 2
    cv.triangle(fx - 46, by - 6, fx + 46, by - 6, fx, by - 22, ORANGE)
    cv.triangle(fx - 26, by - 6, fx + 26, by - 6, fx, by - 14, YELLOW)
    cv.triangle(fx - 10, by - 6, fx + 10, by - 6, fx, by - 8, RED)
    cv.fill_circle(fx - 62, by - 12, 9, (150, 150, 150))
    cv.fill_circle(fx + 60, by - 16, 11, (170, 170, 170))


def draw_chart(cv, x, y, w, h):
    """Record IPO: bars and a rising arrow."""
    cv.fill_rect(x, y, w, h, (232, 240, 232))
    ox, oy = x + 26, y + h - 24
    cv.line(ox, y + 12, ox, oy, INK, 2)
    cv.line(ox, oy, x + w - 14, oy, INK, 2)
    bars = [12, 18, 15, 25, 22, 33, 40]
    bw = (w - 60) // len(bars)
    for i, bh in enumerate(bars):
        cv.fill_rect(ox + 6 + i * bw, oy - bh, bw - 6, bh, BLUE)
    pts = [(ox + 8 + i * bw, oy - bh - 4) for i, bh in enumerate(bars)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.line(ax, ay, bx, by, GREEN, 3)
    ex, ey = pts[-1]
    cv.triangle(ex, ey - 8, ex + 12, ey - 1, ex + 1, ey + 2, GREEN)

# ---------------------------------------------------------------- layout
W, H = 1024, 1024

STORIES = [
    # (accent, picture, headline, caption)
    (NAVY, draw_scales,
     "WORLD COURT RULES ON ROHINGYA GENOCIDE",
     "ICJ: Myanmar killed about 10,000 Rohingya."),
    (DARKRED, draw_bridge,
     "CRIMEA BRIDGE HIT AGAIN",
     "Traffic halted after a third strike in a week."),
    (RED, draw_missile,
     "IRAN STRIKES GULF STATES",
     "Kuwait repels attack after US hit on Qeshm."),
    (GREEN, draw_climate,
     "COP31: RACE FOR A CLIMATE DEAL",
     "Ministers in Antalya race to unblock talks."),
    (ORANGE, draw_fire,
     "BANGLADESH IN TURMOIL",
     "Yunus home torched amid unrest in 28 districts."),
    (BLUE, draw_chart,
     "ANTHROPIC'S $81BN RECORD IPO",
     "AI firm valued at $1.5 trillion in its debut."),
]


def build():
    cv = Canvas(W, H, PAPER)
    cv.rect(0, 0, W, H, INK, 6)

    # ---- masthead ------------------------------------------------
    cv.fill_rect(6, 6, W - 12, 124, NAVY)
    cv.fill_rect(6, 6, W - 12, 5, RED)
    cv.text(W // 2, 22, "THE WORLD IN ONE DAY", 5, (255, 255, 255),
            align="center")
    cv.fill_rect(W // 2 - 300, 72, 600, 3, GOLD)
    cv.text(W // 2, 84, "THURSDAY  19 NOVEMBER 2026", 3, GOLD,
            align="center")
    cv.text(W // 2, 112, "THE DAY'S WORLD NEWS, IN ONE IMAGE", 2,
            (255, 255, 255), align="center")

    # ---- hero: Shenzhen summit ------------------------------------
    hx, hy, hw, hh = 24, 142, W - 48, 316
    cv.fill_rect(hx, hy, hw, hh, CARD)
    cv.rect(hx, hy, hw, hh, INK, 3)
    draw_hero(cv, hx + 3, hy + 3, hw - 6, 168)
    cv.fill_rect(hx, hy + 171, hw, 3, RED)
    cv.text(hx + 20, hy + 184, "TOP STORY - SHENZHEN, CHINA", 2, RED)
    cv.text(W // 2, hy + 208, "THREE NUCLEAR POWERS, ONE TABLE", 4, INK,
            align="center")
    cv.text(W // 2, hy + 252,
            "TRUMP, XI AND PUTIN MEET FOR THE FIRST THREE-WAY SUMMIT", 2,
            INK, align="center")
    cv.text(W // 2, hy + 274,
            "UKRAINE, NUCLEAR ARMS AND IRAN ON THE TABLE", 2, GREY,
            align="center")

    # ---- story grid ------------------------------------------------
    cols, rows = 3, 2
    gx, gy = 24, 470
    cw, chh = 320, 206
    gapx, gapy = 8, 12
    for idx, (accent, pic, head, cap) in enumerate(STORIES):
        cx = gx + (idx % cols) * (cw + gapx)
        cy = gy + (idx // cols) * (chh + gapy)
        cv.fill_rect(cx, cy, cw, chh, CARD)
        cv.rect(cx, cy, cw, chh, INK, 2)
        cv.fill_rect(cx, cy, cw, 8, accent)
        pic(cv, cx + 2, cy + 10, cw - 4, 76)
        lines = cv.wrap(head, 2, cw - 24)
        ly = cy + 96
        for ln in lines[:2]:
            cv.text(cx + 12, ly, ln, 2, INK)
            ly += 18
        for ln in cv.wrap(cap, 2, cw - 24)[:2]:
            cv.text(cx + 12, ly + 2, ln, 2, GREY)
            ly += 18

    # ---- also today ------------------------------------------------
    ty = 906
    cv.fill_rect(24, ty, W - 48, 56, INK)
    items1 = ("ALSO TODAY: VAN GOGH $190.4M RECORD  \u2022  CYCLONE AKVAN: "
              "100,000 FLEE")
    items2 = ("JEFFRIES FIRST BLACK US HOUSE SPEAKER  \u2022  MEASLES "
              "RETURNS IN US  \u2022  GTA VI OUT")
    cv.text(40, ty + 8, items1, 2, (255, 255, 255))
    cv.text(40, ty + 30, items2, 2, (255, 255, 255))

    # ---- footer ----------------------------------------------------
    cv.text(W // 2, 978, "19 NOVEMBER 2026  -  THE WORLD IN ONE IMAGE", 2,
            INK, align="center")
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(W, H, build().px)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
