from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

import fetch_astronomy


class TestConfigLoading(unittest.TestCase):
    def test_load_env_file_parses_key_value_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text(
                """
                # comment
                export IPGEOLOCATION_API_KEY="abc123"
                EXTRA_VALUE = test-value
                INVALID_LINE_WITHOUT_EQUALS
                """,
                encoding="utf-8",
            )

            parsed = fetch_astronomy.load_env_file(env_path)

            self.assertEqual(parsed["IPGEOLOCATION_API_KEY"], "abc123")
            self.assertEqual(parsed["EXTRA_VALUE"], "test-value")
            self.assertNotIn("INVALID_LINE_WITHOUT_EQUALS", parsed)

    def test_get_api_key_returns_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text("IPGEOLOCATION_API_KEY=my-test-key\n", encoding="utf-8")

            key = fetch_astronomy.get_api_key(env_path=env_path)

            self.assertEqual(key, "my-test-key")

    def test_get_api_key_raises_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text("OTHER_KEY=value\n", encoding="utf-8")

            with self.assertRaises(ValueError) as context:
                fetch_astronomy.get_api_key(env_path=env_path)

            self.assertIn("Missing IPGEOLOCATION_API_KEY", str(context.exception))


class TestRequestParameterBuilder(unittest.TestCase):
    def test_build_request_param_candidates_city_state_then_coordinates(self) -> None:
        fixed_date = date(2026, 3, 5)

        candidates = fetch_astronomy.build_request_param_candidates(target_date=fixed_date)

        self.assertEqual(len(candidates), 2)

        city_candidate = candidates[0]
        self.assertEqual(city_candidate["date"], "2026-03-05")
        self.assertEqual(city_candidate["timezone"], "America/Chicago")
        self.assertEqual(city_candidate["location"], "Iowa City, Iowa, US")

        fallback_candidate = candidates[1]
        self.assertEqual(fallback_candidate["date"], "2026-03-05")
        self.assertEqual(fallback_candidate["timezone"], "America/Chicago")
        self.assertEqual(fallback_candidate["lat"], "41.6611")
        self.assertEqual(fallback_candidate["long"], "-91.5302")


if __name__ == "__main__":
    unittest.main()