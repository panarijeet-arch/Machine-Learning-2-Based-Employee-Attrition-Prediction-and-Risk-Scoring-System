import os
import sys

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import plotly.graph_objects as go
import streamlit as st

from explainability import reason_codes
from theme import COLORS, hero, inject_global_css, rail_start, rail_end, risk_badge_html, style_fig
from utils import get_scored_employees, get_trained_models

st.set_page_config(page_title="Employee Risk Profile", page_icon="\U0001F464", layout="wide")
inject_global_css()
hero("Employee Risk Profile", "Look up any individual employee's attrition risk and the factors driving it.")

scored = get_scored_employees()
train_out = get_trained_models()
pipeline = train_out["best_pipeline"]

col_main, col_rail = st.columns([3, 1])

with col_rail:
    rail_start("Employee Selector")
    dept_filter = st.selectbox("Filter by department", ["All"] + sorted(scored["Department"].unique().tolist()), key="profile_dept_filter")
    pool = scored if dept_filter == "All" else scored[scored["Department"] == dept_filter]
    employee_id = st.selectbox("Employee ID", pool["EmployeeID"].tolist(), key="profile_employee_id")
    factors_chart_type = st.radio("Factors chart", ["Bar", "Lollipop"], key="profile_factors_chart")
    rail_end()

emp_row = scored[scored["EmployeeID"] == employee_id].iloc[0]

with col_main:
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        st.metric("Attrition Probability", f"{emp_row['AttritionProbability']*100:.1f}%")
    with c2:
        st.markdown("**Risk Category**")
        st.markdown(risk_badge_html(emp_row["RiskCategory"]), unsafe_allow_html=True)
    with c3:
        st.markdown("**Role**")
        st.write(f"{emp_row['JobRole']} — {emp_row['Department']}")

    st.divider()

    detail_col, factor_col = st.columns([1, 1])
    with detail_col:
        st.markdown("#### Employee Details")
        detail_fields = [
            "Age", "Gender", "MaritalStatus", "MonthlyIncome", "JobLevel",
            "YearsAtCompany", "YearsInCurrentRole", "YearsSinceLastPromotion",
            "OverTime", "BusinessTravel", "WorkLifeBalance", "JobSatisfaction",
            "EnvironmentSatisfaction", "NumCompaniesWorked",
        ]
        for f in detail_fields:
            st.write(f"**{f}:** {emp_row[f]}")

    with factor_col:
        st.markdown("#### Top Contributing Factors")
        from feature_engineering import FEATURE_COLUMNS
        emp_X = scored[scored["EmployeeID"] == employee_id][FEATURE_COLUMNS]
        ref_X = train_out["X_train"]
        rc = reason_codes(pipeline, emp_X, ref_X, top_n=6)

        colors = [COLORS["high_risk"] if v > 0 else COLORS["low_risk"] for v in rc["contribution_score"]]
        if factors_chart_type == "Bar":
            fig = go.Figure(go.Bar(
                x=rc["contribution_score"], y=rc["feature"], orientation="h", marker_color=colors,
            ))
        else:
            fig = go.Figure()
            for i, row in rc.iterrows():
                fig.add_trace(go.Scatter(
                    x=[0, row["contribution_score"]], y=[row["feature"], row["feature"]],
                    mode="lines", line=dict(color=colors[i], width=2), showlegend=False,
                ))
            fig.add_trace(go.Scatter(
                x=rc["contribution_score"], y=rc["feature"], mode="markers",
                marker=dict(color=colors, size=12), showlegend=False,
            ))
        fig.update_layout(
            height=320, margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Contribution to risk (relative)", yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(style_fig(fig), width="stretch")
        st.caption(
            "Positive bars push this employee's risk above the average employee; negative bars pull it "
            "below average. This is a transparent, rule-based explanation (deviation from the training "
            "population mean, weighted by global feature importance) — not a SHAP value, though it serves "
            "the same purpose of surfacing individual reason codes for HR review."
        )
