"""
Skills Base Module - 技能抽象基類模組

本模組定義所有技能 (Skill) 的統一介面 BaseSkill。

【未來開發新技能指南】
欲新增功能（例如：Spotify 播放、YouTube 搜尋、遊戲啟動、Weather、Google 搜尋等），只需：
1. 在 `squirrel_assistant/skills/` 目錄下建立新的 Python 檔案 (例如 `spotify_skill.py`)
2. 繼承 `BaseSkill` 抽象類別
3. 實作 `can_handle(self, text: str) -> bool` 方法以判定意圖關鍵字
4. 實作 `execute(self, text: str) -> str` 方法執行核心業務邏輯並回傳回答文字
5. 在 `main.py` 中使用 `assistant.register_skill(YourNewSkill())` 註冊即可！
"""

from abc import ABC, abstractmethod


class BaseSkill(ABC):
    """
    技能抽象基類 (Skill Base Class)
    所有 Squirrel Assistant 的功能技能皆須繼承此基類。
    """

    @abstractmethod
    def can_handle(self, text: str) -> bool:
        """
        判斷此技能是否機能處理傳入的文字指令

        Args:
            text (str): 使用者輸入的文字指令 (如：「現在幾點」)

        Returns:
            bool: 若此 Skill 可處理則回傳 True，否則回傳 False
        """
        pass

    @abstractmethod
    def execute(self, text: str) -> str:
        """
        執行 Skill 的業務邏輯並回傳回答內容

        Args:
            text (str): 使用者輸入的文字指令

        Returns:
            str: 準備回應給使用者的中文文字內容
        """
        pass
