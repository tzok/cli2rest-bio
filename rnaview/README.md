# RNAView Docker Container

This repository contains a Dockerfile for building a container with the [RNAView](https://github.com/rcsb/RNAView) tool wrapped in the CLI2REST API.

## What is RNAView?

RNAView is a program developed by the RCSB PDB for analyzing and visualizing RNA secondary structures. It identifies base pairs and generates secondary structure diagrams from 3D coordinates.

## Building the Container

To build the container, run:

```bash
docker build -t cli2rest-rnaview .
```

## Running the Container

To start the container and expose the CLI2REST API on port 8000:

```bash
docker run -p 8000:8000 cli2rest-rnaview
```

## Usage

### Using the `cli2rest-bio` Tool

The recommended way to use this container is with the `cli2rest-bio` command-line tool provided in the main repository:

```bash
# Analyze a PDB file using config-pdb.yaml
cli2rest-bio rnaview/config-pdb.yaml your_rna.pdb

# Analyze a CIF file using config-cif.yaml
cli2rest-bio rnaview/config-cif.yaml your_rna.cif

# Process multiple files
cli2rest-bio rnaview/config-pdb.yaml *.pdb
```

This tool handles starting the container, sending requests according to the specified config, saving outputs (prefixed with `rnaview-`), and cleaning up. See the main [README.md](../README.md) for more details on `cli2rest-bio`.

### Using the REST API Directly

You can also interact with the API directly using form data:

#### Example: Analyzing a PDB file (corresponds to `config-pdb.yaml`)

```bash
curl -X POST http://localhost:8000/run-command \
  -F 'arguments=rnaview' \
  -F 'arguments=input.pdb' \
  -F 'output_files=input.pdb.out' \
  -F 'input_files=@path/to/your_local_rna.pdb;filename=input.pdb'
```

#### Example: Analyzing a CIF file (corresponds to `config-cif.yaml`)

```bash
curl -X POST http://localhost:8000/run-command \
  -F 'arguments=rnaview' \
  -F 'arguments=--cif' \
  -F 'arguments=input.cif' \
  -F 'output_files=input.cif.out' \
  -F 'input_files=@path/to/your_local_rna.cif;filename=input.cif'
```

### Response

The API will return a JSON response containing the standard output, standard error, exit code, and the requested output file (`.out`) encoded in base64.

Example response for the PDB analysis:

```json
{
  "exit_code": 0,
  "stdout": "...",
  "stderr": "...",
  "output_files": [
    {
      "relative_path": "input.pdb.out",
      "content_base64": "QmVnaW..."
    }
  ]
}

## RNAView Options

RNAView supports various command-line options:

- Basic usage for PDB files: `rnaview --pdb pdbfile_name`
- Basic usage for CIF files: `rnaview --cif ciffile_name`
- `-p`: Generate fully annotated 2D structure in postscript format with detailed information in XML format (RNAML)
- `-v`: Generate a 3D structure in VRML format for display on internet (with VRML plug-in)
- `-c`: Select specific chains for calculation (e.g., `rnaview -pc --pdb ABC pdbfile_name`)
- `-a`: Process multiple PDB files listed in a file (e.g., `rnaview -a file.list 3.0`)
- `-x`: Input XML (RNAML) file, often combined with -p to generate a 2D structure
- `--label`: Process CIF files using label instead of auth (default) (e.g., `rnaview -p --cif --label ciffile_name`)

For further information, contact: ndbadmin@ndbserver.rutgers.edu
