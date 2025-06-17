# MC-Annotate Docker Container

This repository contains a Dockerfile for building a container with the [MC-Annotate](https://major.iric.ca/MajorLabEn/MC-Tools.htm) tool wrapped in the CLI2REST API.

## What is MC-Annotate?

MC-Annotate is a program for annotating RNA and DNA structures. It analyzes 3D structures and provides detailed annotations about base pairs, stacking interactions, and other structural features.

## Building the Container

To build the container, run:

```bash
docker build -t cli2rest-mc-annotate .
```

## Running the Container

To start the container and expose the CLI2REST API on port 8000:

```bash
docker run -p 8000:8000 cli2rest-mc-annotate
```

## Usage

### Using the `cli2rest-bio` Tool

The recommended way to use this container is with the `cli2rest-bio` command-line tool provided in the main repository:

```bash
# Annotate a PDB file using config.yaml
cli2rest-bio mc-annotate/config.yaml your_structure.pdb

# Process multiple files
cli2rest-bio mc-annotate/config.yaml *.pdb
```

This tool handles starting the container, sending requests according to the specified config, and cleaning up. The annotation results will be captured from stdout/stderr. See the main [README.md](../README.md) for more details on `cli2rest-bio`.

### Using the REST API Directly

You can also interact with the API directly using form data:

#### Example: Annotating a PDB file (corresponds to `config.yaml`)

```bash
curl -X POST http://localhost:8000/run-command \
  -F 'arguments=MC-Annotate' \
  -F 'arguments=input.pdb' \
  -F 'input_files=@path/to/your_structure.pdb;filename=input.pdb'
```

### Response

The API will return a JSON response containing the standard output, standard error, and exit code. The annotation results will be in the stdout field.

Example response:

```json
{
  "exit_code": 0,
  "stdout": "# MC-Annotate annotation results...",
  "stderr": "",
  "output_files": []
}
```

## Common MC-Annotate Options

MC-Annotate supports various command-line options:

- `-b`: Read binary files instead of PDB files
- `-e num`: Number of surrounding layers of connected residues to annotate
- `-f model_number`: Model to print
- `-h`: Print help
- `-l`: Be more verbose (log)
- `-r sel`: Extract these residues from the structure
- `-v`: Be verbose
- `-V`: Print software version info

For a complete list of options, run `MC-Annotate -h` or see the [MC-Annotate documentation](https://major.iric.ca/MajorLabEn/MC-Tools.htm).
