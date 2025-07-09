
import scrapy
import requests
import os
from datetime import datetime, timedelta
from boatrace_scrapy.utils import get_gdrive_service, list_drive_files

class OddsSpider(scrapy.Spider):
    name = 'Odds_Spider'

    # --- 設定項目 ---
    START_DATE = "2024-08-01"
    END_DATE = "2024-08-02"
    BASE_URL = "https://www.boatrace.jp/owpc/pc/race/odds3f"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log("Google Driveの認証を開始します...")
        self.drive = get_gdrive_service()
        self.lzh_folder_id = os.getenv('RESULT_LZH_FOLDER_ID')
        self.txt_folder_id = os.getenv('RESULT_TXT_FOLDER_ID')
        self.csv_folder_id = os.getenv('RESULT_CSV_FOLDER_ID')
        self.html_folder_id = os.getenv('RESULT_ODDS_HTML_FOLDER_ID') or self.csv_folder_id  # 必要に応じて追加
        self.log("Google Driveの認証が完了しました。")

        self.saved_files_count = 0
        self.start_time = datetime.now()
        self.end_time = None

    async def start(self):
        start_date_obj = datetime.strptime(self.START_DATE, '%Y-%m-%d')
        end_date_obj = datetime.strptime(self.END_DATE, '%Y-%m-%d')
        current_date = start_date_obj
        while current_date <= end_date_obj:
            date_str = current_date.strftime('%Y%m%d')
            for jcd in range(1, 25):
                for rno in range(1, 13):
                    url = f"{self.BASE_URL}?rno={rno}&jcd={jcd:02d}&hd={date_str}"
                    file_name = f"{date_str}_{jcd:02d}_{rno:02d}R.html"
                    yield scrapy.Request(url, callback=self.parse, meta={'file_name': file_name})
            current_date += timedelta(days=1)

    def parse(self, response):
        file_name = response.meta['file_name']
        if "データがありません" in response.text:
            self.log(f"Skipping {response.url} - No data")
            return
        try:
            file_list = self.drive.ListFile(
                {'q': f"'{self.html_folder_id}' in parents and title='{file_name}' and trashed=false"}
            ).GetList()
            if not file_list:
                file_drive = self.drive.CreateFile({
                    'title': file_name,
                    'parents': [{'id': self.html_folder_id}]
                })
                file_drive.SetContentString(response.text)
                file_drive.Upload()
                self.log(f"Uploaded file to Google Drive: {file_name}")
                self.saved_files_count += 1
            else:
                self.log(f"File already exists in Google Drive, skipping: {file_name}")
        except Exception as e:
            self.log(f"An error occurred during Google Drive operation: {e}")

    def close(self, reason):
        self.end_time = datetime.now()
        if self.start_time:
            total_time = self.end_time - self.start_time
            self.log(f"Total time: {total_time}")
        self.log(f"Start time: {self.start_time}")
        self.log(f"End time: {self.end_time}")
        self.log(f"Total saved HTML files to Google Drive: {self.saved_files_count}")
