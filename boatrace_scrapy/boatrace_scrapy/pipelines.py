# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import csv
from itemadapter import ItemAdapter


class InfoScrapyPipeline:
    def open_spider(self, spider):
        """スパイダー開始時に呼ばれる"""
        # 保存するCSVファイル名を定義
        self.file_name = f"info_{spider.START_DATE}_{spider.END_DATE}.csv"
        # ファイルを開き、CSVライターを準備
        self.file = open(self.file_name, 'w', newline='', encoding='utf-8-sig')
        self.writer = csv.writer(self.file)
        
        # ヘッダーを定義して書き込む
        header = [
            'レースコード', 'タイトル', '日次', 'レース日', 'レース場', 'レース回', 'レース名', '距離', '電話投票締切予定'
        ]
        player_header_template = [
            '{n}枠_艇番', '{n}枠_登録番号', '{n}枠_選手名', '{n}枠_年齢', '{n}枠_支部', '{n}枠_体重', '{n}枠_級別',
            '{n}枠_全国勝率', '{n}枠_全国2連対率', '{n}枠_当地勝率', '{n}枠_当地2連対率',
            '{n}枠_モーター番号', '{n}枠_モーター2連対率', '{n}枠_ボート番号', '{n}枠_ボート2連対率',
            '1枠_今節成績_1-1', '1枠_今節成績_1-2', '1枠_今節成績_2-1', '1枠_今節成績_2-2', '1枠_今節成績_3-1', '1枠_今節成績_3-2',
            '1枠_今節成績_4-1', '1枠_今節成績_4-2', '1枠_今節成績_5-1', '1枠_今節成績_5-2', '1枠_今節成績_6-1', '1枠_今節成績_6-2', '{n}枠_早見'
        ]
        
        for i in range(1, 7):
            header.extend([h.format(n=i) for h in player_header_template])
        
        self.writer.writerow(header)

    def close_spider(self, spider):
        """スパイダー終了時に呼ばれる"""
        self.file.close()

    def process_item(self, item, spider):
        """Itemがスパイダーから渡されるたびに呼ばれる"""
        adapter = ItemAdapter(item)
        
        # 基本情報をリストとして準備
        row = [
            adapter.get('race_code'), adapter.get('title'), adapter.get('day_num'),
            adapter.get('date'), adapter.get('stadium'), adapter.get('race_round'),
            adapter.get('race_name'), adapter.get('distance'), adapter.get('post_time')
        ]
        
        # 選手データをフラットなリストに展開して追加
        players_data = adapter.get('players_data', [])
        for i in range(6): # 6艇分のデータを保証
            if i < len(players_data):
                p_data = players_data[i]
                # 元のデータ構造に合わせて今節成績を分割
                seiseki = p_data.get('今節成績', '').ljust(12) # 12文字に満たない場合はスペースで埋める
                seiseki_split = [seiseki[j:j+1] for j in range(12)]
                
                row.extend([
                    p_data.get('枠'), p_data.get('登録番号'), p_data.get('選手名'), p_data.get('年齢'),
                    p_data.get('支部'), p_data.get('体重'), p_data.get('級別'),
                    p_data.get('全国勝率'), p_data.get('全国2連対率'),
                    p_data.get('当地勝率'), p_data.get('当地2連対率'),
                    p_data.get('モーター番号'), p_data.get('モーター2連対率'),
                    p_data.get('ボート番号'), p_data.get('ボート2連対率'),
                    *seiseki_split, # 分割した成績を展開して追加
                    p_data.get('早見')
                ])
            else:
                # データがない場合は空欄を追加 (28は選手1人あたりのカラム数)
                row.extend([''] * 28)
        
        self.writer.writerow(row)
        return item

class OddsScrapyPipeline:
    def process_item(self, item, spider):
        return item
    
