#!/usr/bin/env python3
"""Generate IntelOneMono12ptScrollCompact.h: the small scroll font at a shorter line pitch.

LovyanGFX takes a GFX font's line pitch from its tallest ascent plus its deepest descent
over all glyphs. In IntelOneMono12ptScroll.h the only glyphs that rise above printable
ASCII are the capital umlauts: their dots sit on two blank rows above the letter, which
lifts the ascent from 18 to 20 px and the pitch from 25 to 27 px.

This tool copies that font glyph for glyph and, only for glyphs that rise above ASCII,
closes every run of blank rows inside the glyph to a single row. The dots stay clearly
apart from the letter, the pitch drops to 26 px, and every other glyph -- all of ASCII,
the lower-case umlauts, the sharp s and the (c) -- is bit-for-bit unchanged. The result
defines the same font names, so a build selects it just by including this header instead.

    python3 make_compact_scroll_font.py           # (re)write the header
    python3 make_compact_scroll_font.py --check   # verify the committed header is current
"""
import argparse
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC_DIR = HERE.parent.parent / "src" / "Version 6 and newer"
SOURCE = SRC_DIR / "IntelOneMono12ptScroll.h"
TARGET = SRC_DIR / "IntelOneMono12ptScrollCompact.h"
WEIGHTS = ("Regular", "Bold")
VALUES_PER_LINE = 16


def parse_source():
    text = SOURCE.read_text(encoding="utf-8")
    ranges = [tuple(int(v, 0) for v in m) for m in re.findall(
        r"\{\s*(0x[0-9A-Fa-f]+),\s*(0x[0-9A-Fa-f]+),\s*(\d+)\s*\}",
        re.search(r"EncodeRange\s+\w+\[\]\s*PROGMEM\s*=\s*\{(.*?)\};", text, re.S).group(1))]
    fonts = {}
    for weight in WEIGHTS:
        name = f"IntelOneMono_{weight}12pt8b"
        table = re.search(r"GFXglyph\s+%s_ScrollGlyphs\[\]\s*PROGMEM\s*=\s*\{(.*?)\};" % name, text, re.S).group(1)
        glyphs = [tuple(map(int, g)) for g in re.findall(
            r"\{\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+)\s*\}", table)]
        header = re.search(r"GFXfont\s+%s_Scroll\s+PROGMEM\s*=\s*\{(.*?)\};" % name, text, re.S).group(1)
        first, last, y_advance = (int(v, 0) for v in re.search(
            r"(0x[0-9A-Fa-f]+),\s*(0x[0-9A-Fa-f]+),\s*(\d+)", header).groups())
        src = (SRC_DIR / f"{name}.h").read_text(encoding="utf-8")
        bitmaps = [int(v, 16) for v in re.findall(r"0x[0-9A-Fa-f]+", re.search(
            r"%sBitmaps\[\]\s*(?:PROGMEM\s*)?=\s*\{(.*?)\};" % name, src, re.S).group(1))]
        fonts[weight] = {"name": name, "glyphs": glyphs, "bitmaps": bitmaps,
                         "first": first, "last": last, "y_advance": y_advance}
    count = sum(e - s + 1 for s, e, _ in ranges)
    for weight, f in fonts.items():
        if len(f["glyphs"]) != count:
            sys.exit(f"{weight}: {len(f['glyphs'])} glyphs, but the ranges name {count}")
    return ranges, fonts


def glyph_rows(bitmaps, offset, w, h):
    bits = [(bitmaps[offset + (i >> 3)] >> (7 - (i & 7))) & 1 for i in range(w * h)]
    return [bits[r * w:(r + 1) * w] for r in range(h)]


def close_gaps(rows):
    """Keep one row of every run of blank rows between inked rows; return rows, rows removed."""
    inked = [r for r, row in enumerate(rows) if any(row)]
    keep, removed = [], 0
    for r, row in enumerate(rows):
        inside = inked and inked[0] < r < inked[-1]
        if inside and not any(row) and not any(rows[r - 1]):
            removed += 1
            continue
        keep.append(row)
    return keep, removed


def pack(rows, w):
    bits = [b for row in rows for b in row]
    out = []
    for i in range(0, len(bits), 8):
        chunk = bits[i:i + 8] + [0] * (8 - len(bits[i:i + 8]))
        out.append(sum(b << (7 - k) for k, b in enumerate(chunk)))
    return out


def metric(glyphs):
    ascent = max(-g[5] for g in glyphs)
    descent = max(g[2] + g[5] for g in glyphs)
    return ascent, descent, ascent + descent


def build(ranges, fonts):
    ascii_count = ranges[0][1] - ranges[0][0] + 1
    out = {}
    for weight, f in fonts.items():
        ascii_ascent = metric(f["glyphs"][:ascii_count])[0]
        data, glyphs, changed = [], [], []
        for i, (off, w, h, adv, xo, yo) in enumerate(f["glyphs"]):
            rows = glyph_rows(f["bitmaps"], off, w, h)
            if -yo > ascii_ascent:
                rows, removed = close_gaps(rows)
                if removed:
                    changed.append(i)
                    h, yo = h - removed, yo + removed       # bottom row stays on the same line
            glyphs.append((len(data), w, h, adv, xo, yo))
            data += pack(rows, w)
        out[weight] = {"data": data, "glyphs": glyphs, "changed": changed,
                       "before": metric(f["glyphs"]), "after": metric(glyphs)}
    return out


def codepoint(ranges, index):
    for start, end, base in ranges:
        if base <= index <= base + (end - start):
            return start + index - base


def render(ranges, fonts, built):
    lines = [
        "#ifndef INTELONEMONO12PT_SCROLL_COMPACT_H_",
        "#define INTELONEMONO12PT_SCROLL_COMPACT_H_",
        "",
        "// Auto-generated by Software/tools/scroll-font/make_compact_scroll_font.py from",
        "// IntelOneMono12ptScroll.h - do not edit; regenerate when that file changes.",
        "//",
        "// The small scroll font at a shorter line pitch, for panels that fit one more row that way.",
        "// Same glyphs and the same font names as IntelOneMono12ptScroll.h, so a build selects it by",
        "// including this header instead (SCROLL_FONT_COMPACT_UMLAUTS). The one difference: glyphs",
        "// that rise above printable ASCII - the capital umlauts - keep a single blank row between",
        "// their dots and the letter instead of two.",
    ]
    for weight in WEIGHTS:
        b = built[weight]
        lines.append(f"//   {weight}: line pitch {b['before'][2]} -> {b['after'][2]} px "
                     f"(ascent {b['before'][0]} -> {b['after'][0]}, descent {b['after'][1]}), "
                     f"glyphs changed: {', '.join(hex(codepoint(ranges, i)) for i in b['changed'])}")
    lines += ["", "#include <LovyanGFX.hpp>", "",
              "static const lgfx::EncodeRange IntelOneMono12ptScrollCompactRanges[] PROGMEM = {"]
    lines += [f"  {{ 0x{s:02X}, 0x{e:02X}, {base:3} }}," for s, e, base in ranges]
    lines += ["};", f"#define INTELONEMONO12PT_SCROLL_COMPACT_RANGES {len(ranges)}", ""]
    for weight in WEIGHTS:
        f, b = fonts[weight], built[weight]
        name = f["name"]
        lines.append(f"static const uint8_t {name}_ScrollCompactBitmaps[] PROGMEM = {{")
        for i in range(0, len(b["data"]), VALUES_PER_LINE):
            lines.append("  " + ", ".join(f"0x{v:02X}" for v in b["data"][i:i + VALUES_PER_LINE]) + ",")
        lines += ["};", "", f"static const lgfx::GFXglyph {name}_ScrollCompactGlyphs[] PROGMEM = {{"]
        for i, g in enumerate(b["glyphs"]):
            mark = "  // compacted" if i in b["changed"] else ""
            lines.append("  {{ {:5}, {:3}, {:3}, {:3}, {:4}, {:4} }},   // [{:3}] 0x{:02X}{}".format(
                *g, i, codepoint(ranges, i), mark))
        lines += ["};", "",
                  f"const lgfx::GFXfont {name}_Scroll PROGMEM = {{",
                  f"  (uint8_t *) {name}_ScrollCompactBitmaps,",
                  f"  (lgfx::GFXglyph *) {name}_ScrollCompactGlyphs,",
                  f"  0x{f['first']:02X}, 0x{f['last']:02X}, {f['y_advance']},",
                  "  INTELONEMONO12PT_SCROLL_COMPACT_RANGES, (lgfx::EncodeRange *) IntelOneMono12ptScrollCompactRanges",
                  "};", ""]
    lines.append("#endif")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail if the committed header is out of date")
    args = ap.parse_args()
    ranges, fonts = parse_source()
    built = build(ranges, fonts)
    text = render(ranges, fonts, built)
    for weight in WEIGHTS:
        b = built[weight]
        print(f"{weight}: pitch {b['before'][2]} -> {b['after'][2]} px, compacted "
              f"{[hex(codepoint(ranges, i)) for i in b['changed']]}")
    if args.check:
        if not TARGET.exists() or TARGET.read_text(encoding="utf-8") != text:
            sys.exit(f"{TARGET.name} is out of date - rerun without --check")
        print(f"ok: {TARGET.name} is current")
        return
    TARGET.write_text(text, encoding="utf-8")
    print(f"wrote {TARGET}")


if __name__ == "__main__":
    main()
