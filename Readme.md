# 🤖 💾 WayDiffer: Wayback Machine URL Comparison Tool
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://waydiffer.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Description
**Waydiffer** is a Streamlit application that compares website versions archived in the Wayback Machine. It utilizes the [diff_match_patch](https://github.com/google/diff-match-patch) library from Google for tracking differences in HTML, CSS, and JavaScript files between two selected snapshots.

    Features include:
    - Finding available dates for a URL in the Wayback Machine.
    - Diffing support for HTML, CSS, and JavaScript.
    - Auto-beautification of HTML, CSS, and JavaScript files.
    - Custom diff interface with line numbers for easy comparison.
    - Two viewing options: inline or in a new window.

    Note: Open in a new window does not work in Streamlit Hosted Apps.

    Access the source code [here](https://github.com/jroakes/WayDiffer).


## Installation
```bash
git clone https://github.com/jroakes/WayDiffer.git
cd WayDiffer
conda create -n waydiffer python=3.9
activate waydiffer
pip install -r requirements.txt
```


## Usage
```python
streamlit run src/main.py
```

Deployed automatically from Github.


# Install Pre-commit
```
# Add .pre-commit-config.yaml
poetry add -G dev pre-commit
poetry run pre-commit install
poetry run pre-commit run --all-files
```

## Requirements
 - jsbeautifier
- cssbeautifier
- bs4
- diff_match_patch
- loguru
- streamlit

## Environmental Variables
None
