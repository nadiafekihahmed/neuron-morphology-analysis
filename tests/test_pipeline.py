from pathlib import Path

from src.features import extract_features
from src.swc import read_swc


def test_swc_reader_and_dendritic_features(tmp_path: Path):
    swc = tmp_path / "tiny.swc"
    swc.write_text(
        "# tiny synthetic neuron\n"
        "1 1 0 0 0 2 -1\n"
        "2 3 1 0 0 1 1\n"
        "3 3 2 0 0 1 2\n"
        "4 3 2 1 0 1 3\n"
        "5 3 2 -1 0 1 3\n",
        encoding="utf-8",
    )
    parsed = read_swc(swc)
    features = extract_features(parsed)

    assert features["node_count"] == 5
    assert features["dendritic_branch_points"] == 1
    assert features["dendritic_terminal_tips"] == 2
    assert features["dendritic_length_um"] == 4.0
    assert features["mean_dendritic_radius_um"] == 1.0
    assert features["swc_warnings"] == 0
