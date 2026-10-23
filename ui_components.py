import streamlit as st


def inject_custom_css():
    st.markdown("""
    <style>
    /* Google Fonts & Base Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0F172A;
    }
    
    /* Layout boundaries */
    .block-container {
        max-width: 1320px;
        padding-top: 1.2rem;
        padding-bottom: 3.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Top Brand Navigation Bar */
    .brand-top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.85rem 1.4rem;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }
    .brand-logo-group {
        display: flex;
        align-items: center;
        gap: 0.85rem;
    }
    .brand-icon {
        width: 36px;
        height: 36px;
        background: #0F766E;
        color: #FFFFFF;
        border-radius: 9px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 2px 4px rgba(15, 118, 110, 0.25);
    }
    .brand-title {
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #0F172A;
        margin: 0;
        line-height: 1.2;
    }
    .brand-subtitle {
        font-size: 0.78rem;
        font-weight: 500;
        color: #64748B;
        margin: 0;
        letter-spacing: 0.02em;
    }
    .brand-badge {
        font-size: 0.75rem;
        font-weight: 600;
        background: #F1F5F9;
        color: #334155;
        border: 1px solid #CBD5E1;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
    }
    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #10B981;
    }

    /* KPI Cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
        border-color: #CBD5E1;
    }
    .kpi-title {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.1;
        margin-bottom: 0.3rem;
    }
    .kpi-subtext {
        font-size: 0.78rem;
        color: #64748B;
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }

    /* Panel Card Container */
    .panel-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.35rem 1.5rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }
    .panel-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 0.85rem;
        margin-bottom: 1.15rem;
    }
    .panel-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #0F172A;
        margin: 0;
    }
    .panel-subtitle {
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 0.2rem;
    }

    /* Status Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        line-height: 1.2;
    }
    .badge-open {
        background: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
    }
    .badge-investigating {
        background: #FFFBEB;
        color: #B45309;
        border: 1px solid #FDE68A;
    }
    .badge-action {
        background: #FEF2F2;
        color: #B91C1C;
        border: 1px solid #FECACA;
    }
    .badge-resolved {
        background: #ECFDF5;
        color: #047857;
        border: 1px solid #A7F3D0;
    }
    .badge-reopened {
        background: #FAF5FF;
        color: #7E22CE;
        border: 1px solid #E9D5FF;
    }

    /* Priority Badges */
    .priority-immediate {
        background: #7F1D1D;
        color: #FFFFFF;
        padding: 0.22rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .priority-high {
        background: #FEE2E2;
        color: #991B1B;
        border: 1px solid #FCA5A5;
        padding: 0.22rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .priority-moderate {
        background: #FEF3C7;
        color: #92400E;
        border: 1px solid #FCD34D;
        padding: 0.22rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .priority-low {
        background: #E0F2FE;
        color: #0369A1;
        border: 1px solid #BAE6FD;
        padding: 0.22rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* Evidence vs Inference Callouts */
    .fact-card {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-left: 4px solid #16A34A;
        border-radius: 8px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.75rem;
    }
    .fact-title {
        color: #166534;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 0.35rem;
    }
    .inference-card {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-left: 4px solid #D97706;
        border-radius: 8px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.75rem;
    }
    .inference-title {
        color: #92400E;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 0.35rem;
    }
    .unknown-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #64748B;
        border-radius: 8px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.75rem;
    }
    .unknown-title {
        color: #334155;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 0.35rem;
    }

    /* Section Banner */
    .notice-banner {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.85rem 1.1rem;
        color: #475569;
        font-size: 0.85rem;
        line-height: 1.5;
        margin-bottom: 1.25rem;
    }
    .notice-banner strong {
        color: #0F172A;
    }

    /* Streamlit Widget tweaks */
    div[data-testid="stSidebarNav"] {
        display: none !important;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.15s ease;
    }
    .stButton>button[kind="primary"] {
        background-color: #0D9488 !important;
        border-color: #0F766E !important;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #0F766E !important;
    }
    </style>
    """, unsafe_allow_html=True)


def render_brand_header(active_module: str = "Overview", active_case_id: str = ""):
    st.markdown(f"""
    <div class="brand-top-bar">
        <div class="brand-logo-group">
            <div class="brand-icon">RC</div>
            <div>
                <h1 class="brand-title">REALITY CHECK AI</h1>
                <p class="brand-subtitle">Detect What People Miss · Visual Problem Investigation Platform</p>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 0.85rem;">
            {f'<div class="brand-badge"><span style="color:#64748B;">Active Case:</span> <strong>{active_case_id}</strong></div>' if active_case_id else ''}
            <div class="brand-badge">
                <span class="status-dot"></span>
                <span>Gemma 4 Multimodal Vision</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_card(title: str, value: str | int, subtext: str = "", trend_color: str = "#64748B"):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtext" style="color: {trend_color};">{subtext}</div>
    </div>
    """, unsafe_allow_html=True)


def status_badge_html(status: str) -> str:
    status_map = {
        "Open": "badge-open",
        "Investigating": "badge-investigating",
        "Action Required": "badge-action",
        "Resolved": "badge-resolved",
        "Reopened": "badge-reopened"
    }
    css_class = status_map.get(status, "badge-open")
    return f'<span class="badge {css_class}">{status}</span>'


def priority_badge_html(priority: str) -> str:
    p = str(priority).strip()
    if "immediate" in p.lower():
        return '<span class="priority-immediate">⚡ Immediate Attention</span>'
    elif "high" in p.lower():
        return '<span class="priority-high">⚠️ High Priority</span>'
    elif "mod" in p.lower() or "med" in p.lower():
        return '<span class="priority-moderate">⚖️ Moderate Priority</span>'
    else:
        return '<span class="priority-low">ℹ️ Low Priority</span>'


def confidence_badge_html(conf: str) -> str:
    c = str(conf).strip().lower()
    if c == "high":
        return '<span style="background:#DCFCE7; color:#166534; border:1px solid #86EFAC; padding:2px 8px; border-radius:6px; font-size:0.75rem; font-weight:600;">High Visual Confidence</span>'
    elif c == "medium":
        return '<span style="background:#FEF3C7; color:#92400E; border:1px solid #FCD34D; padding:2px 8px; border-radius:6px; font-size:0.75rem; font-weight:600;">Medium Visual Confidence</span>'
    else:
        return '<span style="background:#F1F5F9; color:#475569; border:1px solid #CBD5E1; padding:2px 8px; border-radius:6px; font-size:0.75rem; font-weight:600;">Low Visual Confidence</span>'
