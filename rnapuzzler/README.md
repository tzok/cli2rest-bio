# RNApuzzler via CLI2REST

This directory contains the configuration and wrapper script to run RNApuzzler (from the ViennaRNA package) within the CLI2REST framework.

## Tool Description

RNApuzzler is a layout algorithm for RNA secondary structure visualization, available as part of the [ViennaRNA](https://www.tbi.univie.ac.at/RNA/) package. It produces publication-quality SVG diagrams of RNA structures using a puzzle-piece layout.

The wrapper accepts a JSON input describing RNA strands with extended dot-bracket notation and optional non-canonical interactions/stackings, generates an SVG with the `RNAplot` CLI using the RNApuzzler layout, and post-processes it (colored interaction lines, Leontis–Westhof edge symbols, stacking arrowheads, missing residue markers, strand boundary gaps, CSS cleanup). The final SVG is optimized with `svgcleaner`.

The container installs ViennaRNA from the official prebuilt Debian packages published by the ViennaRNA project.

## Configuration (`config.yaml`)

```yaml
name: "rnapuzzler"
docker_image: "ghcr.io/tzok/cli2rest-rnapuzzler:latest"
arguments:
  - "wrapper.py"
  - "input.json"
input_file: "input.json"
output_files:
  - "clean.svg"
```

## Usage with `cli2rest-bio`

```bash
cli2rest-bio rnapuzzler/config.yaml your_input.json
```

This command will:
1. Start the `ghcr.io/tzok/cli2rest-rnapuzzler:latest` Docker container.
2. Send `your_input.json` to the container as `input.json`.
3. Execute `wrapper.py input.json` inside the container.
4. Retrieve the resulting `clean.svg` file and save it locally with a prefix.
5. Stop the Docker container.

## Input JSON Format

```json
{
  "bp_style": "lw",
  "stacking_arrow_placement": "centered",
  "strands": [
    {
      "name": "A",
      "sequence": "GCGGAUUUALCUCAGUUGG",
      "structure": "(((....)))...(((...)))"
    }
  ],
  "interactions": [
    {"i": 1, "j": 10, "lw": "cWW", "color": "#FF0000"},
    {"i": 3, "j": 15, "lw": "tWH"},
    {"i": 5, "j": 12, "lw": "tWS", "style": "lw_alt"}
  ],
  "stackings": [
    {"i": 2, "j": 3, "color": "blue"},
    {"i": 7, "j": 8}
  ]
}
```

### Fields

- **`bp_style`** (string, optional): Default style for `lw`-annotated interactions.
  - `"lw"` (default) — line + Leontis–Westhof symbol(s) next to each other.
  - `"lw_alt"` — joined/nested symbols (e.g. square inside a circle).
  - `"simple"` — plain colored line, no symbols.
- **`strands`** (list, required): One or more RNA strands.
  - `name` (string): Strand identifier.
  - `sequence` (string): Nucleotide sequence (A, C, G, U, or any IUPAC character).
  - `structure` (string): Extended dot-bracket notation. Supported symbols:
    - `.` — unpaired
    - `()` — canonical base pair (drawn by RNApuzzler)
    - `[]`, `{}`, `<>`, `Aa`, `Bb`, `Cc`, `Dd`, `Ee` — non-canonical pairs (drawn as colored lines; no LW symbols because edges are not encoded)
    - `-` — missing residue (drawn as a red circle marker)
- **`interactions`** (list, optional): Additional non-canonical interactions.
  - `i` (integer, 1-based): 5′ residue position.
  - `j` (integer, 1-based): 3′ residue position.
  - `lw` (string, optional): Leontis–Westhof classification (e.g., `cWW`, `tWH`, `cWS`). When provided, the appropriate edge symbols are drawn.
  - `color` (string, optional): Color for the interaction line and symbols. Falls back to blue if omitted.
  - `style` (string, optional): Override `bp_style` for this interaction (`"lw"`, `"lw_alt"` or `"simple"`).
- **`stackings`** (list, optional): Base-base stackings drawn as a line with VARNA-style arrowhead chevrons.
  - `i` (integer, 1-based): 5′ residue position.
  - `j` (integer, 1-based): 3′ residue position.
  - `color` (string, optional): Chevron color.
  - `thickness` (number, optional): Stroke width.
- **`stacking_arrow_placement`** (string, optional): Position of stacking chevrons.
  - `"centered"` (default), `"first-partner"`, `"second-partner"`, `"both-partners"`, `"opposing-partners"`.
- **`stacking_arrow_gap`** (number, optional): Distance from the center or partner for chevron placement.

### Leontis–Westhof symbols

The first character of `lw` is the stericity (`c` = cis, `t` = trans); the second and third characters are the 5′ and 3′ edges.

| Edge | Symbol | Fill |
|------|--------|------|
| `W` (Watson–Crick) | circle | cis = filled, trans = white + outline |
| `H` (Hoogsteen) | square aligned with the bond | cis = filled, trans = white + outline |
| `S` (Sugar) | triangle with apex along the bond | cis = filled, trans = white + outline |

For matching edges a single symbol is drawn at the bond midpoint; for mixed edges `"lw"` draws the two symbols on the bond close to the midpoint, while `"lw_alt"` draws the 3′ symbol nested inside the 5′ symbol.

## Building the Container

```bash
docker build -t ghcr.io/tzok/cli2rest-rnapuzzler .
```

## References

- [ViennaRNA Package](https://www.tbi.univie.ac.at/RNA/)
- [RNApuzzler algorithm](https://doi.org/10.1093/nar/gkx1195)
