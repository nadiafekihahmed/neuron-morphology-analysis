# Neuron Morphology Analysis

A reproducible computational-neuroscience project comparing the morphology of mouse neurons from the hippocampus and neocortex using standardized SWC reconstructions from [NeuroMorpho.Org](https://neuromorpho.org/).

## Research question

Do sampled mouse pyramidal neurons from the hippocampus and neocortex differ in measurable structural properties?

This is an exploratory morphology study, not a clinical diagnostic tool and not evidence of disease-specific differences.

## Scope

- Species: mouse
- Cell type: pyramidal (where consistently annotated)
- Regions: hippocampus and neocortex
- Initial target: 10–15 usable reconstructions per region
- Input: standardized SWC files plus a curated metadata manifest
- Outputs: per-neuron morphometrics, descriptive plots, and cautious group comparisons

The sample is intentionally small and exploratory. Neurons may come from different labs, experiments, ages, and reconstruction protocols; these factors must be recorded and discussed rather than treated as biological effects.

## Morphometric features

The pipeline extracts node count, branch-point count, terminal-tip count, dendritic cable length, 3D bounding-box diagonal, and mean dendritic radius. SWC node types follow the standard convention (1 soma, 2 axon, 3 basal dendrite, 4 apical dendrite, 5 fork point, 6 end point, 7 custom).

## Data access

NeuroMorpho.Org provides metadata and standardized morphology files. Its terms require acknowledging NeuroMorpho.Org and citing the original peer-reviewed publication associated with each reconstruction.

A convenient optional downloader is [neuromorphopy](https://neuromorphopy.readthedocs.io/). It requires Python 3.11 or later (the analysis code itself supports Python 3.10+). First inspect valid filter values and preview matching records; do not download until the filters and available sample counts have been checked:

```bash
uv tool install neuromorphopy
neuromorpho fields
```

Create a query file based on the valid field values reported by the CLI. For example (confirm exact values with `neuromorpho fields` before use):

```yaml
filters:
  species: ["mouse"]
  brain_region: ["hippocampus", "neocortex"]
  cell_type: ["pyramidal"]
```

Then preview it:

```bash
neuromorpho preview query.yaml
```

If there are too few records, relax one criterion at a time and document the change. Do not silently mix species or cell classes.

## Repository setup

Python 3.10+

```bash
git clone https://github.com/nadiafekihahmed/neuron-morphology-analysis.git
cd neuron-morphology-analysis
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Place downloaded SWC files under `data/raw/` (this directory is git-ignored). Create `data/manifest.csv` with these columns:

`neuron_id,brain_region,species,cell_type,swc_path,archive,doi`

Use paths relative to the repository root, e.g. `data/raw/neuron_001.swc`.

Run:

```bash
python -m src.run_analysis --manifest data/manifest.csv --output-dir outputs
```

Run the small unit test with `pip install pytest && pytest`.

## Reproducibility and interpretation

- Keep original SWC files unchanged.
- Keep a manifest linking every file to its NeuroMorpho.Org record, archive, and original publication/DOI.
- Exclude malformed files with a logged reason; never silently discard them.
- Report sample sizes and missing metadata.
- The current script reports an exploratory Mann–Whitney U test when exactly two regions are present. Treat p-values cautiously, report sample sizes, inspect distributions, and do not make causal claims.
- Do not upload raw data unless the source terms permit redistribution.

## Project status

Initial analysis scaffold. Dataset feasibility and exact metadata filters are the first checkpoint; no biological conclusions are claimed yet.
