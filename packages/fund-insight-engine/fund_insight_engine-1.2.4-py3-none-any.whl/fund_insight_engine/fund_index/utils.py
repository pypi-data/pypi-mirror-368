from functools import partial
import numpy as np
import pandas as pd
from string_date_controller import get_today, get_date_n_days_ago
from shining_pebbles import scan_files_including_regex
from canonical_transformer.morphisms import map_df_to_csv, map_csv_to_df
from fund_insight_engine.fund_data_retriever.fund_codes import get_fund_codes_all
from fund_insight_engine.fund_data_retriever.fund_codes.historical import (
    get_historical_fund_codes_all,
    get_historical_fund_codes_main, 
    get_historical_fund_codes_division_01, 
    get_historical_fund_codes_division_02, 
    get_historical_fund_codes_equity, 
    get_historical_fund_codes_equity_mixed, 
    get_historical_fund_codes_bond_mixed, 
    get_historical_fund_codes_multi_asset, 
    get_historical_fund_codes_variable, 
    get_historical_fund_codes_mothers, 
    get_historical_fund_codes_class, 
    get_historical_fund_codes_generals, 
    get_historical_fund_codes_nonclassified,
)
from fund_insight_engine.path_director import FILE_FOLDER
from .basis import get_df_fund_index


def get_fund_index_total(option_save: bool = True)->pd.DataFrame:
    df_fund_index_total = get_df_fund_index(fund_codes_kernel=get_historical_fund_codes_all)
    if option_save:
        map_df_to_csv(df_fund_index_total, file_folder=FILE_FOLDER['fund_index'], file_name=f'dataset-fund_index_total-save{get_today().replace("-", "")}.csv')
    return df_fund_index_total

def correct_fund_index(df_fund_index):
    df = df_fund_index.copy()
    df.loc[get_date_n_days_ago(df.index[0], 1), :] = np.nan
    df = df.sort_index()
    for col in df.columns:
        first_valid_idx = df[col].first_valid_index()
        if first_valid_idx is not None:
            INITIAL_PRICE = 1000.00
            df.loc[get_date_n_days_ago(first_valid_idx, 1), col] = INITIAL_PRICE
    return df

def load_fund_index_total(file_folder: str = FILE_FOLDER['fund_index'], regex='dataset-fund_index_total-')->pd.DataFrame:
    file_names = scan_files_including_regex(file_folder=file_folder, regex=regex)
    file_name = file_names[-1]
    df = map_csv_to_df(file_folder=file_folder, file_name=file_name)
    return df

def map_label_to_historical_fund_codes_kernel(label: str):
    return {
        'all': get_historical_fund_codes_all,
        'main': get_historical_fund_codes_main,
        'division_01': get_historical_fund_codes_division_01,
        'division_02': get_historical_fund_codes_division_02,
        'equity': get_historical_fund_codes_equity,
        'equity_mixed': get_historical_fund_codes_equity_mixed,
        'bond_mixed': get_historical_fund_codes_bond_mixed,
        'multi_asset': get_historical_fund_codes_multi_asset,
        'variable': get_historical_fund_codes_variable,
        'mothers': get_historical_fund_codes_mothers,
        'class': get_historical_fund_codes_class,
        'generals': get_historical_fund_codes_generals,
        'nonclassified': get_historical_fund_codes_nonclassified,
    }[label]

def get_fund_index_by_label(label: str, option_save: bool = True)->pd.DataFrame:
    df_fund_index_total = load_fund_index_total()
    df_fund_index_by_label = df_fund_index_total[map_label_to_historical_fund_codes_kernel(label)]
    if option_save:
        map_df_to_csv(df_fund_index_by_label, file_folder=FILE_FOLDER['fund_index'], file_name=f'dataset-fund_index_{label}-save{get_today().replace("-", "")}.csv')
    return df_fund_index_by_label

get_fund_index_all = partial(get_fund_index_by_label, label='all')
get_fund_index_main = partial(get_fund_index_by_label, label='main')
get_fund_index_division_01 = partial(get_fund_index_by_label, label='division_01')
get_fund_index_division_02 = partial(get_fund_index_by_label, label='division_02')
get_fund_index_equity = partial(get_fund_index_by_label, label='equity')
get_fund_index_equity_mixed = partial(get_fund_index_by_label, label='equity_mixed')
get_fund_index_bond_mixed = partial(get_fund_index_by_label, label='bond_mixed')
get_fund_index_multi_asset = partial(get_fund_index_by_label, label='multi_asset')
get_fund_index_variable = partial(get_fund_index_by_label, label='variable')
get_fund_index_mothers = partial(get_fund_index_by_label, label='mothers')
get_fund_index_class = partial(get_fund_index_by_label, label='class')
get_fund_index_generals = partial(get_fund_index_by_label, label='generals')
get_fund_index_nonclassified = partial(get_fund_index_by_label, label='nonclassified')
