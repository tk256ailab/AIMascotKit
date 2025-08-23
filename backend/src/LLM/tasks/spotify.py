import requests
import time
import base64
from dotenv import load_dotenv
import os
import urllib.parse

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")

# グローバル変数として初期化
access_token = None
access_token_expires_at = 0  # UNIXタイムスタンプ

def refresh_access_token():
    global access_token, access_token_expires_at
    
    if not CLIENT_ID or not CLIENT_SECRET or not REFRESH_TOKEN:
        raise ValueError("環境変数が設定されていません。CLIENT_ID, CLIENT_SECRET, REFRESH_TOKENを確認してください。")
    
    token_url = "https://accounts.spotify.com/api/token"

    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_str.encode('utf-8')
    auth_header = base64.b64encode(auth_bytes).decode('utf-8')

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }

    encoded_data = urllib.parse.urlencode(data)
    response = requests.post(token_url, headers=headers, data=encoded_data)

    print(f"Token refresh status: {response.status_code}")
    print(f"Response body: {response.text}")

    if response.status_code != 200:
        raise Exception(f"Token refresh failed: {response.status_code} - {response.text}")

    tokens = response.json()
    access_token = tokens["access_token"]
    expires_in = tokens.get("expires_in", 3600)
    access_token_expires_at = time.time() + expires_in - 60  # 60秒前に期限切れとして扱う

def get_headers():
    global access_token, access_token_expires_at
    
    # トークンが存在しないか、期限切れの場合は更新
    if access_token is None or time.time() > access_token_expires_at:
        print("アクセストークンを更新中...")
        refresh_access_token()
    
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

def get_available_devices():
    """利用可能なデバイス一覧を取得"""
    try:
        response = requests.get("https://api.spotify.com/v1/me/player/devices", headers=get_headers())
        if response.status_code == 200:
            return response.json().get("devices", [])
        else:
            return []
    except Exception as e:
        print(f"デバイス取得エラー: {e}")
        return []

def select_device(device_id):
    """指定したデバイスをアクティブにする"""
    try:
        data = {"device_ids": [device_id]}
        response = requests.put("https://api.spotify.com/v1/me/player", headers=get_headers(), json=data)
        return response.status_code == 204
    except Exception as e:
        print(f"デバイス選択エラー: {e}")
        return False

def ensure_active_device():
    """アクティブなデバイスが存在することを確認し、なければ設定"""
    devices = get_available_devices()
    
    if not devices:
        return False, "利用可能なデバイスがありません。Spotifyアプリを起動してください。"
    
    # アクティブなデバイスがあるかチェック
    active_device = next((d for d in devices if d.get("is_active")), None)
    
    if active_device:
        return True, f"アクティブデバイス: {active_device['name']}"
    
    # アクティブなデバイスがない場合、最初の利用可能なデバイスを選択
    first_device = devices[0]
    if select_device(first_device["id"]):
        return True, f"デバイスを選択しました: {first_device['name']}"
    else:
        return False, "デバイスの選択に失敗しました"

def play_music():
    try:
        # デバイスの確認と設定
        device_ok, device_msg = ensure_active_device()
        if not device_ok:
            return {"error": device_msg}
        
        response = requests.put("https://api.spotify.com/v1/me/player/play", headers=get_headers())
        if response.status_code == 204:
            return {"status": "success", "message": "音楽の再生を開始しました"}
        elif response.content:
            return response.json()
        else:
            return {"status": response.status_code}
    except Exception as e:
        return {"error": str(e)}

def pause_music():
    try:
        # デバイスの確認と設定
        device_ok, device_msg = ensure_active_device()
        if not device_ok:
            return {"error": device_msg}
            
        response = requests.put("https://api.spotify.com/v1/me/player/pause", headers=get_headers())
        if response.status_code == 204:
            return {"status": "success", "message": "音楽を一時停止しました"}
        elif response.content:
            return response.json()
        else:
            return {"status": response.status_code}
    except Exception as e:
        return {"error": str(e)}

def next_track():
    try:
        # デバイスの確認と設定
        device_ok, device_msg = ensure_active_device()
        if not device_ok:
            return {"error": device_msg}
            
        response = requests.post("https://api.spotify.com/v1/me/player/next", headers=get_headers())
        if response.status_code == 204:
            return {"status": "success", "message": "次の曲にスキップしました"}
        elif response.content:
            return response.json()
        else:
            return {"status": response.status_code}
    except Exception as e:
        return {"error": str(e)}

def play_track_by_name(track_name):
    try:
        # デバイスの確認と設定
        device_ok, device_msg = ensure_active_device()
        if not device_ok:
            return {"error": device_msg}
            
        # 楽曲を検索
        search_url = "https://api.spotify.com/v1/search"
        params = {"q": track_name, "type": "track", "limit": 1}
        res = requests.get(search_url, headers=get_headers(), params=params)

        if res.status_code != 200:
            return {"error": f"検索失敗: {res.status_code}"}

        tracks = res.json().get("tracks", {}).get("items", [])
        if not tracks:
            return {"error": "曲が見つかりません"}

        uri = tracks[0]["uri"]
        track_info = tracks[0]
        
        # 楽曲を再生
        play_url = "https://api.spotify.com/v1/me/player/play"
        res = requests.put(play_url, headers=get_headers(), json={"uris": [uri]})
        
        if res.status_code == 204:
            return {
                "status": "success", 
                "message": f"'{track_info['name']}' by {track_info['artists'][0]['name']} を再生開始"
            }
        elif res.content:
            return res.json()
        else:
            return {"status": res.status_code}
    except Exception as e:
        return {"error": str(e)}

def play_playlist_by_name(playlist_name):
    try:
        # デバイスの確認と設定
        device_ok, device_msg = ensure_active_device()
        if not device_ok:
            return {"error": device_msg}
            
        # プレイリストを検索
        search_url = "https://api.spotify.com/v1/search"
        params = {"q": playlist_name, "type": "playlist", "limit": 1}
        res = requests.get(search_url, headers=get_headers(), params=params)

        if res.status_code != 200:
            return {"error": f"検索失敗: {res.status_code}"}

        playlists = res.json().get("playlists", {}).get("items", [])
        if not playlists:
            return {"error": "プレイリストが見つかりません"}

        playlist_uri = playlists[0]["uri"]
        playlist_info = playlists[0]
        
        # プレイリストを再生
        play_url = "https://api.spotify.com/v1/me/player/play"
        res = requests.put(play_url, headers=get_headers(), json={"context_uri": playlist_uri})
        
        if res.status_code == 204:
            return {
                "status": "success", 
                "message": f"プレイリスト '{playlist_info['name']}' を再生開始"
            }
        elif res.content:
            return res.json()
        else:
            return {"status": res.status_code}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("=== Spotify API テスト開始 ===")
    
    # まず利用可能なデバイスを表示
    print("\n利用可能なデバイス:")
    devices = get_available_devices()
    if devices:
        for i, device in enumerate(devices):
            status = "🟢 アクティブ" if device.get("is_active") else "⚪ 非アクティブ"
            print(f"  {i+1}. {device['name']} ({device['type']}) - {status}")
    else:
        print("  利用可能なデバイスがありません")
        print("  Spotifyアプリを起動してから再実行してください")
        exit(1)
    
    print("\n=== 音楽制御テスト ===")
    
    try:
        print("1. 再生:", play_music())
        time.sleep(3)
        
        print("2. 停止:", pause_music())
        time.sleep(3)
        
        print("3. 次へ:", next_track())
        time.sleep(3)
        
        print("4. 曲指定:", play_track_by_name("Pretender"))
        time.sleep(3)
        
        print("5. プレイリスト指定:", play_playlist_by_name("お気に入り3"))
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    
    print("\n=== テスト終了 ===")