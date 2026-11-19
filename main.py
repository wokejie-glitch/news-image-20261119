#!/usr/bin/env python3
"""Draw the front page of 19 November 2026 as one image.

The program writes a newspaper front page that sums up the world news of
Thursday 19 November 2026 to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).

It uses only the Python standard library: the picture is drawn with a small
5x7 bitmap font and the PNG bytes are encoded by hand (zlib + struct), so
the program runs with no network and no third-party package, and two runs
write exactly the same bytes.

Stories, all reported on 19 November 2026:
  - Trump, Xi and Putin hold the first-ever trilateral summit in Shenzhen.
  - Israel launches a ground operation in central Gaza.
  - Ethiopia-Eritrea border clashes threaten war.
  - A magnitude 5.7 earthquake jolts Kumamoto, Japan.
  - Category 5 Cyclone Xavier threatens the Cook Islands.
  - COP31 finance row; one child in four now lives in a conflict zone;
    governments warn of a Java flaw.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 768

PAPER = (255, 255, 255)
INK = (0, 0, 0)
BAND = (245, 245, 245)
RED = (178, 34, 52)
BLUE = (60, 59, 110)
CHINA_RED = (222, 41, 16)
GOLD = (255, 222, 0)
RUSSIA_BLUE = (0, 57, 166)
RUSSIA_RED = (213, 43, 30)

# A 5x7 bitmap font. Each glyph is 7 rows of 5 bits, '#' on, ' ' off.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "00000", "00000", "00000", "01100", "00000"),
    ";": ("00000", "01100", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "•": ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}


class Canvas:
    """An RGB canvas backed by one flat bytearray."""

    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.pixels = bytearray(color * width * height)

    def fill_rect(self, x, y, w, h, color):
        for row in range(y, y + h):
            start = (row * self.width + x) * 3
            self.pixels[start:start + w * 3] = bytes(color) * w

    def text_width(self, text, scale):
        # Each glyph is 5 columns plus 1 column of spacing, except the last.
        return len(text) * (5 * scale + scale) - scale if text else 0

    def draw_text(self, x, y, text, scale, color):
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        self.fill_rect(
                            cx + col * scale, y + row * scale,
                            scale, scale, color,
                        )
            cx += 5 * scale + scale

    def draw_text_centered(self, y, text, scale, color, x0=0, x1=None):
        if x1 is None:
            x1 = self.width
        w = self.text_width(text, scale)
        self.draw_text(x0 + (x1 - x0 - w) // 2, y, text, scale, color)

    def wrap_text(self, text, scale, max_width):
        """Greedy word wrap; returns a list of lines that fit max_width."""
        lines = []
        current = ""
        for word in text.split(" "):
            trial = word if not current else current + " " + word
            if self.text_width(trial, scale) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines


def outline(canvas, x, y, w, h, color):
    """A 1px rectangle outline, so a pale flag keeps a visible edge."""
    canvas.fill_rect(x, y, w, 1, color)
    canvas.fill_rect(x, y + h - 1, w, 1, color)
    canvas.fill_rect(x, y, 1, h, color)
    canvas.fill_rect(x + w - 1, y, 1, h, color)


def draw_flag_usa(canvas, x, y, w, h):
    stripe = h // 13
    for i in range(13):
        color = RED if i % 2 == 0 else PAPER
        canvas.fill_rect(x, y + i * stripe, w, stripe, color)
    canton_w = int(w * 0.4)
    canton_h = stripe * 7
    canvas.fill_rect(x, y, canton_w, canton_h, BLUE)
    for row in range(5):
        for col in range(6):
            sx = x + 6 + col * (canton_w - 12) // 5
            sy = y + 3 + row * (canton_h - 6) // 4
            canvas.fill_rect(sx, sy, 2, 2, PAPER)


def draw_flag_china(canvas, x, y, w, h):
    canvas.fill_rect(x, y, w, h, CHINA_RED)
    cx, cy = x + w // 4, y + h // 3
    for dx, dy in ((0, -6), (0, 6), (-6, 0), (6, 0), (0, 0)):
        canvas.fill_rect(cx + dx - 2, cy + dy - 2, 5, 5, GOLD)
    for sx, sy in ((x + w // 2, y + 6), (x + w // 2 + 14, y + 14),
                   (x + w // 2 + 10, y + h - 12), (x + w // 2 - 6, y + h - 8)):
        canvas.fill_rect(sx, sy, 4, 4, GOLD)


def draw_flag_russia(canvas, x, y, w, h):
    third = h // 3
    canvas.fill_rect(x, y, w, third, PAPER)
    canvas.fill_rect(x, y + third, w, third, RUSSIA_BLUE)
    canvas.fill_rect(x, y + 2 * third, w, h - 2 * third, RUSSIA_RED)


def png_bytes(width, height, rgb):
    """Encode RGB bytes as a PNG (8-bit, colour type 2). Deterministic."""
    raw = bytearray()
    stride = width * 3
    for row in range(height):
        raw.append(0)
        raw += rgb[row * stride:(row + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def draw_front_page():
    c = Canvas(WIDTH, HEIGHT, PAPER)

    # Masthead and dateline.
    c.draw_text_centered(28, "THE WORLD TODAY", 6, INK)
    c.draw_text_centered(
        86, "THURSDAY, 19 NOVEMBER 2026 \u2022 GLOBAL EDITION", 2, INK)
    c.fill_rect(36, 112, WIDTH - 72, 3, INK)
    c.fill_rect(36, 118, WIDTH - 72, 1, INK)

    # Main headline and subhead.
    c.draw_text_centered(136, "TRUMP, XI AND PUTIN", 5, INK)
    c.draw_text_centered(180, "MEET IN SHENZHEN", 5, INK)
    c.draw_text_centered(
        228, "U.S., CHINESE AND RUSSIAN LEADERS HOLD FIRST-EVER", 2, INK)
    c.draw_text_centered(
        248, "TRILATERAL SUMMIT TO DISCUSS UKRAINE, IRAN AND ARMS CONTROL",
        2, INK)

    # Summit band: the three flags and the summit label.
    c.fill_rect(36, 278, WIDTH - 72, 82, BAND)
    c.fill_rect(36, 278, WIDTH - 72, 2, INK)
    c.fill_rect(36, 358, WIDTH - 72, 2, INK)
    draw_flag_usa(c, 60, 288, 280, 40)
    draw_flag_china(c, 372, 288, 280, 40)
    draw_flag_russia(c, 684, 288, 280, 40)
    for fx in (60, 372, 684):
        outline(c, fx, 288, 280, 40, INK)
    c.draw_text_centered(
        336, "SHENZHEN TRILATERAL SUMMIT \u2022 19 NOV 2026", 2, INK)

    # Stories: two columns, two rows.
    columns = ((36, 498), (526, 988))
    stories = [
        ("ISRAEL GROUND", "OPERATION IN GAZA",
         "ISRAELI FORCES LAUNCH A GROUND OPERATION IN CENTRAL GAZA AS THE "
         "TRUCE BODY SAYS BOTH SIDES ARE FALLING SHORT."),
        ("ETHIOPIA-ERITREA", "CLASHES THREATEN WAR",
         "BORDER CLASHES INTENSIFY AS THE AFRICAN UNION URGES AN URGENT "
         "CEASEFIRE."),
        ("QUAKE JOLTS", "KUMAMOTO, JAPAN",
         "A MAGNITUDE 5.7 EARTHQUAKE STRIKES KUMAMOTO PREFECTURE. NO "
         "TSUNAMI WARNING ISSUED."),
        ("CYCLONE XAVIER", "THREATENS COOK ISLANDS",
         "CATEGORY 5 CYCLONE XAVIER BEARS DOWN ON THE NORTHERN COOK "
         "ISLANDS. SHELTERS OPEN."),
    ]
    row_tops = (392, 556)
    for index, (line1, line2, body) in enumerate(stories):
        x0, x1 = columns[index % 2]
        y = row_tops[index // 2]
        c.draw_text(x0, y, line1, 3, INK)
        c.draw_text(x0, y + 24, line2, 3, INK)
        body_lines = c.wrap_text(body, 2, x1 - x0)
        for offset, line in enumerate(body_lines):
            c.draw_text(x0, y + 54 + offset * 18, line, 2, INK)

    # Column divider and row divider.
    c.fill_rect(511, 392, 2, 308, INK)
    c.fill_rect(36, 548, WIDTH - 72, 1, INK)

    # Bottom strip.
    c.fill_rect(36, 712, WIDTH - 72, 44, INK)
    c.draw_text_centered(
        727,
        "COP31 FINANCE ROW \u2022 1 IN 4 CHILDREN IN CONFLICT ZONES "
        "\u2022 JAVA FLAW WARNING",
        2, PAPER)

    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    page = draw_front_page()
    data = png_bytes(WIDTH, HEIGHT, page.pixels)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as handle:
        handle.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), WIDTH, HEIGHT))


if __name__ == "__main__":
    main()
