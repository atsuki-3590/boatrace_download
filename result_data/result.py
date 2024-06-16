import os
import re

# データのCSV化
TEXT_FILE_DIR = "競争成績データ/競争成績データ_解凍後/"
CSV_FILE_DIR = "競争成績データ_csv/"
CSV_FILE_NAME = "result.csv"
CSV_FILE_HEADER = ("レースコード,タイトル,日次,レース日,レース場,レース回,レース名,距離(m),天候,風向,風速(m),波の高さ(cm),決まり手,"
                   "単勝_艇番,単勝_払戻金,複勝_1着_艇番,複勝_1着_払戻金,複勝_2着_艇番,複勝_2着_払戻金,"
                   "2連単_組番,2連単_払戻金,2連単_人気,2連複_組番,2連複_払戻金,2連複_人気,"
                   "拡連複_1-2着_組番,拡連複_1-2着_払戻金,拡連複_1-2着_人気,"
                   "拡連複_1-3着_組番,拡連複_1-3着_払戻金,拡連複_1-3着_人気,"
                   "拡連複_2-3着_組番,拡連複_2-3着_払戻金,拡連複_2-3着_人気,"
                   "3連単_組番,3連単_払戻金,3連単_人気,3連複_組番,3連複_払戻金,3連複_人気,"
                   "1着_着順,1着_艇番,1着_登録番号,1着_選手名,1着_モーター番号,1着_ボート番号,1着_展示タイム,1着_進入コース,1着_スタートタイミング,1着_レースタイム,"
                   "2着_着順,2着_艇番,2着_登録番号,2着_選手名,2着_モーター番号,2着_ボート番号,2着_展示タイム,2着_進入コース,2着_スタートタイミング,2着_レースタイム,"
                   "3着_着順,3着_艇番,3着_登録番号,3着_選手名,3着_モーター番号,3着_ボート番号,3着_展示タイム,3着_進入コース,3着_スタートタイミング,3着_レースタイム,"
                   "4着_着順,4着_艇番,4着_登録番号,4着_選手名,4着_モーター番号,4着_ボート番号,4着_展示タイム,4着_進入コース,4着_スタートタイミング,4着_レースタイム,"
                   "5着_着順,5着_艇番,5着_登録番号,5着_選手名,5着_モーター番号,5着_ボート番号,5着_展示タイム,5着_進入コース,5着_スタートタイミング,5着_レースタイム,"
                   "6着_着順,6着_艇番,6着_登録番号,6着_選手名,6着_モーター番号,6着_ボート番号,6着_展示タイム,6着_進入コース,6着_スタートタイミング,6着_レースタイム,\n")

def get_data(text_file):
    with open(CSV_FILE_DIR + CSV_FILE_NAME, "a", encoding="shift_jis") as csv_file:
        for line in text_file:
            if "競走成績" in line:
                text_file.readline()
                title = text_file.readline().strip()
                text_file.readline()
                line = text_file.readline()
                day = line[3:7].strip()
                date = line[17:27].strip().replace(' ', '0')
                stadium = line[62:65].strip().replace('　', '')
                
                while line != "\n":
                    if "R" in line and "H" in line:
                        if "進入固定" in line:
                            line = line.replace('進入固定       H', '進入固定           H')
                        
                        race_round = line[2:5].strip().replace(' ', '0')
                        race_name = line[12:31].strip().replace('　', '')
                        distance = line[36:40].strip()
                        weather = line[43:45].strip()
                        wind_direction = line[50:52].strip()
                        wind_velocity = line[53:55].strip()
                        wave_height = line[60:63].strip()
                        
                        line = text_file.readline()
                        winning_technique = line[50:55].strip()
                        
                        text_file.readline()
                        
                        result_racer = ""
                        line = text_file.readline()
                        while line != "\n":
                            result_racer += "," + line[2:4].strip() + "," + line[6].strip() + "," + line[8:12].strip() \
                                            + "," + line[13:21].strip() + "," + line[22:24].strip() + "," + line[27:29].strip() \
                                            + "," + line[30:35].strip() + "," + line[38].strip() + "," + line[43:47].strip() \
                                            + "," + line[52:58].strip()
                            line = text_file.readline()
                        
                        line = text_file.readline()
                        result_win, result_place_show, result_exacta, result_quinella, result_quinella_place, result_trifecta, result_trio = "", "", "", "", "", "", ""
                        while line != "\n":
                            if "単勝" in line:
                                if "特払い"に line:
                                    line = line.replace('        特払い   ', '   特払い        ')
                                result_win = line[15].strip() + "," + line[22:29].strip()
                            if "複勝" in line:
                                if "特払い"に line:
                                    line = line.replace('        特払い   ', '   特払い        ')
                                if len(line) <= 33:
                                    result_place_show = line[15].strip() + "," + line[22:29].strip() + ",,"
                                else:
                                    result_place_show = line[15].strip() + "," + line[22:29].strip() + "," + line[31].strip() + "," + line[38:45].strip()
                            if "２連単"に line:
                                result_exacta = line[14:17].strip() + "," + line[21:28].strip() + "," + line[36:38].strip()
                            if "２連複"に line:
                                result_quinella = line[14:17].strip() + "," + line[21:28].strip() + "," + line[36:38].strip()
                            if "拡連複"に line:
                                result_quinella_place = line[14:17].strip() + "," + line[21:28].strip() + "," + line[36:38].strip()
                                line = text_file.readline()
                                result_quinella_place += "," + line[17:20].strip() + "," + line[24:31].strip() + "," + line[39:41].strip()
                                line = text_file.readline()
                                result_quinella_place += "," + line[17:20].strip() + "," + line[24:31].strip() + "," + line[39:41].strip()
                            if "３連単"に line:
                                result_trifecta = line[14:19].strip() + "," + line[21:28].strip() + "," + line[35:38].strip()
                            if "３連複"に line:
                                result_trio = line[14:19].strip() + "," + line[21:28].strip() + "," + line[35:38].strip()
                            line = text_file.readline()
                        
                        dict_stadium = {'桐生': 'KRY', '戸田': 'TDA', '江戸川': 'EDG', '平和島': 'HWJ',
                                        '多摩川': 'TMG', '浜名湖': 'HMN', '蒲郡': 'GMG', '常滑': 'TKN',
                                        '津': 'TSU', '三国': 'MKN', '琵琶湖': 'BWK', '住之江': 'SME',
                                        '尼崎': 'AMG', '鳴門': 'NRT', '丸亀': 'MRG', '児島': 'KJM',
                                        '宮島': 'MYJ', '徳山': 'TKY', '下関': 'SMS', '若松': 'WKM',
                                        '芦屋': 'ASY', '福岡': 'FKO', '唐津': 'KRT', '大村': 'OMR'}
                        
                        race_code = date[:4] + date[5:7] + date[8:10] + dict_stadium.get(stadium, 'UNK') + race_round[:2]
                        
                        csv_file.write(race_code + "," + title + "," + day + "," + date + "," + stadium + "," + race_round + "," + race_name + "," + distance + "," + weather + "," + wind_direction + "," + wind_velocity + "," + wave_height + "," + winning_technique + "," + result_win + "," + result_place_show + "," + result_exacta + "," + result_quinella + "," + result_quinella_place + "," + result_trifecta + "," + result_trio + result_racer + "\n")
                        
                    line = text_file.readline()

print("作業を開始します")
os.makedirs(CSV_FILE_DIR, exist_ok=True)

with open(CSV_FILE_DIR + CSV_FILE_NAME, "w", encoding="shift_jis") as csv_file:
    csv_file.write(CSV_FILE_HEADER)

text_file_list = os.listdir(TEXT_FILE_DIR)
for text_file_name in text_file_list:
    if text_file_name.endswith(".TXT"):
        with open(TEXT_FILE_DIR + text_file_name, "r", encoding="shift_jis") as text_file:
            get_data(text_file)

print(CSV_FILE_DIR + CSV_FILE_NAME + " を作成しました")
print("作業を終了しました")