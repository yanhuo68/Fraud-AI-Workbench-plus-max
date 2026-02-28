import streamlit as st
from pathlib import Path
import pandas as pd
from src.rag_sql.erd_generator import build_mermaid_erd, build_png_erd
from src.agents.llm_router import get_api_key, init_llm

def render_erd_tab():
    st.header("📊 ERD Diagram")

    if (
        "table_dataframes" not in st.session_state
        or not st.session_state.table_dataframes
    ):
        st.warning("📊 No tables available yet")
        st.info("""
        **To get started:**
        1. 👈 Go to the **Upload Data** tab
        2. Upload your CSV files
        3. Come back here to visualize table relationships!
        
        Once you upload data, you'll be able to:
        ✨ Auto-generate Entity Relationship Diagrams (ERD)
        🔗 Visualize Primary Key / Foreign Key relationships
        📋 Export ERD as PNG for documentation
        """)
        return
    else:
        all_tables = st.session_state.table_dataframes
        all_pkfk = st.session_state.table_pkfk if "table_pkfk" in st.session_state else {}

        selected_tables = st.multiselect(
            "Select tables to include in ERD",
            list(all_tables.keys()),
            default=list(all_tables.keys()),
        )

        # State management for ERD visibility
        if "erd_visible" not in st.session_state:
            st.session_state.erd_visible = False
        if "last_erd_selection" not in st.session_state:
            st.session_state.last_erd_selection = []

        # Reset visibility if selection changes
        if selected_tables != st.session_state.last_erd_selection:
            st.session_state.erd_visible = False
            st.session_state.last_erd_selection = selected_tables

        if not selected_tables:
            st.warning("Select at least one table to generate ERD.")
            st.session_state.erd_visible = False
        else:
            tables = {k: all_tables[k] for k in selected_tables if k in all_tables}
            pkfk_map = {k: v for k, v in all_pkfk.items() if k in selected_tables}

            # Paths
            erd_dir = Path("data/erd")
            erd_dir.mkdir(parents=True, exist_ok=True)
            mermaid_path = erd_dir / "erd_selected.mmd"
            png_path = erd_dir / "erd_selected.png"
            generated = False # Initialize to avoid NameError

            # Generate Button
            if st.button("🖼️ Generate ERD Preview", use_container_width=True):
                with st.spinner("Generating ERD diagram..."):
                    # 1. Build Mermaid
                    mermaid_text = build_mermaid_erd(tables, pkfk_map)
                    mermaid_path.write_text(mermaid_text, encoding="utf-8")

                    # 2. Build PNG
                    try:
                        rendered_path = build_png_erd(tables, pkfk_map, output_path=str(png_path))
                        png_path = Path(rendered_path)
                        if png_path.exists():
                            st.session_state.erd_visible = True
                            st.success("✅ ERD diagram generated successfully!")
                        else:
                            st.error("❌ PNG file not found after generation")
                    except NameError as ne:
                        st.warning(f"NameError encountered: {ne}. Trying fallback...")
                        # Fallback logic
                        try:
                            from graphviz import Digraph
                            import pathlib as _pl
                            dot = Digraph("ERD", format="png")
                            dot.attr(rankdir="LR")
                            for tbl, df in tables.items():
                                pk = pkfk_map.get(tbl, {}).get("primary_key")
                                label = f"<<TABLE BORDER='1' CELLBORDER='1' CELLSPACING='0'><TR><TD COLSPAN='2'><B>{tbl}</B></TD></TR>"
                                for col in df.columns:
                                    if pk and pk == col:
                                        label += f"<TR><TD><B>{col}</B></TD><TD>PK</TD></TR>"
                                    else:
                                        label += f"<TR><TD>{col}</TD><TD></TD></TR>"
                                label += "</TABLE>>"
                                dot.node(tbl, label=label, shape="plaintext")
                            for t, meta in pkfk_map.items():
                                for fk in meta.get("foreign_keys", []):
                                     a, ca, b, pb = fk
                                     dot.edge(a, b, label=f"{ca} → {pb}")
                            out_base = _pl.Path(png_path)
                            out_base.parent.mkdir(parents=True, exist_ok=True)
                            rendered_path = _pl.Path(dot.render(str(out_base.with_suffix("")), cleanup=True))
                            
                            candidates = [
                                rendered_path,
                                rendered_path.with_suffix(".png"),
                                _pl.Path(str(out_base) + ".png"),
                                _pl.Path(str(out_base) + ".png.png"),
                            ]
                            for cand in candidates:
                                if cand.exists():
                                    png_path = cand
                                    st.session_state.erd_visible = True
                                    st.success("✅ ERD diagram generated (fallback method)")
                                    break
                        except Exception as e:
                            st.error(f"Failed to generate ERD PNG (fallback): {e}")
                            st.error("Please ensure graphviz is installed: `apt-get install graphviz` or `brew install graphviz`")
                    except Exception as e:
                        st.error(f"Failed to generate ERD PNG: {e}")
                        st.error("Please ensure graphviz is installed: `apt-get install graphviz` or `brew install graphviz`")
                    
                    # Store mermaid text in session for display
                    st.session_state.erd_mermaid_code = mermaid_text

            # Display Logic
            if st.session_state.get("erd_visible") and png_path.exists():
                
                # Show mermaid code for debugging (only if visible)
                if "erd_mermaid_code" in st.session_state:
                    with st.expander("📝 Mermaid ERD Code", expanded=False):
                        st.code(st.session_state.erd_mermaid_code, language="mermaid")
                        st.info("You can copy this code to render in tools like Mermaid Live Editor or GitHub markdown.")

                st.subheader("ERD Preview")
                st.image(str(png_path))
                
                # Describe relationships
                rels = []
                for tbl, meta in pkfk_map.items():
                    for fk in meta.get("foreign_keys", []):
                        a, ca, b, pb = fk
                        rels.append(f"- **{a}.{ca} → {b}.{pb}** (FK)")
                if rels:
                    st.markdown("**Table relationships**")
                    st.markdown("\n".join(rels))
                else:
                    st.info("No foreign-key relationships detected for the selected tables.")
                
                # --- LLM Data Modeling Insights ---
                st.markdown("---")
                st.subheader("🧠 Data Modeling Insights")
                
                openai_key = get_api_key("OPENAI_API_KEY") or ""
                has_valid_key = openai_key and not openai_key.startswith("your") and not openai_key.startswith("sk-your")
                
                if not has_valid_key:
                    st.info("""
                    💡 **LLM-powered insights available with API key**
                    
                    Configure your OpenAI API key (sidebar or environment) to get automated analysis of:
                    - Data model quality & normalization
                    - Relationship patterns & integrity
                    - Fraud detection optimization opportunities
                    - Schema design recommendations
                    """)
                else:
                    if st.button("🔍 Generate Data Modeling Analysis", use_container_width=True):
                        with st.spinner("Analyzing data model..."):
                            try:
                                # Build schema summary for LLM
                                schema_summary = []
                                for tbl, df in tables.items():
                                    pk = pkfk_map.get(tbl, {}).get("primary_key", "None")
                                    fks = pkfk_map.get(tbl, {}).get("foreign_keys", [])
                                    cols = ", ".join(df.columns.tolist())
                                    schema_summary.append(f"**{tbl}**")
                                    schema_summary.append(f"  - Primary Key: {pk}")
                                    schema_summary.append(f"  - Columns ({len(df.columns)}): {cols}")
                                    schema_summary.append(f"  - Data Types: {dict(df.dtypes.astype(str))}")
                                    if fks:
                                        schema_summary.append(f"  - Foreign Keys: {fks}")
                                
                                relationships_summary = "\n".join(rels) if rels else "No relationships detected"
                                
                                prompt = f"""You are a senior data architect and fraud analytics expert.

Analyze this database schema for a fraud detection system:

{chr(10).join(schema_summary)}

**Detected Relationships:**
{relationships_summary}

Provide a comprehensive data modeling analysis covering:

1. **Schema Quality Assessment**
   - Normalization level (1NF, 2NF, 3NF, BCNF)
   - Potential redundancy or denormalization issues
   - Data integrity concerns

2. **Relationship Analysis**
   - Cardinality patterns (1:1, 1:N, N:M)
   - Referential integrity status
   - Missing relationships that should exist

3. **Fraud Detection Optimization**
   - Tables/fields critical for fraud detection
   - Recommended indexes for investigations
   - Temporal patterns to track (timestamps, sequences)
   - Entity linking opportunities (users, transactions, devices)

4. **Schema Design Recommendations**
   - Missing tables or fields for fraud analysis
   - Suggested improvements (audit logs, flags, metadata)
   - Partitioning or archival strategies

5. **Query Performance Considerations**
   - Complex join patterns to watch
   - Potential performance bottlenecks
   - Recommended materialized views or aggregations

Format your response with clear headings and bullet points. Be specific and actionable.
"""
                                
                                llm = init_llm(st.session_state.get("selected_llm", "openai:gpt-4o-mini"))
                                response = llm.invoke(prompt)
                                analysis = response.content if hasattr(response, "content") else str(response)
                                
                                st.markdown(analysis)
                                
                                # Save analysis
                                analysis_path = erd_dir / "erd_analysis.md"
                                analysis_path.write_text(f"# ERD Data Modeling Analysis\n\n{analysis}", encoding="utf-8")
                                st.success("✅ Analysis complete! Saved to data/erd/erd_analysis.md")
                                
                            except Exception as e:
                                error_msg = str(e)
                                if "401" in error_msg or "AuthenticationError" in error_msg:
                                    st.error("❌ API key authentication failed. Please check your OpenAI API key.")
                                else:
                                    st.error(f"❌ Analysis failed: {error_msg}")
            elif st.session_state.get("erd_visible") and not png_path.exists():
                st.warning("ERD PNG not found or failed to generate.")
            else:
                st.info("👆 Click 'Generate ERD Preview' button above to render the diagram.")

            # Download buttons
            st.markdown("---")
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    "⬇️ Download ERD PNG",
                    data=open(png_path, "rb").read() if png_path and Path(png_path).exists() else b"",
                    file_name=Path(png_path).name if png_path else "erd.png",
                    disabled=not (png_path and Path(png_path).exists()),
                    use_container_width=True
                )
            with col_dl2:
                st.download_button(
                    "⬇️ Download Mermaid Source",
                    data=mermaid_path.read_text(encoding="utf-8"),
                    file_name=mermaid_path.name,
                    use_container_width=True
                )
