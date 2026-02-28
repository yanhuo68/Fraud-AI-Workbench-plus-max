# RAG Comparison Tab Implementation

## Overview
Add a new "RAG Comparison" tab that allows users to compare the quality, performance, and characteristics of SQL RAG, KB RAG, and Graph RAG against the same question.

## Quick Fix: Rename KB Chat → KB RAG
Change tab label from "KB Chat" to "KB RAG" for consistency with other RAG naming.

## RAG Comparison Tab Features

### User Experience
1. **Input Section**
   - Sample question selector (with common fraud investigation questions)
   - Custom question input
   - "Run All RAG Methods" button
   
2. **Results Display** (3 columns side-by-side)
   - SQL RAG results
   - KB RAG results  
   - Graph RAG results
   
3. **Comparison Metrics**
   - **Performance Metrics**:
     - Response time (seconds)
     - Tokens used
     - API calls made
   
   - **Quality Metrics** (LLM-judged):
     - Relevance score (1-10)
     - Completeness score (1-10)
     - Accuracy score (1-10)
     - Overall rating
   
   - **Result Characteristics**:
     - Answer length (words/characters)
     - Data sources used
     - Confidence indicators
     - SQL queries generated (for SQL RAG)
     - Snippets retrieved (for KB/Graph RAG)

4. **Winner Selection**
   - Automated "best answer" based on combined metrics
   - Color-coded highlighting (🥇 🥈 🥉)

### Implementation Approach

#### Sample Questions
Generate fraud-specific questions that work across all three RAG types:
```python
comparison_questions = [
    "What are the most common fraud indicators in transactions?",
    "How can we detect anomalous payment patterns?",
    "What role does device fingerprinting play in fraud detection?",
    "Explain the relationship between user location and fraud risk",
    "What are best practices for threshold tuning in fraud models?"
]
```

#### Parallel Execution
```python
async def run_all_rag_methods(question, llm_id):
    import asyncio
    
    results = {}
    
    # Run all three in parallel
    sql_task = run_sql_rag(question, llm_id)
    kb_task = run_kb_rag(question, llm_id)
    graph_task = run_graph_rag(question, llm_id)
    
    results['sql'], results['kb'], results['graph'] = await asyncio.gather(
        sql_task, kb_task, graph_task
    )
    
    return results
```

#### Quality Evaluation (LLM Judge)
Use an LLM to evaluate answer quality:
```python
def evaluate_answer_quality(question, answer, llm_id):
    prompt = f"""
You are evaluating the quality of an AI-generated answer to a fraud detection question.

Question: {question}

Answer: {answer}

Rate the answer on these criteria (1-10 scale):
1. Relevance - Does it answer the question?
2. Completeness - Does it cover all key aspects?
3. Accuracy - Is the information correct?
4. Clarity - Is it well-explained?

Return JSON format:
{{
  "relevance": <score>,
  "completeness": <score>,
  "accuracy": <score>,
  "clarity": <score>,
  "overall": <average>,
  "reasoning": "<brief explanation>"
}}
"""
    # Call LLM for evaluation
    ...
```

#### Performance Tracking
```python
import time

def track_performance(func):
    start_time = time.time()
    result = func()
    elapsed = time.time() - start_time
    
    return {
        'result': result,
        'time': elapsed,
        'timestamp': time.time()
    }
```

## Proposed Changes

### [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-plus-max/app/dashboard.py)

#### 1. Rename KB Chat tab
```python
# Line ~420
tabs = st.tabs([
    "🏠 Home",
    "📁 Upload Data", 
    "🔍 SQL RAG",
    "💬 KB RAG",  # Changed from "KB Chat"
    "🧭 Graph RAG",
    "⚖️ RAG Comparison",  # New tab
    "🤖 Agents Demo"
])

tab_home, tab_upload, tab_sql, tab_kb, tab_graph, tab_comparison, tab_agents = tabs
```

#### 2. Add RAG Comparison tab implementation
After the Graph RAG tab section, add:

```python
# ---------------------------------------------------------
#  TAB 6: RAG Comparison
# ---------------------------------------------------------
with tab_comparison:
    st.header("⚖️ RAG Comparison")
    st.caption("Compare SQL RAG, KB RAG, and Graph RAG side-by-side on the same question")
    
    # Sample questions
    comparison_questions = [
        "What are the top 3 fraud indicators in transactions?",
        "How does device fingerprinting help detect fraud?",
        "Explain the relationship between user behavior and fraud risk",
        "What are best practices for handling imbalanced fraud datasets?",
        "How can graph analysis improve fraud detection?"
    ]
    
    st.markdown("### Select or Enter Question")
    picked_q = st.selectbox("Sample comparison questions", comparison_questions, key="comp_q")
    
    question = st.text_area(
        "Question for all RAG methods",
        value=picked_q,
        height=100
    )
    
    # LLM selection
    comparison_llm = st.selectbox(
        "LLM for all RAG methods",
        st.session_state.get("available_llms", []),
        key="comparison_llm"
    )
    
    # Options
    col1, col2 = st.columns(2)
    with col1:
        run_quality_eval = st.checkbox("Run quality evaluation (LLM judge)", value=True)
    with col2:
        show_full_responses = st.checkbox("Show full responses", value=True)
    
    if st.button("🚀 Run All RAG Methods", type="primary"):
        if not question.strip():
            st.warning("Please enter a question")
        else:
            results = {}
            
            # Run each RAG method with performance tracking
            with st.spinner("Running SQL RAG..."):
                start = time.time()
                try:
                    # Call SQL RAG logic
                    sql_answer = run_sql_rag_comparison(question, comparison_llm)
                    results['sql'] = {
                        'answer': sql_answer,
                        'time': time.time() - start,
                        'success': True
                    }
                except Exception as e:
                    results['sql'] = {'error': str(e), 'success': False}
            
            with st.spinner("Running KB RAG..."):
                start = time.time()
                try:
                    kb_answer = run_kb_rag_comparison(question, comparison_llm)
                    results['kb'] = {
                        'answer': kb_answer,
                        'time': time.time() - start,
                        'success': True
                    }
                except Exception as e:
                    results['kb'] = {'error': str(e), 'success': False}
            
            with st.spinner("Running Graph RAG..."):
                start = time.time()
                try:
                    graph_answer = run_graph_rag_comparison(question, comparison_llm)
                    results['graph'] = {
                        'answer': graph_answer,
                        'time': time.time() - start,
                        'success': True
                    }
                except Exception as e:
                    results['graph'] = {'error': str(e), 'success': False}
            
            # Quality evaluation
            if run_quality_eval:
                st.markdown("---")
                st.subheader("📊 Quality Evaluation")
                
                with st.spinner("Evaluating answer quality..."):
                    for method in ['sql', 'kb', 'graph']:
                        if results[method].get('success'):
                            eval_result = evaluate_rag_answer(
                                question, 
                                results[method]['answer'],
                                comparison_llm
                            )
                            results[method]['evaluation'] = eval_result
            
            # Display comparison
            st.markdown("---")
            st.subheader("📋 Results Comparison")
            
            col_sql, col_kb, col_graph = st.columns(3)
            
            with col_sql:
                st.markdown("### 🔍 SQL RAG")
                if results['sql'].get('success'):
                    st.metric("Response Time", f"{results['sql']['time']:.2f}s")
                    if 'evaluation' in results['sql']:
                        st.metric("Quality Score", 
                                 f"{results['sql']['evaluation']['overall']:.1f}/10")
                    if show_full_responses:
                        st.markdown(results['sql']['answer'])
                else:
                    st.error(f"Failed: {results['sql'].get('error')}")
            
            with col_kb:
                st.markdown("### 💬 KB RAG")
                if results['kb'].get('success'):
                    st.metric("Response Time", f"{results['kb']['time']:.2f}s")
                    if 'evaluation' in results['kb']:
                        st.metric("Quality Score",
                                 f"{results['kb']['evaluation']['overall']:.1f}/10")
                    if show_full_responses:
                        st.markdown(results['kb']['answer'])
                else:
                    st.error(f"Failed: {results['kb'].get('error')}")
            
            with col_graph:
                st.markdown("### 🧭 Graph RAG")
                if results['graph'].get('success'):
                    st.metric("Response Time", f"{results['graph']['time']:.2f}s")
                    if 'evaluation' in results['graph']:
                        st.metric("Quality Score",
                                 f"{results['graph']['evaluation']['overall']:.1f}/10")
                    if show_full_responses:
                        st.markdown(results['graph']['answer'])
                else:
                    st.error(f"Failed: {results['graph'].get('error')}")
            
            # Winner determination
            if run_quality_eval:
                st.markdown("---")
                st.subheader("🏆 Winner Analysis")
                
                successful = {k: v for k, v in results.items() 
                             if v.get('success') and 'evaluation' in v}
                
                if successful:
                    # Rank by quality score
                    ranked = sorted(successful.items(), 
                                   key=lambda x: x[1]['evaluation']['overall'],
                                   reverse=True)
                    
                    medals = ["🥇", "🥈", "🥉"]
                    for i, (method, data) in enumerate(ranked[:3]):
                        medal = medals[i] if i < 3 else ""
                        st.markdown(f"{medal} **{method.upper()} RAG**: "
                                   f"{data['evaluation']['overall']:.1f}/10 "
                                   f"({data['time']:.2f}s)")
```

## Verification Plan

1. **Test tab rename**: Verify "KB RAG" appears correctly
2. **Test RAG Comparison**:
   - Run comparison with sample questions
   - Verify all three RAG methods execute
   - Check performance metrics display
   - Validate quality evaluation scores
   - Confirm winner highlighting works

## Alternative Approaches

### Option 1: Simpler Comparison (No LLM Judge)
- Just show responses side-by-side
- Manual user evaluation
- Focus on performance metrics only

### Option 2: Advanced Metrics
- Add context retrieval metrics (precision/recall)
- Track source attribution
- Measure hallucination detection
- Cost comparison (API tokens)

### Option 3: Interactive Judging
- Let user rate each answer
- Collect feedback for improvement
- Build preference dataset

## Recommendation

Start with **Option 1** (simpler comparison without LLM judge initially), then add quality evaluation as enhancement. This allows faster implementation and user can manually assess quality.

Key advantages:
- Side-by-side comparison for easy manual evaluation
- Performance metrics (time) are objective
- Can add LLM judge later if needed
- Lower complexity, faster to implement
