# generate-github-wiki

Generates markdown docs from Python docustrings for publishing to a Github wiki.

## Usage

```sh
>ls example
example.py
> ./gengithubwiki.py --verbose --output example/docs/ example/example.py
Processing example/example.py
example/example.py ready to write (0.000s)
Created 2 documents and skipped 0 (0.003s)
> ls example/docs
test1.md        test2.md
```

## Limitations

- Currently only supports docustrings in [Google docustring format](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
- Assumes that you only want to document things with docustrings; if a function or argument does not have a docustring entry then it will not be documented.
- Multi-level bulleted lists may not convert correctly.
