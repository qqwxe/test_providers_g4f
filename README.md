# G4F Provider & Model Tester

A minimal utility to benchmark free g4f providers across several models and save results to `g4f_test_results.json`. Use it to discover which provider+model pairs are currently working and the fastest.

## What it does
- Iterates over available `g4f.Provider` entries and tests a small set of models.
- Runs tests concurrently and prints progress with successes/errors.
- Saves a full report to `g4f_test_results.json` with timings and a preview.

## Requirements
- Python 3.10+
- Pip

## Installation

Option A — global/default Python
```
pip install -U g4f
```
If `pip` belongs to a different interpreter, use:
```
python -m pip install -U g4f
```
On Windows with the launcher:
```
py -m pip install -U g4f
```

Option B — isolated virtual environment

Windows (PowerShell):
```
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r requirements.txt
```

Linux/macOS:
```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```

## Run

Global/default Python:
```
py test.py
```

Virtual environment (Windows):
```
.venv\Scripts\python test.py
```

Virtual environment (Linux/macOS):
```
.venv/bin/python test.py
```

## Output
- The script writes a detailed report to `g4f_test_results.json`:
  - `all_results`: every tested pair with status, time, and preview.
  - `successful`: convenience list of successful pairs.
  - `success_rate` and totals.

## Troubleshooting
- ModuleNotFoundError: No module named 'g4f'
  - Install the dependency in the interpreter you are using (see Installation).
- Lots of provider errors/logs
  - Normal: many providers are region/ratelimit/credential dependent. Focus on the SUCCESS items.
- Unclosed client session warnings
  - Cosmetic, from upstream providers. You can ignore or reduce concurrency in `test.py`.
- Proxy
  - If you need a proxy, export `HTTPS_PROXY` or `HTTP_PROXY` before running.

## What is this script?
`test_providers_g4f.py` is a benchmark/helper that probes g4f providers to find currently working combinations. You can use the generated JSON to hardcode a priority list in your own plugins/bots.

