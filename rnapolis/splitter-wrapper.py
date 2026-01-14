#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import tarfile

# Attempt to import main from rnapolis.splitter
try:
    from rnapolis.splitter import main as splitter_main
except ImportError:
    print("Error: Could not import 'main' from 'rnapolis.splitter'.")
    print("Please ensure RNAPOLIS is installed correctly.")
    sys.exit(1)


def create_output_archive(output_dir, archive_name):
    """Creates a tar.gz archive from the contents of the output directory."""
    print(f"Creating output archive: {archive_name}")
    # Use subprocess to handle tar creation to easily exclude the parent directory
    # from paths inside the archive.
    try:
        # Check if output directory is empty or doesn't exist
        if not os.path.isdir(output_dir) or not os.listdir(output_dir):
            print(
                f"Warning: Output directory '{output_dir}' is empty or does not exist. Creating an empty archive."
            )
            # Create an empty tar.gz file
            with tarfile.open(archive_name, "w:gz") as tar:
                pass  # Creates an empty archive
            print(f"Created empty archive: {archive_name}")
            return

        # Use tar command via subprocess
        # -C changes directory before adding files
        # . refers to all files in that directory
        command = ["tar", "-czf", os.path.abspath(archive_name), "-C", output_dir, "."]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Successfully created archive: {archive_name}")
        if result.stdout:
            print("tar stdout:", result.stdout)
        if result.stderr:
            print("tar stderr:", result.stderr)
    except FileNotFoundError:
        print("Error: 'tar' command not found. Cannot create output archive.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error creating archive '{archive_name}':")
        print(e.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during archive creation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Wrapper script to run rnapolis.splitter on a PDB/CIF file."
    )
    parser.add_argument(
        "input_file",
        help="Path to the input PDB/CIF file to process.",
    )
    parser.add_argument(
        "--format", help="Optional format argument passed to rnapolis.splitter."
    )
    args = parser.parse_args()

    input_file_path = args.input_file
    output_dir_name = "output"
    output_archive_name = "output.tar.gz"

    # --- 1. Check if input file exists ---
    if not os.path.isfile(input_file_path):
        print(f"Error: Input file '{input_file_path}' not found.")
        sys.exit(1)

    # --- 2. Create output directory ---
    os.makedirs(output_dir_name, exist_ok=True)
    print(f"Ensured output directory exists: {output_dir_name}")

    # --- 3. Prepare arguments for rnapolis.splitter.main ---
    splitter_args = []
    if args.format:
        splitter_args.extend(["--format", args.format])
    splitter_args.extend(["--output", output_dir_name])
    splitter_args.append(input_file_path)  # Add the input file

    print(f"Calling rnapolis.splitter with args: {splitter_args}")

    # --- 4. Call rnapolis.splitter.main ---
    # We need to modify sys.argv as rnapolis.splitter.main likely uses argparse internally
    original_argv = sys.argv
    sys.argv = ["rnapolis.splitter"] + splitter_args  # Simulate command line call
    try:
        splitter_main()
        print("rnapolis.splitter processing finished.")
    except SystemExit as e:
        # Allow clean exits (e.g., from argparse --help)
        # but report errors otherwise.
        if e.code != 0:
            print(f"rnapolis.splitter exited with code {e.code}")
            # Potentially exit the wrapper too, depending on desired behavior
            # sys.exit(e.code) # Uncomment to propagate exit code
        else:
            print("rnapolis.splitter exited cleanly.")
    except Exception as e:
        print(f"An error occurred while running rnapolis.splitter: {e}")
        # Decide if the wrapper should exit with an error
        # sys.exit(1) # Uncomment to exit wrapper on splitter error
    finally:
        sys.argv = original_argv  # Restore original sys.argv

    # --- 5. Create output archive ---
    create_output_archive(output_dir_name, output_archive_name)

    print("Wrapper script finished.")
