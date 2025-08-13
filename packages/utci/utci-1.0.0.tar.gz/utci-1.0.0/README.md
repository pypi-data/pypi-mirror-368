# UTCI - Universal Thermal Climate Index

[![Python Version](https://img.shields.io/pypi/pyversions/utci)](https://pypi.org/project/utci/)
[![PyPI Version](https://img.shields.io/pypi/v/utci)](https://pypi.org/project/utci/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/marvell/utci/actions/workflows/tests.yml/badge.svg)](https://github.com/marvell/utci/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/marvell/utci/branch/main/graph/badge.svg)](https://codecov.io/gh/marvell/utci)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python implementation of the Universal Thermal Climate Index (UTCI) algorithm, providing accurate thermal comfort assessment based on meteorological data.

## Overview

The Universal Thermal Climate Index (UTCI) is one of the most comprehensive indices for evaluating outdoor thermal comfort. It represents the equivalent temperature that would produce the same physiological response in a standard environment. This implementation is a faithful translation of the original Fortran code (Version a 0.002, October 2009) developed by Peter Bröde and the members of COST Action 730.

### Key Features

- **Accurate Implementation**: Exact numerical translation from the reference Fortran implementation
- **Fast Computation**: Optimized 6th-order polynomial approximation with 210 coefficients
- **Comprehensive**: Handles wide ranges of meteorological conditions
- **Well-Tested**: Extensive test coverage with validation against reference data
- **Type-Safe**: Full type hints for better IDE support and code reliability
- **Easy to Use**: Simple API with clear documentation

## Installation

Install the latest stable version from PyPI:

```bash
pip install utci
```

For development or to get the latest features:

```bash
git clone https://github.com/marvell/utci.git
cd utci
pip install -e ".[dev]"
```

## Quick Start

```python
from utci import utci_approx, rh_to_vp

# Input parameters
ta = 25.0      # Air temperature [°C]
rh = 60.0      # Relative humidity [%]
tmrt = 30.0    # Mean radiant temperature [°C]
va = 2.0       # Wind speed at 10m [m/s]

# Convert relative humidity to vapor pressure
vp = rh_to_vp(ta, rh)

# Calculate UTCI
utci_value = utci_approx(ta, vp, tmrt, va)
print(f"UTCI: {utci_value:.1f} °C")
# Output: UTCI: 26.5 °C
```

## API Reference

### Main Functions

#### `utci_approx(ta, eh_pa, tmrt, va) -> float`

Calculate the Universal Thermal Climate Index using polynomial approximation.

**Parameters:**
- `ta` (float): Air temperature [°C]
- `eh_pa` (float): Water vapor pressure [hPa]
- `tmrt` (float): Mean radiant temperature [°C]
- `va` (float): Wind speed at 10m height [m/s]

**Returns:**
- float: UTCI value [°C], or NaN if inputs are outside valid ranges

**Valid Input Ranges:**
- Air temperature: -50 to +50 °C
- Mean radiant temperature: ta-30 to ta+70 °C
- Wind speed: 0.5 to 17 m/s
- Water vapor pressure: 0 to 50 hPa

#### `rh_to_vp(ta, rh) -> float`

Convert relative humidity to water vapor pressure.

**Parameters:**
- `ta` (float): Air temperature [°C]
- `rh` (float): Relative humidity [%]

**Returns:**
- float: Water vapor pressure [hPa]

#### `es(ta) -> float`

Calculate saturation vapor pressure over water using Hardy's ITS-90 formulation.

**Parameters:**
- `ta` (float): Air temperature [°C]

**Returns:**
- float: Saturation vapor pressure [hPa]

## Thermal Stress Categories

The UTCI values can be interpreted using these thermal stress categories:

| UTCI Range (°C) | Thermal Stress Category |
|-----------------|-------------------------|
| > 46            | Extreme heat stress     |
| 38 to 46        | Very strong heat stress |
| 32 to 38        | Strong heat stress      |
| 26 to 32        | Moderate heat stress    |
| 9 to 26         | No thermal stress       |
| 0 to 9          | Slight cold stress      |
| -13 to 0        | Moderate cold stress    |
| -27 to -13      | Strong cold stress      |
| -40 to -27      | Very strong cold stress |
| < -40           | Extreme cold stress     |

## Examples

### Basic Usage

```python
from utci import utci_approx, rh_to_vp

# Summer conditions
ta_summer = 30.0    # Hot air temperature
rh_summer = 70.0    # High humidity
tmrt_summer = 35.0  # Strong solar radiation
va_summer = 1.0     # Light breeze

vp_summer = rh_to_vp(ta_summer, rh_summer)
utci_summer = utci_approx(ta_summer, vp_summer, tmrt_summer, va_summer)
print(f"Summer UTCI: {utci_summer:.1f} °C")  # Strong heat stress

# Winter conditions
ta_winter = -5.0    # Cold air temperature
rh_winter = 80.0    # High humidity
tmrt_winter = -8.0  # No solar radiation
va_winter = 5.0     # Moderate wind

vp_winter = rh_to_vp(ta_winter, rh_winter)
utci_winter = utci_approx(ta_winter, vp_winter, tmrt_winter, va_winter)
print(f"Winter UTCI: {utci_winter:.1f} °C")  # Strong cold stress
```

### Batch Processing

```python
import numpy as np
from utci import utci_approx, rh_to_vp

# Arrays of meteorological data
ta_array = np.array([20.0, 25.0, 30.0, 35.0])
rh_array = np.array([50.0, 60.0, 70.0, 80.0])
tmrt_array = ta_array + 5.0  # Assume 5°C above air temperature
va_array = np.array([2.0, 2.5, 3.0, 3.5])

# Calculate UTCI for all conditions
utci_values = []
for ta, rh, tmrt, va in zip(ta_array, rh_array, tmrt_array, va_array):
    vp = rh_to_vp(ta, rh)
    utci = utci_approx(ta, vp, tmrt, va)
    utci_values.append(utci)

print("UTCI values:", [f"{u:.1f}" for u in utci_values])
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/marvell/utci.git
cd utci

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev,test,docs]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=utci --cov-report=html

# Run specific test file
pytest tests/test_utci.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/utci tests
isort src/utci tests

# Lint code
ruff check src/utci tests

# Type checking
mypy src/utci
```

### Building Documentation

```bash
# Build HTML documentation
cd docs
make html

# View documentation
open _build/html/index.html  # On macOS
xdg-open _build/html/index.html  # On Linux
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure to:
- Update tests as appropriate
- Follow the existing code style
- Update documentation as needed
- Add entry to CHANGELOG.md

## Citation

If you use this package in your research, please cite both this implementation and the original UTCI paper:

```bibtex
@software{utci_python,
  author = {Marvell},
  title = {UTCI: Python Implementation of Universal Thermal Climate Index},
  year = {2024},
  url = {https://github.com/marvell/utci}
}

@article{brode2012utci,
  title={Deriving the operational procedure for the Universal Thermal Climate Index (UTCI)},
  author={Br{\"o}de, Peter and Fiala, Dusan and B{\l}a{\.z}ejczyk, Krzysztof and Holm{\'e}r, Ingvar and Jendritzky, Gerd and Kampmann, Bernhard and Tinz, Birger and Havenith, George},
  journal={International Journal of Biometeorology},
  volume={56},
  number={3},
  pages={481--494},
  year={2012},
  publisher={Springer},
  doi={10.1007/s00484-011-0454-1}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This Python implementation is based on the original UTCI Fortran code developed by:
- Peter Bröde
- Dusan Fiala
- Krzysztof Błażejczyk
- Igor Holmér
- Gerd Jendritzky
- Bernhard Kampmann
- and the members of COST Action 730

The original work was released for public use after the termination of COST Action 730.

## Related Projects

- [ladybug-comfort](https://github.com/ladybug-tools/ladybug-comfort): Comprehensive thermal comfort library
- [pythermalcomfort](https://github.com/CenterForTheBuiltEnvironment/pythermalcomfort): Various thermal comfort indices
- [bioclimatic](https://github.com/pyet-org/bioclimatic): Bioclimatic indices calculations

## Support

If you encounter any problems or have suggestions, please [open an issue](https://github.com/marvell/utci/issues) on GitHub.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

## Roadmap

- [ ] Add vectorized operations support for NumPy arrays
- [ ] Implement additional thermal comfort indices
- [ ] Add climate data integration capabilities
- [ ] Create web-based calculator interface
- [ ] Develop comprehensive documentation with Jupyter notebooks

---

**Note**: This is not an official implementation. For the original reference implementation and additional information about UTCI, visit [utci.org](http://www.utci.org/).