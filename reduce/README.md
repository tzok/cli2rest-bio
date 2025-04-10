# Reduce Docker Container

This repository contains a Dockerfile for building a container with the [Reduce](https://github.com/rlabduke/reduce) tool wrapped in the CLI2REST API.

## What is Reduce?

Reduce is a program for adding hydrogens to RNA and other molecular structure files in PDB format. The program was developed by J. Michael Word at the Richardson Laboratory at Duke University.

## Usage

### Using the `cli2rest-bio` Tool

The recommended way to use this container is with the `cli2rest-bio` command-line tool provided in the main repository:

```bash
# Process a single PDB file
cli2rest-bio reduce/config.yaml your_rna.pdb

# Process multiple PDB files (using shell expansion or listing them)
cli2rest-bio reduce/config.yaml *.pdb
```

This tool handles starting the container, sending requests according to `reduce/config.yaml`, saving outputs (stdout/stderr prefixed with `reduce-`), and cleaning up. See the main [README.md](../README.md) for more details on `cli2rest-bio`.

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

### Example: Adding hydrogens using the API directly

You can use cURL with form data to send a request:

```bash
# Corresponds to reduce/config.yaml
# Note: Reduce often writes the modified structure to stdout.
# The config doesn't request specific output files.

curl -X POST http://localhost:8000/run-command \
  -F 'arguments=reduce' \
  -F 'arguments=input.pdb' \
  -F 'input_files=@path/to/your_local_rna.pdb;filename=input.pdb'
```

### Response

The API will return a JSON response containing the standard output (which usually includes the modified PDB), standard error, and exit code. Since `output_files` is empty in the config, the `output_files` list in the response will also be empty.

Example response:

```json
{
  "exit_code": 0,
  "stdout": "ATOM      1  P     G A   1      -0.521   9.276   5.352  1.00  0.00           P  \n...",
  "stderr": "Reduce version 3.2.3\n...",
  "output_files": []
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
