# Feature Spec -> Fetch from Astronomy API
---

API/docs source: ipgeolocation astronomy API docs. https://ipgeolocation.io/documentation/astronomy-api.html USE THIS THROUGH SERACH TO FIND CORRECT PAYLOAD
Auth: read API key from .env.
Date behavior: use today’s system date.
Output: pretty-printed full JSON response to stdout, plus mapped values for moon phase, moon altitude, sunset, moonrise.
Timezone: America/Chicago for Iowa City interpretation.
Scope Decisions (v1)

Location input: use city/state if supported by endpoint.
Fallback rule: if endpoint requires coordinates, use hardcoded Iowa City lat/long.
Out of scope: retries/backoff, caching/persistence, broad test suite beyond smoke validation, configurable location.
No Open Ambiguities

This is now specific enough to write solid FRs / Non-FRs / scope boundaries.
Want me to draft the final FR, Non-FR, and scope doc text next?

***checkpoint 1***
- [ ] Align feature folder/script layout with project conventions from README.md (single Python script entrypoint for this feature).
- [ ] Add configuration loading from .env for IPGEOLOCATION_API_KEY and validate key presence with a clear failure message.
- [ ] Implement request-input builder for date=today, timezone=America/Chicago, and Iowa City location strategy (city/state first, coordinates fallback).
- [ ] Add unit tests for config parsing/validation and request parameter construction logic only.

***checkpoint 2***
- [x] Implement astronomy API client call to ipgeolocation using the built request parameters.
- [x] Add response handling that prints the full API payload as pretty-printed JSON to stdout.
- [x] Add minimal non-retry error handling for HTTP/network/API error responses (in-scope guardrails only).
- [x] Add unit tests for API client success/error branches and stdout pretty-print behavior only (mock HTTP + capture stdout).

***checkpoint 3***
- [x] Implement field mapping/extraction for moon phase, moon altitude, sunset time, and moonrise time from returned payload shape.
- [x] Print mapped values in a small summary block after the full JSON dump.
- [x] Add/update feature documentation for run command, required .env, and expected output contract.
- [x] Add unit tests for mapping/extraction and summary output formatting only (fixture-based payload tests).

## Runtime Notes (Checkpoint 2 + 3)

Run command (from project root):

```bash
python app/fetch_astronomy.py
```

Required `.env` in project root:

```dotenv
IPGEOLOCATION_API_KEY=<your_api_key>
```

Output contract:

1. Script prints full astronomy API response as pretty-printed JSON.
2. Script prints a blank line.
3. Script prints this summary block:

```text
Summary:
Moon phase: <moon_phase or N/A>
Moon altitude: <moon_altitude or N/A>
Sunset: <sunset or N/A>
Moonrise: <moonrise or N/A>
```

Request behavior:

- Date uses today's date in `America/Chicago`.
- First request candidate uses Iowa City city/state location string.
- Fallback request candidate uses hardcoded Iowa City coordinates (`41.6611`, `-91.5302`).