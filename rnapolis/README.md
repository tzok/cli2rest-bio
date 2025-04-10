# RNAPOLIS - RNA Structure Annotation

RNAPOLIS is a tool for annotating RNA 3D structures, focusing on identifying base pairs and other interactions. This container provides a REST API interface to RNAPOLIS.

## About RNAPOLIS

RNAPOLIS analyzes RNA 3D structures (in PDB or mmCIF format) to identify canonical and non-canonical base pairs, stacking interactions, and other structural features. It provides detailed output in JSON format.

## Usage

### Using the `cli2rest-bio` Tool

The recommended way to use this container is with the `cli2rest-bio` command-line tool provided in the main repository:

```bash
# Process an archive of PDB/CIF files using the unifier
cli2rest-bio rnapolis/config-unifier.yaml your_structures.tar.gz

# Process a single PDB/CIF file using the splitter
cli2rest-bio rnapolis/config-splitter.yaml your_rna.pdb
```

This tool handles starting the container, sending requests, saving outputs, and cleaning up. See the main [README.md](../README.md) for more details on `cli2rest-bio`.

*(Note: The `config-unifier.yaml` uses `unifier-wrapper.py` inside the container to process `.tar.gz` archives containing multiple PDB/CIF files, while `config-splitter.yaml` uses `splitter-wrapper.py` to process a single PDB/CIF file.)*

### Using the REST API Directly

You can also interact with the API directly:

```bash
# Start the container
docker run -p 8000:8000 ghcr.io/tzok/cli2rest-rnapolis:latest

# Send a request using form data
# (Example assumes a hypothetical single-file config for simplicity)
# Replace 'rnapolis -i input.cif -o output.json' with actual arguments from your config
# Replace 'output.json' with actual output file names from your config

curl -X POST http://localhost:8000/run-command \
  -F 'arguments=rnapolis' \
  -F 'arguments=-i' \
  -F 'arguments=input.cif' \
  -F 'arguments=-o' \
  -F 'arguments=output.json' \
  -F 'output_files=output.json' \
  -F 'input_files=@path/to/your_local_rna.cif;filename=input.cif'
```

*(Note: For the `config-unifier.yaml`, you would send `unifier-wrapper.py --format PDB input.tar.gz` as arguments, `output.tar.gz` as output_files, and upload your archive as `input.tar.gz`)*

## Output Format

The output depends on the specific RNAPOLIS command run.

- For the `unifier-wrapper.py` (using `config-unifier.yaml`), the output is a `output.tar.gz` archive containing the processed files.
- For a direct `rnapolis` call (hypothetical example above), the output would be `output.json` containing detailed annotations:
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
