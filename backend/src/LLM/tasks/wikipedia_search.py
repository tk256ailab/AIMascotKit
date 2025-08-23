import wikipedia
import webbrowser
import sys
from typing import Optional, Tuple

def search_and_display_wikipedia(keyword: str, lang: str = 'ja', auto_open: bool = True) -> Tuple[bool, str]:
    """
    Wikipediaで検索してページを表示する関数
    
    Args:
        keyword (str): 検索キーワード
        lang (str): 言語設定 ('ja' for 日本語, 'en' for English)
        auto_open (bool): ブラウザで自動的に開くかどうか
    
    Returns:
        Tuple[bool, str]: (成功フラグ, メッセージまたはURL)
    """
    try:
        # Wikipedia言語設定
        wikipedia.set_lang(lang)
        
        # 検索実行
        print(f"'{keyword}'を検索しています...")
        
        # ページを取得
        page = wikipedia.page(keyword)
        
        # URLを取得
        url = page.url
        print(f"ページが見つかりました: {page.title}")
        print(f"URL: {url}")
        
        # ブラウザで開く
        if auto_open:
            webbrowser.open(url)
            print("ブラウザでページを開きました。")
        
        return True, url
        
    except wikipedia.exceptions.DisambiguationError as e:
        # 曖昧さ回避ページの場合
        print(f"複数の候補が見つかりました: {keyword}")
        print("候補:")
        for i, option in enumerate(e.options[:5], 1):  # 最初の5つを表示
            print(f"  {i}. {option}")
        
        # 最初の候補を自動選択
        try:
            page = wikipedia.page(e.options[0])
            url = page.url
            print(f"\n最初の候補を選択しました: {page.title}")
            print(f"URL: {url}")
            
            if auto_open:
                webbrowser.open(url)
                print("ブラウザでページを開きました。")
            
            return True, url
            
        except Exception as nested_e:
            error_msg = f"候補ページの取得に失敗しました: {str(nested_e)}"
            print(error_msg)
            return False, error_msg
    
    except wikipedia.exceptions.PageError:
        # ページが見つからない場合、類似検索を試行
        try:
            print(f"'{keyword}'のページが見つかりません。類似検索を実行中...")
            search_results = wikipedia.search(keyword, results=5)
            
            if search_results:
                print("類似するページ:")
                for i, result in enumerate(search_results, 1):
                    print(f"  {i}. {result}")
                
                # 最初の検索結果を選択
                page = wikipedia.page(search_results[0])
                url = page.url
                print(f"\n類似ページを選択しました: {page.title}")
                print(f"URL: {url}")
                
                if auto_open:
                    webbrowser.open(url)
                    print("ブラウザでページを開きました。")
                
                return True, url
            else:
                error_msg = f"'{keyword}'に関するページが見つかりませんでした。"
                print(error_msg)
                return False, error_msg
                
        except Exception as nested_e:
            error_msg = f"検索中にエラーが発生しました: {str(nested_e)}"
            print(error_msg)
            return False, error_msg
    
    except Exception as e:
        error_msg = f"予期しないエラーが発生しました: {str(e)}"
        print(error_msg)
        return False, error_msg

def get_wikipedia_summary(keyword: str, lang: str = 'ja', sentences: int = 3) -> Tuple[bool, str]:
    """
    Wikipediaの要約を取得する関数
    
    Args:
        keyword (str): 検索キーワード
        lang (str): 言語設定
        sentences (int): 要約の文数
    
    Returns:
        Tuple[bool, str]: (成功フラグ, 要約テキストまたはエラーメッセージ)
    """
    try:
        wikipedia.set_lang(lang)
        summary = wikipedia.summary(keyword, sentences=sentences)
        return True, summary
    except wikipedia.exceptions.DisambiguationError as e:
        try:
            summary = wikipedia.summary(e.options[0], sentences=sentences)
            return True, f"[{e.options[0]}の要約]\n{summary}"
        except:
            return False, f"複数の候補があります: {', '.join(e.options[:3])}..."
    except wikipedia.exceptions.PageError:
        return False, f"'{keyword}'のページが見つかりませんでした。"
    except Exception as e:
        return False, f"要約取得中にエラー: {str(e)}"

# テスト実行用のメイン関数
def main():
    """テスト実行用のメイン関数"""
    if len(sys.argv) > 1:
        keyword = ' '.join(sys.argv[1:])
    else:
        keyword = input("検索キーワードを入力してください: ")
    
    if not keyword.strip():
        print("キーワードが入力されていません。")
        return
    
    # Wikipedia検索・表示
    success, result = search_and_display_wikipedia(keyword)
    
    if success:
        print(f"\n=== 処理完了 ===")
        print(f"URL: {result}")
        
        # 要約も表示
        print(f"\n=== 要約 ===")
        summary_success, summary = get_wikipedia_summary(keyword)
        if summary_success:
            print(summary)
        else:
            print(f"要約取得失敗: {summary}")
    else:
        print(f"\n=== 処理失敗 ===")
        print(f"エラー: {result}")

if __name__ == "__main__":
    main()