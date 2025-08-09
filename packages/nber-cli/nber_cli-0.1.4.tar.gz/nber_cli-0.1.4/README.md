# NBER-CLI

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://img.shields.io/pypi/v/nber-cli.svg)](https://pypi.org/project/nber-cli/)
[![PyPI Downloads](https://static.pepy.tech/badge/nber-cli)](https://pepy.tech/projects/nber-cli)
[![Issue](https://img.shields.io/badge/Issue-report-green.svg)](https://github.com/sepinetam/nber-cli/issues/new)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/SepineTam/nber-cli)

NBER-CLI is a command line interface for the National Bureau of Economic Research (NBER) paper data.


## Installation
```bash
pip install nber-cli
```

or you can install it from github for the beta version:
```bash
pip install git+https://github.com/sepinetam/nber-cli.git
```

## Usage
```bash
nber-cli --help
```

- Download the certain paper to default directory:
```bash
nber-cli --download paper_id [paper_id ...]
```

- Shorthand:
```bash
nber-cli -d paper_id [paper_id ...]
```

- Download the certain paper to a specific directory:
```bash
nber-cli --download paper_id --save_path /path/to/directory
```

An example of downloading a paper with ID `w1234` to the specific directory:
```bash
(base) ~/Documents/Github/nber_cli git:[master]
nber-cli --download w1234 --save_path ~/Downloads/nber-cli
2025-06-23 12:00:29,266 - INFO - Loaded 1 ok ids and 0 fail ids from db.
2025-06-23 12:00:41,097 - INFO - Successfully downloaded w1234 to /Users/sepinetam/Downloads/nber-cli/w1234.pdf

```

You can also download multiple papers at once:
```bash
nber-cli --download w1234 w5678
```
## Web UI

Start a simple web server with:
```bash
nber-cli-web
```


## LICENSE
[APACHE-2.0](LICENSE)
