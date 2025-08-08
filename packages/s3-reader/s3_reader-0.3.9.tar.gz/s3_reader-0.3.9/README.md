# s3-reader

[![test](https://github.com/rcmdnk/s3-reader/actions/workflows/test.yml/badge.svg)](https://github.com/rcmdnk/s3-reader/actions/workflows/test.yml)
[![test coverage](https://img.shields.io/badge/coverage-check%20here-blue.svg)](https://github.com/rcmdnk/s3-reader/tree/coverage)

Python library to read S3 file as local file.

## Requirement

- Python 3.9, 3.10, 3.11

## Installation

```bash
$ pip install s3-reader
```

## Usage

```
from s3_reader import File


def check_s3_file(path):
    file = File(path)

    with open(file.path) as f:
        ...

check_s3_file('s3://<bucket>/path/to/file')

```

In this example, the S3 file is downloaded when `file = File(path)` is
executed, and it is stored as a temporary file.

`file.path` refers to the path of the locally stored temporary file.

At the end of the `check_s3_file` function, the file object is deleted, and
consequently, the temporary file is also deleted.

If path refers to a local file instead of an S3 file, File simply copies the
path, and you can use the File object in the same manner.
