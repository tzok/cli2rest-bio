# varna-tz CLI2REST Wrapper

This directory contains the configuration and wrapper script to run `varna-tz` within the CLI2REST framework.

## Tool Description

`varna-tz` is a custom version of [VARNA](http://varna.lri.fr/), a tool for drawing the secondary structure of RNA. This version includes specific modifications or features tailored for particular use cases. It takes a JSON input describing the RNA structure and visualization parameters and outputs an SVG image.

The wrapper script also utilizes `svgcleaner` to optimize the generated SVG output.

## Configuration (`config.yaml`)

```yaml
name: "varna-tz"
docker_image: "ghcr.io/tzok/cli2rest-varna-tz:latest"
arguments:
  - "wrapper.sh" # Executes the wrapper script
input_file: "input.json" # Expected input filename inside the container
output_files:
  - "clean.svg" # Optimized SVG output file to retrieve
```

## Usage with `cli2rest-bio`

```bash
cli2rest-bio varna-tz/config.yaml your_input.json
```

This command will:
1. Start the `ghcr.io/tzok/cli2rest-varna-tz:latest` Docker container.
2. Send `your_input.json` to the container as `input.json`.
3. Execute `wrapper.sh` inside the container, which runs `varna-tz` and then `svgcleaner`.
4. Retrieve the resulting `clean.svg` file and save it locally as `varna-tz-clean.svg`.
5. Stop the Docker container.
