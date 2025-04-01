#!/usr/bin/env python3
import argparse
import glob
import json
import os
import sys
import uuid
import stat
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import docker
import jinja2
import requests
import yaml


def load_tool_config(tool_name):
    """Load the YAML configuration for a specific tool."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, tool_name, "config.yaml")

    if not os.path.exists(config_path):
        print(
            f"Error: Configuration for tool '{tool_name}' not found at {config_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config


def parse_arguments(config):
    """Parse command line arguments based on the tool configuration."""
    parser = argparse.ArgumentParser(
        description=config.get("description", "Tool runner")
    )

    # Add arguments for each input defined in the config
    for input_param in config.get("inputs", []):
        arg_name = f"--{input_param['name'].replace('_', '-')}"

        if input_param.get("type") == "boolean":
            parser.add_argument(
                arg_name,
                help=input_param.get("description", ""),
                action="store_true"
                if input_param.get("default", False)
                else "store_false",
                dest=input_param["name"],
            )
        elif input_param.get("required", False):
            parser.add_argument(
                arg_name,
                help=input_param.get("description", ""),
                required=True,
                dest=input_param["name"],
            )
        else:
            parser.add_argument(
                arg_name,
                help=f"{input_param.get('description', '')} (default: {input_param.get('default', None)})",
                default=input_param.get("default", None),
                dest=input_param["name"],
            )

    # Add common arguments
    parser.add_argument(
        "--threads",
        type=int,
        default=os.cpu_count(),
        help="Number of parallel threads to use",
    )

    return parser.parse_args()


def find_input_files(file_path, extensions):
    """Find all files with the specified extensions in the input path."""
    file_path = os.path.abspath(file_path)

    if os.path.isfile(file_path):
        # Check if the file has a valid extension
        if any(file_path.lower().endswith(ext.lower()) for ext in extensions):
            return [file_path]
        else:
            valid_exts = ", ".join(extensions)
            print(
                f"Error: Input file must have one of these extensions: {valid_exts}",
                file=sys.stderr,
            )
            sys.exit(1)

    elif os.path.isdir(file_path):
        # Find all files with the specified extensions
        files = []
        for ext in extensions:
            files.extend(glob.glob(os.path.join(file_path, f"*{ext}")))

        if not files:
            valid_exts = ", ".join(extensions)
            print(
                f"Error: No files with extensions {valid_exts} found in directory '{file_path}'",
                file=sys.stderr,
            )
            sys.exit(1)

        return sorted(files)

    else:
        print(f"Error: '{file_path}' is not a valid file or directory", file=sys.stderr)
        sys.exit(1)


def start_docker_container(docker_image):
    """Start a Docker container with the specified image and return the container ID and port."""
    # Generate a unique container name using UUID
    container_name = (
        f"{docker_image.split('/')[-1].split(':')[0]}-{uuid.uuid4().hex[:8]}"
    )

    print(f"Starting container with image: {docker_image}...", file=sys.stderr)

    # Initialize Docker client
    client = docker.from_env()

    # Pull the image if needed
    try:
        client.images.get(docker_image)
    except docker.errors.ImageNotFound:
        print(f"Pulling image {docker_image}...", file=sys.stderr)
        client.images.pull(docker_image)

    # Start the container with a random port
    container = client.containers.run(
        docker_image,
        name=container_name,
        detach=True,
        ports={"8000/tcp": None},  # Assign a random port
    )

    # Get the port that Docker assigned
    container_info = client.containers.get(container.id)
    port = container_info.ports["8000/tcp"][0]["HostPort"]

    print(f"Container running on port: {port}", file=sys.stderr)

    # Wait for the container to be ready
    print("Waiting for service to be ready...", file=sys.stderr, end="")
    sys.stderr.flush()

    while True:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=1)
            if response.status_code == 200:
                break
        except requests.RequestException:
            pass

        print(".", file=sys.stderr, end="")
        sys.stderr.flush()
        time.sleep(1)

    print(" Ready!", file=sys.stderr)

    return container, port


def stop_docker_container(container):
    """Stop and remove the Docker container."""
    print("Cleaning up...", file=sys.stderr)

    # Stop and remove the container
    container.stop()
    container.remove()


def render_template(template_str, variables):
    """Render a template string with Jinja2."""
    env = jinja2.Environment(
        undefined=jinja2.StrictUndefined, trim_blocks=True, lstrip_blocks=True
    )
    template = env.from_string(template_str)
    return template.render(**variables)


def process_file(input_file, config, args, port):
    """Process a single input file using the specified tool configuration."""
    # Get file information
    input_base = os.path.splitext(os.path.basename(input_file))[0]
    input_ext = os.path.splitext(input_file)[1]
    input_dir = os.path.dirname(input_file)

    # Create variables dictionary for template rendering
    variables = {
        "input_file": input_file,
        "input_file_base": input_base,
        "input_file_ext": input_ext,
        "input_dir": input_dir,
    }

    # Add command line arguments to variables
    for input_param in config.get("inputs", []):
        param_name = input_param["name"]
        if hasattr(args, param_name):
            variables[param_name] = getattr(args, param_name)

    # Determine output file paths
    for output in config.get("outputs", []):
        output_name = output["name"]
        output_pattern = output["file_pattern"]
        output_path = os.path.join(
            input_dir, render_template(output_pattern, variables)
        )
        variables[output_name] = output_path

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Skip if output file already exists
        if os.path.exists(output_path):
            print(
                f"Skipping {input_file} - output file already exists: {output_path}",
                file=sys.stderr,
            )
            return

    print(f"Processing file: {input_file}", file=sys.stderr)

    # Prepare the command
    cli_tool = config["command"]["cli_tool"]
    command_template = config["command"]["template"]

    # Add cli_tool to variables
    variables["cli_tool"] = cli_tool

    # Render the command template
    command = render_template(command_template, variables)
    command_args = command.split()[1:]  # Skip the cli_tool itself

    # Prepare file mappings
    files = []
    for mapping in config["command"].get("file_mappings", []):
        input_path = render_template(mapping["input"], variables)
        container_path = mapping["container_path"]

        with open(input_path, "r") as f:
            content = f.read()

        files.append({"relative_path": container_path, "content": content})

    # Create the JSON payload
    payload = {"cli_tool": cli_tool, "arguments": command_args, "files": files}

    # Send the request to the container
    response = requests.post(
        f"http://localhost:{port}/run-command",
        headers={"Content-Type": "application/json"},
        json=payload,
    )

    if response.status_code != 200:
        print(f"Error processing {input_file}: {response.text}", file=sys.stderr)
        return

    # Extract the output and save to files
    result = response.json()

    # Save stdout to the primary output file
    primary_output = variables.get(config["outputs"][0]["name"])
    with open(primary_output, "w") as f:
        f.write(result["stdout"])

    print(f"Saved output to: {primary_output}", file=sys.stderr)


def main():
    # Get the tool name from the script name
    script_name = os.path.basename(sys.argv[0])
    tool_name = (
        script_name.split("-")[0] if "-" in script_name else script_name.split(".")[0]
    )

    # Load the tool configuration
    config = load_tool_config(tool_name)

    # Parse command line arguments
    args = parse_arguments(config)

    # Find input files for file-type inputs
    input_files = []
    for input_param in config.get("inputs", []):
        if input_param["type"] == "file" and input_param.get("required", False):
            param_name = input_param["name"]
            param_value = getattr(args, param_name)
            extensions = input_param.get("extensions", [])

            files = find_input_files(param_value, extensions)
            input_files.extend(files)

    if len(input_files) > 1:
        print(f"Found {len(input_files)} files to process", file=sys.stderr)

    # Start the Docker container
    container, port = start_docker_container(config["docker_image"])

    try:
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = [
                executor.submit(process_file, input_file, config, args, port)
                for input_file in input_files
            ]

            # Wait for all tasks to complete
            for future in futures:
                future.result()

    finally:
        # Clean up - stop and remove the container
        stop_docker_container(container)

    print("Done!", file=sys.stderr)


if __name__ == "__main__":
    main()
