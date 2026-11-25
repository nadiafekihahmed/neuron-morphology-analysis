"""Morphometric feature extraction from SWC reconstructions."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .swc import SWCReadResult


def extract_features(result: SWCReadResult) -> dict[str, float | int]:
    nodes = result.nodes.copy()
    children = nodes["parent_id"].value_counts().to_dict()
    nodes["child_count"] = nodes["node_id"].map(children).fillna(0).astype(int)

    dendrites = nodes[nodes["node_type"].isin([3, 4])].copy()
    dendrite_ids = set(dendrites["node_id"])
    by_id = nodes.set_index("node_id")

    lengths = []
    for row in dendrites.itertuples(index=False):
        parent_id = int(row.parent_id)
        if parent_id in by_id.index and int(by_id.loc[parent_id, "node_type"]) in [1, 3, 4]:
            parent = by_id.loc[parent_id]
            lengths.append(float(np.linalg.norm(
                np.array([row.x, row.y, row.z], dtype=float)
                - np.array([parent["x"], parent["y"], parent["z"]], dtype=float)
            )))

    if len(dendrites):
        coords = dendrites[["x", "y", "z"]].to_numpy(dtype=float)
        extent = float(np.linalg.norm(coords.max(axis=0) - coords.min(axis=0)))
        mean_radius = float(dendrites["radius"].mean())
    else:
        extent = float("nan")
        mean_radius = float("nan")

    return {
        "node_count": int(len(nodes)),
        "dendritic_branch_points": int((dendrites["child_count"] > 1).sum()),
        "dendritic_terminal_tips": int((dendrites["child_count"] == 0).sum()),
        "dendritic_length_um": float(sum(lengths)),
        "dendritic_extent_um": extent,
        "mean_dendritic_radius_um": mean_radius,
        "swc_warnings": int(len(result.warnings)),
    }
