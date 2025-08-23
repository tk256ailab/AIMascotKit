from dotenv import load_dotenv
import os
import requests
import random

# .envファイルをロード
load_dotenv()

# 環境変数を取得
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

url = "https://newsapi.org/v2/top-headlines"

country_name_to_code = {
    "日本": "jp",
    "アメリカ": "us",
    "中国": "cn",
    "韓国": "kr"
}

def get_news(country_name, category):
    country_code = country_name_to_code.get(country_name)

    params = {
        "country": f"{country_code}",
        "category": f"{category}",
        "pageSize": 10,
        "apiKey": NEWS_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] == "ok":
        articles = data["articles"]
        if articles:
            article = random.choice(articles)
            title = article["title"]
            description = article["description"]
            content = article["content"]
            print("タイトル:", title)
            print("概要:", description)
            print("本文:", content)
            hint = f"以下のニュースを取得しました。これを少し詳しく紹介してください：\nタイトル: {title}\n概要: {description}\n本文:\n{content}\n"
    else:
        print("ニュースを取得できませんでした。\n", data)
        hint = "要望のニュースは見つかりませんでした。"

    return hint

if __name__ == "__main__":
    hint = get_news("アメリカ", "technology")
    print(hint)