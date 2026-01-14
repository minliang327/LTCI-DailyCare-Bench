"""
反派生成器：故意生成包含医疗错误的计划
"""
from models import DailyPlan, CareTask, Qualification

def generate_bad_plan(assessment) -> DailyPlan:
    """生成一个充满错误的护理计划"""
    
    # 错误1：严重违规 - 强行安排"一次性导尿" (ID 35)
    # 这里的关键是：任务本身需要 NURSE，但我故意填了 ANY (代表普通护理员)
    bad_task_1 = CareTask(
        task_id=35,
        name="一次性导尿 (违规操作)",
        min_duration=20,           
        qualification=Qualification.NURSE, # 任务本身要求的资质
        assigned_to=Qualification.ANY,     # <--- 修正：用 ANY 代表普通护理员
        start_time="09:00",
        duration=20
    )
    
    # 错误2：无视风险 - 跌倒风险老人安排"独自步行" (ID 21)
    bad_task_2 = CareTask(
        task_id=21,
        name="步行训练 (高风险)",
        min_duration=20,
        qualification=Qualification.ANY,
        assigned_to=Qualification.ANY,     # <--- 修正：用 ANY
        start_time="10:00",
        duration=30
    )

    return DailyPlan(
        date="2024-01-01",
        tasks=[bad_task_1, bad_task_2],
        total_duration=50 # 故意写短，触发时长扣分
    )