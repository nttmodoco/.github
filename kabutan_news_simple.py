
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from datetime import datetime

BASE_URL = "https://kabutan.jp/news/marketnews/"

# 🌟 海外サーバーからの拒否を減らすため、ヘッダー情報を本物のブラウザに近づけて強化
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache'
}

def get_articles_list():
    """記事一覧を取得"""
    try:
        response = requests.get(BASE_URL, headers=HEADERS, timeout=15) # タイムアウトを少し長めに
        response.encoding = 'utf-8'
        
        # もし拒否されたら、エラーを発生させてGitHubのログに理由を残す
        if response.status_code != 200:
            raise Exception(f"サイトへのアクセスが拒否されました (ステータスコード: {response.status_code})")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        
        # 株探の現在のHTML構造に合わせたセレクタ（s_news_list）
        news_table = soup.find('table', class_='s_news_list mgbt0')
        if news_table:
            article_links = news_table.find_all('a')
        else:
            article_links = []
        
        if not article_links:
            news_container = soup.find('div', class_='news-list')
            if news_container:
                article_links = news_container.find_all('a')
        
        print(f"見つかった記事リンク: {len(article_links)}件")
        
        for link in article_links[:5]:  # 最新5件
            title = link.get_text(strip=True)
            href = link.get('href', '')
            url = urljoin(BASE_URL, href)
            
            # リンクテキストが空、またはJavaScriptのリンクは除外
            if not title or href.startswith('javascript:'):
                continue
                
            articles.append({
                'title': title,
                'url': url,
                'fetched_at': datetime.now().isoformat()
            })
        
        return articles
    
    except Exception as e:
        print(f"記事一覧取得エラー: {str(e)}")
        raise e # エラーを上に投げて、Actionsを確実に失敗させてログを見やすくする

def get_article_body(url):
    """記事の本体テキストを取得"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            return "本文取得失敗（アクセス拒否）"
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        body = (soup.find('div', class_='article-body') or
                soup.find('article') or
                soup.find('div', class_='main-content'))
        
        if body:
            text = body.get_text(strip=True)
            return text[:1000]
        
        return "本文の枠組み（セレクタ）が見つかりません"
    
    except Exception as e:
        print(f"記事詳細取得エラー: {str(e)}")
        return None

def main():
    """メイン処理"""
    print("株探ニュース取得中...\n")
    
    articles = get_articles_list()
    
    if not articles:
        print("有効な記事が1件も見つかりませんでした。")
        return
    
    for i, article in enumerate(articles, 1):
        print(f"\n【{i}】 {article['title']}")
        print(f"URL: {article['url']}")
        
        body = get_article_body(article['url'])
        if body:
            print(f"本体: {body[:100]}...\n")
            article['body'] = body
    
    # JSONファイルに保存
    with open('articles_simple.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ {len(articles)}件の記事情報を articles_simple.json に保存しました")

if __name__ == "__main__":
    main()
