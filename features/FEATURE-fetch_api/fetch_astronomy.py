from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


IOWA_CITY_LAT = "41.6611"
IOWA_CITY_LONG = "-91.5302"
TARGET_TIMEZONE = "America/Chicago"


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


def main() -> None:
    _ = get_api_key()
    _ = build_request_param_candidates()
    print("Checkpoint 1 setup complete: config and request parameter builders are ready.")


if __name__ == "__main__":
    main()