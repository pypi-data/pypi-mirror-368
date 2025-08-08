# PyBigDFT

PyBigDFT is a comprehensive Python package for driving, analyzing, and extending BigDFT electronic structure calculations. It provides tools for setting up simulations, parsing and post-processing results, and integrating BigDFT workflows with other Python-based scientific software.

## Features
- High-level Python interface to BigDFT drivers and analysis tools
- Utilities for atom, molecule, and fragment manipulation
- Database and file format interoperability
- Scripting and automation support for BigDFT workflows
- Extensible framework for custom analysis and integration

## Installation
You can install PyBigDFT and its dependencies using pip:

```sh
pip install .
```

## Documentation
Full documentation is available at: https://www.bigdft.org/

## Contributing
Contributions, bug reports, and feature requests are welcome. Please open an issue or submit a pull request on the project's repository.

### Versioning
PyBigDFT follows a unique versioning system. The `MAJOR.MINOR.PATCH` sections of the version mirror that of the current BigDFT release.
This is supplemented by an incrementing version number that represents the version of `PyBigDFT` over this milestone.

For example, if you are working with BigDFT 1.9.6, you would use `PyBigDFT==1.9.6.x`, where `x` is the actual patch number of `PyBigDFT`.

Version compatibility may exist outside of this system, but development will focus on ensuring compatibility between matching versions. 

### Automatic Versioning

There is configuration for the [bumpver](https://github.com/mbarkhau/bumpver) tool present in `pyproject.toml`.

You can automatically increment the `PyBigDFT` version by running:

`bumpver update`

This will update the version number in the necessary locations.

Force the BigDFT portion of the version number to update with:

`bumpver update --major`, `bumpver update --minor`, or `bumpver update --patch`

## License
PyBigDFT is distributed under the GNU General Public License (GPL).
