import locale
import re
import shutil
from datetime import datetime
from pathlib import Path
from re import Pattern

import numpy as np
import pandas as pd
import xlwings as xw
from dateparser import parse
from pandas.tseries.offsets import MonthEnd

from hmcis_packs import ExcelParser


class FixedAssets:

    def __init__(self, current_period: str = None, previous_period: str = None):
        self.date_handler = lambda year, month, day, **kwargs: "%04i-%02i-%02i" % (year, month, day)
        self.wb = xw.Book.caller()
        print(self.wb.name)
        self.sht = self.wb.sheets[0]
        self.reporting_date_string = self.sht['c2'].options(dates=self.date_handler).value
        self.reporting_date_object = (
                parse(self.reporting_date_string, languages=['ru', 'en']).date() + MonthEnd(0)).date()
        locale.setlocale(locale.LC_ALL, "ru-RU")
        self.Month_name = self.reporting_date_object.strftime("%B")
        locale.setlocale(locale.LC_ALL, "en-EN")
        self.current_period = current_period
        self.previous_period = previous_period

    def define_excel_file_name(self):
        if self.current_period:
            self.reporting_date_object = (self.reporting_date_object + MonthEnd(0)).date()
            print(self.reporting_date_object)
        else:
            self.reporting_date_object = (self.reporting_date_object + MonthEnd(-1)).date()
            print(self.reporting_date_object)
        for item in Path(r"V:\Findep\Incoming\test\DevOps\Fixed assets\DataSource_Backups").rglob("*"):
            pattern = r'\d+\b'
            found_string = re.search(pattern, item.name).group()
            adjusted_string = found_string[:2] + "." + found_string[2:4] + "." + found_string[4:]
            target_date = (parse(adjusted_string, languages=['ru']).date() + MonthEnd(-1)).date()
            if target_date == self.reporting_date_object:
                return Path(item).resolve()

    @staticmethod
    def backup_excel_file():
        shutil.copy(
            src=r'V:\Accounting\Work\ОТДЕЛ ЗАТРАТ\Основные средства и НМА\Амортизация\2025\!Амортизация_ помесячно_БУ_2025.xlsx',
            dst=r'V:/Findep/Incoming/test/DevOps/Fixed assets/DataSource_Backups/!Амортизация_помесячно_БУ_2025_backed up on' + datetime.now().strftime(
                "%d%m%Y") + '.xlsx'
        )

    def read_data_from_excel_file(self):
        df = ExcelParser(self.define_excel_file_name(), str(self.Month_name).lower(), "Класс").read_data()
        df.reset_index(inplace=True, drop=True)
        row_idx = df.index[df.eq("Списание:").any(axis=1)]
        df.drop(index=range(row_idx[0], df.shape[0]), inplace=True)
        df.rename(columns={df.columns[0]: "Sales Indicator"}, inplace=True)
        df['МВЗ'] = df['МВЗ'].astype(str).str.split(".").str.get(0)
        y = [x[0] for x in enumerate(df.columns == 'АГ') if x[1] == True][0]
        df = df.rename(columns={df.columns[y - 1]: "СПИ_2"})

        df = df[pd.notna(df['Класс'])]

        pattern: Pattern[str] = re.compile(
            r'(\bTMA\w*)|(\bXW\w*)|(\bKM\w*)|(\bZ94\w*)|(\bLBE\w*)|(\bVIN\s202\w*)|(\bVIN\s000\w*)')

        @np.vectorize
        def search_text_fragment(x: pd.Series = None):
            if x := re.search(pattern, x):
                return x.group()

        @np.vectorize
        def find_car_name_string(vin_code_text_string, whole_text_string):
            if vin_code_text_string:
                return whole_text_string[:len(whole_text_string) - len(vin_code_text_string)]

        df['VIN_code'] = search_text_fragment(df['Название основного средства'].astype(str))
        df['Car name'] = find_car_name_string(df['VIN_code'], df['Название основного средства'])

        conds = [

            (df['МВЗ'].isin(['44001', '99013'])) & (df['Класс'] == 'HA01B08'),

            (df['МВЗ'].isin(['99015'])) & (df['Класс'] == 'HA01B08'),

            (df['МВЗ'].isin(['11002'])) & (df['Класс'] == 'HA01B03'),

            (df['МВЗ'].isin(['55001'])) & (df['Класс'] == 'HA01B03'),

            (df['МВЗ'].isin(['99004', '44001'])) & (df['Класс'] == 'HA01B03'),

            (~df['VIN_code'].isin([None])) & (df['Класс'] == 'HA01B02')
            & (~df['Название основного средства'].astype(str).str.startswith('Пассажирский электромобиль')),

        ]
        choices = [
            'Mobility',
            'Business Mobility',
            'Corporate',
            'Courtesy',
            'Other cars',
            'Fixed assets_Other',
        ]
        df['category'] = np.select(conds, choices, default=None)
        df = df.rename(
            columns={
                df.columns[8]: "DDA for period",
                df.columns[9]: 'Acc.DDA',
                'ПСт': 'Initial PPE Cost'
            }
        )

        conds_2 = [
            df['category'].isin([None]) & df['Класс'].isin(['HA01A01'])
            & (~np.array([False if x is None else x for x in df['Название основного средства'].str.contains(
                r"(ТЗ|Фотопроизведение|Каталог изображ|Дизайн одежды)", flags=re.I)])),
            df['category'].isin([None]) & df['Класс'].isin(['HA01A01'])
            & (np.array([False if x is None else x for x in df['Название основного средства'].str.contains(
                r"(ТЗ|Фотопроизведение|Каталог изображ|Дизайн одежды)", flags=re.I)])),
            df['category'].isin([None]) & df['Класс'].isin(['HA01A04']),
            df['category'].isin([None]) & df['Класс'].isin(['HA01B01']),
            df['category'].isin([None]) & df['Класс'].isin(['HA01B02']),
            df['category'].isin([None]) & df['Класс'].isin(['HA01B04']),
            df['category'].isin([None]) & df['Класс'].isin(['HA01B05']),
            df['category'].isin([None]) & df['Класс'].isin(['HA01B06']),
            df['category'].isin([None]) & df['Класс'].isin(['HA01B10']),
        ]
        choices_2 = [
            'Software',
            'Other intangible assets',
            'Software Mobility',
            'IT',
            'Furniture&HTA Equipment',
            'Machinery equipments',
            'Buildings',
            'Structures',
            'Operating lease assets non cars',
        ]

        df['category'] = np.select(conds_2, choices_2, default=df['category'])

        conds_3 = [
            (
                    pd.Series([pd.Timestamp(x).date() for x in df['Д/оприход.']]).astype(
                        'datetime64[ns]').dt.month_name() == self.reporting_date_object.strftime('%B')
            )
            & (
                    pd.Series([pd.Timestamp(x).date() for x in df['Д/оприход.']]).astype(
                        'datetime64[ns]').dt.year == int(self.reporting_date_object.strftime('%Y'))
            ),
            [False if pd.isna(x) else x for x in
             df['Sales Indicator'].str.contains('реализация|годные остатки', flags=re.IGNORECASE)],

        ]

        choices_3 = [
            'acquired',
            'disposals',

        ]

        df['flow type'] = np.select(conds_3, choices_3, default='closing balance')
        df['Acc.DDA at beginning of the period'] = df['Acc.DDA'] - df['DDA for period']

        # agg_func = {"Initial PPE Cost": "sum", "DDA for period": "sum", "Acc.DDA": "sum",
        #             'Acc.DDA at beginning of the period': "sum", 'ОснСредство': np.count_nonzero}
        # grouped_df = df.groupby(by=['category',
        #                             'flow type'], dropna=False).agg(agg_func).reset_index()
        # pivoted_df = grouped_df.melt(id_vars=['category', 'flow type'], var_name='variable',
        #                              value_name='Amount/count')

        return df

    def create_grouped_df(self):
        df = self.read_data_from_excel_file().copy()
        agg_func = {"Initial PPE Cost": "sum", "DDA for period": "sum", "Acc.DDA": "sum",
                    'Acc.DDA at beginning of the period': "sum", 'ОснСредство': np.count_nonzero}
        grouped_df = df.groupby(by=['category',
                                    'flow type'], dropna=False).agg(agg_func).reset_index()
        return grouped_df

    def create_pivoted_df(self):
        df = self.create_grouped_df().copy()
        pivoted_df = df.melt(id_vars=['category', 'flow type'], var_name='variable',
                             value_name='Amount/count')
        return pivoted_df


if __name__ == '__main__':
    wkb_path = r'V:\Findep\Incoming\test\DevOps\Fixed assets\Fixed Assets.xlsm'
    xw.Book(wkb_path).set_mock_caller()
    x = FixedAssets(current_period='yes')
    x.read_data_from_excel_file().to_clipboard()
    # x.backup_excel_file()
