# FR3D - Find RNA 3D

FR3D (pronounced "Fred") is a suite of tools for annotating RNA 3D structures. This container provides a REST API interface to FR3D's pairwise interaction annotation capabilities.

## About FR3D

FR3D (Find RNA 3D) is developed by the Bowling Green State University RNA group. It analyzes RNA 3D structures to identify and classify structural features including:

- Base pairs
- Base stacking interactions
- Backbone conformations

The tool is particularly useful for RNA structure analysis, comparison, and classification.

## Usage

### Using the `cli2rest-bio` Tool

The recommended way to use this container is with the `cli2rest-bio` command-line tool provided in the main repository:

```bash
# Process a single CIF file
cli2rest-bio fr3d/config.yaml your_rna.cif

# Process multiple CIF files (using shell expansion or listing them)
cli2rest-bio fr3d/config.yaml *.cif
```

This tool handles starting the container, sending requests according to `fr3d/config.yaml`, saving outputs (prefixed with `fr3d-`), and cleaning up. See the main [README.md](../README.md) for more details on `cli2rest-bio`.

### Using the REST API Directly

You can also interact with the API directly:

```bash
# Start the container
docker run -p 8000:8000 ghcr.io/tzok/cli2rest-fr3d:latest

# Send a request using form data
# Corresponds to fr3d/config.yaml

curl -X POST http://localhost:8000/run-command \
  -F 'arguments=wrapper.py' \
  -F 'arguments=input.cif' \
  -F 'output_files=basepair_detail.txt' \
  -F 'output_files=stacking.txt' \
  -F 'output_files=backbone.txt' \
  -F 'input_files=@path/to/your_local_rna.cif;filename=input.cif'
```

## Output Format

The `cli2rest-bio` tool saves the following output files (prefixed with `fr3d-<input_base_name>-`):

- `basepair_detail.txt`: Detailed base pair annotations.
- `stacking.txt`: Base stacking interactions.
- `backbone.txt`: Backbone conformations.
- `stdout.txt`: Standard output from the wrapper script.
- `stderr.txt`: Standard error from the wrapper script.

The API response itself contains the `stdout`, `stderr`, `exit_code`, and the content of the requested output files encoded in base64 within the `output_files` list. Example snippet of the JSON response:

```json
{
  "exit_code": 0,
  "stdout": "Created: backbone.txt\nCreated: basepair_detail.txt\nCreated: stacking.txt\n",
  "stderr": "",
  "output_files": [
    {
      "relative_path": "basepair_detail.txt",
      "content_base64": "IyBG..."
    },
    {
      "relative_path": "stacking.txt",
      "content_base64": "IyBG..."
    },
    {
      "relative_path": "backbone.txt",
      "content_base64": "IyBG..."
    }
  ]
}
```

## Building the Container

To build the container locally:

```bash
docker build -t cli2rest-fr3d .
```

## References

- [FR3D GitHub Repository](https://github.com/BGSU-RNA/fr3d-python)
- [BGSU RNA Group](http://rna.bgsu.edu/)
