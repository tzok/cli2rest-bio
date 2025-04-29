#! /bin/bash
java -cp /varna-tz.jar pl.poznan.put.varna.AdvancedDrawer input.json
svgcleaner output.svg clean.svg
