# DSSR Docker Container

This repository contains a Dockerfile for building a container with the [DSSR](http://x3dna.org/) tool wrapped in the CLI2REST API.

## What is DSSR?

DSSR (Dissecting the Spatial Structure of RNA) is a component of the 3DNA software suite for analyzing nucleic acid structures. It identifies and annotates various structural features in DNA and RNA structures, including base pairs, multiplets, helices, stems, hairpin loops, bulges, and junctions.

**Important Licensing Notice:** DSSR is licensed by Columbia Technology Ventures and is not freely available. You must:
1. Request a license from Columbia Technology Ventures
2. Download the `x3dna-dssr` binary according to their licensing terms
3. Place the binary in the `dssr/` directory before building the container

Without the licensed binary, this container cannot be built or used.

## Building the Container

To build the container, run:

```bash
docker build -t cli2rest-dssr .
```

## Running the Container

To start the container and expose the CLI2REST API on port 8000:

```bash
docker run -p 8000:8000 cli2rest-dssr
```

## Usage

### Using the `cli2rest-bio` Tool

The recommended way to use this container is with the `cli2rest-bio` command-line tool provided in the main repository:

```bash
# Analyze a CIF file using config.yaml
cli2rest-bio dssr/config.yaml your_structure.cif

# Process multiple files
cli2rest-bio dssr/config.yaml *.cif
```

This tool handles starting the container, sending requests according to the specified config, saving outputs (prefixed with `dssr-`), and cleaning up. See the main [README.md](../README.md) for more details on `cli2rest-bio`.

### Using the REST API Directly

You can also interact with the API directly using form data:

#### Example: Analyzing a CIF file

```bash
curl -X POST http://localhost:8000/run-command \
  -F 'arguments=x3dna-dssr' \
  -F 'arguments=-i=input.cif' \
  -F 'arguments=-o=output.json' \
  -F 'arguments=--json' \
  -F 'arguments=-auxfile=no' \
  -F 'output_files=output.json' \
  -F 'input_files=@path/to/your_local_structure.cif;filename=input.cif'
```

### Response

The API will return a JSON response containing the standard output, standard error, exit code, and the requested output file (`output.json`) encoded in base64.

Example response:

```json
{
  "exit_code": 0,
  "stdout": "...",
  "stderr": "...",
  "output_files": [
    {
      "relative_path": "output.json",
      "content_base64": "eyJzdHJ1Y3R1cmUi..."
    }
  ]
}
```

## DSSR Options

DSSR supports various command-line options:

- `-i=input_file`: Input structure file (PDB, mmCIF, etc.)
- `-o=output_file`: Output file name
- `--json`: Output results in JSON format
- `--more`: More detailed output
- `-auxfile=no`: Do not generate auxiliary files
- `--non-pair`: Also detect non-Watson-Crick base pairs
- `--torsion`: Calculate backbone and chi torsion angles
- `--get-hbond`: Get hydrogen bonding information

For more information about DSSR and its options, visit: http://x3dna.org/

## Requirements

- **License Required:** You must obtain a license for DSSR from Columbia Technology Ventures
- The `x3dna-dssr` binary must be manually downloaded and placed in the `dssr/` directory before building the container
- The binary should be compatible with the Linux environment used in the base image
- Contact Columbia Technology Ventures for licensing information and to obtain the binary

**Note:** This container cannot be built without the licensed `x3dna-dssr` binary.
