import scrapy
import os
from datetime import datetime as dt, timedelta as td

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# class OddsSpider(scrapy.Spider):
#     name = "odds_spider"

#     # 開始日と終了日を指定
#     start_date = dt.strptime('2024-08-01', '%Y-%m-%d')
#     end_date = dt.strptime('2024-08-31', '%Y-%m-%d')

#     # ファイルの保存先を指定
#     save_dir = "odds_data/odds_HTML"
#     if not os.path.exists(save_dir):
#         print("ディレクトリを作成します")
#         os.makedirs(save_dir)

#     def __init__(self, *args, **kwargs):
#         super(OddsSpider, self).__init__(*args, **kwargs)
#         self.start_time = None
#         self.end_time = None
#         self.saved_files_count = 0

#     def start_requests(self):
#         base_url = "https://www.boatrace.jp/owpc/pc/race/odds3f"
#         current_date = self.start_date

#         while current_date <= self.end_date:
#             date_str = current_date.strftime('%Y%m%d')
#             for jcd in range(1, 25):
#                 for rno in range(1, 13):
#                     url = f"{base_url}?rno={rno}&jcd={jcd:02d}&hd={date_str}"
#                     yield scrapy.Request(url, callback=self.parse, meta={'date_str': date_str, 'jcd': jcd, 'rno': rno})

#             # jcd = 5   # 多摩川
#             for rno in range(1, 13):
#                 url = f"{base_url}?rno={rno}&jcd={jcd:02d}&hd={date_str}"
#                 yield scrapy.Request(url, callback=self.parse, meta={'date_str': date_str, 'jcd': jcd, 'rno': rno})
#             current_date += td(days=1)

#     def parse(self, response):
#         date_str = response.meta['date_str']
#         jcd = response.meta['jcd']
#         rno = response.meta['rno']

#         # ファイルのパスを生成
#         file_path = f"{self.save_dir}/{date_str}_{jcd:02d}_{rno:02d}R.html"
        
#         # "データがありません"のチェック
#         if "データがありません" in response.text:
#             self.log(f"Skipping {response.url} - No data")
#             return

#         # ファイルが存在しない場合のみ保存
#         if not os.path.exists(file_path):
#             with open(file_path, 'w', encoding='UTF-8') as file:
#                 file.write(response.text)
#             self.log(f"Saved file {file_path}")
#             self.saved_files_count += 1
#         else:
#             self.log(f"File already exists, skipping {file_path}")

#     def close(self, reason):
#         self.end_time = dt.now()
#         total_time = self.end_time - self.start_time
#         self.log(f"Start time: {self.start_time}")
#         self.log(f"End time: {self.end_time}")
#         self.log(f"Total time: {total_time}")
#         self.log(f"Total saved HTML files: {self.saved_files_count}")


class OddsSpider(scrapy.Spider):
    name = "odds_spider"

    # 開始日と終了日を指定
    start_date = dt.strptime('2024-08-01', '%Y-%m-%d')
    end_date = dt.strptime('2024-08-02', '%Y-%m-%d')

    def __init__(self, *args, **kwargs):
        super(OddsSpider, self).__init__(*args, **kwargs)
        
        # --- ▼▼▼ Google Drive連携処理を追加 ▼▼▼ ---
        print("Google Driveの認証を開始します...")

        settings = {
            'client_config_file': '../client_secrets.json', 
        }
        gauth = GoogleAuth(settings=settings)
        # ローカルWebサーバー経由で認証（初回以降は保存された認証情報を使用）
        gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(gauth)
        self.drive_folder_id = '1G0-CcHvddy4sZOQxLG_FCEphcCLNrbBY'
        print("Google Driveの認証が完了しました。")
        # --- ▲▲▲ ここまで ▲▲▲ ---

        # 実行時間の計測開始
        self.start_time = dt.now()
        self.end_time = None
        self.saved_files_count = 0

    def start_requests(self):
        base_url = "https://www.boatrace.jp/owpc/pc/race/odds3f"
        current_date = self.start_date

        while current_date <= self.end_date:
            date_str = current_date.strftime('%Y%m%d')
            for jcd in range(1, 25):
                for rno in range(1, 13):
                    url = f"{base_url}?rno={rno}&jcd={jcd:02d}&hd={date_str}"
                    # meta情報にファイル名を渡す
                    file_name = f"{date_str}_{jcd:02d}_{rno:02d}R.html"
                    yield scrapy.Request(url, callback=self.parse, meta={'file_name': file_name})
            current_date += td(days=1)

    def parse(self, response):
        file_name = response.meta['file_name']
        
        # "データがありません"のチェック
        if "データがありません" in response.text:
            self.log(f"Skipping {response.url} - No data")
            return

        # --- ▼▼▼ ローカル保存からGoogle Driveへのアップロードに変更 ▼▼▼ ---
        try:
            # Drive上に同名ファイルが存在するかチェック
            file_list = self.drive.ListFile(
                {'q': f"'{self.drive_folder_id}' in parents and title='{file_name}' and trashed=false"}
            ).GetList()

            if not file_list:
                # ファイルが存在しない場合のみアップロード
                file_drive = self.drive.CreateFile({
                    'title': file_name,
                    'parents': [{'id': self.drive_folder_id}]
                })
                file_drive.SetContentString(response.text)
                file_drive.Upload()
                
                self.log(f"Uploaded file to Google Drive: {file_name}")
                self.saved_files_count += 1
            else:
                # ファイルが既に存在する場合
                self.log(f"File already exists in Google Drive, skipping: {file_name}")
        
        except Exception as e:
            self.log(f"An error occurred during Google Drive operation: {e}")
        # --- ▲▲▲ ここまで ▲▲▲ ---

    def close(self, reason):
        self.end_time = dt.now()
        if self.start_time:
            total_time = self.end_time - self.start_time
            self.log(f"Total time: {total_time}")
        self.log(f"Start time: {self.start_time}")
        self.log(f"End time: {self.end_time}")
        self.log(f"Total saved HTML files to Google Drive: {self.saved_files_count}")
