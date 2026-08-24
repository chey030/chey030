"""
Assistant Core Module - 核心控制器模組 (支援多意圖複合組合)

包含單次對話 (run_once) 與持續對話循環 (run_loop)。
當使用者在單一問句中同時包含多個意圖 (如同時問時間與日期) 時，
核心控制器會自動組合多個匹配 Skill 的回答並統一輸出。
"""

from typing import List
from squirrel_assistant.core.interfaces import InputInterface, OutputInterface
from squirrel_assistant.skills.base import BaseSkill
from squirrel_assistant.skills.exit_skill import ExitSkill


class SquirrelAssistant:
    """
    Squirrel Assistant 核心控制器

    Attributes:
        input_interface (InputInterface): 輸入介面
        output_interface (OutputInterface): 輸出介面
        skills (List[BaseSkill]): 註冊之技能外掛清單
        is_running (bool): 控管持續對話循環之狀態旗標
    """

    def __init__(self, input_interface: InputInterface, output_interface: OutputInterface):
        self.input_interface = input_interface
        self.output_interface = output_interface
        self.skills: List[BaseSkill] = []
        self.is_running = True

    def register_skill(self, skill: BaseSkill) -> None:
        """註冊新技能"""
        self.skills.append(skill)

    def run_once(self) -> None:
        """執行單次對話輪次 (支援多意圖複合技能)"""
        # 1. 取得使用者輸入
        text = self.input_interface.get_input()

        # 2. 空指令/靜音防護
        if not text:
            response = "抱歉，我沒有聽到聲音或無法辨識內容。"
            self.output_interface.send_output(response)
            return

        # 3. 收集所有能處理此指令的 Skill (多意圖感應)
        matching_skills: List[BaseSkill] = []
        for skill in self.skills:
            try:
                if skill.can_handle(text):
                    matching_skills.append(skill)
            except Exception as e:
                print(f"[錯誤] 技能檢測異常 ({skill.__class__.__name__}): {e}")

        # 4. 無匹配技能時的預設提示
        if not matching_skills:
            response = "抱歉，我目前還不明白這個指令。"
            self.output_interface.send_output(response)
            return

        # 5. 若包含退出技能 (ExitSkill)，優先處理平滑退出
        exit_skill = next(
            (s for s in matching_skills if isinstance(s, ExitSkill) or getattr(s, "is_exit_triggered", False)),
            None
        )
        if exit_skill:
            response = exit_skill.execute(text)
            self.output_interface.send_output(response)
            self.is_running = False
            return

        # 6. 執行並組合所有匹配 Skill 的回答 (如：同時問時間與日期時自動組合回應)
        responses: List[str] = []
        for skill in matching_skills:
            try:
                res = skill.execute(text)
                if res:
                    responses.append(res)
            except Exception as e:
                print(f"[錯誤] 技能執行異常 ({skill.__class__.__name__}): {e}")

        if responses:
            combined_response = " ".join(responses)
            self.output_interface.send_output(combined_response)
        else:
            response = "抱歉，系統處理時發生異常。"
            self.output_interface.send_output(response)

    def run_loop(self) -> None:
        """
        執行持續對話循環 (Continuous Dialogue Loop)
        直到使用者講出結束/退出關鍵字 (觸發 ExitSkill) 為止
        """
        self.is_running = True
        print("\n==========================================")
        print("🐿️ Squirrel Assistant 已開啟【持續對話模式】")
        print("💡 您可以隨時詢問時間與日期，或說「結束」、「再見」、「謝謝助手」來停止程式。")
        print("==========================================\n")

        while self.is_running:
            self.run_once()

        print("\n[系統提示] Squirrel Assistant 對話已結束。")

    def run(self) -> None:
        """單次執行向下相容方法"""
        self.run_once()
