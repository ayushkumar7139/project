from datetime import datetime
import streamlit as st
from modules.storage import get_all_cases, get_case_by_id, save_case
from modules.ui_components import status_badge_html, priority_badge_html


def render_workspace_view():
    cases = get_all_cases()
    if not cases:
        st.info("No cases available. Please start an inspection first.")
        return
        
    case_ids = [c["id"] for c in cases]
    selected_id = st.session_state.get("selected_case_id")
    if selected_id not in case_ids:
        selected_id = case_ids[0]
        st.session_state["selected_case_id"] = selected_id
        
    case_options = [f"{c['id']} — {c.get('title', 'Untitled')[:40]}" for c in cases]
    curr_idx = case_ids.index(selected_id)
    chosen = st.selectbox("Active Investigation Case", case_options, index=curr_idx)
    selected_id = chosen.split(" — ")[0]
    st.session_state["selected_case_id"] = selected_id
    
    case = get_case_by_id(selected_id)
    if not case:
        st.error("Case not found.")
        return
        
    findings = case.get("ai_findings", {})
    status = case.get("status", "Open")
    priority = findings.get("suggested_priority", "Moderate")
    
    # Workspace Banner
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:1.25rem 1.5rem; margin:0.8rem 0 1.5rem 0;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
            <div style="font-size:1.25rem; font-weight:700; color:#0F172A;">{case.get('id')}: {case.get('title')}</div>
            <div style="display:flex; gap:0.5rem; align-items:center;">
                {status_badge_html(status)}
                {priority_badge_html(priority)}
            </div>
        </div>
        <div style="font-size:0.88rem; color:#64748B;">
            📍 <strong>Location:</strong> {case.get('location')} · 👤 <strong>Assigned:</strong> {case.get('owner', 'Unassigned')} · 📅 <strong>Target Deadline:</strong> {case.get('deadline', 'None set')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_left, col_right = st.columns([7, 5], gap="large")
    
    # Left: Editable Verification Checklist & Notes
    with col_left:
        st.markdown("### 📝 Smart Verification Checklist")
        st.caption("Drafted by Gemma based on visual evidence. Complete each task before sign-off.")
        
        checklist = findings.get("verification_checklist", [])
        updated_check = False
        
        for idx, task in enumerate(checklist):
            c_box, c_text, c_note = st.columns([1, 7, 4])
            with c_box:
                checked = st.checkbox("", value=task.get("completed", False), key=f"work_chk_{selected_id}_{idx}")
                if checked != task.get("completed", False):
                    task["completed"] = checked
                    updated_check = True
            with c_text:
                strike = "line-through" if task.get("completed") else "none"
                color = "#64748B" if task.get("completed") else "#0F172A"
                st.markdown(f"<div style='text-decoration:{strike}; color:{color}; padding-top:4px;'>{task.get('task')}</div>", unsafe_allow_html=True)
            with c_note:
                current_note = task.get("notes", "")
                new_note = st.text_input("Findings", value=current_note, key=f"work_note_{selected_id}_{idx}", placeholder="Field measurement / notes")
                if new_note != current_note:
                    task["notes"] = new_note
                    updated_check = True
                    
        if updated_check:
            save_case(case)
            st.rerun()
            
        # Add new custom task
        with st.expander("➕ Add Custom Verification Task", expanded=False):
            new_task_text = st.text_input("Task Description", placeholder="e.g. Calibrate pressure valve")
            if st.button("Add Task") and new_task_text.strip():
                checklist.append({
                    "id": len(checklist) + 1,
                    "task": new_task_text.strip(),
                    "completed": False,
                    "notes": ""
                })
                findings["verification_checklist"] = checklist
                case["ai_findings"] = findings
                save_case(case)
                st.success("Task added.")
                st.rerun()

        st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)
        
        # Operational Field Notes
        st.markdown("### 📋 Investigation Field Notes")
        notes_list = case.get("investigation_notes", [])
        if notes_list:
            for n in reversed(notes_list):
                st.markdown(f"""
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:0.75rem 1rem; margin-bottom:0.6rem;">
                    <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#64748B; margin-bottom:0.25rem;">
                        <strong>{n.get('author', 'Inspector')}</strong>
                        <span>{n.get('timestamp', '')}</span>
                    </div>
                    <div style="font-size:0.88rem; color:#1E293B;">{n.get('text')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No field notes recorded yet.")
            
        with st.form(f"form_note_{selected_id}", clear_on_submit=True):
            note_author = st.text_input("Author Name / Badge", value=case.get("owner", "Inspector"))
            note_content = st.text_area("Add Field Note", placeholder="Log actions taken, contractor contacts, or interim safety measures...")
            if st.form_submit_button("Post Field Note"):
                if note_content.strip():
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                    notes_list.append({"timestamp": now_str, "author": note_author.strip(), "text": note_content.strip()})
                    case["investigation_notes"] = notes_list
                    save_case(case)
                    st.success("Field note logged.")
                    st.rerun()

    # Right: Case Operations & Human Approval Sign-off
    with col_right:
        st.markdown("### ⚙️ Case Operations")
        with st.form(f"form_ops_{selected_id}"):
            current_status = case.get("status", "Open")
            status_options = ["Open", "Investigating", "Action Required", "Resolved", "Reopened"]
            new_status = st.selectbox("Update Case Status", status_options, index=status_options.index(current_status))
            
            new_owner = st.text_input("Assigned Investigator / Team", value=case.get("owner", "Unassigned"))
            new_deadline = st.text_input("Target Resolution Date", value=case.get("deadline", ""))
            
            if st.form_submit_button("Save Case Updates"):
                if new_status != current_status:
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                    hist = case.get("history", [])
                    hist.append({"timestamp": now_str, "action": f"Status updated from {current_status} to {new_status}", "actor": new_owner})
                    case["history"] = hist
                case["status"] = new_status
                case["owner"] = new_owner
                case["deadline"] = new_deadline
                save_case(case)
                st.success("Case operational details saved.")
                st.rerun()

        st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)
        
        # Human Approval Sign-off Before Resolution
        st.markdown("### 🛡️ Human-in-the-Loop Sign-Off")
        st.caption("AI detects and recommends. A qualified human must verify and sign off before final resolution.")
        
        resolution = case.get("resolution")
        if resolution and resolution.get("approval_status") == "Approved":
            st.markdown(f"""
            <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-radius:10px; padding:1.1rem;">
                <div style="color:#047857; font-weight:700; font-size:1rem; margin-bottom:0.4rem;">✓ Human Verified & Formally Resolved</div>
                <div style="font-size:0.85rem; color:#065F46;">
                    <strong>Approved by:</strong> {resolution.get('resolved_by')}<br>
                    <strong>Timestamp:</strong> {resolution.get('resolved_at')}<br>
                    <strong>Verification Notes:</strong> {resolution.get('verification_notes')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Re-open Investigation for Review"):
                case["status"] = "Reopened"
                case["resolution"]["approval_status"] = "Reopened"
                save_case(case)
                st.rerun()
        else:
            with st.form(f"form_approval_{selected_id}"):
                st.write("Complete physical verification and submit sign-off to resolve:")
                reviewer = st.text_input("Inspector / Sign-Off Authority", placeholder="e.g. Chief Safety Officer Jane Doe")
                sign_notes = st.text_area("Verification Sign-Off Statement", placeholder="State how hazard was mitigated and verified on site.")
                all_done = all(t.get("completed", False) for t in checklist) if checklist else True
                
                if not all_done:
                    st.warning("⚠️ Some checklist tasks remain unverified. It is recommended to complete all checks prior to sign-off.")
                    
                if st.form_submit_button("Formally Approve & Resolve Case", type="primary"):
                    if not reviewer.strip():
                        st.error("Please provide inspector name for sign-off audit.")
                    else:
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        case["status"] = "Resolved"
                        case["resolution"] = {
                            "resolved_by": reviewer.strip(),
                            "resolved_at": now_str,
                            "verification_notes": sign_notes.strip() or "Verified on-site.",
                            "approval_status": "Approved"
                        }
                        hist = case.get("history", [])
                        hist.append({"timestamp": now_str[:16], "action": f"Formally resolved with human sign-off by {reviewer}", "actor": reviewer})
                        case["history"] = hist
                        save_case(case)
                        st.success("Case formally verified and resolved!")
                        st.rerun()

        st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)
        
        # Audit Log / Timeline
        st.markdown("### ⏱️ Case Action Timeline")
        hist = case.get("history", [])
        if hist:
            for item in reversed(hist):
                st.markdown(f"""
                <div style="border-left:2px solid #CBD5E1; padding-left:0.85rem; margin-bottom:0.75rem; position:relative;">
                    <div style="font-size:0.75rem; color:#64748B;">{item.get('timestamp')} · <em>{item.get('actor')}</em></div>
                    <div style="font-size:0.85rem; color:#1E293B; font-weight:500;">{item.get('action')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No history recorded.")
