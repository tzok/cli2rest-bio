# Reduce Docker Container

This repository contains a Dockerfile for building a container with the [Reduce](https://github.com/rlabduke/reduce) tool wrapped in the CLI2REST API.

## What is Reduce?

Reduce is a program for adding hydrogens to a Protein Data Bank (PDB) molecular structure file. The program was developed by J. Michael Word at the Richardson Laboratory at Duke University.

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

### Example: Adding hydrogens to a PDB file

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
        "content": "ATOM      1  N   ALA A   1      11.104   6.134  -6.504  1.00  0.00           N  \nATOM      2  CA  ALA A   1      11.639   6.071  -5.147  1.00  0.00           C  \nATOM      3  C   ALA A   1      10.674   5.323  -4.252  1.00  0.00           C  \nATOM      4  O   ALA A   1       9.705   4.695  -4.708  1.00  0.00           O  \nATOM      5  CB  ALA A   1      11.888   7.456  -4.570  1.00  0.00           C  \nEND"
      }
    ]
  }'
```

### Using jq to format the request

If you have a PDB file locally, you can use jq to build the request:

```bash
jq -n --arg pdb "$(cat your_structure.pdb)" '{
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

For a complete list of options, see the [Reduce documentation](https://github.com/rlabduke/reduce).
