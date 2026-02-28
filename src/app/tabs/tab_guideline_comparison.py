import streamlit as st
import pandas as pd
from pathlib import Path
from src.agents.llm_router import init_llm, get_available_llms
from langchain_core.messages import SystemMessage, HumanMessage

def render_guideline_comparison_tab():
    st.header("📋 Fraud Assessment")
    st.caption("Generate comprehensive Fraud Detection and Fraud Risk assessments from your data.")

    # 1. Data Selection
    st.subheader("1. Select Data")
    if "uploaded_tables" not in st.session_state or not st.session_state.uploaded_tables:
        st.warning("📊 No data uploaded yet")
        st.info("""
        **To get started:**
        1. 👈 Go to the **Upload Data** tab
        2. Upload your fraud detection CSV files
        3. Come back here to generate AI-powered assessments!
        
        Once you upload data, you'll be able to:
        ✨ Generate comprehensive fraud detection assessments
        🛡️ Analyze fraud risk patterns
        💡 Get AI-powered recommendations
        """)
        return

    table_names = list(st.session_state.uploaded_tables.keys())
    selected_table = st.selectbox("Select Table for Analysis", table_names, key="gc_table_select")
    
    # Get dataframe
    df = None
    if "table_dataframes" in st.session_state and selected_table in st.session_state.table_dataframes:
        df = st.session_state.table_dataframes[selected_table]
    elif "uploaded_df" in st.session_state: # Fallback if single upload
         df = st.session_state.uploaded_df

    if df is not None:
        st.dataframe(df.head(), width="stretch")
        st.caption(f"Showing first 5 rows of {len(df)} records.")
    else:
        st.error("Could not load data for selected table.")
        return

    # 2. LLM Selection
    st.subheader("2. Select LLM")
    col_llm, col_scan = st.columns([4, 1])
    with col_llm:
        selected_llm = st.selectbox(
            "Select LLM for Analysis",
            st.session_state.get("available_llms", []),
            key="gc_llm_select"
        )
    with col_scan:
        st.write("") # align
        st.write("") 
        if st.button("🔄 Scan", help="Scan for local LLMs", use_container_width=True):
            st.session_state["available_llms"] = get_available_llms(include_local=True)
            st.rerun()


    # 3. Run Assessment
    if st.button("🚀 Generate Assessment", type="primary", use_container_width=True):
        if not selected_llm:
            st.error("Please select an LLM.")
            return

        # Prepare Data Sample (as text)
        data_sample = df.head(10).to_markdown(index=False)
        data_info = str(df.dtypes)
        
        
        llm = init_llm(selected_llm)
        
        # --- Analysis 1: Fraud Detection ---
        sys_msg_detect = SystemMessage(content="""
You are a Senior Fraud Detection Analyst.
Your task is to write a comprehensive fraud detection assessment based on the provided data.

Your assessment should cover:
- Executive summary of fraud detection effectiveness
- Analysis of fraud patterns and anomalies in the data
- Detection performance insights
- Operational effectiveness observations
- Recommendations for improving detection capabilities

Use specific examples and data points from the sample provided.
""")
        
        human_msg_detect = HumanMessage(content=f"""
### Data Structure
{data_info}

### Data Sample (First 10 rows)
{data_sample}

**TASK:**
Write a comprehensive fraud detection assessment analyzing this data.
Use specific transaction examples and data-driven insights.
""")
        
        # --- Analysis 2: Fraud Risk ---
        sys_msg_risk = SystemMessage(content="""
You are a Senior Fraud Risk Officer.
Your task is to write a comprehensive fraud risk assessment based on the provided data.

Your assessment should cover:
- Identification of inherent fraud risks
- Risk control effectiveness evaluation  
- Residual risk assessment
- Risk appetite and threshold analysis
- Risk mitigation and improvement recommendations

Use specific examples and data points from the sample provided.
""")

        human_msg_risk = HumanMessage(content=f"""
### Data Structure
{data_info}

### Data Sample (First 10 rows)
{data_sample}

**TASK:**
Write a comprehensive fraud risk assessment analyzing this data.
Use specific transaction examples and data-driven insights.
""")

        with st.status("Running Analysis...", expanded=True) as status:
            st.write("🕵️ Analyzing Fraud Detection...")
            try:
                resp_detect = llm.invoke([sys_msg_detect, human_msg_detect]).content
            except Exception as e:
                resp_detect = f"Error: {e}"
                
            st.write("🛡️ Analyzing Fraud Risk...")
            try:
                resp_risk = llm.invoke([sys_msg_risk, human_msg_risk]).content
            except Exception as e:
                resp_risk = f"Error: {e}"
            
            st.write("💡 Generating Comparative Insights...")
            
            # --- Comparison ---
            prompt_compare = f"""
Compare the following two assessments of the same data.

### Assessment 1: Fraud Detection (Focus: Identifying patterns)
{resp_detect}

### Assessment 2: Fraud Risk (Focus: Risk prevention)
{resp_risk}

**Instructions:**
1. Highlight the COMMONALITIES (what do both agree on?).
2. Highlight the DIFFERENCES (what unique insights does each angle provide?).
3. Provide RECOMMENDATIONS for improving the documentation (markdown files) to better cover both angles.
"""
            try:
                resp_compare = llm.invoke(prompt_compare).content
            except Exception as e:
                resp_compare = f"Error: {e}"
                
            status.update(label="Analysis Complete!", state="complete", expanded=False)
            
            # Store results in session state
            st.session_state["gc_results"] = {
                "resp_detect": resp_detect,
                "resp_risk": resp_risk,
                "resp_compare": resp_compare,
                # Debug info
                "debug_prompt_detect": sys_msg_detect.content + "\n\n" + human_msg_detect.content,
                "debug_prompt_risk": sys_msg_risk.content + "\n\n" + human_msg_risk.content
            }
            # Rerun to display results from state
            st.rerun()

    # 6. Display Results (from Session State)
    if "gc_results" in st.session_state:
        results = st.session_state["gc_results"]
        
        # Reset button
        if st.button("Clear Results", use_container_width=True):
            del st.session_state["gc_results"]
            st.rerun()

        st.divider()
        
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.subheader("📝 Detection Assessment")
            with st.container(height=500):
                st.markdown(results['resp_detect'])

        with col_res2:
            st.subheader("📝 Risk Assessment")
            with st.container(height=500):
                st.markdown(results['resp_risk'])
        
        st.divider()
        st.subheader("💡 AI Comparison & Recommendations")
        st.markdown(results['resp_compare'])

        # Debug Expander
        with st.expander("🛠️ Debug: View Prompts"):
            st.markdown("**Detection Prompt:**")
            st.code(results.get("debug_prompt_detect", "N/A"))
            st.markdown("**Risk Prompt:**")
            st.code(results.get("debug_prompt_risk", "N/A"))
