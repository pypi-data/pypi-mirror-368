import numpy as np

from hmcis_packs.parsers.exceldata import ExcelParser


class GetTb:

    def __init__(self, filepath, sht_name, index):
        self.filepath = filepath
        self.sht_name = sht_name
        self.index = index
        self.df = ExcelParser(self.filepath, self.sht_name, self.index).read_data()

    def further_process(self):
        self.df['Amount in LC'] = self.df['Debit Amount'] - self.df['Credit Amount']
        agg_func = {"Amount in LC": np.sum}
        grouped_df = self.df.groupby(by=['Consolidation Account']).agg(agg_func).reset_index()
        return grouped_df


if __name__ == '__main__':
    x = GetTb(r'V:\Accounting\Work\Мерц\2023\3 квартал\Июль 2023\Отчетность\TB_July_2023.xlsx',
              'Sheet1',
              'No')

    x.further_process().to_clipboard()
