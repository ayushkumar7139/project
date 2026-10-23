import os
from PIL import Image, ImageDraw
import streamlit as st
from modules.storage import get_all_cases, get_case_by_id, save_case, save_image_to_storage
from modules.ui_components import status_badge_html, priority_badge_html, confidence_badge_html


def render_evidence_lab_view():
    cases = get_all_cases()
    if not cases:
        st.info("No cases currently recorded. Please create a new inspection first.")
        return
        
    case_ids = [c["id"] for c in cases]
    selected_id = st.session_state.get("selected_case_id")
    if selected_id not in case_ids:
        selected_id = case_ids[0]
        st.session_state["selected_case_id"] = selected_id
        
    # Top Case Navigation Strip
    col_sel, col_stat, col_nav = st.columns([4, 4, 4])
    with col_sel:
        case_options = [f"{c['id']} — {c.get('title', 'Untitled')[:35]}" for c in cases]
        current_idx = case_ids.index(selected_id)
        chosen = st.selectbox("Active Case Selection", case_options, index=current_idx)
        selected_id = chosen.split(" — ")[0]
        st.session_state["selected_case_id"] = selected_id
        
    case = get_case_by_id(selected_id)
    if not case:
        st.error("Selected case could not be retrieved.")
        return
        
    findings = case.get("ai_findings", {})
    priority = findings.get("suggested_priority", "Moderate")
    confidence = findings.get("visual_confidence", "High")
    status = case.get("status", "Open")
    
    with col_stat:
        st.markdown(f"""
        <div style="padding-top:1.6rem; display:flex; align-items:center; gap:0.6rem;">
            {status_badge_html(status)}
            {priority_badge_html(priority)}
            {confidence_badge_html(confidence)}
        </div>
        """, unsafe_allow_html=True)
        
    with col_nav:
        st.markdown("<div style='padding-top:1.4rem; display:flex; justify-content:flex-end; gap:0.5rem;'>", unsafe_allow_html=True)
        if st.button("🛠️ Open Workspace", use_container_width=True):
            st.session_state["nav_module"] = "Investigation Workspace"
            st.rerun()
        if st.button("📋 AI Findings", use_container_width=True):
            st.session_state["nav_module"] = "AI Findings"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr style='margin: 0.8rem 0 1.2rem 0;'>", unsafe_allow_html=True)
    
    # Lab Mode Tabs: Single Image Inspection vs Before/After Verification
    tab_inspect, tab_before_after = st.tabs(["🔬 Detailed Visual Evidence Inspection", "⚖️ Before & After Verification Comparison"])
    
    with tab_inspect:
        col_img, col_facts = st.columns([7, 5], gap="large")
        
        with col_img:
            st.markdown(f"**Evidence Photograph — {case.get('title')}**")
            img_path = case.get("image_path")
            
            show_annotations = st.checkbox("Overlay Detected Evidence Markers", value=True)
            zoom_level = st.select_slider("Image Inspection Scale", options=["Standard", "Enlarged (HD Detail)"], value="Standard")
            
            if img_path and os.path.exists(img_path):
                img = Image.open(img_path)
                display_img = img.copy()
                
                # Draw genuine evidence markers if enabled and annotations exist
                annotations = findings.get("annotations", [])
                if show_annotations and annotations:
                    draw = ImageDraw.Draw(display_img)
                    w, h = display_img.size
                    for idx, ann in enumerate(annotations, start=1):
                        x_px = int((ann.get("x", 50) / 100.0) * w)
                        y_px = int((ann.get("y", 50) / 100.0) * h)
                        r = max(14, int(w * 0.02))
                        # Red target pin
                        draw.ellipse([(x_px - r, y_px - r), (x_px + r, y_px + r)], outline="#DC2626", width=4)
                        draw.ellipse([(x_px - 4, y_px - 4), (x_px + 4, y_px + 4)], fill="#DC2626")
                        draw.text((x_px + r + 6, y_px - r), f"#{idx}: {ann.get('label', '')}", fill="#DC2626")
                        
                st.image(display_img, use_container_width=True, caption=f"Evidence Archive Ref: {os.path.basename(img_path)}")
            else:
                st.warning("Evidence image file not found in storage.")
                
            if findings.get("annotations"):
                st.caption("Active Visual Pins:")
                for idx, ann in enumerate(findings.get("annotations", []), start=1):
                    st.markdown(f"<span style='color:#DC2626; font-weight:700;'>#{idx}</span> **{ann.get('label')}:** {ann.get('note')}", unsafe_allow_html=True)
                    
        with col_facts:
            st.markdown("""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:0.85rem; margin-bottom:1rem;">
                <div style="font-size:0.8rem; font-weight:600; text-transform:uppercase; color:#64748B;">Core Product Principle</div>
                <div style="font-size:0.92rem; font-weight:600; color:#0F172A; margin-top:2px;">
                    Never confuse visible evidence with assumptions.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Evidence vs Inference breakdown
            st.markdown("**1. Direct Visual Observations (Verified in Photo)**")
            obs_list = findings.get("visual_observations", [])
            if obs_list:
                for obs in obs_list:
                    st.markdown(f"""
                    <div class="fact-card">
                        <div class="fact-title">✓ Verified Visual Fact</div>
                        <div style="font-size:0.88rem; color:#1E293B;">{obs}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No direct observations recorded.")
                
            st.markdown("**2. Technical Interpretations (Hypotheses)**")
            interp_list = findings.get("possible_interpretations", [])
            if interp_list:
                for interp in interp_list:
                    st.markdown(f"""
                    <div class="inference-card">
                        <div class="inference-title">? Plausible Hypothesis (Requires On-site Confirmation)</div>
                        <div style="font-size:0.88rem; color:#1E293B;">{interp}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            st.markdown("**3. Unconfirmed Information (Camera Limitations)**")
            unconf_list = findings.get("unconfirmed_information", [])
            if unconf_list:
                for unc in unconf_list:
                    st.markdown(f"""
                    <div class="unknown-card">
                        <div class="unknown-title">✕ Cannot Confirm From Single Image</div>
                        <div style="font-size:0.88rem; color:#1E293B;">{unc}</div>
                    </div>
                    """, unsafe_allow_html=True)

    with tab_before_after:
        st.markdown("### Before & After Resolution Audit")
        st.write("Compare the initial incident photo with the post-remediation verification photo to confirm complete resolution.")
        
        c_before, c_after = st.columns(2, gap="large")
        
        with c_before:
            st.markdown("#### Initial Incident Condition (Before)")
            img_path = case.get("image_path")
            if img_path and os.path.exists(img_path):
                st.image(img_path, caption=f"Reported Condition ({case.get('created_at')})", use_container_width=True)
            else:
                st.info("Initial image unavailable.")
                
        with c_after:
            st.markdown("#### Rectified Condition (After)")
            after_path = case.get("after_image_path")
            if after_path and os.path.exists(after_path):
                st.image(after_path, caption="Verified Rectified Condition", use_container_width=True)
                if st.button("🗑️ Remove After Photo", key=f"del_after_{selected_id}"):
                    case["after_image_path"] = None
                    save_case(case)
                    st.rerun()
            else:
                st.markdown("""
                <div style="border:2px dashed #CBD5E1; border-radius:12px; padding:2.5rem 1.5rem; text-align:center; background:#F8FAFC;">
                    <div style="color:#64748B; font-size:0.95rem; font-weight:500;">No resolution photo uploaded yet.</div>
                    <div style="color:#94A3B8; font-size:0.8rem; margin-top:0.3rem;">Attach proof of repair to complete case verification.</div>
                </div>
                """, unsafe_allow_html=True)
                
                after_file = st.file_uploader("Upload Remediation Proof Photo", type=["jpg", "png", "jpeg", "webp"], key=f"up_after_{selected_id}")
                if after_file:
                    try:
                        raw_after = Image.open(after_file).convert("RGB")
                        saved_after_path = save_image_to_storage(raw_after, filename_prefix="remediated")
                        case["after_image_path"] = saved_after_path
                        save_case(case)
                        st.success("Verification photo uploaded successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving verification photo: {e}")
