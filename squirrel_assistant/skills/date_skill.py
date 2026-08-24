"""
Date Skill Module - 日期與星期查詢技能模組

本模組實作 DateSkill，專門處理日期、月份、幾號及星期相關的意圖查詢。
"""

import datetime
from squirrel_assistant.skills.base import BaseSkill


class DateSkill(BaseSkill):
    """
    日期與星期查詢技能實作

    負責回應「今天幾號」、「今天日期」、「今天星期幾」、「幾月幾號」等指令。
    """

    # 觸發此 Skill 的關鍵字清單
    INTENT_KEYWORDS = ["幾號", "日期", "星期", "禮拜", "幾月"]

    # 星期對照表
    WEEKDAY_ZH = ["一", "二", "三", "四", "五", "六", "日"]

    def can_handle(self, text: str) -> bool:
        """檢查是否包含日期相關關鍵字"""
        if not text:
            return False
        return any(keyword in text for keyword in self.INTENT_KEYWORDS)

    def execute(self, text: str) -> str:
        """
        取得目前 Windows 系統日期並格式化為中文回答

        例如：「今天是 2026 年 8 月 25 號，星期二。」
        """
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        day = now.day
        weekday_str = self.WEEKDAY_ZH[now.weekday()]

        return f"今天是 {year} 年 {month} 月 {day} 號，星期{weekday_str}。"
