#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from tempfile import TemporaryDirectory
from typing import DefaultDict, Deque, Dict, List, Optional, Tuple, TypedDict

import RNA
from lxml import etree


class SymbolType(Enum):
    BEGIN = 0
    END = 1
    NONE = 2


@dataclass(frozen=True)
class Symbol:
    allowed: bool
    type: SymbolType
    sibling: Optional[str]


SYMBOLS: Dict[str, Symbol] = {
    ".": Symbol(True, SymbolType.NONE, None),
    "-": Symbol(False, SymbolType.NONE, None),
    "(": Symbol(True, SymbolType.BEGIN, ")"),
    ")": Symbol(True, SymbolType.END, "("),
    "[": Symbol(False, SymbolType.BEGIN, "]"),
    "]": Symbol(False, SymbolType.END, "["),
    "{": Symbol(False, SymbolType.BEGIN, "}"),
    "}": Symbol(False, SymbolType.END, "{"),
    "<": Symbol(False, SymbolType.BEGIN, ">"),
    ">": Symbol(False, SymbolType.END, "<"),
    "A": Symbol(False, SymbolType.BEGIN, "a"),
    "a": Symbol(False, SymbolType.END, "A"),
    "B": Symbol(False, SymbolType.BEGIN, "b"),
    "b": Symbol(False, SymbolType.END, "B"),
    "C": Symbol(False, SymbolType.BEGIN, "c"),
    "c": Symbol(False, SymbolType.END, "C"),
    "D": Symbol(False, SymbolType.BEGIN, "d"),
    "d": Symbol(False, SymbolType.END, "D"),
    "E": Symbol(False, SymbolType.BEGIN, "e"),
    "e": Symbol(False, SymbolType.END, "E"),
}

COLORS: Dict[str, str] = {
    "]": "0.18 0.439 0.071",
    "}": "0.059 0.125 0.373",
    ">": "0.514 0.075 0",
    "a": "0.333 0.043 0.357",
    "b": "0.29 0.447 0.616",
    "c": "0.545 0.463 0.02",
    "d": "0.773 0.396 0.812",
    "e": "0.624 0.725 0.145",
    "NOT_REPRESENTED": "0.5 0.5 0.5",
    "-": "1 0 0",
    "BASE_PAIR": "0 0 0",
}

SVG_NS = "http://www.w3.org/2000/svg"
OUTPUT_SVG = "rna.svg"
MAX_STRUCTURE_LENGTH = 32767


class StrandInput(TypedDict):
    name: str
    sequence: str
    structure: str


class InteractionInput(TypedDict):
    i: int
    j: int
    lw: Optional[str]
    color: Optional[str]


class PuzzlerInput(TypedDict):
    strands: List[StrandInput]
    interactions: Optional[List[InteractionInput]]


@dataclass(frozen=True)
class PuzzlerInteraction:
    number_left: int
    number_right: int
    color: str


def color_to_svg(color_str: str) -> str:
    color_str = color_str.strip()
    if not color_str:
        return "rgb(128,128,128)"
    if color_str.startswith("#"):
        return color_str
    if color_str.startswith("rgb("):
        return color_str
    if "," in color_str:
        parts = [part.strip() for part in color_str.split(",")]
        if len(parts) == 3:
            return f"rgb({int(parts[0])},{int(parts[1])},{int(parts[2])})"
    parts = color_str.split()
    if len(parts) != 3:
        raise ValueError(f"Unsupported color format: {color_str}")
    r = int(round(float(parts[0]) * 255))
    g = int(round(float(parts[1]) * 255))
    b = int(round(float(parts[2]) * 255))
    return f"rgb({r},{g},{b})"


def load_and_validate_json(file_path: str) -> PuzzlerInput:
    try:
        with open(file_path, "r") as f:
            data: PuzzlerInput = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}", file=sys.stderr)
        raise
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}", file=sys.stderr)
        raise

    if "strands" not in data or not isinstance(data["strands"], list):
        raise ValueError("Missing or invalid 'strands' in JSON data.")
    if not data["strands"]:
        raise ValueError("'strands' list must not be empty.")

    for idx, strand in enumerate(data["strands"]):
        if not isinstance(strand, dict):
            raise ValueError(f"Strand at index {idx} must be an object.")
        for field in ("name", "sequence", "structure"):
            if field not in strand or not isinstance(strand[field], str):
                raise ValueError(f"Strand at index {idx} missing or invalid '{field}'.")
        if len(strand["sequence"]) != len(strand["structure"]):
            raise ValueError(
                f"Strand '{strand['name']}': sequence length ({len(strand['sequence'])}) "
                f"!= structure length ({len(strand['structure'])})"
            )

    if "interactions" in data and data["interactions"] is not None:
        if not isinstance(data["interactions"], list):
            raise ValueError("'interactions' must be a list.")
        for idx, interaction in enumerate(data["interactions"]):
            if not isinstance(interaction, dict):
                raise ValueError(f"Interaction at index {idx} must be an object.")
            for field in ("i", "j"):
                if field not in interaction or not isinstance(interaction[field], int):
                    raise ValueError(
                        f"Interaction at index {idx} missing or invalid '{field}'."
                    )
                if interaction[field] <= 0:
                    raise ValueError(
                        f"Interaction at index {idx} has non-positive '{field}': {interaction[field]}"
                    )

    return data


def preprocess(
    data: PuzzlerInput,
) -> Tuple[str, str, List[PuzzlerInteraction], List[int]]:
    sequence = "".join(s["sequence"] for s in data["strands"])
    structure_raw = "".join(s["structure"] for s in data["strands"])

    interactions: List[PuzzlerInteraction] = []
    missing_res_numbers: List[int] = []
    modified_structure_chars: List[str] = []
    residue_stack: DefaultDict[str, Deque[int]] = defaultdict(deque)

    for i, char in enumerate(structure_raw):
        symbol = SYMBOLS.get(char)
        if symbol is None:
            raise ValueError(f"Unknown structure symbol '{char}' at position {i + 1}")
        if symbol.allowed:
            modified_structure_chars.append(char)
        else:
            modified_structure_chars.append(".")
            if char == "-":
                missing_res_numbers.append(i + 1)
            else:
                if symbol.type == SymbolType.BEGIN:
                    residue_stack[char].append(i + 1)
                else:
                    if not residue_stack[symbol.sibling]:  # type: ignore
                        raise ValueError(
                            f"Unmatched closing symbol '{char}' at position {i + 1}"
                        )
                    interactions.append(
                        PuzzlerInteraction(
                            residue_stack[symbol.sibling].pop(),  # type: ignore
                            i + 1,
                            COLORS[char],
                        )
                    )

    modified_structure = "".join(modified_structure_chars)

    structure_copy = modified_structure
    modified_structure = modified_structure.replace("()", "..")

    for idx, (old, new) in enumerate(zip(structure_copy, modified_structure)):
        if old != new and old == "(":
            interactions.append(
                PuzzlerInteraction(
                    idx + 1,
                    idx + 2,
                    COLORS["BASE_PAIR"],
                )
            )

    extra_interactions = data.get("interactions")
    if extra_interactions:
        for interaction in extra_interactions:
            interactions.append(
                PuzzlerInteraction(
                    interaction["i"],
                    interaction["j"],
                    interaction.get("color") or COLORS["NOT_REPRESENTED"],
                )
            )

    return sequence, modified_structure, interactions, missing_res_numbers


def generate_rnapuzzler_svg(sequence: str, structure: str) -> str:
    seq_len = len(sequence)
    if seq_len > MAX_STRUCTURE_LENGTH:
        raise RuntimeError(
            f"Maximum structure length ({MAX_STRUCTURE_LENGTH}) for RNApuzzler exceeded"
        )

    layout = RNA.plot_layout(structure, RNA.PLOT_TYPE_PUZZLER)

    with TemporaryDirectory() as directory:
        output_file = os.path.join(directory, OUTPUT_SVG)
        result = RNA.plot_structure_svg(output_file, sequence, structure, layout)

        if result == 0 or not os.path.isfile(output_file):
            raise RuntimeError("RNApuzzler SVG was not created!")

        with open(output_file, "r", encoding="utf-8") as f:
            svg_content = f.read()

        if "<svg" not in svg_content:
            raise RuntimeError("RNApuzzler output is not a valid SVG!")

    return svg_content


def extract_nucleotide_coords(
    root: etree._Element,
) -> List[Tuple[float, float]]:
    coords: List[Tuple[float, float]] = []
    seq_group = find_seq_group_by_text(root)
    if seq_group is None:
        return coords

    for text_elem in seq_group.findall(f"{{{SVG_NS}}}text"):
        x = float(text_elem.get("x", "0"))
        y = float(text_elem.get("y", "0"))
        coords.append((x, y))

    if not coords:
        for text_elem in seq_group.findall("text"):
            x = float(text_elem.get("x", "0"))
            y = float(text_elem.get("y", "0"))
            coords.append((x, y))

    return coords


def find_seq_group_by_text(root: etree._Element) -> Optional[etree._Element]:
    g = root.find(f".//{{{SVG_NS}}}g[@id='seq']")
    if g is None:
        g = root.find(".//g[@id='seq']")
    if g is not None:
        return g

    for g in root.iter(f"{{{SVG_NS}}}g"):
        if g.get("font-family") and g.findall(f"{{{SVG_NS}}}text"):
            return g
    for g in root.iter("g"):
        if g.get("font-family") and g.findall("text"):
            return g

    return None


def find_main_group(root: etree._Element) -> Optional[etree._Element]:
    for child in root:
        if child.tag == f"{{{SVG_NS}}}g" or child.tag == "g":
            if child.get("transform"):
                return child
    return None


def find_seq_group(main_group: etree._Element) -> Optional[etree._Element]:
    for child in main_group:
        tag = child.tag
        if (tag == f"{{{SVG_NS}}}g" or tag == "g") and child.get("id") == "seq":
            return child
    for child in main_group:
        tag = child.tag
        if tag == f"{{{SVG_NS}}}g" or tag == "g":
            if child.get("font-family") and (
                child.findall(f"{{{SVG_NS}}}text") or child.findall("text")
            ):
                return child
    return None


def update_css_styles(root: etree._Element) -> None:
    style_elem = root.find(f".//{{{SVG_NS}}}style")
    if style_elem is None:
        style_elem = root.find(".//style")
    if style_elem is None:
        return

    css = style_elem.text or ""
    css = css.replace("stroke: grey", "stroke: rgb(191,191,191)")
    css = css.replace("stroke: red", "stroke: black")
    style_elem.text = css


def center_nucleotide_labels(seq_group: etree._Element) -> None:
    if seq_group.get("transform"):
        del seq_group.attrib["transform"]
    seq_group.set("text-anchor", "middle")
    seq_group.set("dominant-baseline", "central")


def add_interaction_lines(
    main_group: etree._Element,
    seq_group: etree._Element,
    coords: List[Tuple[float, float]],
    interactions: List[PuzzlerInteraction],
) -> None:
    children = list(main_group)
    try:
        insert_idx = children.index(seq_group)
    except ValueError:
        insert_idx = len(children)

    interactions_group = etree.Element(f"{{{SVG_NS}}}g", attrib={"id": "interactions"})

    for interaction in interactions:
        idx_left = interaction.number_left - 1
        idx_right = interaction.number_right - 1

        if idx_left < 0 or idx_left >= len(coords):
            continue
        if idx_right < 0 or idx_right >= len(coords):
            continue

        x1, y1 = coords[idx_left]
        x2, y2 = coords[idx_right]
        svg_color = color_to_svg(interaction.color)

        line_attrib: Dict[str, str] = {
            "x1": f"{x1:.3f}",
            "y1": f"{y1:.3f}",
            "x2": f"{x2:.3f}",
            "y2": f"{y2:.3f}",
            "stroke": svg_color,
            "fill": "none",
        }

        if interaction.color == COLORS["NOT_REPRESENTED"]:
            line_attrib["stroke-width"] = "1.5"
            line_attrib["stroke-dasharray"] = "3 6"
        elif interaction.color == COLORS["BASE_PAIR"]:
            line_attrib["stroke-width"] = "1"
            line_attrib["stroke-dasharray"] = "9 3.01"
            line_attrib["stroke-dashoffset"] = "9"
        else:
            line_attrib["stroke-width"] = "1.5"

        etree.SubElement(interactions_group, f"{{{SVG_NS}}}line", attrib=line_attrib)

    main_group.insert(insert_idx, interactions_group)


def add_missing_residue_markers(
    main_group: etree._Element,
    seq_group: etree._Element,
    coords: List[Tuple[float, float]],
    missing_res_numbers: List[int],
) -> None:
    if not missing_res_numbers:
        return

    children = list(main_group)
    try:
        insert_idx = children.index(seq_group)
    except ValueError:
        insert_idx = len(children)

    missing_color = color_to_svg(COLORS["-"])
    markers_group = etree.Element(f"{{{SVG_NS}}}g", attrib={"id": "missing-residues"})

    for number in missing_res_numbers:
        idx = number - 1
        if idx < 0 or idx >= len(coords):
            continue

        x, y = coords[idx]
        circle_attrib = {
            "cx": f"{x:.3f}",
            "cy": f"{y:.3f}",
            "r": "10",
            "stroke": missing_color,
            "stroke-width": "1",
            "fill": "none",
        }
        etree.SubElement(markers_group, f"{{{SVG_NS}}}circle", attrib=circle_attrib)

    main_group.insert(insert_idx, markers_group)


def split_backbone_at_strand_boundaries(
    main_group: etree._Element, strands: List[StrandInput]
) -> None:
    if len(strands) <= 1:
        return

    boundaries: set = set()
    cumulative = 0
    for strand in strands[:-1]:
        cumulative += len(strand["sequence"])
        boundaries.add(cumulative)

    polylines = []
    for child in list(main_group):
        tag = child.tag
        if tag == f"{{{SVG_NS}}}polyline" or tag == "polyline":
            cls = child.get("class", "")
            if "backbone" in cls:
                polylines.append(child)

    for polyline in polylines:
        points_str = polyline.get("points", "").strip()
        if not points_str:
            continue

        point_pairs = points_str.split("\n")
        points: List[Tuple[float, float]] = []
        for pair in point_pairs:
            pair = pair.strip()
            if not pair:
                continue
            parts = pair.split(",")
            if len(parts) == 2:
                try:
                    points.append((float(parts[0]), float(parts[1])))
                except ValueError:
                    continue

        if not points:
            continue

        polyline_id = polyline.get("id", "outline")
        if polyline_id == "outline":
            start_idx = 0
        else:
            try:
                n = int(polyline_id.replace("outline", ""))
                start_idx = n - 2
            except ValueError:
                start_idx = 0

        split_indices: List[int] = []
        for local_idx in range(len(points)):
            global_idx = start_idx + local_idx
            if global_idx in boundaries:
                split_indices.append(local_idx)

        if not split_indices:
            continue

        parent_idx = list(main_group).index(polyline)
        main_group.remove(polyline)

        segments: List[List[Tuple[float, float]]] = []
        prev = 0
        for split_idx in split_indices:
            if prev <= split_idx:
                segments.append(points[prev:split_idx])
            prev = split_idx
        segments.append(points[prev:])

        for seg_i, segment in enumerate(reversed(segments)):
            if len(segment) < 2:
                continue
            pts = "\n".join(f"      {x:.3f},{y:.3f}" for x, y in segment)
            new_poly = etree.Element(
                f"{{{SVG_NS}}}polyline",
                attrib={
                    "class": "backbone",
                    "id": f"{polyline_id}_s{len(segments) - 1 - seg_i}",
                    "points": f"\n{pts}\n    ",
                },
            )
            main_group.insert(parent_idx, new_poly)


def remove_scripts(root: etree._Element) -> None:
    for script in root.findall(f".//{{{SVG_NS}}}script"):
        parent = script.getparent()
        if parent is not None:
            parent.remove(script)
    for script in root.findall(".//script"):
        parent = script.getparent()
        if parent is not None:
            parent.remove(script)


def remove_background_rect_onclick(root: etree._Element) -> None:
    for rect in root.iter(f"{{{SVG_NS}}}rect"):
        if rect.get("onclick"):
            del rect.attrib["onclick"]
    for rect in root.iter("rect"):
        if rect.get("onclick"):
            del rect.attrib["onclick"]


def postprocess_svg(
    svg_content: str,
    strands: List[StrandInput],
    interactions: List[PuzzlerInteraction],
    missing_res_numbers: List[int],
) -> str:
    root = etree.fromstring(svg_content.encode("utf-8"))

    update_css_styles(root)

    main_group = find_main_group(root)
    if main_group is None:
        return svg_content

    coords = extract_nucleotide_coords(root)

    seq_group = find_seq_group(main_group)

    if seq_group is not None:
        center_nucleotide_labels(seq_group)

    split_backbone_at_strand_boundaries(main_group, strands)

    if seq_group is not None and coords:
        add_missing_residue_markers(main_group, seq_group, coords, missing_res_numbers)
        add_interaction_lines(main_group, seq_group, coords, interactions)

    remove_scripts(root)
    remove_background_rect_onclick(root)

    return etree.tostring(root, encoding="UTF-8", xml_declaration=True).decode("UTF-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="RNApuzzler wrapper script.")
    parser.add_argument(
        "json_file",
        type=str,
        help="Path to the input JSON file for RNApuzzler.",
    )
    args = parser.parse_args()

    try:
        data = load_and_validate_json(args.json_file)
        sequence, structure, interactions, missing_res_numbers = preprocess(data)
        svg_content = generate_rnapuzzler_svg(sequence, structure)
        postprocessed = postprocess_svg(
            svg_content, data["strands"], interactions, missing_res_numbers
        )

        with open("output.svg", "w", encoding="utf-8") as f:
            f.write(postprocessed)

        svgcleaner_cmd = ["svgcleaner", "output.svg", "clean.svg"]
        subprocess.run(svgcleaner_cmd, capture_output=True, text=True, check=True)

    except Exception as e:
        print(f"Processing failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
