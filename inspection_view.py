import os
from datetime import datetime
from PIL import Image, ImageOps
import streamlit as st
from modules.storage import save_case, save_image_to_storage, get_all_cases, IMAGES_DIR
from modules.gemma_client import analyze_inspection_image, DEFAULT_GEMMA_MODEL, get_api_key


def render_inspection_view():
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <h2 style="margin: 0; font-size: 1.4rem; font-weight: 700; color: #0F172A;">Intake & New Visual Inspection</h2>
        <p style="margin: 0.2rem 0 0 0; color: #64748B; font-size: 0.9rem;">
            Upload photographic evidence or select a test scenario. Gemma multimodal vision will extract factual observations and assess risk.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Preset quick-selector for event judges
    with st.expander("✨ Judge / Quick Demo Presets (One-click load real-world scenarios)", expanded=False):
        st.caption("Select a scenario to populate photo and details, then run live Gemma analysis.")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            if st.button("🚪 Obstruction at Fire Exit", use_container_width=True):
                st.session_state["preset_title"] = "Obstructed Corridor Egress Door"
                st.session_state["preset_loc"] = "Student Union, Stairwell 2 West"
                st.session_state["preset_cat"] = "Safety or access"
                st.session_state["preset_desc"] = "Heavy stacked crates and packaging blocking the main emergency exit swing path."
                st.session_state["preset_concern"] = "High"
                st.session_state["preset_image_file"] = str(IMAGES_DIR / "sample_fire_exit.jpg")
                st.rerun()
        with col_p2:
            if st.button("💧 Water Leak Near Electricals", use_container_width=True):
                st.session_state["preset_title"] = "Overhead Water Seepage Near Conduit"
                st.session_state["preset_loc"] = "East Hallway Basement Mechanical Room"
                st.session_state["preset_cat"] = "Building or maintenance"
                st.session_state["preset_desc"] = "Water staining and active droplets running down toward electrical conduit raceway."
                st.session_state["preset_concern"] = "High"
                st.session_state["preset_image_file"] = str(IMAGES_DIR / "sample_water_leak.jpg")
                st.rerun()
        with col_p3:
            if st.button("⚠️ Walkway Heave / Trip Hazard", use_container_width=True):
                st.session_state["preset_title"] = "Raised Concrete Walkway Joint"
                st.session_state["preset_loc"] = "Main Quad Walkway near Lecture Hall 3"
                st.session_state["preset_cat"] = "Road or public space"
                st.session_state["preset_desc"] = "Subgrade displacement created sharp 40mm vertical ridge across pedestrian route."
                st.session_state["preset_concern"] = "Medium"
                st.session_state["preset_image_file"] = str(IMAGES_DIR / "sample_trip_hazard.jpg")
                st.rerun()

    col_media, col_meta = st.columns([1, 1], gap="large")
    
    # Image Input column
    image = None
    with col_media:
        st.markdown("**1. Visual Evidence Capture**")
        input_mode = st.radio("Input Source", ["File Upload", "Camera Capture", "Loaded Preset"], horizontal=True, label_visibility="collapsed")
        
        if input_mode == "File Upload":
            uploaded_file = st.file_uploader(
                "Upload clear photo",
                type=["png", "jpg", "jpeg", "webp"],
                help="Supported formats: JPG, PNG, WEBP. Maximum file size: 25MB."
            )
            if uploaded_file:
                try:
                    raw_img = Image.open(uploaded_file)
                    image = ImageOps.exif_transpose(raw_img).convert("RGB")
                    # Check dimensions
                    if image.width < 100 or image.height < 100:
                        st.warning("Image resolution is very low. Clear photos provide higher confidence.")
                    image.thumbnail((1600, 1600))
                    st.image(image, caption=f"Uploaded photo: {uploaded_file.name} ({image.width}×{image.height}px)", use_container_width=True)
                except Exception as e:
                    st.error(f"Could not load image: {e}")
                    image = None
                    
        elif input_mode == "Camera Capture":
            camera_file = st.camera_input("Capture live photo from camera")
            if camera_file:
                try:
                    raw_img = Image.open(camera_file)
                    image = ImageOps.exif_transpose(raw_img).convert("RGB")
                    image.thumbnail((1600, 1600))
                    st.image(image, caption="Camera capture ready", use_container_width=True)
                except Exception as e:
                    st.error(f"Camera input error: {e}")
                    image = None
                    
        elif input_mode == "Loaded Preset":
            preset_file = st.session_state.get("preset_image_file")
            if preset_file and os.path.exists(preset_file):
                try:
                    image = Image.open(preset_file)
                    st.image(image, caption=f"Loaded Preset: {os.path.basename(preset_file)}", use_container_width=True)
                except Exception as e:
                    st.error(f"Error loading preset: {e}")
                    image = None
            else:
                st.info("No preset selected yet. Click one of the quick scenario buttons above.")

    # Metadata & Inspection Details column
    with col_meta:
        st.markdown("**2. Context & Inspection Metadata**")
        
        default_title = st.session_state.get("preset_title", "")
        title = st.text_input("Inspection Title / Summary", value=default_title, placeholder="e.g. Broken handrail on south staircase")
        
        default_loc = st.session_state.get("preset_loc", "")
        location = st.text_input("Physical Location / Facility Tag", value=default_loc, placeholder="e.g. Science Building, 3rd Floor East Wing")
        
        default_cat = st.session_state.get("preset_cat", "Safety or access")
        cat_options = ["Safety or access", "Building or maintenance", "Cleanliness or waste", "Road or public space", "Equipment or object", "Other"]
        cat_index = cat_options.index(default_cat) if default_cat in cat_options else 0
        category = st.selectbox("Category Classification", cat_options, index=cat_index)
        
        default_concern = st.session_state.get("preset_concern", "Medium")
        concern_options = ["Low", "Medium", "High", "Not sure"]
        concern_index = concern_options.index(default_concern) if default_concern in concern_options else 1
        concern = st.radio("User Preliminary Concern Level", concern_options, index=concern_index, horizontal=True)
        
        default_desc = st.session_state.get("preset_desc", "")
        description = st.text_area("Field Notes / What did you observe?", value=default_desc, placeholder="Describe what led to this inspection, any temporary measures taken, or relevant background.", height=90)
        
        # Duplicate / recurring issue detection check
        if location.strip():
            existing_cases = get_all_cases()
            matches = [c for c in existing_cases if location.strip().lower() in c.get("location", "").lower()]
            if matches:
                st.warning(f"⚠️ Recurring Location Alert: Found {len(matches)} previous inspection(s) at or near '{location}'. Check Case Register to avoid duplicate logging.")

    st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    # Model configuration preview & Action Button
    col_btn, col_info = st.columns([1, 1])
    
    with col_info:
        api_key = get_api_key()
        has_key = bool(api_key and api_key != "YOUR_ACTUAL_API_KEY")
        st.markdown(f"""
        <div style="font-size:0.85rem; color:#64748B; padding:0.4rem 0;">
            <strong>Target Model:</strong> <code style="color:#0F766E;">{DEFAULT_GEMMA_MODEL}</code> · 
            <strong>API Status:</strong> <span style="color:{'#059669' if has_key else '#DC2626'}; font-weight:600;">{'Connected' if has_key else 'Missing Key in secrets.toml'}</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col_btn:
        btn_disabled = (image is None or not title.strip())
        analyze_btn = st.button("🚀 Run Gemma Visual Analysis & Register Case", type="primary", use_container_width=True, disabled=btn_disabled)

    if analyze_btn and image:
        with st.status("Gemma 4 Multimodal Analysis in Progress...", expanded=True) as status_box:
            try:
                st.write("1. Processing optical image resolution & spatial channels...")
                saved_img_path = save_image_to_storage(image, filename_prefix="inspection")
                
                st.write(f"2. Invoking Gemma vision model `{DEFAULT_GEMMA_MODEL}`...")
                findings, raw_text = analyze_inspection_image(
                    image=image,
                    context=description,
                    location=location,
                    category=category,
                    concern=concern,
                    model_id=DEFAULT_GEMMA_MODEL,
                    api_key=api_key
                )
                
                st.write("3. Structuring visual evidence, uncertainty bounds, and verification checklist...")
                
                # Create persistent case
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_case = {
                    "title": title.strip(),
                    "location": location.strip() or "General Facility",
                    "category": category,
                    "user_concern": concern,
                    "user_description": description.strip(),
                    "image_path": saved_img_path,
                    "after_image_path": None,
                    "status": "Action Required" if "immediate" in str(findings.get("suggested_priority", "")).lower() or "high" in str(findings.get("suggested_priority", "")).lower() else "Open",
                    "owner": "Unassigned",
                    "deadline": (datetime.now()).strftime("%Y-%m-%d"),
                    "ai_model": DEFAULT_GEMMA_MODEL,
                    "is_sample": False,
                    "ai_findings": findings,
                    "investigation_notes": [
                        {"timestamp": now_str[:16], "author": "Intake Inspector", "text": "Inspection logged and visual evidence processed by Gemma."}
                    ],
                    "history": [
                        {"timestamp": now_str[:16], "action": "Case created from visual intake", "actor": "Gemma Multimodal Pipeline"}
                    ],
                    "resolution": None
                }
                
                saved = save_case(new_case)
                status_box.update(label="Analysis complete! Case registered.", state="complete", expanded=False)
                
                # Navigate to evidence lab
                st.session_state["selected_case_id"] = saved["id"]
                st.session_state["nav_module"] = "Visual Evidence Lab"
                st.success(f"Case {saved['id']} successfully created!")
                st.rerun()
                
            except Exception as exc:
                status_box.update(label="Analysis failed.", state="error")
                st.error(f"Inspection analysis error: {str(exc)}")
                with st.expander("Diagnostic details"):
                    st.code(str(exc))
