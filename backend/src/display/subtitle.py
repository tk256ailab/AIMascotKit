import requests

def update_subtitle(text):
    url = "http://127.0.0.1:5000/subtitle"
    res = requests.post(url, json={"text": text})
    if res.status_code == 200:
        print("[OK] 字幕送信:", text)
    else:
        print("[ERROR]", res.status_code, res.text)
