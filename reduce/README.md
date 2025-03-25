# Reduce Docker Container

This repository contains a Dockerfile for building a container with the [Reduce](https://github.com/rlabduke/reduce) tool wrapped in the CLI2REST API.

## What is Reduce?

Reduce is a program for adding hydrogens to RNA and other molecular structure files in PDB format. The program was developed by J. Michael Word at the Richardson Laboratory at Duke University.

## Using the reduce.sh Script

For convenience, this repository includes a `reduce.sh` script that simplifies the process of running Reduce on your PDB files:

```bash
# Process a single file
./reduce.sh your_rna.pdb

# Process all PDB files in a directory
./reduce.sh /path/to/pdb/files/
```

The script:
1. Starts a Docker container with Reduce
2. Automatically finds an available port
3. Waits for the service to be ready
4. Processes your PDB file(s) in parallel when processing a directory
5. Saves the processed PDB content to files (e.g., your_rna-reduce.pdb)
6. Cleans up the container when done

The script uses GNU parallel to process multiple files simultaneously when a directory is provided, which significantly speeds up processing when dealing with many files.

### Prerequisites

- Docker installed and running
- `jq` command-line tool for JSON processing
- `curl` for making HTTP requests

## Building the Container

To build the container, run:

```bash
docker build -t cli2rest-reduce .
```

## Running the Container

To start the container and expose the CLI2REST API on port 8000:

```bash
docker run -p 8000:8000 cli2rest-reduce
```

## Using the CLI2REST API

The CLI2REST API allows you to run the Reduce tool via HTTP requests. Here's how to use it:

### Example: Adding hydrogens to an RNA structure

You can use cURL to send a request to the API:

```bash
curl -X POST http://localhost:8000/run-command \
  -H "Content-Type: application/json" \
  -d '{
    "cli_tool": "reduce",
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

If you have a PDB file locally, you can use jq to build the request:

```bash
jq -n --arg pdb "$(cat your_rna.pdb)" '{
  cli_tool: "reduce",
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
- Generated files (if any)

Example response:

```json
{
  "exit_code": 0,
  "stdout": "...",
  "stderr": "...",
  "files": [
    {
      "relative_path": "output.pdb",
      "content": "..."
    }
  ]
}
```

## Additional Reduce Options

Reduce supports various command-line options:

- `-FLIP`: Optimize hydrogen positions by flipping certain groups
- `-NOFLIP`: Don't flip groups
- `-TRIM`: Remove hydrogens
- `-BUILD`: Add hydrogens (default)
- `-HIS`: Change histidine name to HIS
- `-ROTEXIST`: Rotate existing hydrogens

> **Note:** The current `reduce.sh` script uses default options. To use specific Reduce options, you'll need to modify the script or use the CLI2REST API directly as shown in the examples below.

For a complete list of options, see the [Reduce documentation](https://github.com/rlabduke/reduce).
