from pathlib import Path
from re import search

import numpy as np
import pandas as pd
import xlwings as xw
from pandas import offsets


base_dir = r'v:\Findep\Incoming\test\DevOps'

total_df = pd.DataFrame()
for file in Path(base_dir).glob("*бух*справка*"):
    with xw.App(visible=False) as app:
        wkb = app.books.open(file, read_only=True, update_links=False)
        for sht in wkb.sheets:
            if search(r"эрлисар|татрус|нтц инвест", sht.name.lower()) != None:
                rng = sht.used_range
                df = rng.options(pd.DataFrame, index=False).value
                col_idx = [
                    (x[0]) for x in df.iterrows() if "Период" in x[1].tolist()
                ]
                df.columns = df.iloc[col_idx[0], :].str.strip()
                df = df.drop(index=range(col_idx[0] + 1))
                df.dropna(how='all', inplace=True, axis=1)
                df.dropna(how='all', inplace=True, axis=0)
                df = df[[x for x in df.columns if x not in [None, "", 'nan', np.nan, "None"] and not pd.isna(x)]]
                df['sht_name'] = sht.name
                total_df = pd.concat([total_df, df])

            elif search("свод", sht.name.lower()) != None:
                rng = sht.used_range
                svod = rng.options(pd.DataFrame, index=False).value
                col_idx = [
                    (x[0]) for x in svod.iterrows() if "на начало 2023 год" in x[1].tolist()
                ]
                svod.columns = svod.iloc[col_idx[0], :].str.strip()
                svod = svod.drop(index=range(col_idx[0] + 2))
                svod = svod.iloc[:, slice(0, 6)]
                svod.columns = ['IFRS', 'Corp Account', 'Rap_acc', 'SAP_acc', 'Closing Balance_Dr',
                                'Closing Balance_Cr']
                # svod['C']
                svod.loc[:, ['IFRS', 'SAP_acc']] = svod.loc[:, ['IFRS', 'SAP_acc']].map(
                    lambda x: str(x).split(".")[0]
                )
                svod = svod[svod['IFRS'].apply(lambda x: x not in [None, "", "None"] and not pd.isna(x))]

OB_Initial_Amount = svod.iloc[0, :]['Closing Balance_Dr']
# OB_Cumulated_DDA = svod.iloc[1,:]['Opening Balance_Cr']
total_df['Дата'] = total_df['Дата'].astype('datetime64[ns]').dt.date
total_df['Дата'] = (total_df['Дата'] + offsets.MonthEnd()).astype('datetime64[ns]').dt.date
