# Barnaba - Analyse Nucleic Acids Structure and Simulations

Barnaba is a tool for analyzing RNA three-dimensional structures and simulations. This container provides a REST API interface to Barnaba's annotation capabilities.

## About Barnaba

Barnaba is developed by Sandro Bottaro with the crucial help of Giovanni Bussi, Giovanni Pinamonti, Sabine Reißer and Wouter Boomsma. It uses MDtraj to read/write topology and trajectory files, supporting several formats including pdb, xtc, trr, dcd, binpos, netcrf, mdcrd, prmtop, and more.

Key features include:
- Calculate eRMSD
- Calculate RMSD after optimal alignment
- Search for single/double stranded RNA motifs
- Annotate PDB structures with the Leontis-Westhof classification
- Produce dynamic secondary structure figures in SVG format
- Cluster nucleic acids structures using eRMSD as metric distance
- Calculate elastic network models
- Calculate backbone and pucker torsion angles
- Back-calculate 3J scalar couplings
- Score three-dimensional structures using eSCORE

## Usage

### Using the `cli2rest-bio` Tool

The recommended way to use this container is with the `cli2rest-bio` command-line tool provided in the main repository:

```bash
# Annotate a PDB file
cli2rest-bio barnaba/config.yaml your_structure.pdb

# Process multiple PDB files
cli2rest-bio barnaba/config.yaml *.pdb
```

This tool handles starting the container, sending requests according to `barnaba/config.yaml`, saving outputs (prefixed with `barnaba-`), and cleaning up. See the main [README.md](../README.md) for more details on `cli2rest-bio`.

### Using the REST API Directly

You can also interact with the API directly:

```bash
# Start the container
docker run -p 8000:8000 ghcr.io/tzok/cli2rest-barnaba:latest

# Send a request using form data
# Corresponds to barnaba/config.yaml

curl -X POST http://localhost:8000/run-command \
  -F 'arguments=barnaba' \
  -F 'arguments=ANNOTATE' \
  -F 'arguments=--pdb' \
  -F 'arguments=input.pdb' \
  -F 'input_files=@path/to/your_structure.pdb;filename=input.pdb'
```

## Output Format

The `cli2rest-bio` tool saves the following output files (prefixed with `barnaba-<input_base_name>-`):

- `stdout.txt`: Standard output from barnaba containing the annotation results
- `stderr.txt`: Standard error from barnaba

The API response itself contains the `stdout`, `stderr`, `exit_code`. The annotation results will be in the stdout field. Example snippet of the JSON response:

```json
{
  "exit_code": 0,
  "stdout": "# Barnaba annotation results...",
  "stderr": "",
  "output_files": []
}
```

## Building the Container

To build the container locally:

```bash
docker build -t cli2rest-barnaba .
```

## References

- [Barnaba GitHub Repository](https://github.com/srnas/barnaba)
- [Barnaba Paper](https://rnajournal.cshlp.org/content/25/2/219): Bottaro, Sandro, et al. "Barnaba: software for analysis of nucleic acid structures and trajectories." RNA 25.2 (2019): 219-231.
