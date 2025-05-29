# R4RNA via CLI2REST

This container provides the R4RNA package, accessible via the CLI2REST API.

## About R4RNA

R4RNA is a package for RNA basepair analysis, including the visualization of basepairs as arc diagrams for easy comparison and annotation of sequence and structure. Arc diagrams can additionally be projected onto multiple sequence alignments to assess basepair conservation and covariation, with numerical methods for computing statistics for each.

## Usage

### Using the `cli2rest-bio` Tool

The recommended way to use this container is with the `cli2rest-bio` command-line tool provided in the main repository.
The `cli2rest-bio` tool uses a configuration file, typically named `config.yaml` (an example is provided in `src/cli2rest_bio/configs/rchie/config.yaml`), to manage the Docker container and specify input/output behavior.

The `rchie/config.yaml` should look like this:
```yaml
name: "rchie"
docker_image: "ghcr.io/tzok/cli2rest-rchie:latest"
arguments:
  - "wrapper.py"
input_file: "input.json" # This is the name the input file will have inside the container
output_files:
  - "clean.svg" # The final SVG output from the wrapper
```

Example command:
```bash
# Process an input JSON file using the rchie configuration
cli2rest-bio rchie/config.yaml your_input_data.json
```

This command will:
1. Start the `ghcr.io/tzok/cli2rest-rchie:latest` Docker container.
2. Copy `your_input_data.json` into the container as `input.json`.
3. Execute `wrapper.py input.json` inside the container.
4. Retrieve `clean.svg` from the container.
5. Save the output locally, prefixed with "rchie" (e.g., `rchie_your_input_data_clean.svg`).
6. Stop and remove the container.

See the main [README.md](../README.md) for more details on `cli2rest-bio` and general configuration.

### Input JSON Format

The `wrapper.py` script inside the container expects a single JSON file as input. This file must adhere to the following structure:

```json
{
  "sequence": "YOUR_RNA_SEQUENCE_STRING",
  "title": "Optional Title for the Plot",
  "top": [
    {"i": 1, "j": 10, "color": "red"},
    {"i": 2, "j": 9, "color": "blue"}
    // ... more interactions for the top arc diagram
  ],
  "bottom": [
    {"i": 20, "j": 30, "color": "#FF00FF"},
    {"i": 21, "j": 29, "color": null} // null or absent color means default
    // ... more interactions for the bottom arc diagram
  ]
}
```

**Field Descriptions:**

-   `sequence` (string, required): The RNA sequence.
-   `title` (string, optional): An optional title for the generated plot. If omitted, "sequence" will be used.
-   `top` (list of objects, required): A list of interaction objects for the top arc diagram.
-   `bottom` (list of objects, required): A list of interaction objects for the bottom arc diagram.

**Interaction Object:**

Each interaction object within the `top` and `bottom` lists must have:
-   `i` (integer, required): The **1-based** starting position of the interaction.
-   `j` (integer, required): The **1-based** ending position of the interaction.
-   `color` (string or null, optional): The color for the arc representing this interaction. This can be a color name (e.g., "red", "blue") or a hex code (e.g., "#FF00FF"). If `null` or omitted, a default color assignment strategy is used by the R script.

**Important:** The `i` and `j` indices for interactions **MUST BE 1-BASED**. The R4RNA package, which is used for plotting, expects 1-based indexing for sequence positions. Providing 0-based or invalid indices will lead to errors.

### Using the REST API Directly

You can also interact with the API directly:

```bash
# Start the container (replace with the actual image name/tag after building)
docker run -d -p 8000:8000 ghcr.io/tzok/cli2rest-rchie:latest # Example name

# Send a request using form data (adjust arguments and files as needed)
# This is a generic example; actual R4RNA commands will vary.
# You would typically have a wrapper script or directly call Rscript.
curl -X POST http://localhost:8000/run-command \
  -F 'arguments=Rscript' \
  -F 'arguments=-e' \
  -F 'arguments=print(\"Hello from R4RNA\")' # Example R command
  # -F 'input_files=@path/to/your_local_file;filename=input_file.txt' # If needed
  # -F 'output_files=output.txt' # If R4RNA produces specific files
```

## Output Format

The output will depend on the specific R4RNA functions used and how they are invoked. The `cli2rest-bio` tool will save `stdout.txt`, `stderr.txt`, and any files specified in the `output_files` list of your configuration.

The API response itself contains the `stdout`, `stderr`, `exit_code`, and the content of any requested output files encoded in base64.

## Building the Container

To build the container locally:

```bash
docker build -t cli2rest-rchie .
```
(Ensure you are in the `rchie` directory or adjust the context path)

## References

- [R4RNA on Bioconductor](https://www.bioconductor.org/packages/release/bioc/html/R4RNA.html)
