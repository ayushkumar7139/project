import os
import json
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
DB_FILE = DATA_DIR / "cases.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def _load_raw_data() -> dict:
    if not DB_FILE.exists():
        return {"cases": []}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"cases": []}


def _save_raw_data(data: dict) -> None:
    temp_file = DB_FILE.with_suffix(".tmp")
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    temp_file.replace(DB_FILE)


def get_all_cases() -> list:
    data = _load_raw_data()
    cases = data.get("cases", [])
    # Sort descending by updated_at or created_at
    cases.sort(key=lambda c: c.get("updated_at", c.get("created_at", "")), reverse=True)
    return cases


def get_case_by_id(case_id: str) -> dict | None:
    cases = get_all_cases()
    for c in cases:
        if c.get("id") == case_id:
            return c
    return None


def save_case(case: dict) -> dict:
    data = _load_raw_data()
    cases = data.get("cases", [])
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not case.get("id"):
        # Generate new sequential or unique ID
        year = datetime.now().year
        count = len(cases) + 1
        case["id"] = f"RC-{year}-{count:03d}"
        case["created_at"] = now_str
    
    case["updated_at"] = now_str
    
    # Check if existing
    found = False
    for i, existing in enumerate(cases):
        if existing.get("id") == case["id"]:
            cases[i] = case
            found = True
            break
            
    if not found:
        cases.insert(0, case)
        
    data["cases"] = cases
    _save_raw_data(data)
    return case


def delete_case(case_id: str) -> bool:
    data = _load_raw_data()
    cases = data.get("cases", [])
    initial_len = len(cases)
    cases = [c for c in cases if c.get("id") != case_id]
    if len(cases) != initial_len:
        data["cases"] = cases
        _save_raw_data(data)
        return True
    return False


def save_image_to_storage(image: Image.Image, filename_prefix: str = "evidence") -> str:
    unique_name = f"{filename_prefix}_{uuid.uuid4().hex[:10]}.jpg"
    target_path = IMAGES_DIR / unique_name
    image.save(target_path, "JPEG", quality=92)
    return str(target_path)


def seed_sample_cases_if_needed(force: bool = False) -> None:
    cases = get_all_cases()
    if cases and not force:
        return
        
    # Generate 3 realistic sample images
    img1_path = IMAGES_DIR / "sample_fire_exit.jpg"
    img2_path = IMAGES_DIR / "sample_water_leak.jpg"
    img3_path = IMAGES_DIR / "sample_trip_hazard.jpg"
    after1_path = IMAGES_DIR / "sample_fire_exit_cleared.jpg"
    
    # 1. Fire exit with obstruction image
    if not img1_path.exists() or force:
        img1 = Image.new("RGB", (900, 600), color="#E2E8F0")
        d1 = ImageDraw.Draw(img1)
        # Corridor floor & walls
        d1.rectangle([(0, 380), (900, 600)], fill="#94A3B8")
        d1.polygon([(0, 380), (300, 100), (600, 100), (900, 380)], fill="#CBD5E1")
        # Door
        d1.rectangle([(350, 140), (550, 480)], fill="#334155", outline="#0F172A", width=4)
        d1.rectangle([(370, 160), (530, 260)], fill="#10B981") # Exit sign green
        d1.text((410, 200), "EMERGENCY EXIT", fill="#FFFFFF")
        # Obstruction: Wooden pallets and metal crates blocking the door
        d1.rectangle([(320, 350), (460, 490)], fill="#D97706", outline="#78350F", width=3)
        d1.rectangle([(440, 370), (580, 500)], fill="#B45309", outline="#78350F", width=3)
        d1.text((340, 420), "WOODEN CRATES / PALLETS", fill="#FFFFFF")
        d1.text((340, 440), "BLOCKING SWING PATH", fill="#FEF08A")
        img1.save(img1_path, "JPEG")
        
        # After image (cleared)
        after1 = Image.new("RGB", (900, 600), color="#E2E8F0")
        d_after = ImageDraw.Draw(after1)
        d_after.rectangle([(0, 380), (900, 600)], fill="#94A3B8")
        d_after.polygon([(0, 380), (300, 100), (600, 100), (900, 380)], fill="#CBD5E1")
        d_after.rectangle([(350, 140), (550, 480)], fill="#334155", outline="#0F172A", width=4)
        d_after.rectangle([(370, 160), (530, 260)], fill="#10B981")
        d_after.text((410, 200), "EMERGENCY EXIT", fill="#FFFFFF")
        d_after.text((380, 440), "CORRIDOR CLEARED", fill="#047857")
        after1.save(after1_path, "JPEG")

    # 2. Water seepage above conduit
    if not img2_path.exists() or force:
        img2 = Image.new("RGB", (900, 600), color="#F1F5F9")
        d2 = ImageDraw.Draw(img2)
        # Wall / ceiling
        d2.rectangle([(0, 0), (900, 180)], fill="#E2E8F0")
        # Water stain
        d2.ellipse([(280, 40), (620, 220)], fill="#CBD5E1", outline="#94A3B8", width=3)
        d2.ellipse([(340, 80), (560, 190)], fill="#93C5FD", outline="#60A5FA", width=2)
        d2.text((370, 120), "ACTIVE CEILING LEAK / DISCOLORATION", fill="#1E3A8A")
        # Electrical Conduit pipe running right beneath
        d2.rectangle([(100, 260), (800, 280)], fill="#64748B", outline="#334155", width=2)
        d2.rectangle([(420, 280), (540, 440)], fill="#94A3B8", outline="#475569", width=2)
        d2.text((435, 340), "SUBPANEL / CONDUIT", fill="#0F172A")
        # Water droplets
        for pt in [(440, 210), (470, 230), (500, 220)]:
            d2.ellipse([pt, (pt[0]+12, pt[1]+22)], fill="#3B82F6")
        img2.save(img2_path, "JPEG")

    # 3. Trip hazard heave
    if not img3_path.exists() or force:
        img3 = Image.new("RGB", (900, 600), color="#F8FAFC")
        d3 = ImageDraw.Draw(img3)
        # Outdoor pavement slabs
        d3.rectangle([(0, 300), (450, 600)], fill="#94A3B8", outline="#64748B", width=3)
        # Displaced / raised slab
        d3.polygon([(450, 270), (900, 290), (900, 600), (450, 600)], fill="#CBD5E1", outline="#475569", width=4)
        # Crack and gap
        d3.line([(450, 270), (450, 600)], fill="#1E293B", width=6)
        d3.text((470, 320), "RAISED SLAB (~45mm HEAVE)", fill="#B91C1C")
        d3.text((470, 350), "PEDESTRIAN TRIP HAZARD", fill="#991B1B")
        img3.save(img3_path, "JPEG")

    sample_cases = [
        {
            "id": "RC-2026-001",
            "title": "Blocked Emergency Fire Exit Stairwell",
            "location": "Science Wing B, 2nd Floor Stairwell 4",
            "category": "Safety or access",
            "user_concern": "High",
            "user_description": "Wooden pallets and shipping crates dumped right in front of the emergency push-bar exit door during lab deliveries.",
            "image_path": str(img1_path),
            "after_image_path": str(after1_path),
            "created_at": "2026-10-21 09:30:00",
            "updated_at": "2026-10-22 14:15:00",
            "status": "Resolved",
            "owner": "Marcus Vance (Safety Officer)",
            "deadline": "2026-10-22",
            "ai_model": "gemma-4-26b-a4b-it",
            "is_sample": True,
            "ai_findings": {
                "summary": "Large wooden shipping pallets and cardboard crates are positioned directly in front of an outward-swinging emergency exit door marked with an illuminated exit sign.",
                "visual_observations": [
                    "Stacked wooden pallets (approx. 1.2m wide) located within 0.5m of the emergency exit door",
                    "Push-bar emergency egress door swing path is clearly compromised",
                    "Illuminated green 'EMERGENCY EXIT' signage visible above door frame",
                    "Floor surface in corridor shows scuff marks from dragged freight"
                ],
                "possible_interpretations": [
                    "Temporary staging of lab equipment deliveries left unattended",
                    "Storage spillover from adjacent overcrowded loading bay",
                    "Disregard of fire safety egress regulations during renovation"
                ],
                "unconfirmed_information": [
                    "Whether the crates are currently empty or containing hazardous contents",
                    "Duration that the blockage has been in place",
                    "Whether an alternate unlocked egress is accessible nearby within code limits"
                ],
                "potential_consequences": [
                    "Impeded emergency evacuation during building alarm or fire event",
                    "Crush injury or panic blockage at dead-end stairwell threshold",
                    "Severe regulatory violation under National Life Safety Code guidelines"
                ],
                "visual_confidence": "High",
                "confidence_rationale": "Clear, unobstructed sightline with prominent spatial proximity between the obstruction and emergency hardware.",
                "suggested_priority": "Immediate Attention",
                "priority_rationale": "Direct obstruction of a certified life-safety egress route presents immediate risk to human occupants in an evacuation.",
                "verification_checklist": [
                    {"id": 1, "task": "Physically confirm whether push-bar door can open past 30 degrees", "completed": True, "notes": "Blocked at 15 degrees swing"},
                    {"id": 2, "task": "Identify delivery manifest tag or department owner on crate labels", "completed": True, "notes": "Tagged for Dept of Biophysics"},
                    {"id": 3, "task": "Dispatch rapid relocation crew to clear corridor immediately", "completed": True, "notes": "Crates relocated to storage unit S-12"},
                    {"id": 4, "task": "Obtain post-clearance photograph for verification record", "completed": True, "notes": "Uploaded clear photo"}
                ],
                "recommended_actions": [
                    "Dispatch immediate facilities staff to relocate all pallets to designated holding room",
                    "Issue safety violation advisory to Science Wing delivery dock staff",
                    "Conduct follow-up sweep within 4 hours to verify egress remains clear"
                ],
                "suggested_report_message": "URGENT SAFETY NOTICE: Emergency Exit Stairwell 4 in Science Wing B is severely obstructed by stacked wooden pallets. Please dispatch maintenance immediately to restore code compliance.",
                "limitations": "Visual assessment cannot ascertain weight of materials or whether door locking hardware was compromised.",
                "annotations": [
                    {"label": "Obstruction Footprint", "x": 42, "y": 70, "note": "Primary physical blockage"},
                    {"label": "Emergency Hardware", "x": 50, "y": 30, "note": "Designated egress path"}
                ]
            },
            "investigation_notes": [
                {"timestamp": "2026-10-21 10:05", "author": "Marcus Vance", "text": "Called loading dock coordinator. Driver left materials while waiting for freight elevator."},
                {"timestamp": "2026-10-21 11:20", "author": "Facilities Crew 2", "text": "Pallets cleared and hallway swept. Photo captured for record."}
            ],
            "history": [
                {"timestamp": "2026-10-21 09:30", "action": "Case created from visual inspection", "actor": "Automated Gemma Intake"},
                {"timestamp": "2026-10-21 09:45", "action": "Assigned to Marcus Vance (Safety Officer)", "actor": "Admin"},
                {"timestamp": "2026-10-21 11:30", "action": "Verification photo attached", "actor": "Facilities Crew 2"},
                {"timestamp": "2026-10-22 14:15", "action": "Resolved with human approval", "actor": "Chief Inspector L. Ramos"}
            ],
            "resolution": {
                "resolved_by": "Chief Inspector L. Ramos",
                "resolved_at": "2026-10-22 14:15:00",
                "verification_notes": "Corridor fully inspected and confirmed 100% clear. Delivery guidelines reinforced with logistics vendor.",
                "approval_status": "Approved"
            }
        },
        {
            "id": "RC-2026-002",
            "title": "Ceiling Water Seepage Above Electrical Distribution Subpanel",
            "location": "Basement Utility Room U-104",
            "category": "Building or maintenance",
            "user_concern": "High",
            "user_description": "Discoloration and visible moisture dripping onto conduit raceways leading down into building breaker panel.",
            "image_path": str(img2_path),
            "after_image_path": None,
            "created_at": "2026-10-22 15:40:00",
            "updated_at": "2026-10-23 08:10:00",
            "status": "Action Required",
            "owner": "David Kim (Master Electrician)",
            "deadline": "2026-10-23",
            "ai_model": "gemma-4-26b-a4b-it",
            "is_sample": True,
            "ai_findings": {
                "summary": "Moisture ring and water droplets visible on drywall ceiling situated vertically above metallic conduit pipes entering an electrical subpanel.",
                "visual_observations": [
                    "Circular water stain approx 40cm in diameter on ceiling plaster",
                    "Active water droplet bead formation directly above rigid steel conduit",
                    "Electrical enclosure housing circuit breakers mounted 1 meter below seepage zone",
                    "Rust stains beginning to form on galvanized conduit coupling"
                ],
                "possible_interpretations": [
                    "HVAC condensation overflow line backed up on floor above",
                    "Domestic plumbing supply pipe pinhole leak within ceiling cavity",
                    "Rainwater ingress from degraded exterior wall flashing"
                ],
                "unconfirmed_information": [
                    "Source of the water above the ceiling plenum",
                    "Whether liquid has entered the interior of the electrical enclosure",
                    "Voltage rating and live circuits fed by the subpanel"
                ],
                "potential_consequences": [
                    "Short circuit, breaker arc flash, or localized fire inside utility panel",
                    "Electrocution hazard for maintenance personnel touching enclosure",
                    "Unscheduled power outage to downstream critical server rooms"
                ],
                "visual_confidence": "High",
                "confidence_rationale": "High contrast between moisture discolored drywall and clean surrounding substrate; conduit proximity is unmistakable.",
                "suggested_priority": "High",
                "priority_rationale": "Water ingress adjacent to energized electrical distribution creates combined electrocution and equipment destruction risk.",
                "verification_checklist": [
                    {"id": 1, "task": "De-energize subpanel feed if moisture enters enclosure", "completed": True, "notes": "Subpanel inspected; interior dry for now"},
                    {"id": 2, "task": "Inspect floor above (Room 104 plumbing chase) to locate leak origin", "completed": False, "notes": "Waiting for master key to plumbing shaft"},
                    {"id": 3, "task": "Install temporary drip catchment diverter away from electrical gear", "completed": False, "notes": "Catchment tarp staged"},
                    {"id": 4, "task": "Conduct thermal imaging sweep across breaker panel", "completed": False, "notes": "Scheduled for 14:00 today"}
                ],
                "recommended_actions": [
                    "Deploy certified electrician with calibrated insulated tools to monitor panel",
                    "Shut off isolation valves in plumbing chase above if pipe rupture confirmed",
                    "Set up temporary protective water shield over conduit until ceiling repaired"
                ],
                "suggested_report_message": "CRITICAL MAINTENANCE DISPATCH: Water seepage observed directly above electrical subpanel in Room U-104. Urgent plumbing and electrical investigation required to prevent equipment damage.",
                "limitations": "Camera cannot penetrate ceiling tiles to verify hidden piping or water accumulation depth.",
                "annotations": [
                    {"label": "Water Stain", "x": 48, "y": 20, "note": "Primary leak zone"},
                    {"label": "Electrical Panel", "x": 50, "y": 65, "note": "Energized target equipment"}
                ]
            },
            "investigation_notes": [
                {"timestamp": "2026-10-22 16:30", "author": "David Kim", "text": "Verified panel interior is currently dry. Moisture is traveling down outer surface of conduit."},
                {"timestamp": "2026-10-23 08:00", "author": "Facilities Lead", "text": "Escalated to mechanical plumbing vendor for urgent inspection."}
            ],
            "history": [
                {"timestamp": "2026-10-22 15:40", "action": "Case created from visual inspection", "actor": "Inspector J. Patel"},
                {"timestamp": "2026-10-22 16:00", "action": "Status changed to Action Required", "actor": "Operations Dispatch"}
            ],
            "resolution": None
        },
        {
            "id": "RC-2026-003",
            "title": "Severe Concrete Walkway Slab Heave & Trip Hazard",
            "location": "North Quad Pedestrian Plaza, Near Library Entrance",
            "category": "Road or public space",
            "user_concern": "Medium",
            "user_description": "Uneven concrete pavement slab sticking up almost 2 inches along high-traffic student pathway.",
            "image_path": str(img3_path),
            "after_image_path": None,
            "created_at": "2026-10-23 08:30:00",
            "updated_at": "2026-10-23 09:15:00",
            "status": "Investigating",
            "owner": "Elena Rostova (Civil Works)",
            "deadline": "2026-10-26",
            "ai_model": "gemma-4-26b-a4b-it",
            "is_sample": True,
            "ai_findings": {
                "summary": "Differential settlement or tree root intrusion causing an abrupt vertical displacement of approximately 40-50mm between adjacent concrete paving slabs on a primary pedestrian route.",
                "visual_observations": [
                    "Sharp vertical ledge between slab joint sections",
                    "Spalling and edge fracture along the raised slab border",
                    "High-contrast shadow indicating significant vertical offset",
                    "Located directly along paved thoroughfare leading to public building entrance"
                ],
                "possible_interpretations": [
                    "Subsurface tree root heave from nearby mature oak trees",
                    "Soil erosion or freeze-thaw subgrade destabilization",
                    "Heavy maintenance vehicle loading exceeding slab design capacity"
                ],
                "unconfirmed_information": [
                    "Exact physical displacement measurement in millimeters",
                    "Presence of active underground utilities immediately underneath the joint",
                    "Nighttime illumination levels over this specific walkway section"
                ],
                "potential_consequences": [
                    "Pedestrian trip and fall injuries, particularly in low-light or rush hours",
                    "Accessibility barrier and ADA non-compliance for wheelchair users",
                    "Accelerated slab fracturing under repetitive pedestrian load"
                ],
                "visual_confidence": "High",
                "confidence_rationale": "Clear geometric ledge profile, continuous crack line, and surface texture contrast.",
                "suggested_priority": "Moderate",
                "priority_rationale": "Active trip hazard in a high-traffic pedestrian corridor, though not presenting an immediate life-safety collapse.",
                "verification_checklist": [
                    {"id": 1, "task": "Measure exact vertical height delta with digital gauge", "completed": True, "notes": "Measured 46mm max delta"},
                    {"id": 2, "task": "Paint high-visibility safety yellow warning line on ledge", "completed": False, "notes": "Spray paint requisitioned"},
                    {"id": 3, "task": "Assess whether concrete grinding or slab mudjacking is feasible", "completed": False, "notes": "Contractor quote pending"}
                ],
                "recommended_actions": [
                    "Apply temporary high-visibility warning paint immediately",
                    "Place temporary cone or ramp if wheelchair accessible detour is distant",
                    "Schedule concrete scarifying / grinding repair crew within 5 business days"
                ],
                "suggested_report_message": "MAINTENANCE REQUEST: Walkway slab heave of ~46mm detected outside North Quad Library entrance. Poses trip hazard. Please apply safety marking and schedule surface beveling.",
                "limitations": "Surface view cannot reveal root diameter beneath or underlying soil moisture conditions.",
                "annotations": [
                    {"label": "Raised Ledge", "x": 50, "y": 45, "note": "46mm vertical offset"}
                ]
            },
            "investigation_notes": [
                {"timestamp": "2026-10-23 09:10", "author": "Elena Rostova", "text": "Gauge measurement confirmed 46mm. ADA threshold is exceeded (>6mm). Yellow marking scheduled for noon."}
            ],
            "history": [
                {"timestamp": "2026-10-23 08:30", "action": "Reported via mobile inspection intake", "actor": "Student Peer Inspector"},
                {"timestamp": "2026-10-23 08:45", "action": "Assigned to Elena Rostova (Civil Works)", "actor": "Admin"}
            ],
            "resolution": None
        }
    ]

    for sc in sample_cases:
        save_case(sc)
