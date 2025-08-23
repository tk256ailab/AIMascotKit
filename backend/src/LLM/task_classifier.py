import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import re

from .tasks.check_wether import get_weather_by_day
from .tasks.get_news import get_news
from .tasks.spotify import play_track_by_name, pause_music, next_track
from .tasks.wikipedia_search import search_and_display_wikipedia, get_wikipedia_summary
from .tasks.paper_search import search_papers

# .envファイルをロード
load_dotenv()

# 環境変数を取得
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY環境変数が設定されていません")
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

def load_task_definitions(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"タスク定義ファイルが見つかりません: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        print(f"タスク定義ファイルの形式が正しくありません: {e}")
        return {}

def build_prompt(task_definitions):
    base_prompt = """あなたはタスク判定器です。以下のタスク定義に基づいて、与えられた入力がどのタスクに該当するかを判定してください。
該当する場合は、タスク名と抽出された情報を JSON 形式で出力してください。

【タスク定義】
"""
    for task in task_definitions:
        task_text = f"タスク名: {task['task_name']}\n"
        task_text += f"  条件: " + "、".join(f"「{cond}」" for cond in task["conditions"]) + "\n"
        task_text += f"  抽出項目:\n"
        for field in task["fields"]:
            task_text += f"    - {field}\n"
        base_prompt += task_text + "\n"

    base_prompt += """
    【入力】
    {{ユーザーの入力}}

    【出力形式】
    タスクに該当する場合は以下の形式で返してください(statusは必ず"matched"にしてください):

    {
        "status": "matched",
        "task_name": タスク名,
        "fields": ["抽出項目（複数可）"]
    }

    タスクに該当しない場合は、以下のように返して下さい:

    {
        "status": "no_match"
    }
    """
    return base_prompt

task_definitions = load_task_definitions("src/LLM/task_definitions.json")
prompt = build_prompt(task_definitions)
# print(prompt)

chat_session = model.start_chat(history=[{"role":"user","parts":prompt}])

def extract_json_from_text(text):
    try:
        # 最初の { と 最後の } の間を抽出（最も単純で実用的）
        match = re.search(r'{.*}', text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        else:
            raise ValueError("JSON部分が見つかりませんでした")
    except json.JSONDecodeError as e:
        raise ValueError(f"JSONパースエラー: {e}")

def process_task_response(res_text, timer_callback=None):
    # 雑談用LLMが回答できるようにboolとテキスト(hint)を返す
    is_matched = False
    hint = ""  # デフォルト値を初期化
    
    try:
        result = extract_json_from_text(res_text)

        if result.get("status") == "matched":
            task_name = result.get("task_name")
            is_matched = True

            # 時刻確認
            if task_name == "check_time":
                from datetime import datetime
                print("現在時刻:", datetime.now().strftime("%H:%M:%S"))
                hint = "現在時刻は" + datetime.now().strftime("%H:%M:%S") + "です。"

            # 日付確認
            elif task_name == "check_date":
                from datetime import datetime
                print("今日の日付:", datetime.today().strftime("%Y-%m-%d"))
                hint = "今日の日付は" + datetime.today().strftime("%Y-%m-%d") + "です。"

            # タイマーをセット
            elif task_name == "set_timer":
                fields = result.get("fields")
                minutes = fields.get("time") or fields.get("時間")
                # print(type(minutes))
                minutes_float = float(minutes)
                seconds = minutes_float * 60

                import threading

                def timer_finished(minutes):
                    print(f"\n\n{minutes}分のタイマーが終了しました。\n\n")
                    if timer_callback:
                        timer_callback(minutes)

                timer = threading.Timer(seconds, timer_finished, args=[minutes_float])
                timer.start()
                print(f"{minutes}分のタイマーを受け付けました。")
                hint = f"あなたは今から{minutes}分のタイマーをセットします。こちらが指示するまでタイマーは終了させないでください。"

            # 天気予報
            elif task_name == "check_wether":
                fields = result.get("fields")
                date = fields.get("対象日")
                place = fields.get("対象地域")
                print(f"{date}の{place}の天気を取得します。")
                hint = get_weather_by_day(place, date)

            # ニュース記事の取得
            elif task_name == "get_news":
                fields = result.get("fields")
                country = fields.get("country")
                category = fields.get("category")
                print(f"{country}の{category}に関するニュース記事を取得します。")
                hint = get_news(country, category)

            # 曲名から再生指示
            elif task_name == "spotify_play_music":
                fields = result.get("fields")
                print(f"\nfields: {fields}\n")
                track = fields[0]

                print(f"「{track}」を再生します。")
                play_track_by_name(track)
                hint = f"{track}という曲を再生することをお知らせしてください。"

            # 再生中の音楽を一時停止
            elif task_name == "spotify_pause_music":
                print("Spotifyの音楽を停止します。")
                pause_music()
                hint = "再生中の音楽を停止したことをお知らせしてください。"

            # 次の曲を再生（挙動怪しい、、、）
            elif task_name == "spotify_next_track":
                print("次の曲を再生します。")
                next_track()
                hint = "次の曲を再生することをお知らせしてください。"

            # Wikipedia検索
            elif task_name == "wikipedia_search":
                fields = result.get("fields")
                query = fields[0]
                success, url = search_and_display_wikipedia(query)
                if success:
                    print(f"URL: {url}")
                    summary_success, summary = get_wikipedia_summary(query)
                    if summary_success:
                        print(f"要約:\n{summary}")
                        hint = summary # 要約をそのままhintとして渡す
                    else:
                        print("要約の取得に失敗しました。")
                        hint = f"{query}のwikipediaページを開きました。"
                else:
                    print(f"エラー:\n{url}")
                    hint = f"{query}の検索に失敗しました。"

            # 論文検索
            elif task_name == "paper_search":
                fields = result.get("fields")
                keyword = fields[0]
                summary = search_papers(keyword)
                hint = f"以下はあなたが論文検索で得た要約文です。\n{summary}\nあなたはこの論文について解説します。\n"

            else:
                is_matched = False
                hint = f"未知のタスク: {task_name}"
                print(f"未知のタスク: {task_name}")

        elif result.get("status") == "no_match":
            print("タスクには該当しませんでした。")
            return False, ""

    except ValueError as e:
        print("→ JSONのパースに失敗しました。")
        print(e)
        print("元の出力\n", res_text)
        is_matched = False
        hint = "JSONパースエラーが発生しました"
    except Exception as e:
        print("→ タスク処理中に予期しないエラーが発生しました。")
        print(f"エラー: {e}")
        is_matched = False
        hint = "タスク処理エラーが発生しました"

    return is_matched, hint

def task_classifier(user_input: str, timer_callback=None):
    response = chat_session.send_message(user_input)
    print(response.text)
    is_task_matched, hint = process_task_response(response.text, timer_callback)
    return is_task_matched, hint


if __name__ == "__main__":
    user_input = input("テキストを入力： ")
    is_matched, hint = task_classifier(user_input)
    print("AI:", hint)