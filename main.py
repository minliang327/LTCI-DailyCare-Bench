"""
Green Agent Benchmark Main Program (Fixed Version + Standard Answer Analysis)
"""
import json
import argparse
from typing import Dict, Any, List
from models import AssessmentInput, DailyPlan, ScoreResult
from evaluator import GreenAgentEvaluator
from generator import BaselineGenerator
from database import get_required_tasks, get_task_info, ASSESSMENT_RULES

# Try to import bad generator
try:
    from bad_generator import generate_bad_plan
    HAS_BAD_GENERATOR = True
except ImportError:
    HAS_BAD_GENERATOR = False

def load_assessment_from_json(file_path: str) -> AssessmentInput:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return AssessmentInput(**data)

def load_plan_from_json(file_path: str) -> DailyPlan:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return DailyPlan(**data)

def create_sample_assessment() -> AssessmentInput:
    return AssessmentInput(
        assessment_id="ASSESS_001",
        patient_info={"name": "Mr. Zhang", "age": 75, "gender": "Male"},
        assessment_data={
            "Dietary habit: Low sugar or sugar-free": True,
            "Clothing cleanliness: Poor": True,
            "Allergy: Food allergy": True,
            "Fall risk": True,
            "Mobility: Partially unable": True,
            "Toileting ability: Partially unable": True,
            "Bathing ability: Completely unable": True,
            "Indwelling catheter: No": False,
            "Need blood glucose monitoring": True
        },
        eating_habits="Low sugar or sugar-free",
        clothing_neatness=2,
        allergy_info="Food allergy",
        fall_risk=True
    )

def print_assessment_items(assessment: AssessmentInput):
    """Step 1: Print all assessment items selected in the assessment form"""
    print("\n" + "="*60)
    print("📋 Step 1: Assessment Form - All Selected Items")
    print("="*60)
    print(f"Assessment ID: {assessment.assessment_id}")
    if assessment.patient_info:
        print(f"Patient: {assessment.patient_info.get('name', 'N/A')}, "
              f"Age: {assessment.patient_info.get('age', 'N/A')}, "
              f"Gender: {assessment.patient_info.get('gender', 'N/A')}")
    print("\nAssessment Data Items:")
    for key, value in assessment.assessment_data.items():
        if value is True or (isinstance(value, (str, int, float)) and value):
            print(f"  ✓ {key}: {value}")
    print("="*60 + "\n")

def print_ground_truth(assessment: AssessmentInput):
    """Step 3: Print ground truth analysis - show which rules are triggered"""
    print("\n" + "="*60)
    print("🔍 Step 3: Ground Truth Analysis")
    print("="*60)
    print("Based on the assessment data, the following mandatory tasks are required:")
    
    triggered_rules = []
    
    # Check each item in assessment_data
    for key, value in assessment.assessment_data.items():
        # Try to match "Key: Value" format (e.g., "Dietary habit: Low sugar or sugar-free")
        condition_str = f"{key}: {value}"
        required_ids = get_required_tasks(condition_str)
        
        # If not matched, try matching Key (e.g., "Fall risk" when value is True)
        if not required_ids and value is True:
            required_ids = get_required_tasks(key)
            
        if required_ids:
            task_names = []
            for tid in required_ids:
                info = get_task_info(tid)
                task_names.append(f"[{tid}] {info.get('name', 'Unknown')}")
            
            print(f"  • Detected '{key}: {value}'")
            print(f"    -> Triggered rule, required tasks: {', '.join(task_names)}")
            triggered_rules.append((key, value, required_ids))

    if not triggered_rules:
        print("  (No rules triggered from assessment data)")
    
    print("="*60 + "\n")

def print_result(result: ScoreResult, title="Step 4: Evaluation Result"):
    print("\n" + "="*60)
    print(title)
    print("="*60)
    print(f"Overall Score: {result.overall_score:.3f} ({'PASSED' if result.passed else 'FAILED'})")
    print(f"Breakdown: Coverage {result.breakdown.mandatory_coverage:.0%} | "
          f"Safety {result.breakdown.safety_score:.3f} | "
          f"Qualification {result.breakdown.qualification_score:.3f} | "
          f"Duration {result.breakdown.duration_score:.3f}")
    
    if result.breakdown.mandatory_missing:
        print(f"\n[!] Missing Mandatory Tasks: {result.breakdown.mandatory_missing}")
    if result.breakdown.safety_violations:
        print(f"\n[!] Safety Violations: {result.breakdown.safety_violations}")
    if result.breakdown.qualification_issues:
        print(f"\n[!] Qualification Issues:")
        for issue in result.breakdown.qualification_issues:
            print(f"    Task {issue['task_id']} requires {issue['required']}, but assigned to {issue['assigned']}")
    if result.warnings:
        print(f"\n[⚠] Warnings:")
        for warning in result.warnings:
            print(f"    {warning}")
    if result.errors:
        print(f"\n[❌] Errors:")
        for error in result.errors:
            print(f"    {error}")
    print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Green Agent Benchmark - Main Program")
    parser.add_argument("--mode", choices=["demo", "evaluate", "generate"], default="demo",
                       help="Operation mode: demo, evaluate, or generate")
    parser.add_argument("--assessment", type=str, help="Path to assessment JSON file")
    parser.add_argument("--plan", type=str, help="Path to plan JSON file")
    parser.add_argument("--output", type=str, help="Path to output JSON file")
    args = parser.parse_args()
    
    if args.mode == "demo":
        print("Green Agent Benchmark - Demo Mode\n")
        assessment = create_sample_assessment()
        
        # Step 1: Print all assessment items
        print_assessment_items(assessment)
        
        # Step 2: Generate plan (evaluation happens here)
        print("="*60)
        print("📝 Step 2: Plan Generation & Evaluation")
        print("="*60)
        print("🤖 Testing: Baseline Generator (Good Agent)...\n")
        generator = BaselineGenerator(target_duration=120)
        plan = generator.generate_perfect_plan(assessment)
        evaluator = GreenAgentEvaluator()
        result = evaluator.evaluate(assessment, plan)
        
        # Step 3: Ground truth analysis
        print_ground_truth(assessment)
        
        # Step 4: Evaluation result
        print_result(result, title="Step 4: Evaluation Result - Good Agent")

        # Bad Agent test (if available)
        if HAS_BAD_GENERATOR:
            print("\n" + "="*60)
            print("🤖 Testing: Adversarial Test (Bad Agent)...")
            print("="*60 + "\n")
            bad_plan = generate_bad_plan(assessment)
            bad_score = evaluator.evaluate(assessment, bad_plan)
            print_result(bad_score, title="Step 4: Evaluation Result - Bad Agent (Successfully Intercepted)")
    
    elif args.mode == "evaluate":
        assessment = load_assessment_from_json(args.assessment)
        plan = load_plan_from_json(args.plan)
        
        # Step 1: Print all assessment items
        print_assessment_items(assessment)
        
        # Step 2: Evaluation
        print("="*60)
        print("📝 Step 2: Plan Evaluation")
        print("="*60 + "\n")
        evaluator = GreenAgentEvaluator()
        result = evaluator.evaluate(assessment, plan)
        
        # Step 3: Ground truth analysis
        print_ground_truth(assessment)
        
        # Step 4: Evaluation result
        print_result(result)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)
            print(f"Result saved to: {args.output}")

    elif args.mode == "generate":
        assessment = load_assessment_from_json(args.assessment)
        generator = BaselineGenerator(target_duration=120)
        plan = generator.generate_perfect_plan(assessment)
        print(json.dumps(plan.model_dump(), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
