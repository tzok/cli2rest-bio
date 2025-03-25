# CLI2REST Docker Containers

This repository contains Docker containers for various bioinformatics tools wrapped with the CLI2REST API. CLI2REST provides a simple HTTP interface to command-line tools, making them accessible via REST API calls.

## Available Tools

Currently, the following tools are available:

- [Reduce](./reduce/): A tool for adding hydrogens to RNA structures in PDB format
- [MaxiT](./maxit/): A tool for RNA structure format conversion and validation
- [FR3D](./fr3d/): A tool for RNA structure annotation and classification

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
# For Reduce (adding hydrogens to RNA structures)
./reduce/reduce.sh your_rna.pdb                # Process a single file
./reduce/reduce.sh /path/to/pdb/files/         # Process all PDB files in a directory

# For MaxiT format conversions
./maxit/maxit-pdb2cif.sh your_rna.pdb          # Process a single file
./maxit/maxit-pdb2cif.sh /path/to/pdb/files/   # Process all PDB files in a directory

./maxit/maxit-cif2pdb.sh your_rna.cif          # Process a single file
./maxit/maxit-cif2pdb.sh /path/to/cif/files/   # Process all CIF files in a directory

./maxit/maxit-cif2mmcif.sh your_rna.cif        # Process a single file
./maxit/maxit-cif2mmcif.sh /path/to/cif/files/ # Process all CIF files in a directory

# For FR3D RNA structure annotation
./fr3d/fr3d.sh your_rna.cif                    # Process a single file
./fr3d/fr3d.sh /path/to/cif/files/             # Process all CIF files in a directory
```

When processing a single file, the output will be saved to a file with the same base name but a different extension. For example:
- `input.cif` → `input.pdb` (when using maxit-cif2pdb.sh)
- `input.pdb` → `input.cif` (when using maxit-pdb2cif.sh)
- `input.cif` → `input.mmcif` (when using maxit-cif2mmcif.sh)

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
        "content": "ATOM      1  P     G A   1      -0.521   9.276   5.352  1.00  0.00           P  \n..."
      }
    ]
  }'
```

## Pre-built Container Images

Pre-built container images are available on GitHub Container Registry:

```bash
# Pull the Reduce container
docker pull ghcr.io/tzok/cli2rest-reduce:latest

# Pull the MaxiT container
docker pull ghcr.io/tzok/cli2rest-maxit:latest

# Pull the FR3D container
docker pull ghcr.io/tzok/cli2rest-fr3d:latest
```

These images are automatically built and updated with the latest changes.

## Building from Source

If you prefer to build the containers yourself, each tool has its own Dockerfile in its respective directory:

```bash
# Build Reduce container
cd reduce
docker build -t cli2rest-reduce .

# Build MaxiT container
cd maxit
docker build -t cli2rest-maxit .

# Build FR3D container
cd fr3d
docker build -t cli2rest-fr3d .
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
