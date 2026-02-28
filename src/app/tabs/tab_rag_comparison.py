import streamlit as st
import pandas as pd
import time
import json
import re

from src.agents.llm_router import init_llm, get_available_llms
from src.rag_sql.knowledge_base import answer_kb_question
from src.rag_sql.graph_rag import query_graph

def render_rag_comparison_tab():
    st.header("⚖️ RAG Comparison")
    st.caption("Compare SQL RAG, KB RAG, and Graph RAG side-by-side on the same question")
    
    # Check if uploaded_tables exists and is not empty
    if "uploaded_tables" not in st.session_state or not st.session_state.uploaded_tables:
        st.warning("📊 No data uploaded yet")
        st.info("""
        **To get started:**
        1. 👈 Go to the **Upload Data** tab
        2. Upload your CSV files
        3. Come back here to compare different RAG techniques!
        
        Once you upload data, you'll be able to:
        ⚖️ Compare SQL, Knowledge Base, and Graph RAG side-by-side
        ⏱️ Analyze performance and accuracy trade-offs
        🧠 Get AI-powered consistency analysis
        """)
        return
    
    # Initialize sample questions in session state if not exists
    if "comparison_questions" not in st.session_state:
        st.session_state.comparison_questions = [
            "What are the top 3 fraud indicators in transactions?",
            "How does device fingerprinting help detect fraud?",
            "Explain the relationship between user behavior and fraud risk",
            "What are best practices for handling imbalanced fraud datasets?",
            "How can graph analysis improve fraud detection?",
            "What columns are most important for fraud detection models?",
            "Describe common fraud patterns in e-commerce transactions",
        ]
    
    # Callback to sync selectbox to text area
    def update_comp_input():
        st.session_state["comp_question_input"] = st.session_state["comp_q_select"]

    st.markdown("### 📝 Select or Enter Question")
    
    # Add refresh button
    col_select, col_refresh = st.columns([5, 1])
    
    with col_refresh:
        if st.button("🔄 Refresh", help="Generate new sample questions using AI", key="refresh_questions"):
            with st.spinner("Generating fresh questions..."):
                try:
                    # Use the first available LLM
                    available_llms = st.session_state.get("available_llms", [])
                    if available_llms:
                        llm_for_gen = available_llms[0]
                        
                        gen_prompt = """Generate 7 diverse fraud investigation questions that would benefit from RAG comparison.

Include a mix of:
- 2 quantitative questions (best for SQL RAG)
- 2 conceptual questions (best for KB RAG)  
- 2 relational questions (best for Graph RAG)
- 1 hybrid question (could work for multiple methods)

Focus on fraud detection, machine learning, analytics, and investigation topics.

Respond ONLY with a JSON array of 7 questions:
["Question 1", "Question 2", ...]"""
                        
                        llm = init_llm(llm_for_gen)
                        resp = llm.invoke(gen_prompt)
                        
                        # Try to extract JSON array from response
                        content = resp.content
                        json_match = re.search(r'\[.*\]', content, re.DOTALL)
                        if json_match:
                            new_questions = json.loads(json_match.group())
                            if isinstance(new_questions, list) and len(new_questions) > 0:
                                st.session_state.comparison_questions = new_questions
                                # Sync the text area to the first new question immediately
                                st.session_state["comp_question_input"] = new_questions[0]
                                st.success(f"✅ Generated {len(new_questions)} new questions!")
                                st.rerun()
                            else:
                                st.error("Generated questions were not in expected format")
                        else:
                            st.error("Could not parse generated questions")
                    else:
                        st.error("No LLMs available for question generation")
                except Exception as e:
                    st.error(f"❌ Error generating questions: {str(e)}")
                    st.info("💡 Next steps: Make sure you have a valid API key configured in the sidebar or environment variables. Try using a different LLM.")
    
    with col_select:
        picked_comparison_q = st.selectbox(
            "Sample comparison questions", 
            st.session_state.comparison_questions, 
            key="comp_q_select",
            on_change=update_comp_input,
        )
    
    comparison_question = st.text_area(
        "Question for all RAG methods",
        value=picked_comparison_q,
        height=100,
        key="comp_question_input",
        help="This question will be sent to SQL RAG, KB RAG, and Graph RAG simultaneously"
    )
    
    
    # LLM selection with scan button
    col_llm, col_scan, col_opts = st.columns([3, 1, 2])
    with col_llm:
        comparison_llm = st.selectbox(
            "LLM for all RAG methods",
            st.session_state.get("available_llms", []),
            key="comparison_llm_select"
        )
    
    with col_scan:
        st.markdown("<br>", unsafe_allow_html=True)  # Align with selectbox
        if st.button("🔍 Scan", help="Scan for local LLMs (Ollama, LM Studio)", key="scan_local_llms_comparison"):
            with st.spinner("Scanning for local LLMs..."):
                
                # Refresh the available LLMs list
                updated_llms = get_available_llms(include_local=True)
                st.session_state["available_llms"] = updated_llms
                
                # Count local LLMs
                local_count = sum(1 for llm in updated_llms if llm.startswith("local_"))
                
                if local_count > 0:
                    st.success(f"✅ Found {local_count} local LLM(s)")
                else:
                    st.info("No local LLMs detected. Make sure Ollama or LM Studio is running.")
                
                st.rerun()
    
    
    with col_opts:
        st.write("")  # Padding
        show_full_responses = st.checkbox("Show full responses", value=True, key="comp_show_full")
    
    # Helper function for LLM fallback with friendly notifications
    def call_llm_with_fallback(prompt, primary_llm_id, context_name=""):
        """
        Try to call LLM with automatic fallback to cloud APIs if local LLM fails.
        Returns tuple: (response_content, actual_llm_used, fallback_occurred)
        """
        
        # Try primary LLM first
        try:
            llm = init_llm(primary_llm_id)
            resp = llm.invoke(prompt)
            return resp.content, primary_llm_id, False
        except Exception as primary_error:
            # If primary failed and it's a local LLM, try fallback to cloud
            if primary_llm_id.startswith("local_"):
                # Get available cloud LLMs
                available_llms = st.session_state.get("available_llms", [])
                cloud_llms = [llm for llm in available_llms if not llm.startswith("local_")]
                
                if cloud_llms:
                    # Try each cloud LLM in order
                    for fallback_llm in cloud_llms:
                        try:
                            llm = init_llm(fallback_llm)
                            resp = llm.invoke(prompt)
                            
                            # Success with fallback!
                            warning_msg = f"⚠️ {context_name}: Local LLM '{primary_llm_id}' failed. Automatically switched to '{fallback_llm}'"
                            st.warning(warning_msg)
                            
                            return resp.content, fallback_llm, True
                        except Exception as fallback_error:
                            continue  # Try next cloud LLM
                    
                    # All cloud LLMs failed too
                    raise Exception(f"Primary LLM '{primary_llm_id}' and all cloud fallbacks failed. Primary error: {str(primary_error)}")
                else:
                    # No cloud LLMs available
                    raise Exception(f"Local LLM '{primary_llm_id}' failed and no cloud LLMs configured. Error: {str(primary_error)}")
            else:
                # Primary was already a cloud LLM, no fallback
                raise primary_error
    
    if st.button("🚀 Run All RAG Methods", type="primary", key="btn_run_all_rag"):
        if not comparison_question.strip():
            st.warning("⚠️ Please enter a question to compare")
        else:
            results = {}
            llm_used_info = {}  # Track which LLM was actually used for each method
            
            st.markdown("---")
            st.subheader("⏱️ Executing RAG Methods...")
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # ========== SQL RAG ==========
            status_text.text("Running SQL RAG...")
            progress_bar.progress(10)
            
            with st.spinner("🔍 SQL RAG processing..."):
                start_time = time.time()
                try:
                    # Simplified SQL RAG - skip complex SQL generation
                    # Just note that SQL RAG requires uploaded tables
                    selected_tables_list = list(st.session_state.get("uploaded_tables", {}).keys())
                    if selected_tables_list:
                        results['sql'] = {
                            'answer': f"SQL RAG would query tables: {', '.join(selected_tables_list)}. Full SQL generation requires the SQL RAG tab.",
                            'time': time.time() - start_time,
                            'success': True,
                            'metadata': {
                                'query': 'N/A - use SQL RAG tab for full SQL generation',
                                'rows': 0,
                                'method': 'SQL RAG'
                            }
                        }
                    else:
                        results['sql'] = {
                            'error': "No tables uploaded for SQL RAG",
                            'time': time.time() - start_time,
                            'success': False
                        }
                        
                except Exception as e:
                    error_msg = f"SQL RAG error: {str(e)}"
                    if "No tables uploaded" in str(e) or "uploaded_tables" in str(e):
                        error_msg += ". 💡 Upload CSV/Excel files in the 'Upload Data' tab first."
                    results['sql'] = {
                        'error': error_msg,
                        'time': time.time() - start_time,
                        'success': False
                    }
            
            progress_bar.progress(40)
            
            # ========== KB RAG ==========
            status_text.text("Running KB RAG...")
            
            with st.spinner("💬 KB RAG processing..."):
                start_time = time.time()
                try:
                    kb_result = answer_kb_question(
                        comparison_question,
                        llm_id=comparison_llm,
                        return_context=True,
                        k=5
                    )
                    
                    results['kb'] = {
                        'answer': kb_result['answer'],
                        'time': time.time() - start_time,
                        'success': True,
                        'metadata': {
                            'sources': len(kb_result.get('contexts', [])),
                            'method': 'KB RAG'
                        }
                    }
                    # Track LLM used (simplified assumption for KB RAG function)
                    llm_used_info['kb'] = {'llm': comparison_llm, 'fallback': False}

                except Exception as e:
                    error_msg = f"KB RAG error: {str(e)}"
                    if "No knowledge-base documents" in str(e) or "docs" in str(e).lower():
                        error_msg += ". 💡 Add .md or .txt files to the ./docs directory and rebuild the knowledge base."
                    elif "api" in str(e).lower() or "key" in str(e).lower():
                        error_msg += ". 💡 Check your API key configuration in the sidebar."
                    results['kb'] = {
                        'error': error_msg,
                        'time': time.time() - start_time,
                        'success': False
                    }
            
            progress_bar.progress(70)
            
            # ========== Graph RAG ==========
            status_text.text("Running Graph RAG...")
            
            with st.spinner("🧭 Graph RAG processing..."):
                start_time = time.time()
                try:
                    graph_result = query_graph(comparison_question, top_k=8)
                    
                    # Generate final answer using graph context with fallback
                    graph_prompt = f"""Using the following graph knowledge base context, answer the question.

Question: {comparison_question}

Context from Graph:
{graph_result['context']}

Provide a clear, concise answer:"""
                    
                    graph_answer, actual_llm, had_fallback = call_llm_with_fallback(
                        graph_prompt, 
                        comparison_llm,
                        context_name="Graph RAG"
                    )
                    
                    results['graph'] = {
                        'answer': graph_answer,
                        'time': time.time() - start_time,
                        'success': True,
                        'metadata': {
                            'snippets': len(graph_result.get('top_snippets', [])),
                            'entities': len(graph_result.get('entities', [])),
                            'method': 'Graph RAG'
                        }
                    }
                    
                    llm_used_info['graph'] = {
                        'llm': actual_llm,
                        'fallback': had_fallback
                    }
                    
                except Exception as e:
                    error_msg = f"Graph RAG error: {str(e)}"
                    if "graph" in str(e).lower() and "not" in str(e).lower():
                        error_msg += ". 💡 Make sure knowledge base documents are uploaded in ./docs directory."
                    elif "api" in str(e).lower() or "key" in str(e).lower():
                        error_msg += ". 💡 Check your API key configuration in the sidebar."
                    elif "llm" in str(e).lower() or "cloud fallbacks failed" in str(e):
                        error_msg += ". 💡 Configure at least one cloud LLM API key (OpenAI, DeepSeek, Google, or Anthropic)."
                    results['graph'] = {
                        'error': error_msg,
                        'time': time.time() - start_time,
                        'success': False
                    }
            
            progress_bar.progress(100)
            status_text.text("✅ All RAG methods completed!")
            time.sleep(0.5)
            status_text.empty()
            progress_bar.empty()
            
            # ========== Display Comparison ==========
            st.markdown("---")
            st.subheader("📊 Results Comparison")
            
            # Create three columns for side-by-side comparison
            col_sql, col_kb, col_graph = st.columns(3)
            
            # SQL RAG Column
            with col_sql:
                st.markdown("### 🔍 SQL RAG")
                if results.get('sql', {}).get('success'):
                    sql_data = results['sql']
                    st.metric("⏱️ Response Time", f"{sql_data['time']:.2f}s")
                    
                    if 'metadata' in sql_data:
                        if 'rows' in sql_data['metadata']:
                            st.metric("📊 Rows Retrieved", sql_data['metadata']['rows'])
                        if 'query' in sql_data['metadata']:
                            with st.expander("🔎 Generated SQL"):
                                st.code(sql_data['metadata']['query'], language="sql")
                    
                    if show_full_responses:
                        st.markdown("#### Answer")
                        st.markdown(sql_data['answer'])
                else:
                    st.error(f"❌ {results.get('sql', {}).get('error', 'Unknown error')}")
            
            # KB RAG Column
            with col_kb:
                st.markdown("### 💬 KB RAG")
                if results.get('kb', {}).get('success'):
                    kb_data = results['kb']
                    st.metric("⏱️ Response Time", f"{kb_data['time']:.2f}s")
                    
                    if 'metadata' in kb_data and 'sources' in kb_data['metadata']:
                        st.metric("📚 Sources Used", kb_data['metadata']['sources'])
                    
                    # Show which LLM was used
                    if 'kb' in llm_used_info:
                        llm_info = llm_used_info['kb']
                        if llm_info.get('fallback'):
                            st.info(f"🔄 LLM Used: `{llm_info['llm']}` (fallback)")
                        else:
                            st.caption(f"🤖 LLM Used: `{llm_info['llm']}`")
                    
                    if show_full_responses:
                        st.markdown("#### Answer")
                        st.markdown(kb_data['answer'])
                else:
                    st.error(f"❌ {results.get('kb', {}).get('error', 'Unknown error')}")
            
            # Graph RAG Column
            with col_graph:
                st.markdown("### 🧭 Graph RAG")
                if results.get('graph', {}).get('success'):
                    graph_data = results['graph']
                    st.metric("⏱️ Response Time", f"{graph_data['time']:.2f}s")
                    
                    if 'metadata' in graph_data:
                        st.metric("🔗 Graph Snippets", graph_data['metadata'].get('snippets', 0))
                    
                    # Show which LLM was used
                    if 'graph' in llm_used_info:
                        llm_info = llm_used_info['graph']
                        if llm_info.get('fallback'):
                            st.info(f"🔄 LLM Used: `{llm_info['llm']}` (fallback)")
                        else:
                            st.caption(f"🤖 LLM Used: `{llm_info['llm']}`")
                    
                    if show_full_responses:
                        st.markdown("#### Answer")
                        st.markdown(graph_data['answer'])
                else:
                    st.error(f"❌ {results.get('graph', {}).get('error', 'Unknown error')}")
            
            # ========== Performance Summary ==========
            st.markdown("---")
            st.subheader("📈 Performance Summary")
            
            successful_methods = {k: v for k, v in results.items() if v.get('success')}
            
            if successful_methods:
                # Create performance comparison
                
                perf_data = []
                for method, data in successful_methods.items():
                    perf_data.append({
                        'Method': method.upper() + ' RAG',
                        'Response Time (s)': data['time']
                    })
                
                perf_df = pd.DataFrame(perf_data)
                
                # Display performance metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    fastest = min(successful_methods.items(), key=lambda x: x[1]['time'])
                    st.metric("🏆 Fastest Method", 
                             f"{fastest[0].upper()} RAG", 
                             f"{fastest[1]['time']:.2f}s")
                
                with col2:
                    avg_time = sum(r['time'] for r in successful_methods.values()) / len(successful_methods)
                    st.metric("⏱️ Average Time", f"{avg_time:.2f}s")
                
                with col3:
                    st.metric("✅ Success Rate", 
                             f"{len(successful_methods)}/3 methods")
                
                # Bar chart of response times
                st.bar_chart(perf_df.set_index('Method'))
                
                # Recommendations
                st.markdown("### 💡 Recommendations")
                
                if fastest[0] == 'kb':
                    st.info("💬 **KB RAG** was fastest - best for general knowledge questions about documents and concepts.")
                elif fastest[0] == 'sql':
                    st.info("🔍 **SQL RAG** was fastest - best for quantitative questions requiring data analysis and aggregation.")
                elif fastest[0] == 'graph':
                    st.info("🧭 **Graph RAG** was fastest - best for questions about relationships and connections between entities.")
            else:
                st.warning("⚠️ No methods completed successfully. Please check your data and try again.")
            
            # ========== PROFESSIONAL INSIGHTS ==========
            if successful_methods:
                st.markdown("---")
                st.subheader("🎯 Professional Insights & Analysis")
                
                # Option to enable LLM-based quality evaluation
                enable_quality_eval = st.checkbox(
                    "Enable Deep Quality Evaluation (uses LLM judge - takes extra time)",
                    value=False,
                    key="enable_deep_eval",
                    help="Uses an LLM to evaluate answer quality on multiple dimensions: relevance, completeness, accuracy, clarity, and specificity"
                )
                
                evaluations = {}
                
                if enable_quality_eval:
                    st.markdown("#### 📊 Quality Evaluation Scores")
                    
                    with st.spinner("Running quality evaluation..."):
                        for method, data in successful_methods.items():
                            # Evaluate quality
                            eval_prompt = f"""You are an expert evaluator assessing AI-generated answers about fraud detection.

Question: {comparison_question}

Answer to evaluate:
{data['answer']}

Rate the answer on these criteria (1-10 scale) and respond ONLY with valid JSON:
{{
  "relevance": <1-10>,
  "completeness": <1-10>,
  "accuracy": <1-10>,
  "clarity": <1-10>,
  "specificity": <1-10>,
  "overall": <average>,
  "strengths": "<brief strengths>",
  "weaknesses": "<brief weaknesses>"
}}"""
                            
                            try:
                                llm = init_llm(comparison_llm)
                                resp = llm.invoke(eval_prompt)
                                
                                # Try to extract JSON from response
                                content = resp.content
                                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                                if json_match:
                                    eval_result = json.loads(json_match.group())
                                    evaluations[method] = eval_result
                                else:
                                    evaluations[method] = {"error": "Could not parse evaluation"}
                            except Exception as e:
                                error_msg = f"Quality evaluation failed: {str(e)}"
                                if "api" in str(e).lower() or "key" in str(e).lower():
                                    error_msg += ". Check API key."
                                evaluations[method] = {"error": error_msg}
                    
                    # Display quality scores
                    if evaluations:
                        col_sql_q, col_kb_q, col_graph_q = st.columns(3)
                        
                        for col, method in zip([col_sql_q, col_kb_q, col_graph_q], ['sql', 'kb', 'graph']):
                            if method in evaluations and 'error' not in evaluations[method]:
                                with col:
                                    method_name = f"{method.upper()} RAG"
                                    st.markdown(f"**{method_name}**")
                                    
                                    eval_data = evaluations[method]
                                    
                                    # Overall score with color
                                    overall = eval_data.get('overall', 0)
                                    if overall >= 8:
                                        st.success(f"⭐ Overall: {overall}/10")
                                    elif overall >= 6:
                                        st.info(f"Overall: {overall}/10")
                                    else:
                                        st.warning(f"Overall: {overall}/10")
                                    
                                    # Individual metrics
                                    for metric in ['relevance', 'completeness', 'accuracy', 'clarity', 'specificity']:
                                        score = eval_data.get(metric, 0)
                                        st.caption(f"{metric.capitalize()}: {score}/10")
                                    
                                    # Strengths and weaknesses
                                    with st.expander("💪 Details"):
                                        st.markdown(f"**Strengths:** {eval_data.get('strengths', 'N/A')}")
                                        st.markdown(f"**Weaknesses:** {eval_data.get('weaknesses', 'N/A')}")
                
                # ========== Answer Similarity Analysis ==========
                st.markdown("---")
                st.markdown("#### 🔄 Answer Consistency Analysis")
                
                with st.spinner("Analyzing answer consistency..."):
                    answers_text = "\n\n".join([
                        f"**{method.upper()} RAG Answer:**\n{data['answer']}"
                        for method, data in successful_methods.items()
                    ])
                    
                    similarity_prompt = f"""Compare these answers to the same question and analyze their consistency.

Question: {comparison_question}

{answers_text}

Respond ONLY with valid JSON:
{{
  "consistency": "<high/medium/low>",
  "agreement_summary": "<what they agree on>",
  "divergence_summary": "<where they differ>",
  "recommended_answer": "<sql/kb/graph>",
  "recommendation_reason": "<why this answer is best>"
}}"""
                    
                    try:
                        llm = init_llm(comparison_llm)
                        resp = llm.invoke(similarity_prompt)
                        
                        content = resp.content
                        json_match = re.search(r'\{.*\}', content, re.DOTALL)
                        if json_match:
                            similarity_analysis = json.loads(json_match.group())
                        else:
                            similarity_analysis = {"error": "Could not parse analysis"}
                    except Exception as e:
                        error_msg = f"Consistency analysis failed: {str(e)}"
                        if "api" in str(e).lower() or "key" in str(e).lower():
                            error_msg += ". 💡 Check your API key configuration."
                        similarity_analysis = {"error": error_msg}
                        st.warning(f"⚠️ {error_msg}")
                
                if 'error' not in similarity_analysis:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        consistency = similarity_analysis.get('consistency', 'unknown').lower()
                        consistency_emoji = {
                            'high': '🟢',
                            'medium': '🟡',
                            'low': '🔴'
                        }.get(consistency, '⚪')
                        
                        st.metric("Consistency Level", 
                                 f"{consistency_emoji} {consistency.upper()}")
                    
                    with col2:
                        recommended = similarity_analysis.get('recommended_answer', 'N/A').upper()
                        st.metric("Recommended Answer", f"{recommended} RAG")
                    
                    st.markdown("**What answers agree on:**")
                    st.success(similarity_analysis.get('agreement_summary', 'N/A'))
                    
                    if similarity_analysis.get('divergence_summary'):
                        st.markdown("**Key differences:**")
                        st.warning(similarity_analysis.get('divergence_summary', 'N/A'))
                    
                    if similarity_analysis.get('recommendation_reason'):
                        st.markdown("**Why this answer is best:**")
                        st.info(similarity_analysis.get('recommendation_reason', 'N/A'))
                
                # ========== Smart Recommendations ==========
                st.markdown("---")
                st.markdown("#### 💡 Smart Recommendations & Use-Case Guide")
                
                # Analyze question type
                question_lower = comparison_question.lower()
                
                quant_keywords = ['how many', 'count', 'sum', 'average', 'total', 'top', 'most', 'least', 'calculate']
                concept_keywords = ['what is', 'explain', 'describe', 'why', 'how does', 'best practice', 'define']
                relationship_keywords = ['relationship', 'connection', 'related', 'linked', 'pattern', 'network', 'between']
                
                is_quantitative = any(kw in question_lower for kw in quant_keywords)
                is_conceptual = any(kw in question_lower for kw in concept_keywords)
                is_relational = any(kw in question_lower for kw in relationship_keywords)
                
                # Show question type analysis
                question_types = []
                if is_quantitative:
                    question_types.append("📊 Quantitative")
                if is_conceptual:
                    question_types.append("📚 Conceptual")
                if is_relational:
                    question_types.append("🔗 Relational")
                
                if question_types:
                    st.markdown(f"**Question Type Detected:** {' + '.join(question_types)}")
                    
                    # Give specific recommendation based on question type
                    if is_quantitative and 'sql' in successful_methods:
                        st.success("✅ **SQL RAG** is ideal for this quantitative question - it can query and aggregate data directly")
                    elif is_relational and 'graph' in successful_methods:
                        st.success("✅ **Graph RAG** is ideal for this relational question - it can traverse entity connections")
                    elif is_conceptual and 'kb' in successful_methods:
                        st.success("✅ **KB RAG** is ideal for this conceptual question - it retrieves relevant knowledge from documents")
                
                # General use-case guide
                with st.expander("📖 Complete RAG Use-Case Guide", expanded=False):
                    st.markdown("""
### 🔍 SQL RAG
**Best for:** Quantitative analysis, data aggregation, filtering, numerical queries

**Example questions:**
- How many fraudulent transactions occurred in Q4 2024?
- What is the average transaction amount by country?
- Show me the top 10 users with highest fraud risk scores
- Calculate the fraud rate by payment method

**Strengths:**
- ✅ Precise numerical results
- ✅ Complex aggregations and filtering
- ✅ Multi-table JOIN queries
- ✅ Fast execution on structured data

**Limitations:**
- ❌ Limited to uploaded table schemas
- ❌ Cannot answer conceptual questions
- ❌ Requires well-structured data

---

### 💬 KB RAG
**Best for:** Conceptual knowledge, best practices, methodology, definitions

**Example questions:**
- What is feature engineering in fraud detection?
- Explain the difference between supervised and unsupervised learning
- What are best practices for handling imbalanced datasets?
- How does SMOTE work?

**Strengths:**
- ✅ Rich conceptual explanations
- ✅ Best practices and methodology
- ✅ Context from multiple documents
- ✅ Flexible natural language queries

**Limitations:**
- ❌ Depends on document quality and coverage
- ❌ Cannot perform calculations
- ❌ May lack specific numerical data

---

### 🧭 Graph RAG
**Best for:** Relationships, entity connections, pattern discovery, network analysis

**Example questions:**
- How are users and devices connected in the fraud detection system?
- What is the relationship between location and transaction risk?
- Explain the fraud detection knowledge graph structure
- What patterns exist between merchants and fraudulent transactions?

**Strengths:**
- ✅ Reveals hidden connections
- ✅ Multi-hop relationship queries
- ✅ Pattern and trend discovery
- ✅ Holistic knowledge integration

**Limitations:**
- ❌ Requires well-structured knowledge base
- ❌ Complex queries may be slower
- ❌ Quality depends on graph construction
                    """)
                
                
                # Performance vs Quality tradeoff
                st.markdown("---")
                st.markdown("#### ⚖️ Performance vs Quality Tradeoff")
                
                # Always create comparison table with performance data
                
                comparison_data = []
                for method in ['sql', 'kb', 'graph']:
                    if method in successful_methods:
                        row = {
                            'Method': f"{method.upper()} RAG",
                            'Speed (s)': f"{successful_methods[method]['time']:.2f}",
                        }
                        
                        # Add quality score if evaluations were run
                        if evaluations and method in evaluations and 'overall' in evaluations[method]:
                            row['Quality Score'] = f"{evaluations[method]['overall']:.1f}/10"
                        elif evaluations:
                            row['Quality Score'] = 'N/A'
                        # Don't add Quality Score column if evaluations weren't run
                        
                        comparison_data.append(row)
                
                if comparison_data:
                    df_comparison = pd.DataFrame(comparison_data)
                    st.dataframe(df_comparison, hide_index=True, width="stretch")
                    
                    if not evaluations:
                        st.caption("💡 Enable 'Deep Quality Evaluation' above to see quality scores in this table")
