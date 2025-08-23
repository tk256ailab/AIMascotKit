import subprocess

processes = []

try:
    # Local Server
    processes.append(subprocess.Popen(["python", "./frontend/local_server.py"]))
    # Flask Server
    processes.append(subprocess.Popen(["python", "./backend/src/vrm_control/vrm_flask_server.py"]))
    # Webview (UI)
    processes.append(subprocess.Popen(["python", "./frontend/transview.py"]))
    # AITuber System
    processes.append(subprocess.Popen(["python", "./backend/main.py"]))

    for p in processes:
        p.wait()

except KeyboardInterrupt:
    print("終了処理中...")
    for p in processes:
        p.terminate()
