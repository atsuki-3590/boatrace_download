import pandas as pd

print("作業を開始します")

df_info = pd.read_csv("data_csv/new_info.csv")
df_result = pd.read_csv("data_csv/new_result.csv")

# df_info1 = pd.read_csv("data_csv/info.csv", encoding = "shift-jis")
# df_result1 = pd.read_csv("data_csv/result.csv", encoding = "shift-jis")

print("読み込みに成功しました")

concatenate_df = pd.merge(df_info, df_result, on='レースコード', how='inner')
concatenate_df.to_csv("data_csv/concatenate.csv", index=False, encoding = "utf-8")

# data_df = pd.merge(df_info, df_result, on='レースコード', how='inner')
# data_df.to_csv("data_csv/data.csv", index=False, encoding = "shift-jis")

print("作業を終了しました")