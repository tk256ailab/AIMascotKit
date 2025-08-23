import speech_recognition as sr
import sounddevice as sd

#---音声認識---##################################################
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("話してください...")
        try:
            audio = recognizer.listen(source, timeout=60)  # 60秒の沈黙でタイムアウト
        except sr.WaitTimeoutError:
            print("タイムアウトしました。")
            return None

    try:
        print("認識中...")
        text = recognizer.recognize_google(audio, language="ja-JP")  # 日本語認識
        print("認識結果:", text)
        return text, True
    except sr.UnknownValueError:
        print("音声を認識できませんでした。")
        return None, False
    except sr.RequestError as e:
        print(f"Google Speech Recognition APIへのリクエストエラー: {e}")
        return None
###############################################################

if __name__ == "__main__":
    speech_to_text()