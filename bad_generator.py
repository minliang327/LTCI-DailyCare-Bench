"""
Bad Generator: Intentionally generates care plans with medical errors
This generator includes all assessment items from database.py and deliberately violates rules
"""
from typing import List, Set
from models import AssessmentInput, DailyPlan, CareTask, Qualification
from database import (
    get_task_info,
    get_required_tasks,
    get_contraindicated_tasks,
    ASSESSMENT_RULES,
    SAFETY_CONSTRAINTS,
    SERVICE_TASKS,
    is_nurse_only_task
)


def generate_bad_plan(assessment: AssessmentInput) -> DailyPlan:
    """
    Generate a care plan with intentional errors that violate safety and qualification rules.
    This generator includes tasks from ALL assessment rules to test comprehensive coverage.
    
    Strategy: Include ALL tasks from ASSESSMENT_RULES to ensure every assessment item is covered,
    but introduce deliberate errors to test the evaluator's ability to catch violations.
    
    Errors intentionally introduced:
    1. Assign nurse-only tasks to caregivers (qualification violation)
    2. Include tasks that violate safety constraints (e.g., walking for bedridden patients)
    3. Missing some basic mandatory tasks (to test missing task detection)
    4. Incorrect total duration calculation
    5. Include unnecessary tasks for conditions not present in assessment
    """
    
    all_task_ids = set()
    bad_tasks = []
    
    # Step 1: Collect tasks from ALL assessment rules
    # This ensures comprehensive coverage of all assessment items in database.py
    # We include tasks from all rules, regardless of whether the condition matches the assessment
    for condition, required_tasks in ASSESSMENT_RULES.items():
        if isinstance(required_tasks, list):
            all_task_ids.update(required_tasks)
    
    # Step 2: Add ALL nurse-only tasks to test qualification violations
    # These tasks require NURSE qualification but will be assigned to Caregiver
    nurse_only_tasks = [14, 26, 27, 28, 29, 33, 34, 35, 37, 38, 39, 40, 41, 42]
    all_task_ids.update(nurse_only_tasks)
    
    # Step 3: Add tasks that violate safety constraints
    # ERROR: Include walking task (21) even if patient is completely unable to move
    # This violates SAFETY_CONSTRAINTS["Mobility: Completely unable"] = [21]
    all_task_ids.add(21)  # Walking task - will violate if patient is bedridden
    
    # Step 4: Remove some basic mandatory tasks to test missing task detection
    # ERROR: Intentionally exclude basic tasks like task 1 (head/face cleaning)
    # This simulates a plan that forgets essential hygiene tasks
    basic_tasks_to_exclude = [1]  # Exclude head/face cleaning
    all_task_ids.difference_update(basic_tasks_to_exclude)
    
    # Step 5: Create tasks with intentional errors
    total_duration = 0
    
    for task_id in sorted(all_task_ids):
        task_info = get_task_info(task_id)
        if not task_info:
            continue
        
        # ERROR 1: Assign nurse-only tasks to caregivers (qualification violation)
        if is_nurse_only_task(task_id):
            assigned_to = "Caregiver"  # ❌ WRONG: Should be "Nurse"
        else:
            assigned_to = "Caregiver"
        
        # ERROR 2: Use incorrect duration (sometimes shorter than minimum)
        min_duration = task_info["min_duration"]
        # For some tasks, intentionally use shorter duration
        if task_id in [14, 26, 35]:  # Some critical tasks
            duration = max(5, min_duration - 5)  # Make it shorter
        else:
            duration = min_duration
        
        task = CareTask(
            task_id=task_id,
            name=task_info["name"],
            min_duration=min_duration,
            qualification=task_info["qualification"],
            content=task_info.get("content", ""),
            assigned_to=assigned_to  # ❌ Wrong assignment for nurse tasks
        )
        
        bad_tasks.append(task)
        total_duration += duration
    
    # Note: The plan includes tasks that violate safety constraints:
    # - Walking task (21) is included even if patient is completely unable to move
    # - This violates SAFETY_CONSTRAINTS["Mobility: Completely unable"] = [21]
    # - Ostomy care (27) is included even if patient doesn't have ostomy
    # - This violates SAFETY_CONSTRAINTS["No ostomy"] = [27]
    
    # ERROR 3: Incorrect total duration calculation
    # Intentionally report wrong total duration (less than actual)
    reported_duration = max(0, total_duration - 50)  # Report significantly less than actual
    
    # Extract date from assessment or use default
    date_str = "2026-01-16"
    if hasattr(assessment, 'assessment_id') and assessment.assessment_id:
        # Try to extract date from assessment_id if it contains date info
        date_str = "2026-01-16"  # Default date
    
    return DailyPlan(
        date=date_str,
        tasks=bad_tasks,
        total_duration=reported_duration  # ❌ Wrong total duration
    )
