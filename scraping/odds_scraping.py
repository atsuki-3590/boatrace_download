import os
import re
import csv
from datetime import datetime
from bs4 import BeautifulSoup

print("オッズデータのスクレイピングを開始します")

# データcsv化
TEXT_FILE_DIR = "odds_scrapy/odds_data/odds_HTML"
CSV_FILE_DIR = "data_csv/"

# CSV化する日付範囲を指定 (YYYYMMDD形式)
START_DATE = "20240611"  # 開始日
END_DATE = "20240831"    # 終了日

# CSVファイルの名前を指定
CSV_FILE_NAME = f"odds_3f_{START_DATE}_{END_DATE}.csv"

# CSVファイルのヘッダーを指定
CSV_FILE_HEADER = [
    "レースコード", 
    "1=2=3", "1=2=4", "1=2=5", "1=2=6", "1=3=4", "1=3=5", "1=3=6", "1=4=5", "1=4=6", "1=5=6", 
    "2=3=4", "2=3=5", "2=3=6", "2=4=5", "2=4=6", "2=5=6", "3=4=5", "3=4=6", "3=5=6", "4=5=6"
]

dict_stadium = {
    '01': 'KRY', '02': 'TDA', '03': 'EDG', '04': 'HWJ',
    '05': 'TMG', '06': 'HMN', '07': 'GMG', '08': 'TKN',
    '09': 'TSU', '10': 'MKN', '11': 'BWK', '12': 'SME',
    '13': 'AMG', '14': 'NRT', '15': 'MRG', '16': 'KJM',
    '17': 'MYJ', '18': 'TKY', '19': 'SMS', '20': 'WKM',
    '21': 'ASY', '22': 'FKO', '23': 'KRT', '24': 'OMR'
}

odds_positions = {
    # 組み合わせに対応する(line, row)の辞書
    "1=2=3": (0, 2), "1=2=4": (1, 1), "1=2=5": (2, 1), "1=2=6": (3, 1), 
    "1=3=4": (4, 2), "1=3=5": (5, 1), "1=3=6": (6, 1), "1=4=5": (7, 2), 
    "1=4=6": (8, 1), "1=5=6": (9, 2), "2=3=4": (4, 5), "2=3=5": (5, 3), 
    "2=3=6": (6, 3), "2=4=5": (7, 5), "2=4=6": (8, 3), "2=5=6": (9, 5), 
    "3=4=5": (7, 8), "3=4=6": (8, 5), "3=5=6": (9, 8), "4=5=6": (9, 11)
}

# 日付範囲内かをチェックする関数
def is_within_date_range(file_name, start_date, end_date):
    """ファイル名から日付部分を抽出し、指定された日付範囲内かを判定"""
    match = re.search(r"(\d{8})", file_name)
    if match:
        file_date = datetime.strptime(match.group(1), "%Y%m%d")
        start = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")
        return start <= file_date <= end
    return False

def extract_odds(soup, file_name):
    """オッズデータをHTMLから抽出"""
    odds_dict = {}
    for combination, (line, row) in odds_positions.items():
        odds_dict[combination] = get_odds(soup, line, row, file_name)
    return odds_dict

def get_odds(soup, line, row, file_name):
    """HTML内の特定行・列からオッズデータを取得"""
    tbody = soup.find('tbody', class_='is-p3-0')
    if tbody is None:
        return "N/A"
    rows = tbody.find_all('tr')
    if line >= len(rows):
        return "N/A"
    target_row = rows[line]  
    cols = target_row.find_all('td')
    if row >= len(cols):
        return "N/A"
    return cols[row].text.strip()

def save_to_csv(data_list, csv_file):
    """データをCSVファイルに保存"""
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FILE_HEADER)
        writer.writeheader()
        for data in data_list:
            writer.writerow(data)

def generate_race_code(file_name):
    """ファイル名からレースコードを生成"""
    date, stadium_code, race_number = file_name.split('_')
    race_number = race_number.replace('R.html', '')
    stadium_abbr = dict_stadium.get(stadium_code, 'UNKNOWN')
    return f"{date}{stadium_abbr}{race_number}"

def main():
    """メイン処理"""
    data_list = []
    file_count = 0
    for file_name in os.listdir(TEXT_FILE_DIR):
        if file_name.endswith(".html") and is_within_date_range(file_name, START_DATE, END_DATE):
            file_path = os.path.join(TEXT_FILE_DIR, file_name)
            race_code = generate_race_code(file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                odds_data = extract_odds(soup, file_name)
                data = {"レースコード": race_code, **odds_data}
                data_list.append(data)
            file_count += 1
            if file_count % 100 == 0:
                print(f"{file_count} 件のファイルを処理しました")

    save_to_csv(data_list, os.path.join(CSV_FILE_DIR, CSV_FILE_NAME))
    print("CSV保存が完了しました")

if __name__ == "__main__":
    main()

print("スクレイピングが完了しました")
