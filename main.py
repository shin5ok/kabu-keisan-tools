import csv
from datetime import datetime
from io import StringIO

import utils

def calculate_total_value(data_str):
    # 入力データをCSV形式で読み込むための準備
    csv_data = StringIO(data_str)
    reader = csv.DictReader(csv_data)
    
    total_jpy = 0
    details = []
    
    # 各行のデータを処理
    for row in reader:

        if 'Date' in row:
            date_str = row['Date']
        elif 'Vest Date' in row:
            date_str = row['Vest Date']

        date_str = utils.convert_date_format(date_str)

        quantity = float(row['Quantity'])
        price_usd = float(row['Price'].replace('$', ''))
        
        try:
            # 日付をパースして為替レート検索用のキーを作成
            date = datetime.strptime(date_str, '%d-%b-%Y')
            rate_key = date.strftime('%Y%m%d')
        
            # 為替レートを取得
            exchange_rates = utils.get_exchange_rate(rate_key)
            if exchange_rates:
                rate = exchange_rates

                # 計算
                value_usd = price_usd * quantity
                value_jpy = value_usd * rate
                calcurate = (f"USD: {price_usd} * Quantity: {quantity}, Total USD: {value_usd} * JPY Rate/USD: {rate}")


                # 結果を保存
                details.append({
                    'date': date_str,
                    'quantity': quantity,
                    'price_usd': price_usd,
                    'rate': rate,
                    'value_jpy': value_jpy,
                    'calcurate' : calcurate,
                })

                total_jpy += value_jpy
        except:
            pass
    
    # 結果を表示
    print("=== 株のVest詳細 ===")
    for detail in details:
        print(f"日付: {detail['date']}")
        print(f"数量: {detail['quantity']:.3f}株")
        print(f"価格: ${detail['price_usd']:.2f}")
        print(f"為替レート: ¥{detail['rate']:.2f}")
        print(f"日本円換算: ¥{detail['value_jpy']:,.2f}")
        print(f"計算式: {detail['calcurate']}")
        print("-" * 40)
    
    print(f"\n総額: ¥{total_jpy:,.2f}(実数: {total_jpy})")

# 標準入力からデータを読み込む
import sys
input_data = sys.stdin.read()

# 計算を実行
calculate_total_value(input_data)