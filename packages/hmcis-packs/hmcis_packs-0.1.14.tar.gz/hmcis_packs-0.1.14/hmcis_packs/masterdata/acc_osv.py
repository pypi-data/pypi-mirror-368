import pandas as pd

from hmcis_packs.parsers.exceldata import ExcelParser


class GetOSV:

    def __init__(self, filepath, sht_name, index, master_data: pd.DataFrame = None):
        self.master_data = master_data
        self.filepath = filepath
        self.sht_name = sht_name
        self.index = index
        self.df = ExcelParser(self.filepath, self.sht_name, self.index, retain_duplicates=True).read_data()

    def further_process(self):
        self.df = self.df.iloc[:, slice(2, 13)]
        self.df.columns = ['Corp Acc', 'Text Rus', 'Text Eng',
                           'Initials_Dr', 'Initials_Cr', 'OB_adj_Dr', 'OB_adj_Cr', 'Accruals_Dr', 'Accruals_Cr',
                           'CB_Dr', 'CB_Cr']
        self.df['Corp Acc'] = self.df['Corp Acc'].astype(str).str.split(".").str.get(0)
        MasterData_dict = self.master_data.set_index('Local Account Code').T.to_dict()
        self.df['Consolidation_Account'] = self.df['Corp Acc'].apply(lambda x:
                                                                     MasterData_dict.get(x).get(
                                                                         'Consolidation Account') if MasterData_dict.get(
                                                                         x) else None)
        self.df['Consolidation_Account'] = self.df['Consolidation_Account'].astype(str).str.split(".").str.get(0)
        self.df = self.df[~self.df['Corp Acc'].isin([None, "None"])]

        return self.df


if __name__ == '__main__':
    x = GetOSV(r'V:\Accounting\Work\Мерц\2023\3 квартал\Июль 2023\Отчетность\Detail_July_2023.xlsx',
               'ОСВ_Июль_2023',
               'Rus Account')

    x.further_process().to_clipboard()
