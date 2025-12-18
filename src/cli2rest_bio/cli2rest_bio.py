#!/usr/bin/env python3
import argparse
import gzip
import importlib.resources
from importlib.resources.abc import Traversable
import json
import os
import sys
import time
from typing import Any, BinaryIO, Dict, List, Tuple, Union
import uuid
from concurrent.futures import ThreadPoolExecutor
from email import message_from_bytes
from pathlib import Path

import docker
import docker.models
import docker.models.containers
import requests
import yaml


def load_tool_config(config_path: str):
    """
    Load the YAML configuration.

    Tries to load from the path relative to the current working directory first.
    If not found, falls back to loading from the package's 'configs' directory.
    Handles both direct file paths and directory paths (looking for config.yaml/yml).
    """
    # Define candidates as (path_object, description)
    candidates: List[Tuple[Path | Traversable, str]] = []

    # 1. Local filesystem candidates
    local_base = Path(config_path).resolve()
    candidates.append((local_base, f"local file ({local_base})"))
    candidates.append(
        (local_base / "config.yaml", f"local directory ({local_base}/config.yaml)")
    )
    candidates.append(
        (local_base / "config.yml", f"local directory ({local_base}/config.yml)")
    )

    # 2. Package resource candidates
    try:
        package_base = importlib.resources.files("cli2rest_bio.configs").joinpath(
            config_path
        )
        candidates.append((package_base, f"package resource file ({config_path})"))
        candidates.append(
            (
                package_base / "config.yaml",
                f"package resource directory ({config_path}/config.yaml)",
            )
        )
        candidates.append(
            (
                package_base / "config.yml",
                f"package resource directory ({config_path}/config.yml)",
            )
        )
    except (ModuleNotFoundError, FileNotFoundError):
        pass

    for path, description in candidates:
        try:
            if path.is_file():
                with path.open("r") as f:
                    config = yaml.safe_load(f)

                if not config or "name" not in config:
                    print(
                        f"Error: Configuration from {description} must contain a 'name' field",
                        file=sys.stderr,
                    )
                    sys.exit(1)

                print(f"Configuration loaded from: {description}", file=sys.stderr)
                return config
        except (FileNotFoundError, NotADirectoryError, PermissionError):
            continue
        except Exception as e:
            print(
                f"Error reading configuration from {description}: {e}", file=sys.stderr
            )
            sys.exit(1)

    print(
        f"Error: Configuration '{config_path}' not found locally or in package resources.",
        file=sys.stderr,
    )
    sys.exit(1)


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
        "--output-dir",
        type=str,
        help="Directory to save output files. If not provided, outputs are saved next to input files.",
    )

    parser.add_argument(
        "--output-prefix-format",
        type=str,
        default="{tool_name}-{input_base}-",
        help="Format string for output file prefixes. Available placeholders: {tool_name}, {input_base}. Default: '{tool_name}-{input_base}-'",
    )

    parser.add_argument(
        "--api-url",
        type=str,
        help="REST API URL endpoint (e.g., http://localhost:8000). If provided, no Docker container will be created.",
    )

    parser.add_argument(
        "--no-auto-ungzip",
        action="store_true",
        help="Disable automatic ungzipping of .gz input files (enabled by default)",
    )

    parser.add_argument(
        "--output-metadata",
        type=str,
        help="Path to save the metadata JSON from the response (minified).",
    )

    # Add config file and input files as positional arguments
    parser.add_argument(
        "config_and_input_files",
        nargs="+",
        help="Config file path followed by input file(s) to process",
    )

    return parser.parse_args()


def start_docker_container(
    docker_image: str,
) -> Tuple[docker.models.containers.Container, str]:
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
    except Exception:
        print(f"Pulling image {docker_image}...", file=sys.stderr)
        client.images.pull(docker_image)

    # Start the container with a random port
    container: docker.models.containers.Container = client.containers.run(
        docker_image,
        name=container_name,
        detach=True,
        ports={"8000/tcp": None},  # Assign a random port
    )

    # Get the port that Docker assigned
    container_id = str(container.id)
    container_info = client.containers.get(container_id)
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


def stop_docker_container(container: docker.models.containers.Container):
    """Stop and remove the Docker container."""
    print("Cleaning up...", file=sys.stderr)

    # Stop and remove the container
    container.stop()
    container.remove()


def process_file(
    input_file: str,
    config: Dict[str, Any],
    args: argparse.Namespace,
    base_url: str,
    tool_name: str,
    output_dir_base: str,
):
    """Process a single input file using the specified tool configuration."""
    # Get file information
    input_base = os.path.splitext(os.path.basename(input_file))[0]
    # Determine the effective output directory
    effective_output_dir = output_dir_base or os.path.dirname(
        os.path.abspath(input_file)
    )

    # Format the output prefix
    output_prefix = args.output_prefix_format.format(
        tool_name=tool_name, input_base=input_base
    )

    print(f"Processing file: {input_file}", file=sys.stderr)

    # Get configuration directly from the YAML
    # Get the full arguments list (including the tool command)
    full_arguments = config.get("arguments", [])
    if not full_arguments:
        print("Error: No arguments specified in configuration", file=sys.stderr)
        return

    # Prepare input files for the 'files' parameter
    files_to_upload: Dict[str, Tuple[str, Union[BinaryIO, gzip.GzipFile]]] = {}

    # Get the input file path from config
    input_file_config_path = config.get("input_file")
    if input_file_config_path:
        try:
            file_object: Union[BinaryIO, gzip.GzipFile]
            # Check if we need to ungzip the file
            if not args.no_auto_ungzip and input_file.endswith(".gz"):
                print(f"Streaming ungzipped {input_file}...", file=sys.stderr)
                file_object = gzip.open(input_file, "rb")
            else:
                file_object = open(input_file, "rb")

            # Use the field name expected by the FastAPI server ("input_files")
            # and pass the configured filename within the tuple.
            files_to_upload["input_files"] = (input_file_config_path, file_object)
        except FileNotFoundError:
            print(f"Error: Input file {input_file} not found.", file=sys.stderr)
            return
        except Exception as e:
            print(f"Error opening input file {input_file}: {e}", file=sys.stderr)
            return
    else:
        print("Error: No input_file specified in configuration", file=sys.stderr)
        return

    # Get expected output file names
    output_file_names = config.get("output_files", [])

    # Prepare form data
    form_data = {
        "arguments": tuple(full_arguments),  # Send arguments as a tuple/list
        "output_files": tuple(
            output_file_names
        ),  # Send output file names as tuple/list
    }

    # Send the request to the API endpoint using multipart/form-data
    try:
        response = requests.post(
            f"{base_url}/run-command",
            data=form_data,
            files=files_to_upload,
        )
    finally:
        # Ensure uploaded files are closed
        for _, f in files_to_upload.values():
            f.close()

    if response.status_code != 200:
        print(f"Error processing {input_file}: {response.text}", file=sys.stderr)
        if args.output_metadata:
            error_metadata: Dict[str, Any] = {
                "status": "CLI2REST-FAILED",
                "http_code": response.status_code,
                "http_message": response.reason,
                "exit_code": None,
                "missing_files": output_file_names,
                "execution_stats": {
                    "start_time": None,
                    "end_time": None,
                    "duration_seconds": None,
                    "max_rss_kb": None,
                    "cpu_user_seconds": None,
                },
                "stdout": None,
                "stderr": None,
                "command": full_arguments,
            }
            try:
                with open(args.output_metadata, "w") as f:
                    json.dump(error_metadata, f, separators=(",", ":"))
            except IOError as e:
                print(f"Error writing metadata file: {e}", file=sys.stderr)
        return

    # Parse the multipart response
    raw_message = (
        f"Content-Type: {response.headers.get('Content-Type')}\r\n\r\n".encode()
        + response.content
    )
    msg = message_from_bytes(raw_message)

    result: Dict[str, Any] = {}
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        disposition = part.get("Content-Disposition", "")

        if 'name="metadata"' in disposition:
            payload = part.get_payload(decode=True)
            if isinstance(payload, bytes):
                result = json.loads(payload.decode("utf-8"))
        elif "filename=" in disposition:
            filename = part.get_filename()
            payload = part.get_payload(decode=True)
            if not isinstance(payload, bytes):
                continue
            content_bytes = payload

            # Create the file path with the formatted prefix
            prefixed_output_path = os.path.join(
                effective_output_dir, f"{output_prefix}{filename}"
            )
            os.makedirs(os.path.dirname(prefixed_output_path), exist_ok=True)

            try:
                with open(prefixed_output_path, "wb") as f:
                    f.write(content_bytes)
                print(f"Saved output to: {prefixed_output_path}", file=sys.stderr)
            except IOError as e:
                print(
                    f"Error writing output file {prefixed_output_path}: {e}",
                    file=sys.stderr,
                )

    if not result:
        print(
            f"Error: No metadata found in response for {input_file}",
            file=sys.stderr,
        )
        if args.output_metadata:
            error_metadata: Dict[str, Any] = {
                "status": "CLI2REST-FAILED",
                "http_code": response.status_code,
                "http_message": "No metadata in multipart response",
                "exit_code": None,
                "missing_files": output_file_names,
                "execution_stats": {
                    "start_time": None,
                    "end_time": None,
                    "duration_seconds": None,
                    "max_rss_kb": None,
                    "cpu_user_seconds": None,
                },
                "stdout": None,
                "stderr": None,
                "command": full_arguments,
            }
            try:
                with open(args.output_metadata, "w") as f:
                    json.dump(error_metadata, f, separators=(",", ":"))
            except IOError as e:
                print(f"Error writing metadata file: {e}", file=sys.stderr)
        return

    if args.output_metadata:
        try:
            with open(args.output_metadata, "w") as f:
                json.dump(result, f, separators=(",", ":"))
        except IOError as e:
            print(f"Error writing metadata file: {e}", file=sys.stderr)

    if result.get("status") != "COMPLETED":
        print(
            f"API returned status {result.get('status')} for {input_file}",
            file=sys.stderr,
        )


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
    # The load_tool_config function now prints where it loaded from

    # Get the input files (all arguments after the first one)
    input_files: List[str] = []
    for input_file in args.config_and_input_files[1:]:
        # Check if the file exists
        if not os.path.isfile(input_file):
            print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
            sys.exit(1)
        input_files.append(input_file)

    # Determine if we're using an external API or starting a Docker container
    container = None
    base_url: str = args.api_url

    # Create output directory if specified and it doesn't exist
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        print(f"Output directory set to: {args.output_dir}", file=sys.stderr)

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
                    process_file,
                    input_file,
                    config,
                    args,
                    base_url,
                    tool_name,
                    args.output_dir,
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
