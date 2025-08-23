import google.generativeai as genai
from dotenv import load_dotenv
import os

# .envファイルをロード
load_dotenv()

# 環境変数を取得
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    "temperature": 0, # 安定した出力に
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
    }

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    }
]

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-lite",
    generation_config=generation_config,
    safety_settings=safety_settings
    )

prompt = """あなたは感情分析をするAIです。
    以下のテキストを読み取り、話者の感情を判定してください。
    次のいずれかのラベルから、最も適切なものを **1つだけ英語で** 出力してください。
    **使用可能な感情ラベル**: normal, angry, sad, happy, excited, blush, surprised, sleepy, thinking, relax, goodbye

    すべての出力はラベル名のみで、余計な説明は含めないでください。

    参考例:
    - 「今日も普通に過ごせたな」→ normal
    - 「むかつく！なんなんだよ！」→ angry
    - 「失敗しちゃった……がっかり」→ sad
    - 「やった！うまくいった！」→ happy
    - 「すごい！最高だ！」→ excited
    - 「えっ、な、なんでそんなこと言うの？」→ blush
    - 「うそっ！？ほんとに！？」→ surprised
    - 「眠くてぼーっとする……」→ sleepy
    - 「うーん、どうしようかな…」→ thinking
    - 「やっとリラックスできる」→ relax
    - 「それじゃあ、また今度ね」→ goodbye
"""
# print(prompt)
chat_session = model.start_chat(history=[{"role":"user","parts":prompt}])


def emotion_analyzer(text: str):
    response = chat_session.send_message(text)
    print(response.text)

    emotion = "normal"
    if "normal" in response.text:
        emotion = "normal"
    elif "angry" in response.text:
        emotion = "angry"
    elif "sad" in response.text:
        emotion = "sad"
    elif "happy" in response.text:
        emotion = "happy"
    elif "excited" in response.text:
        emotion = "excited"
    elif "blush" in response.text:
        emotion = "blush"
    elif "surprised" in response.text:
        emotion = "surprised"
    elif "sleepy" in response.text:
        emotion = "sleepy"
    elif "thinking" in response.text:
        emotion = "thinking"
    elif "relax" in response.text:
        emotion = "relax"
    elif "goodbye" in response.text:
        emotion = "goodbye"

    return emotion

if __name__ == "__main__":
    while True:
        user_input = input("テキストを入力： ")
        if user_input.lower() == 'q':
            break
        emotion = emotion_analyzer(user_input)
        print(f"検出された感情: {emotion}")