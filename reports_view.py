import os
import base64
from datetime import datetime
import pandas as pd
import streamlit as st
from modules.storage import get_all_cases, get_case_by_id


def _image_to_base64(path: str) -> str:
    if not path or not os.path.exists(path):
        return ""
    try:
        with open(path, "rb") as f:
            data = f.read()
            ext = os.path.splitext(path)[1].lower().replace(".", "")
            if ext == "jpg":
                ext = "jpeg"
            return f"data:image/{ext};base64,{base64.b64encode(data).decode('utf-8')}"
    except Exception:
        return ""


def build_printable_html_report(case: dict) -> str:
    findings = case.get("ai_findings", {})
    img_b64 = _image_to_base64(case.get("image_path", ""))
    after_b64 = _image_to_base64(case.get("after_image_path", ""))
    
    obs_html = "".join([f"<li><strong>Observation:</strong> {o}</li>" for o in findings.get("visual_observations", [])])
    interp_html = "".join([f"<li><strong>Hypothesis:</strong> {i}</li>" for i in findings.get("possible_interpretations", [])])
    unconf_html = "".join([f"<li><strong>Camera Limitation / Unknown:</strong> {u}</li>" for u in findings.get("unconfirmed_information", [])])
    actions_html = "".join([f"<li>{a}</li>" for a in findings.get("recommended_actions", [])])
    
    checklist = findings.get("verification_checklist", [])
    check_rows = ""
    for t in checklist:
        status_sym = "[X] COMPLETED" if t.get("completed") else "[ ] PENDING"
        check_rows += f"<tr><td style='padding:6px; border:1px solid #CBD5E1;'>{status_sym}</td><td style='padding:6px; border:1px solid #CBD5E1;'>{t.get('task')}</td><td style='padding:6px; border:1px solid #CBD5E1;'>{t.get('notes', '—')}</td></tr>"

    resolution = case.get("resolution", {}) or {}
    resolved_html = ""
    if resolution.get("approval_status") == "Approved":
        resolved_html = f"""
        <div style="background:#ECFDF5; border:1px solid #A7F3D0; padding:12px; border-radius:6px; margin-top:15px;">
            <h4 style="color:#047857; margin:0 0 6px 0;">FORMAL HUMAN SIGN-OFF RECORD</h4>
            <p style="margin:0; font-size:13px; color:#065F46;">
                <strong>Sign-off Inspector:</strong> {resolution.get('resolved_by')}<br>
                <strong>Verification Timestamp:</strong> {resolution.get('resolved_at')}<br>
                <strong>Inspector Statement:</strong> {resolution.get('verification_notes')}
            </p>
        </div>
        """
    else:
        resolved_html = """
        <div style="border:1px dashed #CBD5E1; padding:12px; border-radius:6px; margin-top:15px; font-size:12px; color:#64748B;">
            <strong>Human Approval Status:</strong> Pending on-site verification and certified sign-off.
        </div>
        """

    img_section = f"""
    <div style="text-align:center; margin:15px 0;">
        <img src="{img_b64}" style="max-width:100%; max-height:420px; border-radius:8px; border:1px solid #CBD5E1;" />
        <div style="font-size:11px; color:#64748B; margin-top:4px;">Primary Evidence Photograph — Case {case.get('id')}</div>
    </div>
    """ if img_b64 else "<p><em>No image embedded</em></p>"

    after_section = f"""
    <div style="text-align:center; margin:15px 0;">
        <h4 style="color:#0F172A; margin-bottom:6px;">Post-Remediation Verification Photograph</h4>
        <img src="{after_b64}" style="max-width:100%; max-height:420px; border-radius:8px; border:1px solid #10B981;" />
    </div>
    """ if after_b64 else ""

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>Inspection Report - {case.get('id')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #0F172A; margin: 25px; line-height: 1.5; font-size: 13.5px; }}
        h1, h2, h3, h4 {{ color: #0F172A; margin-top: 15px; margin-bottom: 8px; }}
        .header-table {{ width: 100%; border-bottom: 2px solid #0F766E; padding-bottom: 12px; margin-bottom: 18px; }}
        .meta-box {{ background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px; border-radius: 6px; margin-bottom: 16px; }}
        .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px; }}
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; }}
        .badge-urgent {{ background: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5; }}
        .badge-normal {{ background: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        ul {{ padding-left: 20px; margin: 6px 0; }}
        li {{ margin-bottom: 4px; }}
        .disclaimer {{ background: #F1F5F9; border-left: 4px solid #64748B; padding: 10px; font-size: 11.5px; color: #475569; margin-top: 25px; }}
        @media print {{
            body {{ margin: 0; }}
            button {{ display: none !important; }}
        }}
    </style>
    </head>
    <body>
        <table class="header-table">
            <tr>
                <td>
                    <h2 style="margin:0; color:#0F766E;">REALITY CHECK AI · AUDIT REPORT</h2>
                    <div style="font-size:12px; color:#64748B;">Detect What People Miss · Formal Visual Safety & Asset Inspection</div>
                </td>
                <td style="text-align:right;">
                    <div style="font-size:16px; font-weight:bold; color:#0F172A;">{case.get('id')}</div>
                    <div style="font-size:12px; color:#64748B;">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
                </td>
            </tr>
        </table>

        <div class="meta-box">
            <div class="meta-grid">
                <div><strong>Inspection Title:</strong> {case.get('title')}</div>
                <div><strong>Current Status:</strong> {case.get('status')}</div>
                <div><strong>Facility Location:</strong> {case.get('location')}</div>
                <div><strong>Assessed Urgency:</strong> {findings.get('suggested_priority', 'Moderate')}</div>
                <div><strong>Category:</strong> {case.get('category')}</div>
                <div><strong>Assigned Investigator:</strong> {case.get('owner', 'Unassigned')}</div>
                <div><strong>Intake Date:</strong> {case.get('created_at')}</div>
                <div><strong>Vision Model:</strong> {case.get('ai_model', 'gemma-4-26b-a4b-it')}</div>
            </div>
        </div>

        <h3>1. Executive Summary</h3>
        <p>{findings.get('summary', 'No summary provided.')}</p>

        <h3>2. Visual Photographic Evidence</h3>
        {img_section}
        {after_section}

        <h3>3. Fact-Inference-Uncertainty Matrix</h3>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; padding:10px; border-radius:6px;">
                <h4 style="color:#166534; margin:0 0 6px 0;">Direct Photographic Observations</h4>
                <ul>{obs_html or '<li>None</li>'}</ul>
            </div>
            <div style="background:#FFFBEB; border:1px solid #FDE68A; padding:10px; border-radius:6px;">
                <h4 style="color:#92400E; margin:0 0 6px 0;">Technical Hypotheses & Unknowns</h4>
                <strong>Interpretations:</strong>
                <ul>{interp_html or '<li>None</li>'}</ul>
                <strong>Cannot Confirm:</strong>
                <ul>{unconf_html or '<li>None</li>'}</ul>
            </div>
        </div>

        <h3>4. Risk Rationale & Recommended Actions</h3>
        <p><strong>Urgency Rationale:</strong> {findings.get('priority_rationale', '')}</p>
        <p><strong>Optical Confidence:</strong> {findings.get('visual_confidence', 'High')} — {findings.get('confidence_rationale', '')}</p>
        <h4>Prescribed Remediation Steps:</h4>
        <ol>{actions_html or '<li>None recorded</li>'}</ol>

        <h3>5. On-Site Verification Checklist</h3>
        <table>
            <thead>
                <tr style="background:#F1F5F9;">
                    <th style="padding:6px; border:1px solid #CBD5E1; text-align:left; width:120px;">Verification</th>
                    <th style="padding:6px; border:1px solid #CBD5E1; text-align:left;">Inspection Item</th>
                    <th style="padding:6px; border:1px solid #CBD5E1; text-align:left;">Field Result</th>
                </tr>
            </thead>
            <tbody>
                {check_rows or "<tr><td colspan='3' style='padding:6px;'>No checklist items</td></tr>"}
            </tbody>
        </table>

        {resolved_html}

        <div class="disclaimer">
            <strong>DISCLAIMER & LIMITATIONS:</strong> This inspection document is generated by Reality Check AI utilizing Google Gemma multimodal vision reasoning. Observations are bounded by optical perspective and camera resolution. This preliminary guidance does not supersede statutory local authority codes or certified licensed structural engineering inspections.
        </div>
    </body>
    </html>
    """
    return html


def build_markdown_report(case: dict) -> str:
    findings = case.get("ai_findings", {})
    checklist = findings.get("verification_checklist", [])
    
    check_lines = "\n".join([f"- [{'x' if t.get('completed') else ' '}] {t.get('task')} (Notes: {t.get('notes', 'None')})" for t in checklist])
    obs_lines = "\n".join([f"- {o}" for o in findings.get("visual_observations", [])])
    interp_lines = "\n".join([f"- {i}" for i in findings.get("possible_interpretations", [])])
    unconf_lines = "\n".join([f"- {u}" for u in findings.get("unconfirmed_information", [])])
    action_lines = "\n".join([f"{idx+1}. {a}" for idx, a in enumerate(findings.get("recommended_actions", []))])
    
    return f"""# REALITY CHECK AI · AUDIT REPORT
**Case ID:** {case.get('id')}
**Title:** {case.get('title')}
**Location:** {case.get('location')}
**Status:** {case.get('status')}
**Priority:** {findings.get('suggested_priority', 'Moderate')}
**Visual Confidence:** {findings.get('visual_confidence', 'High')}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Model:** {case.get('ai_model', 'gemma-4-26b-a4b-it')}

---

## 1. Quick Summary
{findings.get('summary', 'No summary available.')}

## 2. Direct Visual Observations (Verified Facts)
{obs_lines or 'None'}

## 3. What This Might Mean (Technical Hypotheses)
{interp_lines or 'None'}

## 4. What Cannot Be Confirmed From Photo
{unconf_lines or 'None'}

## 5. Priority & Optical Rationale
- **Urgency Rationale:** {findings.get('priority_rationale', '')}
- **Confidence Explanation:** {findings.get('confidence_rationale', '')}

## 6. Recommended Next Steps
{action_lines or 'None'}

## 7. Verification Checklist
{check_lines or 'None'}

## 8. Suggested Dispatch Message
{findings.get('suggested_report_message', '')}

## 9. Limitations & AI Boundaries
{findings.get('limitations', 'Single photo optical assessment.')}
"""


def render_reports_view():
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <h2 style="margin: 0; font-size: 1.4rem; font-weight: 700; color: #0F172A;">Formal Reports & Data Export</h2>
        <p style="margin: 0.2rem 0 0 0; color: #64748B; font-size: 0.9rem;">
            Generate printable audit reports, export case manifests to CSV, and download Markdown documentation.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    cases = get_all_cases()
    if not cases:
        st.info("No cases currently recorded.")
        return
        
    tab_single, tab_batch = st.tabs(["📄 Individual Case Audit Report", "📊 Case Register CSV Export"])
    
    with tab_single:
        case_options = [f"{c['id']} — {c.get('title', 'Untitled')[:40]}" for c in cases]
        selected_id = st.session_state.get("selected_case_id", cases[0]["id"])
        curr_idx = 0
        for i, c in enumerate(cases):
            if c["id"] == selected_id:
                curr_idx = i
                break
                
        chosen = st.selectbox("Select Case to Generate Formal Audit Report", case_options, index=curr_idx)
        case_id = chosen.split(" — ")[0]
        case = get_case_by_id(case_id)
        
        if not case:
            st.error("Case not found.")
            return

        html_content = build_printable_html_report(case)
        md_content = build_markdown_report(case)

        # Download and print buttons
        col_d1, col_d2, col_d3 = st.columns([1, 1, 1])
        with col_d1:
            st.download_button(
                "⬇️ Download Audit Report (.md)",
                data=md_content,
                file_name=f"reality_check_{case.get('id')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_d2:
            st.download_button(
                "⬇️ Download Text Summary (.txt)",
                data=md_content,
                file_name=f"reality_check_{case.get('id')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_d3:
            st.download_button(
                "🖨️ Download Printable HTML / PDF",
                data=html_content,
                file_name=f"reality_check_{case.get('id')}_report.html",
                mime="text/html",
                type="primary",
                use_container_width=True
            )

        st.markdown("<hr style='margin:1.2rem 0;'>", unsafe_allow_html=True)
        st.markdown("#### Live Printable Report Preview:")
        # Render HTML report inside an iframe or container
        st.components.v1.html(html_content, height=750, scrolling=True)

    with tab_batch:
        st.markdown("#### Export Case Registry to CSV")
        st.write("Export all case records including priority, status, category, location, and owner for reporting in Excel or BI tools.")
        
        records = []
        for c in cases:
            f = c.get("ai_findings", {})
            records.append({
                "Case ID": c.get("id"),
                "Title": c.get("title"),
                "Location": c.get("location"),
                "Category": c.get("category"),
                "Status": c.get("status"),
                "Priority": f.get("suggested_priority", "Moderate"),
                "Confidence": f.get("visual_confidence", "High"),
                "Owner": c.get("owner", "Unassigned"),
                "Deadline": c.get("deadline", ""),
                "Created At": c.get("created_at"),
                "Updated At": c.get("updated_at"),
                "Is Sample": c.get("is_sample", False)
            })
            
        df = pd.DataFrame(records)
        st.dataframe(df, use_container_width=True)
        
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Export Entire Register to CSV (.csv)",
            data=csv_data,
            file_name=f"reality_check_register_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            type="primary"
        )
