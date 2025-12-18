#! /bin/bash
exec reduce ${1:-input.pdb} | tee output.pdb
