#! /bin/bash
java -cp /varna-tz.jar pl.poznan.put.varna.AdvancedDrawer input.json
inkscape output.svg --export-area-drawing --export-filename=converted.svg
svgcleaner converted.svg clean.svg
