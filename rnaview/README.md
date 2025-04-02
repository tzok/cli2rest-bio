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

## Using the CLI2REST API

The CLI2REST API allows you to run the RNAView tool via HTTP requests. The convenience scripts support parallel processing of multiple files using GNU parallel, which significantly improves performance when processing directories with many files.

Here's how to use the API directly:

### Example: Analyzing an RNA structure file

You can use cURL to send a request to the API:

```bash
curl -X POST http://localhost:8000/run-command \
  -H "Content-Type: application/json" \
  -d '{
    "cli_tool": "rnaview",
    "arguments": ["input.pdb"],
    "files": [
      {
        "relative_path": "input.pdb",
        "content": "ATOM      1  P     G A   1      -0.521   9.276   5.352  1.00  0.00           P  \nATOM      2  OP1   G A   1      -0.880   9.088   6.785  1.00  0.00           O  \nATOM      3  OP2   G A   1      -1.154  10.349   4.548  1.00  0.00           O  \nATOM      4  O5\'   G A   1       1.056   9.358   5.199  1.00  0.00           O  \nATOM      5  C5\'   G A   1       1.849   8.189   5.386  1.00  0.00           C  \nEND"
      }
    ]
  }'
```

### Using jq to format the request

If you have a structure file locally, you can use jq to build the request:

```bash
jq -n --arg pdb "$(cat your_rna.pdb)" '{
  cli_tool: "rnaview",
  arguments: ["input.pdb"],
  files: [
    {
      relative_path: "input.pdb",
      content: $pdb
    }
  ]
}' | curl -X POST http://localhost:8000/run-command \
     -H "Content-Type: application/json" \
     -d @-
```

### Response

The API will return a JSON response with:

- The exit code of the command
- Standard output
- Standard error
- Generated files (containing the analysis results)

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
