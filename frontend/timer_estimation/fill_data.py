from compileall import compile_path

import numpy as np
import pandas as pd

comp_path = "../comp.csv"
processed_path = "../processed_data.csv"


df = pd.read_csv(comp_path, usecols=["alg", "time", "number", "length", "source", "dest"])

df['number'] = df['number'].astype(int)
existing_triplets = df[['alg', 'source', 'dest']].drop_duplicates()
numbers_range_df = pd.DataFrame({'number': range(7)})

existing_triplets['_key'] = 1
numbers_range_df['_key'] = 1

expected_structure = pd.merge(existing_triplets, numbers_range_df, on='_key').drop('_key', axis=1)
df_expanded = pd.merge(expected_structure, df, on=['alg', 'source', 'dest', 'number'], how='left')
df_expanded['time'] = df_expanded['time'].fillna(300)
rows_with_number_0 = df_expanded[df_expanded['number'] == 0].copy()
length_mapping = rows_with_number_0.drop_duplicates(subset=['source', 'dest'], keep='first')[['source', 'dest', 'length']]
length_mapping = length_mapping.rename(columns={'length': 'length_at_number_0'})
df_final = pd.merge(df_expanded, length_mapping, on=['source', 'dest'], how='left')
df_final = df_final.sort_values(by=['alg', 'source', 'dest', 'number']).reset_index(drop=True)

subset_cols = ["alg", "source", "dest", "number"]
df_final = df_final.drop_duplicates(subset=subset_cols, keep='first')
df_final.to_csv(processed_path, index=False)
