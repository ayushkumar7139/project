import pandas as pd
import streamlit as st
from modules.storage import get_all_cases, delete_case, get_case_by_id
from modules.ui_components import status_badge_html, priority_badge_html


def render_cases_view():
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <h2 style="margin: 0; font-size: 1.4rem; font-weight: 700; color: #0F172A;">Case Register & Asset Operations</h2>
        <p style="margin: 0.2rem 0 0 0; color: #64748B; font-size: 0.9rem;">
            Central index of all AI visual inspections, incident records, assignments, and resolution states.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    cases = get_all_cases()
    if not cases:
        st.info("No cases currently recorded. Click 'New Inspection' to start.")
        return
        
    # Search and Filter Bar
    c_search, c_status, c_priority, c_cat = st.columns([4, 3, 3, 3])
    with c_search:
        search_query = st.text_input("Search Cases", placeholder="Search ID, title, location, owner...", label_visibility="collapsed")
    with c_status:
        status_filter = st.selectbox("Status", ["All Statuses", "Open", "Investigating", "Action Required", "Resolved", "Reopened"], label_visibility="collapsed")
    with c_priority:
        priority_filter = st.selectbox("Priority", ["All Priorities", "Immediate Attention", "High", "Moderate", "Low"], label_visibility="collapsed")
    with c_cat:
        cat_filter = st.selectbox("Category", ["All Categories", "Safety or access", "Building or maintenance", "Cleanliness or waste", "Road or public space", "Equipment or object", "Other"], label_visibility="collapsed")
        
    # Apply filters
    filtered = cases
    if search_query.strip():
        q = search_query.strip().lower()
        filtered = [
            c for c in filtered
            if q in c.get("id", "").lower()
            or q in c.get("title", "").lower()
            or q in c.get("location", "").lower()
            or q in c.get("owner", "").lower()
        ]
    if status_filter != "All Statuses":
        filtered = [c for c in filtered if c.get("status") == status_filter]
    if priority_filter != "All Priorities":
        filtered = [c for c in filtered if priority_filter.lower() in str(c.get("ai_findings", {}).get("suggested_priority", "")).lower()]
    if cat_filter != "All Categories":
        filtered = [c for c in filtered if c.get("category") == cat_filter]

    st.markdown(f"<div style='font-size:0.85rem; color:#64748B; margin:0.8rem 0;'>Showing <strong>{len(filtered)}</strong> of {len(cases)} cases</div>", unsafe_allow_html=True)

    if not filtered:
        st.info("No cases matched your search filter criteria.")
        return

    # Table Header
    st.markdown("""
    <div style="background:#F1F5F9; border:1px solid #E2E8F0; border-radius:8px; padding:0.6rem 1rem; font-weight:600; font-size:0.78rem; text-transform:uppercase; color:#475569; display:grid; grid-template-columns: 1.3fr 3.2fr 1.6fr 1.6fr 1.5fr 1.6fr 1.8fr; gap:0.5rem; align-items:center;">
        <div>Case ID</div>
        <div>Inspection Title & Location</div>
        <div>Category</div>
        <div>Priority</div>
        <div>Status</div>
        <div>Owner</div>
        <div>Actions</div>
    </div>
    """, unsafe_allow_html=True)

    # Render Rows
    for c in filtered:
        cid = c.get("id")
        title = c.get("title", "Untitled")
        loc = c.get("location", "Unspecified")
        cat = c.get("category", "General")
        findings = c.get("ai_findings", {})
        priority = findings.get("suggested_priority", "Moderate")
        status = c.get("status", "Open")
        owner = c.get("owner", "Unassigned")
        is_sample = c.get("is_sample", False)
        
        with st.container():
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1.3, 3.2, 1.6, 1.6, 1.5, 1.6, 1.8])
            with c1:
                st.markdown(f"**{cid}**")
                if is_sample:
                    st.caption("Sample")
            with c2:
                st.markdown(f"**{title}**")
                st.caption(f"📍 {loc}")
            with c3:
                st.markdown(f"<span style='font-size:0.85rem;'>{cat}</span>", unsafe_allow_html=True)
            with c4:
                st.markdown(priority_badge_html(priority), unsafe_allow_html=True)
            with c5:
                st.markdown(status_badge_html(status), unsafe_allow_html=True)
            with c6:
                st.markdown(f"<span style='font-size:0.85rem; color:#334155;'>{owner}</span>", unsafe_allow_html=True)
            with c7:
                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    if st.button("Lab", key=f"tbl_lab_{cid}", use_container_width=True):
                        st.session_state["selected_case_id"] = cid
                        st.session_state["nav_module"] = "Visual Evidence Lab"
                        st.rerun()
                with col_act2:
                    if st.button("Edit", key=f"tbl_edit_{cid}", use_container_width=True):
                        st.session_state["selected_case_id"] = cid
                        st.session_state["nav_module"] = "Investigation Workspace"
                        st.rerun()
            st.markdown("<hr style='margin:0.3rem 0; border:none; border-top:1px solid #F1F5F9;'>", unsafe_allow_html=True)
