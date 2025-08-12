import numpy as np
import pandas as pd

from hmcis_packs import ExcelParser, MasterData


@np.vectorize
def offset_date(x, y):
    return x + pd.offsets.Day(y)


class Df1Parser:
    def __init__(self, filepath, sht, index, report_date, master_data: pd.DataFrame = None):
        self.report_date = report_date
        self.master_data = master_data
        self.df1 = ExcelParser(filepath, sht, index, retain_duplicates=True).read_data()

    def further_process_df1(self):
        mydict2_object = self.master_data.set_index('Local Account Code').T.to_dict()
        self.df1.columns = ['Счет', 'Субконто 1', 'None', 'Субконто 2', 'Субконто 3.Дата', 'Нач. Остаток Дт',
                            'Нач. Остаток Кт', 'Обороты Дт', 'Обороты Кт', 'Кон. Остаток Дт', 'Кон. Остаток Кт',
                            'Количество записей']
        self.df1 = self.df1[~self.df1['Счет'].isin(['Total', '', None])]
        conds = [
            ~self.df1['Кон. Остаток Дт'].isin(['None']),
            ~self.df1['Кон. Остаток Кт'].isin(['None'])
        ]

        choices = [
            True, True
        ]

        self.df1 = self.df1[np.select(conds, choices, default=False)]
        params = {'60.01': 'A21000101', '60.02': 'A21000106', '62.01': 'A11010601'}
        self.df1['Corp Account'] = self.df1['Счет'].apply(lambda element: params.get(element))
        self.df1['Company_code'] = '1C Counterparty'
        self.df1['Кон. Остаток Дт'] = self.df1['Кон. Остаток Дт'].apply(
            lambda x: float(x) if x not in ['None', None] else 0)
        self.df1['Кон. Остаток Кт'] = self.df1['Кон. Остаток Кт'].apply(
            lambda x: float(x) * -1 if x not in ['None', None] else 0)

        self.df1 = self.df1.rename(columns=
                                   {"Субконто 1": "Company_name",
                                    'Субконто 2': 'Text',
                                    'Счет': 'Rap Account',
                                    'Субконто 3.Дата': 'Pstng Date',
                                    })

        self.df1['Amount in LC'] = self.df1[['Кон. Остаток Дт', 'Кон. Остаток Кт']].sum(axis=1)
        self.df1 = self.df1.drop(columns=['Кон. Остаток Дт', 'Кон. Остаток Кт', 'Количество записей',
                                          'Нач. Остаток Дт', 'Нач. Остаток Кт', 'Обороты Дт', 'Обороты Кт'])

        self.df1['FS Line name'] = self.df1['Corp Account'].apply(
            lambda x: mydict2_object.get(x).get('FS Line name') if mydict2_object.get(x) else x)
        self.df1['Category'] = self.df1['Corp Account'].apply(
            lambda x: mydict2_object.get(x).get('Category') if mydict2_object.get(x) else x)
        self.df1['FS Sub Line name'] = self.df1['Corp Account'].apply(
            lambda x: mydict2_object.get(x).get('FS Sub Line name') if mydict2_object.get(x) else x)
        self.df1['Corp Account Name'] = self.df1['Corp Account'].apply(
            lambda x: mydict2_object.get(x).get('Local Account Name_Eng') if mydict2_object.get(x) else x)
        self.df1['Transaction Type'] = 'HML'
        self.df1['Pstng Date'] = pd.to_datetime(self.report_date).date()
        self.df1 = self.df1.drop(columns=['None'])
        self.df1.loc[:, "Group Account Number"] = self.df1.loc[:, "Corp Account"] \
            .apply(lambda x: mydict2_object.get(x).get("Consolidation Account") if mydict2_object.get(x) else x)
        self.df1.loc[:, "Group Account Name"] = self.df1.loc[:, "Corp Account"] \
            .apply(lambda x: mydict2_object.get(x).get("Consolidation Account Name") if mydict2_object.get(x) else x)
        # self.df1.loc[:, "Group Account Name_Korean"] = self.df1.loc[
        #                                                :, "Corp Account"
        #                                                ].apply(
        #     lambda x: mydict2_object.get(x).get("Consolidation Account Korean Name") if mydict2_object.get(x) else x)

        self.df1['Deferred_Payment_Days'] = 0
        self.df1['Due Date'] = offset_date(self.df1["Pstng Date"],
                                           self.df1["Deferred_Payment_Days"])
        self.df1["Overdue days"] = (
                pd.to_datetime(self.report_date)
                - pd.to_datetime(self.df1["Due Date"])
        ).apply(lambda x: x.days)
        self.df1['Param'] = 'Before due date'
        self.df1 = self.df1[self.df1['Amount in LC'] != 0]

        return self.df1


class Df2Parser:
    def __init__(self, filepath, sht, index, report_date, master_data: pd.DataFrame = None):
        self.report_date = report_date
        self.master_data = master_data
        self.df1 = ExcelParser(filepath, sht, index, retain_duplicates=True).read_data()

        self.df1.columns = ['Счет', 'Субконто 1', 'None', 'Субконто 2', 'Субконто 3.Дата', 'Нач. Остаток Дт',
                            'Нач. Остаток Кт', 'Обороты Дт', 'Обороты Кт', 'Кон. Остаток Дт', 'Кон. Остаток Кт',
                            'Количество записей']
        self.df1.dropna(how='all', axis=1, inplace=True)
        self.df1.dropna(how='all', axis=0, inplace=True)
        self.df1 = self.df1[self.df1['Количество записей'] == 1]

    def further_process_df1(self):
        mydict2_object = self.master_data.set_index('Local Account Code').T.to_dict()
        conds = [
            ~self.df1['Кон. Остаток Дт'].isin(['None']),
            ~self.df1['Кон. Остаток Кт'].isin(['None'])
        ]

        choices = [
            True, True
        ]

        self.df1 = self.df1[np.select(conds, choices, default=False)]
        params = {'76.09': 'A11011206', '76.29': 'A11011206'}
        self.df1['Corp Account'] = self.df1['Счет'].apply(lambda element: params.get(element))
        self.df1['Company_code'] = '1C Counterparty'
        self.df1['Кон. Остаток Дт'] = self.df1['Кон. Остаток Дт'].apply(
            lambda x: float(x) if x not in ['None', None] else 0)
        self.df1['Кон. Остаток Кт'] = self.df1['Кон. Остаток Кт'].apply(
            lambda x: float(x) if x not in ['None', None] else 0)

        self.df1 = self.df1.rename(columns=
                                   {"Субконто 1": "Company_name",
                                    'Субконто 2': 'Text',
                                    'Счет': 'Rap Account',
                                    'Субконто 3.Дата': 'Pstng Date',
                                    })
        #
        self.df1['Amount in LC'] = self.df1[['Кон. Остаток Дт', 'Кон. Остаток Кт']].sum(axis=1)
        self.df1 = self.df1.drop(columns=['Кон. Остаток Дт', 'Кон. Остаток Кт', 'Количество записей',
                                          'Нач. Остаток Дт', 'Нач. Остаток Кт', 'Обороты Дт', 'Обороты Кт'])

        self.df1['FS Line name'] = self.df1['Corp Account'].apply(
            lambda x: mydict2_object.get(x).get('FS Line name') if mydict2_object.get(x) else x)
        self.df1['Category'] = self.df1['Corp Account'].apply(
            lambda x: mydict2_object.get(x).get('Category') if mydict2_object.get(x) else x)
        self.df1['FS Sub Line name'] = self.df1['Corp Account'].apply(
            lambda x: mydict2_object.get(x).get('FS Sub Line name') if mydict2_object.get(x) else x)
        self.df1['Corp Account Name'] = self.df1['Corp Account'].apply(
            lambda x: mydict2_object.get(x).get('Local Account Name_Eng') if mydict2_object.get(x) else x)
        self.df1['Transaction Type'] = 'HML'
        self.df1['Pstng Date'] = pd.to_datetime(self.report_date).date()
        self.df1.loc[:, "Group Account Number"] = self.df1.loc[:, "Corp Account"] \
            .apply(lambda x: mydict2_object.get(x).get("Consolidation Account") if mydict2_object.get(x) else x)
        self.df1.loc[:, "Group Account Name"] = self.df1.loc[:, "Corp Account"] \
            .apply(lambda x: mydict2_object.get(x).get("Consolidation Account Name") if mydict2_object.get(x) else x)
        # self.df1.loc[:, "Group Account Name_Korean"] = self.df1.loc[
        #                                                :, "Corp Account"
        #                                                ].apply(
        #     lambda x: mydict2_object.get(x).get("Consolidation Account Korean Name") if mydict2_object.get(x) else x)
        self.df1['Deferred_Payment_Days'] = 0
        self.df1['Due Date'] = offset_date(self.df1["Pstng Date"],
                                           self.df1["Deferred_Payment_Days"])
        self.df1["Overdue days"] = (
                pd.to_datetime(self.report_date)
                - pd.to_datetime(self.df1["Due Date"])
        ).apply(lambda x: x.days)
        self.df1['Param'] = 'Before due date'
        return self.df1


class Df3Parser:
    def __init__(self, filepath, sht, index, report_date, master_data: pd.DataFrame = None):
        self.report_date = report_date
        self.master_data = master_data
        self.df1 = ExcelParser(filepath, sht, index, retain_duplicates=True).read_data()

    def further_process_df1(self):
        mydict2_object = self.master_data.set_index('Local Account Code').T.to_dict()

        self.df1.columns = ['Счет', 'Наименование счета', 'Сальдо на начало периода Дт',
                            'Сальдо на начало периода Кт', 'Обороты за период Дт', 'Обороты за период Кт',
                            'Сальдо на конец периода Дт', 'Сальдо на конец периода Кт']
        self.df1 = self.df1[self.df1['Счет'].isin(['68.01.1', '68.02', '69.01', '69.11', '69.09'])]
        #
        self.df1['Сальдо на конец периода Кт'] = self.df1['Сальдо на конец периода Кт'].apply(
            lambda x: float(str(x)) * -1 if x not in ['None', None] else 0)
        #
        self.df1['Сальдо на конец периода Дт'] = self.df1['Сальдо на конец периода Дт'].apply(
            lambda x: float(str(x)) if x not in ['None', None] else 0)
        #
        self.df1['Amount in LC'] = self.df1[['Сальдо на конец периода Дт', 'Сальдо на конец периода Кт']].sum(axis=1)
        self.df1 = self.df1.rename(columns={'Счет': 'Rap Account'})

        #
        @np.vectorize
        def define_corp_acc(x):
            if x == '68.01.1':
                return 'A21009007'
            elif x == '68.02':
                return 'A11013005'
            elif x == '69.01':
                return 'A21009012'
            elif x == '69.11':
                return 'A21009020'
            elif x == '69.09':
                return 'A21009013'

        #
        self.df1['Corp Account'] = define_corp_acc(self.df1['Rap Account'])
        self.df1['Pstng Date'] = pd.to_datetime(self.report_date).date()
        #
        cols_to_drop = ['Наименование счета', 'Сальдо на начало периода Дт',
                        'Сальдо на начало периода Кт',
                        'Обороты за период Дт', 'Обороты за период Кт', 'Сальдо на конец периода Дт',
                        'Сальдо на конец периода Кт']
        #
        self.df1 = self.df1.drop(columns=cols_to_drop)
        self.df1['FS Line name'] = self.df1['Corp Account'].apply(
            lambda x: mydict2_object.get(x).get('FS Line name') if mydict2_object.get(x) else x)
        self.df1['Category'] = self.df1['Corp Account'].apply(
            lambda x: mydict2_object.get(x).get('Category') if mydict2_object.get(x) else x)
        self.df1['FS Sub Line name'] = self.df1['Corp Account'].apply(
            lambda x: mydict2_object.get(x).get('FS Sub Line name') if mydict2_object.get(x) else x)
        self.df1 = self.df1[self.df1['FS Line name'].isin(
            ["Accounts Receivable", "Other Receivables", "Trade and Other Payables, Current",
             "Trade and Other Payables, Current_Other AP"])]
        self.df1['Corp Account Name'] = self.df1['Corp Account'].apply(
            lambda x: mydict2_object.get(x).get('Local Account Name_Eng') if mydict2_object.get(x) else x)
        self.df1['Transaction Type'] = 'HML'
        #
        self.df1.loc[:, "Group Account Number"] = self.df1.loc[:, "Corp Account"] \
            .apply(lambda x: mydict2_object.get(x).get("Consolidation Account") if mydict2_object.get(x) else x)
        self.df1.loc[:, "Group Account Name"] = self.df1.loc[:, "Corp Account"] \
            .apply(lambda x: mydict2_object.get(x).get("Consolidation Account Name") if mydict2_object.get(x) else x)
        # self.df1.loc[:, "Group Account Name_Korean"] = self.df1.loc[
        #                                                :, "Corp Account"
        #                                                ].apply(
        #     lambda x: mydict2_object.get(x).get("Consolidation Account Korean Name") if mydict2_object.get(x) else x)
        #
        self.df1['Deferred_Payment_Days'] = 0
        self.df1['Due Date'] = offset_date(self.df1["Pstng Date"],
                                           self.df1["Deferred_Payment_Days"])
        self.df1["Overdue days"] = (
                pd.to_datetime(self.report_date)
                - pd.to_datetime(self.df1["Due Date"])
        ).apply(lambda x: x.days)
        self.df1['Param'] = 'Before due date'

        return self.df1


if __name__ == '__main__':
    tb = ExcelParser(r'V:\Findep\Incoming\test\DevOps\References\HMCIS TB structure_2023.xlsx',
                     'TB_01_07_2023', 'Local Account Code').read_data()
    pl = ExcelParser(r'V:\Findep\Incoming\test\DevOps\References\HMCIS PL structure_2023.xlsx',
                     'Sheet1', 'Local Account Code').read_data()
    bs = ExcelParser(r'V:\Findep\Incoming\test\DevOps\References\HMCIS BS structure_2023.xlsx',
                     'Sheet1', 'Local Account Code').read_data()
    osv = ExcelParser(r"V:\Findep\Incoming\test\DevOps\References\HMCIS OSV structure_2023.xlsx",
                      'Sheet1',
                      'Rus Account').read_data()
    korean_reference = ExcelParser(r"V:\Findep\Incoming\test\DevOps\HSE1_CoA\Current CoA_2023.xlsx",
                                   'Sheet2',
                                   'Eng name').read_data()
    master_data = MasterData().further_process()

    x = Df3Parser(
        filepath=r'V:\Findep\Incoming\test\DevOps\ARAP Project\Project\Accounting Input Data\YTD12_2023\ОСВ за 2023 year ООО  ХЕНДЭ МОБИЛИТИ ЛАБ.xls',
        sht='Sheet_1', index='Счет', report_date='09/30/2023', master_data=master_data)

    # y = Df2Parser(
    #     filepath=r'C:\Users\slalnazarov\Desktop\08YTD2023_76.xlsx', index='Счет',
    #     sht='TDSheet', report_date='06/30/2023')

    # z = Df3Parser(
    #     filepath=r'V:\Findep\Incoming\test\DevOps\ARAP Project\Project\Accounting Input Data\YTD07_2023\Оборотно-сальдовая ведомость за January 2023 - July 2023 ООО  ХЕНДЭ МОБИЛИТИ ЛАБ.xls',
    #     sht='TDSheet', index='Счет',
    #     report_date='06/30/2023')

    print(x.further_process_df1().to_clipboard())
