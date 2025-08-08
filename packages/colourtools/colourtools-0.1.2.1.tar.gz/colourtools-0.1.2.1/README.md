### colourtools

**colourtools** is a lightweight Python library for intuitive conversion and manipulation of colours across multiple formats.


#### Features

- Convert between **CMYK**, **RGB**, and **HEX** colour spaces
- Support for both integer and floating-point representations
- Simple, readable API for common colour transformations
- Utility functions for encoding and decoding colour values
- Designed for clarity, reliability, and easy integration into your projects


#### Example Usage

```python
from colourtools import cmyk_to_rgb, rgb_to_cmyk, hex_to_rgb

rgb = cmyk_to_rgb((0, 1, 1, 0))       # Convert CMYK to RGB
cmyk = rgb_to_cmyk((255, 0, 0))       # Convert RGB to CMYK
rgb = hex_to_rgb("#FF0000")           # Convert HEX to RGB
```

#### Installation

```bash
pip install colourtools
```


#### License

MIT License

*colourtools* makes colour conversion in Python simple, consistent, and accessible for everyone—no matter how you spell it.

