# pyiron_vasp

[![Pipeline](https://github.com/pyiron/pyiron_vasp/actions/workflows/pipeline.yml/badge.svg)](https://github.com/pyiron/pyiron_vasp/actions/workflows/pipeline.yml)
[![codecov](https://codecov.io/gh/pyiron/pyiron_vasp/graph/badge.svg?token=PWWLjnbDJz)](https://codecov.io/gh/pyiron/pyiron_vasp)

Parser for the Vienna Ab initio Simulation Package (VASP)

## Installation 
Via pip
```
pip install pyiron_vasp
```

Via conda
```
conda install -c conda-forge pyiron_vasp
```

## Usage
Parse an directory with VASP output files 
```python
from pyiron_vasp.vasp.output import parse_vasp_output

output_dict = parse_vasp_output(working_directory="path/to/calculation")
```
