import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum

# インポート（VRM対応版）
from src.LLM.conversation import send_message_with_image, send_message
from src.TTS.AivisSpeech import save_wavefile
from src.STT.speech_to_text import speech_to_text
from src.screenshot.screenshot import get_window_by_app_name
from src.screenshot.screenshot_front import get_frontmost_window_info, capture_window
from src.display.subtitle import update_subtitle
from src.LLM.translator import translator
from src.LLM.task_classifier import task_classifier
from src.LLM.image_requirement import image_requirement_detector
from src.LLM.emotion_analyzer import emotion_analyzer
from src.LLM.mood_analyzer import mood_analyzer
from src.vrm_control.vrm_controller import VRMController


class InputMode(Enum):
    """入力モードの定義"""
    MANUAL = 0
    VOICE = 1

@dataclass
class ConversationMetrics:
    """会話のパフォーマンス指標"""
    total_time: float = 0.0
    response_generation_time: float = 0.0
    translation_time: float = 0.0
    emotion_analysis_time: float = 0.0
    mood_value_analysis_time: float = 0.0
    voice_synthesis_time: float = 0.0
    screenshot_time: float = 0.0
    task_classification_time: float = 0.0
    image_requirement_time: float = 0.0


class VRMAITuberSystem:
    """VRM AITuberシステムのメインクラス"""

    def __init__(self, default_app_name: str = "Google Chrome"):
        """
        VRM AITuberSystemの初期化
        
        Args:
            default_app_name: デフォルトでスクリーンショットを取得するアプリ名
        """
        self.default_app_name = default_app_name
        self.image_path = "./backend/src/image/screenshot.png"
        self.window_info = None
        self.executor = ThreadPoolExecutor()
        self.metrics = ConversationMetrics()
        
        # VRM制御システム初期化
        self.vrm_controller = VRMController()
        
        # 初期化処理
        self._initialize_system()
    
    def _initialize_system(self) -> None:
        """システムの初期化"""
        self.window_info = get_window_by_app_name(self.default_app_name)
        update_subtitle(" ")
        
        # VRMサーバーが利用できない場合でも続行
        try:
            self.vrm_controller.set_expression("normal")
        except Exception as e:
            print(f"[警告] VRMサーバーが利用できません: {e}")
            
        print("VRM AITuberシステムが初期化されました")
    
    def _update_ui_and_voice(self, response: str, en_res: str) -> None:
        """UIと音声の更新"""
        subtitle = f"{response} <br> {en_res}"
        update_subtitle(subtitle)
        save_wavefile(response)
        time.sleep(0.1)
        self.vrm_controller.set_expression("normal")
        self.vrm_controller.play_motion("normal")
        self.vrm_controller.play_voice()
    
    def timer_done_callback(self, minutes: int) -> None:
        """
        タイマー終了時のコールバック関数
        
        Args:
            minutes: タイマーの分数
        """
        print(f"\n[TIMER DONE]\n")
        prompt = "タイマーが終了しました。終了のお知らせをしてください。"
        response = send_message(prompt)
        
        print("AI:\n", response)
        en_res = translator(response)
        print("Eng:\n", en_res)
        
        self._update_ui_and_voice(response, en_res)
    
    def _get_user_input(self, mode: InputMode) -> Tuple[str, bool]:
        """
        ユーザー入力の取得
        
        Args:
            mode: 入力モード
            
        Returns:
            (user_input, is_recognized): ユーザー入力と認識成功フラグ
        """
        if mode == InputMode.MANUAL:
            user_input = input("あなた:")
            return user_input, True
        elif mode == InputMode.VOICE:
            return speech_to_text()
        else:
            raise ValueError(f"Unsupported input mode: {mode}")
    
    def _detect_image_requirement(self, user_input: str) -> bool:
        """画像必要性の検出"""
        start = time.time()
        is_image_requirement = image_requirement_detector(user_input)
        elapsed = time.time() - start
        self.metrics.image_requirement_time = elapsed
        print(f"画像必要性判定にかかった時間: {elapsed:.2f}秒")
        return is_image_requirement
    
    def _classify_task(self, user_input: str) -> Tuple[bool, str]:
        """タスクの分類"""
        start = time.time()
        is_task_matched, hint = task_classifier(user_input, timer_callback=self.timer_done_callback)
        elapsed = time.time() - start
        self.metrics.task_classification_time = elapsed
        print(f"タスク判定にかかった時間: {elapsed:.2f}秒")
        return is_task_matched, hint
    
    def _translate_text(self, text: str) -> str:
        """テキストの翻訳"""
        start = time.time()
        result = translator(text)
        elapsed = time.time() - start
        self.metrics.translation_time = elapsed
        print(f"翻訳にかかった時間: {elapsed:.2f}秒")
        return result
    
    def _analyze_emotion(self, text: str) -> str:
        """感情分析"""
        start = time.time()
        emotion = emotion_analyzer(text)
        elapsed = time.time() - start
        self.metrics.emotion_analysis_time = elapsed
        print(f"感情分析にかかった時間: {elapsed:.2f}秒")
        return emotion

    def _analyze_mood_value(self, user_input: str, llm_output: str) -> int:
        """ご機嫌度診断"""
        start = time.time()
        mood_value = mood_analyzer(user_input, llm_output)
        elapsed = time.time() - start
        self.metrics.mood_value_analysis_time = elapsed
        print(f"ご機嫌度診断にかかった時間: {elapsed:.2f}秒")
        return mood_value
    
    def _save_voice_file(self, text: str) -> None:
        """音声ファイルの保存"""
        start = time.time()
        save_wavefile(text)
        elapsed = time.time() - start
        self.metrics.voice_synthesis_time = elapsed
        print(f"音声合成にかかった時間: {elapsed:.2f}秒")
    
    def _capture_screenshot(self, mode: InputMode) -> None:
        """スクリーンショットの撮影"""
        start = time.time()
        
        # 音声入力の場合、アクティブウィンドウを取得
        if mode == InputMode.VOICE:
            self.window_info = get_frontmost_window_info()
        
        capture_window(self.window_info, save_path=self.image_path)
        elapsed = time.time() - start
        self.metrics.screenshot_time = elapsed
        print(f"スクリーンショットにかかった時間: {elapsed:.2f}秒")
    
    def _generate_response(self, prompt: str, use_image: bool, mode: InputMode) -> str:
        """AI応答の生成"""
        start = time.time()
        
        if use_image:
            self._capture_screenshot(mode)
            response = send_message_with_image(prompt, self.image_path)
        else:
            response = send_message(prompt)
        
        elapsed = time.time() - start
        self.metrics.response_generation_time = elapsed
        print(f"応答生成にかかった時間: {elapsed:.2f}秒")
        return response
    
    def _process_parallel_tasks(self, user_input: str) -> Tuple[bool, str, bool]:
        """並列タスクの処理（タスク分類と画像必要性検出）"""
        future_task = self.executor.submit(self._classify_task, user_input)
        future_detection = self.executor.submit(self._detect_image_requirement, user_input)
        
        is_task_matched, hint = future_task.result()
        is_image_requirement = future_detection.result()
        
        return is_task_matched, hint, is_image_requirement
    
    def _process_response_tasks(self, user_input: str, response: str) -> Tuple[str, str, int]:
        """応答後の並列タスク処理（翻訳、感情分析、ご機嫌度診断、音声合成）"""
        future_translate = self.executor.submit(self._translate_text, response)
        future_emotion = self.executor.submit(self._analyze_emotion, response)
        future_mood_value = self.executor.submit(self._analyze_mood_value, user_input, response)
        future_save_wave = self.executor.submit(self._save_voice_file, response)
        
        en_res = future_translate.result()
        emotion = future_emotion.result()
        mood_value = future_mood_value.result()
        future_save_wave.result()  # 完了を待つ
        
        return en_res, emotion, mood_value
    
    def _update_vrm_and_ui(self, response: str, en_res: str, emotion: str, mood_value: int) -> None:
        """VRMとUIの更新"""
        print("AI:\n", response)
        print("Eng:\n", en_res)
        
        subtitle = f"{response} <br> {en_res}"
        update_subtitle(subtitle)
        
        # VRM表情・アニメーション制御
        self.vrm_controller.set_expression(emotion)  # 表情設定
        self.vrm_controller.handle_emotion_from_live2d(emotion)  # アニメーション再生
        self.vrm_controller.set_mood_value(mood_value)
        self.vrm_controller.play_voice()
    
    def _print_metrics(self) -> None:
        """パフォーマンス指標の出力"""
        print(f"会話にかかった時間: {self.metrics.total_time:.2f}秒\n")

    def greeting(self) -> None:
        """起動時の挨拶"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        print("現在時刻:", current_time)
        mode = InputMode(0)
        response = self._generate_response(f"【現在時刻は{current_time}です。ユーザーに挨拶してください。】", False, mode)
        en_res, emotion, mood_value = self._process_response_tasks("", response)
        self._update_vrm_and_ui(response, en_res, emotion, mood_value)
        self.vrm_controller.send_subtitle(response, en_res)
    
    def process_conversation(self, user_input: str, mode: InputMode) -> None:
        """
        一回の会話処理
        
        Args:
            user_input: ユーザーの入力
            mode: 入力モード
        """
        conv_start = time.time()
        
        # 並列タスク処理
        is_task_matched, hint, is_image_requirement = self._process_parallel_tasks(user_input)
        
        # プロンプトの準備
        if is_task_matched:
            prompt = f"【{hint}これを踏まえて次のメッセージに返答して。】\n\n{user_input}"
        else:
            prompt = user_input
        
        # AI応答の生成
        response = self._generate_response(prompt, is_image_requirement, mode)
        
        # 応答後の並列処理
        en_res, emotion, mood_value = self._process_response_tasks(prompt, response)
        
        # UI更新
        self._update_vrm_and_ui(response, en_res, emotion, mood_value)
        
        # 字幕送信
        self.vrm_controller.send_subtitle(response, en_res)
        
        # メトリクス更新
        self.metrics.total_time = time.time() - conv_start
        self._print_metrics()
    
    def run(self) -> None:
        """メインループの実行"""
        try:
            # モード選択
            mode_input = int(input("手入力:0 音声認識:1 "))
            mode = InputMode(mode_input)
            
            print(f"VRM AITuberシステム開始 - モード: {mode.name}")

            # 起動時の挨拶
            self.greeting()
            
            while True:
                # ユーザー入力の取得
                user_input, is_recognized = self._get_user_input(mode)
                
                # 終了条件チェック
                if mode == InputMode.MANUAL and user_input.lower() == 'q':
                    break
                
                # 認識成功した場合のみ処理
                if is_recognized:
                    self.process_conversation(user_input, mode)
                    if "さよなら" in user_input:
                        time.sleep(3)
                        self.cleanup()
                        break
                    
        except ValueError as e:
            print(f"エラー: {e}")
        except KeyboardInterrupt:
            print("\nシステムを終了します...")
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """リソースのクリーンアップ"""
        print("システムを終了しています...")
        
        # UI初期化
        update_subtitle(" ")
        
        # VRMサーバーが利用できない場合でもエラーにしない
        try:
            self.vrm_controller.set_expression("normal")
            self.vrm_controller.set_mood_value(50)
        except Exception as e:
            print(f"[警告] VRM終了処理でエラー: {e}")
        
        # ExecutorのShutdown
        self.executor.shutdown(wait=True)
        
        print("VRM AITuberシステムが終了しました。")


def main():
    """メイン関数"""
    system = VRMAITuberSystem()
    system.run()


if __name__ == "__main__":
    main()