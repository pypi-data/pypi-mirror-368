# Contributing to maildeck

## Development setup

The project has no dependencies other than the Python standard library at the
version specified in the `pyproject.toml` file so as long as you have Python you
don't need to install anything else for development.

To release however, it is best to have [`rye`](https://rye-up.com/) installed.

To build and publish the package, run:

```bash
rye build --clean
rye publish
```
