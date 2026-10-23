import streamlit as st
from modules.storage import get_all_cases, get_case_by_id, save_case
from modules.ui_components import priority_badge_html, confidence_badge_html, status_badge_html


def render_findings_view():
    cases = get_all_cases()
    if not cases:
        st.info("No cases available. Please create an inspection first.")
        return
        
    case_ids = [c["id"] for c in cases]
    selected_id = st.session_state.get("selected_case_id")
    if selected_id not in case_ids:
        selected_id = case_ids[0]
        st.session_state["selected_case_id"] = selected_id
        
    case_options = [f"{c['id']} — {c.get('title', 'Untitled')[:40]}" for c in cases]
    curr_idx = case_ids.index(selected_id)
    chosen = st.selectbox("Inspect AI Findings for Case", case_options, index=curr_idx)
    selected_id = chosen.split(" — ")[0]
    st.session_state["selected_case_id"] = selected_id
    
    case = get_case_by_id(selected_id)
    if not case:
        st.error("Case not found.")
        return
        
    findings = case.get("ai_findings", {})
    summary = findings.get("summary", "No summary available.")
    priority = findings.get("suggested_priority", "Moderate")
    p_rationale = findings.get("priority_rationale", "No rationale provided.")
    confidence = findings.get("visual_confidence", "High")
    c_rationale = findings.get("confidence_rationale", "No confidence explanation provided.")
    consequences = findings.get("potential_consequences", [])
    actions = findings.get("recommended_actions", [])
    limitations = findings.get("limitations", "Assessment bounded by single image.")
    message = findings.get("suggested_report_message", "")
    
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:1.25rem 1.5rem; margin:1rem 0 1.5rem 0;">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.75rem;">
            <div style="font-size:1.2rem; font-weight:700; color:#0F172A;">{case.get('id')}: {case.get('title')}</div>
            <div style="display:flex; gap:0.5rem; align-items:center;">
                {status_badge_html(case.get('status', 'Open'))}
                {priority_badge_html(priority)}
                {confidence_badge_html(confidence)}
            </div>
        </div>
        <p style="margin:0; font-size:0.95rem; color:#334155; line-height:1.5;">
            <strong>Executive Summary:</strong> {summary}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Explainable Risk & Confidence Cards
    col_p, col_c = st.columns(2, gap="medium")
    with col_p:
        st.markdown(f"""
        <div style="background:#FFF7ED; border:1px solid #FED7AA; border-radius:10px; padding:1.1rem; height:100%;">
            <div style="font-size:0.8rem; font-weight:700; text-transform:uppercase; color:#9A3412;">Explainable Risk Prioritization</div>
            <div style="font-size:1.1rem; font-weight:700; color:#7C2D12; margin:0.3rem 0;">Assessed: {priority}</div>
            <div style="font-size:0.88rem; color:#9A3412; line-height:1.45;">{p_rationale}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_c:
        st.markdown(f"""
        <div style="background:#F0FDFA; border:1px solid #99F6E4; border-radius:10px; padding:1.1rem; height:100%;">
            <div style="font-size:0.8rem; font-weight:700; text-transform:uppercase; color:#0F766E;">Optical Confidence Assessment</div>
            <div style="font-size:1.1rem; font-weight:700; color:#115E59; margin:0.3rem 0;">Clarity Rating: {confidence}</div>
            <div style="font-size:0.88rem; color:#0F766E; line-height:1.45;">{c_rationale}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # Detailed 4-part matrix
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown("### ⚠️ Potential Consequences if Unaddressed")
        if consequences:
            for item in consequences:
                st.markdown(f"• **{item}**")
        else:
            st.info("No specific consequences documented.")
            
        st.markdown("### 🛡️ Recommended Safe Next Steps")
        if actions:
            for idx, act in enumerate(actions, start=1):
                st.markdown(f"{idx}. {act}")
        else:
            st.info("No actions recorded.")
            
    with c2:
        st.markdown("### ✉️ Drafted Stakeholder Dispatch Message")
        st.caption("Copy and paste to email or ticketing systems:")
        st.text_area("Suggested Dispatch Message", value=message, height=130, key=f"msg_box_{selected_id}")
        
        st.markdown("### ⚖️ Optical & AI Boundaries (Limitations)")
        st.markdown(f"""
        <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:0.9rem; font-size:0.85rem; color:#475569;">
            {limitations}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 1.5rem 0 1.2rem 0;'>", unsafe_allow_html=True)
    
    # Interactive Verification Questionnaire (Context-Aware Follow-up questions)
    st.markdown("### 🔍 Context-Aware Field Verification Questions")
    st.caption("Gemma generated these specific inquiries for on-site personnel before signing off on resolution:")
    
    checklist = findings.get("verification_checklist", [])
    if checklist:
        for idx, task_obj in enumerate(checklist):
            cols_check = st.columns([1, 8])
            with cols_check[0]:
                is_done = st.checkbox("", value=task_obj.get("completed", False), key=f"find_chk_{selected_id}_{idx}")
                if is_done != task_obj.get("completed", False):
                    task_obj["completed"] = is_done
                    save_case(case)
                    st.rerun()
            with cols_check[1]:
                strike = "line-through" if task_obj.get("completed") else "none"
                color = "#64748B" if task_obj.get("completed") else "#0F172A"
                st.markdown(f"<span style='text-decoration:{strike}; color:{color}; font-size:0.95rem; font-weight:500;'>{task_obj.get('task')}</span>", unsafe_allow_html=True)
                if task_obj.get("notes"):
                    st.caption(f"Note: {task_obj.get('notes')}")
    else:
        st.info("No verification checks recorded.")
