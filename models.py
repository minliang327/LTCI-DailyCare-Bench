"""
Pydantic models for Green Agent Benchmark
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class Qualification(str, Enum):
    """护理人员资质类型"""
    ANY = "Any"  # 任何护理人员
    NURSE = "Nurse"  # 仅护士


class CareTask(BaseModel):
    """单个护理任务"""
    task_id: int = Field(..., description="任务ID")
    name: str = Field(..., description="任务名称")
    min_duration: int = Field(..., ge=0, description="最小持续时间（分钟）")
    qualification: Qualification = Field(..., description="所需资质")
    content: Optional[str] = Field(None, description="任务内容描述")
    assigned_to: Optional[str] = Field(None, description="分配给谁（Nurse/Caregiver）")


class DailyPlan(BaseModel):
    """每日护理计划"""
    date: str = Field(..., description="日期")
    tasks: List[CareTask] = Field(default_factory=list, description="任务列表")
    total_duration: Optional[int] = Field(None, description="总时长（分钟）")


class AssessmentInput(BaseModel):
    """评估输入数据"""
    assessment_id: str = Field(..., description="评估ID")
    patient_info: Dict[str, Any] = Field(default_factory=dict, description="患者信息")
    assessment_data: Dict[str, Any] = Field(default_factory=dict, description="评估数据")
    
    # 常见评估字段（示例）
    eating_habits: Optional[str] = Field(None, description="饮食习惯")
    clothing_neatness: Optional[int] = Field(None, description="衣着整洁度")
    allergy_info: Optional[str] = Field(None, description="过敏情况")
    fall_risk: Optional[bool] = Field(None, description="跌倒风险")
    
    def get_field_value(self, field_name: str) -> Any:
        """获取评估字段值"""
        return self.assessment_data.get(field_name) or getattr(self, field_name, None)


class ScoreBreakdown(BaseModel):
    """评分明细"""
    mandatory_score: float = Field(0.0, ge=0.0, le=1.0, description="强制性任务得分 (0-1)")
    mandatory_coverage: float = Field(0.0, ge=0.0, le=1.0, description="强制性任务覆盖率")
    mandatory_missing: List[int] = Field(default_factory=list, description="缺失的强制性任务ID")
    
    safety_score: float = Field(0.0, ge=0.0, le=1.0, description="安全约束得分 (0-1)")
    safety_violations: List[int] = Field(default_factory=list, description="违反安全约束的任务ID")
    
    duration_score: float = Field(0.0, ge=0.0, le=1.0, description="时长得分 (0-1)")
    duration_minutes: int = Field(0, description="实际总时长（分钟）")
    duration_target: int = Field(120, description="目标时长（分钟）")
    
    qualification_score: float = Field(0.0, ge=0.0, le=1.0, description="资质得分 (0-1)")
    qualification_issues: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="资质问题列表，格式: [{'task_id': int, 'required': str, 'assigned': str}]"
    )


class ScoreResult(BaseModel):
    """评估结果"""
    overall_score: float = Field(0.0, ge=0.0, le=1.0, description="总分 (0-1)")
    breakdown: ScoreBreakdown = Field(..., description="评分明细")
    passed: bool = Field(False, description="是否通过基准测试")
    warnings: List[str] = Field(default_factory=list, description="警告信息")
    errors: List[str] = Field(default_factory=list, description="错误信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "overall_score": 0.85,
                "breakdown": {
                    "mandatory_score": 0.9,
                    "safety_score": 1.0,
                    "duration_score": 0.8,
                    "qualification_score": 1.0
                },
                "passed": True
            }
        }
