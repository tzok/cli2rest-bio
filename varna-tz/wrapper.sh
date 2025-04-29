#! /bin/bash
java -cp /varna-tz.jar pl.poznan.put.varna.AdvancedDrawer input.json
rsvg-convert --format svg --output converted.svg output.svg
svgcleaner converted.svg clean.svg
