import tempfile
from pathlib import Path

import pandas as pd
import pytest

erd = pytest.importorskip("src.rag_sql.erd_generator")


def test_build_mermaid_and_png_with_fk():
    df_a = pd.DataFrame({"id": [1, 2], "val": [10, 20]})
    df_b = pd.DataFrame({"id": [1, 2], "a_id": [1, 2]})
    tables = {"a": df_a, "b": df_b}
    pkfk = {
        "a": {"primary_key": "id", "foreign_keys": []},
        "b": {"primary_key": "id", "foreign_keys": [("b", "a_id", "a", "id")]},
    }

    mermaid = erd.build_mermaid_erd(tables, pkfk)
    assert "b }o--|| a" in mermaid or "b }o--|| a" in mermaid.replace(" ", "")

    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "test_erd.png"
        png_path = erd.build_png_erd(tables, pkfk, output_path=str(out))
        assert Path(png_path).exists(), "ERD PNG should be generated"
