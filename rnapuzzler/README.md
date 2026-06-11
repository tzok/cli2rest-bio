# RNApuzzler via CLI2REST

This directory contains the configuration and wrapper script to run RNApuzzler (from the ViennaRNA package) within the CLI2REST framework.

## Tool Description

RNApuzzler is a layout algorithm for RNA secondary structure visualization, available as part of the [ViennaRNA](https://www.tbi.univie.ac.at/RNA/) package. It produces publication-quality SVG diagrams of RNA structures using a puzzle-piece layout.

The wrapper accepts a JSON input describing RNA strands with extended dot-bracket notation and optional non-canonical interactions, generates an SVG with the `RNAplot` CLI using the RNApuzzler layout, and post-processes it (colored interaction lines, missing residue markers, strand boundary gaps, CSS cleanup). The final SVG is optimized with `svgcleaner`.

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
  "strands": [
    {
      "name": "A",
      "sequence": "GCGGAUUUALCUCAGUUGG",
      "structure": "(((....)))...(((...)))"
    }
  ],
  "interactions": [
    {"i": 1, "j": 10, "lw": "cWW", "color": "#FF0000"},
    {"i": 3, "j": 15, "lw": "tWH"}
  ]
}
```

### Fields

- **`strands`** (list, required): One or more RNA strands.
  - `name` (string): Strand identifier.
  - `sequence` (string): Nucleotide sequence (A, C, G, U, or any IUPAC character).
  - `structure` (string): Extended dot-bracket notation. Supported symbols:
    - `.` — unpaired
    - `()` — canonical base pair (drawn by RNApuzzler)
    - `[]`, `{}`, `<>`, `Aa`, `Bb`, `Cc`, `Dd`, `Ee` — non-canonical pairs (drawn as colored lines)
    - `-` — missing residue (drawn as a red circle marker)
- **`interactions`** (list, optional): Additional non-canonical interactions.
  - `i` (integer, 1-based): Left residue position.
  - `j` (integer, 1-based): Right residue position.
  - `lw` (string, optional): Leontis-Westhof classification (e.g., `cWW`, `tWH`). Reserved for future use.
  - `color` (string, optional): Color for the interaction line. Reserved for future use.

## Building the Container

```bash
docker build -t ghcr.io/tzok/cli2rest-rnapuzzler .
```

## References

- [ViennaRNA Package](https://www.tbi.univie.ac.at/RNA/)
- [RNApuzzler algorithm](https://doi.org/10.1093/nar/gkx1195)
