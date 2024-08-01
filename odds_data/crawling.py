# -*- coding: UTF-8 -*-
import requests
import time
import os
from datetime import datetime as dt
from datetime import timedelta as td
from bs4 import BeautifulSoup 
import pandas as pd

print("オッズデータのクローニングを開始します")

# 各ディレクトリを作成
if not os.path.exists('data_crawling'):
    os.mkdir('data_crawling')
    print("ディレクトリを作成しました")


if not os.path.exists('data_crawling/racelist'):
    os.mkdir('data_crawling/racelist')
    print("出走表ディレクトリを作成しました")

if not os.path.exists('data_crawling/beforeinfo'):
    os.mkdir('data_crawling/beforeinfo')
    print("直前情報ディレクトリを作成しました")

if not os.path.exists('data_crawling/raceresult'):
    os.mkdir("data_crawling/raceresult")
    print("結果ディレクトリを作成しました")
    
if not os.path.exists("data_crawling/racedate"):
    os.mkdir("data_crawling/racedate")
    print("日程ディレクトリを作成しました")


    
START_YEAR = 2022
END_YEAR = 2023 
START_DATE = "2022-11-01"
END_DATE = "2023-10-31"

start_date = dt.strptime(START_DATE, '%Y-%m-%d')
end_date = dt.strptime(END_DATE, '%Y-%m-%d')

year_dif = ((END_YEAR) - (START_YEAR)) + 1

# 年ごとの日程に関するHTMLを取得
for i in range(year_dif):
    current_year = START_YEAR + i
    if not os.path.exists(f"data_crawling/racedate/{current_year}"):
        url = f"https://tamagawa.kyotei.club/racelist-{str(current_year)}.html"
        
        response = requests.get(url)
        time.sleep(1)
        response.encoding = response.apparent_encoding
        bs = BeautifulSoup(response.text, "html.parser")
        
        with open(f"data_crawling/racedate/{current_year}", 'w', encoding='UTF-8') as file:
            file.write(response.text)
        print(f"{current_year}のレース日程の基データを保存しました")

# 年ごとの節の始まりの日を取得
def get_date(year):
    file_path = f"data_crawling/racedate/{year}"
    # ファイルを開いて内容を読み取る
    with open(file_path, 'r', encoding='UTF-8') as file:
        file_content = file.read()
        soup = BeautifulSoup(file_content, 'html.parser')

    date_list = []
    
    date_elems = soup.find_all("tr", class_="end")
    for date_elem in date_elems:
        ymds_elem = date_elem.find("td", class_="ymds")
        if ymds_elem:
            # 要素のテキストから日付を取得
            date = ymds_elem.text.strip()
            date = date.replace(" ～", "")
            # 日付をリストに追加
            date_list.append(date)
    date_list.reverse()
    return date_list


# 節の始まりを含め6日間（1節間の最大開催日数）の日付（YYYY-MM-DD）をDateFrameとして取得
def generate_flat_date_list(dates, year):
    flat_date_list = []
    
    for date in dates:
        date_obj = dt.strptime(f"{year}-{date}", '%Y-%m/%d')
        flat_date_list.extend([(date_obj + td(days=i)).strftime('%Y-%m-%d') for i in range(6)])
    
    return flat_date_list

df_dates = pd.DataFrame() # 空のDataFrameを初期化

for i in range(year_dif):
    current_year = START_YEAR + i
    dates = get_date(current_year)
    flat_date_list = generate_flat_date_list(dates, current_year)
    # 一時的なDataFrameを作成して、メインのDataFrameに追加
    temp_df = pd.DataFrame({'date': flat_date_list})
    df_dates = df_dates.append(temp_df, ignore_index=True)
    
    

filtered_dates = df_dates[(df_dates['date'] >= START_DATE) & (df_dates['date'] <= END_DATE)]




# 出走表データ取得
for index, row in filtered_dates.iterrows():
    current_date = dt.strptime(row['date'], '%Y-%m-%d')
    for j in range(12):
        filename = f"data_crawling/racelist/{current_date.strftime('%Y%m%d')}_{(j + 1):02d}R"
        if not os.path.exists(filename):
            # 日付とレース番号を含めたURLを構築
            url = f"https://www.boatrace.jp/owpc/pc/race/racelist?rno={j + 1}&jcd=05&hd={current_date.strftime('%Y%m%d')}"
            # URLからデータを取得
            response = requests.get(url)
            time.sleep(1)
            response.encoding = response.apparent_encoding
            bs = BeautifulSoup(response.text, 'html.parser')
            # データの保存
            with open(f"data_crawling/racelist/{current_date.strftime('%Y%m%d')}_{(j + 1):02d}R", 'w', encoding='UTF-8') as file:
                file.write(response.text)
            print(f"{current_date.strftime('%Y-%m-%d')}_{(j + 1):02d}Rの出走表データを保存しました")
    


    

# 直前情報データを取得
for index, row in filtered_dates.iterrows():
    current_date = dt.strptime(row['date'], '%Y-%m-%d')
    for j in range(12):
        filename = f"data_crawling/beforeinfo/{current_date.strftime('%Y%m%d')}_{(j + 1):02d}R"
        if not os.path.exists(filename):
            # 日付とレース番号を含めたURLを構築
            url = f"https://www.boatrace.jp/owpc/pc/race/beforeinfo?rno={j + 1}&jcd=05&hd={current_date.strftime('%Y%m%d')}"
        # URLからデータを取得
            response = requests.get(url)
            time.sleep(1)
            response.encoding = response.apparent_encoding
            bs = BeautifulSoup(response.text, 'html.parser')
        # データの保存
            with open(f"data_crawling/beforeinfo/{current_date.strftime('%Y%m%d')}_{(j + 1):02d}R", 'w', encoding='UTF-8') as file:
                file.write(response.text)
            print(f"{current_date.strftime('%Y-%m-%d')}_{(j + 1):02d}Rの直前情報データを保存しました")




# 結果データを取得
for index, row in filtered_dates.iterrows():
    current_date = dt.strptime(row['date'], '%Y-%m-%d')
    for j in range(12):
        filename = f"data_crawling/raceresult/{current_date.strftime('%Y%m%d')}_{(j + 1):02d}R"
        if not os.path.exists(filename):
        # 日付とレース番号を含めたURLを構築
            url = f"https://www.boatrace.jp/owpc/pc/race/raceresult?rno={j + 1}&jcd=05&hd={current_date.strftime('%Y%m%d')}"
        # URLからデータを取得
            response = requests.get(url)
            time.sleep(1)
            response.encoding = response.apparent_encoding
            bs = BeautifulSoup(response.text, 'html.parser')
        # データの保存
            with open(f"data_crawling/raceresult/{current_date.strftime('%Y%m%d')}_{(j + 1):02d}R", 'w', encoding='UTF-8') as file:
                file.write(response.text)
            print(f"{current_date.strftime('%Y-%m-%d')}_{(j + 1):02d}Rの結果データを保存しました")
    
    
print("クローニングを完了しました")