# eppy-stubs

[![PyPI - eppy-stubs]()](https://pypi.org/project/types-eppy/)
[![PyPI - Python Version]()](https://pypi.org/project/types-eppy/)
[![Docs](https://img.shields.io/badge/Material_for_MkDocs-526CFE?style=for-the-badge&amp;logo=MaterialForMkDocs&amp;logoColor=white)](https://types-eppy.readthedocs.io/)
[![PyPI - Downloads]()]()

Type annotations for
[eppy 23.1.0]()
compatible with
[VSCode](https://code.visualstudio.com/),
[PyCharm](https://www.jetbrains.com/pycharm/),
[Emacs](https://www.gnu.org/software/emacs/),
[Sublime Text](https://www.sublimetext.com/),
[mypy](https://github.com/python/mypy),
[pyright](https://github.com/microsoft/pyright)
and other tools.

Generated with [mypy_eppy_builder 0.0.1](https://github.com/samuelduchesne/mypy-eppy-builder).

## How to install

### Generate locally (recommended)

You can generate type annotations for `eppy` package locally with `mypy_eppy_builder`.
Use [uv](https://docs.astral.sh/uv/getting-started/installation/) for build isolation.

1. Run mypy_eppy_builder in your package root directory: `uvx --with 'eppy==23.1.0' mypy_eppy_builder`

### From PyPI with pip

Install `types_eplus2310` to add type checking for `eppy` package.

```bash
# install type annotations only for eppy
python -m pip install types_eplus2310

```

## How to uninstall

```bash
# uninstall eppy-stubs
python -m pip uninstall -y eppy-stubs
```

## Usage

### VSCode

- Install [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- Install [Pylance extension](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
- Set `Pylance` as your Python Language Server
- Install `eppy-stubs[latest]` in your environment:

```bash
python -m pip install 'eppy-stubs[latest]'
```

Both type checking and code completion should now work.
No explicit type annotations required, write your `eppy` code as usual.
