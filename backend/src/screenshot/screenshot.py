import PIL.Image
import Quartz
import AppKit

#---スクショ---##################################################
def get_window_by_app_name(app_name):
    """指定したアプリ名のウィンドウを取得"""
    window_list = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)

    for window in window_list:
        owner_name = window.get("kCGWindowOwnerName", "")
        if app_name.lower() in owner_name.lower():
            return window  # 最初に見つかったウィンドウを返す
    return None

def capture_window(window_info, save_path="screenshot.png"):
    """ウィンドウ情報からスクリーンショットを撮影"""
    if not window_info:
        print("指定したアプリのウィンドウが見つかりません。")
        return False

    window_id = window_info["kCGWindowNumber"]
    image = Quartz.CGWindowListCreateImage(
        Quartz.CGRectNull,
        Quartz.kCGWindowListOptionIncludingWindow,
        window_id,
        Quartz.kCGWindowImageBoundsIgnoreFraming
    )

    if not image:
        print("スクリーンショットの取得に失敗しました。")
        return False

    # Quartz の画像を PIL に変換
    bitmap = AppKit.NSBitmapImageRep.alloc().initWithCGImage_(image)
    png_data = bitmap.representationUsingType_properties_(AppKit.NSPNGFileType, None)
    
    with open(save_path, "wb") as f:
        f.write(png_data.bytes())

    print(f"スクリーンショットを保存しました: {save_path}")
    return True
###############################################################

if __name__ == "__main__":
    app_name = "Google Chrome"
    window_info = get_window_by_app_name(app_name)
    capture_window(window_info) #スクショの保存
    image = PIL.Image.open("screenshot.png")