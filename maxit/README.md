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

## Using the CLI2REST API

The CLI2REST API allows you to run the MAXIT tool via HTTP requests. Here's how to use it:

### Example: Converting a PDB file to mmCIF

You can use cURL to send a request to the API:

```bash
curl -X POST http://localhost:8000/run-command \
  -H "Content-Type: application/json" \
  -d '{
    "cli_tool": "maxit",
    "arguments": ["-input", "input.pdb", "-output", "/dev/stdout", "-o", "1"],
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
  cli_tool: "maxit",
  arguments: ["-input", "input.pdb", "-output", "/dev/stdout", "-o", "1"],
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
- Standard output (containing the converted file content)
- Standard error
- Generated files (if any)

Example response:

```json
{
  "exit_code": 0,
  "stdout": "data_RNA\n#\n_entry.id RNA\n...",
  "stderr": "...",
  "files": []
}
```

When using `/dev/stdout` as the output file, the converted content will be in the `stdout` field rather than in the `files` array. This is how our convenience scripts are designed to work.

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
