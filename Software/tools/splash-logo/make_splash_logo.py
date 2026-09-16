#!/usr/bin/env python3
"""Generate the anti-aliased boot-splash logo headers used by MorseOutput::dispM32Logo().

The source is the 1-bit M32c_bits bitmap in MorseOutput.cpp: the "M32" mark with the
word "Pocket" set below the "32". Downscaling that bitmap to two thirds with Pillow's
LANCZOS filter reproduces m32logo_aa.h byte for byte -- run with --check to confirm.

For another board, --name replaces the "Pocket" lettering. It is set in Helvetica Bold
at 51 px, which matches the original lettering glyph for glyph and its letter spacing to
within a pixel, on the same baseline and left edge. The canvas is then trimmed to the
new lettering, so the logo stays centred on the panel.

    python3 make_splash_logo.py --check
    python3 make_splash_logo.py --name Nano --out "../../src/Version 6 and newer/m32logo_nano_aa.h"

Needs Pillow and a Helvetica Bold font file (macOS ships it; see --font).
"""
import argparse
import pathlib
import re
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
SRC_DIR = HERE.parent.parent / "src" / "Version 6 and newer"

SRC_W, SRC_H = 318, 136
AA_W_STOCK, AA_H = 212, 91          # two thirds of the source, as in m32logo_aa.h
LETTERING_BOX = (150, 60, SRC_W, SRC_H)   # holds only "Pocket": right of the M, below the 32
LETTERING_LEFT = 157                # left edge of the "P"
BASELINE = 135                      # capitals end on row 134
FONT_SIZE = 51
VALUES_PER_LINE = 20


def load_source():
    text = (SRC_DIR / "MorseOutput.cpp").read_text(encoding="utf-8")
    body = re.search(r"static unsigned char M32c_bits\[\]\s*=\s*\{(.*?)\};", text, re.S).group(1)
    data = [int(v, 16) for v in re.findall(r"0x[0-9a-fA-F]+", body)]
    stride = (SRC_W + 7) // 8
    if len(data) != stride * SRC_H:
        sys.exit(f"M32c_bits has {len(data)} bytes, expected {stride * SRC_H}")
    img = Image.new("L", (SRC_W, SRC_H))
    px = img.load()
    for y in range(SRC_H):
        for x in range(SRC_W):
            if data[y * stride + x // 8] >> (x % 8) & 1:     # XBM is LSB first
                px[x, y] = 255
    return img


def replace_lettering(img, name, font):
    img = img.copy()
    img.paste(0, LETTERING_BOX)
    # Render wide, threshold to 1 bit like the source, then place by the ink's left edge.
    tmp = Image.new("L", (SRC_W * 2, SRC_H))
    ImageDraw.Draw(tmp).text((20, BASELINE), name, font=font, fill=255, anchor="ls")
    tmp = tmp.point(lambda v: 255 if v > 127 else 0)
    left, top, right, bottom = tmp.getbbox()
    ink = tmp.crop((left, 0, right, SRC_H))
    canvas_w = max(SRC_W, LETTERING_LEFT + ink.width + 2)
    out = Image.new("L", (canvas_w, SRC_H))
    out.paste(img, (0, 0))
    out.paste(ink, (LETTERING_LEFT, 0), ink)
    # Trim to the content, keeping the one-column right margin the source has.
    return out.crop((0, 0, out.getbbox()[2] + 1, SRC_H))


def downscale(img):
    aa_w = round(img.width * AA_W_STOCK / SRC_W)
    return img.resize((aa_w, AA_H), Image.LANCZOS)


def to_header(aa, comment_lines):
    vals = list(aa.tobytes())
    lines = [f"// {c}" for c in comment_lines]
    lines += ["#pragma once",
              f"#define M32_AA_W {aa.width}",
              f"#define M32_AA_H {aa.height}",
              f"static const uint8_t M32logo_aa[{len(vals)}] = {{"]
    rows = [vals[i:i + VALUES_PER_LINE] for i in range(0, len(vals), VALUES_PER_LINE)]
    for i, row in enumerate(rows):
        lines.append("  " + ",".join(map(str, row)) + ("," if i < len(rows) - 1 else ""))
    lines.append("};")
    return "\n".join(lines) + "\n"


def header_values(path):
    text = path.read_text(encoding="utf-8")
    return [int(v) for v in re.findall(r"\b\d+\b", text.split("{", 1)[1])]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="verify the stock m32logo_aa.h is reproduced")
    ap.add_argument("--name", help='lettering to put in place of "Pocket"')
    ap.add_argument("--out", help="header file to write (with --name)")
    ap.add_argument("--font", default="/System/Library/Fonts/Helvetica.ttc")
    ap.add_argument("--font-index", type=int, default=1, help="face in a .ttc; 1 = Helvetica Bold")
    ap.add_argument("--preview", help="also write a PNG of the result")
    args = ap.parse_args()

    source = load_source()
    if args.check:
        stock = downscale(source)
        expected = header_values(SRC_DIR / "m32logo_aa.h")
        if list(stock.tobytes()) != expected or stock.size != (AA_W_STOCK, AA_H):
            sys.exit("MISMATCH: the stock logo is not reproduced")
        print("ok: m32logo_aa.h is reproduced exactly")
        return
    if not (args.name and args.out):
        ap.error("give --check, or --name together with --out")

    font = ImageFont.truetype(args.font, FONT_SIZE, index=args.font_index)
    master = replace_lettering(source, args.name, font)
    aa = downscale(master)
    comment = [
        f"Auto-generated anti-aliased 'M32 {args.name}' boot logo (white-on-black, 8-bit grey).",
        f"Source: M32c_bits (318x136, 1-bit) with 'Pocket' replaced by '{args.name}' (Helvetica Bold 51),",
        f"trimmed to {master.width}x{master.height} and downscaled to {aa.width}x{aa.height} with LANCZOS.",
        "Regenerate with Software/tools/splash-logo/make_splash_logo.py.",
    ]
    pathlib.Path(args.out).write_text(to_header(aa, comment), encoding="utf-8")
    if args.preview:
        aa.save(args.preview)
    print(f"wrote {args.out}: {aa.width}x{aa.height}")


if __name__ == "__main__":
    main()
