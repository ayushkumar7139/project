import json
import streamlit as st
from modules.gemma_client import get_api_key, test_gemma_connection, DEFAULT_GEMMA_MODEL
from modules.storage import seed_sample_cases_if_needed, _save_raw_data, get_all_cases, DB_FILE


def render_settings_view():
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <h2 style="margin: 0; font-size: 1.4rem; font-weight: 700; color: #0F172A;">System Settings & Diagnostics</h2>
        <p style="margin: 0.2rem 0 0 0; color: #64748B; font-size: 0.9rem;">
            Model configuration, API connectivity verification, theme preferences, and data privacy controls.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_model, col_data = st.columns(2, gap="large")
    
    # Left: Gemma Model & API Diagnostics
    with col_model:
        st.markdown("### 🤖 Gemma Vision Model Configuration")
        
        current_model = st.text_input("Active Multimodal Model ID", value=st.session_state.get("active_model_id", DEFAULT_GEMMA_MODEL))
        st.session_state["active_model_id"] = current_model
        
        api_key = get_api_key()
        has_key = bool(api_key and api_key != "YOUR_ACTUAL_API_KEY")
        
        st.markdown(f"""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:0.9rem; margin:1rem 0;">
            <div style="font-size:0.8rem; font-weight:600; text-transform:uppercase; color:#64748B;">API Credential Security Status</div>
            <div style="font-size:0.95rem; font-weight:600; color:{'#059669' if has_key else '#DC2626'}; margin-top:0.25rem;">
                {'✓ Key Loaded from .streamlit/secrets.toml' if has_key else '✕ Missing or Unconfigured API Key'}
            </div>
            <div style="font-size:0.8rem; color:#64748B; margin-top:0.2rem;">
                {'Key length: ' + str(len(api_key)) + ' characters (safe mask: ' + api_key[:4] + '...' + api_key[-4:] + ')' if has_key else 'Configure GOOGLE_API_KEY in .streamlit/secrets.toml'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⚡ Test Live Gemma Connection", type="primary", use_container_width=True):
            with st.spinner(f"Pinging {current_model}..."):
                ok, msg = test_gemma_connection(model_id=current_model)
                if ok:
                    st.success(f"✓ {msg}")
                else:
                    st.error(f"✕ {msg}")
                    
        st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)
        st.markdown("### 🎨 Visual Theme & Interface")
        st.write("Interface follows human-designed enterprise principles inspired by modern hospital management systems.")
        st.info("Theme: Clean Warm White canvas (#F8FAFC), crisp white panels, deep navy typography (#0F172A), and restrained teal accents (#0D9488).")

    # Right: Data & Privacy Controls
    with col_data:
        st.markdown("### 🛡️ Sample Data & Event Showcase")
        st.caption("Pre-loaded realistic inspections designed for student hackathon judges to explore instantly.")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("🔄 Reload Judge Sample Pack", use_container_width=True):
                seed_sample_cases_if_needed(force=True)
                st.success("Sample inspection pack refreshed with 3 rich test scenarios.")
                st.rerun()
                
        with col_s2:
            if st.button("🗑️ Clear All Stored Cases", use_container_width=True):
                _save_raw_data({"cases": []})
                st.warning("All case records purged from local storage.")
                st.rerun()
                
        st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)
        st.markdown("### 🔒 Data Privacy & Local Sovereignty")
        st.markdown("""
        • **Zero Remote Storage:** All photographic evidence and case metadata remain 100% stored in local project folders (`/data/`).<br>
        • **Sensitive Data Protection:** Photographic inputs are stripped of EXIF coordinates and inspected solely via Google GenAI multimodal endpoint.<br>
        • **No Human Identification:** Prompts strictly instruct the vision model to decline facial profiling or identity inference.
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
        
        # Download raw database JSON
        cases = get_all_cases()
        raw_json = json.dumps({"cases": cases}, indent=2)
        st.download_button(
            "⬇️ Export Raw Database JSON Backup",
            data=raw_json,
            file_name="reality_check_database_backup.json",
            mime="application/json",
            use_container_width=True
        )
