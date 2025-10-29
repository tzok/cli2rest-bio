#!/usr/bin/env python3
import argparse, subprocess, tempfile, os, sys
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def q(name):
    return f"{{{SVG_NS}}}{name}"


def main():
    p = argparse.ArgumentParser(
        description="Add a label to an SVG and export to PDF via Inkscape"
    )
    p.add_argument("input_svg")
    p.add_argument("label_text")
    p.add_argument("output_pdf")
    p.add_argument(
        "--x-percent",
        type=float,
        default=0.0,
        help="Horizontal position as percent (default 0)",
    )
    p.add_argument(
        "--y-percent",
        type=float,
        default=105.0,
        help="Vertical position as percent (default 105)",
    )
    p.add_argument("--font-family", default="DejaVu Sans")
    p.add_argument("--font-size", default="12pt")
    p.add_argument("--fill", default="#000000")
    args = p.parse_args()

    tree = ET.parse(args.input_svg)
    root = tree.getroot()

    text_el = ET.Element(
        q("text"),
        {
            "x": f"{args.x_percent}%",
            "y": f"{args.y_percent}%",
            "text-anchor": "left",
            "font-family": args.font_family,
            "font-size": args.font_size,
            "fill": args.fill,
        },
    )
    text_el.text = args.label_text
    root.append(text_el)

    with tempfile.TemporaryDirectory() as td:
        tmp_svg = os.path.join(td, "tmp.svg")
        tree.write(tmp_svg, encoding="utf-8", xml_declaration=True)
        cmd = [
            "inkscape",
            tmp_svg,
            "--export-area-drawing",
            f"--export-filename={args.output_pdf}",
        ]
        try:
            subprocess.run(
                cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            sys.stderr.write(e.stderr.decode(errors="ignore"))
            sys.exit(e.returncode)


if __name__ == "__main__":
    main()
