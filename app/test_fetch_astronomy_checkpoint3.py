from __future__ import annotations

import unittest

import fetch_astronomy


class TestCheckpoint3Mapping(unittest.TestCase):
    def test_extract_summary_fields_maps_expected_keys(self) -> None:
        payload = {
            "moon_phase": "Waning Crescent",
            "moon_altitude": "-22.5",
            "sunset": "18:14",
            "moonrise": "04:07",
            "other": "ignored",
        }

        summary = fetch_astronomy.extract_summary_fields(payload)

        self.assertEqual(summary["moon_phase"], "Waning Crescent")
        self.assertEqual(summary["moon_altitude"], "-22.5")
        self.assertEqual(summary["sunset"], "18:14")
        self.assertEqual(summary["moonrise"], "04:07")

    def test_extract_summary_fields_defaults_to_na_when_missing(self) -> None:
        payload: dict[str, object] = {}

        summary = fetch_astronomy.extract_summary_fields(payload)

        self.assertEqual(summary["moon_phase"], "N/A")
        self.assertEqual(summary["moon_altitude"], "N/A")
        self.assertEqual(summary["sunset"], "N/A")
        self.assertEqual(summary["moonrise"], "N/A")

    def test_format_summary_block_renders_contract_lines(self) -> None:
        summary = {
            "moon_phase": "Waning Crescent",
            "moon_altitude": "-22.5",
            "sunset": "18:14",
            "moonrise": "04:07",
        }

        formatted = fetch_astronomy.format_summary_block(summary)

        self.assertEqual(
            formatted,
            "\n".join(
                [
                    "Summary:",
                    "Moon phase: Waning Crescent",
                    "Moon altitude: -22.5",
                    "Sunset: 18:14",
                    "Moonrise: 04:07",
                ]
            ),
        )


if __name__ == "__main__":
    unittest.main()
