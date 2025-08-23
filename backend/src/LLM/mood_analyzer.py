import google.generativeai as genai
from dotenv import load_dotenv
import os
import re

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

base_prompt = """
あなたは、対話中のAITuberの感情を分析するAIアナリストです。
以下に、ユーザーとAITuberの会話ログが与えられます。
この会話の内容から、AITuberの現在の「ご機嫌度」を**0〜100の数値**で出力してください。

- 0は「非常に不機嫌」、100は「とても機嫌が良い」状態を示します。
- ご機嫌度は、AITuberの**発言内容**、**口調**、**ユーザーの発言への反応**などから判断してください。
- 感情表現が曖昧な場合は、中立（50）を基準に推定してください。
- **出力は数値（整数）だけにしてください。説明やコメントは不要です。**

#### 会話ログ（例）：
ユーザー：今日は一緒にゲームしよう！
AITuber：やったー！ずっと待ってたよー！楽しみ〜！

#### 出力形式：
72
"""

# print(base_prompt)
chat_session = model.start_chat(history=[{"role":"user","parts":base_prompt}])


def extract_mood_score(llm_output: str) -> int:
    """
    LLMの出力から最初に現れる0〜100の整数を抽出し、返す関数。
    該当する数値が見つからなければ ValueError を投げる。
    """
    match = re.search(r'\b([0-9]{1,3})\b', llm_output)
    if match:
        score = int(match.group(1))
        if 0 <= score <= 100:
            return score
        else:
            raise ValueError(f"数値 {score} は 0〜100 の範囲外です")
    else:
        raise ValueError("0〜100の数値が見つかりませんでした")

def mood_analyzer(user_input, llm_output):
    prompt = f"""
    ユーザーの発言: {user_input}
    AITuberの発言: {llm_output}
    """
    response = chat_session.send_message(prompt)
    print(f"ご機嫌度：{response.text}")
    mood_value = extract_mood_score(response.text)
    return mood_value


if __name__ == "__main__":
    while True:
        user_input = input("ユーザーの発言： ")
        llm_output = input("AITuberの発言： ")
        mood_value = mood_analyzer(user_input, llm_output)
        print(mood_value)