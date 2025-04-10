# MAXIT Docker Container

This repository contains a Dockerfile for building a container with the [MAXIT](https://sw-tools.rcsb.org/apps/MAXIT/) tool wrapped in the CLI2REST API.

## What is MAXIT?

MAXIT is a program developed by the RCSB PDB for manipulating and validating PDB and mmCIF files. It can convert between PDB and mmCIF formats, extract information from structure files, and perform various validation checks.

## Building the Container

To build the container, run:

```bash
docker build -t cli2rest-maxit .
```

## Running the Container

To start the container and expose the CLI2REST API on port 8000:

```bash
docker run -p 8000:8000 cli2rest-maxit
```

## Usage

### Using the `cli2rest-bio` Tool

The recommended way to use this container is with the `cli2rest-bio` command-line tool provided in the main repository:

```bash
# Convert a PDB file to CIF using config-pdb2cif.yaml
cli2rest-bio maxit/config-pdb2cif.yaml your_rna.pdb

# Convert a CIF file to PDB using config-cif2pdb.yaml
cli2rest-bio maxit/config-cif2pdb.yaml your_rna.cif

# Convert a CIF file to mmCIF using config-cif2mmcif.yaml
cli2rest-bio maxit/config-cif2mmcif.yaml your_rna.cif

# Process multiple files
cli2rest-bio maxit/config-pdb2cif.yaml *.pdb
```

This tool handles starting the container, sending requests according to the specified config, saving outputs (prefixed with `maxit-`), and cleaning up. See the main [README.md](../README.md) for more details on `cli2rest-bio`.

### Using the REST API Directly

You can also interact with the API directly using form data:

#### Example: Converting PDB to CIF (corresponds to `config-pdb2cif.yaml`)

```bash
curl -X POST http://localhost:8000/run-command \
  -F 'arguments=maxit' \
  -F 'arguments=-input' \
  -F 'arguments=input.pdb' \
  -F 'arguments=-output' \
  -F 'arguments=output.cif' \
  -F 'arguments=-o' \
  -F 'arguments=1' \
  -F 'output_files=output.cif' \
  -F 'input_files=@path/to/your_local_rna.pdb;filename=input.pdb'
```

### Response

The API will return a JSON response containing the standard output, standard error, exit code, and any requested output files encoded in base64.

Example response for the PDB to CIF conversion above:

```json
{
  "exit_code": 0,
  "stdout": "",
  "stderr": "...",
  "output_files": [
    {
      "relative_path": "output.cif",
      "content_base64": "ZGF0YV..."
    }
  ]
}

## Common MAXIT Options

MAXIT supports various command-line options:

- `-input <file>`: Input file name
- `-output <file>`: Output file name
- `-o 1`: Convert PDB to CIF
- `-o 2`: Convert CIF to PDB
- `-o 8`: Convert CIF to mmCIF
- `-report`: Generate validation report
- `-dict <file>`: Use specified dictionary

For a complete list of options, see the [MAXIT documentation](https://sw-tools.rcsb.org/apps/MAXIT/).
