# R4RNA via CLI2REST

This container provides the R4RNA package, accessible via the CLI2REST API.

## About R4RNA

R4RNA is a package for RNA basepair analysis, including the visualization of basepairs as arc diagrams for easy comparison and annotation of sequence and structure. Arc diagrams can additionally be projected onto multiple sequence alignments to assess basepair conservation and covariation, with numerical methods for computing statistics for each.

## Usage

### Using the `cli2rest-bio` Tool

The recommended way to use this container is with the `cli2rest-bio` command-line tool provided in the main repository. You will need to create a `config.yaml` file specific to how you want to run R4RNA.

Example (assuming you have a `rchie/config.yaml`):
```bash
# Process an input file (specifics depend on R4RNA usage)
cli2rest-bio rchie/config.yaml your_input_file
```

This tool handles starting the container, sending requests according to your `config.yaml`, saving outputs, and cleaning up. See the main [README.md](../README.md) for more details on `cli2rest-bio`.

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
