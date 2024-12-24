import re
from bs4 import BeautifulSoup
from datetime import datetime

import requests

# グローバル変数として為替レートを保存
exchange_rates = {}
sample_html = ""

def initialize_exchange_rates():
    """
    HTMLコンテンツから為替レートを解析し、グローバル変数に保存する
    
    Args:
        html_content (str): 解析対象のHTML文字列
    """

    global sample_html
    if not sample_html:
        print("Getting rate html")
        r = requests.get("https://www.77bank.co.jp/kawase/usd2024.html")
        sample_html = r.content
    
    global exchange_rates
    
    # BeautifulSoupでHTML解析
    soup = BeautifulSoup(sample_html, 'html.parser')
    
    # テーブルを検索
    table = soup.find('table')
    if not table:
        raise Exception("テーブルが見つかりませんでした")
    
    # 月の行を取得
    months = [th.text.strip() for th in table.find('tr').find_all('th')[1:]]  # 最初の"日付"列をスキップ
    
    # 各行のデータを処理
    for row in table.find_all('tr')[1:]:  # ヘッダー行をスキップ
        # 日付の列を取得
        day = row.find('th')
        if not day or not day.text.strip().isdigit():
            continue
        
        day = day.text.strip().zfill(2)  # 1桁の日付を2桁に
        
        # 各月のデータを処理
        cells = row.find_all('td')
        for month_idx, cell in enumerate(cells):
            if not cell.text.strip() or cell.text.strip() == '\xa0':  # 空のセルをスキップ
                continue
                
            # コメント内の日付を取得
            comment = cell.get('class', [''])[0]  # classを取得
            
            try:
                # テキストから為替レートを取得
                rate = float(cell.text.strip())
                
                # 日付を生成 (YYYYMMDD形式)
                date_key = f"2024{str(month_idx + 1).zfill(2)}{day}"
                
                # 為替レートを保存
                exchange_rates[date_key] = rate
            except ValueError:
                continue

def get_exchange_rate(date_str):
    """
    指定された日付の為替レート（仲値）を取得する
    
    Args:
        date_str (str): YYYYMMDD形式の日付文字列 (例: "20240104")
    
    Returns:
        float: 為替レート。データが存在しない場合はNone
    """
    initialize_exchange_rates()
    global exchange_rates
    return exchange_rates.get(date_str)

# 使用例
if __name__ == "__main__":
    # 初期化
    initialize_exchange_rates()
    
    # データ確認
    print("取得した為替レートデータ:")
    for date, rate in sorted(exchange_rates.items()):
        print(f"{date}: {rate}")
    
    # 特定の日付の為替レート取得例
    import sys
    test_date = sys.argv[1]
    rate = get_exchange_rate(test_date)
    if rate:
        print(f"\n{test_date}の為替レート: {rate}")
    else:
        print(f"\n{test_date}の為替レートは見つかりませんでした")