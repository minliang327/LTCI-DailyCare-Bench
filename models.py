"""
Pydantic models for Green Agent Benchmark
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class Qualification(str, Enum):
    """Caregiver qualification levels"""
    ANY = "Any"      # Any caregiver
    NURSE = "Nurse"  # Nurse only


class CareTask(BaseModel):
    """Single care task definition"""
    task_id: int = Field(..., description="Task ID")
    name: str = Field(..., description="Task Name")
    min_duration: int = Field(..., ge=0, description="Minimum Duration (minutes)")
    qualification: Qualification = Field(..., description="Required Qualification")
    content: Optional[str] = Field(None, description="Task Description")
    assigned_to: Optional[str] = Field(None, description="Assigned Role (Nurse/Caregiver)")


class DailyPlan(BaseModel):
    """Daily Care Plan"""
    date: str = Field(..., description="Date")
    tasks: List[CareTask] = Field(default_factory=list, description="List of tasks")
    total_duration: Optional[int] = Field(None, description="Total Duration (minutes)")


class AssessmentInput(BaseModel):
    """Assessment Input Data"""
    assessment_id: str = Field(..., description="Assessment ID")
    patient_info: Dict[str, Any] = Field(default_factory=dict, description="Patient Info")
    assessment_data: Dict[str, Any] = Field(default_factory=dict, description="Assessment Raw Data")
    
    # Common fields shortcut
    eating_habits: Optional[str] = Field(None, description="Dietary Habits")
    clothing_neatness: Optional[int] = Field(None, description="Clothing Neatness")
    allergy_info: Optional[str] = Field(None, description="Allergy Info")
    fall_risk: Optional[bool] = Field(None, description="Fall Risk")
    
    def get_field_value(self, field_name: str) -> Any:
        """Helper to retrieve field value from data dict or attribute"""
        return self.assessment_data.get(field_name) or getattr(self, field_name, None)


class ScoreBreakdown(BaseModel):
    """Scoring Breakdown details"""
    mandatory_score: float = Field(0.0, ge=0.0, le=1.0, description="Mandatory Task Score (0-1)")
    mandatory_coverage: float = Field(0.0, ge=0.0, le=1.0, description="Mandatory Task Coverage")
    mandatory_missing: List[int] = Field(default_factory=list, description="IDs of missing mandatory tasks")
    
    safety_score: float = Field(0.0, ge=0.0, le=1.0, description="Safety Score (0-1)")
    safety_violations: List[int] = Field(default_factory=list, description="IDs of tasks violating safety rules")
    
    duration_score: float = Field(0.0, ge=0.0, le=1.0, description="Duration Score (0-1)")
    duration_minutes: int = Field(0, description="Actual Total Duration")
    duration_target: int = Field(120, description="Target Duration")
    
    qualification_score: float = Field(0.0, ge=0.0, le=1.0, description="Qualification Score (0-1)")
    qualification_issues: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="List of qualification issues"
    )


class ScoreResult(BaseModel):
    """Final Evaluation Result"""
    overall_score: float = Field(0.0, ge=0.0, le=1.0, description="Overall Score (0-1)")
    breakdown: ScoreBreakdown = Field(..., description="Detailed Breakdown")
    passed: bool = Field(False, description="Whether the plan passed the benchmark")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    errors: List[str] = Field(default_factory=list, description="Error messages")
