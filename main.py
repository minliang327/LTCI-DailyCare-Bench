"""
Green Agent Benchmark 主程序 (修复版 + 标准答案解析)
"""
import json
import argparse
from typing import Dict, Any, List
from models import AssessmentInput, DailyPlan, ScoreResult
from evaluator import GreenAgentEvaluator
from generator import BaselineGenerator
from database import get_required_tasks, get_task_info, ASSESSMENT_RULES

# 尝试导入坏生成器
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
        patient_info={"name": "张先生", "age": 75, "gender": "男"},
        assessment_data={
            "饮食习惯": "低糖或无糖",
            "衣着整洁": 3,
            "过敏情况": "食物过敏",
            "跌倒风险": True,
            "行动能力": "部分不能",
            "如厕能力": "部分不能",
            "洗浴能力": "完全不能",
            "留置尿管": "否",
            "需要监测血糖": True
        },
        eating_habits="低糖或无糖",
        clothing_neatness=3,
        allergy_info="食物过敏",
        fall_risk=True
    )

def print_ground_truth(assessment: AssessmentInput):
    """【新功能】打印标准答案解析：显示评估单触发了哪些规则"""
    print("\n" + "="*60)
    print("🔍 标准答案解析 (Ground Truth Analysis)")
    print("="*60)
    print("根据评估单数据，Green Agent 推导出的【必须执行任务】如下：")
    
    # 1. 遍历评估单中的所有键值对
    # 注意：这里我们简化处理，直接用 assessment_data 来匹配 database 里的规则
    triggered_rules = []
    
    # 检查 assessment_data 里的每一项
    for key, value in assessment.assessment_data.items():
        # 构造可能的查询条件，例如 "跌倒风险" 或 "饮食习惯: 低糖"
        # 简单逻辑：检查 key 是否在规则库，或者 "key: value" 是否在规则库
        
        # 尝试匹配 "Key: Value" 格式 (例如 "饮食习惯: 低糖或无糖")
        condition_str = f"{key}: {value}"
        required_ids = get_required_tasks(condition_str)
        
        # 如果没匹配到，尝试匹配 Key (例如 "跌倒风险" 为 True 时)
        if not required_ids and value is True:
            required_ids = get_required_tasks(key)
            
        if required_ids:
            task_names = []
            for tid in required_ids:
                info = get_task_info(tid)
                task_names.append(f"[{tid}]{info.get('name', '未知')}")
            
            print(f"  • 检测到 '{key}: {value}'")
            print(f"    -> 触发规则，要求任务: {', '.join(task_names)}")

    print("="*60 + "\n")

def print_result(result: ScoreResult, title="评估结果"):
    print("\n" + "-"*60)
    print(title)
    print("-"*60)
    print(f"总分: {result.overall_score:.3f} ({'通过' if result.passed else '未通过'})")
    print(f"明细: 覆盖率 {result.breakdown.mandatory_coverage:.0%} | 安全 {result.breakdown.safety_score} | 资质 {result.breakdown.qualification_score}")
    
    if result.breakdown.mandatory_missing:
        print(f"\n[!] 缺失任务: {result.breakdown.mandatory_missing}")
    if result.breakdown.safety_violations:
        print(f"\n[!] 安全违规: {result.breakdown.safety_violations}")
    if result.breakdown.qualification_issues:
        print(f"\n[!] 资质违规:")
        for issue in result.breakdown.qualification_issues:
            print(f"    任务{issue['task_id']} 需要 {issue['required']}, 实际 {issue['assigned']}")
    print("-"*60 + "\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["demo", "evaluate", "generate"], default="demo")
    parser.add_argument("--assessment", type=str)
    parser.add_argument("--plan", type=str)
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    
    if args.mode == "demo":
        print("Green Agent Benchmark - 演示模式\n")
        assessment = create_sample_assessment()
        
        # 【新增】打印标准答案解析，满足你的需求
        print_ground_truth(assessment)
        
        # 1. Good Agent
        print("🤖 测试 1: 基准生成器 (Good Agent)...")
        generator = BaselineGenerator(target_duration=120)
        plan = generator.generate_perfect_plan(assessment)
        evaluator = GreenAgentEvaluator()
        result = evaluator.evaluate(assessment, plan)
        print_result(result, title="✅ Good Agent 结果")

        # 2. Bad Agent
        if HAS_BAD_GENERATOR:
            print("🤖 测试 2: 对抗性测试 (Bad Agent)...")
            bad_plan = generate_bad_plan(assessment)
            bad_score = evaluator.evaluate(assessment, bad_plan)
            print_result(bad_score, title="❌ Bad Agent 结果 (成功拦截)")
    
    elif args.mode == "evaluate":
        assessment = load_assessment_from_json(args.assessment)
        plan = load_plan_from_json(args.plan)
        # 评估模式也打印解析
        print_ground_truth(assessment)
        evaluator = GreenAgentEvaluator()
        result = evaluator.evaluate(assessment, plan)
        print_result(result)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)

    elif args.mode == "generate":
        assessment = load_assessment_from_json(args.assessment)
        generator = BaselineGenerator(target_duration=120)
        plan = generator.generate_perfect_plan(assessment)
        print(json.dumps(plan.model_dump(), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()