# ISS Pass Tracker

A small Python library to fetch upcoming International Space Station (ISS) passes for a given latitude/longitude. Intended as a PyPI-ready example and a practical utility.

## Features
- Query Open Notify (free) for next N passes.
- Return results as typed dataclasses.
- Optional CLI (requires `click` extra).

## Installation (from source / TestPyPI)
```bash
pip install build twine
python -m build
twine upload dist/*


```


## run locally after installing

pip install iss-now-sanjeet

python -m iss_now_sanjeet --now

will print:

ISS is currently at 50.4712°, -87.2649° at 2025-08-10T14:42:44+00:00

