# Green Agent Benchmark

用于评估医疗保健代理生成老年人日常护理计划的基准测试系统。

## 项目概述

本项目是一个Python基准测试框架，用于评估基于长期护理保险（LTCI）评估生成日常护理计划的医疗保健代理。系统通过以下维度评估护理计划的质量：

- **强制性任务覆盖率** (50%): 检查代理是否包含了评估规则要求的必需任务
- **安全约束** (20%): 检查代理是否避免了禁忌任务
- **时长合理性** (30%): 检查总服务时长是否在合理范围内（100-140分钟）
- **资质匹配**: 检查任务是否分配给了具备相应资质的护理人员

## 项目结构

```
green_agent_benchmark/
├── models.py          # Pydantic数据模型
├── database.py        # 硬编码的任务列表和评估规则
├── evaluator.py       # 核心评估逻辑
├── generator.py       # 基线代理生成器
├── main.py            # CLI主程序
├── requirements.txt   # Python依赖
├── Dockerfile         # Docker部署文件
└── README.md          # 项目文档
```

## 安装

### 使用pip安装依赖

```bash
pip install -r requirements.txt
```

### 使用Docker

```bash
docker build -t green-agent-benchmark .
docker run green-agent-benchmark
```

## 使用方法

### 1. 演示模式（默认）

运行示例评估和计划生成：

```bash
python main.py --mode demo
```

### 2. 评估模式

评估一个护理计划：

```bash
python main.py --mode evaluate \
    --assessment assessment.json \
    --plan plan.json \
    --output result.json
```

### 3. 生成模式

基于评估数据生成基线护理计划：

```bash
python main.py --mode generate \
    --assessment assessment.json \
    --output plan.json
```

## 数据格式

### 评估输入 (AssessmentInput)

```json
{
  "assessment_id": "ASSESS_001",
  "patient_info": {
    "name": "张先生",
    "age": 75
  },
  "assessment_data": {
    "饮食习惯": "低糖或无糖",
    "衣着整洁": 3,
    "B卷-跌倒风险": true,
    "需要监测血糖": true
  }
}
```

### 护理计划 (DailyPlan)

```json
{
  "date": "2024-01-01",
  "tasks": [
    {
      "task_id": 7,
      "name": "协助进食/水",
      "min_duration": 15,
      "qualification": "Any",
      "assigned_to": "Caregiver"
    }
  ],
  "total_duration": 120
}
```

### 评估结果 (ScoreResult)

```json
{
  "overall_score": 0.85,
  "passed": true,
  "breakdown": {
    "mandatory_score": 0.9,
    "mandatory_coverage": 0.9,
    "mandatory_missing": [],
    "safety_score": 1.0,
    "safety_violations": [],
    "duration_score": 0.8,
    "duration_minutes": 115,
    "qualification_score": 1.0,
    "qualification_issues": []
  },
  "warnings": [],
  "errors": []
}
```

## 评估规则

系统包含42个护理任务和多个评估规则映射。主要规则包括：

- **饮食习惯**: 低糖/无糖 → 需要任务7（协助进食/水）和任务36（饮食指导）
- **跌倒风险**: 需要任务23（安全防护）和任务21（协助行走）
- **行动能力**: 完全不能 → 需要任务11（协助翻身）、13（协助床上移动）、19（协助上下床）
- **如厕能力**: 完全不能 → 需要任务14（人工取便）和任务16（协助使用便器）

完整规则列表请参考 `database.py` 中的 `ASSESSMENT_RULES`。

## 评分标准

- **总分计算**: 
  ```
  总分 = 强制性任务得分 × 0.5 + 时长得分 × 0.3 + 安全约束得分 × 0.2
  ```
  如果有资质问题，会额外扣分（最多20%）

- **通过标准**: 
  - 总分 >= 0.8
  - 无安全约束违规
  - 无资质不匹配问题

## 开发说明

### 添加新任务

在 `database.py` 的 `SERVICE_TASKS` 字典中添加新任务：

```python
43: {
    "name": "新任务名称",
    "min_duration": 10,
    "qualification": Qualification.ANY,
    "content": "任务描述"
}
```

### 添加新规则

在 `database.py` 的 `ASSESSMENT_RULES` 字典中添加新规则：

```python
"新条件: 值": [7, 36]  # 需要任务7和36（AND关系）
# 或
"新条件: 值": {9, 15}  # 需要任务9或15（OR关系）
```

### 自定义评估器权重

```python
evaluator = GreenAgentEvaluator(
    mandatory_weight=0.5,
    duration_weight=0.3,
    safety_weight=0.2
)
`````

## 许可证

MIT License
