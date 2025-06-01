# llm_model/llm_services.py
import os
import json
from datetime import datetime
from mistralai import Mistral
from flask import jsonify
from dotenv import load_dotenv

load_dotenv()

# 初始化 Mistral 客戶端
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))


def generate_structured_output(
        event_name: str,
        event_deadline: str,
        created_at: datetime,  # 新增創建時間參數
        event_description: str,
        user_habits: list = None,  # 新增使用者習慣參數
        json_schema: dict = None
) -> dict:
    """
    根據目標資料生成每日任務 (JSON格式)
    新增 created_at 參數用於時間區間控制
    新增 user_habits 參數用於提供習慣資訊

    :param event_name: 目標名稱
    :param event_deadline: 截止日期 (格式: YYYY-MM-DD)
    :param created_at: 目標創建時間 (datetime物件)
    :param event_description: 目標詳細描述
    :param user_habits: 使用者的習慣列表
    :param json_schema: 自訂JSON結構 (預設使用內建結構)
    :return: 解析後的任務字典
    """
    try:
        # 轉換為日期對象進行驗證
        deadline_date = datetime.strptime(event_deadline, "%Y-%m-%d").date()
        created_date = created_at.date()

        if created_date >= deadline_date:
            raise ValueError("截止日期必須晚於創建時間")

        default_schema = {
            "tasks": [
                {
                    "task_name": "string",
                    "due_date": "YYYY-MM-DD",
                    "priority": "high/medium/low",
                    "dependencies": ["string"],
                }
            ]
        }
        json_schema = json_schema or default_schema

        # 組織使用者習慣資訊
        habits_prompt = ""
        if user_habits and len(user_habits) > 0:
            habits_prompt = "使用者習慣資訊：\n"
            for habit in user_habits:
                habits_prompt += f"- 習慣名稱：{habit.get('name', '')}\n"
                if 'frequency' in habit:
                    habits_prompt += f"  頻率：{habit.get('frequency', '')}\n"
                if 'intensity' in habit:
                    habits_prompt += f"  強度：{habit.get('intensity', '')}\n"
                if 'description' in habit:
                    habits_prompt += f"  描述：{habit.get('description', '')}\n"
            habits_prompt += "\n"

        # 組合提示詞 (包含創建時間和使用者習慣)
        system_prompt = f"""你是一位專業任務規劃助理。請根據下方的 eventDescription，嚴格拆解出每日任務，並只以純 JSON 格式回傳（不要有任何說明文字）。

eventDescription: "{event_description}"

{habits_prompt}請參考上述使用者習慣，讓任務安排與使用者的習慣保持一致。

請嚴格遵守以下 JSON 結構：
{json.dumps(json_schema, indent=2, ensure_ascii=False)}

規則：
1. 只允許輸出 JSON，不能有其他文字。
2. 每個任務必須能從 eventDescription 找到依據。
3. 每個任務的 due_date 必須介於目標創建時間 ({created_date.strftime('%Y-%m-%d')}) 和截止日期 ({event_deadline}) 之間，且格式為 YYYY-MM-DD。
4. 任務名稱務必用中文。
5. 任務規劃應考慮用戶習慣，調整任務的安排以適應用戶的生活習慣。"""

        # 組織使用者習慣資訊的簡短摘要
        habits_summary = ""
        if user_habits and len(user_habits) > 0:
            habits_summary = "User Habits:\n"
            for habit in user_habits:
                habits_summary += f"- {habit.get('name', '')}: {habit.get('frequency', '')} frequency, {habit.get('intensity', '')} intensity\n"
        
        user_prompt = f"""
            Goal Name: {event_name}
            Deadline: {event_deadline}
            Description: {event_description}
            {habits_summary}"""

        # 呼叫 Mistral API
        response = client.chat.complete(
            model="open-mistral-nemo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )

        # 解析 JSON
        result = json.loads(response.choices[0].message.content)

        # 驗證時間區間
        for task in result.get('tasks', []):
            task_date = datetime.strptime(task['due_date'], "%Y-%m-%d").date()
            if not (created_date <= task_date <= deadline_date):
                raise ValueError(f"任務 '{task['task_name']}' 的日期超出有效範圍")
            

        return result

    except json.JSONDecodeError as e:
        return {"error": f"JSON 解析失敗: {str(e)}"}
    except Exception as e:
        return {"error": f"API 呼叫失敗: {str(e)}"}

def generate_tasks_for_habit_building(habit_name: str, frequency: str, intensity: str, created_at: datetime, deadline: str) -> dict:
    """
    專門為習慣養成拆解每日任務的函式。
    
    :param habit_name: 習慣名稱，例如「喝水2000ml」
    :param frequency: 頻率 (low, medium, high)
    :param intensity: 強度 (low, medium, high)
    :param created_at: 習慣建立時間 datetime 物件
    :param deadline: 任務拆解截止日期 字串，格式 'YYYY-MM-DD'
    :return: 拆解後的任務字典，格式同 generate_structured_output
    """
    event_description = (
        f"請協助我把習慣「{habit_name}」拆解成每天的小任務。"
        f"此習慣頻率為 {frequency}，強度為 {intensity}。"
        "任務需要每天分配，幫助我持續養成這個習慣。"
    )
    
    # 直接呼叫通用的 generate_structured_output
    return generate_structured_output(
        event_name=habit_name,
        event_deadline=deadline,
        created_at=created_at,
        event_description=event_description
    )
