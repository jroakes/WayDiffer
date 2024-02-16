# 🤖 💾 WayDiffer: Wayback Machine URL Comparison Tool
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://waydiffer.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Description
Diff a file with a historical Wayback Machine file and highlight the differences.
Works for HTML, CSS, and JS files.

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
