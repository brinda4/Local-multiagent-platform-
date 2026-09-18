"""Translational Genomics and Anatomical Intelligence Platform.
Emerald and Slate Theme Streamlit Web Portal.
Zero emoji characters across all UI elements and text.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.tools.db_tool import ReadOnlyDatabaseTool
from src.agents.supervisor_orchestrator import SupervisorOrchestrator

st.set_page_config(
    page_title="Translational Genomics & Anatomical Intelligence Platform",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom High-Contrast Emerald and Slate CSS Theme
CUSTOM_CSS = """
<style>
    /* Dark Slate Backgrounds */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    header, .stHeader {
        background-color: #0b0f19 !important;
    }
    
    /* Top Header Styling */
    .portal-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
    }
    .portal-title {
        color: #ffffff;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 6px;
    }
    .portal-subtitle {
        color: #10b981;
        font-size: 15px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .portal-desc {
        color: #94a3b8;
        font-size: 14px;
        margin-top: 8px;
    }
    
    /* KPI Card Container */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 28px;
    }
    .kpi-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-top: 3px solid #10b981;
        border-radius: 8px;
        padding: 16px 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        border-color: #059669;
        transform: translateY(-2px);
    }
    .kpi-title {
        color: #94a3b8;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        color: #ffffff;
        font-size: 26px;
        font-weight: 700;
        margin-top: 4px;
        letter-spacing: -0.5px;
    }
    .kpi-source {
        color: #10b981;
        font-size: 11px;
        margin-top: 4px;
        font-weight: 500;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0f172a;
        padding: 8px;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 14px;
        padding: 10px 20px;
        background-color: transparent;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #059669 !important;
        color: #ffffff !important;
        box-shadow: 0 2px 8px rgba(5, 150, 105, 0.4);
    }
    
    /* Button Styling */
    .stButton > button {
        background-color: #059669;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 8px 20px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #10b981;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    /* Inputs */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
    }
    
    /* Dataframes */
    .stDataFrame {
        border: 1px solid #334155;
        border-radius: 8px;
        overflow: hidden;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

@st.cache_resource
def get_db_tool():
    return ReadOnlyDatabaseTool()

@st.cache_resource
def get_orchestrator():
    return SupervisorOrchestrator()

db_tool = get_db_tool()
orchestrator = get_orchestrator()

# Header
st.markdown("""
<div class="portal-header">
    <div class="portal-title">Translational Genomics & Anatomical Intelligence Platform</div>
    <div class="portal-subtitle">PrimeKG Data Integration | Bgee & DisGeNET Focus</div>
    <div class="portal-desc">
        High-throughput local biomedical intelligence system connecting anatomical tissue gene expression,
        expert-curated disease variant scoring, drug target mechanisms, and unified disease ontologies.
        Strictly local, offline-capable execution.
    </div>
</div>
""", unsafe_allow_html=True)

# Live Database KPI Metrics
metrics = db_tool.get_kpi_metrics()
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-title">Anatomical Tissues</div>
        <div class="kpi-value">{metrics['anatomical_tissues']:,}</div>
        <div class="kpi-source">Bgee Expression DB</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Gene-Disease Variants</div>
        <div class="kpi-value">{metrics['gene_disease_variants']:,}</div>
        <div class="kpi-source">DisGeNET Curated</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Drug Targets</div>
        <div class="kpi-value">{metrics['drug_targets']:,}</div>
        <div class="kpi-source">DrugCentral Interactions</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Approved Molecules</div>
        <div class="kpi-value">{metrics['approved_drugs']:,}</div>
        <div class="kpi-source">DrugCentral Structures</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Disease Concepts</div>
        <div class="kpi-value">{metrics['disease_ontology_terms']:,}</div>
        <div class="kpi-source">MONDO Ontology</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Horizontal Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Anatomical Expression Explorer",
    "Gene-Disease DisGeNET Intelligence",
    "Pharmacology & Drug Mechanism Portal",
    "Multi-Agent Query Suite"
])

# =============================================================================
# TAB 1: Anatomical Expression Explorer (Bgee Tissue Data)
# =============================================================================
with tab1:
    st.markdown("### Anatomical Expression Explorer")
    st.caption("Investigate gene expression intensity, gold quality ranks, and anatomical distribution across human organs and tissues.")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        gene_input = st.text_input("Filter by Gene Symbol", value="EGFR", key="bgee_gene_input").strip().upper()
    with col2:
        tissue_input = st.text_input("Filter by Anatomical Structure", value="", placeholder="e.g. lung, brain, liver", key="bgee_tissue_input").strip()
    with col3:
        bgee_limit = st.slider("Result Limit", min_value=10, max_value=100, value=25, key="bgee_limit")
        
    query_conditions = ["expression_call = 'present'"]
    params = []
    
    if gene_input:
        query_conditions.append("gene_name = ?")
        params.append(gene_input)
    if tissue_input:
        query_conditions.append("anatomy_name LIKE ?")
        params.append(f"%{tissue_input}%")
        
    where_clause = " AND ".join(query_conditions)
    sql_bgee = f"""
    SELECT gene_name, anatomy_name, anatomy_id, expression_score, expression_rank, call_quality
    FROM bgee_expression
    WHERE {where_clause}
    ORDER BY expression_score DESC, expression_rank ASC
    LIMIT ?;
    """
    params.append(bgee_limit)
    
    bgee_res = db_tool.execute_query(sql_bgee, tuple(params))
    
    if bgee_res["success"] and not bgee_res["data"].empty:
        df_bgee = bgee_res["data"]
        
        # Interactive Plotly Chart
        chart_df = df_bgee.head(15)
        fig_bgee = px.bar(
            chart_df,
            x="expression_score",
            y="anatomy_name",
            orientation="h",
            title=f"Expression Intensity for {gene_input if gene_input else 'Queried Entities'}",
            labels={"expression_score": "Expression Score (0-100)", "anatomy_name": "Anatomical Tissue"},
            color="expression_score",
            color_continuous_scale=["#064e3b", "#059669", "#10b981", "#34d399"]
        )
        fig_bgee.update_layout(
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            font_color="#f8fafc",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig_bgee, use_container_width=True)
        
        # Table and Download
        st.dataframe(df_bgee, use_container_width=True)
        csv_data = df_bgee.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Export Results to CSV",
            data=csv_data,
            file_name=f"bgee_expression_{gene_input}_{time.strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_bgee_csv"
        )
    else:
        st.info("No expression records matching the specified criteria were located.")

# =============================================================================
# TAB 2: Gene-Disease DisGeNET Intelligence
# =============================================================================
with tab2:
    st.markdown("### Gene-Disease DisGeNET Intelligence")
    st.caption("Expert-curated disease genomics, variant confidence scores, and MONDO unified ontology alignments.")
    
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        dis_input = st.text_input("Search Disease Phenotype", value="glioblastoma", key="disgenet_dis_input").strip()
    with c2:
        g_input = st.text_input("Filter by Gene Symbol", value="", placeholder="e.g. TP53, PTEN", key="disgenet_gene_input").strip().upper()
    with c3:
        min_score = st.slider("Min GDA Score", min_value=0.1, max_value=0.9, value=0.3, step=0.05, key="disgenet_min_score")
        
    dis_conditions = ["association_score >= ?"]
    dis_params = [min_score]
    
    if dis_input:
        dis_conditions.append("disease_name LIKE ?")
        dis_params.append(f"%{dis_input}%")
    if g_input:
        dis_conditions.append("gene_symbol = ?")
        dis_params.append(g_input)
        
    dis_where = " AND ".join(dis_conditions)
    sql_dis = f"""
    SELECT gene_symbol, disease_name, association_score, variant_score,
           evidence_count, evidence_level, disease_category, disease_id
    FROM disgenet_associations
    WHERE {dis_where}
    ORDER BY association_score DESC, variant_score DESC
    LIMIT 50;
    """
    dis_res = db_tool.execute_query(sql_dis, tuple(dis_params))
    
    if dis_res["success"] and not dis_res["data"].empty:
        df_dis = dis_res["data"]
        
        # Interactive Scatter / Bar Plot
        fig_dis = px.scatter(
            df_dis.head(30),
            x="association_score",
            y="variant_score",
            size="evidence_count",
            color="evidence_level",
            hover_data=["gene_symbol", "disease_name"],
            title=f"DisGeNET Evidence Landscape: {dis_input if dis_input else 'Candidate Diseases'}",
            labels={"association_score": "Gene-Disease Association Score", "variant_score": "Variant Impact Score"},
            color_discrete_map={
                "Definitive": "#10b981",
                "Strong": "#059669",
                "Moderate": "#0284c7",
                "Limited": "#94a3b8"
            }
        )
        fig_dis.update_layout(
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            font_color="#f8fafc",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_dis, use_container_width=True)
        
        st.dataframe(df_dis, use_container_width=True)
        csv_dis = df_dis.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Export Results to CSV",
            data=csv_dis,
            file_name=f"disgenet_associations_{time.strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_disgenet_csv"
        )
    else:
        st.info("No gene-disease associations matching the query criteria were identified.")
# =============================================================================
# TAB 3: Pharmacology & Drug Mechanism Portal (DrugCentral)
# =============================================================================
with tab3:
    st.markdown("### Pharmacology & Drug Mechanism Portal")
    st.caption("Investigate pharmaceutical active ingredients, biological target mechanisms, action types, and chemical representations.")
    
    p1, p2, p3 = st.columns([2, 2, 1])
    with p1:
        drug_query = st.text_input("Search Active Ingredient / Drug", value="", placeholder="e.g. osimertinib, erlotinib", key="drug_input").strip().lower()
    with p2:
        target_gene_query = st.text_input("Search by Target Gene Symbol", value="EGFR", key="target_gene_input").strip().upper()
    with p3:
        moa_only = st.checkbox("Confirmed MoA Only", value=True, key="moa_only_check")
        
    ph_conds = []
    ph_params = []
    
    if drug_query:
        ph_conds.append("t.drug_name LIKE ?")
        ph_params.append(f"%{drug_query}%")
    if target_gene_query:
        ph_conds.append("t.gene_symbol = ?")
        ph_params.append(target_gene_query)
    if moa_only:
        ph_conds.append("t.moa = 1")
        
    ph_where = " AND ".join(ph_conds) if ph_conds else "1=1"
    sql_ph = f"""
    SELECT t.drug_name, t.gene_symbol, t.target_name, t.target_class,
           t.action_type, t.moa, t.act_type, t.act_value, t.act_unit,
           s.smiles, s.inchikey
    FROM drugcentral_targets t
    LEFT JOIN drugcentral_structures s ON t.struct_id = s.struct_id
    WHERE {ph_where}
    ORDER BY t.moa DESC, t.drug_name ASC
    LIMIT 50;
    """
    ph_res = db_tool.execute_query(sql_ph, tuple(ph_params))
    
    if ph_res["success"] and not ph_res["data"].empty:
        df_ph = ph_res["data"]
        
        # Donut Chart for Action Types
        if "action_type" in df_ph.columns and not df_ph["action_type"].dropna().empty:
            act_counts = df_ph["action_type"].replace("", "UNSPECIFIED").value_counts().reset_index()
            act_counts.columns = ["action_type", "count"]
            
            fig_ph = px.pie(
                act_counts,
                names="action_type",
                values="count",
                hole=0.45,
                title="Pharmacological Action Type Modalities",
                color_discrete_sequence=["#10b981", "#059669", "#047857", "#0284c7", "#64748b"]
            )
            fig_ph.update_layout(
                paper_bgcolor="#0f172a",
                plot_bgcolor="#0f172a",
                font_color="#f8fafc",
                height=350,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_ph, use_container_width=True)
            
        st.dataframe(df_ph, use_container_width=True)
        csv_ph = df_ph.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Export Results to CSV",
            data=csv_ph,
            file_name=f"drugcentral_targets_{time.strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_drug_csv"
        )
    else:
        st.info("No pharmacological targets matching the specified criteria were identified.")

# =============================================================================
# TAB 4: Multi-Agent Query Suite
# =============================================================================
with tab4:
    st.markdown("### Multi-Agent Query Suite")
    st.caption("Execute collaborative multi-agent cross-domain queries linking DisGeNET genomics, Bgee tissue expression, and DrugCentral mechanisms.")
    
    # Preset Prompts
    st.markdown("**Sample Translational Research Queries:**")
    sq_col1, sq_col2, sq_col3 = st.columns(3)
    sample_to_inject = None
    with sq_col1:
        if st.button("Glioblastoma Multi-Agent Discovery"):
            sample_to_inject = "Find drugs targeting genes associated with glioblastoma and check their tissue expression in the brain"
    with sq_col2:
        if st.button("EGFR Epithelial & Lung Profiling"):
            sample_to_inject = "Investigate EGFR targeted therapies and evaluate expression in lung and epithelial tissues"
    with sq_col3:
        if st.button("Alzheimer Target & Drug Exploration"):
            sample_to_inject = "Identify DisGeNET biomarkers for Alzheimer disease and query cholinesterase inhibitors"
            
    default_q = sample_to_inject or "Find drugs targeting genes associated with glioblastoma and check their tissue expression in the brain"
    user_query = st.text_area("Biomedical Research Query", value=default_q, height=90, key="agent_query_box")
    
    if st.button("Execute Multi-Agent Query", type="primary"):
        with st.spinner("Executing multi-agent routing, querying local relational database, and synthesizing evidence..."):
            result = orchestrator.route_and_execute(user_query)
            
        st.success(f"Multi-Agent Execution Completed in {result['elapsed_ms']} ms | Intent: {result['intent']}")
        
        # Display Final Synthesized Report
        st.markdown("#### Synthesized Translational Discovery Report")
        st.markdown(result["final_report"])
        
        # Display Intermediate Agent Evidence Traces
        st.markdown("---")
        st.markdown("#### Specialized Agent Evidence Tables")
        
        for table_key, df_table in result["data_tables"].items():
            if not df_table.empty:
                st.markdown(f"**Dataset Table: `{table_key}` ({len(df_table)} records)**")
                st.dataframe(df_table, use_container_width=True)
                csv_tbl = df_table.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=f"Export {table_key} to CSV",
                    data=csv_tbl,
                    file_name=f"{table_key}_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key=f"dl_{table_key}"
                )
                
        # Session History
        history = orchestrator.get_history()
        if len(history) > 1:
            st.markdown("---")
            st.markdown("#### Conversational Session History")
            for idx, h in enumerate(reversed(history[:-1])):
                with st.expander(f"Prior Query {len(history) - idx - 1}: {h['query']}"):
                    st.write(f"**Intent**: {h['intent']} | **Duration**: {h['elapsed_ms']} ms")
                    st.markdown(h["final_report"])
