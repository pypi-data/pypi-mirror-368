import numpy as np
import pandas as pd

from hmcis_packs.parsers.exceldata import ExcelParser
from hmcis_packs.parsers.txtdata import TxtParser


class GetCustomers:
    def __init__(self, filepath, value):

        self.dataframe = TxtParser(filepath, value).read_data()

        self.Mobility_Filepath = r'V:\Hyundai Mobility\Incoming\New Status report\Status report 2.0.xlsm'
        self.MobilityPtShtName = 'Клиенты'

        self.AS_Filepath = r'V:\Findep\Incoming\test\DevOps\References\Payment Terms\Срок отсрочки платежа 191023.xlsx'
        self.ASPtShtNameRetail = 'Розница'
        self.ASPtShtNameOpt = 'ОПТ'

        self.MobilityPT = ExcelParser(self.Mobility_Filepath,
                                      self.MobilityPtShtName,
                                      'SAP код').read_data()

        self.ASPT_retail = ExcelParser(self.AS_Filepath,
                                       self.ASPtShtNameRetail,
                                       'Контрагент').read_data()

        self.ASPT_retail['Channel'] = "Retail"
        self.ASPT_retail = self.ASPT_retail.assign(Sap_code_and_channel=self.ASPT_retail['Контрагент.Код SAP'] + "_" +
                                                                        self.ASPT_retail['Channel'])
        self.ASPT_retail.drop_duplicates(subset=['Sap_code_and_channel'], keep='first', inplace=True)
        self.ASPT_retail.rename(columns={"Допустимое число дней дебиторской задолженности": 'Отсрочка платежа'},
                                inplace=True)
        self.ASPT_retail['Отсрочка платежа'] = (self.ASPT_retail['Отсрочка платежа'].
                                                astype(str).apply(lambda x: x.replace("None", '0')))
        self.ASPT_retail['Отсрочка платежа'] = self.ASPT_retail['Отсрочка платежа'].str.split(".").str.get(0).apply(
            lambda x: 0 if x == 'nan' else int(x))

        self.ASPT_opt = ExcelParser(self.AS_Filepath,
                                    self.ASPtShtNameOpt,
                                    'Контрагент').read_data()

        self.ASPT_opt['Channel'] = "WholeSales"
        self.ASPT_opt.rename(columns={"Допустимое число дней дебиторской задолженности": 'Отсрочка платежа'},
                             inplace=True)
        self.ASPT_opt = self.ASPT_opt.assign(Sap_code_and_channel=self.ASPT_opt['Контрагент.Код SAP'] + "_" +
                                                                  self.ASPT_opt['Channel'])
        self.ASPT_opt.drop_duplicates(subset=['Sap_code_and_channel'], keep='first', inplace=True)

    def further_process(self):
        df = self.dataframe
        df = df[['KUNNR', 'LAND1', 'NAME1', 'NAME2', 'ORT01', 'PSTLZ', 'REGIO', 'SORTL', 'STRAS',
                 'TELF1', 'TELFX', 'XCPDK', 'ADRNR', 'MCOD1', 'MCOD2', 'MCOD3', "LOEVM"]]
        df = df[(~df['LAND1'].isin([None, "None", ])) & (df['LOEVM'].isin(['X', "None"]) == False) & (
                df["LAND1"].str.len() == 2)
                ]
        df['KUNNR'] = df['KUNNR'].astype(str).str.split(".").str.get(0)
        df = df[df['LAND1'].apply(lambda x: len(str(x)) == 2)]
        self.MobilityPT.loc[:, 'SAP код'] = self.MobilityPT.loc[:, 'SAP код'].astype(str).str.split(".").str.get(0)
        self.MobilityPT[r'Отсрочка платежа (дн.)'] = self.MobilityPT[r'Отсрочка платежа (дн.)'].astype(str)
        self.MobilityPT = self.MobilityPT.loc[:,
                          ['Сейлз', 'Менеджер', 'Клиент', 'ИНН', 'SAP код', 'Номер Договора аренды',
                           'Дата Договора аренды',
                           'Отсрочка платежа (дн.)', 'ЭДО', 'Статус клиента']]

        merged_df = pd.merge(df, self.MobilityPT, left_on='KUNNR', right_on='SAP код', how='left', sort=False)
        merged_df_with_retail = pd.merge(merged_df, self.ASPT_retail, left_on='KUNNR', right_on='Контрагент.Код SAP',
                                         how='left', sort=False)
        merged_df_with_ws = pd.merge(merged_df_with_retail, self.ASPT_opt, left_on='KUNNR',
                                     right_on='Контрагент.Код SAP',
                                     how='left', sort=False)
        cols_to_drop = [  # 'Сейлз', 'Менеджер',
            'Клиент', 'ИНН_x', 'SAP код', 'Номер Договора аренды',
            'Дата Договора аренды', 'ЭДО', 'Статус клиента', 'Контрагент_x', 'ИНН_y', 'КПП_x',
            'Код дилера_x', 'Контрагент.Код SAP_x', 'Основной договор контрагента_x', 'Ведение взаиморасчетов_x',
            'Sap_code_and_channel_x', 'Контрагент_y', 'ИНН', 'КПП_y', 'Код дилера_y',
            'Контрагент.Код SAP_y', 'Основной договор контрагента_y', 'Ведение взаиморасчетов_y',
            'Sap_code_and_channel_y']
        merged_df_with_ws.drop(columns=cols_to_drop, inplace=True)
        f = lambda x: 0 if x in [None, "", np.nan, 'None'] else x
        merged_df_with_ws['Отсрочка платежа (дн.)'] = merged_df_with_ws['Отсрочка платежа (дн.)'].apply(f)
        merged_df_with_ws['Отсрочка платежа_x'] = merged_df_with_ws['Отсрочка платежа_x'].apply(f)
        merged_df_with_ws['Отсрочка платежа_x'] = merged_df_with_ws['Отсрочка платежа_x'].apply(
            lambda x: 0 if pd.isna(x) else x)
        merged_df_with_ws['Отсрочка платежа_y'] = merged_df_with_ws['Отсрочка платежа_y'].apply(f)
        cols = {
            "Отсрочка платежа_x": "Отсрочка платежа, дни, розница",
            "Отсрочка платежа_y": "Отсрочка платежа, дни, опт"
        }
        merged_df_with_ws.rename(columns=cols, inplace=True)

        @np.vectorize
        def custom_function(x: pd.Series, y: pd.Series, z: pd.Series):
            if pd.notna(x) and pd.isna(y):
                return "AS_" + x
            if pd.notna(x) and pd.notna(y):
                return "AS_" + y
            elif pd.isna(x) and pd.notna(y):
                return "AS_" + y
            elif z != 0:
                return "Mobility channel"

            elif pd.isna(x) and pd.isna(y):
                return 'not applicable'

        merged_df_with_ws['channel'] = custom_function(merged_df_with_ws['Channel_x'], merged_df_with_ws['Channel_y'],
                                                       merged_df_with_ws['Отсрочка платежа (дн.)'])
        merged_df_with_ws = merged_df_with_ws.drop(columns=['Channel_x', 'Channel_y'])

        return merged_df_with_ws


if __name__ == '__main__':
    parse_data = GetCustomers(
        filepath=r'\\hms-dfs-01\\root$\\FinDep\\Incoming\\test\\DevOps\\References\\KNA1 26012024.txt',
        value='KUNNR')

    df = parse_data.further_process()
    df.to_clipboard()
