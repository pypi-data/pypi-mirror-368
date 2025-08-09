# neuromotifs
Python tools to load neuronal microcircuit geometry, generate geometry-aware null models, and quantify over/under-expression of 3-node motifs.

> Paper: *Neuron Morphological Asymmetry Explains Fundamental Network Stereotypy Across Neocortex* (Gal et al.)

## Install
```bash
pip install neuromotifs
# or, for dev
pip install -e .[dev]
```

## Highlights
- Motif counting for directed triplets (#1-#13)
- Geometry-driven random graph generators (1st-5th order) mirroring the paper’s models
- Reproducibility notebooks for Figures 1-4
- Simple CLI: `neuromotifs motifs`, `neuromotifs generate`, `neuromotifs fit`

## Quickstart
```python
# TBD
```

## Data
- `data/nmc/` contains tiny demonstrators only.
- For full datasets, see `data/README.md` for scripted download instructions.

## Citing
Please cite the paper and this package (see `CITATION.cff`).