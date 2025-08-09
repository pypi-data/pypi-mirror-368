# swatoutpy

A lightweight Python package to read SWAT model (Rev 681) output files: `.rch`, `.sub`, and `.hru`.

## How to install

```bash
pip install swatoutpy
```

## How to use

For `*.rch` files

```bash
from swatoutpy.reader import read_rch

df = read_rch("output_monthly.rch", timestep="monthly")
print(df.head())
```

For `*.sub` files

```bash
from swatoutpy.reader import read_sub

df = read_sub("output_monthly.sub", timestep="monthly")
print(df.head())
```
