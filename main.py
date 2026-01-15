"""
Green Agent Benchmark Main Program (Fixed Version + Standard Answer Analysis)
"""
import json
import argparse
import sys
import time
import webbrowser
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# Try to import pytz for timezone conversion
try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False
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

# Global variable to store output for HTML report
HTML_OUTPUT_DATA = {
    "assessment": None,
    "ground_truth": [],
    "results": [],
    "perfect_plan": None,
    "timestamp": None
}

def show_loading(message: str = "Processing", duration: float = 1.5):
    """
    Show a loading animation with spinner (hacker-style)
    
    Args:
        message: Loading message
        duration: Duration to show loading (seconds)
    """
    spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    dots = ['.', '..', '...']
    start_time = time.time()
    i = 0
    dot_i = 0
    
    # Print initial message
    print(f"\n{message}", end='', flush=True)
    
    while time.time() - start_time < duration:
        # Calculate which frame to show
        frame_time = time.time() - start_time
        spinner_frame = int(frame_time * 10) % len(spinner_chars)
        dot_frame = int(frame_time * 2) % len(dots)
        
        # Print spinner and dots
        display = f'\r{message} {spinner_chars[spinner_frame]}{dots[dot_frame]}'
        print(display, end='', flush=True)
        time.sleep(0.05)
        i += 1
    
    # Clear the loading line completely
    clear_length = len(message) + 10  # Account for spinner and dots
    print('\r' + ' ' * clear_length + '\r', end='', flush=True)

def slow_print(text: str, delay: float = 0.02, end: str = "\n", flush: bool = True):
    """
    Print text with typing effect (hacker-style)
    
    Args:
        text: Text to print
        delay: Delay between characters (seconds)
        end: End character (default newline)
        flush: Whether to flush output immediately
    """
    for char in text:
        print(char, end='', flush=flush)
        time.sleep(delay)
    print(end, end='', flush=flush)

def generate_html_report(output_file: str = "report.html"):
    """
    Generate a beautiful HTML report with all evaluation data
    
    Args:
        output_file: Output HTML file path
    """
    # Convert timestamp to Pacific Time
    if HAS_PYTZ:
        pacific_tz = pytz.timezone('America/Los_Angeles')
        if HTML_OUTPUT_DATA.get('timestamp'):
            try:
                # Parse the timestamp string
                dt = datetime.strptime(HTML_OUTPUT_DATA['timestamp'], '%Y-%m-%d %H:%M:%S')
                # Assume it's in UTC and convert to Pacific
                if dt.tzinfo is None:
                    dt = pytz.utc.localize(dt)
                pacific_dt = dt.astimezone(pacific_tz)
                formatted_timestamp = pacific_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
            except:
                # Fallback to original timestamp if conversion fails
                formatted_timestamp = HTML_OUTPUT_DATA.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        else:
            pacific_dt = datetime.now(pacific_tz)
            formatted_timestamp = pacific_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
    else:
        # Fallback if pytz is not available
        if HTML_OUTPUT_DATA.get('timestamp'):
            formatted_timestamp = HTML_OUTPUT_DATA['timestamp'] + ' (PST)'
        else:
            formatted_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' (PST)'
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Green Agent Benchmark Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            color: #00ff00;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(0, 0, 0, 0.8);
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 0 30px rgba(0, 255, 0, 0.3);
        }}
        
        h1 {{
            color: #00ff00;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 0 10px #00ff00;
            animation: glow 2s ease-in-out infinite alternate;
        }}
        
        @keyframes glow {{
            from {{ text-shadow: 0 0 10px #00ff00; }}
            to {{ text-shadow: 0 0 20px #00ff00, 0 0 30px #00ff00; }}
        }}
        
        .timestamp {{
            text-align: center;
            color: #888;
            margin-bottom: 30px;
            font-size: 0.9em;
        }}
        
        .section {{
            margin: 30px 0;
            padding: 20px;
            background: rgba(0, 255, 0, 0.05);
            border-left: 4px solid #00ff00;
            border-radius: 5px;
        }}
        
        .section h2 {{
            color: #00ff00;
            margin-bottom: 15px;
            font-size: 1.8em;
        }}
        
        .assessment-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .info-item {{
            padding: 10px;
            background: rgba(0, 255, 0, 0.1);
            border-radius: 5px;
        }}
        
        .info-item strong {{
            color: #00ff00;
        }}
        
        .rule-item {{
            margin: 10px 0;
            padding: 10px;
            background: rgba(0, 255, 0, 0.05);
            border-radius: 5px;
            border-left: 3px solid #00ff00;
        }}
        
        .rule-item .condition {{
            color: #ffff00;
            font-weight: bold;
        }}
        
        .rule-item .tasks {{
            color: #00ffff;
            margin-top: 5px;
        }}
        
        .result-card {{
            margin: 20px 0;
            padding: 20px;
            background: rgba(0, 255, 0, 0.05);
            border: 2px solid #00ff00;
            border-radius: 10px;
        }}
        
        .score {{
            font-size: 2em;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }}
        
        .score.passed {{
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
        }}
        
        .score.failed {{
            color: #ff0000;
            text-shadow: 0 0 10px #ff0000;
        }}
        
        .breakdown {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .breakdown-item {{
            padding: 15px;
            background: rgba(0, 255, 0, 0.1);
            border-radius: 5px;
            text-align: center;
        }}
        
        .breakdown-item .label {{
            color: #888;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        
        .breakdown-item .value {{
            color: #00ff00;
            font-size: 1.5em;
            font-weight: bold;
        }}
        
        .issues {{
            margin-top: 20px;
        }}
        
        .issue {{
            padding: 10px;
            margin: 5px 0;
            background: rgba(255, 0, 0, 0.1);
            border-left: 3px solid #ff0000;
            border-radius: 5px;
        }}
        
        .warning {{
            padding: 10px;
            margin: 5px 0;
            background: rgba(255, 255, 0, 0.1);
            border-left: 3px solid #ffff00;
            border-radius: 5px;
            color: #ffff00;
        }}
        
        .error {{
            padding: 10px;
            margin: 5px 0;
            background: rgba(255, 0, 0, 0.1);
            border-left: 3px solid #ff0000;
            border-radius: 5px;
            color: #ff0000;
        }}
        
        .care-plan {{
            margin: 30px 0;
            padding: 20px;
            background: rgba(0, 255, 0, 0.05);
            border: 2px solid #00ff00;
            border-radius: 10px;
        }}
        
        .care-plan-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 0.9em;
        }}
        
        .care-plan-table th {{
            background: rgba(0, 255, 0, 0.2);
            color: #00ff00;
            padding: 12px;
            text-align: left;
            border: 1px solid #00ff00;
        }}
        
        .care-plan-table td {{
            padding: 10px;
            border: 1px solid rgba(0, 255, 0, 0.3);
            color: #00ffff;
        }}
        
        .care-plan-table tr:nth-child(even) {{
            background: rgba(0, 255, 0, 0.02);
        }}
        
        .care-plan-table tr:hover {{
            background: rgba(0, 255, 0, 0.1);
        }}
        
        .download-btn {{
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(135deg, #00ff00 0%, #00cc00 100%);
            color: #000;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin: 20px 0;
            transition: all 0.3s ease;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
        }}
        
        .download-btn:hover {{
            background: linear-gradient(135deg, #00cc00 0%, #00ff00 100%);
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
            transform: translateY(-2px);
        }}
        
        .total-duration {{
            text-align: right;
            font-size: 1.2em;
            font-weight: bold;
            color: #00ff00;
            margin-top: 15px;
            padding: 10px;
            background: rgba(0, 255, 0, 0.1);
            border-radius: 5px;
        }}
        
        .typing-effect {{
            border-right: 2px solid #00ff00;
            animation: blink 1s infinite;
        }}
        
        @keyframes blink {{
            0%, 50% {{ border-color: #00ff00; }}
            51%, 100% {{ border-color: transparent; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ GREEN AGENT BENCHMARK REPORT</h1>
        <div class="timestamp">Generated: {formatted_timestamp}</div>
"""
    
    # Add assessment section
    if HTML_OUTPUT_DATA.get('assessment'):
        assessment = HTML_OUTPUT_DATA['assessment']
        html_content += f"""
        <div class="section">
            <h2>📋 Assessment Information</h2>
            <div class="assessment-info">
                <div class="info-item">
                    <strong>Assessment ID:</strong> {assessment.assessment_id}
                </div>
"""
        if assessment.patient_info:
            html_content += f"""
                <div class="info-item">
                    <strong>Patient:</strong> {assessment.patient_info.get('name', 'N/A')}
                </div>
                <div class="info-item">
                    <strong>Age:</strong> {assessment.patient_info.get('age', 'N/A')}
                </div>
                <div class="info-item">
                    <strong>Gender:</strong> {assessment.patient_info.get('gender', 'N/A')}
                </div>
"""
        html_content += """
            </div>
        </div>
"""
    
    # Add ground truth section
    if HTML_OUTPUT_DATA.get('ground_truth'):
        html_content += """
        <div class="section">
            <h2>🔍 Ground Truth Analysis</h2>
"""
        for rule in HTML_OUTPUT_DATA['ground_truth']:
            html_content += f"""
            <div class="rule-item">
                <div class="condition">• {rule['condition']}</div>
                <div class="tasks">→ Required Tasks: {', '.join(rule['tasks'])}</div>
            </div>
"""
        html_content += """
        </div>
"""
    
    # Add perfect care plan section
    if HTML_OUTPUT_DATA.get('perfect_plan'):
        plan = HTML_OUTPUT_DATA['perfect_plan']
        html_content += """
        <div class="section">
            <h2>✅ 100% Correct Care Plan</h2>
            <div class="care-plan">
                <p style="color: #00ff00; margin-bottom: 15px;">This is the perfect care plan generated based on assessment data and database rules.</p>
                <a href="#" class="download-btn" onclick="downloadCarePlanCSV()">📥 Download Care Plan CSV</a>
                <table class="care-plan-table">
                    <thead>
                        <tr>
                            <th>Task ID</th>
                            <th>Service Name</th>
                            <th>Duration (minutes)</th>
                            <th>Qualification</th>
                            <th>Assigned To</th>
                            <th>Content</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        total_duration = 0
        for task in plan.tasks:
            total_duration += task.min_duration
            html_content += f"""
                        <tr>
                            <td>{task.task_id}</td>
                            <td>{task.name}</td>
                            <td>{task.min_duration}</td>
                            <td>{task.qualification.value}</td>
                            <td>{task.assigned_to or 'N/A'}</td>
                            <td>{task.content or 'N/A'}</td>
                        </tr>
"""
        html_content += f"""
                    </tbody>
                </table>
                <div class="total-duration">
                    Total Duration: {total_duration} minutes ({total_duration // 60}h {total_duration % 60}m)
                </div>
            </div>
        </div>
"""
    
    # Add results section
    if HTML_OUTPUT_DATA.get('results'):
        html_content += """
        <div class="section">
            <h2>📊 Evaluation Results</h2>
"""
        for i, result_data in enumerate(HTML_OUTPUT_DATA['results']):
            result = result_data['result']
            title = result_data.get('title', f'Result {i+1}')
            passed_class = 'passed' if result.passed else 'failed'
            passed_text = 'PASSED' if result.passed else 'FAILED'
            
            html_content += f"""
            <div class="result-card">
                <h3>{title}</h3>
                <div class="score {passed_class}">{result.overall_score:.3f} - {passed_text}</div>
                <div class="breakdown">
                    <div class="breakdown-item">
                        <div class="label">Coverage</div>
                        <div class="value">{result.breakdown.mandatory_coverage:.0%}</div>
                    </div>
                    <div class="breakdown-item">
                        <div class="label">Safety</div>
                        <div class="value">{result.breakdown.safety_score:.3f}</div>
                    </div>
                    <div class="breakdown-item">
                        <div class="label">Qualification</div>
                        <div class="value">{result.breakdown.qualification_score:.3f}</div>
                    </div>
                    <div class="breakdown-item">
                        <div class="label">Duration</div>
                        <div class="value">{result.breakdown.duration_score:.3f}</div>
                    </div>
                </div>
"""
            if result.breakdown.mandatory_missing:
                html_content += f"""
                <div class="issues">
                    <div class="issue">⚠️ Missing Mandatory Tasks: {result.breakdown.mandatory_missing}</div>
                </div>
"""
            if result.breakdown.safety_violations:
                html_content += f"""
                <div class="issues">
                    <div class="error">❌ Safety Violations: {result.breakdown.safety_violations}</div>
                </div>
"""
            if result.breakdown.qualification_issues:
                html_content += """
                <div class="issues">
"""
                for issue in result.breakdown.qualification_issues:
                    html_content += f"""
                    <div class="error">❌ Task {issue['task_id']} requires {issue['required']}, but assigned to {issue['assigned']}</div>
"""
                html_content += """
                </div>
"""
            if result.warnings:
                html_content += """
                <div class="issues">
"""
                for warning in result.warnings:
                    html_content += f"""
                    <div class="warning">⚠️ {warning}</div>
"""
                html_content += """
                </div>
"""
            if result.errors:
                html_content += """
                <div class="issues">
"""
                for error in result.errors:
                    html_content += f"""
                    <div class="error">❌ {error}</div>
"""
                html_content += """
                </div>
"""
            html_content += """
            </div>
"""
        html_content += """
        </div>
"""
    
    html_content += """
    </div>
    <script>
        // Care plan data for CSV download
        const carePlanData = """
    
    # Add care plan data as JSON
    if HTML_OUTPUT_DATA.get('perfect_plan'):
        plan = HTML_OUTPUT_DATA['perfect_plan']
        plan_data = {
            'date': plan.date,
            'total_duration': plan.total_duration,
            'tasks': [
                {
                    'task_id': task.task_id,
                    'name': task.name,
                    'duration': task.min_duration,
                    'qualification': task.qualification.value,
                    'assigned_to': task.assigned_to or 'N/A',
                    'content': task.content or 'N/A'
                }
                for task in plan.tasks
            ]
        }
        import json
        html_content += json.dumps(plan_data, ensure_ascii=False, indent=8)
    else:
        html_content += "null"
    
    html_content += """;
        
        // CSV download function
        function downloadCarePlanCSV() {
            if (!carePlanData || !carePlanData.tasks) {
                alert('No care plan data available');
                return;
            }
            
            // Create CSV header
            const headers = ['Task ID', 'Service Name', 'Duration (minutes)', 'Qualification', 'Assigned To', 'Content'];
            const csvRows = [headers.join(',')];
            
            // Add task rows
            carePlanData.tasks.forEach(task => {
                const row = [
                    task.task_id,
                    '"' + task.name.replace(/"/g, '""') + '"',
                    task.duration,
                    task.qualification,
                    task.assigned_to,
                    '"' + (task.content || '').replace(/"/g, '""') + '"'
                ];
                csvRows.push(row.join(','));
            });
            
            // Add total duration row
            csvRows.push('');
            csvRows.push(`Total Duration,${carePlanData.total_duration} minutes,${Math.floor(carePlanData.total_duration / 60)}h ${carePlanData.total_duration % 60}m`);
            
            // Create CSV content
            const csvContent = csvRows.join('\\n');
            
            // Create blob and download
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            
            link.setAttribute('href', url);
            link.setAttribute('download', `care_plan_${carePlanData.date || 'report'}.csv`);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        
        // Add typing effect animation
        document.addEventListener('DOMContentLoaded', function() {
            const elements = document.querySelectorAll('.rule-item, .result-card, .care-plan');
            elements.forEach((el, index) => {
                setTimeout(() => {
                    el.style.opacity = '0';
                    el.style.transform = 'translateY(20px)';
                    el.style.transition = 'all 0.5s ease';
                    setTimeout(() => {
                        el.style.opacity = '1';
                        el.style.transform = 'translateY(0)';
                    }, 100);
                }, index * 100);
            });
        });
    </script>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_file

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
    # Show loading animation
    show_loading("🔍 Analyzing assessment data", 2.0)
    
    slow_print("\n" + "="*60)
    slow_print("🔍 Step 3: Ground Truth Analysis")
    slow_print("="*60)
    slow_print("Based on the assessment data, the following mandatory tasks are required:")
    
    triggered_rules = []
    html_rules = []
    
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
            task_ids_str = []
            for tid in required_ids:
                info = get_task_info(tid)
                task_names.append(f"[{tid}] {info.get('name', 'Unknown')}")
                task_ids_str.append(f"[{tid}] {info.get('name', 'Unknown')}")
            
            condition_text = f"  • Detected '{key}: {value}'"
            slow_print(condition_text)
            task_text = f"    -> Triggered rule, required tasks: {', '.join(task_names)}"
            slow_print(task_text)
            triggered_rules.append((key, value, required_ids))
            html_rules.append({
                'condition': f"{key}: {value}",
                'tasks': task_ids_str
            })

    if not triggered_rules:
        slow_print("  (No rules triggered from assessment data)")
    
    slow_print("="*60 + "\n")
    
    # Store for HTML report
    HTML_OUTPUT_DATA['ground_truth'] = html_rules
    HTML_OUTPUT_DATA['assessment'] = assessment

def print_result(result: ScoreResult, title="Step 4: Evaluation Result"):
    # Show loading animation
    show_loading("📊 Calculating evaluation results", 2.0)
    
    slow_print("\n" + "="*60)
    slow_print(title)
    slow_print("="*60)
    score_text = f"Overall Score: {result.overall_score:.3f} ({'PASSED' if result.passed else 'FAILED'})"
    slow_print(score_text)
    breakdown_text = (f"Breakdown: Coverage {result.breakdown.mandatory_coverage:.0%} | "
                      f"Safety {result.breakdown.safety_score:.3f} | "
                      f"Qualification {result.breakdown.qualification_score:.3f} | "
                      f"Duration {result.breakdown.duration_score:.3f}")
    slow_print(breakdown_text)
    
    if result.breakdown.mandatory_missing:
        slow_print(f"\n[!] Missing Mandatory Tasks: {result.breakdown.mandatory_missing}")
    if result.breakdown.safety_violations:
        slow_print(f"\n[!] Safety Violations: {result.breakdown.safety_violations}")
    if result.breakdown.qualification_issues:
        slow_print(f"\n[!] Qualification Issues:")
        for issue in result.breakdown.qualification_issues:
            slow_print(f"    Task {issue['task_id']} requires {issue['required']}, but assigned to {issue['assigned']}")
    if result.warnings:
        slow_print(f"\n[⚠] Warnings:")
        for warning in result.warnings:
            slow_print(f"    {warning}")
    if result.errors:
        slow_print(f"\n[❌] Errors:")
        for error in result.errors:
            slow_print(f"    {error}")
    slow_print("="*60 + "\n")
    
    # Store for HTML report
    HTML_OUTPUT_DATA['results'].append({
        'result': result,
        'title': title
    })

def main():
    # Initialize HTML output data
    global HTML_OUTPUT_DATA
    HTML_OUTPUT_DATA = {
        "assessment": None,
        "ground_truth": [],
        "results": [],
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    parser = argparse.ArgumentParser(description="Green Agent Benchmark - Main Program")
    parser.add_argument("--mode", choices=["demo", "evaluate", "generate"], default="demo",
                       help="Operation mode: demo, evaluate, or generate")
    parser.add_argument("--assessment", type=str, help="Path to assessment JSON file")
    parser.add_argument("--plan", type=str, help="Path to plan JSON file")
    parser.add_argument("--output", type=str, help="Path to output JSON file")
    parser.add_argument("--no-html", action="store_true", help="Don't generate HTML report")
    args = parser.parse_args()
    
    try:
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
            return  # Don't generate HTML for generate mode
        
        # Generate perfect care plan for HTML report
        if not args.no_html and args.mode != "generate":
            # Generate perfect plan based on assessment
            if HTML_OUTPUT_DATA.get('assessment'):
                assessment = HTML_OUTPUT_DATA['assessment']
                generator = BaselineGenerator(target_duration=120)
                perfect_plan = generator.generate_perfect_plan(assessment)
                HTML_OUTPUT_DATA['perfect_plan'] = perfect_plan
        
        # Generate HTML report and open browser
        if not args.no_html and args.mode != "generate":
            slow_print("\n" + "="*60)
            slow_print("🌐 Generating HTML Report...")
            slow_print("="*60)
            
            html_file = generate_html_report("green_agent_report.html")
            html_path = os.path.abspath(html_file)
            
            slow_print(f"\n✅ HTML Report Generated: {html_path}")
            slow_print("🚀 Opening browser...\n")
            
            # Open browser
            try:
                webbrowser.open(f'file://{html_path}')
                slow_print("✨ Report opened in browser!")
            except Exception as e:
                slow_print(f"⚠️  Could not open browser automatically: {e}")
                slow_print(f"   Please open manually: {html_path}")
    
    except KeyboardInterrupt:
        slow_print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        slow_print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
