#!/usr/bin/env python3

import os
import argparse
import glob
import tarfile
import sys
import subprocess

# Attempt to import main from rnapolis.unifier
try:
    from rnapolis.unifier import main as unifier_main
except ImportError:
    print("Error: Could not import 'main' from 'rnapolis.unifier'.")
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
             print(f"Warning: Output directory '{output_dir}' is empty or does not exist. Creating an empty archive.")
             # Create an empty tar.gz file
             with tarfile.open(archive_name, "w:gz") as tar:
                 pass # Creates an empty archive
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
        description="Wrapper script to run rnapolis.unifier on an archive of PDB/CIF files."
    )
    parser.add_argument(
        "input_archive", help="Path to the input .tar.gz archive containing PDB/CIF files."
    )
    parser.add_argument(
        "--format", help="Optional format argument passed to rnapolis.unifier."
    )
    args = parser.parse_args()

    input_archive_path = args.input_archive
    output_dir_name = "output"
    output_archive_name = "output.tar.gz"

    # --- 1. Extract the input archive ---
    print(f"Extracting archive: {input_archive_path}")
    try:
        with tarfile.open(input_archive_path, "r:gz") as tar:
            tar.extractall(path=".")
        print("Extraction complete.")
    except tarfile.ReadError:
        print(f"Error: '{input_archive_path}' is not a valid tar.gz file.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Input archive '{input_archive_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during extraction: {e}")
        sys.exit(1)


    # --- 2. Create output directory ---
    os.makedirs(output_dir_name, exist_ok=True)
    print(f"Ensured output directory exists: {output_dir_name}")

    # --- 3. Collect PDB and CIF files ---
    # Search in the current directory after extraction
    pdb_files = glob.glob("*.pdb")
    cif_files = glob.glob("*.cif")
    input_files = pdb_files + cif_files
    print(f"Found {len(input_files)} PDB/CIF files for processing.")
    if not input_files:
        print("Warning: No PDB or CIF files found after extraction.")
        # Create an empty output archive and exit cleanly
        create_output_archive(output_dir_name, output_archive_name)
        print("Exiting as there are no files to process.")
        sys.exit(0)


    # --- 4. Prepare arguments for rnapolis.unifier.main ---
    unifier_args = []
    if args.format:
        unifier_args.extend(["--format", args.format])
    unifier_args.extend(["--output", output_dir_name])
    unifier_args.extend(input_files) # Add the list of files

    print(f"Calling rnapolis.unifier with args: {unifier_args}")

    # --- 5. Call rnapolis.unifier.main ---
    # We need to modify sys.argv as rnapolis.unifier.main likely uses argparse internally
    original_argv = sys.argv
    sys.argv = ["rnapolis.unifier"] + unifier_args # Simulate command line call
    try:
        unifier_main()
        print("rnapolis.unifier processing finished.")
    except SystemExit as e:
         # Allow clean exits (e.g., from argparse --help)
         # but report errors otherwise.
         if e.code != 0:
             print(f"rnapolis.unifier exited with code {e.code}")
             # Potentially exit the wrapper too, depending on desired behavior
             # sys.exit(e.code) # Uncomment to propagate exit code
         else:
             print("rnapolis.unifier exited cleanly.")
    except Exception as e:
        print(f"An error occurred while running rnapolis.unifier: {e}")
        # Decide if the wrapper should exit with an error
        # sys.exit(1) # Uncomment to exit wrapper on unifier error
    finally:
        sys.argv = original_argv # Restore original sys.argv


    # --- 6. Create output archive ---
    create_output_archive(output_dir_name, output_archive_name)

    print("Wrapper script finished.")
