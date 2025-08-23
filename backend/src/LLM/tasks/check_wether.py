import requests

CITY_ID_MAP = {
    "札幌": "016010",
    "仙台": "040010",
    "東京": "130010",
    "横浜": "140010",
    "名古屋": "230010",
    "大阪": "270000",
    "広島": "340010",
    "福岡": "400010",
    "那覇": "471010"
}

def get_weather_by_day(city_name: str, day_label: str):
    if city_name not in CITY_ID_MAP:
        return f"{city_name}の天気情報は得られませんでした。"

    city_id = CITY_ID_MAP[city_name]
    url = f"https://weather.tsukumijima.net/api/forecast?city={city_id}"
    headers = {"User-Agent": "MyWeatherApp/1.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        text = f"【{data['title']}】\n"
        text += f"発表日時: {data['publicTimeFormatted']}\n"
        text += f"発表機関: {data['publishingOffice']}\n"
        text += "=" * 30 + "\n"

        forecast_text = ""
        for forecast in data["forecasts"]:
            if forecast.get("dateLabel") == day_label:
                date = forecast.get("date", "不明")
                weather = forecast.get("telop", "不明")
                min_temp = forecast["temperature"]["min"]["celsius"] if forecast["temperature"]["min"] else "N/A"
                max_temp = forecast["temperature"]["max"]["celsius"] if forecast["temperature"]["max"] else "N/A"

                forecast_text += f"\n■ {day_label}（{date}）の天気 in {city_name}:\n"
                forecast_text += f"天気: {weather}\n"
                forecast_text += f"最低気温: {min_temp}℃\n"
                forecast_text += f"最高気温: {max_temp}℃\n"

                # 降水確率（時間帯ごと）
                chance_of_rain = forecast.get("chanceOfRain")
                if chance_of_rain:
                    forecast_text += "\n降水確率:\n"
                    for time_range, percent in chance_of_rain.items():
                        forecast_text += f"  {time_range}: {percent}\n"

                # アドバイスの追加
                advice = get_weather_advice(weather, min_temp, max_temp)
                forecast_text += f"\n服装アドバイス: {advice}\n"
                break

        if not forecast_text:
            return f"{day_label}の天気情報は得られませんでした。"

        # 概況文
        desc = data.get("description", {})
        text += forecast_text
        text += "\n■ 天気概況:\n"
        text += "【" + desc.get("headlineText", "見出しなし") + "】\n"
        text += desc.get("bodyText", "概況本文なし")

        print(text)
        return text

    except requests.exceptions.RequestException as e:
        return f"天気情報の取得中にエラーが発生しました: {e}"

def get_weather_advice(weather: str, min_temp: str, max_temp: str) -> str:
    advice = ""

    # 天気ベースのアドバイス
    if "雨" in weather:
        advice += "傘を忘れずに。濡れても大丈夫な靴を選びましょう。"
    elif "雪" in weather:
        advice += "滑りやすいので足元注意、防寒対策も万全に。"
    elif "晴" in weather:
        advice += "日差しが強いかも。日焼け止めや帽子を活用して。"
    elif "曇" in weather:
        advice += "念のため折りたたみ傘があると安心です。"
    else:
        advice += "天候が変わりやすい可能性があります。注意して過ごしましょう。"

    # 気温ベースのアドバイス
    try:
        min_temp = float(min_temp) if min_temp != "N/A" else None
        max_temp = float(max_temp) if max_temp != "N/A" else None

        if max_temp is not None:
            if max_temp >= 30:
                advice += " 熱中症に注意！通気性の良い服を着ましょう。"
            elif max_temp >= 25:
                advice += " 少し暑く感じるかもしれません。半袖でOKです。"
            elif max_temp < 15:
                advice += " 少し肌寒いです。上着を忘れずに。"
        elif min_temp is not None and min_temp < 5:
            advice += " 朝晩は特に冷え込みます。防寒対策を。"

    except ValueError:
        pass

    return advice.strip()

if __name__ == "__main__":
    text = get_weather_by_day("東京", "明日")
    print(text)
