import scrapy
import os
from datetime import datetime as dt, timedelta as td

class OddsSpider(scrapy.Spider):
    name = "odds_spider"

    # 開始日と終了日を指定
    start_date = dt.strptime('2020-01-01', '%Y-%m-%d')
    end_date = dt.strptime('2024-09-30', '%Y-%m-%d')

    # ファイルの保存先を指定
    save_dir = "odds_data/odds_HTML"
    if not os.path.exists(save_dir):
        print("ディレクトリを作成します")
        os.makedirs(save_dir)

    def __init__(self, *args, **kwargs):
        super(OddsSpider, self).__init__(*args, **kwargs)
        self.start_time = None
        self.end_time = None
        self.saved_files_count = 0

    def start_requests(self):
        base_url = "https://www.boatrace.jp/owpc/pc/race/odds3f"
        current_date = self.start_date

        while current_date <= self.end_date:
            date_str = current_date.strftime('%Y%m%d')
            # for jcd in range(1, 25):
            #     for rno in range(1, 13):
            #         url = f"{base_url}?rno={rno}&jcd={jcd:02d}&hd={date_str}"
            #         yield scrapy.Request(url, callback=self.parse, meta={'date_str': date_str, 'jcd': jcd, 'rno': rno})

            jcd = 5   # 多摩川
            for rno in range(1, 13):
                url = f"{base_url}?rno={rno}&jcd={jcd:02d}&hd={date_str}"
                yield scrapy.Request(url, callback=self.parse, meta={'date_str': date_str, 'jcd': jcd, 'rno': rno})
            current_date += td(days=1)

    def parse(self, response):
        date_str = response.meta['date_str']
        jcd = response.meta['jcd']
        rno = response.meta['rno']

        # ファイルのパスを生成
        file_path = f"{self.save_dir}/{date_str}_{jcd:02d}_{rno:02d}R.html"
        
        # "データがありません"のチェック
        if "データがありません" in response.text:
            self.log(f"Skipping {response.url} - No data")
            return

        # ファイルが存在しない場合のみ保存
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='UTF-8') as file:
                file.write(response.text)
            self.log(f"Saved file {file_path}")
            self.saved_files_count += 1
        else:
            self.log(f"File already exists, skipping {file_path}")

    def close(self, reason):
        self.end_time = dt.now()
        total_time = self.end_time - self.start_time
        self.log(f"Start time: {self.start_time}")
        self.log(f"End time: {self.end_time}")
        self.log(f"Total time: {total_time}")
        self.log(f"Total saved HTML files: {self.saved_files_count}")