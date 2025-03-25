# CLI2REST Docker Containers

This repository contains Docker containers for various bioinformatics tools wrapped with the CLI2REST API. CLI2REST provides a simple HTTP interface to command-line tools, making them accessible via REST API calls.

## Available Tools

Currently, the following tools are available:

- [Reduce](./reduce/): A tool for adding hydrogens to PDB files
- [MaxiT](./maxit/): A tool for PDB file format conversion and validation

## How It Works

Each tool is containerized with Docker and exposed through a REST API that follows the same pattern:

1. You send a JSON request with:
   - The command-line tool to run
   - Arguments to pass to the tool
   - Input files encoded as strings

2. The API returns a JSON response with:
   - Exit code
   - Standard output
   - Standard error
   - Any generated files

## Quick Start

### Using the Convenience Scripts

Each tool comes with a convenience script that simplifies usage:

```bash
# For Reduce (adding hydrogens to PDB files)
./reduce/reduce.sh your_structure.pdb > your_structure_with_hydrogens.pdb

# For MaxiT (if available)
./maxit/maxit.sh your_structure.pdb > converted_structure.cif
```

### Using the REST API Directly

You can also interact with the API directly:

```bash
# Start a container (example with Reduce)
docker run -p 8000:8000 ghcr.io/tzok/cli2rest-reduce:latest

# Send a request
curl -X POST http://localhost:8000/run-command \
  -H "Content-Type: application/json" \
  -d '{
    "cli_tool": "reduce",
    "arguments": ["input.pdb"],
    "files": [
      {
        "relative_path": "input.pdb",
        "content": "ATOM      1  N   ALA A   1      11.104   6.134  -6.504  1.00  0.00           N  \n..."
      }
    ]
  }'
```

## Building from Source

Each tool has its own Dockerfile in its respective directory:

```bash
# Build Reduce container
cd reduce
docker build -t cli2rest-reduce .

# Build MaxiT container
cd maxit
docker build -t cli2rest-maxit .
```

## Requirements

- Docker
- curl (for API requests)
- jq (for processing JSON responses)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The original tool developers for their valuable contributions to bioinformatics
- The CLI2REST framework for simplifying API access to command-line tools
