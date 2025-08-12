import copy

import pandas as pd

from hmcis_packs.parsers.exceldata import ExcelParser


class MasterData:
    """"""

    def __init__(self):
        self.df = ExcelParser(filepath=r'V:\Findep\Incoming\test\DevOps\HMCIS_Mapping_2023\HMCIS_Mapping_2023.xlsm',
                              sheet_name='Mapping_new',
                              index_value='Balance or PnL').read_data()

    def further_process(self):
        df = copy.deepcopy(self.df)
        return df


class MasterDataMappedWithBudget:
    """"""

    def __init__(self,
                 tb: pd.DataFrame = None,
                 bs: pd.DataFrame = None,
                 pl: pd.DataFrame = None,
                 osv: pd.DataFrame = None,
                 korean_reference: pd.DataFrame = None,
                 mapping: pd.DataFrame = None
                 ):
        """Constructor for MasterDataMappedWithBudget"""
        self.master_data = MasterData(tb=tb, bs=bs, pl=pl, osv=osv, korean_reference=korean_reference

                                      ).further_process()
        self.mapping = mapping

    def create_mapped_df(self):
        mapped_df = pd.merge(self.master_data, self.mapping, left_on='Local Account Code',
                             right_on='Cost Elem.', how='left', sort=False,
                             validate='one_to_many')
        # mapped_df = mapped_df[pd.notna(mapped_df['Cost Center Name'])]

        return mapped_df


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
    # mapping = Mapping().further_process()

    x = MasterData()
    # y = MasterDataMappedWithBudget(tb=tb, pl=pl, bs=bs,
    #                                osv=osv, korean_reference=korean_reference, mapping=mapping)
    # y.create_mapped_df().to_clipboard()
    # y.create_mapped_df().to_clipboard()
    x.further_process().to_clipboard()
    # mapping.to_clipboard()
