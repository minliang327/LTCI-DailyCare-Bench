"""
硬编码的数据库：基于长护险 42 项服务标准 (清洗版)
"""
from typing import Dict, List, Set, Union
from models import Qualification

# ==================== 数据A: 服务任务列表 (42个任务) ====================
SERVICE_TASKS: Dict[int, Dict[str, Union[str, int, Qualification]]] = {
    1: {"name": "头面部清洁、梳理", "min_duration": 10, "qualification": Qualification.ANY, "content": "清洁面部、梳头、剃须"},
    2: {"name": "洗发", "min_duration": 20, "qualification": Qualification.ANY, "content": "舒适体位下清洗头发"},
    3: {"name": "指/趾甲护理", "min_duration": 10, "qualification": Qualification.ANY, "content": "修剪指/趾甲，处理灰指甲"},
    4: {"name": "手、足部清洁", "min_duration": 15, "qualification": Qualification.ANY, "content": "清洗手足部"},
    5: {"name": "温水擦浴", "min_duration": 30, "qualification": Qualification.ANY, "content": "全身温水擦浴"},
    6: {"name": "床上洗头", "min_duration": 25, "qualification": Qualification.ANY, "content": "为卧床者洗头"},
    7: {"name": "协助进食/水", "min_duration": 15, "qualification": Qualification.ANY, "content": "协助进食饮水"},
    8: {"name": "口腔护理", "min_duration": 15, "qualification": Qualification.ANY, "content": "刷牙、漱口、清洁口腔"},
    9: {"name": "穿脱衣服", "min_duration": 15, "qualification": Qualification.ANY, "content": "协助穿脱衣物"},
    10: {"name": "整理床单位", "min_duration": 20, "qualification": Qualification.ANY, "content": "更换床单被套"},
    11: {"name": "大小便护理", "min_duration": 20, "qualification": Qualification.ANY, "content": "协助排泄、使用便盆"},
    12: {"name": "失禁护理", "min_duration": 20, "qualification": Qualification.ANY, "content": "失禁后皮肤清洁护理"},
    13: {"name": "便秘护理", "min_duration": 20, "qualification": Qualification.ANY, "content": "非侵入性措施缓解便秘"},
    14: {"name": "人工取便", "min_duration": 15, "qualification": Qualification.NURSE, "content": "⚠️ 手法取便 (仅护士)"},
    15: {"name": "日常个人清洁协助", "min_duration": 15, "qualification": Qualification.ANY, "content": "洗脸洗手等日常修饰"},
    16: {"name": "睡眠与环境照护", "min_duration": 15, "qualification": Qualification.ANY, "content": "安置体位，调整环境"},
    17: {"name": "床单/褥垫更换", "min_duration": 15, "qualification": Qualification.ANY, "content": "更换污损床单褥垫"},
    18: {"name": "药物管理", "min_duration": 15, "qualification": Qualification.ANY, "content": "指导或代为管理药品"},
    19: {"name": "翻身与叩背", "min_duration": 20, "qualification": Qualification.ANY, "content": "翻身、叩背排痰"},
    20: {"name": "坐起与移动协助", "min_duration": 20, "qualification": Qualification.ANY, "content": "协助卧床者坐起或移动"},
    21: {"name": "步行与上下楼", "min_duration": 20, "qualification": Qualification.ANY, "content": "协助平地步行或上下楼"},
    22: {"name": "皮肤用药", "min_duration": 15, "qualification": Qualification.ANY, "content": "涂抹或贴敷外用药"},
    23: {"name": "认知功能支持与陪伴", "min_duration": 20, "qualification": Qualification.ANY, "content": "交流、认知训练"},
    24: {"name": "功能锻炼", "min_duration": 30, "qualification": Qualification.ANY, "content": "肢体功能训练"},
    25: {"name": "压疮预防护理", "min_duration": 20, "qualification": Qualification.ANY, "content": "翻身、检查高危部位"},
    26: {"name": "留置尿管护理", "min_duration": 15, "qualification": Qualification.NURSE, "content": "⚠️ 尿管尿袋管理 (仅护士)"},
    27: {"name": "造瘘口护理", "min_duration": 20, "qualification": Qualification.NURSE, "content": "⚠️ 肠道/泌尿造瘘护理 (仅护士)"},
    28: {"name": "排便辅助", "min_duration": 15, "qualification": Qualification.NURSE, "content": "⚠️ 开塞露/灌肠/直肠给药 (仅护士)"},
    29: {"name": "胃管护理", "min_duration": 20, "qualification": Qualification.NURSE, "content": "⚠️ 鼻饲/胃管护理 (仅护士)"},
    30: {"name": "药物监督与提醒", "min_duration": 10, "qualification": Qualification.ANY, "content": "提醒和监督服药"},
    31: {"name": "物理降温", "min_duration": 15, "qualification": Qualification.ANY, "content": "温水/酒精擦浴降温"},
    32: {"name": "生命体征监测", "min_duration": 15, "qualification": Qualification.ANY, "content": "测温、脉搏、呼吸、血压"},
    33: {"name": "氧气吸入", "min_duration": 20, "qualification": Qualification.NURSE, "content": "⚠️ 鼻导管吸氧 (仅护士)"},
    34: {"name": "灌肠", "min_duration": 20, "qualification": Qualification.NURSE, "content": "⚠️ 实施灌肠 (仅护士)"},
    35: {"name": "一次性导尿", "min_duration": 20, "qualification": Qualification.NURSE, "content": "⚠️ 临时导尿 (仅护士)"},
    36: {"name": "血糖监测", "min_duration": 10, "qualification": Qualification.ANY, "content": "指尖血糖检测"},
    37: {"name": "伤口护理", "min_duration": 20, "qualification": Qualification.NURSE, "content": "⚠️ 换药、清洁伤口 (仅护士)"},
    38: {"name": "静脉血标本采集", "min_duration": 15, "qualification": Qualification.NURSE, "content": "⚠️ 抽血 (仅护士)"},
    39: {"name": "肌肉注射", "min_duration": 15, "qualification": Qualification.NURSE, "content": "⚠️ 肌肉注射 (仅护士)"},
    40: {"name": "皮下注射", "min_duration": 15, "qualification": Qualification.NURSE, "content": "⚠️ 皮下注射 (仅护士)"},
    41: {"name": "引流管护理", "min_duration": 20, "qualification": Qualification.NURSE, "content": "⚠️ 各种引流管维护 (仅护士)"},
    42: {"name": "PICC管路维护", "min_duration": 20, "qualification": Qualification.NURSE, "content": "⚠️ PICC换药冲管 (仅护士)"}
}

# ==================== 数据B: 逻辑映射规则 (清洗版 - 无AB卷前缀) ====================
ASSESSMENT_RULES: Dict[str, List[int]] = {
    # --- 饮食 ---
    "饮食习惯: 低糖或无糖": [7, 36],       # 映射: 协助进食(7) + 血糖监测(36)
    "饮食习惯: 低盐": [7],                # 映射: 协助进食(7)
    "过敏情况: 食物过敏": [7],            # 映射: 协助进食(7) - 注意饮食
    "过敏情况: 药物过敏": [18],           # 映射: 药物管理(18)
    "噎食风险": [7],                     # 映射: 协助进食(7) - 防噎食
    "误吸风险": [7],                     # 映射: 协助进食(7) - 防误吸

    # --- 移动与安全 ---
    "跌倒风险": [23, 21],                # 映射: 安全护理(23) + 器具移动/行走(21)
    "步态异常": [21, 23],                # 映射: 器具移动(21) + 安全护理(23)
    "行动能力: 部分不能": [21, 28],       # 原文逻辑保留
    
    # --- 皮肤与压疮 ---
    "皮肤完整性: 受损": [22, 25, 37],     # 映射: 涂药(22) + 压疮预防(25) + 伤口换药(37)
    "压疮风险: 高": [19, 25],            # 映射: 翻身(19) + 压疮预防(25)
    
    # --- 个人卫生 ---
    "衣着整洁: 差": [9, 15],             # 映射: 穿脱衣(9) + 个人清洁(15)
    "身体潮湿": [10, 12, 25],            # 映射: 整理床(10) + 失禁/会阴(12) + 压疮预防(25)

    # --- 医疗护理 (重点检查) ---
    "留置尿管: 是": [26],                # 映射: 尿管护理(26) - 必须包含
    "需要监测血糖": [36],                # 映射: 血糖监测(36)
    "需要物理降温": [31],                # 映射: 物理降温(31)
    "需要吸氧": [33],                    # 映射: 氧气吸入(33)
    "需要PICC维护": [42],                # 映射: PICC维护(42)
    "严重便秘": [28],                    # 映射: 开塞露/灌肠(28)
}

# ==================== 安全约束 (清洗版) ====================
SAFETY_CONSTRAINTS: Dict[str, List[int]] = {
    "行动能力: 完全不能": [21],           # 卧床者不应安排"步行"
    "吞咽困难": [7],                      # (示例) 需要特殊护理
    "无尿管": [26],                       # 无尿管不能收护理费
    "无造口": [27],                       # 无造口不能收护理费
}

# ==================== 辅助函数 (包含 is_nurse_only_task) ====================
def get_task_info(task_id: int) -> Dict[str, Union[str, int, Qualification]]:
    return SERVICE_TASKS.get(task_id, {})

def get_required_tasks(condition: str) -> List[int]:
    """支持模糊匹配 (只要包含关键词就触发)"""
    required = []
    for key, tasks in ASSESSMENT_RULES.items():
        # 例如: 如果输入是 "过敏情况: 食物过敏"，能匹配 key "过敏情况: 食物过敏"
        if key in condition or condition in key: 
            required.extend(tasks)
    return list(set(required))

def get_contraindicated_tasks(condition: str) -> List[int]:
    return SAFETY_CONSTRAINTS.get(condition, [])

def get_all_task_ids() -> List[int]:
    return list(SERVICE_TASKS.keys())

def is_nurse_only_task(task_id: int) -> bool:
    """判断任务是否仅限护士"""
    task_info = get_task_info(task_id)
    if not task_info:
        return False
    return task_info.get("qualification") == Qualification.NURSE