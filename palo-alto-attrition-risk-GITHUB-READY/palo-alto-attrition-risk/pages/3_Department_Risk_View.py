import os
import sys

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import plotly.graph_objects as go
import streamlit as st

from theme import COLORS, hero, inject_global_css, rail_start, rail_end, style_fig
from utils import department_role_summary, get_scored_employees

st.set_page_config(page_title="Department Risk View", page_icon="\U0001F3E2", layout="wide")
inject_global_css()
hero("Department-Level Risk View", "Aggregated attrition risk by department and job role.")

scored = get_scored_employees()
departments = sorted(scored["Department"].unique())

col_main, col_rail = st.columns([3, 1])

with col_rail:
    rail_start("Filters & Chart")
    selected_depts = st.multiselect("Department", departments, default=departments, key="dept_filter")
    dept_chart_type = st.radio("Department chart", ["Bar", "Line"], key="dept_chart_type")
    bubble_metric = st.radio("Bubble size = ", ["Headcount", "High-Risk Count"], key="bubble_metric")
    rail_end()

filtered = scored[scored["Department"].isin(selected_depts)]
summary = department_role_summary(filtered)

with col_main:
    st.markdown("#### Average Predicted Risk by Department")
    dept_avg = filtered.groupby("Department")["AttritionProbability"].mean().sort_values(ascending=False) * 100
    if dept_chart_type == "Bar":
        fig = go.Figure(go.Bar(
            x=dept_avg.index, y=dept_avg.values, marker_color=COLORS["orange"],
            text=[f"{v:.1f}%" for v in dept_avg.values], textposition="outside",
        ))
    else:
        fig = go.Figure(go.Scatter(
            x=dept_avg.index, y=dept_avg.values, mode="lines+markers",
            line=dict(color=COLORS["orange"], width=3), marker=dict(size=9),
        ))
    fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Avg. Predicted Attrition Risk (%)")
    st.plotly_chart(style_fig(fig), width="stretch")

st.divider()
st.markdown("#### Department × Job Role Breakdown")
st.dataframe(
    summary.rename(columns={
        "AvgRiskProbability": "Avg Risk %",
        "HighRiskCount": "High-Risk Count",
        "ActualAttritionRate": "Historical Attrition %",
    }),
    width="stretch", hide_index=True,
)

st.divider()
st.markdown("#### High-Risk Concentration")
size_col = "Headcount" if bubble_metric == "Headcount" else "HighRiskCount"
fig2 = go.Figure(go.Scatter(
    x=summary["JobRole"], y=summary["AvgRiskProbability"],
    mode="markers",
    marker=dict(
        size=summary[size_col] * (3 if size_col == "Headcount" else 8), sizemode="area",
        color=summary["AvgRiskProbability"],
        colorscale=[[0, COLORS["low_risk"]], [0.5, COLORS["medium_risk"]], [1, COLORS["high_risk"]]],
        showscale=True,
    ),
    text=summary["Department"],
))
fig2.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Avg Risk %", xaxis_tickangle=-30)
st.plotly_chart(style_fig(fig2), width="stretch")
st.caption(f"Bubble size represents {bubble_metric.lower()} per department/role combination.")
