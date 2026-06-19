#!/usr/bin/python3
import argparse
import json
import math
import os
import re
import subprocess
import sys
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from tempfile import TemporaryDirectory
from typing import (
    DefaultDict,
    Deque,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    TypedDict,
    Union,
)

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
    "NOT_REPRESENTED": "#6b7280",
    "-": "1 0 0",
}

CSS_COLOR_NAMES: Dict[str, str] = {
    "black": "#000000",
    "blue": "#0000ff",
    "cyan": "#00ffff",
    "gray": "#808080",
    "green": "#008000",
    "grey": "#808080",
    "magenta": "#ff00ff",
    "orange": "#ffa500",
    "purple": "#800080",
    "red": "#ff0000",
    "white": "#ffffff",
    "yellow": "#ffff00",
}

SVG_NS = "http://www.w3.org/2000/svg"
OUTPUT_SVG = "rna.svg"
MAX_STRUCTURE_LENGTH = 32767
NUCLEOTIDE_RADIUS = 8.0
SYMBOL_RADIUS = NUCLEOTIDE_RADIUS * 0.5
INNER_SCALE = 0.45
CANONICAL_BP_COLOR = "#c0c0c0"
CIRCLE_FILL = "#f7f7f7"
CIRCLE_STROKE = "#777777"
CIRCLE_STROKE_WIDTH = "1"
MISSING_CIRCLE_STROKE = "#d32f2f"
MISSING_TEXT_FILL = "#d32f2f"
LINE_PADDING = NUCLEOTIDE_RADIUS + float(CIRCLE_STROKE_WIDTH) / 2.0

LW_EDGE_MAP = {"W": "W", "H": "H", "S": "S"}
BP_STYLES = {"simple", "lw", "lw_alt"}
STACKING_PLACEMENTS = {
    "centered",
    "first-partner",
    "second-partner",
    "both-partners",
    "opposing-partners",
}

SYMBOL_OPTIMIZATION_CANDIDATES = 15
SYMBOL_OVERLAP_WEIGHT = 100.0
CIRCLE_OVERLAP_WEIGHT = 100.0
PREFERENCE_WEIGHT = 0.1
SYMBOL_OVERLAP_MARGIN = 1.0
DEFAULT_NUM_PERIOD = 10
NUMBER_TICK_LENGTH = 5.0
NUMBER_GAP = 4.0
NUMBER_FONT_SIZE = "7"
NUMBER_FONT_WEIGHT = "bold"
NUMBER_COLOR = "#555555"


class StrandInput(TypedDict):
    name: str
    sequence: str
    structure: str


class InteractionInput(TypedDict):
    i: int
    j: int
    lw: Optional[str]
    color: Optional[str]
    style: Optional[str]


class StackingInput(TypedDict):
    i: int
    j: int
    color: Optional[str]
    thickness: Optional[Union[int, float, str]]


class PuzzlerInput(TypedDict):
    strands: List[StrandInput]
    interactions: Optional[List[InteractionInput]]
    stackings: Optional[List[StackingInput]]
    nucleotide_colors: Optional[Dict[str, str]]
    num_labels: Optional[Dict[str, str]]
    num_period: Optional[int]
    bp_style: Optional[str]
    stacking_arrow_placement: Optional[str]
    stacking_arrow_gap: Optional[float]
    draw_backbone: Optional[bool]
    debug: Optional[bool]


@dataclass(frozen=True)
class PuzzlerInteraction:
    number_left: int
    number_right: int
    color: str
    stroke_width: str = "2"
    dasharray: Optional[str] = None
    dashoffset: Optional[str] = None
    lw: Optional[str] = None
    edge5: Optional[str] = None
    edge3: Optional[str] = None
    cis: bool = True
    style: str = "lw"
    is_canonical: bool = False


@dataclass(frozen=True)
class PuzzlerStacking:
    number_left: int
    number_right: int
    color: str
    stroke_width: str = "2.5"
    arrow_placement: str = "centered"
    arrow_gap: Optional[float] = None


@dataclass
class SymbolPlacement:
    """A candidate optimizable LW symbol (or rigid pair of symbols) on a bond."""

    style: str  # "single", "pair", "alt"
    ideal_center: Tuple[float, float]
    center: Tuple[float, float]
    radius: float
    nucleotide_i: int
    nucleotide_j: int
    preferred_t: float
    ux: float
    uy: float
    dist: float
    angle: float
    edge5: str
    edge3: str
    cis: bool
    color: str
    stroke_width: str
    symbol_radius: float
    pair_offset: float = 0.0


def color_to_svg(color_str: str) -> str:
    color_str = color_str.strip()
    if not color_str:
        return "rgb(128,128,128)"
    lower = color_str.lower()
    if lower in CSS_COLOR_NAMES:
        return CSS_COLOR_NAMES[lower]
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


def parse_lw(lw: str) -> Optional[Tuple[bool, str, str]]:
    """Parse a Leontis–Westhof string (e.g. 'cWW', 'tWH') into (cis, edge5, edge3)."""
    if not lw or len(lw) != 3:
        return None
    s = lw.upper()
    if s[0] == "C":
        cis = True
    elif s[0] == "T":
        cis = False
    else:
        return None
    edge5 = LW_EDGE_MAP.get(s[1])
    edge3 = LW_EDGE_MAP.get(s[2])
    if edge5 is None or edge3 is None:
        return None
    return cis, edge5, edge3


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

    if "stackings" in data and data["stackings"] is not None:
        if not isinstance(data["stackings"], list):
            raise ValueError("'stackings' must be a list.")
        for idx, stacking in enumerate(data["stackings"]):
            if not isinstance(stacking, dict):
                raise ValueError(f"Stacking at index {idx} must be an object.")
            for field in ("i", "j"):
                if field not in stacking or not isinstance(stacking[field], int):
                    raise ValueError(
                        f"Stacking at index {idx} missing or invalid '{field}'."
                    )
                if stacking[field] <= 0:
                    raise ValueError(
                        f"Stacking at index {idx} has non-positive '{field}': {stacking[field]}"
                    )

    if data.get("bp_style") is not None and data["bp_style"].lower() not in BP_STYLES:
        raise ValueError(
            f"Invalid bp_style '{data['bp_style']}'. Allowed: {sorted(BP_STYLES)}."
        )

    if data.get("stacking_arrow_placement") is not None:
        placement = data["stacking_arrow_placement"].lower()
        if placement not in STACKING_PLACEMENTS:
            raise ValueError(
                f"Invalid stacking_arrow_placement '{data['stacking_arrow_placement']}'. "
                f"Allowed: {sorted(STACKING_PLACEMENTS)}."
            )

    if data.get("draw_backbone") is not None and not isinstance(
        data["draw_backbone"], bool
    ):
        raise ValueError("'draw_backbone' must be a boolean.")

    if data.get("debug") is not None and not isinstance(data["debug"], bool):
        raise ValueError("'debug' must be a boolean.")

    return data


def preprocess(
    data: PuzzlerInput,
) -> Tuple[
    str, str, List[PuzzlerInteraction], List[PuzzlerStacking], List[int], Set[int]
]:
    orig_lengths = [len(s["sequence"]) for s in data["strands"]]

    # --- build phantom-included sequence and structure ---
    seq_parts: List[str] = []
    struct_parts: List[str] = []
    phantom_positions: Set[int] = set()
    cumulative = 0
    for i, (seq, struct) in enumerate(
        zip(
            (s["sequence"] for s in data["strands"]),
            (s["structure"] for s in data["strands"]),
        )
    ):
        seq_parts.append(seq)
        struct_parts.append(struct)
        cumulative += len(seq)
        if i < len(orig_lengths) - 1:
            phantom_positions.add(cumulative + 1)  # 1‑based in new numbering
            seq_parts.append("N")
            struct_parts.append(".")
    sequence = "".join(seq_parts)
    structure_raw = "".join(struct_parts)

    # --- position shifter (original → phantom‑included) ---
    def shift_pos(p: int) -> int:
        result = p
        cumsum = 0
        for length in orig_lengths[:-1]:
            cumsum += length
            if p > cumsum:
                result += 1
        return result

    bp_style = (data.get("bp_style") or "lw").lower()
    if bp_style not in BP_STYLES:
        bp_style = "lw"

    canonical_interactions: List[PuzzlerInteraction] = []
    custom_interactions: List[PuzzlerInteraction] = []
    stackings: List[PuzzlerStacking] = []
    missing_res_numbers: List[int] = []
    modified_structure_chars: List[str] = []
    residue_stack: DefaultDict[str, Deque[int]] = defaultdict(deque)

    for i, char in enumerate(structure_raw):
        symbol = SYMBOLS.get(char)
        if symbol is None:
            raise ValueError(f"Unknown structure symbol '{char}' at position {i + 1}")
        # Phantom positions are always unpaired – skip them during parsing.
        if (i + 1) in phantom_positions:
            modified_structure_chars.append(".")
            continue
        if symbol.allowed:
            modified_structure_chars.append(char)
            if char == "(":
                residue_stack[char].append(i + 1)
            elif char == ")":
                if not residue_stack[symbol.sibling]:  # type: ignore[arg-type]
                    raise ValueError(
                        f"Unmatched closing symbol '{char}' at position {i + 1}"
                    )
                canonical_interactions.append(
                    PuzzlerInteraction(
                        residue_stack[symbol.sibling].pop(),  # type: ignore[arg-type]
                        i + 1,
                        "rgb(0,0,0)",
                        is_canonical=True,
                    )
                )
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
                    custom_interactions.append(
                        PuzzlerInteraction(
                            residue_stack[symbol.sibling].pop(),  # type: ignore
                            i + 1,
                            COLORS[char],
                            style="simple",
                        )
                    )

    modified_structure = "".join(modified_structure_chars)

    extra_interactions = data.get("interactions")
    if extra_interactions:
        for interaction in extra_interactions:
            color = interaction.get("color") or COLORS["NOT_REPRESENTED"]
            style = (interaction.get("style") or bp_style).lower()
            if style not in BP_STYLES:
                style = bp_style
            lw = interaction.get("lw")
            parsed = parse_lw(lw) if lw else None
            if parsed is None:
                style = "simple"
            custom_interactions.append(
                PuzzlerInteraction(
                    shift_pos(interaction["i"]),
                    shift_pos(interaction["j"]),
                    color,
                    lw=lw,
                    edge5=parsed[1] if parsed else None,
                    edge3=parsed[2] if parsed else None,
                    cis=parsed[0] if parsed else True,
                    style=style,
                )
            )

    extra_stackings = data.get("stackings")
    if extra_stackings:
        placement = (data.get("stacking_arrow_placement") or "centered").lower()
        if placement not in STACKING_PLACEMENTS:
            placement = "centered"
        gap = data.get("stacking_arrow_gap")
        for stacking in extra_stackings:
            color = stacking.get("color") or "#4a90e2"
            thickness = str(stacking.get("thickness", "2.5"))
            stackings.append(
                PuzzlerStacking(
                    shift_pos(stacking["i"]),
                    shift_pos(stacking["j"]),
                    color,
                    stroke_width=thickness,
                    arrow_placement=placement,
                    arrow_gap=gap,
                )
            )

    for symbol, stack in residue_stack.items():
        if stack:
            raise ValueError(f"Unmatched opening symbol '{symbol}' in structure")

    custom_pairs = {
        tuple(sorted((interaction.number_left, interaction.number_right)))
        for interaction in custom_interactions
    }
    interactions = [
        interaction
        for interaction in canonical_interactions
        if tuple(sorted((interaction.number_left, interaction.number_right)))
        not in custom_pairs
    ]
    interactions.extend(custom_interactions)

    return (
        sequence,
        modified_structure,
        interactions,
        stackings,
        missing_res_numbers,
        phantom_positions,
    )


def generate_rnapuzzler_svg(sequence: str, structure: str) -> str:
    seq_len = len(sequence)
    if seq_len > MAX_STRUCTURE_LENGTH:
        raise RuntimeError(
            f"Maximum structure length ({MAX_STRUCTURE_LENGTH}) for RNApuzzler exceeded"
        )

    with TemporaryDirectory() as directory:
        subprocess.run(
            ["RNAplot", "-t", "4", "--output-format=svg"],
            input=f">rna\n{sequence}\n{structure}\n",
            capture_output=True,
            cwd=directory,
            text=True,
            check=True,
        )

        svg_candidates = [
            os.path.join(directory, filename)
            for filename in os.listdir(directory)
            if filename.endswith(".svg")
        ]

        if not svg_candidates:
            raise RuntimeError("RNApuzzler SVG was not created!")

        with open(svg_candidates[0], "r", encoding="utf-8") as f:
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


def get_main_group_scale(main_group: Optional[etree._Element]) -> float:
    """Return the average uniform scale factor applied by RNAplot's root <g>."""
    if main_group is None:
        return 1.0
    transform = main_group.get("transform") or ""
    match = re.search(r"scale\(([^)]+)\)", transform)
    if not match:
        return 1.0
    parts = [p for p in re.split(r"[,\s]+", match.group(1).strip()) if p]
    if not parts:
        return 1.0
    try:
        sx = float(parts[0])
        sy = float(parts[1]) if len(parts) > 1 else sx
    except ValueError:
        return 1.0
    return (abs(sx) + abs(sy)) / 2.0


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
    css = css.replace("stroke: grey", f"stroke: {CANONICAL_BP_COLOR}")
    css = css.replace("stroke: red", "stroke: black")
    style_elem.text = css


def center_nucleotide_labels(
    seq_group: etree._Element,
    nucleotide_colors: Optional[Dict[str, str]] = None,
    missing_res_numbers: Optional[List[int]] = None,
    phantom_positions: Optional[Set[int]] = None,
) -> None:
    if seq_group.get("transform"):
        del seq_group.attrib["transform"]
    seq_group.set("text-anchor", "middle")
    seq_group.set("dominant-baseline", "central")
    seq_group.set("fill", "#333333")
    seq_group.set("font-family", "sans-serif")

    missing_set = {str(n) for n in missing_res_numbers or []}
    phantom_set = phantom_positions or set()

    def _style_text(text_elem: etree._Element, pos: str) -> None:
        text_elem.set("font-family", "sans-serif")
        if int(pos) in phantom_set:
            text_elem.set("display", "none")
        elif pos in missing_set:
            text_elem.set("fill", MISSING_TEXT_FILL)
            text_elem.set("stroke", "none")
            text_elem.set("stroke-width", "0")
        elif nucleotide_colors and pos in nucleotide_colors:
            svg_color = color_to_svg(nucleotide_colors[pos])
            text_elem.set("fill", svg_color)
            text_elem.set("stroke", "none")
            text_elem.set("stroke-width", "0")

    for i, text_elem in enumerate(seq_group.findall(f"{{{SVG_NS}}}text")):
        _style_text(text_elem, str(i + 1))
    for i, text_elem in enumerate(seq_group.findall("text")):
        _style_text(text_elem, str(i + 1))


def shorten_line(
    x1: float, y1: float, x2: float, y2: float, padding: float = LINE_PADDING
) -> Tuple[float, float, float, float]:
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return x1, y1, x2, y2

    shrink = min(padding, max((length / 2) - 0.1, 0))
    ux = dx / length
    uy = dy / length
    return (
        x1 + (ux * shrink),
        y1 + (uy * shrink),
        x2 - (ux * shrink),
        y2 - (uy * shrink),
    )


def _points_to_svg(points: List[Tuple[float, float]]) -> str:
    return " ".join(f"{x:.3f},{y:.3f}" for x, y in points)


def _add_circle(
    group: etree._Element,
    cx: float,
    cy: float,
    radius: float,
    fill: str,
    stroke: str,
    stroke_width: str,
) -> None:
    etree.SubElement(
        group,
        f"{{{SVG_NS}}}circle",
        attrib={
            "cx": f"{cx:.3f}",
            "cy": f"{cy:.3f}",
            "r": f"{radius:.3f}",
            "fill": fill,
            "stroke": stroke,
            "stroke-width": stroke_width,
        },
    )


def _add_polygon(
    group: etree._Element,
    points: List[Tuple[float, float]],
    fill: str,
    stroke: str,
    stroke_width: str,
) -> None:
    etree.SubElement(
        group,
        f"{{{SVG_NS}}}polygon",
        attrib={
            "points": _points_to_svg(points),
            "fill": fill,
            "stroke": stroke,
            "stroke-width": stroke_width,
        },
    )


def _symbol_group(
    parent: etree._Element, cx: float, cy: float, angle: float
) -> etree._Element:
    # Translate the shape to (cx,cy) and then rotate it around its own center.
    return etree.SubElement(
        parent,
        f"{{{SVG_NS}}}g",
        attrib={
            "transform": f"translate({cx:.3f},{cy:.3f}) rotate({math.degrees(angle):.3f})"
        },
    )


def _square_points(side: float) -> List[Tuple[float, float]]:
    half = side / 2.0
    return [(-half, -half), (half, -half), (half, half), (-half, half)]


def _triangle_points(side: float) -> List[Tuple[float, float]]:
    """Return an equilateral triangle centered at its centroid, apex along +x."""
    height = (side * math.sqrt(3.0)) / 2.0
    return [
        (-height / 3.0, -side / 2.0),
        (-height / 3.0, side / 2.0),
        (2.0 * height / 3.0, 0.0),
    ]


def _draw_shape(
    group: etree._Element,
    cx: float,
    cy: float,
    angle: float,
    edge: str,
    radius: float,
    fill: str,
    stroke: str,
    stroke_width: str,
) -> None:
    if edge == "W":
        _add_circle(group, cx, cy, radius, fill, stroke, stroke_width)
    elif edge == "H":
        side = math.sqrt(math.pi) * radius
        g = _symbol_group(group, cx, cy, angle)
        _add_polygon(g, _square_points(side), fill, stroke, stroke_width)
    elif edge == "S":
        side = 2.0 * math.sqrt(math.pi / math.sqrt(3.0)) * radius
        g = _symbol_group(group, cx, cy, angle)
        _add_polygon(g, _triangle_points(side), fill, stroke, stroke_width)


def _draw_single_symbol(
    group: etree._Element,
    cx: float,
    cy: float,
    angle: float,
    edge: str,
    radius: float,
    cis: bool,
    color: str,
    stroke_width: str,
) -> None:
    fill = color if cis else "white"
    _draw_shape(group, cx, cy, angle, edge, radius, fill, color, stroke_width)


def _draw_lw_separate(
    group: etree._Element,
    cx: float,
    cy: float,
    ux: float,
    uy: float,
    edge5: str,
    edge3: str,
    cis: bool,
    color: str,
    stroke_width: str,
    dist: float,
    radius: float,
) -> None:
    # Place the two edge symbols on the bond, close to the midpoint.
    # The offset is capped so they do not drift toward the nucleotides on
    # long crossing interactions.
    angle = math.atan2(uy, ux)
    offset = min(radius * 1.6, max((dist / 2.0) - radius, 0.0))
    _draw_single_symbol(
        group,
        cx - ux * offset,
        cy - uy * offset,
        angle,
        edge5,
        radius,
        cis,
        color,
        stroke_width,
    )
    _draw_single_symbol(
        group,
        cx + ux * offset,
        cy + uy * offset,
        angle,
        edge3,
        radius,
        cis,
        color,
        stroke_width,
    )


def _draw_lw_alternative(
    group: etree._Element,
    cx: float,
    cy: float,
    angle: float,
    edge5: str,
    edge3: str,
    cis: bool,
    color: str,
    stroke_width: str,
    radius: float,
) -> None:
    # Outer shape masks the bond line with a white fill + colored outline.
    _draw_shape(group, cx, cy, angle, edge5, radius, "white", color, stroke_width)
    # Inner shape encodes the 3' edge, drawn smaller and nested inside.
    _draw_single_symbol(
        group,
        cx,
        cy,
        angle,
        edge3,
        radius * INNER_SCALE,
        cis,
        color,
        stroke_width,
    )


def _draw_filled_arrowhead(
    group: etree._Element,
    tip: Tuple[float, float],
    ux: float,
    uy: float,
    arrow_len: float,
    color: str,
) -> None:
    """Draw a solid triangular arrowhead.

    The triangle tip is placed at ``tip`` and points along ``(ux, uy)``.
    """
    if arrow_len <= 0.0:
        return
    bx = tip[0] - ux * arrow_len
    by = tip[1] - uy * arrow_len
    nx = -uy
    ny = ux
    half_base = arrow_len * math.tan(math.radians(22.5))
    p1x = bx + nx * half_base
    p1y = by + ny * half_base
    p2x = bx - nx * half_base
    p2y = by - ny * half_base
    points = _points_to_svg([(tip[0], tip[1]), (p1x, p1y), (p2x, p2y)])
    etree.SubElement(
        group,
        f"{{{SVG_NS}}}polygon",
        attrib={
            "points": points,
            "fill": color,
            "stroke": "none",
        },
    )


def _symbol_bounding_radius(edge: str, radius: float) -> float:
    """Return a circular bounding radius for the given LW edge symbol."""
    if edge == "H":
        # Square: half the diagonal.
        side = math.sqrt(math.pi) * radius
        return side / math.sqrt(2.0)
    if edge == "S":
        # Triangle: circumradius.
        side = 2.0 * math.sqrt(math.pi / math.sqrt(3.0)) * radius
        return side / math.sqrt(3.0)
    # Circle (W).
    return radius


def _placement_centers(
    placement: SymbolPlacement, cx: float, cy: float
) -> List[Tuple[float, float]]:
    """Return the center point(s) to use for overlap checks."""
    if placement.style == "pair":
        offset = placement.pair_offset
        ux, uy = placement.ux, placement.uy
        return [
            (cx - ux * offset, cy - uy * offset),
            (cx + ux * offset, cy + uy * offset),
        ]
    return [(cx, cy)]


def _obstacle_penalty(
    placement: SymbolPlacement,
    cx: float,
    cy: float,
    coords: List[Tuple[float, float]],
    fixed: List[SymbolPlacement],
) -> float:
    """Compute overlap penalty against nucleotide circles and fixed symbols."""
    penalty = 0.0
    radius = placement.radius
    for scx, scy in _placement_centers(placement, cx, cy):
        for nx, ny in coords:
            d = math.hypot(scx - nx, scy - ny)
            overlap = max(0.0, NUCLEOTIDE_RADIUS + radius - d)
            penalty += CIRCLE_OVERLAP_WEIGHT * overlap * overlap
        for other in fixed:
            for ocx, ocy in _placement_centers(other, other.center[0], other.center[1]):
                d = math.hypot(scx - ocx, scy - ocy)
                overlap = max(0.0, radius + other.radius - d)
                penalty += SYMBOL_OVERLAP_WEIGHT * overlap * overlap
    return penalty


def _candidate_t_values(placement: SymbolPlacement) -> List[float]:
    """Return candidate positions along the bond, respecting nucleotide circles."""
    dist = placement.dist
    if dist == 0.0:
        return [placement.preferred_t]
    margin = (NUCLEOTIDE_RADIUS + placement.radius + placement.pair_offset) / dist
    t_min = min(margin, 0.5)
    t_max = max(1.0 - margin, 0.5)
    if t_min > t_max:
        return [max(t_max, min(placement.preferred_t, t_min))]

    candidates = [
        t_min + (t_max - t_min) * i / (SYMBOL_OPTIMIZATION_CANDIDATES - 1)
        for i in range(SYMBOL_OPTIMIZATION_CANDIDATES)
    ]
    pref = max(t_min, min(placement.preferred_t, t_max))
    if all(abs(c - pref) > 1e-6 for c in candidates):
        candidates.append(pref)
    return candidates


def _optimize_symbol_placements(
    placements: List[SymbolPlacement],
    coords: List[Tuple[float, float]],
) -> None:
    """Place symbols greedily to minimize overlap while staying near the ideal spot."""
    if not placements:
        return

    # Place the most constrained symbols first.
    scored = []
    for p in placements:
        others = [q for q in placements if q is not p]
        penalty = _obstacle_penalty(
            p, p.ideal_center[0], p.ideal_center[1], coords, others
        )
        scored.append((penalty, p))
    scored.sort(key=lambda item: -item[0])

    fixed: List[SymbolPlacement] = []
    for _, placement in scored:
        x1, y1 = coords[placement.nucleotide_i]
        x2, y2 = coords[placement.nucleotide_j]
        ux, uy = placement.ux, placement.uy
        dist = placement.dist
        ideal_cx, ideal_cy = placement.ideal_center

        # Fast path: the ideal position already has no collisions with fixed
        # symbols or nucleotide circles.
        if _obstacle_penalty(placement, ideal_cx, ideal_cy, coords, fixed) < 1e-9:
            placement.center = (ideal_cx, ideal_cy)
            fixed.append(placement)
            continue

        best_penalty = float("inf")
        best = (ideal_cx, ideal_cy)

        def evaluate(t: float) -> Tuple[float, Tuple[float, float]]:
            cx = x1 + ux * t * dist
            cy = y1 + uy * t * dist
            pen = _obstacle_penalty(placement, cx, cy, coords, fixed)
            dx = cx - ideal_cx
            dy = cy - ideal_cy
            pen += PREFERENCE_WEIGHT * (dx * dx + dy * dy)
            return pen, (cx, cy)

        candidates_t = _candidate_t_values(placement)
        for t in candidates_t:
            pen, cand = evaluate(t)
            if pen < best_penalty:
                best_penalty = pen
                best = cand

        placement.center = best
        fixed.append(placement)


def _draw_symbol_placement(
    group: etree._Element,
    placement: SymbolPlacement,
) -> None:
    """Render a symbol placement using the existing drawing helpers."""
    cx, cy = placement.center
    angle = placement.angle
    color = placement.color
    stroke_width = placement.stroke_width
    symbol_radius = placement.symbol_radius
    edge5 = placement.edge5
    edge3 = placement.edge3
    cis = placement.cis

    if placement.style == "alt":
        _draw_lw_alternative(
            group, cx, cy, angle, edge5, edge3, cis, color, stroke_width, symbol_radius
        )
    elif placement.style == "pair":
        ux, uy = placement.ux, placement.uy
        offset = placement.pair_offset
        _draw_single_symbol(
            group,
            cx - ux * offset,
            cy - uy * offset,
            angle,
            edge5,
            symbol_radius,
            cis,
            color,
            stroke_width,
        )
        _draw_single_symbol(
            group,
            cx + ux * offset,
            cy + uy * offset,
            angle,
            edge3,
            symbol_radius,
            cis,
            color,
            stroke_width,
        )
    else:
        _draw_single_symbol(
            group, cx, cy, angle, edge5, symbol_radius, cis, color, stroke_width
        )


def class_tokens(element: etree._Element) -> set[str]:
    return set((element.get("class") or "").split())


def remove_rnaplot_base_pair_graphics(main_group: etree._Element) -> None:
    candidates = list(main_group.iterdescendants())
    for element in candidates:
        if "basepairs" not in class_tokens(element):
            continue
        parent = element.getparent()
        if parent is not None:
            parent.remove(element)


def remove_backbone(main_group: etree._Element) -> None:
    """Remove all backbone elements (polyline/path/line) from the SVG."""
    to_remove = []
    for element in main_group.iterdescendants():
        if "backbone" in class_tokens(element):
            to_remove.append(element)
    for element in to_remove:
        parent = element.getparent()
        if parent is not None:
            parent.remove(element)


def draw_backbone(
    main_group: etree._Element,
    seq_group: etree._Element,
    coords: List[Tuple[float, float]],
    strands: List[StrandInput],
    phantom_positions: Set[int],
    color: str = CANONICAL_BP_COLOR,
    stroke_width: str = "1.5",
) -> None:
    """Draw backbone line segments within each strand."""
    children = list(main_group)
    try:
        insert_idx = children.index(seq_group)
    except ValueError:
        insert_idx = len(children)

    backbone_group = etree.Element(f"{{{SVG_NS}}}g", attrib={"id": "backbone"})

    phantom_set = phantom_positions or set()
    cumulative = 0
    for strand_idx, strand in enumerate(strands):
        length = len(strand["sequence"])
        global_start = cumulative + strand_idx + 1
        for intra in range(1, length):
            pos_a = global_start + intra - 1
            pos_b = global_start + intra
            if pos_a in phantom_set or pos_b in phantom_set:
                continue
            idx_a = pos_a - 1
            idx_b = pos_b - 1
            if idx_a < 0 or idx_a >= len(coords):
                continue
            if idx_b < 0 or idx_b >= len(coords):
                continue
            x1, y1, x2, y2 = shorten_line(
                coords[idx_a][0],
                coords[idx_a][1],
                coords[idx_b][0],
                coords[idx_b][1],
            )
            etree.SubElement(
                backbone_group,
                f"{{{SVG_NS}}}line",
                attrib={
                    "x1": f"{x1:.3f}",
                    "y1": f"{y1:.3f}",
                    "x2": f"{x2:.3f}",
                    "y2": f"{y2:.3f}",
                    "stroke": color,
                    "stroke-width": stroke_width,
                    "fill": "none",
                },
            )
        cumulative += length

    if len(backbone_group) > 0:
        main_group.insert(insert_idx, backbone_group)


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
    symbol_radius = SYMBOL_RADIUS

    placements: List[SymbolPlacement] = []

    for interaction in interactions:
        idx_left = interaction.number_left - 1
        idx_right = interaction.number_right - 1

        if idx_left < 0 or idx_left >= len(coords):
            continue
        if idx_right < 0 or idx_right >= len(coords):
            continue

        x1_orig, y1_orig = coords[idx_left]
        x2_orig, y2_orig = coords[idx_right]
        x1, y1, x2, y2 = shorten_line(x1_orig, y1_orig, x2_orig, y2_orig)
        svg_color = color_to_svg(interaction.color)
        symbol_stroke_width = str(max(1.0, float(interaction.stroke_width)))
        line_stroke_width = interaction.stroke_width

        if interaction.is_canonical:
            svg_color = CANONICAL_BP_COLOR
            line_stroke_width = "1.5"

        line_attrib: Dict[str, str] = {
            "x1": f"{x1:.3f}",
            "y1": f"{y1:.3f}",
            "x2": f"{x2:.3f}",
            "y2": f"{y2:.3f}",
            "stroke": svg_color,
            "fill": "none",
            "stroke-width": line_stroke_width,
        }

        if interaction.dasharray:
            line_attrib["stroke-dasharray"] = interaction.dasharray
        if interaction.dashoffset:
            line_attrib["stroke-dashoffset"] = interaction.dashoffset

        etree.SubElement(interactions_group, f"{{{SVG_NS}}}line", attrib=line_attrib)

        edge5 = interaction.edge5
        edge3 = interaction.edge3
        if edge5 is None or edge3 is None or interaction.style == "simple":
            continue

        effective_radius = (
            max(
                _symbol_bounding_radius(edge5, symbol_radius),
                _symbol_bounding_radius(edge3, symbol_radius),
            )
            + SYMBOL_OVERLAP_MARGIN
        )

        dx = x2_orig - x1_orig
        dy = y2_orig - y1_orig
        dist = math.hypot(dx, dy)
        if dist == 0:
            continue
        ux = dx / dist
        uy = dy / dist
        cx = (x1_orig + x2_orig) / 2.0
        cy = (y1_orig + y2_orig) / 2.0
        angle = math.atan2(uy, ux)

        if interaction.style == "lw_alt":
            placements.append(
                SymbolPlacement(
                    style="alt",
                    ideal_center=(cx, cy),
                    center=(cx, cy),
                    radius=effective_radius,
                    nucleotide_i=idx_left,
                    nucleotide_j=idx_right,
                    preferred_t=0.5,
                    ux=ux,
                    uy=uy,
                    dist=dist,
                    angle=angle,
                    edge5=edge5,
                    edge3=edge3,
                    cis=interaction.cis,
                    color=svg_color,
                    stroke_width=symbol_stroke_width,
                    symbol_radius=symbol_radius,
                )
            )
        elif edge5 == edge3:
            placements.append(
                SymbolPlacement(
                    style="single",
                    ideal_center=(cx, cy),
                    center=(cx, cy),
                    radius=effective_radius,
                    nucleotide_i=idx_left,
                    nucleotide_j=idx_right,
                    preferred_t=0.5,
                    ux=ux,
                    uy=uy,
                    dist=dist,
                    angle=angle,
                    edge5=edge5,
                    edge3=edge3,
                    cis=interaction.cis,
                    color=svg_color,
                    stroke_width=symbol_stroke_width,
                    symbol_radius=symbol_radius,
                )
            )
        else:
            offset = min(symbol_radius * 1.6, max((dist / 2.0) - symbol_radius, 0.0))
            placements.append(
                SymbolPlacement(
                    style="pair",
                    ideal_center=(cx, cy),
                    center=(cx, cy),
                    radius=effective_radius,
                    nucleotide_i=idx_left,
                    nucleotide_j=idx_right,
                    preferred_t=0.5,
                    ux=ux,
                    uy=uy,
                    dist=dist,
                    angle=angle,
                    edge5=edge5,
                    edge3=edge3,
                    cis=interaction.cis,
                    color=svg_color,
                    stroke_width=symbol_stroke_width,
                    symbol_radius=symbol_radius,
                    pair_offset=offset,
                )
            )

    _optimize_symbol_placements(placements, coords)

    for placement in placements:
        _draw_symbol_placement(interactions_group, placement)

    main_group.insert(insert_idx, interactions_group)


def add_stacking_markers(
    main_group: etree._Element,
    seq_group: etree._Element,
    coords: List[Tuple[float, float]],
    stackings: List[PuzzlerStacking],
) -> None:
    if not stackings:
        return

    children = list(main_group)
    try:
        insert_idx = children.index(seq_group)
    except ValueError:
        insert_idx = len(children)

    stackings_group = etree.Element(f"{{{SVG_NS}}}g", attrib={"id": "stackings"})

    for stacking in stackings:
        idx_left = stacking.number_left - 1
        idx_right = stacking.number_right - 1

        if idx_left < 0 or idx_left >= len(coords):
            continue
        if idx_right < 0 or idx_right >= len(coords):
            continue

        x1, y1 = coords[idx_left]
        x2, y2 = coords[idx_right]
        dx = x2 - x1
        dy = y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            continue
        ux = dx / dist
        uy = dy / dist

        color = color_to_svg(stacking.color)
        stroke_width = stacking.stroke_width
        symbol_stroke_width = f"{max(1.0, float(stroke_width)):.3f}"

        line_x1, line_y1, line_x2, line_y2 = shorten_line(x1, y1, x2, y2)
        etree.SubElement(
            stackings_group,
            f"{{{SVG_NS}}}line",
            attrib={
                "x1": f"{line_x1:.3f}",
                "y1": f"{line_y1:.3f}",
                "x2": f"{line_x2:.3f}",
                "y2": f"{line_y2:.3f}",
                "stroke": color,
                "stroke-width": symbol_stroke_width,
            },
        )

        arrow_len = SYMBOL_RADIUS * 1.2
        available = math.hypot(line_x2 - line_x1, line_y2 - line_y1)
        if available < arrow_len:
            arrow_len = max(0.0, available)
        if arrow_len <= 0.0:
            continue

        gap = stacking.arrow_gap or 0.0
        half = available / 2.0
        centered_tip = (
            (line_x1 + line_x2) / 2.0
            + ux * max(-half + arrow_len, min(gap, half - arrow_len)),
            (line_y1 + line_y2) / 2.0
            + uy * max(-half + arrow_len, min(gap, half - arrow_len)),
        )
        first_tip = (
            line_x1 + ux * max(0.0, min(gap, available)),
            line_y1 + uy * max(0.0, min(gap, available)),
        )
        second_tip = (
            line_x2 - ux * max(0.0, min(gap, available)),
            line_y2 - uy * max(0.0, min(gap, available)),
        )

        placement = stacking.arrow_placement
        if placement == "centered":
            _draw_filled_arrowhead(
                stackings_group, centered_tip, ux, uy, arrow_len, color
            )
        elif placement == "first-partner":
            _draw_filled_arrowhead(stackings_group, first_tip, ux, uy, arrow_len, color)
        elif placement == "second-partner":
            _draw_filled_arrowhead(
                stackings_group, second_tip, ux, uy, arrow_len, color
            )
        elif placement == "both-partners":
            _draw_filled_arrowhead(stackings_group, first_tip, ux, uy, arrow_len, color)
            _draw_filled_arrowhead(
                stackings_group, second_tip, ux, uy, arrow_len, color
            )
        elif placement == "opposing-partners":
            _draw_filled_arrowhead(
                stackings_group, first_tip, -ux, -uy, arrow_len, color
            )
            _draw_filled_arrowhead(
                stackings_group, second_tip, ux, uy, arrow_len, color
            )

    main_group.insert(insert_idx, stackings_group)


def add_nucleotide_circles(
    main_group: etree._Element,
    seq_group: etree._Element,
    coords: List[Tuple[float, float]],
    missing_res_numbers: List[int],
    phantom_positions: Optional[Set[int]] = None,
) -> None:
    children = list(main_group)
    try:
        insert_idx = children.index(seq_group)
    except ValueError:
        insert_idx = len(children)

    missing_set = set(missing_res_numbers)
    phantom_set = phantom_positions or set()
    circles_group = etree.Element(f"{{{SVG_NS}}}g", attrib={"id": "nucleotide-circles"})

    for i, (x, y) in enumerate(coords):
        if (i + 1) in phantom_set:
            continue
        stroke = MISSING_CIRCLE_STROKE if (i + 1) in missing_set else CIRCLE_STROKE
        circle_attrib = {
            "cx": f"{x:.3f}",
            "cy": f"{y:.3f}",
            "r": f"{NUCLEOTIDE_RADIUS:.3f}",
            "fill": CIRCLE_FILL,
            "stroke": stroke,
            "stroke-width": CIRCLE_STROKE_WIDTH,
        }
        etree.SubElement(circles_group, f"{{{SVG_NS}}}circle", attrib=circle_attrib)

    main_group.insert(insert_idx, circles_group)


def remove_scripts(root: etree._Element) -> None:
    for script in root.findall(f".//{{{SVG_NS}}}script"):
        parent = script.getparent()
        if parent is not None:
            parent.remove(script)
    for script in root.findall(".//script"):
        parent = script.getparent()
        if parent is not None:
            parent.remove(script)


def remove_background_rectangles(root: etree._Element) -> None:
    for rect in list(root.findall(f".//{{{SVG_NS}}}rect")):
        parent = rect.getparent()
        if parent is not None:
            parent.remove(rect)
    for rect in list(root.findall(".//rect")):
        parent = rect.getparent()
        if parent is not None:
            parent.remove(rect)


def postprocess_svg(
    svg_content: str,
    strands: List[StrandInput],
    interactions: List[PuzzlerInteraction],
    stackings: List[PuzzlerStacking],
    missing_res_numbers: List[int],
    phantom_positions: Set[int],
    nucleotide_colors: Optional[Dict[str, str]] = None,
    num_period: int = DEFAULT_NUM_PERIOD,
    labels: Optional[Dict[str, str]] = None,
    draw_backbone_flag: bool = False,
) -> str:
    root = etree.fromstring(svg_content.encode("utf-8"))

    update_css_styles(root)

    main_group = find_main_group(root)
    if main_group is None:
        return etree.tostring(root, encoding="UTF-8", xml_declaration=True).decode(
            "UTF-8"
        )

    coords = extract_nucleotide_coords(root)

    seq_group = find_seq_group(main_group)

    if seq_group is not None:
        center_nucleotide_labels(
            seq_group, nucleotide_colors, missing_res_numbers, phantom_positions
        )

    remove_rnaplot_base_pair_graphics(main_group)
    remove_backbone(main_group)

    if seq_group is not None and coords:
        if draw_backbone_flag:
            draw_backbone(main_group, seq_group, coords, strands, phantom_positions)
        add_interaction_lines(main_group, seq_group, coords, interactions)
        add_nucleotide_circles(
            main_group, seq_group, coords, missing_res_numbers, phantom_positions
        )
        add_stacking_markers(main_group, seq_group, coords, stackings)
        _add_nucleotide_numbers(
            main_group,
            seq_group,
            coords,
            strands,
            num_period,
            labels,
            phantom_positions,
        )

    remove_scripts(root)
    remove_background_rectangles(root)

    return etree.tostring(root, encoding="UTF-8", xml_declaration=True).decode("UTF-8")


def _outward_directions(
    coords: List[Tuple[float, float]],
) -> List[Tuple[float, float]]:
    """Compute an outward-pointing unit vector for each nucleotide.

    The backbone bisector is computed for each residue and rotated 90°
    counter-clockwise.  Among the two perpendicular candidates the one
    that places the number tick farthest from all *other* nucleotide
    centres is chosen.
    """
    n = len(coords)
    if n == 0:
        return []
    if n == 1:
        return [(1.0, 0.0)]

    # Precompute bisectors.
    bisectors: List[Tuple[float, float]] = []
    for i in range(n):
        prev = coords[i - 1] if i > 0 else coords[i]
        nxt = coords[i + 1] if i < n - 1 else coords[i]
        dx1 = coords[i][0] - prev[0]
        dy1 = coords[i][1] - prev[1]
        dx2 = nxt[0] - coords[i][0]
        dy2 = nxt[1] - coords[i][1]
        len1 = math.hypot(dx1, dy1)
        len2 = math.hypot(dx2, dy2)
        ux1 = dx1 / len1 if len1 > 0 else 0.0
        uy1 = dy1 / len1 if len1 > 0 else 0.0
        ux2 = dx2 / len2 if len2 > 0 else 0.0
        uy2 = dy2 / len2 if len2 > 0 else 0.0
        bx = ux1 + ux2
        by = uy1 + uy2
        blen = math.hypot(bx, by)
        if blen > 0:
            bx /= blen
            by /= blen
        else:
            bx, by = 1.0, 0.0
        bisectors.append((bx, by))

    result: List[Tuple[float, float]] = []
    for i in range(n):
        bx, by = bisectors[i]
        # Two perpendicular candidates.
        cand_a = (-by, bx)
        cand_b = (by, -bx)

        best_dir = cand_a
        best_dist = -1.0
        for nx, ny in (cand_a, cand_b):
            tip_x = coords[i][0] + nx * (NUCLEOTIDE_RADIUS + NUMBER_TICK_LENGTH)
            tip_y = coords[i][1] + ny * (NUCLEOTIDE_RADIUS + NUMBER_TICK_LENGTH)
            min_d = float("inf")
            for j, (ox, oy) in enumerate(coords):
                if j == i:
                    continue
                d = math.hypot(tip_x - ox, tip_y - oy)
                if d < min_d:
                    min_d = d
            if min_d > best_dist:
                best_dist = min_d
                best_dir = (nx, ny)

        result.append(best_dir)
    return result


def _number_positions(
    strands: List[StrandInput],
    num_period: int,
    labels: Optional[Dict[str, str]] = None,
) -> List[Tuple[int, str]]:
    """Return (global-position-1-based, label-text) for numbered residues.

    Numbering restarts at 1 for each strand.  The first and last residue of
    every strand are always numbered, together with every *num_period*-th
    residue counted from the start of the strand.  Custom labels from the
    ``num_labels`` input dictionary override auto-generated labels.
    """
    result: List[Tuple[int, str]] = []
    if num_period <= 0:
        return result

    labels_by_global = labels or {}
    seen_global: set[int] = set()
    cumulative = 0

    for strand in strands:
        length = len(strand["sequence"])
        for intra_pos in range(1, length + 1):
            global_pos = cumulative + intra_pos
            label = None

            # Custom label takes priority.
            custom = labels_by_global.get(str(global_pos))
            if custom is not None:
                label = custom
            elif intra_pos == 1:
                label = str(intra_pos)
            elif intra_pos == length:
                label = str(intra_pos)
            elif intra_pos % num_period == 0:
                label = str(intra_pos)

            if label is not None and global_pos not in seen_global:
                result.append((global_pos, label))
                seen_global.add(global_pos)

        cumulative += length

    return sorted(result)


def _add_nucleotide_numbers(
    main_group: etree._Element,
    seq_group: etree._Element,
    coords: List[Tuple[float, float]],
    strands: List[StrandInput],
    num_period: int,
    labels: Optional[Dict[str, str]] = None,
    phantom_positions: Optional[Set[int]] = None,
) -> None:
    """Draw tick lines and number labels at selected nucleotide positions."""
    numbers = _number_positions(strands, num_period, labels)
    phantom_set = phantom_positions or set()
    # Shift positions for inserted phantom residues and filter them out.
    shifted = []
    for p, lbl in numbers:
        shift_amount = sum(1 for q in phantom_set if q <= p)
        pp = p + shift_amount
        if pp not in phantom_set:
            shifted.append((pp, lbl))
    numbers = shifted
    if not numbers:
        return

    outward = _outward_directions(coords)

    children = list(main_group)
    try:
        insert_idx = children.index(seq_group)
    except ValueError:
        insert_idx = len(children)

    numbers_group = etree.Element(f"{{{SVG_NS}}}g", attrib={"id": "nucleotide-numbers"})

    for global_pos, label_text in numbers:
        idx = global_pos - 1
        if idx < 0 or idx >= len(coords):
            continue
        cx, cy = coords[idx]
        nx, ny = outward[idx]
        tick_start_x = cx + nx * NUCLEOTIDE_RADIUS
        tick_start_y = cy + ny * NUCLEOTIDE_RADIUS
        tick_end_x = cx + nx * (NUCLEOTIDE_RADIUS + NUMBER_TICK_LENGTH)
        tick_end_y = cy + ny * (NUCLEOTIDE_RADIUS + NUMBER_TICK_LENGTH)
        etree.SubElement(
            numbers_group,
            f"{{{SVG_NS}}}line",
            attrib={
                "x1": f"{tick_start_x:.3f}",
                "y1": f"{tick_start_y:.3f}",
                "x2": f"{tick_end_x:.3f}",
                "y2": f"{tick_end_y:.3f}",
                "stroke": NUMBER_COLOR,
                "stroke-width": "1",
            },
        )
        label_x = cx + nx * (NUCLEOTIDE_RADIUS + NUMBER_TICK_LENGTH + NUMBER_GAP)
        label_y = cy + ny * (NUCLEOTIDE_RADIUS + NUMBER_TICK_LENGTH + NUMBER_GAP)
        etree.SubElement(
            numbers_group,
            f"{{{SVG_NS}}}text",
            attrib={
                "x": f"{label_x:.3f}",
                "y": f"{label_y:.3f}",
                "fill": NUMBER_COLOR,
                "font-size": NUMBER_FONT_SIZE,
                "font-weight": NUMBER_FONT_WEIGHT,
                "font-family": "sans-serif",
                "text-anchor": "middle",
                "dominant-baseline": "central",
            },
        )
        numbers_group[-1].text = label_text

    main_group.insert(insert_idx, numbers_group)


def ensure_svg_viewbox(svg_content: str) -> str:
    """Add viewBox and preserveAspectRatio to the SVG root if missing."""
    root = etree.fromstring(svg_content.encode("utf-8"))
    width = root.get("width")
    height = root.get("height")

    if width and height:
        # Strip optional units such as px or pt.
        w_str = width.replace("px", "").replace("pt", "").strip()
        h_str = height.replace("px", "").replace("pt", "").strip()
        try:
            w = float(w_str)
            h = float(h_str)
            if not root.get("viewBox"):
                root.set("viewBox", f"0 0 {w} {h}")
            root.set("preserveAspectRatio", "xMidYMid meet")
        except ValueError:
            pass

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
        (
            sequence,
            structure,
            interactions,
            stackings,
            missing_res_numbers,
            phantom_positions,
        ) = preprocess(data)
        svg_content = generate_rnapuzzler_svg(sequence, structure)
        nucleotide_colors = data.get("nucleotide_colors")
        num_period = data.get("num_period", DEFAULT_NUM_PERIOD)
        labels = data.get("num_labels")
        postprocessed = postprocess_svg(
            svg_content,
            data["strands"],
            interactions,
            stackings,
            missing_res_numbers,
            phantom_positions,
            nucleotide_colors,
            num_period=num_period,
            labels=labels,
            draw_backbone_flag=data.get("draw_backbone", False),
        )

        with open("raw.svg", "w", encoding="utf-8") as f:
            f.write(postprocessed)

        if data.get("debug", False):
            with open("clean.svg", "w", encoding="utf-8") as f:
                f.write(ensure_svg_viewbox(postprocessed))
        else:
            inkscape_cmd = [
                "inkscape",
                "raw.svg",
                "--export-area-drawing",
                "--export-filename=output.svg",
            ]
            subprocess.run(inkscape_cmd, capture_output=True, text=True, check=True)

            svgcleaner_cmd = ["svgcleaner", "output.svg", "clean.svg"]
            subprocess.run(svgcleaner_cmd, capture_output=True, text=True, check=True)

    except Exception as e:
        print(f"Processing failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
