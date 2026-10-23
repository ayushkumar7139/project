import os
import json
import re
from typing import Dict, Any, Tuple
from PIL import Image
from google import genai

DEFAULT_GEMMA_MODEL = "gemma-4-26b-a4b-it"


def get_api_key() -> str:
    # 1. Try streamlit secrets if running inside streamlit
    try:
        import streamlit as st
        key = st.secrets.get("GOOGLE_API_KEY", "")
        if key and key.strip() and key.strip() != "YOUR_ACTUAL_API_KEY":
            return key.strip()
    except Exception:
        pass
    
    # 2. Try direct read from .streamlit/secrets.toml
    try:
        import tomllib
        from pathlib import Path
        secrets_path = Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml"
        if secrets_path.exists():
            with open(secrets_path, "rb") as f:
                data = tomllib.load(f)
                key = data.get("GOOGLE_API_KEY", "")
                if key and key.strip() and key.strip() != "YOUR_ACTUAL_API_KEY":
                    return key.strip()
    except Exception:
        pass

    # 3. Try environment variable
    env_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if env_key and env_key != "YOUR_ACTUAL_API_KEY":
        return env_key
    return ""


def test_gemma_connection(model_id: str = DEFAULT_GEMMA_MODEL, api_key: str = "") -> Tuple[bool, str]:
    key = api_key or get_api_key()
    if not key:
        return False, "API key is missing or set to placeholder value."
    try:
        client = genai.Client(api_key=key)
        # Test with a minimal prompt
        resp = client.models.generate_content(
            model=model_id.strip(),
            contents="Respond with the word 'ONLINE' if you are active."
        )
        text = (resp.text or "").strip()
        return True, f"Connection successful! Model response: {text[:60]}"
    except Exception as exc:
        return False, f"Connection error: {str(exc)}"


def build_analysis_prompt(context: str, location: str, category: str, concern: str) -> str:
    return f"""You are REALITY CHECK AI, a senior visual evidence investigator and diagnostic safety reasoning engine.
Analyze the attached photograph carefully and objectively for real-world issues, hazards, structural defects, accessibility barriers, or maintenance concerns.

INSPECTION CONTEXT SUPPLIED BY OPERATOR:
- Location / Environment: {location.strip() or "Not specified"}
- User Context Note: {context.strip() or "No additional notes provided"}
- Operator Category: {category}
- Reported Concern Level: {concern}

CORE OPERATIONAL RULES:
1. SEE THE EVIDENCE: Only document details that are directly, unmistakably visible in the image as "visual_observations".
2. UNDERSTAND THE UNCERTAINTY: Clearly distinguish what is directly observed from "possible_interpretations" and "unconfirmed_information".
3. NO FABRICATION: Do not invent measurements, exact codes, legal violations, hidden structural statuses, or human identities.
4. CONFIDENCE VS SEVERITY: "visual_confidence" is strictly how clearly the camera captures the physical condition. "suggested_priority" is the operational urgency. Do not conflate the two.
5. SAFE, ACTIONABLE GUIDANCE: Provide pragmatic, safe verification steps and recommendations.

You MUST respond ONLY with a single valid JSON object following this exact structure with no extra text before or after:
{{
  "summary": "1 to 2 concise sentences summarizing the primary physical condition visible.",
  "visual_observations": [
    "Factually observed item 1 with approximate visual location and spatial context",
    "Factually observed item 2"
  ],
  "possible_interpretations": [
    "Plausible technical interpretation or potential origin 1",
    "Plausible technical interpretation or potential origin 2"
  ],
  "unconfirmed_information": [
    "Crucial factor that cannot be confirmed from this single photo alone 1",
    "Crucial factor that cannot be confirmed from this single photo alone 2"
  ],
  "potential_consequences": [
    "Realistic downstream consequence if left unattended 1",
    "Realistic downstream consequence if left unattended 2"
  ],
  "visual_confidence": "High" | "Medium" | "Low",
  "confidence_rationale": "Clear explanation of image clarity, angles, lighting, and occlusion factors.",
  "suggested_priority": "Immediate Attention" | "High" | "Moderate" | "Low",
  "priority_rationale": "Technical rationale balancing consequence severity with likelihood.",
  "verification_checklist": [
    "Specific physical check or measurement to execute on-site 1",
    "Specific physical check or measurement to execute on-site 2",
    "Specific physical check or measurement to execute on-site 3"
  ],
  "recommended_actions": [
    "Immediate containment or safety step",
    "Remediation or repair action",
    "Follow-up verification procedure"
  ],
  "suggested_report_message": "A concise, professional email or ticket message suitable for dispatching to a facilities manager or civic public works desk.",
  "limitations": "Statement documenting the boundaries of single-angle optical AI assessment."
}}"""


def _clean_and_parse_json(raw_text: str) -> Dict[str, Any]:
    text = raw_text.strip()
    
    # Strip markdown code fencing if present
    if text.startswith("```"):
        # Match ```json ... ``` or ``` ... ```
        pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        match = re.search(pattern, text)
        if match:
            text = match.group(1).strip()
            
    # Try direct JSON parsing
    try:
        return json.loads(text)
    except Exception:
        pass
        
    # Find outer curly braces
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end + 1]
        try:
            return json.loads(candidate)
        except Exception:
            pass

    # If JSON parsing completely fails, extract structured markdown sections
    return _fallback_markdown_parser(raw_text)


def _fallback_markdown_parser(text: str) -> Dict[str, Any]:
    # Robust fallback when model returns markdown sections
    result = {
        "summary": "AI visual analysis generated findings from the submitted photograph.",
        "visual_observations": [],
        "possible_interpretations": [],
        "unconfirmed_information": [],
        "potential_consequences": [],
        "visual_confidence": "Medium",
        "confidence_rationale": "Evaluated based on single photographic perspective.",
        "suggested_priority": "Moderate",
        "priority_rationale": "Preliminary visual assessment pending physical site inspection.",
        "verification_checklist": ["Inspect site in person", "Confirm dimensions and substrate condition"],
        "recommended_actions": ["Restrict access if hazard exists", "Notify maintenance coordinator"],
        "suggested_report_message": "Inspection record submitted for review.",
        "limitations": "Guidance derived from automated visual model inference."
    }
    
    lines = text.split("\n")
    current_key = None
    
    for line in lines:
        l = line.strip()
        lower = l.lower()
        if "summary" in lower and ("#" in l or ":" in l):
            current_key = "summary"
            continue
        elif "visible" in lower or "observation" in lower or "evidence" in lower:
            current_key = "visual_observations"
            continue
        elif "might mean" in lower or "interpretation" in lower:
            current_key = "possible_interpretations"
            continue
        elif "cannot confirm" in lower or "uncertain" in lower or "unknown" in lower:
            current_key = "unconfirmed_information"
            continue
        elif "consequence" in lower or "risk" in lower:
            current_key = "potential_consequences"
            continue
        elif "priority" in lower:
            if "immediate" in lower:
                result["suggested_priority"] = "Immediate Attention"
            elif "high" in lower:
                result["suggested_priority"] = "High"
            elif "low" in lower:
                result["suggested_priority"] = "Low"
            else:
                result["suggested_priority"] = "Moderate"
            continue
        elif "recommend" in lower or "action" in lower or "next step" in lower:
            current_key = "recommended_actions"
            continue
        elif "verify" in lower or "checklist" in lower:
            current_key = "verification_checklist"
            continue
            
        if l and current_key:
            clean_item = re.sub(r"^[-*0-9.]+\s*", "", l).strip()
            if clean_item:
                if isinstance(result[current_key], list):
                    result[current_key].append(clean_item)
                elif current_key == "summary" and len(result["summary"]) < 100:
                    result["summary"] = clean_item

    return result


def analyze_inspection_image(
    image: Image.Image,
    context: str,
    location: str,
    category: str,
    concern: str,
    model_id: str = DEFAULT_GEMMA_MODEL,
    api_key: str = ""
) -> Tuple[Dict[str, Any], str]:
    """
    Submits image and prompt to Gemma multimodal model.
    Returns (structured_findings, raw_response_text).
    Raises Exception if API call fails.
    """
    key = api_key or get_api_key()
    if not key:
        raise ValueError("Google AI API Key not found. Please provide an API key in .streamlit/secrets.toml or Settings.")
        
    client = genai.Client(api_key=key)
    prompt = build_analysis_prompt(context, location, category, concern)
    
    response = client.models.generate_content(
        model=model_id.strip(),
        contents=[prompt, image]
    )
    
    raw_text = (response.text or "").strip()
    if not raw_text:
        raise ValueError("The Gemma model returned an empty response. Verify image format and model availability.")
        
    structured = _clean_and_parse_json(raw_text)
    
    # Format checklist into objects with completed flags
    raw_checklist = structured.get("verification_checklist", [])
    formatted_checklist = []
    for idx, item in enumerate(raw_checklist, start=1):
        if isinstance(item, str):
            formatted_checklist.append({"id": idx, "task": item, "completed": False, "notes": ""})
        elif isinstance(item, dict):
            formatted_checklist.append(item)
    structured["verification_checklist"] = formatted_checklist
    
    return structured, raw_text
