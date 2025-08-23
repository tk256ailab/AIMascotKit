import google.generativeai as genai
from dotenv import load_dotenv
import os
import PIL.Image
import json

# .envファイルをロード
load_dotenv()

# 環境変数を取得
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# テキストファイルの内容をそのままbase_promptとして読み込む
try:
    with open("assets/characters/Sample/data/Sample_system_prompt.txt", "r", encoding="utf-8") as f:
        base_prompt = f.read()
except FileNotFoundError:
    print("エラー: システムプロンプトが見つかりません。")
    print("パスが正しいか、ファイルが存在するか確認してください。")
    exit() # ファイルが見つからない場合はプログラムを終了

chat_session = model.start_chat(history=[{"role":"user","parts":base_prompt}])

def send_message(user_input: str):
    """メッセージを送信し、応答を返す"""
    response = chat_session.send_message(user_input)
    return response.text

def send_message_with_image(user_input: str, image_path):
    """画像付きでメッセージを送信し、応答を返す"""
    image = PIL.Image.open(image_path)
    response = chat_session.send_message([user_input, image])
    return response.text

if __name__ == "__main__":
    user_input = input("テキストを入力： ")
    # response = send_message_with_image(user_input, "test.png")
    response = send_message(user_input)
    print("AI:", response)