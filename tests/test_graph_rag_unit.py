import tempfile
from pathlib import Path

import pytest

from src.rag_sql import graph_rag as gr


def test_build_and_query_graph_simple_corpus():
    # Force embedding off to keep test light/fast
    gr._has_st = False  # type: ignore
    with tempfile.TemporaryDirectory() as tmpdir:
        corpus_path = Path(tmpdir) / "corpus.txt"
        corpus_path.write_text(
            "# table_a\nuser id links to transactions\n"
            "# table_b\ntransaction id amount fraud\n",
            encoding="utf-8",
        )
        out_dir = Path(tmpdir) / "graph"
        out_dir.mkdir(parents=True, exist_ok=True)

        graph = gr.build_graph_store(corpus_path, out_dir)
        assert "nodes" in graph and graph["nodes"], "Graph store should have nodes"

        res = gr.query_graph("transactions fraud amount", top_k=3, out_dir=out_dir)
        assert res["top_snippets"], "Should return top snippets"
        assert isinstance(res["context"], str)


def test_parse_structured_filters():
    filters = gr.parse_structured_filters("payment_method = Debit Card and amount = 100")
    assert ("payment_method", "Debit Card") in filters
    assert ("amount", "100") in filters
