# データcsv化
# 必要なモジュールのインポート
import os
import re
from datetime import datetime

# 解凍したテキストファイルの格納先を指定
TEXT_FILE_DIR = "info_data/番組表データ_解凍後/"

# CSVファイルの保存先を指定
CSV_FILE_DIR = "data_csv/"

# CSV化する日付範囲を指定 (YYYYMMDD形式)
START_DATE = "20240611"  # 開始日
END_DATE = "20240831"    # 終了日



# 日付フォーマットの関数
def extract_date_from_filename(filename):
    """ファイル名から日付部分を抽出し、標準日付形式に変換"""
    match = re.search(r"B(\d{6})\.TXT", filename)
    if match:
        raw_date = match.group(1)
        formatted_date = "20" + raw_date[:2] + raw_date[2:4] + raw_date[4:6]
        return datetime.strptime(formatted_date, "%Y%m%d")
    return None

# CSVファイルの名前を指定　※YYYYMMDDには対象期間を入力
CSV_FILE_NAME = f"info_{START_DATE}_{END_DATE}.csv"


# CSVファイルのヘッダーを指定
CSV_FILE_HEADER = [
    'レースコード', 'タイトル', '日次', 'レース日', 'レース場', 'レース回', 'レース名', '距離', '電話投票締切予定',
    '1枠_艇番', '1枠_登録番号', '1枠_選手名', '1枠_年齢', '1枠_支部', '1枠_体重', '1枠_級別',
    '1枠_全国勝率', '1枠_全国2連対率', '1枠_当地勝率', '1枠_当地2連対率',
    '1枠_モーター番号', '1枠_モーター2連対率', '1枠_ボート番号', '1枠_ボート2連対率',
    '1枠_今節成績_1-1', '1枠_今節成績_1-2', '1枠_今節成績_2-1', '1枠_今節成績_2-2', '1枠_今節成績_3-1', '1枠_今節成績_3-2',
    '1枠_今節成績_4-1', '1枠_今節成績_4-2', '1枠_今節成績_5-1', '1枠_今節成績_5-2', '1枠_今節成績_6-1', '1枠_今節成績_6-2', '1枠_早見',
    '2枠_艇番', '2枠_登録番号', '2枠_選手名', '2枠_年齢', '2枠_支部', '2枠_体重', '2枠_級別',
    '2枠_全国勝率', '2枠_全国2連対率', '2枠_当地勝率', '2枠_当地2連対率',
    '2枠_モーター番号', '2枠_モーター2連対率', '2枠_ボート番号', '2枠_ボート2連対率',
    '2枠_今節成績_1-1', '2枠_今節成績_1-2', '2枠_今節成績_2-1', '2枠_今節成績_2-2', '2枠_今節成績_3-1', '2枠_今節成績_3-2',
    '2枠_今節成績_4-1', '2枠_今節成績_4-2', '2枠_今節成績_5-1', '2枠_今節成績_5-2', '2枠_今節成績_6-1', '2枠_今節成績_6-2', '2枠_早見',
    '3枠_艇番', '3枠_登録番号', '3枠_選手名', '3枠_年齢', '3枠_支部', '3枠_体重', '3枠_級別',
    '3枠_全国勝率', '3枠_全国2連対率', '3枠_当地勝率', '3枠_当地2連対率',
    '3枠_モーター番号', '3枠_モーター2連対率', '3枠_ボート番号', '3枠_ボート2連対率',
    '3枠_今節成績_1-1', '3枠_今節成績_1-2', '3枠_今節成績_2-1', '3枠_今節成績_2-2', '3枠_今節成績_3-1', '3枠_今節成績_3-2',
    '3枠_今節成績_4-1', '3枠_今節成績_4-2', '3枠_今節成績_5-1', '3枠_今節成績_5-2', '3枠_今節成績_6-1', '3枠_今節成績_6-2', '3枠_早見',
    '4枠_艇番', '4枠_登録番号', '4枠_選手名', '4枠_年齢', '4枠_支部', '4枠_体重', '4枠_級別',
    '4枠_全国勝率', '4枠_全国2連対率', '4枠_当地勝率', '4枠_当地2連対率',
    '4枠_モーター番号', '4枠_モーター2連対率', '4枠_ボート番号', '4枠_ボート2連対率',
    '4枠_今節成績_1-1', '4枠_今節成績_1-2', '4枠_今節成績_2-1', '4枠_今節成績_2-2', '4枠_今節成績_3-1', '4枠_今節成績_3-2',
    '4枠_今節成績_4-1', '4枠_今節成績_4-2', '4枠_今節成績_5-1', '4枠_今節成績_5-2', '4枠_今節成績_6-1', '4枠_今節成績_6-2', '4枠_早見',
    '5枠_艇番', '5枠_登録番号', '5枠_選手名', '5枠_年齢', '5枠_支部', '5枠_体重', '5枠_級別',
    '5枠_全国勝率', '5枠_全国2連対率', '5枠_当地勝率', '5枠_当地2連対率',
    '5枠_モーター番号', '5枠_モーター2連対率', '5枠_ボート番号', '5枠_ボート2連対率',
    '5枠_今節成績_1-1', '5枠_今節成績_1-2', '5枠_今節成績_2-1', '5枠_今節成績_2-2', '5枠_今節成績_3-1', '5枠_今節成績_3-2',
    '5枠_今節成績_4-1', '5枠_今節成績_4-2', '5枠_今節成績_5-1', '5枠_今節成績_5-2', '5枠_今節成績_6-1', '5枠_今節成績_6-2', '5枠_早見',
    '6枠_艇番', '6枠_登録番号', '6枠_選手名', '6枠_年齢', '6枠_支部', '6枠_体重', '6枠_級別',
    '6枠_全国勝率', '6枠_全国2連対率', '6枠_当地勝率', '6枠_当地2連対率',
    '6枠_モーター番号', '6枠_モーター2連対率', '6枠_ボート番号', '6枠_ボート2連対率',
    '6枠_今節成績_1-1', '6枠_今節成績_1-2', '6枠_今節成績_2-1', '6枠_今節成績_2-2', '6枠_今節成績_3-1', '6枠_今節成績_3-2',
    '6枠_今節成績_4-1', '6枠_今節成績_4-2', '6枠_今節成績_5-1', '6枠_今節成績_5-2', '6枠_今節成績_6-1', '6枠_今節成績_6-2', '6枠_早見'
]

CSV_FILE_HEADER = ','.join(CSV_FILE_HEADER) + '\n'  # リストをカンマ区切りの文字列に変換し、末尾に改行を追加

# OSの機能を利用するパッケージ os をインポート
import os

# 正規表現をサポートするモジュール re をインポート
import re


# テキストファイルからデータを抽出し、CSVファイルに書き込む関数 get_data を定義
def get_data(text_file):
    # CSVファイルを追記モードで開く
    csv_file = open(CSV_FILE_DIR + CSV_FILE_NAME, "a", encoding="UTF-8")

    # テキストファイルから中身を順に取り出す
    for contents in text_file:

        trans_asc = str.maketrans('１２３４５６７８９０Ｒ：　', '1234567890R: ')

        # キーワード「番組表」を見つけたら(rは正規表現でraw文字列を指定するおまじない)
        if re.search(r"番組表", contents):
            # 1行スキップ
            text_file.readline()

            # タイトルを格納
            line = text_file.readline()
            title = line[:-1].strip()

            # 1行スキップ
            text_file.readline()

            # 日次・レース日・レース場を格納
            line = text_file.readline()
            day = line[3:7].translate(trans_asc).replace(' ', '')
            date = line[17:28].translate(trans_asc).replace(' ', '0')
            stadium = line[52:55].replace('　', '')

        # キーワード「電話投票締切予定」を見つけたら
        if re.search(r"電話投票締切予定", contents):

            # キーワードを見つけた行を格納
            line = contents

            # レース名にキーワード「進入固定」が割り込んだ際の補正(「進入固定戦隊」は除くためＨまで含めて置換)
            if re.search(r"進入固定", line):
                line = line.replace('進入固定 Ｈ', '進入固定     Ｈ')

            # レース回・レース名・距離(m)・電話投票締切予定を格納
            race_round = line[0:3].translate(trans_asc).replace(' ', '0')
            race_name = line[5:21].replace('　', '')
            distance = line[22:26].translate(trans_asc)
            post_time = line[37:42].translate(trans_asc)

            # 4行スキップ(ヘッダー部分)
            text_file.readline()
            text_file.readline()
            text_file.readline()
            text_file.readline()

            # 選手データを格納する変数を定義
            racer_data = ""

            # 選手データを読み込む行(開始行)を格納
            line = text_file.readline()

            # 空行またはキーワード「END」まで処理を繰り返す = 1～6艇分の選手データを取得
            while line != "\n":

                if re.search(r"END", line):
                    break

                # 選手データを格納(行末にカンマが入らないように先頭にカンマを入れる)
                racer_data += "," + line[0] + "," + line[2:6] + "," + line[6:10] + "," + line[10:12] \
                              + "," + line[12:14] + "," + line[14:16] + "," + line[16:18] \
                              + "," + line[19:23] + "," + line[24:29] + "," + line[30:34] \
                              + "," + line[35:40] + "," + line[41:43] + "," + line[44:49] \
                              + "," + line[50:52] + "," + line[53:58] + "," + line[59:60] \
                              + "," + line[60:61] + "," + line[61:62] + "," + line[62:63] \
                              + "," + line[63:64] + "," + line[64:65] + "," + line[65:66] \
                              + "," + line[66:67] + "," + line[67:68] + "," + line[68:69] \
                              + "," + line[69:70] + "," + line[70:71] + "," + line[71:73]

                # 次の行を読み込む
                line = text_file.readline()

            # レースコードを生成
            dict_stadium = {'桐生': 'KRY', '戸田': 'TDA', '江戸川': 'EDG', '平和島': 'HWJ',
                            '多摩川': 'TMG', '浜名湖': 'HMN', '蒲郡': 'GMG', '常滑': 'TKN',
                            '津': 'TSU', '三国': 'MKN', '琵琶湖': 'BWK','びわこ': 'BWK', '住之江': 'SME',
                            '尼崎': 'AMG', '鳴門': 'NRT', '丸亀': 'MRG', '児島': 'KJM',
                            '宮島': 'MYJ', '徳山': 'TKY', '下関': 'SMS', '若松': 'WKM',
                            '芦屋': 'ASY', '福岡': 'FKO', '唐津': 'KRT', '大村': 'OMR'
                            }

            race_code = date[0:4] + date[5:7] + date[8:10] + dict_stadium[stadium] + race_round[0:2]

            # 抽出したデータをCSVファイルに書き込む
            csv_file.write(race_code + "," + title + "," + day + "," + date + "," + stadium + "," + race_round
                           + "," + race_name + "," + distance + "," + post_time + racer_data + "\n")
    # CSVファイルを閉じる
    csv_file.close()


# # 開始合図
# print("作業を開始します")

# # CSVファイルを保存するフォルダを作成
# if not os.path.exists(CSV_FILE_DIR):
#     os.makedirs(CSV_FILE_DIR)

# # CSVファイルを作成しヘッダ情報を書き込む
# csv_file = open(CSV_FILE_DIR + CSV_FILE_NAME, "w", encoding="UTF-8")
# csv_file.write(CSV_FILE_HEADER)
# csv_file.close()

# # テキストファイルのリストを取得
# text_file_list = os.listdir(TEXT_FILE_DIR)

# # リストからファイル名を順に取り出す
# for text_file_name in text_file_list:

#     # 拡張子が TXT のファイルに対してのみ実行
#     if re.search(".TXT", text_file_name):
#         # テキストファイルを開く
#         text_file = open(TEXT_FILE_DIR + text_file_name, "r", encoding="shift_jis")

#         # 関数 get_data にファイル(オブジェクト)を渡す
#         get_data(text_file)

#         # テキストファイルを閉じる
#         text_file.close()

# print(CSV_FILE_DIR + CSV_FILE_NAME + " を作成しました")

# # 終了合図
# print("作業を終了しました")


# 開始合図
print("作業を開始します")

# CSVファイルを保存するフォルダを作成
if not os.path.exists(CSV_FILE_DIR):
    os.makedirs(CSV_FILE_DIR)

# CSVファイルを作成しヘッダー情報を書き込む
csv_file = open(CSV_FILE_DIR + CSV_FILE_NAME, "w", encoding="UTF-8")
csv_file.write(CSV_FILE_HEADER)
csv_file.close()

# テキストファイルのリストを取得
text_file_list = os.listdir(TEXT_FILE_DIR)

# 日付範囲を適用
start_date_obj = datetime.strptime(START_DATE, "%Y%m%d")
end_date_obj = datetime.strptime(END_DATE, "%Y%m%d")

# リストからファイル名を順に取り出す
for text_file_name in text_file_list:
    file_date_obj = extract_date_from_filename(text_file_name)

    # 日付が指定範囲内で、拡張子がTXTのファイルに対してのみ実行
    if file_date_obj and start_date_obj <= file_date_obj <= end_date_obj and re.search(r".TXT$", text_file_name):
        # テキストファイルを開く
        text_file_path = os.path.join(TEXT_FILE_DIR, text_file_name)
        with open(text_file_path, "r", encoding="shift_jis") as text_file:
            # 関数 get_data にファイル(オブジェクト)を渡す
            get_data(text_file)

print(CSV_FILE_DIR + CSV_FILE_NAME + " を作成しました")

# 終了合図
print("作業を終了しました")