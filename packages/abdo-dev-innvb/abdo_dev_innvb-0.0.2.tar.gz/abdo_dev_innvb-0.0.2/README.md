# abdo_dev_innvb

A simple library to execute Python scripts and install PHP on Linux.

## Installation

```bash
pip install abdo_dev_innvb
```

## Usage

### Execute a Python Script

```python
from abdo_dev_innvb import abdo

# Execute a python file in the same directory
abdo("my_script.py")

# Execute a python file in a subdirectory
abdo("scripts/another_script.py")
```

### Install Latest PHP (for Debian/Ubuntu)

This function requires `sudo` privileges.

```python
from abdo_dev_innvb import abdophp

# This will add the necessary PPA and install the latest PHP version
abdophp()
```