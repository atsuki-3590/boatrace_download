# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import csv
import io
from itemadapter import ItemAdapter
# Itemクラスをインポート
from .items import InfoItem, ResultItem


class InfoScrapyPipeline:
    def __init__(self):
        """初期化処理。アイテムを貯めるリストを準備"""
        self.items = []
        self.drive = None
        self.csv_folder_id = None
        self.start_date = None
        self.end_date = None

    def open_spider(self, spider):
        # InfoSpiderの場合のみヘッダーを追加するようにする
        if spider.name == 'Info_Spider':
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
                current_player_header = [h.format(n=i) for h in player_header_template]
                header.extend(current_player_header)

            self.items.append(header)

    def close_spider(self, spider):
        # itemsリストにデータがある場合（ヘッダー含む）のみ処理
        if not self.items:
            return
            
        spider.log(f"すべてのデータをCSVに変換し、Google Driveへアップロードします...(Info)")
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(self.items)
        csv_content = output.getvalue()
        output.close()
        
        try:
            def to_yyyymmdd(date_val):
                if hasattr(date_val, 'strftime'): return date_val.strftime('%Y%m%d')
                elif isinstance(date_val, str): return date_val.replace('-', '')
                return str(date_val) if date_val else "unknown"

            start_date_str = to_yyyymmdd(self.start_date)
            end_date_str = to_yyyymmdd(self.end_date)
            csv_file_name = f"info_{start_date_str}_{end_date_str}.csv"
            csv_drive_file = self.drive.CreateFile({
                'title': csv_file_name, 'parents': [{'id': self.csv_folder_id}], 'mimeType': 'text/csv'
            })
            csv_drive_file.content = io.BytesIO(csv_content.encode('utf-8-sig'))
            csv_drive_file.Upload()
            spider.log(f"CSVファイルのアップロードが完了しました: {csv_file_name}")
        except Exception as e:
            spider.log(f"CSVファイルのGoogle Driveへのアップロード中にエラーが発生しました: {e}")

    def process_item(self, item, spider):
        # ★★★ 修正点 ★★★
        # InfoItemでなければ、何もせずitemを次のパイプラインに渡す
        if not isinstance(item, InfoItem):
            return item

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
                # '今節成績'がない場合も考慮
                seiseki = p_data.get('今節成績', '').ljust(12)
                seiseki_split = [seiseki[j:j+2] for j in range(0, 12, 2)] # 2文字ずつ分割
                
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
                # 1選手あたりのカラム数に合わせて空文字を追加
                row.extend([''] * 21) # 15(基本) + 6(成績) + 1(早見) = 22
        
        self.items.append(row)
        return item


class ResultScrapyPipeline:
    def __init__(self):
        self.items = []
        self.drive = None
        self.csv_folder_id = None
        self.start_date = None
        self.end_date = None

    def open_spider(self, spider):
        # ResultSpiderの場合のみヘッダーを追加するようにする
        if spider.name == 'Result_Spider':
            self.drive = spider.drive
            self.csv_folder_id = spider.csv_folder_id
            self.start_date = spider.START_DATE
            self.end_date = spider.END_DATE
            self.header = [
                'レースコード', 'タイトル', '日次', 'レース日', 'レース場', 'レース回', 'レース名', '距離', '天候', '風向', '風速', '波の高さ', '決まり手',
                '単勝_艇番', '単勝_払戻金',
                '複勝_1着_艇番', '複勝_1着_払戻金', '複勝_2着_艇番', '複勝_2着_払戻金',
                '2連単_組番', '2連単_払戻金', '2連単_人気',
                '2連複_組番', '2連複_払戻金', '2連複_人気',
                '拡連複_1-2着_組番', '拡連複_1-2着_払戻金', '拡連複_1-2着_人気',
                '拡連複_1-3着_組番', '拡連複_1-3着_払戻金', '拡連複_1-3着_人気',
                '拡連複_2-3着_組番', '拡連複_2-3着_払戻金', '拡連複_2-3着_人気',
                '3連単_組番', '3連単_払戻金', '3連単_人気',
                '3連複_組番', '3連複_払戻金', '3連複_人気',
                '1着_着順', '1着_艇番', '1着_登録番号', '1着_選手名', '1着_モーター番号', '1着_ボート番号', '1着_展示タイム', '1着_進入コース', '1着_スタートタイミング', '1着_レースタイム',
                '2着_着順', '2着_艇番', '2着_登録番号', '2着_選手名', '2着_モーター番号', '2着_ボート番号', '2着_展示タイム', '2着_進入コース', '2着_スタートタイミング', '2着_レースタイム',
                '3着_着順', '3着_艇番', '3着_登録番号', '3着_選手名', '3着_モーター番号', '3着_ボート番号', '3着_展示タイム', '3着_進入コース', '3着_スタートタイミング', '3着_レースタイム',
                '4着_着順', '4着_艇番', '4着_登録番号', '4着_選手名', '4着_モーター番号', '4着_ボート番号', '4着_展示タイム', '4着_進入コース', '4着_スタートタイミング', '4着_レースタイム',
                '5着_着順', '5着_艇番', '5着_登録番号', '5着_選手名', '5着_モーター番号', '5着_ボート番号', '5着_展示タイム', '5着_進入コース', '5着_スタートタイミング', '5着_レースタイム',
                '6着_着順', '6着_艇番', '6着_登録番号', '6着_選手名', '6着_モーター番号', '6着_ボート番号', '6着_展示タイム', '6着_進入コース', '6着_スタートタイミング', '6着_レースタイム',
            ]
            self.items.append(self.header)

    def close_spider(self, spider):
        if not self.items:
            return
            
        spider.log("すべてのデータをCSVに変換し、Google Driveへアップロードします...(Result)")
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(self.items)
        csv_content = output.getvalue()
        output.close()
        try:
            def to_yyyymmdd(date_val):
                if hasattr(date_val, 'strftime'): return date_val.strftime('%Y%m%d')
                elif isinstance(date_val, str): return date_val.replace('-', '')
                return str(date_val) if date_val else "unknown"

            start_date_str = to_yyyymmdd(self.start_date)
            end_date_str = to_yyyymmdd(self.end_date)
            csv_file_name = f"result_{start_date_str}_{end_date_str}.csv"
            csv_drive_file = self.drive.CreateFile({
                'title': csv_file_name, 'parents': [{'id': self.csv_folder_id}], 'mimeType': 'text/csv'
            })
            csv_drive_file.content = io.BytesIO(csv_content.encode('utf-8-sig'))
            csv_drive_file.Upload()
            spider.log(f"CSVファイルのアップロードが完了しました: {csv_file_name}")
        except Exception as e:
            spider.log(f"CSVファイルのGoogle Driveへのアップロード中にエラーが発生しました: {e}")

    def process_item(self, item, spider):
        # ★★★ 修正点 ★★★
        # ResultItemでなければ、何もせずitemを次のパイプラインに渡す
        if not isinstance(item, ResultItem):
            return item
        
        # itemから直接値を取得してリストを作成
        row = [
            item.get('race_code'), item.get('title'), item.get('day'), item.get('date'), item.get('stadium'),
            item.get('race_round'), item.get('race_name'), item.get('distance'), item.get('weather'),
            item.get('wind_direction'), item.get('wind_velocity'), item.get('wave_height'), item.get('winning_technique'),
            # split(',')でカンマ区切りの文字列をリストに展開
            *(item.get('result_win', '').split(',')),
            *(item.get('result_place_show', '').split(',')),
            *(item.get('result_exacta', '').split(',')),
            *(item.get('result_quinella', '').split(',')),
            *(item.get('result_quinella_place', '').split(',')),
            *(item.get('result_trifecta', '').split(',')),
            *(item.get('result_trio', '').split(',')),
            *(item.get('result_racer', '').split(',')),
        ]
        self.items.append(row)
        return item