import re
from bs4 import BeautifulSoup
from datetime import datetime
import os

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
    global exchange_rates

    # 環境変数からURLを取得、なければデフォルト値を使用
    exchange_rate_url = os.environ.get("EXCHANGE_RATE_URL", "https://www.77bank.co.jp/kawase/usd2024.html")
    
    if not sample_html:
        print(f"Getting rate html from: {exchange_rate_url}")
        try:
            r = requests.get(exchange_rate_url)
            r.raise_for_status()  # エラーレスポンス（4xx or 5xx）をチェック
            sample_html = r.content
        except requests.exceptions.RequestException as e:
            print(f"Error fetching exchange rate data: {e}")
            return  # エラーが発生した場合は処理を中断

    # BeautifulSoupでHTML解析
    soup = BeautifulSoup(sample_html, 'html.parser')
    
    # テーブルを検索
    table = soup.find('table')
    if not table:
        raise Exception("テーブルが見つかりませんでした")
    
    # 月の行を取得
    months = [th.text.strip() for th in table.find('tr').find_all('th')[1:]]  # 最初の"日付"列をスキップ
    
    # URLから年を抽出
    match = re.search(r"usd(\d{4})", exchange_rate_url)
    if match:
        year = int(match.group(1))
    else:
        print("Warning: Could not determine year from URL. Assuming current year.")
        year = datetime.now().year

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
                date_key = f"{year}{str(month_idx + 1).zfill(2)}{day}"
                
                # 為替レートを保存
                exchange_rates[date_key] = rate
            except ValueError:
                continue

def convert_date_format(date_str):
    """Converts a date string from "dd-m-yyyy" to "dd-mmm-yyyy" format.

    Args:
        date_str: The date string in "dd-m-yyyy" or "dd-mmm-yyyy" format.

    Returns:
        The date string in "dd-mmm-yyyy" format if the input is "dd-m-yyyy",
         otherwise returns the original input string. Returns None if the input is invalid.
    """
    try:
        # First, try parsing with the target format. If successful, no conversion is needed.
        datetime.strptime(date_str, '%d-%b-%Y')
        return date_str  # Return original string if already in correct format
    except ValueError:
        try:
            # If the target format fails, try parsing with the source format and convert.
             date_obj = datetime.strptime(date_str, '%d-%m-%Y')
             return date_obj.strftime('%d-%b-%Y')
        except ValueError:
            return None

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
