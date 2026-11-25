"""Minimal, validated reader for the SWC neuron morphology format."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

SWC_COLUMNS = ["node_id", "node_type", "x", "y", "z", "radius", "parent_id"]


@dataclass
class SWCReadResult:
    nodes: pd.DataFrame
    warnings: list[str]


def read_swc(path: str | Path) -> SWCReadResult:
    """Read an SWC file, ignoring comments/blank lines and validating its structure."""
    path = Path(path)
    rows: list[list[float]] = []
    warnings: list[str] = []

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 7:
                warnings.append(f"Line {line_number}: expected 7 columns, found {len(parts)}")
                continue
            try:
                rows.append([float(value) for value in parts[:7]])
            except ValueError:
                warnings.append(f"Line {line_number}: non-numeric value")
    
    if not rows:
        raise ValueError(f"No valid SWC nodes found in {path}")

    frame = pd.DataFrame(rows, columns=SWC_COLUMNS)
    if frame["node_id"].duplicated().any():
        raise ValueError(f"Duplicate node IDs in {path}")
    if not np.all(np.equal(frame["node_id"], frame["node_id"].astype(int))):
        raise ValueError(f"Node IDs must be integers in {path}")
    if not np.all(np.equal(frame["parent_id"], frame["parent_id"].astype(int))):
        raise ValueError(f"Parent IDs must be integers in {path}")

    frame["node_id"] = frame["node_id"].astype(int)
    frame["node_type"] = frame["node_type"].astype(int)
    frame["parent_id"] = frame["parent_id"].astype(int)

    known_ids = set(frame["node_id"])
    missing = sorted(set(frame.loc[frame["parent_id"] >= 0, "parent_id"]) - known_ids)
    if missing:
        warnings.append(f"{len(missing)} parent references are missing")
    if (frame["radius"] < 0).any():
        warnings.append("Negative radius values found")
    if not np.isfinite(frame[["x", "y", "z", "radius"]].to_numpy()).all():
        raise ValueError(f"Non-finite coordinate or radius in {path}")

    return SWCReadResult(nodes=frame, warnings=warnings)
