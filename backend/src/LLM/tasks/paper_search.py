import requests
import xml.etree.ElementTree as ET
from openai import OpenAI
import re
from typing import List, Dict, Optional
import time
import webbrowser
import random

def search_and_summarize_papers(
    keyword: str, 
    max_results: int = 5,
    openai_api_key: Optional[str] = None,
    lang: str = "ja"
) -> Dict[str, List[str]]:
    """
    キーワードを使って論文を検索し、要約を生成する関数
    
    Args:
        keyword (str): 検索キーワード
        max_results (int): 取得する論文の最大数（デフォルト: 5）
        openai_api_key (str, optional): OpenAI APIキー
        lang (str): 要約の言語（"ja": 日本語, "en": 英語）
    
    Returns:
        Dict[str, List[str]]: 検索結果と要約のリスト
    """
    
    def search_arxiv_papers(keyword: str, max_results: int) -> List[Dict]:
        """arXiv APIを使用して論文を検索"""
        # arXiv API URL
        base_url = "http://export.arxiv.org/api/query"
        
        # 検索クエリの作成
        query = f"search_query=all:{keyword}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
        url = f"{base_url}?{query}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # XMLをパース
            root = ET.fromstring(response.content)
            
            papers = []
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
                
                # 著者情報の取得
                authors = []
                for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
                    name = author.find('{http://www.w3.org/2005/Atom}name').text
                    authors.append(name)
                
                # 公開日の取得
                published = entry.find('{http://www.w3.org/2005/Atom}published').text
                
                # arXiv IDとURLの取得
                arxiv_url = entry.find('{http://www.w3.org/2005/Atom}id').text
                arxiv_id = arxiv_url.split('/')[-1]
                
                # PDF URLの生成
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                
                papers.append({
                    'title': title,
                    'summary': summary,
                    'authors': authors,
                    'published': published[:10],  # 日付部分のみ
                    'arxiv_id': arxiv_id,
                    'url': arxiv_url,
                    'pdf_url': pdf_url
                })
                
            return papers
            
        except requests.RequestException as e:
            print(f"論文検索中にエラーが発生しました: {e}")
            return []
        except ET.ParseError as e:
            print(f"XMLパース中にエラーが発生しました: {e}")
            return []
    
    def clean_text(text: str) -> str:
        """テキストのクリーニング"""
        # 改行や余分な空白を削除
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def summarize_with_openai(text: str, openai_api_key: str, lang: str) -> str:
        """OpenAI APIを使用してテキストを要約"""
        try:
            client = OpenAI(api_key=openai_api_key)
            
            prompt = {
                "ja": f"以下の論文の要約を日本語で3-4文にまとめてください。専門用語は適切に日本語に翻訳し、重要なポイントを含めてください:\n\n{text}",
                "en": f"Please summarize the following paper abstract in 3-4 sentences, highlighting the key points:\n\n{text}"
            }
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant that summarizes academic papers."},
                    {"role": "user", "content": prompt[lang]}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"要約生成中にエラーが発生しました: {e}"
    
    def simple_summarize(text: str, lang: str) -> str:
        """シンプルな要約（OpenAI APIが使用できない場合）"""
        sentences = re.split(r'[.!?]+', text)
        # 最初の5文を取得
        summary_sentences = sentences[:5]
        summary = '. '.join(s.strip() for s in summary_sentences if s.strip())
        
        if lang == "ja":
            return f"[自動要約] {summary}..."
        else:
            return f"[Auto Summary] {summary}..."
    
    # メイン処理
    print(f"キーワード '{keyword}' で論文を検索中...")
    papers = search_arxiv_papers(keyword, max_results)
    
    if not papers:
        return {"error": ["論文が見つかりませんでした。"]}
    
    results = {
        "summaries": [],
        "details": []
    }
    
    ai_summaries = []
    pdf_urls = []
    for i, paper in enumerate(papers, 1):
        print(f"論文 {i}/{len(papers)} を処理中...")
        
        # タイトルと基本情報
        title = clean_text(paper['title'])
        summary_text = clean_text(paper['summary'])
        authors_str = ", ".join(paper['authors'][:3])  # 最初の3人の著者
        if len(paper['authors']) > 3:
            authors_str += " et al."
        
        # 要約生成
        if openai_api_key:
            ai_summary = summarize_with_openai(summary_text, openai_api_key, lang)
        else:
            ai_summary = simple_summarize(summary_text, lang)

        ai_summaries.append(ai_summary)
        pdf_urls.append(paper["pdf_url"])
        
        # 結果の整理
        if lang == "ja":
            formatted_result = f"""
【論文 {i}】
タイトル: {title}
著者: {authors_str}
発表日: {paper['published']}
arXiv ID: {paper['arxiv_id']}
論文URL: {paper['url']}
PDF URL: {paper['pdf_url']}

要約: {ai_summary}
"""
        else:
            formatted_result = f"""
【Paper {i}】
Title: {title}
Authors: {authors_str}
Published: {paper['published']}
arXiv ID: {paper['arxiv_id']}
Paper URL: {paper['url']}
PDF URL: {paper['pdf_url']}

Summary: {ai_summary}
"""
        
        results["summaries"].append(formatted_result.strip())
        results["details"].append(paper)
        
        # API制限を考慮して少し待機
        if openai_api_key:
            time.sleep(1)
    
    return results, ai_summaries, pdf_urls

def search_papers(keyword, auto_open=True):
    results, summaries, pdf_urls = search_and_summarize_papers(keyword, max_results=5)

    if "error" in results:
        print("エラー:", results["error"][0])
        return "論文検索でエラーが発生しました。"
    else:
        random_idx = random.randint(0, 4)
        summary = summaries[random_idx]
        url = pdf_urls[random_idx]
        print(f"\n=== '{keyword}' に関する論文検索結果 ===\n")
        print(summary)

        # ブラウザで開く
        if auto_open:
            webbrowser.open(url)
            print("ブラウザでページを開きました。")

        return summary

# 使用例
if __name__ == "__main__":
    # 基本的な使用方法
    keyword = "deep learning"
    
    # OpenAI APIキーを設定する場合（推奨）
    # api_key = "your-openai-api-key-here"
    # results = search_and_summarize_papers(keyword, max_results=3, openai_api_key=api_key)
    
    # OpenAI APIキーなしで使用する場合
    results, _, _ = search_and_summarize_papers(keyword, max_results=5)
    
    if "error" in results:
        print("エラー:", results["error"][0])
    else:
        print(f"\n=== '{keyword}' に関する論文検索結果 ===\n")
        for summary in results["summaries"]:
            print(summary)
            print("-" * 80)