import anndata as ad
import pandas as pd
import numpy as np
import os

def tcga_to_bulk_adata(directory, df_sample, biospecimen_df, TCGA=None):
    # ディレクトリ内のファイルリストを取得し、条件に合うものだけをソートして選択
    file_in_directory = sorted([filename for filename in os.listdir(directory) if filename.startswith('TCGA')])
    dfs = []  # DataFrameを格納するためのリスト
    tumor_descriptors = []  # tumor_descriptorを格納するためのリスト
    column_names = []  # 列名（サンプルID）を格納するためのリスト
    count = 0
    for filename in file_in_directory:
        count += 1
        full_path = os.path.join(directory, filename)
        column_name_16 = filename[:16]

        # df_sampleからtumor_descriptorを取得
        if column_name_16 in df_sample['sample_submitter_id'].values:
            tumor_descriptor = df_sample.loc[df_sample['sample_submitter_id'] == column_name_16, 'tumor_descriptor'].iloc[0]
        else:
            tumor_descriptor = None
        tumor_descriptors.append(tumor_descriptor)
        column_names.append(column_name_16)

        # ファイルを読み込み、'unstranded'列のみを保持
        df = pd.read_csv(full_path, sep='\t', skiprows=[0,2,3,4,5], usecols=['gene_name', 'unstranded'], index_col='gene_name')
        df = df.rename(columns={'unstranded': column_name_16})  # 列名を設定
        dfs.append(df)
    print(count, 'bulk data loaded')

    # DataFrameを結合
    df_combined = pd.concat(dfs, axis=1)
    df_combined.loc['tumor_descriptor'] = tumor_descriptors

    # 列名の重複を確認
    duplicates = df_combined.columns[df_combined.columns.duplicated(keep=False)]
    unique_duplicates = set(duplicates)  # 重複しているユニークな列名を取得
    
    for col_name in unique_duplicates:#16桁のIDが重複している列名について、それぞれのIDに対応する列を抽出し、それらの合計値が最も大きい列を残す
        df_combined_col = df_combined.loc[:, col_name]
        df_combined_col.columns = [col_name + f'_{i}' for i in range(len(df_combined_col.columns))]
        total_counts = df_combined_col.drop('tumor_descriptor').sum(axis=0)
        most_biggest = total_counts.astype(int).idxmax()
        df_combined = df_combined.drop(columns=col_name)
        df_combined[col_name] = df_combined_col[most_biggest]
    columns_to_keep = []
    

    for unique_id in set(column_name[:12] for column_name in column_names):
        # 現在のIDに対応する列を抽出
        cols = [col for col in column_names if col.startswith(unique_id)]
        cols = list(set(cols))
        #print(cols)
        # primary_cols = [col for col in cols if df_combined.loc['tumor_descriptor', col] == 'Primary']
        primary_cols = [col for col in cols if 'Primary' in df_combined.loc['tumor_descriptor', col]]
        meta_cols = [col for col in cols if 'Metastatic' in df_combined.loc['tumor_descriptor', col]]
        all_cols = [df_combined.loc['tumor_descriptor', col] for col in cols]

        if len(primary_cols) > 1:
            total_counts = df_combined[primary_cols].drop('tumor_descriptor').sum(axis=0)
            most_biggest = total_counts.astype(int).idxmax()
            # combined_col = df_combined[primary_cols].sum(axis=1)
            # new_col_name = primary_cols[0] + '_' + primary_cols[1]
            # df_combined[new_col_name] = combined_col
            # df_combined = df_combined.drop(columns=unique_id)
            print('Primary > 1 data.', f"Combined columns for ID {unique_id}({all_cols}): {primary_cols} -> most_biggest {most_biggest}")
            columns_to_keep.append(most_biggest)
        elif len(primary_cols) == 1:
            columns_to_keep.append(primary_cols[0])
        else:
            if len(meta_cols) == 1:
                columns_to_keep.append(meta_cols[0])
            elif len(meta_cols) > 1:
                total_counts = df_combined[meta_cols].drop('tumor_descriptor').sum(axis=0)
                most_biggest = total_counts.astype(int).idxmax()
                print('Meta > 1 data.', f"Combined ID {unique_id}({all_cols}): {meta_cols} -> most_biggest {most_biggest}")
                columns_to_keep.append(most_biggest)
            elif len(cols) == 1:
                print(cols, 'only 1 column', all_cols[0])
                columns_to_keep.append(cols[0])
            else:
                print(cols)
                print('No primary or metastatic columns found for ID', unique_id)
                raise ValueError('No primary or metastatic columns found')
                
    df_filtered = df_combined[columns_to_keep]
    df_filtered = df_filtered.T

    index_name_16 = df_filtered.index
    df_filtered.index = df_filtered.index.str.slice(0, 12)
    tumor_descriptor_ = df_filtered.T.loc['tumor_descriptor']
    df_filtered = df_filtered.T
    df_filtered = df_filtered.drop('tumor_descriptor')
    df_filtered = df_filtered.T
    bulk_adata = ad.AnnData(df_filtered)
    bulk_adata.obs['sample_submitter_id'] = index_name_16
    bulk_adata.obs['tumor_descriptor'] = tumor_descriptor_.astype(str)
    bulk_adata.X = bulk_adata.X.astype(np.int64)
    bulk_adata.obs['days_to_sample_procurement'] = None
    for idx in list(bulk_adata.obs_names):
        if idx in list(biospecimen_df['bcr_patient_barcode']):
            bulk_adata.obs['days_to_sample_procurement'][idx] = biospecimen_df['days_to_sample_procurement'][biospecimen_df['bcr_patient_barcode'] == idx].item()
    return bulk_adata

def make_biospecimen_df(biospecimen_path):
    biospecimen_df = pd.read_csv(biospecimen_path, sep='\t', skiprows=[0, 2])
    biospecimen_df = biospecimen_df[['bcr_patient_barcode', 'days_to_sample_procurement']]
    biospecimen_df = biospecimen_df.drop_duplicates()
    biospecimen_df['days_to_sample_procurement'] = pd.to_numeric(biospecimen_df['days_to_sample_procurement'], errors='coerce')
    biospecimen_df = biospecimen_df.groupby('bcr_patient_barcode', as_index=False).min()
    return biospecimen_df

def make_clinical_df(clinical_path, bulk_adata):
    filter_columns = list(bulk_adata.obs_names)
    clinical_df = pd.read_csv(clinical_path, sep='\t')
    clinical_df = clinical_df[['case_submitter_id', 'vital_status', 'days_to_death', 'days_to_last_follow_up']]
    clinical_df = clinical_df.drop_duplicates(subset='case_submitter_id')
    clinical_df = clinical_df[clinical_df['case_submitter_id'].isin(filter_columns)]
    clinical_df = clinical_df.set_index('case_submitter_id')
    clinical_df = clinical_df.loc[filter_columns]
    clinical_df['days_to_death'] = pd.to_numeric(clinical_df['days_to_death'], errors='coerce')
    clinical_df['days_to_last_follow_up'] = pd.to_numeric(clinical_df['days_to_last_follow_up'], errors='coerce')
    bulk_adata.obs['days_to_death'] = clinical_df['days_to_death']
    bulk_adata.obs['vital_status'] = clinical_df['vital_status']
    bulk_adata.obs['days_to_last_follow_up'] = clinical_df['days_to_last_follow_up']
    return bulk_adata

def select_survival_time(row, TCGA):
    if TCGA == 'OV':
        if pd.notna(row['days_to_sample_procurement']):
            if pd.notna(row['days_to_death']):
                return row['days_to_death']- row['days_to_sample_procurement']
            elif pd.notna(row['days_to_last_follow_up']):
                return row['days_to_last_follow_up'] - row['days_to_sample_procurement']
            else:
                return None
        else:
            if pd.notna(row['days_to_death']):
                return row['days_to_death'] 
            elif pd.notna(row['days_to_last_follow_up']):
                return row['days_to_last_follow_up']
            else:
                return None
    else:
        if pd.notna(row['days_to_sample_procurement']):
            if pd.notna(row['days_to_death']) and pd.notna(row['days_to_sample_procurement']):
                return row['days_to_death']- row['days_to_sample_procurement']
            elif pd.notna(row['days_to_last_follow_up']) and pd.notna(row['days_to_sample_procurement']):
                return row['days_to_last_follow_up'] - row['days_to_sample_procurement']
            else:
                # return 0
                return None
        else:
            return None