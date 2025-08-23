import google.generativeai as genai
from dotenv import load_dotenv
import os

# .envファイルをロード
load_dotenv()

# 環境変数を取得
GEMINI_API_KEY = os.getenv("GEMINI_TRANSLATE_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    "temperature": 1,
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

chat_session = model.start_chat(history=[{"role":"user","parts":[
    "あなたは翻訳機です。"
    "与えられたテキストを英語に翻訳してください。"
    "回答は翻訳結果のみにしてください。"
    ]}])

def translator(user_input: str):
    response = chat_session.send_message(user_input)
    return response.text

if __name__ == "__main__":
    user_input = input("テキストを入力： ")
    response = translator(user_input)
    print("AI:", response)