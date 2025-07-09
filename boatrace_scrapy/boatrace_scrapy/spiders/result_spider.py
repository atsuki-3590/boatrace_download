import scrapy
import requests
import lhafile
import io
import re
import os
from datetime import datetime, timedelta
from boatrace_scrapy.utils import get_gdrive_service, list_drive_files
from boatrace_scrapy.items import ResultItem

class ResultSpider(scrapy.Spider):
    name = 'Result_Spider'

    # --- 設定項目 ---
    START_DATE = "2024-08-01"
    END_DATE = "2024-08-03"
    FIXED_URL = "http://www1.mbrace.or.jp/od2/K/{yyyymm}/k{yymmdd}.lzh"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log("Google Driveの認証を開始します...")
        self.drive = get_gdrive_service()
        self.lzh_folder_id = os.getenv('RESULT_LZH_FOLDER_ID')
        self.txt_folder_id = os.getenv('RESULT_TXT_FOLDER_ID')
        self.csv_folder_id = os.getenv('RESULT_CSV_FOLDER_ID')
        self.log("Google Driveの認証が完了しました。")

    # ★★★ 修正点: start_requests を async def start に変更 ★★★
    async def start(self):
        """
        Scrapyの非同期処理と連携するためのエントリーポイント。
        ダウンロード、解凍、パース処理を順次実行する。
        """
        self.log("====== 全処理開始 ======")

        # --- フェーズ1: LZHダウンロード ---
        self.log("====== フェーズ1: LZHダウンロード開始 ======")
        existing_lzh_obj = list_drive_files(self.drive, self.lzh_folder_id)
        existing_lzh_files = [f['title'] for f in existing_lzh_obj]
        
        start_date_obj = datetime.strptime(self.START_DATE, '%Y-%m-%d')
        end_date_obj = datetime.strptime(self.END_DATE, '%Y-%m-%d')
        current_date = start_date_obj

        while current_date <= end_date_obj:
            yymmdd = current_date.strftime("%y%m%d")
            file_name = f"k{yymmdd}.lzh"

            if file_name not in existing_lzh_files:
                yyyymm = current_date.strftime("%Y%m")
                url = self.FIXED_URL.format(yyyymm=yyyymm, yymmdd=yymmdd)
                self.log(f"Downloading: {url}")
                try:
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

        # --- フェーズ2: TXTファイル解凍 ---
        self.log("====== フェーズ2: TXTファイル解凍開始 ======")
        lzh_files = list_drive_files(self.drive, self.lzh_folder_id)
        txt_files_obj = list_drive_files(self.drive, self.txt_folder_id)
        existing_txt_names = [f['title'] for f in txt_files_obj]
        
        for lzh_file in lzh_files:
            lzh_name = lzh_file['title']
            expected_txt_name = lzh_name.replace('k', 'K').replace('.lzh', '.TXT')

            if expected_txt_name not in existing_txt_names:
                self.log(f"Unzipping required for: {lzh_name}")
                try:
                    lzh_content_stream = lzh_file.GetContentIOBuffer()
                    lzh_bytes = lzh_content_stream.read()
                    lzh_in_memory_file = io.BytesIO(lzh_bytes)
                    lha = lhafile.Lhafile(lzh_in_memory_file)

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
        
        # ★★★ 修正点: Scrapy.Requestを使わず、直接ファイルを処理する ★★★
        for txt_file in txt_files:
            self.log(f"Parsing: {txt_file['title']}")
            try:
                # Driveから直接テキスト内容を取得
                text_data = txt_file.GetContentString(encoding='shift_jis')
                # パース処理を行い、Itemを直接yieldする
                for item in self._parse_content(text_data):
                    yield item
            except Exception as e:
                self.log(f"Failed to read or parse {txt_file['title']}: {e}")

    def _parse_content(self, text_data):
        """
        競争成績TXTファイルの内容を解析し、ResultItemを生成する。
        """
        lines = text_data.splitlines()
        trans_asc = str.maketrans('１２３４５６７８９０Ｒ．：　', '1234567890R.: ')
        
        stadium, race_date, title, day_num = "", "", "", ""
        race_data = {}

        # 選手成績の正規表現をより柔軟に修正
        racer_pattern = re.compile(
             r'^\s*([ＦLSEＫ失C\d])\s+'  # 1. 着順 (F,L,S,E,K,失,C,数字)
             r'(\d)\s+'                 # 2. 艇番
             r'(\d{4})\s+'              # 3. 登録番号
             r'(.{4})\s+'               # 4. 選手名 (4文字)
             r'(\d{2})\s+'              # 5. モーター番号
             r'(\d{2})\s+'              # 6. ボート番号
             r'(.{8})\s+'               # 7. 展示タイム (8文字)
             r'(\d)\s+'                 # 8. 進入コース
             r'(F?\.?\d{2})\s+'         # 9. スタートタイミング
             r'(\d\.\d{2}\.\d)\s*$'      # 10. レースタイム
        )

        for line in lines:
            line = line.translate(trans_asc)
            
            # ヘッダー情報のパース
            if "成績表" in line:
                stadium = line[0:3].strip()
                match_date = re.search(r'(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日', line)
                if match_date:
                    race_date = f"{match_date.group(1)}{int(match_date.group(2)):02d}{int(match_date.group(3)):02d}"
                title_match = re.search(r'「(.*?)」', line)
                title = title_match.group(1).strip() if title_match else ""
                day_num_match = re.search(r'(\d)\s*日目', line)
                day_num = day_num_match.group(1) if day_num_match else ""
                continue

            # レース見出し行のパース
            match = re.search(r'([0-9]{1,2}R)\s+(.*?)\s+H?([0-9]+m)', line)
            if match:
                if race_data:
                    race_data['result_racer'] = ",".join(race_data.get('result_racer', []))
                    yield ResultItem(**race_data)
                
                race_round_str = match.group(1).replace('R', '')
                race_data = {
                    'stadium': stadium, 'date': race_date, 'title': title, 'day': day_num,
                    'race_round': race_round_str.zfill(2) + 'R',
                    'race_name': match.group(2).strip(),
                    'distance': re.sub(r'\D', '', match.group(3)),
                    'result_racer': []
                }
                dict_stadium = {'桐生': 'KRY', '戸田': 'TDA', '江戸川': 'EDG', '平和島': 'HWJ', '多摩川': 'TMG', '浜名湖': 'HMN', '蒲郡': 'GMG', '常滑': 'TKN', '津': 'TSU', '三国': 'MKN', '琵琶湖': 'BWK','びわこ': 'BWK', '住之江': 'SME', '尼崎': 'AMG', '鳴門': 'NRT', '丸亀': 'MRG', '児島': 'KJM', '宮島': 'MYJ', '徳山': 'TKY', '下関': 'SMS', '若松': 'WKM', '芦屋': 'ASY', '福岡': 'FKO', '唐津': 'KRT', '大村': 'OMR'}
                stadium_code = dict_stadium.get(stadium, 'XXX')
                race_data['race_code'] = f"{race_date}{stadium_code}{race_round_str.zfill(2)}"
                continue

            if not race_data: continue

            # 気象情報のパース
            weather_match = re.search(r'天候\s*(.*?)\s*風向\s*(.*?)\s*風速\s*(\d+m)\s*波\s*(\d+cm)', line)
            if weather_match:
                race_data['weather'] = weather_match.group(1).strip()
                race_data['wind_direction'] = weather_match.group(2).strip()
                race_data['wind_velocity'] = re.sub(r'\D', '', weather_match.group(3))
                race_data['wave_height'] = re.sub(r'\D', '', weather_match.group(4))
                continue

            if "決まり手" in line: race_data['winning_technique'] = line.split("決まり手")[1].strip()
            if "単勝" in line: race_data['result_win'] = ",".join(line.split()[1:])
            if "複勝" in line: race_data['result_place_show'] = ",".join(line.split()[1:])
            if "2連単" in line: race_data['result_exacta'] = ",".join(line.split()[1:])
            if "2連複" in line: race_data['result_quinella'] = ",".join(line.split()[1:])
            if "拡連複" in line: race_data['result_quinella_place'] = ",".join(line.split()[1:])
            if "3連単" in line: race_data['result_trifecta'] = ",".join(line.split()[1:])
            if "3連複" in line: race_data['result_trio'] = ",".join(line.split()[1:])
                
            # 各艇成績のパース
            racer_match = racer_pattern.match(line)
            if racer_match:
                # 着順,艇番,登録番号,選手名,モーター,ボート,展示,進入,ST,レースタイム
                g = racer_match.groups()
                race_data['result_racer'].extend([
                    g[0], g[1], g[2], g[3].strip(), g[4], g[5], g[6].strip(), g[7], g[8], g[9]
                ])
                
        if race_data:
            race_data['result_racer'] = ",".join(race_data.get('result_racer', []))
            yield ResultItem(**race_data)