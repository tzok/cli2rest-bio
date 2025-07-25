#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
from typing import Any, Dict, List, Optional, TypedDict


class Interaction(TypedDict):
    i: int
    j: int
    color: Optional[str]


class RchieData(TypedDict):
    sequence: str
    title: Optional[str]  # New optional title field
    top: List[Interaction]
    bottom: List[Interaction]


def load_json_data(file_path: str) -> RchieData:
    """Loads and validates R-CHIE JSON data from a file."""
    try:
        with open(file_path, "r") as f:
            data: RchieData = json.load(f)
        # Basic validation (can be expanded)
        if "sequence" not in data or not isinstance(data["sequence"], str):
            raise ValueError("Missing or invalid 'sequence' in JSON data.")
        if "title" in data and not isinstance(data["title"], str):
            raise ValueError("Invalid 'title' in JSON data, must be a string.")
        if "top" not in data or not isinstance(data["top"], list):
            raise ValueError("Missing or invalid 'top' interactions in JSON data.")
        if "bottom" not in data or not isinstance(data["bottom"], list):
            raise ValueError("Missing or invalid 'bottom' interactions in JSON data.")

        # Validate 'i' and 'j' in interactions
        for interaction_list_name in ["top", "bottom"]:
            interaction_list = data[interaction_list_name]
            for idx, interaction in enumerate(interaction_list):
                if not isinstance(interaction, dict):
                    raise ValueError(
                        f"Invalid interaction at {interaction_list_name}[{idx}], must be an object."
                    )
                i_val = interaction.get("i")
                j_val = interaction.get("j")
                # color_val = interaction.get("color") # Optional, can be None or string

                if not isinstance(i_val, int) or i_val <= 0:
                    raise ValueError(
                        f"Interaction {interaction_list_name}[{idx}] has invalid 'i' value: {i_val}. Must be a positive integer."
                    )
                if not isinstance(j_val, int) or j_val <= 0:
                    raise ValueError(
                        f"Interaction {interaction_list_name}[{idx}] has invalid 'j' value: {j_val}. Must be a positive integer."
                    )
                # Optional: Validate color if specific constraints exist, e.g., must be string if not None.
                # if color_val is not None and not isinstance(color_val, str):
                #     raise ValueError(
                #         f"Interaction {interaction_list_name}[{idx}] has invalid 'color' value: {color_val}. Must be a string or null."
                #     )
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        raise
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}")
        raise
    except ValueError as ve:
        print(f"Error: Invalid JSON data structure: {ve}")
        raise


def main() -> None:
    """Main function to parse arguments and process R-CHIE data."""
    parser = argparse.ArgumentParser(description="R-CHIE wrapper script.")
    parser.add_argument(
        "json_file", type=str, help="Path to the input JSON file for R-CHIE."
    )
    args = parser.parse_args()

    try:
        rchie_data = load_json_data(args.json_file)
        # At this point, rchie_data contains the parsed JSON.
        print(f"Successfully loaded R-CHIE data for sequence: {rchie_data['sequence']}")
        process_rchie_data(rchie_data)
        print("Successfully processed R-CHIE data and generated output files.")
    except Exception as e:
        # Errors from load_json_data are already printed if they occur there
        print(f"Processing failed: {e}")
        # Exit with a non-zero status code to indicate failure
        exit(1)


def process_rchie_data(rchie_data: RchieData) -> None:
    """Processes RchieData to generate color mappings and output files."""
    all_colors: List[Optional[str]] = []
    for interaction in rchie_data["top"]:
        all_colors.append(interaction.get("color"))
    for interaction in rchie_data["bottom"]:
        all_colors.append(interaction.get("color"))

    # Create a list of unique colors while preserving the order of first appearance
    unique_colors_ordered = list(dict.fromkeys(all_colors))

    color_to_int_map: Dict[Optional[str], int] = {
        color: i for i, color in enumerate(unique_colors_ordered)
    }

    # Prepare interaction lists for direct R data.frame creation
    top_i_list = [interaction["i"] for interaction in rchie_data["top"]]
    top_j_list = [interaction["j"] for interaction in rchie_data["top"]]
    top_val_list = [
        f'"{interaction.get("color")}"'
        if interaction.get("color") is not None
        else "NA"
        for interaction in rchie_data["top"]
    ]
    bottom_i_list = [interaction["i"] for interaction in rchie_data["bottom"]]
    bottom_j_list = [interaction["j"] for interaction in rchie_data["bottom"]]
    bottom_val_list = [
        f'"{interaction.get("color")}"'
        if interaction.get("color") is not None
        else "NA"
        for interaction in rchie_data["bottom"]
    ]

    # Create integer‐based value lists for R
    top_val_list_int = [
        str(color_to_int_map[interaction.get("color")])
        for interaction in rchie_data["top"]
    ]
    bottom_val_list_int = [
        str(color_to_int_map[interaction.get("color")])
        for interaction in rchie_data["bottom"]
    ]

    sequence = rchie_data["sequence"]
    # Use title for FASTA header, default to "sequence" if not present or empty
    fasta_header = rchie_data.get("title") or "sequence"
    output_pdf_path = "rchie_output.pdf"  # Output PDF file path

    r_script_lines = [
        "library(R4RNA)",
        "library(Biostrings)",
        "",
        # Embed sequence and header directly
        f'sequence_str <- "{sequence}"',
        f'fasta_header_str <- "{fasta_header}"',
        "fasta_data <- Biostrings::BStringSet(setNames(sequence_str, fasta_header_str))",
        "sequence_name <- names(fasta_data)[1]",  # This will pick up fasta_header_str
        "",
        # Hardcode the output PDF path for R
        f'output_pdf_r_path <- "{output_pdf_path}"',
        "",
        "# Construct helix1 directly from interaction lists",
        f"i_top <- c({','.join(str(i) for i in top_i_list)})",
        f"j_top <- c({','.join(str(j) for j in top_j_list)})",
        f"val_top <- c({','.join(top_val_list_int)})",
        f"helix1 <- data.frame(i = i_top, j = j_top, length = rep(1L, length(i_top)), value = val_top)",
        f"helix1 <- as.helix(helix1, {len(sequence)})",
        # helix1$col assignments replaced by dynamic mapping below
        "",
        "# Construct helix2 directly from interaction lists",
        f"i_bottom <- c({','.join(str(i) for i in bottom_i_list)})",
        f"j_bottom <- c({','.join(str(j) for j in bottom_j_list)})",
        f"val_bottom <- c({','.join(bottom_val_list_int)})",
        f"helix2 <- data.frame(i = i_bottom, j = j_bottom, length = rep(1L, length(i_bottom)), value = val_bottom)",
        f"helix2 <- as.helix(helix2, {len(sequence)})",
        # helix2$col assignments replaced by dynamic mapping below
        "",
    ]

    # Initialize col vector for helix1 and helix2 before conditional assignment
    r_script_lines.append(f"helix1$col <- rep(NA_character_, nrow(helix1))")
    r_script_lines.append(f"helix2$col <- rep(NA_character_, nrow(helix2))")

    # Assign colors in R based on integer ‘value’
    for color, idx in color_to_int_map.items():
        if color is not None:
            r_script_lines.append(
                f'helix1$col[which(helix1$value=={idx})] <- "{color}"'
            )
            r_script_lines.append(
                f'helix2$col[which(helix2$value=={idx})] <- "{color}"'
            )
    r_script_lines.extend(
        [
            "",
            "# Prepare sequence for plotting (extracting from BStringSet)",
            "sequence_for_plot <- as.character(fasta_data[[1]])",
            "",
            # Use the hardcoded PDF path variable
            "plotDoubleCovariance(helix1, helix2, top.msa=sequence_for_plot, bot.msa=NA, main.title=sequence_name, add=FALSE, grid=TRUE, legend=FALSE, scale=FALSE, text=TRUE, lwd=3, pdf=output_pdf_r_path)",
            "",
            "print(paste('Generated PDF:', output_pdf_r_path))",
        ]
    )

    r_script_content = "\n".join(r_script_lines)
    r_script_file_path = "rchie_script.R"

    try:
        # Create R script file
        with open(r_script_file_path, "w", encoding="utf-8") as r_script_file:
            r_script_file.write(r_script_content)
        print(f"Generated R script file: {r_script_file_path}")

        cmd = [
            "Rscript",
            r_script_file_path,
            # No more file paths as arguments
        ]

        print(f"Executing R script: {' '.join(cmd)}")
        # Use check=True to raise CalledProcessError on non-zero exit code
        process = subprocess.run(cmd, capture_output=True, text=True, check=True)

        print("R script executed successfully.")
        print("R Script Stdout:")
        print(process.stdout)
        if process.stderr:  # Stderr might contain warnings even on success
            print("R Script Stderr (warnings/info):")
            print(process.stderr)
        print(f"Output PDF generated at: {output_pdf_path}")

        # Convert PDF to SVG
        svg_path = output_pdf_path.replace(".pdf", ".svg")
        print(f"Converting PDF {output_pdf_path} to SVG {svg_path}...")
        pdftosvg_cmd = ["pdftocairo", "-svg", output_pdf_path, svg_path]
        process_pdftosvg = subprocess.run(
            pdftosvg_cmd, capture_output=True, text=True, check=True
        )
        print(f"pdftosvg Stdout:\n{process_pdftosvg.stdout}")
        if process_pdftosvg.stderr:
            print(f"pdftosvg Stderr:\n{process_pdftosvg.stderr}")
        print(f"SVG generated at: {svg_path}")

        # Clean SVG using svgcleaner
        cleaned_svg_path = "clean.svg"  # Changed to fixed name
        print(f"Cleaning SVG {svg_path} to {cleaned_svg_path}...")
        svgcleaner_cmd = ["svgcleaner", svg_path, cleaned_svg_path]
        process_svgcleaner = subprocess.run(
            svgcleaner_cmd, capture_output=True, text=True, check=True
        )
        print(f"svgcleaner Stdout:\n{process_svgcleaner.stdout}")
        if process_svgcleaner.stderr:
            print(f"svgcleaner Stderr:\n{process_svgcleaner.stderr}")
        print(f"Cleaned SVG generated at: {cleaned_svg_path}")
        print(f"Final output SVG is available at: {cleaned_svg_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error during subprocess execution ({' '.join(e.cmd)}):")
        print(f"Command: {' '.join(e.cmd)}")
        print(f"Return code: {e.returncode}")
        print("Stdout:")
        print(e.stdout)
        print("Stderr:")
        print(e.stderr)
        # Re-raise as a generic RuntimeError to be caught by main's handler
        raise RuntimeError("R script execution failed.") from e
    except Exception as e:
        # Catch any other unexpected errors during file operations or script prep
        print(f"An unexpected error occurred before or during R script execution: {e}")
        raise  # Re-raise to be caught by main's handler


if __name__ == "__main__":
    main()
