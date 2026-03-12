from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import fetch_astronomy


class TestCheckpoint2Client(unittest.TestCase):
    def test_fetch_astronomy_payload_returns_first_successful_candidate(self) -> None:
        candidates = [
            {"location": "Iowa City, Iowa, US", "date": "2026-03-12", "timezone": "America/Chicago"},
            {"lat": "41.6611", "long": "-91.5302", "date": "2026-03-12", "timezone": "America/Chicago"},
        ]

        def fake_request(api_key: str, params: dict[str, str]) -> dict[str, object]:
            self.assertEqual(api_key, "abc")
            if "location" in params:
                return {"message": "invalid location"}
            return {"sunset": "18:01", "moonrise": "04:10"}

        payload = fetch_astronomy.fetch_astronomy_payload("abc", candidates, request_func=fake_request)

        self.assertEqual(payload["sunset"], "18:01")
        self.assertEqual(payload["moonrise"], "04:10")

    def test_fetch_astronomy_payload_raises_when_all_candidates_fail(self) -> None:
        candidates = [{"location": "Iowa City, Iowa, US", "date": "2026-03-12", "timezone": "America/Chicago"}]

        def fake_request(_: str, __: dict[str, str]) -> dict[str, object]:
            raise fetch_astronomy.AstronomyAPIError("network down")

        with self.assertRaises(fetch_astronomy.AstronomyAPIError) as context:
            fetch_astronomy.fetch_astronomy_payload("abc", candidates, request_func=fake_request)

        self.assertIn("Failed to fetch astronomy data", str(context.exception))
        self.assertIn("network down", str(context.exception))

    @patch("fetch_astronomy.fetch_astronomy_payload")
    @patch("fetch_astronomy.build_request_param_candidates")
    @patch("fetch_astronomy.get_api_key")
    def test_main_prints_pretty_json_output(
        self,
        mock_get_api_key,
        mock_build_candidates,
        mock_fetch_payload,
    ) -> None:
        mock_get_api_key.return_value = "abc"
        mock_build_candidates.return_value = [{"location": "Iowa City, Iowa, US"}]
        mock_fetch_payload.return_value = {
            "moon_phase": "Waxing Gibbous",
            "moon_altitude": "-15.2",
            "sunset": "19:11",
            "moonrise": "03:31",
            "extra": {"nested": True},
        }

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            fetch_astronomy.main()

        output = buffer.getvalue()
        self.assertIn('"extra": {', output)
        self.assertIn('  "nested": true', output)
        self.assertIn("Summary:\n", output)


if __name__ == "__main__":
    unittest.main()
