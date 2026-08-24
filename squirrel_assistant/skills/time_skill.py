"""
Time Skill Module - 時間查詢技能模組

本模組實作 TimeSkill，專門處理時間相關的意圖查詢。
包含系統時間讀取、12小時制轉換、時段判定 (凌晨/上午/中午/下午/晚上)，
以及將阿拉伯數字平滑轉換為自然口語的繁體中文文字。
"""

import re
import datetime
from squirrel_assistant.skills.base import BaseSkill


def _int_to_zh(n: int) -> str:
    """
    將 0-59 的整數轉換為自然口語的繁體中文數字表示

    Args:
        n (int): 0 到 59 之間的整數

    Returns:
        str: 對應的繁體中文數字字串
    """
    zh_digits = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]

    if 0 <= n <= 10:
        return zh_digits[n]
    elif 11 <= n <= 19:
        return "十" + zh_digits[n % 10]
    elif 20 <= n <= 59:
        tens = n // 10
        units = n % 10
        return zh_digits[tens] + "十" + (zh_digits[units] if units > 0 else "")

    return str(n)


class TimeSkill(BaseSkill):
    """
    時間查詢技能實作

    負責回應「現在幾點」、「現在時間」、「幾點了」、「報時」等文字指令。
    """

    # 觸發此 Skill 的精確關鍵字清單
    INTENT_KEYWORDS = ["幾點", "時間", "報時"]

    def can_handle(self, text: str) -> bool:
        """
        檢查輸入文字是否包含時間查詢關鍵字

        Args:
            text (str): 使用者輸入的文字

        Returns:
            bool: 包含關鍵字回傳 True
        """
        if not text:
            return False
        return any(keyword in text for keyword in self.INTENT_KEYWORDS)

    def execute(self, text: str) -> str:
        """
        取得目前 Windows 系統時間並格式化為中文回答

        Args:
            text (str): 傳入的文字指令

        Returns:
            str: 格式化後的中文回答
        """
        # 1. 取得當前本地系統時間
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute

        # 2. 判定時間區段 (時段)
        if 0 <= hour < 6:
            period = "凌晨"
        elif 6 <= hour < 12:
            period = "上午"
        elif 12 <= hour < 13:
            period = "中午"
        elif 13 <= hour < 18:
            period = "下午"
        else:
            period = "晚上"

        # 3. 轉換為 12 小時制
        hour_12 = hour % 12
        if hour_12 == 0:
            hour_12 = 12

        hour_zh = _int_to_zh(hour_12)

        # 4. 格式化分鐘
        if minute == 0:
            minute_str = "整"
        elif minute < 10:
            minute_str = f"零{_int_to_zh(minute)}分"
        else:
            minute_str = f"{_int_to_zh(minute)}分"

        # 5. 組裝最終語音文字
        return f"現在是{period}{hour_zh}點{minute_str}。"
