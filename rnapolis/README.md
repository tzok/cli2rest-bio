# RNAPOLIS - RNA Structure Annotation

RNAPOLIS is a tool for annotating RNA 3D structures, focusing on identifying base pairs and other interactions. This container provides a REST API interface to RNAPOLIS.

## About RNAPOLIS

RNAPOLIS analyzes RNA 3D structures (in PDB or mmCIF format) to identify canonical and non-canonical base pairs, stacking interactions, and other structural features. It provides detailed output in JSON format.

## Usage

### Using the Convenience Script

The simplest way to use this container is with the provided convenience script:

```bash
# Process a single file
./rnapolis.sh your_rna.cif

# Process all CIF files in a directory
./rnapolis.sh /path/to/cif/files/
```

This will:
1. Start a container with RNAPOLIS
2. Process your CIF file(s) in parallel when processing a directory
3. Save the annotations as JSON files (e.g., your_rna-rnapolis.json)
4. Clean up the container

*(Note: The convenience script `rnapolis.sh` needs to be created separately)*

### Using the REST API Directly

You can also interact with the API directly:

```bash
# Start the container
docker run -p 8000:8000 ghcr.io/tzok/cli2rest-rnapolis:latest

# Send a request
curl -X POST http://localhost:8000/run-command \
  -H "Content-Type: application/json" \
  -d '{
    "cli_tool": "rnapolis",
    "arguments": ["-i", "input.cif", "-o", "output.json"],
    "files": [
      {
        "relative_path": "input.cif",
        "content": "data_1EHZ\n#\n_entry.id 1EHZ\n..."
      }
    ]
  }'
```

## Output Format

The output is a JSON file containing detailed annotations of the RNA structure.

Example output (`output.json`):
```json
{
  "interactions": [
    {
      "nt1": "A.1",
      "nt2": "U.10",
      "bp_type": "cWW",
      ...
    },
    ...
  ],
  ...
}
```

## Building the Container

To build the container locally:

```bash
docker build -t cli2rest-rnapolis .
```

## References

- [RNAPOLIS GitHub Repository](https://github.com/analyze-rna/rnapolis)
