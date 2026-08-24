"""
Core Interfaces - 輸入與輸出介面模組 (穩定化增強版)

本模組定義 Squirrel Assistant 的輸入與輸出介面。
具備邊界情況防護、動態語音切斷 (VAD)、音量峰值正規化與長短句穩定相容。
"""

import os
import time
import logging
import warnings
import numpy as np
from abc import ABC, abstractmethod

# 壓制所有第三方庫非關鍵日誌與警告
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
warnings.filterwarnings("ignore")
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("faster_whisper").setLevel(logging.ERROR)


class InputInterface(ABC):
    """輸入介面抽象基類"""

    @abstractmethod
    def get_input(self) -> str:
        """取得使用者輸入並統一轉換為文字字串"""
        pass


class OutputInterface(ABC):
    """輸出介面抽象基類"""

    @abstractmethod
    def send_output(self, text: str) -> None:
        """將系統回答文字輸出至目標管道"""
        pass


class CLIInput(InputInterface):
    """控制台文字輸入實作"""

    def get_input(self) -> str:
        return input("請輸入指令: ").strip()


class ConsoleOutput(OutputInterface):
    """控制台文字輸出實作"""

    def send_output(self, text: str) -> None:
        print(f"助手：{text}")


class VoiceInput(InputInterface):
    """
    麥克風語音輸入實作 (sounddevice + faster-whisper)
    支援：
    1. 靈敏音量感應與動態 VAD 切斷 (短句說完 0.6 秒立刻結束，長句支援最長 5 秒)
    2. 音量 Peak Normalization (峰值自動增益)，確保 tiny 模型穩定高精準度
    3. 靜音/未發聲邊界安全防護
    """

    def __init__(
        self,
        model_size: str = "tiny",
        max_duration: float = 5.0,
        silence_timeout: float = 0.6,
        silence_threshold: float = 0.004,
        sample_rate: int = 16000
    ):
        """
        初始化 VoiceInput 穩定參數

        Args:
            model_size (str): Whisper 模型 ("tiny", "base")
            max_duration (float): 最長允許錄音上限 (秒，放寬至 5 秒以支援長句)
            silence_timeout (float): 說完話後安靜超過此秒數即自動結束錄音 (秒)
            silence_threshold (float): 音量門檻 (值越小越靈敏)
            sample_rate (int): 麥克風取樣率 (Hz)
        """
        self.model_size = model_size
        self.max_duration = max_duration
        self.silence_timeout = silence_timeout
        self.silence_threshold = silence_threshold
        self.sample_rate = sample_rate
        self.model = None

    def _load_model(self) -> None:
        """延遲載入 Whisper 模型"""
        if self.model is None:
            os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
            logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
            logging.getLogger("faster_whisper").setLevel(logging.ERROR)

            from faster_whisper import WhisperModel
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")

    def get_input(self) -> str:
        """開啟麥克風錄音並傳回 STT 文字，含健全邊界處理"""
        import sounddevice as sd

        print("Squirrel Assistant 啟動")
        print("請說話...")

        chunk_samples = int(self.sample_rate * 0.1)  # 100ms
        frames = []
        has_spoken = False
        silence_start = None
        start_time = time.time()

        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype="float32") as stream:
                while True:
                    chunk, _ = stream.read(chunk_samples)
                    frames.append(chunk)

                    # 計算當前區塊的 RMS 音量
                    rms = float(np.sqrt(np.mean(chunk ** 2)))
                    now = time.time()
                    elapsed = now - start_time

                    if rms > self.silence_threshold:
                        has_spoken = True
                        silence_start = None
                    else:
                        if has_spoken:
                            if silence_start is None:
                                silence_start = now
                            elif now - silence_start >= self.silence_timeout:
                                # 說完話連續安靜 0.6 秒，自動結束
                                break

                    # 到達長度上限自動結束
                    if elapsed >= self.max_duration:
                        break
        except Exception as e:
            print(f"[警告] 麥克風讀取異常: {e}")
            return ""

        print("錄音結束，正在辨識語音...")

        # 完全未講話或未檢測到發聲
        if not frames or not has_spoken:
            print("你：（未檢測到有效聲音）")
            return ""

        audio_data = np.concatenate(frames, axis=0).flatten()

        # 音量 Peak Normalization (峰值自動增益)
        max_amplitude = np.max(np.abs(audio_data))
        if max_amplitude > 0.001:
            audio_data = (audio_data / max_amplitude) * 0.85

        self._load_model()

        # 進行 Whisper 轉譯
        segments, _ = self.model.transcribe(
            audio_data,
            language="zh",
            beam_size=5,
            suppress_blank=True,
            initial_prompt="現在幾點？現在時間？幾點了？"
        )

        text = "".join([s.text for s in segments]).strip()
        print(f"你：{text}")
        return text


class VoiceOutput(OutputInterface):
    """語音合成輸出實作 (pyttsx3 + Windows SAPI5)"""

    def __init__(self):
        self.engine = None

    def _init_engine(self) -> None:
        if self.engine is None:
            import pyttsx3
            self.engine = pyttsx3.init()

            try:
                voices = self.engine.getProperty("voices")
                for voice in voices:
                    voice_id_lower = voice.id.lower()
                    if any(kw in voice_id_lower for kw in ["zh", "chinese", "taiwan", "han", "zhi"]):
                        self.engine.setProperty("voice", voice.id)
                        break
            except Exception:
                pass

    def send_output(self, text: str) -> None:
        print(f"助手：{text}")

        self._init_engine()
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
