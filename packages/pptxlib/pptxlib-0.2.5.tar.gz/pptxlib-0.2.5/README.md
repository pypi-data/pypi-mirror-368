# pptxlib

[![PyPI Version][pypi-v-image]][pypi-v-link]
[![Python Version][python-v-image]][python-v-link]
[![Build Status][GHAction-image]][GHAction-link]
[![Coverage Status][codecov-image]][codecov-link]

A Python library for automating Microsoft PowerPoint operations.

## Overview

pptxlib is a high-level Python library that provides a simple and intuitive interface
for automating Microsoft PowerPoint operations. It allows you to create, modify, and
manage PowerPoint presentations programmatically.

## Features

- Create and manage PowerPoint presentations
- Add and modify slides
- Work with shapes, tables, and charts
- Customize text, colors, and formatting
- Automate presentation generation
- Support for Windows platforms

## Quick Start

```python
from pptxlib import App

app = App()
# Optional: keep the window minimized (PowerPoint doesn't allow hiding the UI)
app.minimize()
# Or create a presentation without opening a window
prs = app.presentations.add(with_window=False)
slide = prs.slides.add()
shape = slide.shapes.add("Rectangle", 100, 100, 200, 100)
```

## Installation

```bash
pip install pptxlib
```

Optional extras:

- For image support (Pillow):

```bash
pip install "pptxlib[images]"
```

- For Matplotlib figure export:

```bash
pip install "pptxlib[figures]"
```

## Requirements

- Windows operating system
- Microsoft PowerPoint
- Python 3.11 or higher

<!-- Badges -->
[pypi-v-image]: https://img.shields.io/pypi/v/pptxlib.svg
[pypi-v-link]: https://pypi.org/project/pptxlib/
[python-v-image]: https://img.shields.io/pypi/pyversions/pptxlib.svg
[python-v-link]: https://pypi.org/project/pptxlib
[GHAction-image]: https://github.com/daizutabi/pptxlib/actions/workflows/ci.yaml/badge.svg?branch=main&event=push
[GHAction-link]: https://github.com/daizutabi/pptxlib/actions?query=event%3Apush+branch%3Amain
[codecov-image]: https://codecov.io/github/daizutabi/pptxlib/coverage.svg?branch=main
[codecov-link]: https://codecov.io/github/daizutabi/pptxlib?branch=main
