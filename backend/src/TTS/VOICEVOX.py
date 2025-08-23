import re
import requests
import time
import numpy as np
import wave
import simpleaudio

#---音声合成---##################################################
def audio_query(text, speaker, max_retry):
    for query_i in range(max_retry):
        try:
            # `params=` を使うのが正しい
            r = requests.post(
                "http://localhost:50021/audio_query",
                params={"text": text, "speaker": speaker},  # ← ここを `params=` に修正
                headers={"Content-Type": "application/json"},  
                timeout=(10.0, 300.0)
            )

            if r.status_code == 200:
                query_data = r.json()
                query_data["speedScale"] = 1.2  # 再生速度を変更
                return query_data

            print(f"audio_query エラー: {r.status_code} - {r.text}")

        except requests.exceptions.RequestException as e:
            print(f"リクエストエラー: {e}")

        time.sleep(1)

    raise ConnectionError(f"リトライ回数が上限に到達しました。 audio_query : {text[:30]}")

def synthesis(speaker, query_data, max_retry):
    for synth_i in range(max_retry):
        try:
            r = requests.post(
                "http://localhost:50021/synthesis",
                params={"speaker": speaker},  # ここは `params=` でOK
                json=query_data,  # `json=` を使う
                headers={"Content-Type": "application/json"},
                timeout=(10.0, 300.0)
            )

            if r.status_code == 200:
                return r.content

            print(f"synthesis エラー: {r.status_code} - {r.text}")

        except requests.exceptions.RequestException as e:
            print(f"リクエストエラー: {e}")

        time.sleep(1)

    raise ConnectionError(f"音声エラー：リトライ回数が上限に到達しました。 synthesis")

def save_wav(data, filename, volume_gain=2.0):
    # バイナリを numpy.int16 に変換
    audio_array = np.frombuffer(data, dtype=np.int16)

    # 音量を増幅（クリッピング対策で16bitの範囲に収める）
    audio_array = np.clip(audio_array * volume_gain, -32768, 32767).astype(np.int16)

    # numpy配列 → バイナリ
    amplified_data = audio_array.tobytes()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)       # モノラル
        wf.setsampwidth(2)       # 16bit = 2bytes
        wf.setframerate(24000)   # VOICEVOXの出力サンプリング周波数
        wf.writeframes(amplified_data)

def save_wavefile(texts, speaker=46, max_retry=20):
    if texts==False:
        texts="ちょっと、通信状態悪いかも？"
    texts=re.split("(?<=！|。|？)",texts)
    all_voice_data = b''
    play_obj=None
    for text in texts:

        if not text.strip():
            continue

        # audio_query
        query_data = audio_query(text,speaker,max_retry)

        # synthesis
        voice_data=synthesis(speaker,query_data,max_retry)

        # データを結合
        all_voice_data += voice_data

    #音声の保存
    filename = "voice.wav"
    save_wav(all_voice_data, filename)
    print(f"音声ファイルを保存しました: {filename}")

    #音声の再生
    # wave_obj=simpleaudio.WaveObject(all_voice_data,1,2,24000)
    # play_obj=wave_obj.play()
    # play_obj.wait_done()
###############################################################

if __name__ == "__main__":
    save_wavefile("こんにちは")