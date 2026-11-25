"""Run a reproducible exploratory comparison from a curated metadata manifest."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import mannwhitneyu

from .features import extract_features
from .swc import read_swc

REQUIRED = {"neuron_id", "brain_region", "species", "cell_type", "swc_path", "archive", "doi"}
FEATURES = [
    "node_count", "branch_points", "terminal_tips",
    "dendritic_length_um", "dendritic_extent_um", "mean_dendritic_radius_um",
]


def run(manifest_path: Path, output_dir: Path) -> pd.DataFrame:
    manifest = pd.read_csv(manifest_path)
    missing = REQUIRED - set(manifest.columns)
    if missing:
        raise ValueError(f"Manifest missing columns: {', '.join(sorted(missing))}")

    output_dir.mkdir(parents=True, exist_ok=True)
    root = manifest_path.resolve().parent.parent
    rows, failures = [], []

    for record in manifest.to_dict(orient="records"):
        swc_path = (root / str(record["swc_path"])).resolve()
        try:
            parsed = read_swc(swc_path)
            row = {key: record[key] for key in REQUIRED}
            row.update(extract_features(parsed))
            rows.append(row)
        except Exception as exc:
            failures.append({"neuron_id": record["neuron_id"], "swc_path": str(swc_path), "reason": str(exc)})

    results = pd.DataFrame(rows)
    if results.empty:
        raise RuntimeError("No usable SWC files. See failures.csv for details.")
    results.to_csv(output_dir / "morphology_features.csv", index=False)
    pd.DataFrame(failures, columns=["neuron_id", "swc_path", "reason"]).to_csv(
        output_dir / "failures.csv", index=False
    )

    summaries = results.groupby("brain_region")[FEATURES].agg(["count", "mean", "median", "std"])
    summaries.to_csv(output_dir / "group_summary.csv")

    regions = sorted(results["brain_region"].dropna().unique())
    comparisons = []
    if len(regions) == 2:
        left = results[results["brain_region"] == regions[0]]
        right = results[results["brain_region"] == regions[1]]
        for feature in FEATURES:
            x, y = left[feature].dropna(), right[feature].dropna()
            if len(x) and len(y):
                test = mannwhitneyu(x, y, alternative="two-sided")
                comparisons.append({
                    "feature": feature, "group_1": regions[0], "n_1": len(x),
                    "group_2": regions[1], "n_2": len(y),
                    "u_statistic": test.statistic, "p_value_exploratory": test.pvalue,
                })
    pd.DataFrame(comparisons).to_csv(output_dir / "exploratory_tests.csv", index=False)

    for feature in FEATURES:
        fig, ax = plt.subplots(figsize=(7, 4))
        data = [results.loc[results["brain_region"] == region, feature].dropna() for region in regions]
        if data and any(len(values) for values in data):
            ax.boxplot(data, labels=regions, showmeans=True)
            ax.set_title(feature.replace("_", " ").title())
            ax.set_ylabel("µm" if feature.endswith("_um") else "Count")
            ax.tick_params(axis="x", rotation=15)
            fig.tight_layout()
            fig.savefig(output_dir / f"{feature}.png", dpi=160)
        plt.close(fig)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    result = run(args.manifest, args.output_dir)
    print(f"Processed {len(result)} neurons. Results saved to {args.output_dir}")


if __name__ == "__main__":
    main()
