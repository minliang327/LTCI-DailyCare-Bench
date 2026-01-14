"""
基线代理：基于规则生成完美的护理计划
"""
from typing import List, Set
from models import AssessmentInput, DailyPlan, CareTask, Qualification
from database import (
    get_task_info,
    get_required_tasks,
    ASSESSMENT_RULES,
    SERVICE_TASKS
)


class BaselineGenerator:
    """基线生成器：根据评估规则生成完美的护理计划"""
    
    def __init__(self, target_duration: int = 120):
        """
        初始化生成器
        
        Args:
            target_duration: 目标总时长（分钟）
        """
        self.target_duration = target_duration
    
    def generate_perfect_plan(self, assessment: AssessmentInput, date: str = "2024-01-01") -> DailyPlan:
        """
        生成完美的护理计划
        
        Args:
            assessment: 评估输入数据
            date: 日期字符串
            
        Returns:
            DailyPlan: 生成的护理计划
        """
        required_task_ids = set()
        
        # 1. 收集所有必需的任务
        for condition, required_tasks in ASSESSMENT_RULES.items():
            if self._condition_matches(assessment, condition):
                if isinstance(required_tasks, list):
                    # AND关系：添加所有任务
                    required_task_ids.update(required_tasks)
                elif isinstance(required_tasks, set):
                    # OR关系：选择第一个任务（或可以优化选择）
                    required_task_ids.add(list(required_tasks)[0])
        
        # 2. 添加基础任务（如果还没有）
        basic_tasks = [1, 3, 4, 7]  # 头面部清洁、口腔清洁、手部清洁、协助进食/水
        for task_id in basic_tasks:
            if task_id not in required_task_ids:
                required_task_ids.add(task_id)
        
        # 3. 创建任务对象
        tasks = []
        total_duration = 0
        
        for task_id in sorted(required_task_ids):
            task_info = get_task_info(task_id)
            if not task_info:
                continue
            
            # 确定分配给谁
            assigned_to = "Nurse" if task_info["qualification"] == Qualification.NURSE else "Caregiver"
            
            task = CareTask(
                task_id=task_id,
                name=task_info["name"],
                min_duration=task_info["min_duration"],
                qualification=task_info["qualification"],
                content=task_info.get("content"),
                assigned_to=assigned_to
            )
            
            tasks.append(task)
            total_duration += task_info["min_duration"]
        
        # 4. 如果总时长不足，添加一些可选任务来填充
        if total_duration < self.target_duration:
            optional_tasks = [2, 5, 6, 10, 11, 40]  # 可选的基础任务
            for task_id in optional_tasks:
                if task_id in required_task_ids:
                    continue
                
                task_info = get_task_info(task_id)
                if not task_info:
                    continue
                
                if total_duration + task_info["min_duration"] <= self.target_duration + 20:
                    assigned_to = "Nurse" if task_info["qualification"] == Qualification.NURSE else "Caregiver"
                    
                    task = CareTask(
                        task_id=task_id,
                        name=task_info["name"],
                        min_duration=task_info["min_duration"],
                        qualification=task_info["qualification"],
                        content=task_info.get("content"),
                        assigned_to=assigned_to
                    )
                    
                    tasks.append(task)
                    total_duration += task_info["min_duration"]
        
        return DailyPlan(
            date=date,
            tasks=tasks,
            total_duration=total_duration
        )
    
    def _condition_matches(self, assessment: AssessmentInput, condition: str) -> bool:
        """
        检查评估数据是否匹配条件（与evaluator中的逻辑相同）
        """
        if ":" not in condition:
            return False
        
        field_name, expected_value = condition.split(":", 1)
        field_name = field_name.strip()
        expected_value = expected_value.strip()
        
        actual_value = assessment.get_field_value(field_name)
        
        if actual_value is None:
            return False
        
        if isinstance(expected_value, str):
            if expected_value.startswith(">="):
                try:
                    threshold = int(expected_value[2:].strip())
                    return isinstance(actual_value, (int, float)) and actual_value >= threshold
                except ValueError:
                    return False
            elif expected_value.startswith("<"):
                try:
                    threshold = int(expected_value[1:].strip())
                    return isinstance(actual_value, (int, float)) and actual_value < threshold
                except ValueError:
                    return False
            elif expected_value == "是":
                return actual_value is True or str(actual_value) == "是"
            elif expected_value == "否":
                return actual_value is False or str(actual_value) == "否"
            else:
                return str(actual_value) == expected_value or expected_value in str(actual_value)
        
        return False
