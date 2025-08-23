import webview

# ウィンドウの作成
window = webview.create_window('AIMascotKit', 'http://localhost:8000/frontend/public/index.html',
                               transparent=True, 
                               width=1000, 
                               height=1400,
                               on_top=True)

webview.start()