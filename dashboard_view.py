import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from modules.storage import get_all_cases
from modules.ui_components import render_kpi_card, status_badge_html, priority_badge_html


def render_dashboard_view():
    cases = get_all_cases()
    
    # Calculate real metrics
    total_cases = len(cases)
    open_cases = sum(1 for c in cases if c.get("status") in ["Open", "Investigating", "Action Required"])
    urgent_cases = sum(1 for c in cases if "immediate" in str(c.get("ai_findings", {}).get("suggested_priority", "")).lower() or "high" in str(c.get("ai_findings", {}).get("suggested_priority", "")).lower())
    resolved_cases = sum(1 for c in cases if c.get("status") == "Resolved")
    
    # 4 KPI cards row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Total Inspections", total_cases, "All recorded site scans", "#0D9488")
    with c2:
        render_kpi_card("Active Open Cases", open_cases, "In progress or awaiting action", "#D97706" if open_cases > 0 else "#64748B")
    with c3:
        render_kpi_card("Urgent Findings", urgent_cases, "High or Immediate priority", "#DC2626" if urgent_cases > 0 else "#10B981")
    with c4:
        render_kpi_card("Resolved & Verified", resolved_cases, "Human-verified resolutions", "#059669")
        
    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
    
    # Quick action banner
    col_act1, col_act2, col_act3 = st.columns([2, 1, 1])
    with col_act1:
        st.markdown("""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:0.85rem 1.2rem; display:flex; align-items:center; justify-content:space-between;">
            <div>
                <strong style="color:#0F172A; font-size:0.95rem;">Operational Principle:</strong>
                <span style="color:#475569; font-size:0.88rem; margin-left:0.4rem;">See the evidence · Understand the uncertainty · Take the next step · Verify the result.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_act2:
        if st.button("➕ Start New Inspection", type="primary", use_container_width=True):
            st.session_state["nav_module"] = "New Inspection"
            st.rerun()
    with col_act3:
        if st.button("📂 Open Case Register", use_container_width=True):
            st.session_state["nav_module"] = "Case Management"
            st.rerun()

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
    
    if not cases:
        st.info("No inspection records found in storage. Click 'Start New Inspection' or go to Settings to seed sample cases.")
        return

    # Two-column layout: Recent Activity Table & Risk Distribution
    col_main, col_side = st.columns([7, 5], gap="large")
    
    with col_main:
        st.markdown("""
        <div class="panel-card">
            <div class="panel-header">
                <div>
                    <h3 class="panel-title">Recent Inspection Cases</h3>
                    <div class="panel-subtitle">Latest computer vision findings logged across facilities</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Build clean custom table
        for case in cases[:5]:
            cid = case.get("id")
            title = case.get("title", "Untitled Inspection")
            loc = case.get("location", "Unspecified Location")
            status = case.get("status", "Open")
            findings = case.get("ai_findings", {})
            priority = findings.get("suggested_priority", "Moderate")
            created = case.get("created_at", "")[:10]
            
            with st.container():
                rc1, rc2, rc3, rc4 = st.columns([4, 2, 2, 2])
                with rc1:
                    st.markdown(f"**{cid}**: {title}")
                    st.caption(f"📍 {loc} · 📅 {created}")
                with rc2:
                    st.markdown(priority_badge_html(priority), unsafe_allow_html=True)
                with rc3:
                    st.markdown(status_badge_html(status), unsafe_allow_html=True)
                with rc4:
                    if st.button("Inspect ➔", key=f"btn_open_{cid}", use_container_width=True):
                        st.session_state["selected_case_id"] = cid
                        st.session_state["nav_module"] = "Visual Evidence Lab"
                        st.rerun()
                st.markdown("<hr style='margin:0.5rem 0 0.8rem 0; border:none; border-top:1px solid #F1F5F9;'>", unsafe_allow_html=True)
                
    with col_side:
        # Risk Distribution Chart
        st.markdown("""
        <div class="panel-card">
            <div class="panel-header">
                <div>
                    <h3 class="panel-title">Risk Priority Profile</h3>
                    <div class="panel-subtitle">Assessed urgency distribution</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        priorities = [c.get("ai_findings", {}).get("suggested_priority", "Moderate") for c in cases]
        p_counts = {}
        for p in priorities:
            p_counts[p] = p_counts.get(p, 0) + 1
            
        p_df = pd.DataFrame([{"Priority": k, "Cases": v} for k, v in p_counts.items()])
        
        if not p_df.empty:
            chart = alt.Chart(p_df).mark_bar(cornerRadius=6, size=24).encode(
                x=alt.X('Cases:Q', axis=alt.Axis(tickMinStep=1)),
                y=alt.Y('Priority:N', sort=['Immediate Attention', 'High', 'Moderate', 'Low']),
                color=alt.Color('Priority:N', scale=alt.Scale(
                    domain=['Immediate Attention', 'High', 'Moderate', 'Low'],
                    range=['#DC2626', '#EA580C', '#D97706', '#0284C7']
                ), legend=None),
                tooltip=['Priority', 'Cases']
            ).properties(height=180)
            st.altair_chart(chart, use_container_width=True)
            
        # Outstanding Verification Tasks across open cases
        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
        st.markdown("**Outstanding Verification Checks**")
        all_tasks = []
        for c in cases:
            if c.get("status") != "Resolved":
                checklist = c.get("ai_findings", {}).get("verification_checklist", [])
                for t in checklist:
                    if not t.get("completed", False):
                        all_tasks.append((c.get("id"), t.get("task", "")))
                        
        if all_tasks:
            for cid, task_text in all_tasks[:4]:
                st.markdown(f"• **[{cid}]** {task_text}")
            if len(all_tasks) > 4:
                st.caption(f"+ {len(all_tasks) - 4} more tasks pending in Workspace")
        else:
            st.success("All inspection verification checklists are complete!")
