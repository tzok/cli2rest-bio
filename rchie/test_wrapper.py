#!/usr/bin/env python3
"""Unit tests for the colour handling in rchie/wrapper.py.

R only accepts colour names and #rgb/#rgba/#rrggbb/#rrggbbaa. A CSS colour such as
"rgba(0, 0, 0, 0.5)" written straight into the generated script makes plot.xy()
abort with "invalid color name", killing the whole drawing, so the wrapper
normalises colours before building the R script.

Run with: python3 rchie/test_wrapper.py
"""
import importlib.util
import json
import os
import tempfile
import unittest
from unittest.mock import patch

WRAPPER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wrapper.py")


def load_wrapper():
    spec = importlib.util.spec_from_file_location("rchie_wrapper", WRAPPER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


wrapper = load_wrapper()


class ToRColorTest(unittest.TestCase):
    def test_rgba_is_converted_to_eight_digit_hex(self):
        self.assertEqual(wrapper.to_r_color("rgba(0, 0, 0, 0.5)"), "#00000080")

    def test_whitespace_is_tolerated(self):
        self.assertEqual(wrapper.to_r_color("rgba(0,0,0,0.5)"), "#00000080")
        self.assertEqual(wrapper.to_r_color("  rgba(0, 0, 0, 0.5)  "), "#00000080")

    def test_rgb_without_alpha_is_plain_hex(self):
        self.assertEqual(wrapper.to_r_color("rgb(255, 0, 0)"), "#ff0000")

    def test_functional_notation_is_case_insensitive(self):
        self.assertEqual(wrapper.to_r_color("RGB(1, 2, 3)"), "#010203")

    def test_fully_opaque_rgba_drops_the_alpha_channel(self):
        self.assertEqual(wrapper.to_r_color("rgba(255,255,255,1)"), "#ffffff")

    def test_fully_transparent_rgba_keeps_zero_alpha(self):
        self.assertEqual(wrapper.to_r_color("rgba(0,0,0,0)"), "#00000000")

    def test_hex_values_pass_through_unchanged(self):
        for value in ("#000000", "#808080", "#00000080", "#abc", "#abcd", "#AABBCCDD"):
            self.assertEqual(wrapper.to_r_color(value), value)

    def test_colour_names_pass_through_unchanged(self):
        for value in ("red", "dark gray", "NA"):
            self.assertEqual(wrapper.to_r_color(value), value)

    def test_out_of_range_channels_are_rejected(self):
        with self.assertRaises(ValueError):
            wrapper.to_r_color("rgba(300, 0, 0, 0.5)")

    def test_out_of_range_alpha_is_rejected(self):
        with self.assertRaises(ValueError):
            wrapper.to_r_color("rgba(0, 0, 0, 2)")

    def test_malformed_values_are_rejected(self):
        for value in ("#12345", "#GGGGGG", "rgb(0,0)", "", "rgb(1,2,3,4,5)"):
            with self.assertRaises(ValueError):
                wrapper.to_r_color(value)


class LoadJsonDataTest(unittest.TestCase):
    def _load(self, payload):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(payload, handle)
            path = handle.name
        try:
            return wrapper.load_json_data(path)
        finally:
            os.unlink(path)

    def test_colours_are_normalised_on_load(self):
        data = self._load(
            {
                "sequence": "GCAUUGC",
                "top": [{"i": 1, "j": 7, "color": "rgba(0, 0, 0, 0.5)"}],
                "bottom": [],
            }
        )
        self.assertEqual(data["top"][0]["color"], "#00000080")

    def test_absent_and_null_colours_stay_null(self):
        data = self._load(
            {
                "sequence": "GCAUUGC",
                "top": [{"i": 1, "j": 7}, {"i": 2, "j": 6, "color": None}],
                "bottom": [],
            }
        )
        # absent key stays absent; it is read with .get() downstream
        self.assertNotIn("color", data["top"][0])
        self.assertIsNone(data["top"][1]["color"])

    def test_invalid_colour_is_reported_before_runs(self):
        with self.assertRaises(ValueError):
            self._load(
                {
                    "sequence": "GCAUUGC",
                    "top": [{"i": 1, "j": 7, "color": "not-a-real-color()"}],
                    "bottom": [],
                }
            )

    def test_non_string_colour_is_rejected(self):
        with self.assertRaises(ValueError):
            self._load(
                {
                    "sequence": "GCAUUGC",
                    "top": [{"i": 1, "j": 7, "color": 123}],
                    "bottom": [],
                }
            )


class GeneratedScriptTest(unittest.TestCase):
    """Checks the R script that would be written, without running R."""

    def _generated_script(self, payload):
        written = {}

        def fake_run(cmd, **_kwargs):
            with open(cmd[1], encoding="utf-8") as handle:
                written["script"] = handle.read()
            raise RuntimeError("stop before R")

        with tempfile.TemporaryDirectory() as directory:
            previous = os.getcwd()
            os.chdir(directory)
            try:
                with patch.object(wrapper.subprocess, "run", side_effect=fake_run):
                    try:
                        wrapper.process_rchie_data(payload)
                    except RuntimeError:
                        pass
            finally:
                os.chdir(previous)

        return written.get("script", "")

    def test_css_colour_never_reaches_the_r_script(self):
        script = self._generated_script(
            {
                "sequence": "GCAUUGC",
                "title": "",
                "top": [{"i": 1, "j": 7, "color": "rgb(128, 128, 128)"}],
                "bottom": [{"i": 2, "j": 6, "color": "rgba(0, 0, 0, 0.5)"}],
            }
        )

        self.assertNotIn("rgba(", script)
        self.assertNotIn("rgb(", script)
        self.assertIn('"#808080"', script)
        self.assertIn('"#00000080"', script)


if __name__ == "__main__":
    unittest.main(verbosity=2)
