# Green Agent Benchmark
[![Docker Image](https://img.shields.io/docker/pulls/liangmin0327/ltci-dailycare-bench.svg)](https://hub.docker.com/r/liangmin0327/ltci-dailycare-bench)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A benchmark system for evaluating healthcare agents that generate daily care plans for elderly individuals.

## Project Overview

This project is a Python benchmark framework for assessing healthcare agents that generate daily care plans based on Long-Term Care Insurance (LTCI) assessments. The system evaluates the quality of care plans across the following dimensions:

- **Mandatory Task Coverage** (50%): Checks whether the agent includes all required tasks according to the assessment rules.
- **Safety Constraints** (20%): Checks whether the agent avoids prohibited tasks.
- **Duration Reasonableness** (30%): Checks if the total service duration is within a reasonable range (100–140 minutes).
- **Qualification Matching**: Checks whether tasks are assigned to caregivers with the appropriate qualifications.

## Project Structure

```
green_agent_benchmark/
├── models.py          # Pydantic data models
├── database.py        # Hardcoded task list and assessment rules
├── evaluator.py       # Core evaluation logic
├── generator.py       # Baseline agent generator
├── main.py            # CLI main program
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker deployment file
└── README.md          # Project documentation
```

## Installation

### Install dependencies with pip

```bash
pip install -r requirements.txt
```

### Using Docker

```bash
docker build -t green-agent-benchmark .
docker run green-agent-benchmark
```

## Usage

### 1. Demo Mode (default)

Run a demonstration evaluation and plan generation:

```bash
python main.py --mode demo
```

### 2. Evaluation Mode

Evaluate a care plan:

```bash
python main.py --mode evaluate \
    --assessment assessment.json \
    --plan plan.json \
    --output result.json
```

### 3. Generation Mode

Generate a baseline care plan based on assessment data:

```bash
python main.py --mode generate \
    --assessment assessment.json \
    --output plan.json
```

## Data Formats

### Assessment Input (AssessmentInput)

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

### Daily Care Plan (DailyPlan)

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

### Evaluation Result (ScoreResult)

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

## Evaluation Rules

The system includes 42 care tasks and multiple assessment rule mappings. Major rules include:

- **Dietary Habit**:  Low-sugar/sugar-free → requires tasks 7 (Assistance with eating/drinking) and 36 (Diet guidance)
- **Fall Risk**: Requires tasks 23 (Safety protection) and 21 (Assistance with walking)
- **Mobility**: Completely unable → requires tasks 11 (Assistance with turning), 13 (Assistance in-bed movement), 19 (Assistance with bed transfer)
- **Toileting Ability**: Completely unable → requires tasks 14 (Manual toileting) and 16 (Assistance with commode)

For the full rule list, see ASSESSMENT_RULES in database.py.

## Scoring Criteria

- **Total Score Calculation**: 
  ```
  Total Score = Mandatory Task Score × 0.5 + Duration Score × 0.3 + Safety Constraint Score × 0.2
  ```
  Qualification issues will incur additional deductions (up to 20%).

- **Passing Criteria**: 
  - Total score >= 0.8
  - No safety violations
  - No qualification mismatches


## Development Notes

### Adding New Tasks

Add new tasks to the SERVICE_TASKS dictionary in database.py:

```python
43: {
    "name": "新任务名称",
    "min_duration": 10,
    "qualification": Qualification.ANY,
    "content": "任务描述"
}
```

### Adding New Rules

Add new rules to the ASSESSMENT_RULES dictionary in database.py:

```python
"新条件: 值": [7, 36]  # 需要任务7和36（AND关系）
# 或
"新条件: 值": {9, 15}  # 需要任务9或15（OR关系）
```

### Customizing Evaluator Weights

```python
evaluator = GreenAgentEvaluator(
    mandatory_weight=0.5,
    duration_weight=0.3,
    safety_weight=0.2
)
```
