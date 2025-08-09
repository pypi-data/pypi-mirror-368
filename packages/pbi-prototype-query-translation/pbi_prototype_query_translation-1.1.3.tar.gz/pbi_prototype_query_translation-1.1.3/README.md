# Dev Instructions


## Set Up

```shell
python -m venv venv
venv\Scripts\activate
python -m pip install .[dev]
pre-commit install
```

# Building package

1. Run the C# application against x64 target
2. Run add_libs to refresh the C# libs being binded to python
3. Run the shell command below

```shell
python -m build .
```

# Sphinx

sphinx-quickstart