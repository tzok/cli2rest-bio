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


def load_tool_config(config_path):
    """Load the YAML configuration from the specified path."""
    # If config_path is a directory, look for config.yaml or config.yml
    if os.path.isdir(config_path):
        yaml_path = os.path.join(config_path, "config.yaml")
        yml_path = os.path.join(config_path, "config.yml")
        
        if os.path.exists(yaml_path):
            config_path = yaml_path
        elif os.path.exists(yml_path):
            config_path = yml_path
        else:
            print(
                f"Error: No config.yaml or config.yml found in directory {config_path}",
                file=sys.stderr,
            )
            sys.exit(1)
    
    if not os.path.exists(config_path):
        print(
            f"Error: Configuration file not found at {config_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Ensure the config has a name field
    if "name" not in config:
        print(
            f"Error: Configuration file must contain a 'name' field",
            file=sys.stderr,
        )
        sys.exit(1)

    return config


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="cli2rest-bio.py",
    )

    # Add common arguments
    parser.add_argument(
        "--threads",
        type=int,
        default=os.cpu_count(),
        help="Number of parallel threads to use",
    )

    parser.add_argument(
        "--api-url",
        type=str,
        help="REST API URL endpoint (e.g., http://localhost:8000). If provided, no Docker container will be created.",
    )

    # Add config file and input files as positional arguments
    parser.add_argument(
        "config_and_input_files",
        nargs="+",
        help="Config file path followed by input file(s) to process",
    )

    return parser.parse_args()


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


def process_file(input_file, config, args, base_url, tool_name):
    """Process a single input file using the specified tool configuration."""
    # Get file information
    input_base = os.path.splitext(os.path.basename(input_file))[0]
    input_dir = os.path.dirname(input_file)

    print(f"Processing file: {input_file}", file=sys.stderr)

    # Get configuration directly from the YAML
    # Get cli_tool and arguments
    cli_tool = config.get("cli_tool")
    if not cli_tool:
        print(f"Error: No cli_tool specified in configuration", file=sys.stderr)
        return

    arguments = config.get("arguments", [])

    # Prepare input files
    input_files = []
    # Get the input file path from config
    input_file_path = config.get("input_file")
    if input_file_path:
        with open(input_file, "r") as f:
            content = f.read()

        input_files.append({"relative_path": input_file_path, "content": content})
    else:
        print(f"Error: No input_file specified in configuration", file=sys.stderr)
        return

    # Get output files
    output_files = config.get("output_files", [])

    # Create the JSON payload
    payload = {
        "cli_tool": cli_tool,
        "arguments": arguments,
        "input_files": input_files,
        "output_files": output_files,
    }

    # Send the request to the API endpoint
    response = requests.post(
        f"{base_url}/run-command",
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
    # Parse command line arguments
    args = parse_arguments()

    # Ensure we have at least a config file and one input file
    if len(args.config_and_input_files) < 2:
        print(
            "Error: You must provide a config file path and at least one input file",
            file=sys.stderr,
        )
        sys.exit(1)

    # First argument is the config file path
    config_path = args.config_and_input_files[0]

    # Load the tool configuration
    config = load_tool_config(config_path)

    # Get the tool name from the config
    tool_name = config["name"]

    print(f"Using tool: {tool_name}", file=sys.stderr)
    print(f"Configuration loaded from: {config_path}", file=sys.stderr)

    # Get the input files (all arguments after the first one)
    input_files = []
    for input_file in args.config_and_input_files[1:]:
        # Check if the file exists
        if not os.path.isfile(input_file):
            print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
            sys.exit(1)
        input_files.append(input_file)

    # Determine if we're using an external API or starting a Docker container
    container = None
    base_url = args.api_url

    if base_url:
        # Using external API
        print(f"Using external API at: {base_url}", file=sys.stderr)
        # Remove trailing slash if present
        base_url = base_url.rstrip("/")
        port = None  # Not needed when using external API
    else:
        # Start the Docker container
        container, port = start_docker_container(config["docker_image"])
        base_url = f"http://localhost:{port}"

    try:
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = [
                executor.submit(
                    process_file, input_file, config, args, base_url, tool_name
                )
                for input_file in input_files
            ]

            # Wait for all tasks to complete
            for future in futures:
                future.result()

    finally:
        # Clean up - stop and remove the container if we created one
        if container:
            stop_docker_container(container)

    print("Done!", file=sys.stderr)


if __name__ == "__main__":
    main()
