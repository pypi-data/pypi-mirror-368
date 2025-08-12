# NXBrew-dl

[![](https://img.shields.io/pypi/v/nxbrew-dl.svg?label=PyPI&style=flat-square)](https://pypi.org/pypi/nxbrew-dl/)
[![](https://img.shields.io/pypi/pyversions/nxbrew-dl.svg?label=Python&color=yellow&style=flat-square)](https://pypi.org/pypi/nxbrew-dl/)
[![Docs](https://readthedocs.org/projects/nxbrew-dl/badge/?version=latest&style=flat-square)](https://nxbrew-dl.readthedocs.io/en/latest/)
[![Actions](https://img.shields.io/github/actions/workflow/status/bbtufty/nxbrew-dl/build.yaml?branch=main&style=flat-square)](https://github.com/bbtufty/nxbrew-dl/actions)
[![License](https://img.shields.io/badge/license-GNUv3-blue.svg?label=License&style=flat-square)](LICENSE)

NXBrew-dl is intended to be an easy-to-user interface to download ROMs, DLC and update files for NSP. It does so via
a GUI interface, allowing users to download items in bulk and keeping things up-to-date.

As of now, this is in extremely early development. It will parse and download many ROMs, and by default will only
grab ROMs from either the USA or Europe (USA preferred) that are marked as having English language releases.

## Installation

We recommend using the executable version. You can grab the latest release from the [releases page](https://github.com/bbtufty/nxbrew-dl/releases). Place the 
.exe wherever you want, and double-click to load.

Alternatively, you can install via pip:
```shell
pip install nxbrew-dl
```
Or download the latest from GitHub:
```shell
git clone https://github.com/bbtufty/nxbrew-dl.git
cd nxbrew-dl
pip install -e . -r requirements.txt
```
If you use these versions, you can then run from the terminal as:
```shell
nxbrew-dl
```

## 

To get things set up, see the [documentation](https://nxbrew-dl.readthedocs.io/en/latest/).

We encourage users to open [issues](https://github.com/bbtufty/nxbrew-dl/issues>) as and where they find them.