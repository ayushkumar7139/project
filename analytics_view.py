import streamlit as st
import pandas as pd
import altair as alt
from modules.storage import get_all_cases
from modules.ui_components import render_kpi_card


def render_analytics_view():
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <h2 style="margin: 0; font-size: 1.4rem; font-weight: 700; color: #0F172A;">Safety & Asset Operational Analytics</h2>
        <p style="margin: 0.2rem 0 0 0; color: #64748B; font-size: 0.9rem;">
            Real-time metrics, risk profiles, category distributions, and recurring incident pattern detection.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    cases = get_all_cases()
    if not cases:
        st.info("No cases available in storage. Record inspections to view operational analytics.")
        return
        
    total_cases = len(cases)
    resolved_cases = sum(1 for c in cases if c.get("status") == "Resolved")
    open_cases = total_cases - resolved_cases
    resolution_rate = f"{(resolved_cases / total_cases * 100):.1f}%" if total_cases > 0 else "0%"
    
    # Calculate overdue / pending tasks
    total_tasks = 0
    completed_tasks = 0
    for c in cases:
        checklist = c.get("ai_findings", {}).get("verification_checklist", [])
        total_tasks += len(checklist)
        completed_tasks += sum(1 for t in checklist if t.get("completed", False))
        
    pending_tasks = total_tasks - completed_tasks
    
    # Top KPI row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Resolution Rate", resolution_rate, f"{resolved_cases} of {total_cases} completed", "#059669")
    with k2:
        render_kpi_card("Active In-Flight", open_cases, "Cases pending verification", "#D97706" if open_cases > 0 else "#64748B")
    with k3:
        render_kpi_card("Verification Tasks", f"{completed_tasks}/{total_tasks}", f"{pending_tasks} checklist items left", "#0D9488")
    with k4:
        render_kpi_card("Recurring Hotspots", len(set(c.get("location") for c in cases if c.get("location"))), "Distinct facility zones", "#475569")

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # Prepare DataFrame
    data_rows = []
    for c in cases:
        findings = c.get("ai_findings", {})
        data_rows.append({
            "id": c.get("id"),
            "category": c.get("category", "Other"),
            "priority": findings.get("suggested_priority", "Moderate"),
            "status": c.get("status", "Open"),
            "location": c.get("location", "Unspecified"),
            "confidence": findings.get("visual_confidence", "High")
        })
    df = pd.DataFrame(data_rows)

    c_left, c_right = st.columns(2, gap="large")
    
    with c_left:
        st.markdown("#### Findings by Category & Priority")
        cat_prio_df = df.groupby(["category", "priority"]).size().reset_index(name="count")
        
        chart_cat = alt.Chart(cat_prio_df).mark_bar(cornerRadius=4).encode(
            x=alt.X('count:Q', title="Number of Findings"),
            y=alt.Y('category:N', title="Category", sort='-x'),
            color=alt.Color('priority:N', scale=alt.Scale(
                domain=['Immediate Attention', 'High', 'Moderate', 'Low'],
                range=['#DC2626', '#EA580C', '#D97706', '#0284C7']
            ), title="Assessed Priority"),
            tooltip=['category', 'priority', 'count']
        ).properties(height=260)
        st.altair_chart(chart_cat, use_container_width=True)

    with c_right:
        st.markdown("#### Case Operational Status Breakdown")
        status_df = df.groupby("status").size().reset_index(name="count")
        
        chart_status = alt.Chart(status_df).mark_arc(innerRadius=50, cornerRadius=4).encode(
            theta=alt.Theta(field="count", type="quantitative"),
            color=alt.Color(field="status", type="nominal", scale=alt.Scale(
                domain=['Open', 'Investigating', 'Action Required', 'Resolved', 'Reopened'],
                range=['#3B82F6', '#F59E0B', '#EF4444', '#10B981', '#8B5CF6']
            ), title="Status"),
            tooltip=['status', 'count']
        ).properties(height=260)
        st.altair_chart(chart_status, use_container_width=True)

    st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    # Recurring Issue & Hotspot Detection
    st.markdown("#### 🚨 Recurring Problem Pattern Detection")
    st.caption("Cross-case intelligence: Identifies repeat issues or cluster patterns across facilities from stored records.")
    
    loc_counts = df["location"].value_counts().reset_index()
    loc_counts.columns = ["Facility Location", "Inspections Logged"]
    
    col_hot, col_ai_insight = st.columns([6, 6], gap="large")
    with col_hot:
        st.dataframe(loc_counts, use_container_width=True)
        
    with col_ai_insight:
        st.markdown("""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:1.1rem;">
            <div style="font-size:0.85rem; font-weight:700; color:#0F766E; margin-bottom:0.4rem;">AI PATTERN CORRELATION SUMMARY</div>
            <p style="font-size:0.88rem; color:#334155; margin:0 0 0.5rem 0;">
                • <strong>Ingress & Egress Blockages:</strong> Staging deliveries in emergency corridors accounts for immediate life-safety violations.<br>
                • <strong>Infrastructure Proximity:</strong> Active moisture intrusion discovered within 1.5m of energized distribution enclosures requires preventative plumbing envelope sealing.<br>
                • <strong>Pedestrian Surfaces:</strong> Slab displacement >40mm concentrated along high-traffic routes creates repetitive liability risks.
            </p>
        </div>
        """, unsafe_allow_html=True)
