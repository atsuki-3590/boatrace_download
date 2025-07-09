import scrapy
import requests  # Webダウンロード用にインポート
import lhafile
import io
import re
import os
from datetime import datetime, timedelta
from boatrace_scrapy.utils import get_gdrive_service, list_drive_files
from boatrace_scrapy.items import InfoItem


class InfoSpider(scrapy.Spider):
    name = 'Info_Spider'

    # --- 設定項目 ---
    START_DATE = "2024-08-01"
    END_DATE = "2024-08-03"
    FIXED_URL = "http://www1.mbrace.or.jp/od2/B/{yyyymm}/b{yymmdd}.lzh"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log("Google Driveの認証を開始します...")
        self.drive = get_gdrive_service()
        self.lzh_folder_id = os.getenv('INFO_LZH_FOLDER_ID')
        self.txt_folder_id = os.getenv('INFO_TXT_FOLDER_ID')
        self.csv_folder_id = os.getenv('INFO_CSV_FOLDER_ID')
        self.log("Google Driveの認証が完了しました。")

    async def start(self):
        """
        ダウンロード、解凍、CSV化の全処理を順番に実行する
        """

        self.log("====== 全処理開始 ======")

        # --- フェーズ1: 不足しているLZHファイルのダウンロード ---
        self.log("====== フェーズ1: LZHダウンロード開始 ======")
        existing_lzh_obj = list_drive_files(self.drive, self.lzh_folder_id)
        existing_lzh_files = [f['title'] for f in existing_lzh_obj]
        self.log(f"既存LZHファイル数: {len(existing_lzh_files)}")
        
        start_date_obj = datetime.strptime(self.START_DATE, '%Y-%m-%d')
        end_date_obj = datetime.strptime(self.END_DATE, '%Y-%m-%d')
        current_date = start_date_obj

        while current_date <= end_date_obj:
            yymmdd = current_date.strftime("%y%m%d")
            file_name = f"b{yymmdd}.lzh"

            if file_name not in existing_lzh_files:
                yyyymm = current_date.strftime("%Y%m")
                url = self.FIXED_URL.format(yyyymm=yyyymm, yymmdd=yymmdd)
                self.log(f"Downloading: {url}")
                try:
                    # Scrapyエンジンを経由せず直接ダウンロード
                    response = requests.get(url, timeout=30)
                    if response.status_code == 200:
                        lzh_drive_file = self.drive.CreateFile({
                            'title': file_name,
                            'parents': [{'id': self.lzh_folder_id}]
                        })
                        lzh_drive_file.content = io.BytesIO(response.content)
                        lzh_drive_file.Upload()
                        self.log(f"Uploaded LZH file: {file_name}")
                    else:
                        self.log(f"Download failed for {url} with status code: {response.status_code}")
                except Exception as e:
                    self.log(f"An error occurred during download/upload of {file_name}: {e}")
            else:
                self.log(f"Skipping download, LZH exists: {file_name}")

            current_date += timedelta(days=1)
        self.log("====== フェーズ1: LZHダウンロード完了 ======")

        self.log("====== フェーズ2: TXTファイル解凍開始 ======")
        lzh_files = list_drive_files(self.drive, self.lzh_folder_id)
        txt_files_obj = list_drive_files(self.drive, self.txt_folder_id)
        existing_txt_names = [f['title'] for f in txt_files_obj]
        
        for lzh_file in lzh_files:
            lzh_name = lzh_file['title']
            expected_txt_name = lzh_name.replace('b', 'B').replace('.lzh', '.TXT')

            if expected_txt_name not in existing_txt_names:
                self.log(f"Unzipping required for: {lzh_name}")
                try:
                    # --- ▼ 変更箇所 ▼ ---
                    # Driveからのストリームを取得
                    lzh_content_stream = lzh_file.GetContentIOBuffer()
                    # ストリームから全データをバイトとして読み出す
                    lzh_bytes = lzh_content_stream.read()
                    # lhafileが扱えるように、バイトデータからメモリ上のファイルを作成
                    lzh_in_memory_file = io.BytesIO(lzh_bytes)
                    
                    # 修正したメモリ上のファイルをlhafileに渡す
                    lha = lhafile.Lhafile(lzh_in_memory_file)
                    # --- ▲ 変更箇所 ▲ ---

                    for file_info in lha.infolist():
                        if file_info.filename.upper() == expected_txt_name:
                            txt_content_bytes = lha.read(file_info.filename)
                            txt_drive_file = self.drive.CreateFile({
                                'title': expected_txt_name,
                                'parents': [{'id': self.txt_folder_id}]
                            })
                            txt_drive_file.content = io.BytesIO(txt_content_bytes)
                            txt_drive_file.Upload()
                            self.log(f"Uploaded TXT file: {expected_txt_name}")
                            break
                except Exception as e:
                    self.log(f"Failed to process {lzh_name}: {e}")
            else:
                self.log(f"Skipping unzip, TXT exists: {expected_txt_name}")
        self.log("====== フェーズ2: TXTファイル解凍完了 ======")

        # --- フェーズ3: CSV化処理 ---
        self.log("====== CSV化処理開始 ======")
        txt_files = list_drive_files(self.drive, self.txt_folder_id)
        self.log(f"CSV化対象のTXTファイル数: {len(txt_files)}")

        if not txt_files:
            self.log("処理対象のTXTファイルが見つかりません。")
            return

        # Google Driveから取得した各ファイルを直接処理する
        for txt_file in txt_files:
            self.log(f"Processing: {txt_file['title']}")
            try:
                text_data = txt_file.GetContentString(encoding='shift_jis')
                
                # 'yield from' を 'for' ループに変更
                for item in self._parse_content(text_data):
                    yield item
                    
            except Exception as e:
                self.log(f"Failed to read or parse {txt_file['title']}: {e}")
        
        self.log("====== CSV化処理完了 ======")

    def _parse_content(self, text_data):
        # こちらのヘルパーメソッドは前回の修正から変更ありません
        lines = text_data.splitlines()
        trans_asc = str.maketrans('１２３４５６７８９０Ｒ：　', '1234567890R: ')
        
        title, day, date, stadium = "", "", "", ""
        
        for i, line in enumerate(lines):
            # 新しいレース場のヘッダー情報を見つけたら更新
            if "番組表" in line and i + 4 < len(lines):
                info_line = lines[i+4]
                print(f"ヘッダー行: {info_line.strip()}")
                print(f"ヘッダー行の長さ: {len(info_line)}")
                if len(info_line) > 20:
                    title = lines[i+2].strip()
                    day = info_line[3:7].translate(trans_asc).replace(' ', '')
                    date = info_line[17:28].translate(trans_asc).replace(' ', '0')
                    stadium = info_line[52:55].replace('　', '')
                else:
                    self.log(f"警告: ヘッダー行の形式が不正です。Line {i+3}: {info_line}")

            # レース情報を見つけたらパース
            if "電話投票締切予定" in line:
                if not stadium or not date:
                    self.log(f"警告: ヘッダー情報が未設定のままレース情報が見つかりました。スキップします。Line {i}: {line}")
                    continue

                item = InfoItem()
                item['title'] = title
                item['day_num'] = day
                item['date'] = date
                item['stadium'] = stadium
                
                # 正規表現パターンを定義
                # (?P<name>...) のようにグループに名前を付けると後で分かりやすい
                pattern = re.compile(
                    r"^(?P<round>\s*.+?Ｒ)\s*"         # round: 先頭から 'R' まで (非貪欲)
                    r"(?P<name>.+?)\s*"             # name: roundの後から distance の直前まで (非貪欲)
                    r"(?P<distance>Ｈ１[２８]００ｍ)\s*"  # distance: 'Ｈ１２００ｍ' または 'Ｈ１８００ｍ'
                    r"電話投票締切予定\s*(?P<time>.+?)\s*$" # time: '電話投票締切予定' の後の文字列
                )
                print(f"line: {line}")
                print(f"Processing line: {line.strip()}")
                
                match = pattern.search(line)
                
                if match:
                    race_round = match.group('round').translate(trans_asc).replace(' ', '0')
                    # レース名に含まれる可能性のある全角スペースを半角に統一してから不要な空白を除去
                    race_name = match.group('name').replace('　', ' ').strip()
                    
                    # 距離は1200か1800に正規化
                    distance_str = match.group('distance').translate(trans_asc)
                    if "1200" in distance_str:
                        distance = 1200
                    else:
                        distance = 1800 # 1800m or other
                        
                    post_time = match.group('time').translate(trans_asc)

                    item['race_round'] = race_round
                    item['race_name'] = race_name
                    item['distance'] = distance
                    item['post_time'] = post_time
                else:
                    self.log(f"警告: 正規表現にマッチしませんでした。スキップします。 Line: {line}")
                    continue # マッチしない場合はこのレースの処理を中断

                
                dict_stadium = {'桐生': 'KRY', '戸田': 'TDA', '江戸川': 'EDG', '平和島': 'HWJ', '多摩川': 'TMG', '浜名湖': 'HMN', '蒲郡': 'GMG', '常滑': 'TKN', '津': 'TSU', '三国': 'MKN', '琵琶湖': 'BWK','びわこ': 'BWK', '住之江': 'SME', '尼崎': 'AMG', '鳴門': 'NRT', '丸亀': 'MRG', '児島': 'KJM', '宮島': 'MYJ', '徳山': 'TKY', '下関': 'SMS', '若松': 'WKM', '芦屋': 'ASY', '福岡': 'FKO', '唐津': 'KRT', '大村': 'OMR'}
                race_code_date = date.replace('年', '').replace('月', '').replace('日', '')
                stadium_code = dict_stadium.get(stadium, 'XXX')
                
                if race_code_date and stadium_code and race_round:
                    item['race_code'] = f"{race_code_date}{stadium_code}{race_round.zfill(2)}"
                else:
                    item['race_code'] = "CODE_GENERATION_ERROR"

                players_data_list = []
                player_line_idx = i + 5
                while player_line_idx < len(lines) and lines[player_line_idx].strip() != "" and "END" not in lines[player_line_idx]:
                    p_line = lines[player_line_idx]
                    player_data = {
                        '枠': p_line[0], '登録番号': p_line[2:6], '選手名': p_line[6:10], '年齢': p_line[10:12],
                        '支部': p_line[12:14], '体重': p_line[14:16], '級別': p_line[16:18],
                        '全国勝率': p_line[19:23], '全国2連対率': p_line[24:29],
                        '当地勝率': p_line[30:34], '当地2連対率': p_line[35:40],
                        'モーター番号': p_line[41:43], 'モーター2連対率': p_line[44:49],
                        'ボート番号': p_line[50:52], 'ボート2連対率': p_line[53:58],
                        '今節成績': p_line[59:71], '早見': p_line[71:73]
                    }
                    players_data_list.append(player_data)
                    player_line_idx += 1
                item['players_data'] = players_data_list
                
                yield item