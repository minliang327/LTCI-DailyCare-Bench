"""
Green Agent Evaluator Core Logic
"""
from typing import List, Set, Dict, Any, Union
from models import (
    AssessmentInput, 
    DailyPlan, 
    CareTask, 
    ScoreResult, 
    ScoreBreakdown,
    Qualification
)
from database import (
    get_task_info,
    get_required_tasks,
    get_contraindicated_tasks,
    is_nurse_only_task,
    ASSESSMENT_RULES,
    SAFETY_CONSTRAINTS
)


class GreenAgentEvaluator:
    """Green Agent Evaluator"""
    
    def __init__(
        self,
        mandatory_weight: float = 0.5,
        duration_weight: float = 0.3,
        safety_weight: float = 0.2,
        duration_min: int = 100,
        duration_max: int = 140,
        duration_target: int = 120
    ):
        """
        Initialize the evaluator
        
        Args:
            mandatory_weight: Weight for mandatory tasks (default 50%)
            duration_weight: Weight for duration score (default 30%)
            safety_weight: Weight for safety constraints (default 20%)
            duration_min: Minimum duration in minutes
            duration_max: Maximum duration in minutes
            duration_target: Target duration in minutes
        """
        self.mandatory_weight = mandatory_weight
        self.duration_weight = duration_weight
        self.safety_weight = safety_weight
        self.duration_min = duration_min
        self.duration_max = duration_max
        self.duration_target = duration_target
        
        # Validate that weights sum to 1.0
        total_weight = mandatory_weight + duration_weight + safety_weight
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, current sum is {total_weight}")
    
    def evaluate(self, assessment: AssessmentInput, plan: DailyPlan) -> ScoreResult:
        """
        Evaluate a care plan
        
        Args:
            assessment: Assessment input data
            plan: Daily care plan
            
        Returns:
            ScoreResult: Evaluation result
        """
        # Extract task IDs from the plan
        plan_task_ids = {task.task_id for task in plan.tasks}
        
        # 1. Evaluate mandatory tasks
        mandatory_result = self._evaluate_mandatory_tasks(assessment, plan_task_ids)
        
        # 2. Evaluate safety constraints
        safety_result = self._evaluate_safety_constraints(assessment, plan_task_ids)
        
        # 3. Evaluate duration
        duration_result = self._evaluate_duration(plan)
        
        # 4. Evaluate qualifications
        qualification_result = self._evaluate_qualifications(plan)
        
        # Build score breakdown
        breakdown = ScoreBreakdown(
            mandatory_score=mandatory_result["score"],
            mandatory_coverage=mandatory_result["coverage"],
            mandatory_missing=mandatory_result["missing"],
            safety_score=safety_result["score"],
            safety_violations=safety_result["violations"],
            duration_score=duration_result["score"],
            duration_minutes=duration_result["minutes"],
            duration_target=self.duration_target,
            qualification_score=qualification_result["score"],
            qualification_issues=qualification_result["issues"]
        )
        
        # Calculate overall score (qualification issues as penalty, not weighted)
        overall_score = (
            mandatory_result["score"] * self.mandatory_weight +
            duration_result["score"] * self.duration_weight +
            safety_result["score"] * self.safety_weight
        )
        
        # Apply qualification penalty if there are issues (max 20% penalty)
        if qualification_result["issues"]:
            qualification_penalty = min(0.2, len(qualification_result["issues"]) * 0.05)
            overall_score = max(0.0, overall_score - qualification_penalty)
        
        # Determine if passed (overall score >= 0.8 and no serious errors)
        passed = (
            overall_score >= 0.8 and
            len(safety_result["violations"]) == 0 and
            len(qualification_result["issues"]) == 0
        )
        
        # Generate warnings and errors
        warnings = []
        errors = []
        
        if mandatory_result["missing"]:
            warnings.append(f"Missing {len(mandatory_result['missing'])} mandatory tasks")
        
        if safety_result["violations"]:
            errors.append(f"Safety constraint violations: tasks {safety_result['violations']}")
        
        if qualification_result["issues"]:
            errors.append(f"Qualification mismatch: {len(qualification_result['issues'])} tasks")
        
        if duration_result["minutes"] < self.duration_min:
            warnings.append(f"Total duration too short: {duration_result['minutes']} minutes (recommended: {self.duration_min}-{self.duration_max} minutes)")
        elif duration_result["minutes"] > self.duration_max:
            warnings.append(f"Total duration too long: {duration_result['minutes']} minutes (recommended: {self.duration_min}-{self.duration_max} minutes)")
        
        return ScoreResult(
            overall_score=round(overall_score, 3),
            breakdown=breakdown,
            passed=passed,
            warnings=warnings,
            errors=errors
        )
    
    def _evaluate_mandatory_tasks(
        self, 
        assessment: AssessmentInput, 
        plan_task_ids: Set[int]
    ) -> Dict[str, Any]:
        """Evaluate mandatory task coverage"""
        required_task_ids = set()
        
        # Extract all conditions from assessment data and find required tasks
        for condition, required_tasks in ASSESSMENT_RULES.items():
            # Check if assessment data contains this condition
            if self._condition_matches(assessment, condition):
                if isinstance(required_tasks, list):
                    # AND relationship: all tasks must be included
                    required_task_ids.update(required_tasks)
                elif isinstance(required_tasks, set):
                    # OR relationship: at least one must be included
                    required_task_ids.update(required_tasks)
        
        # Calculate coverage
        if not required_task_ids:
            # If no mandatory tasks required, return full score
            return {
                "score": 1.0,
                "coverage": 1.0,
                "missing": []
            }
        
        # Check OR relationship tasks (at least one must be satisfied)
        missing_tasks = []
        satisfied_or_groups = set()
        
        for condition, required_tasks in ASSESSMENT_RULES.items():
            if not self._condition_matches(assessment, condition):
                continue
                
            if isinstance(required_tasks, list):
                # AND relationship: check if all tasks are in the plan
                for task_id in required_tasks:
                    if task_id not in plan_task_ids:
                        missing_tasks.append(task_id)
            elif isinstance(required_tasks, set):
                # OR relationship: check if at least one task is in the plan
                if not any(task_id in plan_task_ids for task_id in required_tasks):
                    missing_tasks.extend(list(required_tasks))
                else:
                    satisfied_or_groups.add(condition)
        
        # Remove duplicates
        missing_tasks = list(set(missing_tasks))
        
        # Calculate coverage
        total_required = len(required_task_ids)
        covered = total_required - len(missing_tasks)
        coverage = covered / total_required if total_required > 0 else 1.0
        
        # Calculate score (coverage directly as score)
        score = coverage
        
        return {
            "score": round(score, 3),
            "coverage": round(coverage, 3),
            "missing": missing_tasks
        }
    
    def _evaluate_safety_constraints(
        self,
        assessment: AssessmentInput,
        plan_task_ids: Set[int]
    ) -> Dict[str, Any]:
        """Evaluate safety constraints"""
        violations = []
        
        # Check all safety constraints
        for condition, contraindicated_tasks in SAFETY_CONSTRAINTS.items():
            if self._condition_matches(assessment, condition):
                # If plan contains contraindicated tasks, record violation
                for task_id in contraindicated_tasks:
                    if task_id in plan_task_ids:
                        violations.append(task_id)
        
        # Calculate score (0.0 if violations exist, 1.0 if no violations)
        score = 0.0 if violations else 1.0
        
        return {
            "score": score,
            "violations": violations
        }
    
    def _evaluate_duration(self, plan: DailyPlan) -> Dict[str, Any]:
        """Evaluate duration"""
        # Calculate total duration
        if plan.total_duration is not None:
            total_minutes = plan.total_duration
        else:
            # If total duration not provided, calculate from tasks
            total_minutes = sum(task.min_duration for task in plan.tasks)
        
        # Calculate score (based on distance from target duration)
        if total_minutes < self.duration_min:
            # Below minimum duration, linear penalty
            score = max(0.0, total_minutes / self.duration_min)
        elif total_minutes > self.duration_max:
            # Exceeds maximum duration, linear penalty
            excess = total_minutes - self.duration_max
            max_excess = 60  # Allow up to 60 minutes excess
            score = max(0.0, 1.0 - (excess / max_excess))
        else:
            # Within reasonable range, full score
            score = 1.0
        
        return {
            "score": round(score, 3),
            "minutes": total_minutes
        }
    
    def _evaluate_qualifications(self, plan: DailyPlan) -> Dict[str, Any]:
        """Evaluate qualification matching"""
        issues = []
        
        for task in plan.tasks:
            task_info = get_task_info(task.task_id)
            required_qualification = task_info.get("qualification")
            
            # If task requires nurse qualification
            if required_qualification == Qualification.NURSE:
                # Check if assigned to non-nurse
                if task.assigned_to and task.assigned_to.lower() not in ["nurse"]:
                    issues.append({
                        "task_id": task.task_id,
                        "task_name": task.name,
                        "required": "Nurse",
                        "assigned": task.assigned_to
                    })
        
        # Calculate score (penalty if qualification issues exist)
        score = 1.0 if len(issues) == 0 else 0.0
        
        return {
            "score": score,
            "issues": issues
        }
    
    def _condition_matches(self, assessment: AssessmentInput, condition: str) -> bool:
        """
        Check if assessment data matches the condition
        
        Args:
            assessment: Assessment input
            condition: Condition string, format like "Dietary habit: Low sugar or sugar-free"
            
        Returns:
            bool: Whether the condition matches
        """
        # Parse condition string
        if ":" not in condition:
            return False
        
        field_name, expected_value = condition.split(":", 1)
        field_name = field_name.strip()
        expected_value = expected_value.strip()
        
        # Get field value from assessment data
        actual_value = assessment.get_field_value(field_name)
        
        if actual_value is None:
            return False
        
        # Handle different types of comparisons
        if isinstance(expected_value, str):
            # String matching
            if expected_value.startswith(">="):
                # Numeric comparison >=
                try:
                    threshold = int(expected_value[2:].strip())
                    return isinstance(actual_value, (int, float)) and actual_value >= threshold
                except ValueError:
                    return False
            elif expected_value.startswith("<"):
                # Numeric comparison <
                try:
                    threshold = int(expected_value[1:].strip())
                    return isinstance(actual_value, (int, float)) and actual_value < threshold
                except ValueError:
                    return False
            elif expected_value.lower() in ["yes", "true", "是"]:
                # Boolean or string matching
                return actual_value is True or str(actual_value).lower() in ["yes", "true", "是"]
            elif expected_value.lower() in ["no", "false", "否"]:
                return actual_value is False or str(actual_value).lower() in ["no", "false", "否"]
            else:
                # Exact match or substring match
                # Also check in assessment_data dictionary directly
                if field_name in assessment.assessment_data:
                    assessment_value = assessment.assessment_data[field_name]
                    # Check if condition key matches or value matches
                    if condition in assessment.assessment_data:
                        return assessment.assessment_data[condition] is True
                    if isinstance(assessment_value, bool) and assessment_value is True:
                        # If it's a boolean True, check if condition key contains the field name
                        return field_name in condition or condition in str(assessment_value)
                    return str(assessment_value) == expected_value or expected_value in str(assessment_value)
                return str(actual_value) == expected_value or expected_value in str(actual_value)
        
        return False
