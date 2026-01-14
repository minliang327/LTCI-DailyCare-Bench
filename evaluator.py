"""
Green Agent 评估器核心逻辑
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
    """Green Agent 评估器"""
    
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
        初始化评估器
        
        Args:
            mandatory_weight: 强制性任务权重（默认50%）
            duration_weight: 时长权重（默认30%）
            safety_weight: 安全约束权重（默认20%）
            duration_min: 最小时长（分钟）
            duration_max: 最大时长（分钟）
            duration_target: 目标时长（分钟）
        """
        self.mandatory_weight = mandatory_weight
        self.duration_weight = duration_weight
        self.safety_weight = safety_weight
        self.duration_min = duration_min
        self.duration_max = duration_max
        self.duration_target = duration_target
        
        # 验证权重总和为1.0
        total_weight = mandatory_weight + duration_weight + safety_weight
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"权重总和必须为1.0，当前为{total_weight}")
    
    def evaluate(self, assessment: AssessmentInput, plan: DailyPlan) -> ScoreResult:
        """
        评估护理计划
        
        Args:
            assessment: 评估输入数据
            plan: 每日护理计划
            
        Returns:
            ScoreResult: 评估结果
        """
        # 提取计划中的任务ID
        plan_task_ids = {task.task_id for task in plan.tasks}
        
        # 1. 评估强制性任务
        mandatory_result = self._evaluate_mandatory_tasks(assessment, plan_task_ids)
        
        # 2. 评估安全约束
        safety_result = self._evaluate_safety_constraints(assessment, plan_task_ids)
        
        # 3. 评估时长
        duration_result = self._evaluate_duration(plan)
        
        # 4. 评估资质
        qualification_result = self._evaluate_qualifications(plan)
        
        # 构建评分明细
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
        
        # 计算总分（资质问题作为扣分项，不计入权重）
        overall_score = (
            mandatory_result["score"] * self.mandatory_weight +
            duration_result["score"] * self.duration_weight +
            safety_result["score"] * self.safety_weight
        )
        
        # 如果有资质问题，扣分（最多扣20%）
        if qualification_result["issues"]:
            qualification_penalty = min(0.2, len(qualification_result["issues"]) * 0.05)
            overall_score = max(0.0, overall_score - qualification_penalty)
        
        # 判断是否通过（总分 >= 0.8 且没有严重错误）
        passed = (
            overall_score >= 0.8 and
            len(safety_result["violations"]) == 0 and
            len(qualification_result["issues"]) == 0
        )
        
        # 生成警告和错误信息
        warnings = []
        errors = []
        
        if mandatory_result["missing"]:
            warnings.append(f"缺失{len(mandatory_result['missing'])}个强制性任务")
        
        if safety_result["violations"]:
            errors.append(f"违反安全约束: 任务{safety_result['violations']}")
        
        if qualification_result["issues"]:
            errors.append(f"资质不匹配: {len(qualification_result['issues'])}个任务")
        
        if duration_result["minutes"] < self.duration_min:
            warnings.append(f"总时长过短: {duration_result['minutes']}分钟（建议{self.duration_min}-{self.duration_max}分钟）")
        elif duration_result["minutes"] > self.duration_max:
            warnings.append(f"总时长过长: {duration_result['minutes']}分钟（建议{self.duration_min}-{self.duration_max}分钟）")
        
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
        """评估强制性任务覆盖率"""
        required_task_ids = set()
        
        # 从评估数据中提取所有条件并查找所需任务
        for condition, required_tasks in ASSESSMENT_RULES.items():
            # 检查评估数据中是否包含此条件
            if self._condition_matches(assessment, condition):
                if isinstance(required_tasks, list):
                    # AND关系：所有任务都必须包含
                    required_task_ids.update(required_tasks)
                elif isinstance(required_tasks, set):
                    # OR关系：至少包含一个
                    required_task_ids.update(required_tasks)
        
        # 计算覆盖率
        if not required_task_ids:
            # 如果没有强制性任务要求，返回满分
            return {
                "score": 1.0,
                "coverage": 1.0,
                "missing": []
            }
        
        # 检查OR关系的任务（至少满足一个即可）
        missing_tasks = []
        satisfied_or_groups = set()
        
        for condition, required_tasks in ASSESSMENT_RULES.items():
            if not self._condition_matches(assessment, condition):
                continue
                
            if isinstance(required_tasks, list):
                # AND关系：检查所有任务是否都在计划中
                for task_id in required_tasks:
                    if task_id not in plan_task_ids:
                        missing_tasks.append(task_id)
            elif isinstance(required_tasks, set):
                # OR关系：检查是否至少有一个任务在计划中
                if not any(task_id in plan_task_ids for task_id in required_tasks):
                    missing_tasks.extend(list(required_tasks))
                else:
                    satisfied_or_groups.add(condition)
        
        # 去重
        missing_tasks = list(set(missing_tasks))
        
        # 计算覆盖率
        total_required = len(required_task_ids)
        covered = total_required - len(missing_tasks)
        coverage = covered / total_required if total_required > 0 else 1.0
        
        # 计算得分（覆盖率直接作为得分）
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
        """评估安全约束"""
        violations = []
        
        # 检查所有安全约束
        for condition, contraindicated_tasks in SAFETY_CONSTRAINTS.items():
            if self._condition_matches(assessment, condition):
                # 如果计划中包含禁忌任务，记录违规
                for task_id in contraindicated_tasks:
                    if task_id in plan_task_ids:
                        violations.append(task_id)
        
        # 计算得分（有违规则得0分，无违规则得1分）
        score = 0.0 if violations else 1.0
        
        return {
            "score": score,
            "violations": violations
        }
    
    def _evaluate_duration(self, plan: DailyPlan) -> Dict[str, Any]:
        """评估时长"""
        # 计算总时长
        if plan.total_duration is not None:
            total_minutes = plan.total_duration
        else:
            # 如果没有提供总时长，从任务中计算
            total_minutes = sum(task.min_duration for task in plan.tasks)
        
        # 计算得分（基于目标时长的距离）
        if total_minutes < self.duration_min:
            # 低于最小时长，线性扣分
            score = max(0.0, total_minutes / self.duration_min)
        elif total_minutes > self.duration_max:
            # 超过最大时长，线性扣分
            excess = total_minutes - self.duration_max
            max_excess = 60  # 允许超过60分钟
            score = max(0.0, 1.0 - (excess / max_excess))
        else:
            # 在合理范围内，得满分
            score = 1.0
        
        return {
            "score": round(score, 3),
            "minutes": total_minutes
        }
    
    def _evaluate_qualifications(self, plan: DailyPlan) -> Dict[str, Any]:
        """评估资质匹配"""
        issues = []
        
        for task in plan.tasks:
            task_info = get_task_info(task.task_id)
            required_qualification = task_info.get("qualification")
            
            # 如果任务需要护士资质
            if required_qualification == Qualification.NURSE:
                # 检查是否分配给了非护士
                if task.assigned_to and task.assigned_to.lower() not in ["nurse", "护士"]:
                    issues.append({
                        "task_id": task.task_id,
                        "task_name": task.name,
                        "required": "Nurse",
                        "assigned": task.assigned_to
                    })
        
        # 计算得分（有资质问题则扣分）
        score = 1.0 if len(issues) == 0 else 0.0
        
        return {
            "score": score,
            "issues": issues
        }
    
    def _condition_matches(self, assessment: AssessmentInput, condition: str) -> bool:
        """
        检查评估数据是否匹配条件
        
        Args:
            assessment: 评估输入
            condition: 条件字符串，格式如 "饮食习惯: 低糖或无糖"
            
        Returns:
            bool: 是否匹配
        """
        # 解析条件字符串
        if ":" not in condition:
            return False
        
        field_name, expected_value = condition.split(":", 1)
        field_name = field_name.strip()
        expected_value = expected_value.strip()
        
        # 从评估数据中获取字段值
        actual_value = assessment.get_field_value(field_name)
        
        if actual_value is None:
            return False
        
        # 处理不同类型的比较
        if isinstance(expected_value, str):
            # 字符串匹配
            if expected_value.startswith(">="):
                # 数值比较 >=
                try:
                    threshold = int(expected_value[2:].strip())
                    return isinstance(actual_value, (int, float)) and actual_value >= threshold
                except ValueError:
                    return False
            elif expected_value.startswith("<"):
                # 数值比较 <
                try:
                    threshold = int(expected_value[1:].strip())
                    return isinstance(actual_value, (int, float)) and actual_value < threshold
                except ValueError:
                    return False
            elif expected_value == "是":
                # 布尔值或字符串匹配
                return actual_value is True or str(actual_value) == "是"
            elif expected_value == "否":
                return actual_value is False or str(actual_value) == "否"
            else:
                # 精确匹配或包含匹配
                return str(actual_value) == expected_value or expected_value in str(actual_value)
        
        return False
