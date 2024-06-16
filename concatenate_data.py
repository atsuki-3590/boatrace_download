import pandas as pd

print("作業を開始します")

df_info = pd.read_csv("data_csv/new_info.csv")
df_result = pd.read_csv("data_csv/new_result.csv")

concatenate_df = pd.merge(df_info, df_result, on='レースコード', how='inner')
concatenate_df.to_csv("data_csv/concatenate.csv", index=False)

print("作業を終了しました")