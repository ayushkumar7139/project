import streamlit as st
from modules.storage import seed_sample_cases_if_needed, get_all_cases, get_case_by_id
from modules.ui_components import inject_custom_css, render_brand_header, status_badge_html
from modules.dashboard_view import render_dashboard_view
from modules.inspection_view import render_inspection_view
from modules.evidence_lab_view import render_evidence_lab_view
from modules.findings_view import render_findings_view
from modules.workspace_view import render_workspace_view
from modules.cases_view import render_cases_view
from modules.reports_view import render_reports_view
from modules.analytics_view import render_analytics_view
from modules.settings_view import render_settings_view

# Page configuration
st.set_page_config(
    page_title="REALITY CHECK AI — Detect What People Miss",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom design CSS
inject_custom_css()

# Seed sample data on first launch so the dashboard is immediately functional
seed_sample_cases_if_needed()

# Session state initialization
if "nav_module" not in st.session_state:
    st.session_state["nav_module"] = "Overview Dashboard"

cases = get_all_cases()
if "selected_case_id" not in st.session_state and cases:
    st.session_state["selected_case_id"] = cases[0]["id"]

# Persistent Sidebar Navigation
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 1.2rem 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 1.2rem;">
        <div style="display: flex; align-items: center; gap: 0.65rem;">
            <div style="width: 32px; height: 32px; background: #0F766E; color: white; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.95rem;">RC</div>
            <div>
                <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A; line-height: 1.2;">REALITY CHECK AI</div>
                <div style="font-size: 0.72rem; color: #64748B; font-weight: 500;">Detect What People Miss</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#94A3B8; letter-spacing:0.05em; margin-bottom:0.5rem;'>Operational Modules</div>", unsafe_allow_html=True)
    
    nav_items = [
        "Overview Dashboard",
        "New Inspection",
        "Visual Evidence Lab",
        "AI Findings",
        "Investigation Workspace",
        "Case Management",
        "Reports & Export",
        "Analytics & Trends",
        "Settings & Model"
    ]
    
    current_nav = st.session_state.get("nav_module", "Overview Dashboard")
    chosen_module = st.radio(
        "Navigation",
        nav_items,
        index=nav_items.index(current_nav) if current_nav in nav_items else 0,
        label_visibility="collapsed"
    )
    if chosen_module != current_nav:
        st.session_state["nav_module"] = chosen_module
        st.rerun()

    st.markdown("<hr style='margin: 1.2rem 0;'>", unsafe_allow_html=True)
    
    # Active Case Quick Switcher in Sidebar
    if cases:
        st.markdown("<div style='font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#94A3B8; letter-spacing:0.05em; margin-bottom:0.35rem;'>Active Inspection Case</div>", unsafe_allow_html=True)
        active_id = st.session_state.get("selected_case_id", cases[0]["id"])
        case_options = [c["id"] for c in cases]
        if active_id not in case_options:
            active_id = case_options[0]
            st.session_state["selected_case_id"] = active_id
            
        selected_cid = st.selectbox(
            "Select Case",
            case_options,
            index=case_options.index(active_id),
            label_visibility="collapsed"
        )
        if selected_cid != active_id:
            st.session_state["selected_case_id"] = selected_cid
            st.rerun()
            
        active_case = get_case_by_id(selected_cid)
        if active_case:
            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:0.6rem 0.75rem; margin-top:0.4rem; font-size:0.8rem;">
                <div style="font-weight:600; color:#0F172A; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{active_case.get('title')}</div>
                <div style="color:#64748B; font-size:0.75rem; margin-top:2px;">📍 {active_case.get('location')}</div>
                <div style="margin-top:4px;">{status_badge_html(active_case.get('status', 'Open'))}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 1.4rem 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 0.73rem; color: #94A3B8; line-height: 1.4;">
        Powered by <strong>Google Gemma 4</strong> Multimodal Vision.<br>
        Built for Student Developer Showcase 2026.
    </div>
    """, unsafe_allow_html=True)

# Main Canvas Header
active_case_id = st.session_state.get("selected_case_id", "")
render_brand_header(active_module=st.session_state["nav_module"], active_case_id=active_case_id)

# Module Routing
active_mod = st.session_state["nav_module"]

if active_mod == "Overview Dashboard":
    render_dashboard_view()
elif active_mod == "New Inspection":
    render_inspection_view()
elif active_mod == "Visual Evidence Lab":
    render_evidence_lab_view()
elif active_mod == "AI Findings":
    render_findings_view()
elif active_mod == "Investigation Workspace":
    render_workspace_view()
elif active_mod == "Case Management":
    render_cases_view()
elif active_mod == "Reports & Export":
    render_reports_view()
elif active_mod == "Analytics & Trends":
    render_analytics_view()
elif active_mod == "Settings & Model":
    render_settings_view()
