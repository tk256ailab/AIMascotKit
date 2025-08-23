"""
VRM感情制御システム
Live2Dの感情分析結果をVRMのVRMAアニメーションにマッピング
"""

import requests
import json
from typing import Optional
import warnings

# requestsの警告を抑制
warnings.filterwarnings('ignore')

class VRMController:
    def __init__(self, flask_server_url: str = "http://127.0.0.1:5000"):
        self.flask_server_url = flask_server_url
        self.server_available = self._check_server_availability()
        
        # Live2D表情 → VRM感情のマッピング
        self.live2d_to_vrm_emotion = {
            'normal': 'normal',
            'happy': 'happy',
            'sad': 'sad',
            'angry': 'angry',
            'excited': 'excited',
            'blush': 'blush',
            'surprised': 'surprised',
            'sleepy': 'sleepy',
            'thinking': 'thinking',
            'relax': 'relax',
            'goodbye': 'goodbye',
            # 後方互換性のための旧マッピング
            'neutral': 'normal',
            'smile': 'happy',
            'cry': 'sad',
            'laugh': 'excited',
            'worry': 'sad'
        }
        
        # VRM感情 → VRMAファイルのマッピング
        self.emotion_to_vrma = {
            'normal': 'Relax.vrma',
            'angry': 'Angry.vrma',
            'sad': 'Sad.vrma',
            'happy': 'Clapping.vrma',
            'excited': 'Jump.vrma',
            'blush': 'Blush.vrma',
            'surprised': 'Surprised.vrma',
            'sleepy': 'Sleepy.vrma',
            'thinking': 'Thinking.vrma',
            'relax': 'Relax.vrma',
            'goodbye': 'Goodbye.vrma'
        }
    
    def _check_server_availability(self) -> bool:
        """VRMサーバーが利用可能かチェック"""
        try:
            response = requests.get(f"{self.flask_server_url}/", timeout=1)
            return response.status_code == 200
        except:
            return False
    
    def send_vrm_emotion(self, emotion: str) -> bool:
        """
        VRM感情をFlaskサーバーに送信
        
        Args:
            emotion: 感情 ('normal', 'angry', 'sad', 'happy', 'excited', 'blush', 'surprised', 'sleepy', 'thinking', 'relax', 'goodbye')
        
        Returns:
            bool: 送信成功かどうか
        """
        if not self.server_available:
            return False
            
        try:
            response = requests.post(
                f"{self.flask_server_url}/vrm/motion",
                json={'emotion': emotion},
                timeout=2
            )
            
            if response.status_code == 200:
                print(f"[VRM] 感情 '{emotion}' を送信しました")
                return True
            else:
                # VRMサーバーが利用できない場合は静かに失敗
                return False
                
        except requests.exceptions.RequestException as e:
            # VRMサーバーが起動していない場合は静かに失敗
            return False
    
    def convert_live2d_emotion(self, live2d_emotion: str) -> Optional[str]:
        """
        Live2D表情をVRM感情に変換
        
        Args:
            live2d_emotion: Live2D表情名
            
        Returns:
            str: VRM感情名、またはNone
        """
        return self.live2d_to_vrm_emotion.get(live2d_emotion.lower())
    
    def handle_emotion_from_live2d(self, live2d_emotion: str) -> bool:
        """
        Live2Dの感情分析結果を受け取ってVRMに送信
        
        Args:
            live2d_emotion: Live2D感情分析の結果
            
        Returns:
            bool: 処理成功かどうか
        """
        vrm_emotion = self.convert_live2d_emotion(live2d_emotion)
        
        if vrm_emotion:
            return self.send_vrm_emotion(vrm_emotion)
        else:
            # 未対応の感情の場合はデフォルトでnormalを送信
            return self.send_vrm_emotion('normal')
    
    def send_idle_animation(self) -> bool:
        """
        アイドル状態のアニメーションを送信
        """
        return self.send_vrm_emotion('normal')
    
    def get_vrma_file_for_emotion(self, emotion: str) -> Optional[str]:
        """
        感情に対応するVRMAファイル名を取得
        
        Args:
            emotion: 感情名
            
        Returns:
            str: VRMAファイル名、またはNone
        """
        return self.emotion_to_vrma.get(emotion)
    
    def set_expression(self, emotion: str) -> bool:
        """
        表情を設定（Live2D互換メソッド）
        
        Args:
            emotion: 感情名
            
        Returns:
            bool: 設定成功かどうか
        """
        # 表情設定をFlaskサーバーに送信（モーションとは別のエンドポイント）
        if not self.server_available:
            return False
            
        try:
            response = requests.post(
                f"{self.flask_server_url}/expression",
                json={'expression': emotion},
                timeout=2
            )
            
            if response.status_code == 200:
                print(f"[VRM] 表情 '{emotion}' を送信しました")
                return True
            else:
                return False
                
        except requests.exceptions.RequestException as e:
            return False
    
    def play_motion(self, motion: str) -> bool:
        """
        モーションを再生（Live2D互換メソッド）
        
        Args:
            motion: モーション名
            
        Returns:
            bool: 再生成功かどうか
        """
        # モーション名を感情に変換
        emotion = self.live2d_to_vrm_emotion.get(motion, 'normal')
        return self.send_vrm_emotion(emotion)
    
    def play_voice(self) -> bool:
        """
        音声を再生（Live2D互換メソッド）
        VRMサーバーに音声再生指示を送信
        
        Returns:
            bool: 送信成功かどうか
        """
        if not self.server_available:
            return False
            
        try:
            response = requests.post(
                f"{self.flask_server_url}/voice",
                json={'action': 'play'},
                timeout=2
            )
            
            if response.status_code == 200:
                print("[VRM] 音声再生指示を送信しました")
                return True
            else:
                # VRMサーバーが利用できない場合は静かに失敗
                return False
                
        except requests.exceptions.RequestException as e:
            # VRMサーバーが起動していない場合は静かに失敗
            return False
    
    def set_mood_value(self, mood_value: int) -> bool:
        """
        ご機嫌度を設定（Live2D互換メソッド）
        
        Args:
            mood_value: ご機嫌度（0-100）
            
        Returns:
            bool: 設定成功かどうか
        """
        if not self.server_available:
            return False
            
        try:
            response = requests.post(
                f"{self.flask_server_url}/mood",
                json={'mood_value': mood_value},
                timeout=2
            )
            
            if response.status_code == 200:
                print(f"[VRM] ご機嫌度 {mood_value} を送信しました")
                return True
            else:
                # VRMサーバーが利用できない場合は静かに失敗
                return False
                
        except requests.exceptions.RequestException as e:
            # VRMサーバーが起動していない場合は静かに失敗
            return False
    
    def send_subtitle(self, japanese_text: str, english_text: str) -> bool:
        """
        字幕を送信（VRM向け拡張メソッド）
        
        Args:
            japanese_text: 日本語字幕
            english_text: 英語字幕
            
        Returns:
            bool: 送信成功かどうか
        """
        if not self.server_available:
            return False
            
        try:
            response = requests.post(
                f"{self.flask_server_url}/subtitle",
                json={
                    'japanese': japanese_text,
                    'english': english_text
                },
                timeout=2
            )
            
            if response.status_code == 200:
                print(f"[VRM] 字幕を送信しました")
                return True
            else:
                # VRMサーバーが利用できない場合は静かに失敗
                return False
                
        except requests.exceptions.RequestException as e:
            # VRMサーバーが起動していない場合は静かに失敗
            return False

# 使用例とテスト用関数
def test_vrm_emotion_controller():
    """VRM感情制御システムのテスト"""
    controller = VRMController()
    
    # テスト用感情リスト
    test_emotions = ['normal', 'angry', 'sad', 'happy', 'excited', 'blush', 'surprised', 'sleepy', 'thinking', 'relax', 'goodbye']
    
    print("=== VRM感情制御システムテスト ===")
    
    for emotion in test_emotions:
        print(f"\nテスト感情: {emotion}")
        vrm_emotion = controller.convert_live2d_emotion(emotion)
        print(f"変換後VRM感情: {vrm_emotion}")
        
        if vrm_emotion:
            vrma_file = controller.get_vrma_file_for_emotion(vrm_emotion)
            print(f"対応VRMAファイル: {vrma_file}")
            
            # 実際にサーバーに送信（サーバーが起動している場合）
            success = controller.send_vrm_emotion(vrm_emotion)
            print(f"送信結果: {'成功' if success else '失敗'}")

if __name__ == "__main__":
    test_vrm_emotion_controller()