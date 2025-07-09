# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import csv
import io
from itemadapter import ItemAdapter


class InfoScrapyPipeline:
    def __init__(self):
        """初期化処理。アイテムを貯めるリストを準備"""
        self.items = []
        self.drive = None
        self.csv_folder_id = None
        self.start_date = None
        self.end_date = None

    def open_spider(self, spider):
        """
        スパイダー開始時に呼ばれる。
        スパイダーからGoogle Driveの接続情報と日付設定を受け取る。
        """
        self.drive = spider.drive
        self.csv_folder_id = spider.csv_folder_id
        self.start_date = spider.START_DATE
        self.end_date = spider.END_DATE
        
        # ヘッダーを定義
        header = [
            'レースコード', 'タイトル', '日次', 'レース日', 'レース場', 'レース回', 'レース名', '距離', '電話投票締切予定'
        ]
        player_header_template = [
            '{n}枠_艇番', '{n}枠_登録番号', '{n}枠_選手名', '{n}枠_年齢', '{n}枠_支部', '{n}枠_体重', '{n}枠_級別',
            '{n}枠_全国勝率', '{n}枠_全国2連対率', '{n}枠_当地勝率', '{n}枠_当地2連対率',
            '{n}枠_モーター番号', '{n}枠_モーター2連対率', '{n}枠_ボート番号', '{n}枠_ボート2連対率',
            '{n}枠_今節成績_1-1', '{n}枠_今節成績_1-2', '{n}枠_今節成績_2-1', '{n}枠_今節成績_2-2', '{n}枠_今節成績_3-1', '{n}枠_今節成績_3-2',
            '{n}枠_今節成績_4-1', '{n}枠_今節成績_4-2', '{n}枠_今節成績_5-1', '{n}枠_今節成績_5-2', '{n}枠_今節成績_6-1', '{n}枠_今節成績_6-2', '{n}枠_早見'
        ]
        for i in range(1, 7):
            # player_header_template内の'{n}枠_今節成績...'は元のコードのままだとバグの元なので修正
            current_player_header = []
            for h in player_header_template:
                # 複雑な今節成績ヘッダーは1枠のものをそのまま使うという元の仕様を維持しつつ、単純なヘッダーは枠番で置換
                if '今節成績' in h:
                    current_player_header.append(h.format(n=1))
                else:
                    current_player_header.append(h.format(n=i))
            header.extend(current_player_header)

        # ヘッダー行をメモリ上のリストの先頭に追加
        self.items.append(header)

    def close_spider(self, spider):
        """
        スパイダー終了時に呼ばれる。
        メモリ上の全データをCSV化し、Google Driveにアップロードする。
        """
        if len(self.items) <= 1:
            spider.log("データが抽出されなかったため、CSVファイルの作成をスキップします。")
            return
            
        spider.log("すべてのデータをCSVに変換し、Google Driveへアップロードします...")
        
        # メモリ上でCSVファイルを作成
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(self.items)
        csv_content = output.getvalue()
        output.close()
        
        # Google Driveにアップロード
        try:
            def to_yyyymmdd(date_val):
                if hasattr(date_val, 'strftime'):
                    return date_val.strftime('%Y%m%d')
                elif isinstance(date_val, str):
                    # 例: '2024-08-01' → '20240801'
                    return date_val.replace('-', '')
                else:
                    return str(date_val) if date_val else "unknown"

            start_date_str = to_yyyymmdd(self.start_date)
            end_date_str = to_yyyymmdd(self.end_date)
            csv_file_name = f"info_{start_date_str}_{end_date_str}.csv"
            csv_drive_file = self.drive.CreateFile({
                'title': csv_file_name,
                'parents': [{'id': self.csv_folder_id}],
                'mimeType': 'text/csv'
            })
            # contentをセットする際はUTF-8でエンコードしたバイト列にする
            csv_drive_file.content = io.BytesIO(csv_content.encode('utf-8-sig'))
            csv_drive_file.Upload()
            spider.log(f"CSVファイルのアップロードが完了しました: {csv_file_name}")
        except Exception as e:
            spider.log(f"CSVファイルのGoogle Driveへのアップロード中にエラーが発生しました: {e}")

    def process_item(self, item, spider):
        """
        Itemが渡されるたびに呼ばれる。
        データをメモリ上のリストに追記する。
        """
        adapter = ItemAdapter(item)
        row = [
            adapter.get('race_code'), adapter.get('title'), adapter.get('day_num'),
            adapter.get('date'), adapter.get('stadium'), adapter.get('race_round'),
            adapter.get('race_name'), adapter.get('distance'), adapter.get('post_time')
        ]
        players_data = adapter.get('players_data', [])
        for i in range(6):
            if i < len(players_data):
                p_data = players_data[i]
                seiseki = p_data.get('今節成績', '').ljust(12)
                seiseki_split = [seiseki[j:j+1] for j in range(12)]
                
                player_row = [
                    p_data.get('枠'), p_data.get('登録番号'), p_data.get('選手名'), p_data.get('年齢'),
                    p_data.get('支部'), p_data.get('体重'), p_data.get('級別'),
                    p_data.get('全国勝率'), p_data.get('全国2連対率'),
                    p_data.get('当地勝率'), p_data.get('当地2連対率'),
                    p_data.get('モーター番号'), p_data.get('モーター2連対率'),
                    p_data.get('ボート番号'), p_data.get('ボート2連対率'),
                    *seiseki_split,
                    p_data.get('早見')
                ]
                row.extend(player_row)
            else:
                row.extend([''] * 28)
        
        self.items.append(row)
        return item
    

class OddsScrapyPipeline:
    def process_item(self, item, spider):
        return item
    
