"""
VRM制御用Flask APIサーバー
Live2D制御サーバーと同じシンプルな仕組み
"""

import logging
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 状態管理用
current_emotion = None
current_expression = None
current_voice = False
latest_subtitle = {"japanese": "", "english": "", "timestamp": 0}
mood_value = 50

@app.route('/vrm/motion', methods=['GET'])
def get_motion():
    """クライアントが定期取得"""
    global current_emotion
    if current_emotion:
        emotion = current_emotion
        current_emotion = None
        return jsonify({'emotion': emotion})
    return jsonify({'emotion': None})

@app.route('/vrm/motion', methods=['POST'])
def set_motion():
    """感情/モーションを設定"""
    global current_emotion
    data = request.get_json()
    emotion = data.get('emotion')
    if emotion:
        current_emotion = emotion
        print(f"[VRM Flask] 感情設定: {emotion}")
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error', 'message': 'emotion not provided'}), 400

@app.route('/expression', methods=['GET'])
def get_expression():
    """クライアントが表情を定期取得"""
    global current_expression
    if current_expression:
        expression = current_expression
        current_expression = None
        return jsonify({'expression': expression})
    return jsonify({'expression': None})

@app.route('/expression', methods=['POST'])
def set_expression():
    """表情を設定"""
    global current_expression
    data = request.get_json()
    expression = data.get('expression')
    if expression:
        current_expression = expression
        print(f"[VRM Flask] 表情設定: {expression}")
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error', 'message': 'expression not provided'}), 400

@app.route('/voice', methods=['GET'])
def get_voice():
    """音声再生状態を取得"""
    global current_voice
    if current_voice:
        current_voice = False
        return jsonify({'play': True})
    return jsonify({'play': False})

@app.route('/voice', methods=['POST'])
def set_voice():
    """音声再生を設定"""
    global current_voice
    current_voice = True
    print("[VRM Flask] 音声再生設定")
    return jsonify({'status': 'ok'})

@app.route('/subtitle', methods=['GET'])
def get_subtitle():
    """字幕を取得"""
    return jsonify(latest_subtitle)

@app.route('/subtitle', methods=['POST'])
def set_subtitle():
    """字幕を設定"""
    global latest_subtitle
    data = request.get_json()
    japanese = data.get('japanese', '')
    english = data.get('english', '')
    
    if japanese is not None or english is not None:
        import time
        latest_subtitle = {
            "japanese": japanese,
            "english": english,
            "timestamp": time.time()
        }
        print(f"[VRM Flask] 字幕設定: {japanese}")
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error', 'message': 'japanese or english text not provided'}), 400

@app.route('/mood', methods=['GET'])
def get_mood_value():
    """ご機嫌度を取得"""
    return jsonify({'mood': mood_value})

@app.route('/mood', methods=['POST'])
def set_mood_value():
    """ご機嫌度を設定"""
    global mood_value
    data = request.get_json()
    mood = data.get('mood_value') or data.get('mood')
    if isinstance(mood, (int, float)):
        mood_value = max(0, min(100, mood))  # 0-100の範囲に制限
        print(f"[VRM Flask] ご機嫌度設定: {mood_value}")
        return jsonify({'status': 'ok', 'new_mood': mood_value})
    return jsonify({'status': 'error', 'message': 'Valid numeric mood value not provided'}), 400

@app.route('/', methods=['GET'])
def health_check():
    """ヘルスチェック"""
    return jsonify({'status': 'ok', 'service': 'VRM Control Server'})

@app.route('/api/vrm/status', methods=['GET'])
def get_status():
    """システム状態取得"""
    return jsonify({
        'status': 'ok',
        'service': 'VRM Control Server',
        'current_emotion': current_emotion,
        'current_expression': current_expression,
        'mood_value': mood_value,
        'subtitle': latest_subtitle
    })

# API v1 エンドポイント（互換性のため）
@app.route('/api/vrm/expression', methods=['POST'])
def api_set_expression():
    """API v1: 表情設定"""
    return set_expression()

@app.route('/api/vrm/mood', methods=['POST'])
def api_set_mood():
    """API v1: ご機嫌度設定"""
    return set_mood_value()

@app.route('/api/vrm/subtitle', methods=['GET'])
def api_get_subtitle():
    """API v1: 字幕取得"""
    return get_subtitle()

@app.route('/api/vrm/subtitle', methods=['POST'])
def api_set_subtitle():
    """API v1: 字幕設定"""
    return set_subtitle()

if __name__ == '__main__':
    print("VRM Flask APIサーバーを起動中...")
    print("利用可能なエンドポイント:")
    print("  GET  / - ヘルスチェック")
    print("  GET  /api/vrm/status - システム状態")
    print("  POST /vrm/motion - 感情/モーション設定")
    print("  GET  /vrm/motion - 感情/モーション取得")
    print("  POST /expression - 表情設定")
    print("  GET  /expression - 表情取得")
    print("  POST /voice - 音声再生設定")
    print("  GET  /voice - 音声再生取得")
    print("  POST /subtitle - 字幕設定")
    print("  GET  /subtitle - 字幕取得")
    print("  POST /mood - ご機嫌度設定")
    print("  GET  /mood - ご機嫌度取得")
    print("  POST /api/vrm/* - API v1エンドポイント")
    # 明示的に 127.0.0.1:5000 で起動（VRMControllerと整合）

    # --- 起動後のアクセスログを消す ---
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)  # INFO 以下は表示されない

    app.run(host="127.0.0.1", port=5000, debug=False)