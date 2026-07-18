import os
import sys

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from theme import COLORS, RISK_COLOR_MAP, hero, inject_global_css, rail_start, rail_end, style_fig
from utils import get_scored_employees, get_trained_models

st.set_page_config(page_title="Attrition Risk Dashboard", page_icon="\U0001F4CA", layout="wide")
inject_global_css()
hero("Attrition Risk Dashboard", "Overall risk distribution and model performance across the current workforce.")

scored = get_scored_employees()
train_out = get_trained_models()
best_name = train_out["best_model_name"]
metrics = train_out["results"][best_name]["test_metrics"]
cv = train_out["results"][best_name]["cv_roc_auc"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Employees", f"{len(scored):,}")
c2.metric("High Risk", int((scored["RiskCategory"] == "High Risk").sum()))
c3.metric("Medium Risk", int((scored["RiskCategory"] == "Medium Risk").sum()))
c4.metric("Low Risk", int((scored["RiskCategory"] == "Low Risk").sum()))

st.divider()

col_main, col_rail = st.columns([3, 1])

with col_rail:
    rail_start("Chart Controls")
    dist_chart_type = st.radio("Risk distribution", ["Bar", "Donut"], key="risk_dist_type")
    proba_chart_type = st.radio("Probability distribution", ["Histogram", "Box"], key="proba_dist_type")
    top_n = st.slider("High-risk table rows", 5, 30, 15, key="top_n_rows")
    rail_end()

with col_main:
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown("#### Risk Category Distribution")
        counts = scored["RiskCategory"].value_counts().reindex(["Low Risk", "Medium Risk", "High Risk"]).fillna(0)
        if dist_chart_type == "Bar":
            fig = go.Figure(go.Bar(
                x=counts.index, y=counts.values,
                marker_color=[RISK_COLOR_MAP[c] for c in counts.index],
                text=counts.values, textposition="outside",
            ))
        else:
            fig = go.Figure(go.Pie(
                labels=counts.index, values=counts.values,
                marker=dict(colors=[RISK_COLOR_MAP[c] for c in counts.index]),
                hole=0.5, textinfo="label+percent",
            ))
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Employees" if dist_chart_type == "Bar" else None)
        st.plotly_chart(style_fig(fig), width="stretch")

    with ch2:
        st.markdown("#### Attrition Probability Distribution")
        if proba_chart_type == "Histogram":
            fig2 = go.Figure(go.Histogram(x=scored["AttritionProbability"], nbinsx=30, marker_color=COLORS["blue_accent"]))
            fig2.add_vline(x=0.30, line_dash="dash", line_color=COLORS["medium_risk"])
            fig2.add_vline(x=0.60, line_dash="dash", line_color=COLORS["high_risk"])
            fig2.update_layout(xaxis_title="Predicted Attrition Probability", yaxis_title="Employees")
        else:
            fig2 = go.Figure(go.Box(
                y=scored["AttritionProbability"], boxpoints="outliers",
                marker_color=COLORS["blue_accent"], name="Attrition Probability",
            ))
            fig2.update_layout(yaxis_title="Predicted Attrition Probability")
        fig2.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(style_fig(fig2), width="stretch")

st.divider()
st.markdown("#### Model Performance Comparison")
comp_rows = []
for name, r in train_out["results"].items():
    row = {"Model": name, **r["test_metrics"], "CV ROC-AUC (mean)": r["cv_roc_auc"]["mean"]}
    comp_rows.append(row)
comp_df = pd.DataFrame(comp_rows).sort_values("roc_auc", ascending=False)
st.dataframe(comp_df, width="stretch", hide_index=True)
st.caption(
    f"**{best_name}** was selected as the production model (highest test ROC-AUC = {metrics['roc_auc']}, "
    f"5-fold cross-validated ROC-AUC = {cv['mean']} ± {cv['std']})."
)

st.divider()
st.markdown(f"#### High-Risk Employees (Top {top_n} by probability)")
topN = scored.sort_values("AttritionProbability", ascending=False).head(top_n)[
    ["EmployeeID", "Department", "JobRole", "AttritionProbability", "RiskCategory", "OverTime", "MonthlyIncome"]
]
st.dataframe(topN, width="stretch", hide_index=True)
