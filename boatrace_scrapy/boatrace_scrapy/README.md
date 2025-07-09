# boatrace_scrapy 仕様書（番組表データ取得版）

## 概要

本プロジェクトは、ボートレースの「番組表データ（info）」をWebから自動取得し、Google Driveに保存・管理するためのScrapyベースのクローラーです。
主に「番組表データ（LZH形式）」のダウンロード、解凍、テキスト解析、CSV化、Google Driveへのアップロードを自動化します。

---

## ディレクトリ構成（主要部分）

```
boatrace_scrapy/
├─ scrapy.cfg
├─ boatrace_scrapy/
│  ├─ __init__.py
│  ├─ items.py
│  ├─ middlewares.py
│  ├─ pipelines.py
│  ├─ settings.py
│  ├─ utils.py
│  └─ spiders/
│     ├─ __init__.py
│     ├─ info_spider.py
│     └─ odds_spider.py（未使用）
```

---

## 主なファイル・役割

### items.py

- `InfoItem`：番組表データ1レース分の情報を格納するItemクラス。
  - レース基本情報（race_code, title, date, stadium など）
  - 各選手情報（players_data：辞書リスト）

### pipelines.py

- `InfoScrapyPipeline`：取得したItemをメモリ上でCSV化し、Google Driveへアップロードするパイプライン。
  - スパイダー開始時にヘッダー行を作成
  - スパイダー終了時に全データをCSV化し、Google Driveへアップロード

### utils.py

- Google Drive APIの認証・ファイル一覧取得用のユーティリティ関数を提供
  - `get_gdrive_service()`
  - `list_drive_files(drive, folder_id)`

### spiders/info_spider.py

- 番組表データ取得のメインスパイダー
  - `START_DATE`, `END_DATE` で取得期間を指定
  - LZHファイルのダウンロード（Google Driveに保存）
  - LZHファイルの解凍（TXTファイルをGoogle Driveに保存）
  - TXTファイルの内容をパースし、Itemとして出力
  - 取得したItemはパイプラインでCSV化・Google Driveへアップロード

---

## データ取得フロー

1. **LZHファイルのダウンロード**
   - 指定期間のLZHファイルをWebからダウンロード
   - 既にGoogle Driveに存在する場合はスキップ

2. **LZHファイルの解凍**
   - Google Drive上のLZHファイルを解凍し、TXTファイルとしてGoogle Driveに保存
   - 既にTXTファイルが存在する場合はスキップ

3. **TXTファイルのパース**
   - TXTファイルを1行ずつ解析し、レース情報・選手情報を抽出
   - `InfoItem`として出力

4. **CSV化・Google Driveアップロード**
   - すべてのItemをCSVファイルにまとめ、Google Driveの指定フォルダにアップロード

---

## 取得データ例

- ファイル名例：`info_20240801_20240803.csv`
- CSVカラム例：
  - レースコード, タイトル, 日次, レース日, レース場, レース回, レース名, 距離, 電話投票締切予定, 1枠_艇番, ... 6枠_早見

---

## 注意事項

- Google Driveの各種フォルダIDは環境変数で指定
- 取得対象は「番組表データ（info）」のみ（競争成績やオッズ等は未対応）
- `odds_spider.py` や `OddsScrapyItem` など未使用コードが一部存在

---

## 今後の拡張例

- 競争成績データやオッズデータの取得対応
- 取得データの自動前処理・分析
- エラー通知やリトライ機能の強化

---

ご要望に応じて、より詳細なクラス・関数仕様や処理フロー図も作成可能です。
