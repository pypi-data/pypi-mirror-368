# Tikka

_The rich desktop Python client for Duniter V2 Ğ1 crypto-currency_

**Tikka** is a rich desktop Python client to manage your Ğ1 accounts.

It has a system integrated GUI, is fast and powerful.

It is licenced under the [GPLv3 licence](https://www.gnu.org/licenses/gpl-3.0.en.html) terms.

## Requirements

* [Python](https://www.python.org/) interpreter >= 3.7
* [sqlite3](https://sqlite.org/index.html) database system via [sqlite3](https://docs.python.org/3/library/sqlite3.html) package
* [Qt5](https://www.qt.io/) via [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) package

## Install with pipx

You can use [pipx](https://pypa.github.io/pipx/installation/) to install Tikka.

    pipx install tikka

Then simply run the `tikka` command:

    tikka

Upgrade or uninstall:

    pipx upgrade tikka

    pipx uninstall tikka

## Install/upgrade from PyPI

If you are in a Python virtual environment:

    pip install --upgrade tikka

If you are not:

    # GNU/Linux virtualenv creation
    mkdir tikka
    cd tikka
    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade tikka

    # get the path of the tikka command
    which tikka

## Run from PyPI installation

    tikka

Or

    python -m tikka

GNU/Linux system requirements:

    sudo apt-get install libsodium23 gcc
