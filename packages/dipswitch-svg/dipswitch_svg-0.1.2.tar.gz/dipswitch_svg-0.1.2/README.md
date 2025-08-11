# dipswitch_svg

![release badge](https://codeberg.org/pengumc/dipswitch_svg/badges/release.svg)

SVG generation for dipswitch documentation

Also available online: https://pengumc.codeberg.page/dipswitch_svg/

Example output:  
![Note: image not available on pypi, see source repo](./example.svg)

## Usage

```py
from dipswitch_svg import dipswitch
svg_text = dipswitch("dipswitch 1", range(1, 9), 0x1)
```

## Installation

```shell
pip install dipswitch-svg
```