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


def parse_arguments(config, tool_name):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog=f"cli2rest-bio.py {tool_name}",
        description=config.get("description", "Tool runner"),
    )

    # Add common arguments
    parser.add_argument(
        "--threads",
        type=int,
        default=os.cpu_count(),
        help="Number of parallel threads to use",
    )

    # Add input files as positional arguments
    parser.add_argument(
        "input_files",
        nargs="+",
        help="Input file(s) to process",
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


def process_file(input_file, config, args, port, tool_name):
    """Process a single input file using the specified tool configuration."""
    # Get file information
    input_base = os.path.splitext(os.path.basename(input_file))[0]
    input_dir = os.path.dirname(input_file)

    print(f"Processing file: {input_file}", file=sys.stderr)

    # Get cli2rest configuration
    cli2rest_config = config.get("cli2rest", {})
    if not cli2rest_config:
        print(f"Error: No cli2rest configuration found in config.yaml", file=sys.stderr)
        return

    # Get cli_tool and arguments
    cli_tool = cli2rest_config.get("cli_tool")
    arguments = cli2rest_config.get("arguments", [])

    # Prepare input files
    input_files = []
    for input_file_config in cli2rest_config.get("input_files", []):
        relative_path = input_file_config.get("relative_path")
        file_path = input_file

        with open(file_path, "r") as f:
            content = f.read()

        input_files.append({"relative_path": relative_path, "content": content})

    # Get output files
    output_files = cli2rest_config.get("output_files", [])

    # Create the JSON payload
    payload = {
        "cli_tool": cli_tool,
        "arguments": arguments,
        "input_files": input_files,
        "output_files": output_files,
    }

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

    # Process output files from the response
    if "output_files" in result and result["output_files"]:
        # Save each output file
        for output_file in result["output_files"]:
            relative_path = output_file["relative_path"]
            content = output_file["content"]

            # Create the file with tool_name prefix
            prefixed_output_path = os.path.join(
                input_dir, f"{tool_name}-{input_base}-{relative_path}"
            )

            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(prefixed_output_path), exist_ok=True)

            # Write the content
            with open(prefixed_output_path, "w") as f:
                f.write(content)
            print(f"Saved output to: {prefixed_output_path}", file=sys.stderr)
    else:
        # Report error if output_files are not in the response
        print(
            f"Error: No output_files found in response for {input_file}",
            file=sys.stderr,
        )

    # Always create stdout and stderr files
    stdout_path = os.path.join(input_dir, f"{tool_name}-{input_base}-stdout.txt")
    with open(stdout_path, "w") as f:
        f.write(result["stdout"])
    print(f"Saved stdout to: {stdout_path}", file=sys.stderr)

    stderr_path = os.path.join(input_dir, f"{tool_name}-{input_base}-stderr.txt")
    with open(stderr_path, "w") as f:
        f.write(result.get("stderr", ""))
    print(f"Saved stderr to: {stderr_path}", file=sys.stderr)


def main():
    # Check if a tool name was provided
    if len(sys.argv) < 2:
        print(
            "Error: Tool name must be provided as the first argument", file=sys.stderr
        )
        print("Usage: ./cli2rest-bio.py <tool_name> [options]", file=sys.stderr)
        sys.exit(1)

    # Get the tool name from the first argument
    tool_name = sys.argv[1]

    # Remove the tool name from sys.argv to not interfere with argparse
    sys.argv.pop(1)

    # Load the tool configuration
    config = load_tool_config(tool_name)

    # Parse command line arguments
    args = parse_arguments(config, tool_name)

    # Get the input files
    input_files = []
    for input_file in args.input_files:
        # Check if the file exists
        if not os.path.isfile(input_file):
            print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
            sys.exit(1)
        input_files.append(input_file)

    if len(input_files) > 1:
        print(f"Found {len(input_files)} files to process", file=sys.stderr)

    # Start the Docker container
    container, port = start_docker_container(config["docker_image"])

    try:
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = [
                executor.submit(process_file, input_file, config, args, port, tool_name)
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
