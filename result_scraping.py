# データのCSV化
# テキストファイルが保存されている場所を指定
TXT_FILE_DIR = "データ格納_解凍後/"

# CSVファイルを保存する場所を指定
CSV_FILE_DIR = "データ格納_csv/"

# CSVファイルの名前を指定
CSV_FILE_NAME = "result.csv"

# CSVファイルのヘッダ情報を指定
CSV_FILE_HEADER = "タイトル,日次,レース日,レース場,レース回,\
3連単_組番,3連単_払戻金,3連複_組番,3連複_払戻金,2連単_組番,2連単_払戻金,2連複_組番,2連複_払戻金\n"

# 正規表現をサポートするモジュール re をインポート
import re

# オペレーティングシステムの機能を利用するパッケージ os をインポート
import os

# 開始合図
print("作業を開始します")

# CSVファイルを格納するフォルダを作成
os.makedirs(CSV_FILE_DIR, exist_ok=True)

# CSVファイルを作成しヘッダ情報を書き込む
csv_file = open(CSV_FILE_DIR + CSV_FILE_NAME, "w", encoding="shift_jis")
csv_file.write(CSV_FILE_HEADER)
csv_file.close()


# テキストファイルからデータを抽出し、CSVファイルに書き込む関数
def get_data(text_file):
    # CSVファイルを追記モードで開く
    csv_file = open(CSV_FILE_DIR + CSV_FILE_NAME, "a", encoding="shift_jis")

    # テキストファイルからデータを抽出
    for contents in text_file:

        # 文字列「競争成績」を検索してタイトル・日次・レース日・レース場を取得
        # rは正規表現でraw文字列を指定するおまじない
        if re.search(r"競走成績", contents):
            # 1行スキップ
            text_file.readline()

            # タイトルを取得
            line = text_file.readline()
            title = line[:-1].strip()

            # 1行スキップ
            text_file.readline()

            # 日次、レース日、レース場を取得
            line = text_file.readline()
            day = line[3:7].replace(' ', '')
            date = line[17:27].replace(' ', '')
            stadium = line[62:65].replace('　', '')

        # 文字列「払戻金」を検索してレース結果を取得
        if re.search(r"払戻金", contents):

            line = text_file.readline()

            # 空行まで処理を繰り返す = 12レース分を取得
            while line != "\n":
                results = line[10:13].strip() + "," \
                          + line[15:20] + "," + line[21:28].strip() + "," \
                          + line[32:37] + "," + line[38:45].strip() + "," \
                          + line[49:52] + "," + line[53:60].strip() + "," \
                          + line[64:67] + "," + line[68:75].strip()

                # 抽出したデータをCSVファイルに書き込む
                csv_file.write(title + "," + day + "," + date + "," + stadium + "," + results + "\n")

                # 次の行を読み込む
                line = text_file.readline()

    # CSVファイルを閉じる
    csv_file.close()


# テキストファイルのリストを取得
text_file_list = os.listdir(TXT_FILE_DIR)

# ファイルの数だけ処理を繰り返す
for txt_file_name in text_file_list:

    # 拡張子が txt のファイルに対してのみ実行
    if re.search(".TXT", txt_file_name):

        # テキストファイルを開く
        text_file = open(TXT_FILE_DIR + txt_file_name, "r", encoding="shift_jis")

        # データを抽出する
        get_data(text_file)

        # テキストファイルを閉じる
        text_file.close()

print(CSV_FILE_DIR + CSV_FILE_NAME + " を作成しました")

# 終了合図
print("作業を終了しました")
