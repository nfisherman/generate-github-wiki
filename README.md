# generate-github-wiki

Generates markdown docs from Python docustrings for publishing to a Github wiki.

## Usage

```sh

```

## Limitations

- Currently only supports docustrings in [Google docustring format](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
- Assumes that you only want to document things with docustrings; if a function or argument does not have a docustring entry then it will not be documented.
- Multi-level bulleted lists may not convert correctly.
