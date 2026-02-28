from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    import networkx as nx
    _has_nx = True
except Exception:
    _has_nx = False

try:
    from sentence_transformers import SentenceTransformer
    _has_st = True
except Exception:
    _has_st = False


def _tokenize(text: str) -> List[str]:
    return [t.strip(".,:;()[]{}\"'").lower() for t in text.split() if len(t) > 3]


def build_graph_store(
    corpus_path: Path = Path("data/graph/graph_corpus.txt"),
    out_dir: Path = Path("data/graph"),
) -> Dict:
    """
    Build a lightweight graph + TF-IDF index from the text corpus.
    Nodes:
      - entity nodes (tokens)
      - snippet nodes (lines of text)
    Edges: entity -> snippet when the entity appears in the snippet.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    if not corpus_path.exists():
        raise FileNotFoundError(f"Corpus not found: {corpus_path}")

    entity_ids: Dict[str, str] = {}
    nodes: List[Dict] = []
    edges: List[Tuple[str, str, int]] = []
    snippet_ids: List[str] = []
    snippet_texts: List[str] = []

    current_source = "corpus"
    snippet_counter = 0

    for line in corpus_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        if line.startswith("# "):
            current_source = line[2:].strip()
            continue

        snippet_id = f"s{snippet_counter}"
        snippet_counter += 1
        snippet_ids.append(snippet_id)
        snippet_texts.append(line.strip())
        nodes.append(
            {"id": snippet_id, "type": "snippet", "text": line.strip(), "source": current_source}
        )

        tokens = _tokenize(line)
        for tok in tokens:
            if tok not in entity_ids:
                entity_id = f"e{len(entity_ids)}"
                entity_ids[tok] = entity_id
                nodes.append({"id": entity_id, "type": "entity", "text": tok})
            else:
                entity_id = entity_ids[tok]
            edges.append((entity_id, snippet_id, 1))

    # Build TF-IDF over snippet texts
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(snippet_texts)

    # Optional embedding model
    emb_model = None
    emb_matrix = None
    emb_name = None
    if _has_st:
        try:
            emb_model = SentenceTransformer("all-MiniLM-L6-v2")
            emb_matrix = emb_model.encode(snippet_texts, normalize_embeddings=True)
            emb_name = "all-MiniLM-L6-v2"
        except Exception:
            emb_model = None
            emb_matrix = None

    # Persist graph + index artifacts
    graph = {
        "nodes": nodes,
        "edges": [{"src": e[0], "dst": e[1], "weight": e[2]} for e in edges],
        "snippet_ids": snippet_ids,
        "source": str(corpus_path),
        "embedding_model": emb_name,
    }
    (out_dir / "graph_store.json").write_text(json.dumps(graph, indent=2))
    joblib.dump(
        {"vectorizer": vectorizer, "matrix": tfidf_matrix, "snippet_ids": snippet_ids},
        out_dir / "graph_tfidf.joblib",
    )
    if emb_matrix is not None:
        joblib.dump(
            {"embeddings": emb_matrix, "snippet_ids": snippet_ids, "model": emb_name},
            out_dir / "graph_embeds.joblib",
        )

    # Optional networkx graph for path reasoning
    if _has_nx:
        G = nx.DiGraph()
        for n in nodes:
            G.add_node(n["id"], **n)
        for e in edges:
            G.add_edge(e[0], e[1], weight=e[2])
        try:
            nx.write_gpickle(G, out_dir / "graph_nx.gpickle")
        except Exception:
            pass
    return graph


def load_graph_index(out_dir: Path = Path("data/graph")):
    store_path = out_dir / "graph_store.json"
    tfidf_path = out_dir / "graph_tfidf.joblib"
    if not store_path.exists() or not tfidf_path.exists():
        raise FileNotFoundError("Graph store/index not built. Rebuild graph first.")
    graph = json.loads(store_path.read_text())
    tfidf_bundle = joblib.load(tfidf_path)
    embed_bundle = None
    embed_path = out_dir / "graph_embeds.joblib"
    if embed_path.exists():
        embed_bundle = joblib.load(embed_path)
    nx_graph = None
    if _has_nx:
        nx_path = out_dir / "graph_nx.gpickle"
        if nx_path.exists():
            try:
                nx_graph = nx.read_gpickle(nx_path)
            except Exception:
                nx_graph = None
    return graph, tfidf_bundle, embed_bundle, nx_graph


def _embed_query(question: str, embed_bundle: dict) -> Optional[List[float]]:
    if embed_bundle is None:
        return None
    if not _has_st:
        return None
    try:
        model_name = embed_bundle.get("model")
        model = SentenceTransformer(model_name) if model_name else SentenceTransformer("all-MiniLM-L6-v2")
        return model.encode([question], normalize_embeddings=True)[0]
    except Exception:
        return None


def query_graph(question: str, top_k: int = 8, out_dir: Path = Path("data/graph")) -> Dict:
    graph, tfidf_bundle, embed_bundle, nx_graph = load_graph_index(out_dir)
    vectorizer: TfidfVectorizer = tfidf_bundle["vectorizer"]
    matrix = tfidf_bundle["matrix"]
    snippet_ids = tfidf_bundle["snippet_ids"]

    if matrix.shape[0] == 0:
        return {"top_snippets": [], "entities": [], "context": ""}

    q_vec = vectorizer.transform([question])
    sims_tfidf = cosine_similarity(q_vec, matrix).ravel()

    # Embedding similarity (if available)
    sims_emb = None
    if embed_bundle is not None:
        q_emb = _embed_query(question, embed_bundle)
        if q_emb is not None:
            import numpy as np
            emb_matrix = embed_bundle["embeddings"]
            sims_emb = emb_matrix @ q_emb

    # Hybrid scoring: TF-IDF + embedding (if present)
    if sims_emb is not None:
        import numpy as np
        sims = 0.5 * sims_tfidf + 0.5 * sims_emb
    else:
        sims = sims_tfidf

    top_idx = sims.argsort()[::-1][:top_k]

    node_lookup = {n["id"]: n for n in graph["nodes"]}
    edge_list = graph.get("edges", [])
    neighbor_entities = set()
    top_snippets = []
    for idx in top_idx:
        snip_id = snippet_ids[idx]
        snip_node = node_lookup.get(snip_id, {})
        top_snippets.append(
            {
                "id": snip_id,
                "text": snip_node.get("text", ""),
                "source": snip_node.get("source", ""),
                "score": float(sims[idx]),
            }
        )
        for e in edge_list:
            if e["dst"] == snip_id and e["src"].startswith("e"):
                neighbor_entities.add(e["src"])

    entities = [node_lookup[eid]["text"] for eid in neighbor_entities if eid in node_lookup]
    context_lines = []
    for sn in top_snippets:
        context_lines.append(f"- [{sn['source']}] {sn['text']} (score={sn['score']:.4f})")
    if entities:
        context_lines.append("\nEntities connected to top snippets:")
        context_lines.append(", ".join(sorted(entities))[:2000])

    # Simple path explanations: entity -> snippet edges
    path_explanations = []
    if nx_graph is not None:
        for sn in top_snippets[:5]:
            sn_id = sn["id"]
            preds = list(nx_graph.predecessors(sn_id))
            for p in preds:
                pdata = node_lookup.get(p, {})
                if pdata.get("type") == "entity":
                    path_explanations.append(f"{pdata.get('text','entity')} → {sn.get('text','snippet')}")

    return {
        "top_snippets": top_snippets,
        "entities": entities,
        "context": "\n".join(context_lines),
        "paths": path_explanations,
    }


def parse_structured_filters(question: str) -> List[Tuple[str, str]]:
    """Heuristic filter extraction: look for 'X = Y' patterns."""
    import re
    filters = []
    
    # Split by ' and ' (case insensitive) to handle multiple conditions
    # This prevents the regex from greedily consuming the next condition as part of the value
    conditions = re.split(r'\s+and\s+', question, flags=re.IGNORECASE)
    
    patterns = [
        r"([A-Za-z0-9_ ]+)\s*=\s*['\"]?([A-Za-z0-9 _.-]+)['\"]?",
        r"using\s+([A-Za-z0-9_ ]+)\s+(?:as|=)\s+([A-Za-z0-9 _.-]+)",
    ]
    
    for cond in conditions:
        for pat in patterns:
            m = re.search(pat, cond.strip(), flags=re.IGNORECASE)
            if m:
                col = m.group(1).strip()
                val = m.group(2).strip()
                if col and val:
                    filters.append((col, val))
                    break # Stop after first match for this condition
    return filters
    return filters
