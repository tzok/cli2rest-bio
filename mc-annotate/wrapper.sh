#! /bin/bash
exec MC-Annotate ${1:-input.pdb} | tee stdout.txt
