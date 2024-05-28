import os
import re
import lhafile

#  データ解凍
# ダウンロードしたLZHファイルが保存されている場所を指定
LZH_FILE_DIR = "払い戻しデータ_解凍前/"

# 解凍したファイルを保存する場所を指定
TEXT_FILE_DIR = "払い戻しデータ_解凍後/"
# 解凍先ディレクトリが存在しない場合は作成
if not os.path.exists(TEXT_FILE_DIR):
    print("ディレクトリを作成します")
    os.makedirs(TEXT_FILE_DIR, exist_ok=True)

# 開始合図
print("作業を開始します")

# LZHファイルのリストを取得
lzh_file_list = os.listdir(LZH_FILE_DIR)

# リストからファイル名を順に取り出す
for lzh_file_name in lzh_file_list:
    # 拡張子が lzh のファイルに対してのみ実行
    if re.search(".lzh$", lzh_file_name):
        lzh_file_path = os.path.join(LZH_FILE_DIR, lzh_file_name)
        try:
            file = lhafile.Lhafile(lzh_file_path)
            # 解凍するファイルの名前を取得
            info = file.infolist()
            for f in info:
                file_name = f.filename
                extracted_file_path = os.path.join(TEXT_FILE_DIR, file_name)
                
                # 既に解凍されたファイルが存在する場合はスキップ
                if not os.path.exists(extracted_file_path):
                    # ファイル名を指定して保存
                    with open(extracted_file_path, 'wb') as output_file:
                        output_file.write(file.read(file_name))
                    print(extracted_file_path + " を解凍しました")
                else:
                    print(extracted_file_path + " はすでに存在します")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            
# 終了合図
print("解凍作業を終了しました")

