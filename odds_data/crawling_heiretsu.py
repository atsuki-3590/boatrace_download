# -*- coding: UTF-8 -*-
import requests
import time
import os
from datetime import datetime as dt
from datetime import timedelta as td
from bs4 import BeautifulSoup 
import concurrent.futures

print("オッズデータのクローニングを開始します")

# レース払い戻しデータスクレイピング
# 開始日と終了日を指定(YYYY-MM-DD)
START_DATE = "2024-01-01"
END_DATE = "2024-01-10"

# ファイルの保存先を指定
SAVE_DIR = "odds_data/オッズ_HTML"
if not os.path.exists(SAVE_DIR):
    print("ディレクトリを作成します")
    os.makedirs(SAVE_DIR)

# 日付範囲を設定
start_date = dt.strptime(START_DATE, '%Y-%m-%d')
end_date = dt.strptime(END_DATE, '%Y-%m-%d')

# URLのベース
base_url = "https://www.boatrace.jp/owpc/pc/race/odds3f"

# ページの内容に基づいてクローリングするかどうかを判断する関数
def should_crawl(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    if soup.find(string="データがありません。"):
        return False
    return True

# rnoとjcdの範囲を設定
rno_range = range(1, 13)  # rnoは1から12
jcd_range = range(1, 25)  # jcdは1から24

# クローリング処理を実行する関数
def crawl(date_str, rno, jcd):
    url = f"{base_url}?rno={rno}&jcd={jcd:02d}&hd={date_str}"
    response = requests.get(url)
    time.sleep(1)  # リクエスト間の間隔を1秒に設定

    if response.status_code == 200:
        page_content = response.content
        if should_crawl(page_content):
            file_path = f"{SAVE_DIR}/{date_str}_{jcd:02d}_{rno:02d}R.html"
            if not os.path.exists(file_path):
                print(f"Crawling {url}")
                response.encoding = response.apparent_encoding
                bs = BeautifulSoup(response.text, 'html.parser')
                # データの保存
                with open(file_path, 'w', encoding='UTF-8') as file:
                    file.write(response.text)
                print(f"{file_path}のデータを保存しました")
            else:
                print(f"File already exists, skipping {file_path}")
        else:
            print(f"Skipping {url}")
    else:
        print(f"Failed to retrieve {url}")

# 並列処理を使用してクローリング
def parallel_crawling(start_date, end_date):
    tasks = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y%m%d')
        for jcd in range(1, 25):
            for rno in range(1, 13):
                tasks.append((date_str, rno, jcd))
        current_date += td(days=1)

    with Pool(processes=10) as pool:
        try:
            pool.map(crawl, tasks)
        except KeyboardInterrupt:
            print("クローリングを中断しました")
            pool.terminate()
            pool.join()

if __name__ == "__main__":
    parallel_crawling(start_date, end_date)
    print("クローニングを完了しました")