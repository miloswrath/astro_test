# Project
---
Astronomer’s Night Quality Predictor

Goal: Tell users if tonight is good for stargazing.

Features

Input: location

Fetch:

- moon phase
- moon altitude
- sunset time
- moonrise time

Calculate:

- dark sky window
- moon brightness penalty

Output: stargazing score (0–100)

Stack
---
- Python
- FastAPI
- matplotlib
- astronomy API

```
Example output
Location: Iowa City
Dark sky window: 9:02pm – 4:12am
Moon phase: 0.78 (waning crescent)

Stargazing score: 82 / 100
```

Extra: plot darkness timeline.