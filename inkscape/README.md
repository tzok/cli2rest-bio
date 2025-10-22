# Inkscape Docker Container

This repository contains a Dockerfile for building a container with [Inkscape](https://inkscape.org/) wrapped in the CLI2REST API.

## What is Inkscape?

Inkscape is a professional vector graphics editor for Linux, Windows and macOS. It's free and open source. It can be used from the command line to perform various operations on SVG files, including exporting to other formats.

## Usage

### Using the `cli2rest-bio` Tool

The recommended way to use this container is with the `cli2rest-bio` command-line tool provided in the main repository:

```bash
# Convert SVG files to PNG with Inkscape
cli2rest-bio src/cli2rest_bio/configs/inkscape/config.yaml your_drawing.svg
```

This tool handles starting the container, sending requests according to the appropriate configuration file, saving outputs, and cleaning up. See the main [README.md](../README.md) for more details on `cli2rest-bio`.

## Building the Container

To build the container, run:

```bash
docker build -t cli2rest-inkscape .
```

## Running the Container

To start the container and expose the CLI2REST API on port 8000:

```bash
docker run -p 8000:8000 cli2rest-inkscape
```

## Using the CLI2REST API

The CLI2REST API allows you to run Inkscape via HTTP requests. Here's how to use it:

### Example: Converting an SVG to PNG using the API directly

You can use cURL with form data to send a request:

```bash
# Corresponds to src/cli2rest_bio/configs/inkscape/config.yaml
curl -X POST http://localhost:8000/run-command \
  -F 'arguments=inkscape' \
  -F 'arguments=input.svg' \
  -F 'arguments=--export-type=png' \
  -F 'arguments=--export-filename=output.png' \
  -F 'input_files=@path/to/your_local_drawing.svg;filename=input.svg'
```

### Response

The API will return a JSON response containing the standard output, standard error, exit code, and the output PNG file.

Example response:

```json
{
  "exit_code": 0,
  "stdout": "Background RRGGBBAA: ffffff00\nArea 0:0:100:100 exported to 100 x 100 pixels (96 DPI)\n",
  "stderr": "",
  "output_files": [
    {
      "filename": "output.png",
      "content": "base64_encoded_content"
    }
  ]
}
```
