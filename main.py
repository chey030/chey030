"""
Squirrel Assistant - 主程式入口點 (Main Entry Point)

支援持續對話循環模式，支援多意圖複合詢問 (同時問時間與日期)，並可說出「結束」、「再見」、「謝謝助手」安全退出。
"""

import os
import sys
import logging
import warnings

# 全域徹底壓制所有第三方庫非關鍵 Warning 與 Logging，保證 Console 完全乾淨
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
warnings.filterwarnings("ignore")
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("faster_whisper").setLevel(logging.ERROR)

from squirrel_assistant.core.assistant import SquirrelAssistant
from squirrel_assistant.core.interfaces import VoiceInput, VoiceOutput
from squirrel_assistant.skills.time_skill import TimeSkill
from squirrel_assistant.skills.date_skill import DateSkill
from squirrel_assistant.skills.exit_skill import ExitSkill


def main() -> None:
    """
    Squirrel Assistant 主執行動向 (持續對話與多意圖複合模式)
    """
    # 1. 初始化智慧語音輸入介面
    voice_input = VoiceInput(
        model_size="tiny",
        max_duration=5.0,
        silence_timeout=0.6,
        silence_threshold=0.004
    )

    # 2. 初始化語音輸出介面
    voice_output = VoiceOutput()

    # 3. 建立 Squirrel Assistant 核心控制器
    assistant = SquirrelAssistant(
        input_interface=voice_input,
        output_interface=voice_output
    )

    # 4. 註冊功能技能 (順序：DateSkill -> TimeSkill -> ExitSkill)
    # 同時問時間與日期時會先唸日期再唸時間，符合自然語意
    assistant.register_skill(DateSkill())
    assistant.register_skill(TimeSkill())
    assistant.register_skill(ExitSkill())

    # 5. 啟動持續對話循環
    assistant.run_loop()


if __name__ == "__main__":
    main()
