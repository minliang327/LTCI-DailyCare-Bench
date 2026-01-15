"""
Hardcoded database: Based on 42 long-term care insurance service standards (cleaned version)
"""
from typing import Dict, List, Set, Union
from models import Qualification

# ==================== Data A: Service Task List (42 tasks) ====================
SERVICE_TASKS: Dict[int, Dict[str, Union[str, int, Qualification]]] = {
    1: {"name": "Head and face cleaning and grooming", "min_duration": 10, "qualification": Qualification.ANY, "content": "Clean face, comb hair, shave"},
    2: {"name": "Hair washing", "min_duration": 20, "qualification": Qualification.ANY, "content": "Wash hair in comfortable position"},
    3: {"name": "Nail care", "min_duration": 10, "qualification": Qualification.ANY, "content": "Trim fingernails/toenails, treat onychomycosis"},
    4: {"name": "Hand and foot cleaning", "min_duration": 15, "qualification": Qualification.ANY, "content": "Wash hands and feet"},
    5: {"name": "Warm water bath", "min_duration": 30, "qualification": Qualification.ANY, "content": "Full body warm water bath"},
    6: {"name": "Bedside hair washing", "min_duration": 25, "qualification": Qualification.ANY, "content": "Wash hair for bedridden patients"},
    7: {"name": "Assist with eating/drinking", "min_duration": 15, "qualification": Qualification.ANY, "content": "Assist with eating and drinking"},
    8: {"name": "Oral care", "min_duration": 15, "qualification": Qualification.ANY, "content": "Brush teeth, rinse mouth, clean oral cavity"},
    9: {"name": "Dressing and undressing", "min_duration": 15, "qualification": Qualification.ANY, "content": "Assist with dressing and undressing"},
    10: {"name": "Bed making", "min_duration": 20, "qualification": Qualification.ANY, "content": "Change bed sheets and covers"},
    11: {"name": "Bowel and bladder care", "min_duration": 20, "qualification": Qualification.ANY, "content": "Assist with elimination, use bedpan"},
    12: {"name": "Incontinence care", "min_duration": 20, "qualification": Qualification.ANY, "content": "Skin cleaning and care after incontinence"},
    13: {"name": "Constipation care", "min_duration": 20, "qualification": Qualification.ANY, "content": "Non-invasive measures to relieve constipation"},
    14: {"name": "Manual fecal extraction", "min_duration": 15, "qualification": Qualification.NURSE, "content": "⚠️ Manual fecal extraction (nurse only)"},
    15: {"name": "Daily personal hygiene assistance", "min_duration": 15, "qualification": Qualification.ANY, "content": "Daily grooming such as washing face and hands"},
    16: {"name": "Sleep and environment care", "min_duration": 15, "qualification": Qualification.ANY, "content": "Positioning, adjust environment"},
    17: {"name": "Bed sheet/mattress pad change", "min_duration": 15, "qualification": Qualification.ANY, "content": "Change soiled bed sheets and mattress pads"},
    18: {"name": "Medication management", "min_duration": 15, "qualification": Qualification.ANY, "content": "Guide or manage medications"},
    19: {"name": "Turning and back tapping", "min_duration": 20, "qualification": Qualification.ANY, "content": "Turn patient, tap back to expectorate"},
    20: {"name": "Sitting and mobility assistance", "min_duration": 20, "qualification": Qualification.ANY, "content": "Assist bedridden patients to sit up or move"},
    21: {"name": "Walking and stair climbing", "min_duration": 20, "qualification": Qualification.ANY, "content": "Assist with walking on level ground or climbing stairs"},
    22: {"name": "Topical medication", "min_duration": 15, "qualification": Qualification.ANY, "content": "Apply or patch external medication"},
    23: {"name": "Cognitive function support and companionship", "min_duration": 20, "qualification": Qualification.ANY, "content": "Communication, cognitive training"},
    24: {"name": "Functional exercise", "min_duration": 30, "qualification": Qualification.ANY, "content": "Limb function training"},
    25: {"name": "Pressure ulcer prevention care", "min_duration": 20, "qualification": Qualification.ANY, "content": "Turn patient, check high-risk areas"},
    26: {"name": "Indwelling catheter care", "min_duration": 15, "qualification": Qualification.NURSE, "content": "⚠️ Catheter and urine bag management (nurse only)"},
    27: {"name": "Ostomy care", "min_duration": 20, "qualification": Qualification.NURSE, "content": "⚠️ Intestinal/urinary ostomy care (nurse only)"},
    28: {"name": "Bowel movement assistance", "min_duration": 15, "qualification": Qualification.NURSE, "content": "⚠️ Enema suppository/enema/rectal medication (nurse only)"},
    29: {"name": "Nasogastric tube care", "min_duration": 20, "qualification": Qualification.NURSE, "content": "⚠️ Nasogastric tube care (nurse only)"},
    30: {"name": "Medication supervision and reminders", "min_duration": 10, "qualification": Qualification.ANY, "content": "Remind and supervise medication taking"},
    31: {"name": "Physical cooling", "min_duration": 15, "qualification": Qualification.ANY, "content": "Warm water/alcohol bath for fever reduction"},
    32: {"name": "Vital signs monitoring", "min_duration": 15, "qualification": Qualification.ANY, "content": "Temperature, pulse, respiration, blood pressure"},
    33: {"name": "Oxygen inhalation", "min_duration": 20, "qualification": Qualification.NURSE, "content": "⚠️ Nasal cannula oxygen (nurse only)"},
    34: {"name": "Enema", "min_duration": 20, "qualification": Qualification.NURSE, "content": "⚠️ Enema administration (nurse only)"},
    35: {"name": "One-time catheterization", "min_duration": 20, "qualification": Qualification.NURSE, "content": "⚠️ Temporary catheterization (nurse only)"},
    36: {"name": "Blood glucose monitoring", "min_duration": 10, "qualification": Qualification.ANY, "content": "Fingerstick blood glucose testing"},
    37: {"name": "Wound care", "min_duration": 20, "qualification": Qualification.NURSE, "content": "⚠️ Dressing change, wound cleaning (nurse only)"},
    38: {"name": "Venous blood sample collection", "min_duration": 15, "qualification": Qualification.NURSE, "content": "⚠️ Blood draw (nurse only)"},
    39: {"name": "Intramuscular injection", "min_duration": 15, "qualification": Qualification.NURSE, "content": "⚠️ Intramuscular injection (nurse only)"},
    40: {"name": "Subcutaneous injection", "min_duration": 15, "qualification": Qualification.NURSE, "content": "⚠️ Subcutaneous injection (nurse only)"},
    41: {"name": "Drainage tube care", "min_duration": 20, "qualification": Qualification.NURSE, "content": "⚠️ Various drainage tube maintenance (nurse only)"},
    42: {"name": "PICC line maintenance", "min_duration": 20, "qualification": Qualification.NURSE, "content": "⚠️ PICC dressing change and flushing (nurse only)"}
}

# ==================== Data B: Logic Mapping Rules (cleaned version - no AB prefix) ====================
ASSESSMENT_RULES: Dict[str, List[int]] = {
    # --- Diet ---
    "Dietary habit: Low sugar or sugar-free": [7, 36],       # Map: Assist eating(7) + Blood glucose monitoring(36)
    "Dietary habit: Low salt": [7],                # Map: Assist eating(7)
    "Allergy: Food allergy": [7],            # Map: Assist eating(7) - dietary attention
    "Allergy: Drug allergy": [18],           # Map: Medication management(18)
    "Choking risk": [7],                     # Map: Assist eating(7) - prevent choking
    "Aspiration risk": [7],                     # Map: Assist eating(7) - prevent aspiration

    # --- Mobility and Safety ---
    "Fall risk": [23, 21],                # Map: Safety care(23) + Mobility/walking(21)
    "Gait abnormality": [21, 23],                # Map: Mobility(21) + Safety care(23)
    "Mobility: Partially unable": [21, 28],       # Original logic preserved
    
    # --- Skin and Pressure Ulcers ---
    "Skin integrity: Impaired": [22, 25, 37],     # Map: Topical medication(22) + Pressure ulcer prevention(25) + Wound dressing(37)
    "Pressure ulcer risk: High": [19, 25],            # Map: Turning(19) + Pressure ulcer prevention(25)
    
    # --- Personal Hygiene ---
    "Clothing cleanliness: Poor": [9, 15],             # Map: Dressing(9) + Personal cleaning(15)
    "Body moisture": [10, 12, 25],            # Map: Bed making(10) + Incontinence/perineal(12) + Pressure ulcer prevention(25)

    # --- Medical Care (key checks) ---
    "Indwelling catheter: Yes": [26],                # Map: Catheter care(26) - must include
    "Need blood glucose monitoring": [36],                # Map: Blood glucose monitoring(36)
    "Need physical cooling": [31],                # Map: Physical cooling(31)
    "Need oxygen": [33],                    # Map: Oxygen inhalation(33)
    "Need PICC maintenance": [42],                # Map: PICC maintenance(42)
    "Severe constipation": [28],                    # Map: Enema suppository/enema(28)
}

# ==================== Safety Constraints (cleaned version) ====================
SAFETY_CONSTRAINTS: Dict[str, List[int]] = {
    "Mobility: Completely unable": [21],           # Bedridden patients should not be scheduled for "walking"
    "Dysphagia": [7],                      # (Example) Requires special care
    "No catheter": [26],                       # Cannot charge for catheter care without catheter
    "No ostomy": [27],                       # Cannot charge for ostomy care without ostomy
}

# ==================== Helper Functions (includes is_nurse_only_task) ====================
def get_task_info(task_id: int) -> Dict[str, Union[str, int, Qualification]]:
    return SERVICE_TASKS.get(task_id, {})

def get_required_tasks(condition: str) -> List[int]:
    """Supports fuzzy matching (triggers as long as keywords are included)"""
    required = []
    for key, tasks in ASSESSMENT_RULES.items():
        # Example: If input is "Allergy: Food allergy", it can match key "Allergy: Food allergy"
        if key in condition or condition in key: 
            required.extend(tasks)
    return list(set(required))

def get_contraindicated_tasks(condition: str) -> List[int]:
    return SAFETY_CONSTRAINTS.get(condition, [])

def get_all_task_ids() -> List[int]:
    return list(SERVICE_TASKS.keys())

def is_nurse_only_task(task_id: int) -> bool:
    """Determine if task is nurse-only"""
    task_info = get_task_info(task_id)
    if not task_info:
        return False
    return task_info.get("qualification") == Qualification.NURSE
