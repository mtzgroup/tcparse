# qcparse

A library for parsing Quantum Chemistry output files into structured data objects. Uses data structures from [qcio](https://github.com/coltonbh/qcio).

[![image](https://img.shields.io/pypi/v/qcparse.svg)](https://pypi.python.org/pypi/qcparse)
[![image](https://img.shields.io/pypi/l/qcparse.svg)](https://pypi.python.org/pypi/qcparse)
[![image](https://img.shields.io/pypi/pyversions/qcparse.svg)](https://pypi.python.org/pypi/qcparse)
[![Actions status](https://github.com/coltonbh/qcparse/workflows/Tests/badge.svg)](https://github.com/coltonbh/qcparse/actions)
[![Actions status](https://github.com/coltonbh/qcparse/workflows/Basic%20Code%20Quality/badge.svg)](https://github.com/coltonbh/qcparse/actions)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)

## ☝️ NOTE

This package was originally designed to run as a standalone parser to generate `SinglePointResult` and `SinglePointFailure` objects parsing all input and provenance data in addition to computed output data; however, once [qcop](https://github.com/coltonbh/qcop) was built to power quantum chemistry programs the only parsing needed was for the simpler `SinglePointComputedProps` values. There are still remnants of the original `parse` function in the repo and I've left them for now in case I find a use for the general purpose parsing.

## ✨ Basic Usage

- Installation:

  ```sh
  python -m pip install qcparse
  ```

- Parse a file into a `SinglePointComputedProps` object with a single line of code.

  ```python
  from qcparse import parse_computed_props

  computed = parse_computed_props("/path/to/tc.out", "terachem")
  ```

- The `computed` object will be a `SinglePointComputedProps` object. Run `dir(computed)` inside a Python interpreter to see the various values you can access. A few prominent values are shown here as an example:

  ```python
  from qcparse import parse_computed_props

  computed = parse_computed_props("/path/to/tc.out", "terachem")

  computed.energy
  computed.gradient # If a gradient calc
  computed.hessian # If a hessian calc

  computed.calcinfo_nmo # Number of molecular orbitals
  ```

- Parsed values can be written to disk like this:

  ```py
  with open("computed.json", "w") as f:
      f.write(result.json())
  ```

- And read from disk like this:

  ```py
  from qcio import SinglePointComputedProps as SPProps

  computed = SPProps.open("myresult.json")
  ```

- You can also run `qcparse` from the command line like this:

  ```sh
  qcparse -h # Get help message for cli

  qcparse terachem ./path/to/tc.out > computed.json # Parse TeraChem stdout to json
  ```

## 🤩 Next Steps

This package is integrated into [qcop](https://github.com/coltonbh/qcop). This means you can use `qcop` to power your QC programs using standard input data structures in pure Python and get back standardized Python output objects.

```python
from qcop import compute
from qcio import Molecule, SinglePointInput

molecule = Molecule.open("mymolecule.xyz")
sp_input = SinglePointInput(
    molecule=molecule,
    program_args={
          "calctype": "gradient", # "energy" | "gradient" | "hessian"
          "model": {"method": "b3lyp", "basis": "6-31gs"},
          "keywords": {"restricted": True, "purify": "no"} # Keywords are optional
    })

# result will be SinglePointResult or SinglePointFailure
result = compute(sp_input, "terachem")
```

## 💻 Contributing

If there's data you'd like parsed fromI output files, please open an issue in this repo explaining the data items you'd like parsed and include an example output file containing the data, like [this](https://github.com/coltonbh/qcparse/issues/2).

If you'd like to add a parser yourself see the docstring in `qcparse.parsers` for a primer and see the examples written in the module. Adding a parser for new data is quick and easy :)
