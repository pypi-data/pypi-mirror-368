from copy import deepcopy

import numpy as np
import pandas as pd

from hmcis_packs import MasterData, ExcelParser

pd.options.display.width = None


# pd.options.mode.use_inf_as_na = True


class OBAdj:
    """
    This class shall be  used for getting OB adjustments from accounting files
    """

    def __init__(self, filepath, sht_name, master_data: pd.DataFrame = None,
                 ):
        self.dataframe = ExcelParser(filepath, sht_name, "Rus Account", retain_duplicates=True).read_data()
        self.dataframe = self.dataframe.iloc[:, slice(1, 13)]
        self.dataframe['Corp Acc'] = self.dataframe['Corp Acc']. \
            astype(str).str.split(".").str.get(0)
        self.master_data = master_data
        self.master_data['Local Account Code'] = self.master_data['Local Account Code']. \
            astype(str).str.split(".").str.get(0)
        self.dataframe = self.dataframe[
            self.dataframe['Corp Acc'].isin(self.master_data['Local Account Code'])]

        self.mydict = self.master_data.drop_duplicates(subset='Rus Account', keep='first').set_index(
            "Rus Account").T.to_dict()
        self.mydict2 = self.master_data.drop_duplicates(subset='Local Account Code', keep='first').set_index(
            "Local Account Code").T.to_dict()

    def further_process(self):
        self.dataframe.columns = ['col' + str(x) for x in range(len(self.dataframe.columns))]
        cols_to_be = [
            'Rus Account', 'Corp Acc', 'RUS_Text', 'ENG_Text', 'Initials_Dr', 'Initials_Cr',
            'OB_adj_Dr', 'OB_adj_Cr', 'Accruals_Dr', 'Accruals_Cr', 'CB_Dr', 'CB_Cr', 'Acc_Group']
        self.dataframe = self.dataframe.rename(columns=dict(zip(self.dataframe.columns, cols_to_be)))
        merged_df = pd.merge(self.dataframe, self.master_data, left_on='Corp Acc', right_on='Local Account Code',
                             how='left',
                             sort=False)
        return merged_df

    def reveal_ob_adjustments(self):
        df = self.further_process().copy()

        # print(df.columns)

        @np.vectorize
        def check_if_none(x, y):
            if x in [0, None, ""] and y in [0, None, ""]:
                return False
            else:
                return True

        df = df[check_if_none(df['OB_adj_Dr'], df['OB_adj_Cr'])]

        df.rename(columns={'Corp Acc': 'Corp Account',
                           'ENG_Text': 'Corp Account Name',
                           'Rus Account_y': 'Rap Account'
                           }, inplace=True)

        @np.vectorize
        def func1(x, y):
            if x in [None, "None", '0.0', 0] and y not in [None, "None", '0.0', 0]:
                return y
            elif x not in [None, "None", '0.0', 0] and y in [None, "None", '0.0', 0]:
                return x

        df['Amount in LC'] = func1(df['OB_adj_Dr'], df['OB_adj_Cr'])
        cols_to_select = ['Corp Account', 'Corp Account Name', 'Rap Account', 'Amount in LC',
                          "FS Sub Line name", "FS Line name", "Category"]
        df = df[cols_to_select]
        df = deepcopy(df)
        df['Transaction Type'] = 'Opening Balance adjustment'
        df['Pstng Date'] = pd.to_datetime('01/01/2024').date()
        df['Param'] = 'Before due date'
        df['Text'] = 'This is opening balance adjustment at the beginning of the 2023 year'
        df['Amount in LC'] = df['Amount in LC'].astype(str).str.split(".").str.get(0).astype(float)

        df.loc[:, "Group Account Number"] = df.loc[:, "Corp Account"] \
            .apply(lambda x: self.mydict2.get(x).get("Consolidation Account") if self.mydict2.get(x) else x)
        df.loc[:, "Group Account Name"] = df.loc[:, "Corp Account"] \
            .apply(lambda x: self.mydict2.get(x).get("Consolidation Account Name") if self.mydict2.get(x) else x)
        # df.loc[:, "Group Account Name_Korean"] = df.loc[:, "Corp Account"].apply(
        #     lambda x: self.mydict2.get(x).get("Consolidation Account Korean Name") if self.mydict2.get(x) else x)

        return df

    def reveal_ob_adj_ARAP(self):
        df = self.reveal_ob_adjustments().copy()
        df = df[
            df['FS Line name'].isin(['Other Receivables', 'Accounts Receivable', 'Trade and Other Payables, Current'])]
        # df['Category'] = df['reporting_line']
        df['Amount in LC'] = df['Amount in LC'].astype(str).str.split(".").str.get(0).astype(float)

        conds = [
            df['FS Line name'].isin(["Trade and Other Payables, Current"])
        ]

        choices = [
            df['Amount in LC'] * -1
        ]

        df['Amount in LC'] = np.select(conds, choices, default=df['Amount in LC'])

        return df


if __name__ == '__main__':
    # tb = ExcelParser(r'V:\Findep\Incoming\test\DevOps\References\HMCIS TB structure_2023.xlsx',
    #                  'TB_01_07_2023', 'Local Account Code').read_data()
    # pl = ExcelParser(r'V:\Findep\Incoming\test\DevOps\References\HMCIS PL structure_2023.xlsx',
    #                  'Sheet1', 'Local Account Code').read_data()
    # bs = ExcelParser(r'V:\Findep\Incoming\test\DevOps\References\HMCIS BS structure_2023.xlsx',
    #                  'Sheet1', 'Local Account Code').read_data()
    # osv = ExcelParser(r"V:\Findep\Incoming\test\DevOps\References\HMCIS OSV structure_2023.xlsx",
    #                   'Sheet1',
    #                   'Rus Account').read_data()
    # korean_reference = ExcelParser(r"V:\Findep\Incoming\test\DevOps\HSE1_CoA\Current CoA_2023.xlsx",
    #                                'Sheet2',
    #                                'Eng name').read_data()

    master_data = MasterData().further_process()

    x = OBAdj(r'V:\Findep\Work\FINDEP HMCIS\PL\Preliminary\2024\01 January\TB from Accounting\Detail_Jan_2024.xlsx',
              'ОСВ_Январь_2024',
              master_data=master_data)
    print(x.reveal_ob_adj_ARAP().to_clipboard())
