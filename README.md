# CLI2REST Docker Containers

This repository contains Docker containers for various bioinformatics tools wrapped with the CLI2REST API. CLI2REST provides a simple HTTP interface to command-line tools, making them accessible via REST API calls.

## Available Tools

Currently, the following tools are available:

- [Reduce](./reduce/): A tool for adding hydrogens to RNA structures in PDB format
- [MaxiT](./maxit/): A tool for RNA structure format conversion and validation
- [FR3D](./fr3d/): A tool for RNA structure annotation and classification
- [RNAPOLIS](./rnapolis/): A tool for RNA structure annotation
- [RNAView](./rnaview/): A tool for RNA secondary structure annotation

## How It Works

Each tool is containerized with Docker and exposed through a REST API that follows the same pattern:

1. You send a JSON request with:
   - The command-line tool to run
   - Arguments to pass to the tool
   - Input files encoded as strings

2. The API returns a JSON response with:
   - Standard output
   - Standard error
   - Any generated output files

## Installation

You can install the CLI2REST Bio tool directly from this repository:

```bash
# Install from the repository
pip install .

# Or install in development mode
pip install -e .
```

## Using the CLI2REST Command Line Tool

After installation, you can use the `cli2rest-bio` command to interact with the containerized tools:

```bash
# Basic usage
cli2rest-bio <config_file> <input_file1> [<input_file2> ...]

# Example with Reduce
cli2rest-bio reduce/config.yaml sample.pdb

# Example with MaxiT for PDB to CIF conversion
cli2rest-bio maxit/config-pdb2cif.yaml sample.pdb

# Process multiple files
cli2rest-bio fr3d/config.yaml sample1.cif sample2.cif sample3.cif

# Control parallelism
cli2rest-bio --threads 4 rnaview/config-pdb.yaml *.pdb
```

The script will:
1. Start the appropriate Docker container
2. Process each input file according to the configuration
3. Save output files with the tool name as a prefix
4. Clean up the container when done

## Configuration Files

Each tool requires a YAML configuration file that specifies:

- `name`: The tool name (used for output file prefixes)
- `docker_image`: The Docker image to use
- `cli_tool`: The command-line tool to run inside the container
- `arguments`: Command-line arguments to pass to the tool
- `input_file`: The relative path where the input file should be placed
- `output_files`: List of output files to retrieve from the container

Example configuration (reduce/config.yaml):
```yaml
name: "reduce"
docker_image: "ghcr.io/tzok/cli2rest-reduce:latest"
cli_tool: "reduce"
arguments:
  - "input.pdb"
input_file: "input.pdb"
```

Example configuration with output files (fr3d/config.yaml):
```yaml
name: "fr3d"
docker_image: "ghcr.io/tzok/cli2rest-fr3d:latest"
cli_tool: "wrapper.py"
arguments:
  - "input.cif"
input_file: "input.cif"
output_files:
  - "basepair_detail.txt"
  - "stacking.txt"
  - "backbone.txt"
```

## Creating Configuration Files for New Tools

To add support for a new tool:

1. Create a new directory for your tool
2. Create a Dockerfile that installs the tool and the CLI2REST wrapper
3. Create a YAML configuration file with the following structure:

```yaml
name: "your-tool-name"
docker_image: "ghcr.io/your-username/cli2rest-your-tool:latest"
cli_tool: "your-tool-command"
arguments:
  - "arg1"
  - "arg2"
  - "input.ext"
input_file: "input.ext"
output_files:
  - "output1.ext"
  - "output2.ext"
```

Guidelines for configuration files:
- `name`: Should be short and descriptive, used as a prefix for output files
- `docker_image`: Must point to a valid Docker image with the CLI2REST wrapper
- `cli_tool`: The exact command to run inside the container
- `arguments`: List of arguments in the order they should be passed to the tool
- `input_file`: The path where your input file will be placed inside the container
- `output_files`: List of files that should be retrieved from the container after processing (optional)

## Pre-built Container Images

Pre-built container images are available on GitHub Container Registry:

```bash
# Pull the Reduce container
docker pull ghcr.io/tzok/cli2rest-reduce:latest

# Pull the MaxiT container
docker pull ghcr.io/tzok/cli2rest-maxit:latest

# Pull the FR3D container
docker pull ghcr.io/tzok/cli2rest-fr3d:latest

# Pull the RNAPOLIS container
docker pull ghcr.io/tzok/cli2rest-rnapolis:latest

# Pull the RNAView container
docker pull ghcr.io/tzok/cli2rest-rnaview:latest
```

## Requirements

- Python 3.7+
- Docker
- Python packages: docker, requests, pyyaml (automatically installed when using pip)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The original tool developers for their valuable contributions to bioinformatics
- The CLI2REST framework for simplifying API access to command-line tools
