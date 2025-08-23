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

prompt = """あなたは画像の必要性を判断するAIです。
    ユーザーの発言が「現在の画面や視覚的な要素」に依存している場合にのみ「必要」と答えてください。

    以下の基準に従って判断してください：

    【「必要」と判定する条件】
    - 「これ」「この」「ここ」など、指示語を含んでいて明確な対象が文脈上不明なとき
    - UI（ボタン、アイコン、画像）などの操作対象を指している可能性があるとき
    - 見た目に関する発言（「かわいいね」「色が変」など）

    【「不要」と判定する条件】
    - 一般的な雑談、挨拶、質問（「おはよう」「元気？」など）
    - 状況や画面を見なくても返答できる内容（「何食べたい？」「元気そうだね」など）

    すべての出力は「必要」または「不要」のいずれかのみで返答してください。

    例：
    - 「これって何？」 → 必要
    - 「このボタンって押すべき？」 → 必要
    - 「このキャラ強い？」 → 必要
    - 「画面見えてる？」 → 必要
    - 「お腹空いた」 → 不要
    - 「やる気出ないなぁ」 → 不要
"""
# print(prompt)
chat_session = model.start_chat(history=[{"role":"user","parts":prompt}])


def image_requirement_detector(user_input: str):
    response = chat_session.send_message(user_input)
    print(response.text)
    if "必要" in response.text:
        is_image_required = True
    else:
        is_image_required = False
    return is_image_required


if __name__ == "__main__":
    while True:
        user_input = input("テキストを入力： ")
        is_image_requirement = image_requirement_detector(user_input)