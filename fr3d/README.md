# FR3D - Find RNA 3D

FR3D (pronounced "Fred") is a suite of tools for annotating RNA 3D structures. This container provides a REST API interface to FR3D's pairwise interaction annotation capabilities.

## About FR3D

FR3D (Find RNA 3D) is developed by the Bowling Green State University RNA group. It analyzes RNA 3D structures to identify and classify structural features including:

- Base pairs
- Base stacking interactions
- Backbone conformations

The tool is particularly useful for RNA structure analysis, comparison, and classification.

## Usage

### Using the Convenience Script

The simplest way to use this container is with the provided convenience script:

```bash
# Process a single file
./fr3d.sh your_rna.cif

# Process all CIF files in a directory
./fr3d.sh /path/to/cif/files/
```

This will:
1. Start a container with FR3D
2. Process your CIF file(s) in parallel when processing a directory
3. Save the annotations as JSON files (e.g., your_rna-fr3d.json)
4. Clean up the container

The script uses GNU parallel to process multiple files simultaneously when a directory is provided, which significantly speeds up processing when dealing with many files.

### Using the REST API Directly

You can also interact with the API directly:

```bash
# Start the container
docker run -p 8000:8000 ghcr.io/tzok/cli2rest-fr3d:latest

# Send a request
curl -X POST http://localhost:8000/run-command \
  -H "Content-Type: application/json" \
  -d '{
    "cli_tool": "fr3d_runner.py",
    "arguments": ["input.cif"],
    "files": [
      {
        "relative_path": "input.cif",
        "content": "data_1EHZ\n#\n_entry.id 1EHZ\n..."
      }
    ]
  }'
```

## Output Format

The output is a JSON object with three main sections:

- `basepair`: Detailed base pair annotations
- `stacking`: Base stacking interactions
- `backbone`: Backbone conformations

Example output:
```json
{
  "basepair": "# FR3D basepair annotations for 1EHZ\n...",
  "stacking": "# FR3D stacking annotations for 1EHZ\n...",
  "backbone": "# FR3D backbone annotations for 1EHZ\n..."
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
