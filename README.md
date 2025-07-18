# CLI2REST Docker Containers

This repository contains Docker containers for various bioinformatics tools wrapped with the CLI2REST API. CLI2REST provides a simple HTTP interface to command-line tools, making them accessible via REST API calls.

## Available Tools

Currently, the following tools are available:

- [Reduce](./reduce/): A tool for adding hydrogens to RNA structures in PDB format
- [MaxiT](./maxit/): A tool for RNA structure format conversion and validation
- [FR3D](./fr3d/): A tool for RNA structure annotation and classification
- [RNAPOLIS](./rnapolis/): A tool for RNA structure annotation
- [RNAView](./rnaview/): A tool for RNA secondary structure annotation
- [R-Chie](./rchie/): A tool for RNA 2D structure visualization using R4RNA, producing arc diagrams.
- [VARNA-TZ](./varna-tz/): A custom tool for RNA 2D structure visualization
- [BPNet](./bpnet/): A tool for computing base pair networks in DNA/RNA structures
- [MC-Annotate](./mc-annotate/): A tool for RNA and DNA structure annotation
- [Barnaba](./barnaba/): A tool for analyzing RNA three-dimensional structures and simulations
- [DSSR](./dssr/): A tool for analyzing nucleic acid structures and identifying structural features

## How It Works

Each tool is containerized with Docker and exposed through a REST API that follows the same pattern:

1. You send a `multipart/form-data` request with:
   - `arguments`: A list of strings representing the command and its arguments.
   - `output_files`: A list of relative paths for files expected as output.
   - `input_files`: One or more uploaded files, each associated with a filename expected by the tool inside the container.

2. The API returns a JSON response with:
   - `exit_code`: The exit code of the command.
   - `stdout`: Standard output from the command.
   - `stderr`: Standard error from the command.
   - `output_files`: A list of objects, each containing `relative_path` and `content_base64` (base64-encoded content) for the requested output files.

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

# Example with R-Chie for arc diagram visualization
cli2rest-bio rchie/config.yaml your_rchie_input.json

# Example with BPNet for base pair network analysis (mmCIF files)
cli2rest-bio bpnet/config-cif.yaml sample.cif

# Example with BPNet for base pair network analysis (PDB files)
cli2rest-bio bpnet/config-pdb.yaml sample.pdb

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

- `name`: The tool name (used for output file prefixes).
- `docker_image`: The Docker image to use.
- `arguments`: A list containing the command-line tool to run followed by its arguments.
- `input_file` (string, optional, legacy): The relative path expected by the tool for the *single* input file. Use `input_files` for new configurations or multiple inputs.
- `input_files` (list of strings, optional): A list of relative paths expected by the tool for the input files. The first path in this list corresponds to the primary input file provided on the command line. Subsequent files are inferred based on the primary file's name and location (see `cli2rest-bio.py` for details). Prefer this over `input_file`.
- `output_files`: List of relative paths for output files to retrieve from the container (optional).

**Note:** Default configuration files for the included tools are packaged within the `src/cli2rest_bio/configs` directory. When you run `cli2rest-bio <config_path> ...`, the tool first looks for `<config_path>` relative to your current directory. If not found, it attempts to load the configuration from the package's internal `configs` directory (e.g., `cli2rest-bio fr3d/config.yaml` will load the packaged `fr3d/config.yaml` if it's not present locally).

Example configuration (reduce/config.yaml):
```yaml
name: "reduce"
docker_image: "ghcr.io/tzok/cli2rest-reduce:latest"
# Command and arguments combined
arguments:
  - "reduce"
  - "input.pdb"
# Define the single input file's expected path
input_file: "input.pdb"
# No specific output files requested (Reduce modifies in place or outputs to stdout)
```

Example configuration with multiple output files (fr3d/config.yaml):
```yaml
name: "fr3d"
docker_image: "ghcr.io/tzok/cli2rest-fr3d:latest"
arguments:
  - "wrapper.py" # The wrapper script is the command
  - "input.cif"  # Argument to the wrapper
input_file: "input.cif"
output_files: # Files generated by the wrapper
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
- `name`: Should be short and descriptive, used as a prefix for output files.
- `docker_image`: Must point to a valid Docker image containing the CLI tool and the `cli2rest` server.
- `arguments`: A list starting with the command to run inside the container, followed by its arguments. Use placeholders like `input.ext` if the tool expects specific filenames.
- `input_file` / `input_files`: Define the path(s) where the input file(s) will be placed inside the container, matching any filename arguments in the `arguments` list. Use `input_files` (list) for clarity and multiple inputs.
- `output_files`: List of relative paths for files generated by the tool that should be retrieved (optional).

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

# Pull the R-Chie container
docker pull ghcr.io/tzok/cli2rest-rchie:latest

# Pull the VARNA-TZ container
docker pull ghcr.io/tzok/cli2rest-varna-tz:latest

# Pull the BPNet container
docker pull ghcr.io/tzok/cli2rest-bpnet:latest

# Pull the MC-Annotate container
docker pull ghcr.io/tzok/cli2rest-mc-annotate:latest

# Pull the Barnaba container
docker pull ghcr.io/tzok/cli2rest-barnaba:latest
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
