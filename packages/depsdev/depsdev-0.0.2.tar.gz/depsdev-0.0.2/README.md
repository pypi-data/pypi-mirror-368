# depsdev

[![PyPI - Version](https://img.shields.io/pypi/v/depsdev.svg)](https://pypi.org/project/depsdev)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/depsdev.svg)](https://pypi.org/project/depsdev)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/FlavioAmurrioCS/depsdev/main.svg)](https://results.pre-commit.ci/latest/github/FlavioAmurrioCS/depsdev/main)

-----

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [License](#license)

## Overview

Thin Python wrapper (async-first) around the public [deps.dev REST API](https://deps.dev) plus an optional Typer-based CLI. Provides straightforward methods mapping closely to the documented endpoints; responses are returned as decoded JSON (dict / list). Alpha endpoints can be enabled via `DEPSDEV_V3_ALPHA=true` and may change without notice.

## Installation

```bash
pip install depsdev            # library only
pip install depsdev[cli]       # library + CLI
```

## License

`depsdev` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
