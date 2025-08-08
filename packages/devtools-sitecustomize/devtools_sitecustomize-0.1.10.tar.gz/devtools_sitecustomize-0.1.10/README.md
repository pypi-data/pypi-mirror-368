# devtools-sitecustomize

A simple Python package designed to automatically make [`devtools.debug`](https://github.com/samuelcolvin/python-devtools?tab=readme-ov-file#usage) available as a global `debug()` function in your Python interpreter sessions and scripts, by leveraging the [`sitecustomize-entrypoints`](https://github.com/Darsstar/sitecustomize-entrypoints) mechanism. This removes the need for manual `import` statements or custom `PYTHONSTARTUP` configurations.

## ✨ Features

* **Automatic `debug()`:** Provides `devtools.debug` directly in your `builtins`, accessible as `debug()`.
* **Zero Configuration for Users:** Once installed as a dependency, it just works.
* **`uv` Friendly:** Integrates seamlessly with `uv`-managed Python environments.
* **Non-Interactive & Interactive Mode:** Works for both running scripts and interactive interpreter sessions.

## 🚀 Installation

Install `devtools-sitecustomize` into your project's environment.
If your project is `uv`-managed: Just run `uv add --dev devtools-sitecustomize`.


## ⚙️ How it Works
This package works by defining a `sitecustomize` entry point in its own `pyproject.toml`. When `devtools-sitecustomize` is installed, the `sitecustomize-entrypoints` library (which is a dependency of this package) intercepts Python's startup sequence. It finds all registered `sitecustomize` entry points, including the one from this package, and executes them. This allows `devtools.debug` to be imported and assigned to `builtins.debug` very early in the Python interpreter's lifecycle.
