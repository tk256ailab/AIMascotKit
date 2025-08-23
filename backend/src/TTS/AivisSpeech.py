import io
import json
import soundfile
import requests
import time
import re

class AivisAdapter:
    def __init__(self):
        # APIサーバーのエンドポイントURL
        self.URL = "http://127.0.0.1:10101"
        # 話者ID (話させたい音声モデルidに変更してください)
        self.speaker = 888753760 # ノーマル
        # self.speaker = 706073888 # white

    def save_voice(self, text: str, output_filename: str = "voice.wav"):
        params = {"text": text, "speaker": self.speaker}
        query_response = requests.post(f"{self.URL}/audio_query", params=params).json()

        audio_response = requests.post(
            f"{self.URL}/synthesis",
            params={"speaker": self.speaker},
            headers={"accept": "audio/wav", "Content-Type": "application/json"},
            data=json.dumps(query_response),
        )

        with io.BytesIO(audio_response.content) as audio_stream:
            data, rate = soundfile.read(audio_stream)
            soundfile.write(output_filename, data, rate)

def hiraganize(text):
    """特別な読み方をして欲しいものを登録して平仮名に変換"""
    text = re.sub(r'桜夜（さよ）', 'さよ', text)
    text = re.sub(r'桜夜', 'さよ', text)
    text = re.sub(r'TK256', 'ティーケー', text) #カタカナなのは目を瞑ってください
    return text

def save_wavefile(text):
    adapter = AivisAdapter()
    text_replaced = hiraganize(text)
    adapter.save_voice(text_replaced, output_filename="backend/src/voice/voice.wav")


def main():
    adapter = AivisAdapter()
    while True:
        text = input("> ")
        start = time.time()
        # Q or q を入力して終了
        if text.lower() == "q":
            break
        adapter.save_voice(text)
        end = time.time()
        print(f"開始 {start}")
        print(f"終了 {end}")
        print(f"合成にかかった時間: {end - start:.2f} 秒")


if __name__ == "__main__":
    main()
