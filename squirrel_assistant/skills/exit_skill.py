"""
Exit Skill Module - 結束與退出技能模組

本模組實作 ExitSkill，處理使用者講出「結束」、「再見」、「拜拜」、「謝謝」、「退下」等退出意圖。
"""

from squirrel_assistant.skills.base import BaseSkill


class ExitSkill(BaseSkill):
    """
    結束/退出技能實作

    當使用者說出離別或感謝詞彙時觸發，並標記結束訊號。
    """

    # 觸發結束/退出的關鍵字清單
    EXIT_KEYWORDS = ["結束", "再見", "拜拜", "謝謝", "感謝", "關閉", "離開", "停止", "退下", "休息"]

    def __init__(self):
        self.is_exit_triggered = False

    def can_handle(self, text: str) -> bool:
        """檢查是否包含退出關鍵字"""
        if not text:
            return False
        return any(keyword in text for keyword in self.EXIT_KEYWORDS)

    def execute(self, text: str) -> str:
        """
        執行退出回應，並標記退出觸發狀態
        """
        self.is_exit_triggered = True

        if "謝謝" in text or "感謝" in text:
            return "不客氣！很高興為您服務，再見！"
        elif "拜拜" in text or "再見" in text:
            return "再見！祝您有美好的一天！"
        else:
            return "好的，已為您結束對話，有需要隨時找我！"
