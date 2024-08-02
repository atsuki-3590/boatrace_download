# -*- coding: UTF-8 -*-
import requests
import time
import os
from datetime import datetime as dt
from datetime import timedelta as td
from bs4 import BeautifulSoup 
import pandas as pd

print("オッズデータのクローニングを開始します")

# レース払い戻しデータスクレイピング
# 開始日と終了日を指定(YYYY-MM-DD)
START_DATE = "2024-01-01"
END_DATE = "2024-01-02"

# ファイルの保存先を指定　※コラボでGoogleドライブをマウントした状態を想定
SAVE_DIR = "odds_data/オッズ_HTML"
if not os.path.exists(SAVE_DIR):
    print("ディレクトリを作成します")
    os.makedirs(SAVE_DIR)

# for i in range(1,25)
#     DIR_by_Boatrace_course = f"odds_data/オッズ_HTML/jcd_{i}"
#     if not os.path.exists(DIR_by_Boatrace_course):
#         print(f"jcd={i}のディレクトリを作成します")
#         os.makedirs(SAVE_DIR)


# リクエスト間隔を指定(秒)　※サーバに負荷をかけないよう3秒以上を推奨
INTERVAL = 3



start_date = dt.strptime(START_DATE, '%Y-%m-%d')
end_date = dt.strptime(END_DATE, '%Y-%m-%d')


# URLのベース
base_url = "https://www.boatrace.jp/owpc/pc/race/odds3f"
# odds3t:3連単、odds3f:3連複、odds2tf:2連単・2連複、oddsk:拡連複、oddstf:単勝・複勝

# ページの内容に基づいてクローリングするかどうかを判断する関数
def should_crawl(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    if soup.find(string="データがありません。"):
        return False
    return True

# rnoとjcdの範囲を設定
rno_range = range(1, 13)  # rnoは1から12
jcd_range = range(1, 25)  # jcdは1から24

# 日付をループしてクローリング
current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime('%Y%m%d')
    for jcd in jcd_range:
        for rno in rno_range:
            url = f"{base_url}?rno={rno}&jcd={jcd:02d}&hd={date_str}"
            response = requests.get(url)
            
            if response.status_code == 200:
                page_content = response.content
                if should_crawl(page_content):
                    file_path = f"{SAVE_DIR}/{date_str}_jcd{jcd:02d}_{rno:02d}R.html"
                    if not os.path.exists(file_path):
                        print(f"Crawling {url}")
                        time.sleep(1)
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
            # time.sleep(2)
    print(f"{current_date.strftime('%Y-%m-%d')}のデータを保存しました")
    current_date += td(days=1)

print("クローニングを完了しました")



# # 年ごとの日程に関するHTMLを取得
# for i in range(year_dif):
#     current_year = START_YEAR + i
#     if not os.path.exists(f"data_crawling/racedate/{current_year}"):
#         url = f"https://tamagawa.kyotei.club/racelist-{str(current_year)}.html"
        
#         response = requests.get(url)
#         time.sleep(1)
#         response.encoding = response.apparent_encoding
#         bs = BeautifulSoup(response.text, "html.parser")
        
#         with open(f"data_crawling/racedate/{current_year}", 'w', encoding='UTF-8') as file:
#             file.write(response.text)
#         print(f"{current_year}のレース日程の基データを保存しました")

# # 年ごとの節の始まりの日を取得
# def get_date(year):
#     file_path = f"data_crawling/racedate/{year}"
#     # ファイルを開いて内容を読み取る
#     with open(file_path, 'r', encoding='UTF-8') as file:
#         file_content = file.read()
#         soup = BeautifulSoup(file_content, 'html.parser')

#     date_list = []
    
#     date_elems = soup.find_all("tr", class_="end")
#     for date_elem in date_elems:
#         ymds_elem = date_elem.find("td", class_="ymds")
#         if ymds_elem:
#             # 要素のテキストから日付を取得
#             date = ymds_elem.text.strip()
#             date = date.replace(" ～", "")
#             # 日付をリストに追加
#             date_list.append(date)
#     date_list.reverse()
#     return date_list


# # 節の始まりを含め6日間（1節間の最大開催日数）の日付（YYYY-MM-DD）をDateFrameとして取得
# def generate_flat_date_list(dates, year):
#     flat_date_list = []
    
#     for date in dates:
#         date_obj = dt.strptime(f"{year}-{date}", '%Y-%m/%d')
#         flat_date_list.extend([(date_obj + td(days=i)).strftime('%Y-%m-%d') for i in range(6)])
    
#     return flat_date_list

# df_dates = pd.DataFrame() # 空のDataFrameを初期化

# for i in range(year_dif):
#     current_year = START_YEAR + i
#     dates = get_date(current_year)
#     flat_date_list = generate_flat_date_list(dates, current_year)
#     # 一時的なDataFrameを作成して、メインのDataFrameに追加
#     temp_df = pd.DataFrame({'date': flat_date_list})
#     df_dates = df_dates.append(temp_df, ignore_index=True)
    
    

# filtered_dates = df_dates[(df_dates['date'] >= START_DATE) & (df_dates['date'] <= END_DATE)]




# # 出走表データ取得
# for index, row in filtered_dates.iterrows():
#     current_date = dt.strptime(row['date'], '%Y-%m-%d')
#     for j in range(12):
#         filename = f"data_crawling/racelist/{current_date.strftime('%Y%m%d')}_{(j + 1):02d}R"
#         if not os.path.exists(filename):
#             # 日付とレース番号を含めたURLを構築
#             url = f"https://www.boatrace.jp/owpc/pc/race/racelist?rno={j + 1}&jcd=05&hd={current_date.strftime('%Y%m%d')}"
#             # URLからデータを取得
#             response = requests.get(url)
#             time.sleep(1)
#             response.encoding = response.apparent_encoding
#             bs = BeautifulSoup(response.text, 'html.parser')
#             # データの保存
#             with open(f"data_crawling/racelist/{current_date.strftime('%Y%m%d')}_{(j + 1):02d}R", 'w', encoding='UTF-8') as file:
#                 file.write(response.text)
#             print(f"{current_date.strftime('%Y-%m-%d')}_{(j + 1):02d}Rの出走表データを保存しました")
    


    

# # 直前情報データを取得
# for index, row in filtered_dates.iterrows():
#     current_date = dt.strptime(row['date'], '%Y-%m-%d')
#     for j in range(12):
#         filename = f"data_crawling/beforeinfo/{current_date.strftime('%Y%m%d')}_{(j + 1):02d}R"
#         if not os.path.exists(filename):
#             # 日付とレース番号を含めたURLを構築
#             url = f"https://www.boatrace.jp/owpc/pc/race/beforeinfo?rno={j + 1}&jcd=05&hd={current_date.strftime('%Y%m%d')}"
#         # URLからデータを取得
#             response = requests.get(url)
#             time.sleep(1)
#             response.encoding = response.apparent_encoding
#             bs = BeautifulSoup(response.text, 'html.parser')
#         # データの保存
#             with open(f"data_crawling/beforeinfo/{current_date.strftime('%Y%m%d')}_{(j + 1):02d}R", 'w', encoding='UTF-8') as file:
#                 file.write(response.text)
#             print(f"{current_date.strftime('%Y-%m-%d')}_{(j + 1):02d}Rの直前情報データを保存しました")




# # 結果データを取得
# for index, row in filtered_dates.iterrows():
#     current_date = dt.strptime(row['date'], '%Y-%m-%d')
#     for j in range(12):
#         filename = f"data_crawling/raceresult/{current_date.strftime('%Y%m%d')}_{(j + 1):02d}R"
#         if not os.path.exists(filename):
#         # 日付とレース番号を含めたURLを構築
#             url = f"https://www.boatrace.jp/owpc/pc/race/raceresult?rno={j + 1}&jcd=05&hd={current_date.strftime('%Y%m%d')}"
#         # URLからデータを取得
#             response = requests.get(url)
#             time.sleep(1)
#             response.encoding = response.apparent_encoding
#             bs = BeautifulSoup(response.text, 'html.parser')
#         # データの保存
#             with open(f"data_crawling/raceresult/{current_date.strftime('%Y%m%d')}_{(j + 1):02d}R", 'w', encoding='UTF-8') as file:
#                 file.write(response.text)
#             print(f"{current_date.strftime('%Y-%m-%d')}_{(j + 1):02d}Rの結果データを保存しました")
    
    
# print("クローニングを完了しました")