import PIL.Image
import Quartz
import AppKit

#--- 選択中のウィンドウを取得 ---#
def get_frontmost_window_info():
    """最前面のウィンドウ情報を取得"""
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

    for window in window_list:
        title = window.get("kCGWindowName", "")
        layer = window.get("kCGWindowLayer", 0)
        if title and layer == 0:
            return window  # 最前面の通常ウィンドウ
    return None

#--- スクショ取得 ---#
def capture_window(window_info, save_path="screenshot.png"):
    """ウィンドウ情報からスクリーンショットを撮影"""
    if not window_info:
        print("選択中のウィンドウが見つかりません。")
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

#--- 実行 ---#
if __name__ == "__main__":
    window_info = get_frontmost_window_info()
    capture_window(window_info)
    image = PIL.Image.open("screenshot.png")
    image.show()
