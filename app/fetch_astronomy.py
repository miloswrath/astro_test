from __future__ import annotations

from datetime import date, datetime
import json
from pathlib import Path
from typing import Callable
from urllib import error, parse, request
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


IOWA_CITY_LAT = "41.6611"
IOWA_CITY_LONG = "-91.5302"
TARGET_TIMEZONE = "America/Chicago"
ASTRONOMY_API_BASE_URL = "https://api.ipgeolocation.io/astronomy"


class AstronomyAPIError(RuntimeError):
    pass


def load_env_file(env_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}

    if not env_path.exists():
        return values

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[len("export ") :].strip()

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            continue

        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]

        values[key] = value

    return values


def get_api_key(env_path: Path | None = None) -> str:
    key_name = "IPGEOLOCATION_API_KEY"
    resolved_env_path = env_path or Path.cwd() / ".env"
    env_values = load_env_file(resolved_env_path)
    api_key = env_values.get(key_name, "").strip()

    if not api_key:
        raise ValueError(
            f"Missing {key_name} in {resolved_env_path}. Add {key_name}=<your_api_key> to continue."
        )

    return api_key


def get_today_in_timezone(timezone_name: str = TARGET_TIMEZONE) -> date:
    try:
        timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as error:
        raise ValueError(f"Invalid timezone: {timezone_name}") from error

    return datetime.now(timezone).date()


def build_request_param_candidates(
    target_date: date | None = None,
    timezone_name: str = TARGET_TIMEZONE,
) -> list[dict[str, str]]:
    request_date = target_date or get_today_in_timezone(timezone_name)
    request_date_str = request_date.isoformat()

    city_state_candidate = {
        "date": request_date_str,
        "timezone": timezone_name,
        "location": "Iowa City, Iowa, US",
    }

    coordinate_fallback_candidate = {
        "date": request_date_str,
        "timezone": timezone_name,
        "lat": IOWA_CITY_LAT,
        "long": IOWA_CITY_LONG,
    }

    return [city_state_candidate, coordinate_fallback_candidate]


def _build_url(api_key: str, params: dict[str, str]) -> str:
    query_params = {"apiKey": api_key, **params}
    encoded = parse.urlencode(query_params)
    return f"{ASTRONOMY_API_BASE_URL}?{encoded}"


def _is_api_payload_error(payload: dict[str, object]) -> bool:
    error_keys = {"message", "error", "status"}
    return any(key in payload for key in error_keys) and "sunset" not in payload


def request_astronomy_payload(
    api_key: str,
    params: dict[str, str],
    timeout_seconds: float = 15.0,
) -> dict[str, object]:
    url = _build_url(api_key, params)

    try:
        with request.urlopen(url, timeout=timeout_seconds) as response:
            status_code = getattr(response, "status", None)
            body = response.read().decode("utf-8")
    except error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        raise AstronomyAPIError(
            f"Astronomy API HTTP error {exc.code}: {error_body or exc.reason}"
        ) from exc
    except error.URLError as exc:
        raise AstronomyAPIError(f"Astronomy API network error: {exc.reason}") from exc

    if status_code is not None and status_code >= 400:
        raise AstronomyAPIError(f"Astronomy API HTTP error {status_code}: {body}")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise AstronomyAPIError("Astronomy API returned non-JSON response") from exc

    if not isinstance(payload, dict):
        raise AstronomyAPIError("Astronomy API returned unexpected JSON structure")

    return payload


def fetch_astronomy_payload(
    api_key: str,
    param_candidates: list[dict[str, str]],
    request_func: Callable[[str, dict[str, str]], dict[str, object]] | None = None,
) -> dict[str, object]:
    request_impl = request_func or request_astronomy_payload
    errors: list[str] = []

    for params in param_candidates:
        try:
            payload = request_impl(api_key, params)
        except AstronomyAPIError as exc:
            errors.append(str(exc))
            continue

        if _is_api_payload_error(payload):
            errors.append(json.dumps(payload, sort_keys=True))
            continue

        return payload

    details = "; ".join(errors) if errors else "No response data received"
    raise AstronomyAPIError(f"Failed to fetch astronomy data for Iowa City: {details}")


def format_json_payload(payload: dict[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def extract_summary_fields(payload: dict[str, object]) -> dict[str, str]:
    def _value_for(key: str) -> str:
        value = payload.get(key)
        if value is None:
            return "N/A"
        text = str(value).strip()
        return text if text else "N/A"

    return {
        "moon_phase": _value_for("moon_phase"),
        "moon_altitude": _value_for("moon_altitude"),
        "sunset": _value_for("sunset"),
        "moonrise": _value_for("moonrise"),
    }


def format_summary_block(summary_fields: dict[str, str]) -> str:
    return "\n".join(
        [
            "Summary:",
            f"Moon phase: {summary_fields.get('moon_phase', 'N/A')}",
            f"Moon altitude: {summary_fields.get('moon_altitude', 'N/A')}",
            f"Sunset: {summary_fields.get('sunset', 'N/A')}",
            f"Moonrise: {summary_fields.get('moonrise', 'N/A')}",
        ]
    )


def main() -> None:
    api_key = get_api_key()
    param_candidates = build_request_param_candidates()
    payload = fetch_astronomy_payload(api_key, param_candidates)

    print(format_json_payload(payload))
    print()
    print(format_summary_block(extract_summary_fields(payload)))


if __name__ == "__main__":
    main()
