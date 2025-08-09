# esi-utils-transfer

## Introduction

Utility package for transferring files via pdl, ftp, email and other protocols
as used by ShakeMap and PAGER. 

## Installation

From repository base, run
```
conda create --name transfer pip
conda activate transfer
pip install git+https://code.usgs.gov/ghsc/esi/esi-utils-io
pip install -r requirements.txt .
```

## Tests

```
pip install pytest
pytest .
```
