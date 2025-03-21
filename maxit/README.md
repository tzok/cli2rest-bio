# MAXIT Docker Container

This repository contains a Dockerfile for building a container with the [MAXIT](https://sw-tools.rcsb.org/apps/MAXIT/) tool wrapped in the CLI2REST API.

## What is MAXIT?

MAXIT is a program developed by the RCSB PDB for manipulating and validating PDB and mmCIF files. It can convert between PDB and mmCIF formats, extract information from structure files, and perform various validation checks.

## Building the Container

To build the container, run:

```bash
docker build -t cli2-rest-maxit .
```

## Running the Container

To start the container and expose the CLI2REST API on port 8000:

```bash
docker run -p 8000:8000 cli2-rest-maxit
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
    "arguments": ["-input", "input.pdb", "-output", "output.cif", "-o"],
    "files": [
      {
        "relative_path": "input.pdb",
        "content": "ATOM      1  N   ALA A   1      11.104   6.134  -6.504  1.00  0.00           N  \nATOM      2  CA  ALA A   1      11.639   6.071  -5.147  1.00  0.00           C  \nATOM      3  C   ALA A   1      10.674   5.323  -4.252  1.00  0.00           C  \nATOM      4  O   ALA A   1       9.705   4.695  -4.708  1.00  0.00           O  \nATOM      5  CB  ALA A   1      11.888   7.456  -4.570  1.00  0.00           C  \nEND"
      }
    ]
  }'
```

### Using jq to format the request

If you have a PDB file locally, you can use jq to build the request:

```bash
jq -n --arg pdb "$(cat your_structure.pdb)" '{
  cli_tool: "maxit",
  arguments: ["-input", "input.pdb", "-output", "output.cif", "-o"],
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
      "relative_path": "output.cif",
      "content": "..."
    }
  ]
}
```

## Common MAXIT Options

MAXIT supports various command-line options:

- `-input <file>`: Input file name
- `-output <file>`: Output file name
- `-o`: Convert PDB to mmCIF
- `-i`: Convert mmCIF to PDB
- `-report`: Generate validation report
- `-dict <file>`: Use specified dictionary

For a complete list of options, see the [MAXIT documentation](https://sw-tools.rcsb.org/apps/MAXIT/).
