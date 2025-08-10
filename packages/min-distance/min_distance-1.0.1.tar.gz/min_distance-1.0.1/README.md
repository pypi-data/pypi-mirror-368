# min_distance

[![PyPI version](https://img.shields.io/pypi/v/min_distance.svg)](https://pypi.org/project/min_distance/)
[![Python Version](https://img.shields.io/pypi/pyversions/min_distance.svg)](https://pypi.org/project/min_distance/)

Calculate the minimum distance between two geographic points (latitude and longitude) using the Haversine formula in Python.

---

## Features

- Simple and lightweight Python package
- Accurate distance calculation on Earth’s surface (in kilometers)
- Easy to integrate into any Python project
- Well-tested with unit tests included

---

## Installation

Install via pip:

```bash
pip install min_distance
```

---

## Usage

```python
from min_distance import calculate_min_distance

lat1, lon1 = 40.7128, -74.0060  # New York
lat2, lon2 = 51.5074, -0.1278   # London

distance_km = calculate_min_distance(lat1, lon1, lat2, lon2)
print(f"Distance: {distance_km:.2f} km")
```

---

## API Reference

### `calculate_min_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float`

Calculate the minimum distance between two points on the Earth specified by latitude and longitude.

- **Parameters:**
  - `lat1`, `lon1`: Latitude and Longitude of the first point in decimal degrees.
  - `lat2`, `lon2`: Latitude and Longitude of the second point in decimal degrees.

- **Returns:** Distance in kilometers as a `float`.

---

## Development

Want to contribute? Feel free to open issues or submit pull requests!

Run tests with:

```bash
python -m unittest discover -s tests
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

Vansh  
[GitHub](https://github.com/vanshbhardwajhere) | [LinkedIn](https://linkedin.com/in/vanshbhardwajhere)
