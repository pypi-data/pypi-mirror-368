from copy import deepcopy

import numpy as np
import pandas as pd

from hmcis_packs import (
    GetCustomers,
    GetVendors,
    MasterData,
    Translated,
    TxtParser,
)


class Initials:
    def __init__(self, AR_filepath: str = None, AP_filepath: str = None, index: str = 'Account',
                 report_date: str = None, master_data: pd.DataFrame = None, translated: dict = None,
                 customers: dict = None, vendors: dict = None):

        self.vendors = vendors
        self.customers = customers
        self.CoA = master_data
        self.CoA = self.CoA.drop_duplicates(subset='Rus Account', keep='first')
        self.mydict = self.CoA.set_index('Rus Account').T.to_dict()
        self.mydict2 = self.CoA.set_index('Local Account Code').T.to_dict()
        self.translated = translated
        self.AP_path = AP_filepath
        self.AR_path = AR_filepath
        self.index = index
        self.report_date = report_date

        if self.AP_path is not None:
            self.AP_df = TxtParser(self.AP_path, self.index).read_data()
        else:
            self.AR_df = TxtParser(self.AR_path, self.index).read_data()

    def get_days(self, row):
        x = row['Company_code']
        y = row['Rap Account']
        z = row['Text']
        a = self.customers.get(x)
        if a:
            if a.get('channel') == 'AS_Retail' and y == '62.01.05' and not str(z).__contains__('опт'):
                return a.get("Отсрочка платежа, дни, розница")
            elif a.get('channel') == 'AS_WholeSales' and y == '62.01.05' and str(z).__contains__('опт'):
                return a.get("Отсрочка платежа, дни, опт")
            elif a.get('channel') == 'AS_WholeSales' and y == '62.01.05' and not str(z).__contains__('опт'):
                return a.get("Отсрочка платежа, дни, розница")
            elif a.get('channel') == 'Mobility channel':
                return a.get("Отсрочка платежа (дн.)")
            elif a.get('channel') == 'not applicable':
                return 0
        else:
            return 0

    def get_name(self, code):
        if self.vendors.get(code):
            return self.vendors.get(code).get("NAME1")
        elif self.customers.get(code):
            return self.customers.get(code).get("NAME1")
        else:
            return 'not applicable'

    @staticmethod
    @np.vectorize
    def offset_date(x, y):
        return x + pd.offsets.Day(y)

    @staticmethod
    @np.vectorize
    def format_string(x):
        if type(x) == str and x.startswith('00'):
            return str(int(x))
        elif type(x) == str and not x.startswith('00'):
            return x
        else:
            return x

    @staticmethod
    @np.vectorize
    def trailing_negative_numbers_(x):
        x = str(x).replace(",", "")
        if x[-1] == '-':
            return np.float64(x[-1] + x[:-1])
        else:
            return np.float64(x)

    def make_ap_df(self):
        # from IPython import embed;
        self.AP_df = deepcopy(self.AP_df)

        self.AP_df = self.AP_df.drop(columns=self.AP_df.columns[self.AP_df.columns.str.contains("Unnamed")
                                                                | self.AP_df.columns.isin(['TTy', 'AccTy', ''])])
        self.AP_df['Rap Account'] = self.AP_df['Account'].apply(lambda x:
                                                                self.mydict2.get(x).get(
                                                                    "Rus Account") if self.mydict2.get(
                                                                    x) is not None else None)
        # embed()
        self.AP_df = self.AP_df[~self.AP_df['Entry Date'].isin([None, "", "Entry Date"])]
        # self.AP_df = self.AP_df[~self.AP_df['Entry Date'].isin([None, "", "Entry Date"])]
        # #
        # @np.vectorize
        # def convert_to_date(x):
        #     try:
        #         return pd.to_datetime(x, dayfirst=True)
        #     except:
        #         return x
        #
        self.AP_df.loc[:, 'Entry Date'] = pd.to_datetime(self.AP_df['Entry Date'], dayfirst=True)
        # #
        conds = [
            (self.AP_df['Rap Account'].isin(['60.01.00'])) & (self.AP_df['Entry Date'] < pd.to_datetime('01/01/2023'))
        ]

        choices = [False]
        #
        self.AP_df = self.AP_df[np.select(conds, choices, True)]

        self.AP_df = self.AP_df[~self.AP_df['Rap Account'].isin(
            ['76.02.00', '', None])]

        self.AP_df = self.AP_df[~self.AP_df['Account'].isin(
            [np.nan, "", None, 'nan', "Account", "None"])]
        self.AP_df['Amount in LC'] = self.trailing_negative_numbers_(
            self.AP_df['Amount in LC'])
        self.AP_df['Doc. Date'] = self.AP_df['Doc. Date'].astype(str)
        # self.AP_df['Pstng Date'] = self.AP_df['Pstng Date'].astype(str)
        # self.AP_df['Pstng Date'] = self.AP_df['Pstng Date'].astype(str)
        # self.AP_df['Entry Date'] = self.AP_df['Entry Date'].astype(str)

        self.AP_df[['Doc. Date', 'Pstng Date']] = self.AP_df[['Doc. Date', 'Pstng Date']].map(
            lambda x: x.split(".")[2] + "-" + x.split(".")[1] + "-" + x.split(".")[0]).astype('datetime64[ns]')
        self.AP_df['Entry date and time'] = self.AP_df['Entry Date'].astype(str) + " " + self.AP_df['Time']
        self.AP_df['Entry date and time'] = self.AP_df['Entry date and time'].astype('datetime64[ns]')

        self.AP_df['DocumentNo'] = self.AP_df['DocumentNo'].str.split(".").str.get(0)
        self.AP_df['Sp.G/L ass'] = self.format_string(self.AP_df['Sp.G/L ass'])
        self.AP_df['Corp Account'] = np.where(self.AP_df['Account'].isin(set(self.AP_df['Account'])),
                                              self.AP_df['Account'], self.AP_df['Offst.acct'])
        self.AP_df['Corp Account Name'] = self.AP_df.loc[:, 'Corp Account'].apply(
            lambda x: self.mydict2.get(x).get("Local Account Name_Eng") if self.mydict2.get(x) is not None else None)

        self.AP_df['Doc. Date'] = np.where(self.AP_df['Doc. Date'].dt.year == 2200,
                                           self.AP_df['Pstng Date'], self.AP_df['Doc. Date'])
        self.AP_df['Group Account Number'] = self.AP_df.loc[:, 'Corp Account'].apply(
            lambda x: self.mydict2.get(x).get("Consolidation Account") if self.mydict2.get(x) is not None else None)
        self.AP_df['Group Account Name'] = self.AP_df.loc[:, 'Corp Account'].apply(
            lambda x: self.mydict2.get(x).get("Consolidation Account Name") if self.mydict2.get(
                x) is not None else None)
        # self.AP_df['Group Account Name_Korean'] = self.AP_df.loc[:, 'Corp Account'].apply(
        #     lambda x: self.mydict2.get(x).get("Consolidation Account Korean Name") if self.mydict2.get(
        #         x) is not None else None)
        self.AP_df['Transaction Type'] = "Initial Accounting"
        self.AP_df['Category'] = self.AP_df['Corp Account'].apply(lambda x: self.mydict2.get(x).get("Category")
        if self.mydict2.get(x) is not None else None)
        self.AP_df['FS Line name'] = self.AP_df['Corp Account'].apply(lambda x: self.mydict2.get(x).get("FS Line name")
        if self.mydict2.get(x) is not None else None)
        self.AP_df['FS Sub Line name'] = self.AP_df['Corp Account'].apply(
            lambda x: self.mydict2.get(x).get("FS Sub Line name")
            if self.mydict2.get(x) is not None else None)
        # self.AP_df = self.AP_df[self.AP_df['Category'] != 'not applicable for ARAP']
        conds = [
            (self.AP_df["Customer"] == "") & (self.AP_df["Vendor"] == ""),
            (self.AP_df["Customer"] != "") & (self.AP_df["Vendor"] == ""),
        ]
        choices = [
            self.AP_df["Assign."],
            self.AP_df["Customer"],
        ]

        self.AP_df["Company_code"] = np.select(
            conds, choices, self.AP_df["Vendor"])
        self.AP_df["Company_code"] = (
            self.AP_df["Company_code"].astype(str).str.split(".").str.get(0)
        )
        self.AP_df["Company_name"] = self.AP_df["Company_code"].apply(
            lambda x: self.get_name(x)
        )

        cols_to_drop = ['Account', 'Offst.acct', 'Doc. Date', 'Customer', 'Clearing',
                        'LCurr', 'Assign.', 'Entry Date', 'Time', 'Sp.G/L ass', 'Vendor',
                        'Clrng doc.', 'ClgI', 'Entry date and time']
        self.AP_df = self.AP_df.drop(columns=cols_to_drop)
        self.AP_df['Deferred_Payment_Days'] = self.AP_df.apply(
            lambda row: self.get_days(row), axis=1)
        self.AP_df['Deferred_Payment_Days'] = self.AP_df['Deferred_Payment_Days'].apply(
            lambda x: int(str(x).split('.')[0]) if pd.notna(x) else 0)

        self.AP_df['Due Date'] = self.offset_date(self.AP_df['Pstng Date'],
                                                  self.AP_df['Deferred_Payment_Days'])
        self.AP_df['Overdue days'] = (
                pd.to_datetime(self.report_date) - pd.to_datetime(self.AP_df["Due Date"])).apply(
            lambda x: x.days)
        bins = [-1000, 0, 31, 61, 90, 20000]
        group_names = ['Before due date', '0-30',
                       '31-60', '61-90', 'over 90 days']

        self.AP_df['Param'] = pd.cut(
            self.AP_df['Overdue days'], bins=bins, labels=group_names)
        self.AP_df = self.AP_df[self.AP_df['FS Line name'] != 'Other Receivables']
        self.AP_df['Company_name'] = self.AP_df.apply(
            lambda row: self.translated.get(row['Company_code'], {}).get(
                "Translated", row['Company_name']),
            axis=1
        )
        self.AP_df = self.AP_df[self.AP_df['FS Line name'].isin(
            ['Trade and Other Payables, Current', 'Trade and Other Payables, Current_Other AP'])]
        return self.AP_df

    def make_ar_df(self):
        self.AR_df = self.AR_df. \
            drop(columns=self.AR_df.columns[self.AR_df.columns.str.contains("Unnamed")
                                            | self.AR_df.columns.isin(['TTy', 'AccTy', ''])])
        self.AR_df['Rap Account'] = self.AR_df['Account'].apply(
            lambda x: self.mydict2.get(x).get("Rus Account") if
            self.mydict2.get(x) is not None else None)
        self.AR_df = self.AR_df[~self.AR_df['Rap Account'].isin(
            ['76.02.00', '60.01.00', '', None])]

        # self.AR_df = deepcopy(self.AR_df)
        self.AR_df.loc[:, 'Amount in LC'] = self.trailing_negative_numbers_(
            self.AR_df['Amount in LC'])
        self.AR_df.loc[:, ['Doc. Date', 'Pstng Date', 'Entry Date']] = self.AR_df[
            ['Doc. Date', 'Pstng Date', 'Entry Date']].map(
            lambda x: x.split(".")[2] + "-" + x.split(".")[1] + "-" + x.split(".")[0]).astype('datetime64[ns]')
        self.AR_df['Entry Date'] = self.AR_df['Entry Date'].astype('datetime64[ns]').dt.date.astype(str)
        self.AR_df.loc[:, 'Entry date and time'] = self.AR_df['Entry Date'].astype(
            str) + " " + self.AR_df['Time']

        # @np.vectorize
        # def convert_to_datetime(s):
        #     date_part, time_part = s.split(' ')[0], s.split(' ')[-1]
        #     return date_part +" "+time_part

        self.AR_df['Entry date and time'] = self.AR_df['Entry date and time'].astype('datetime64[ns]')
        # self.AR_df['Entry date and time_ver1'] = self.AR_df['Entry date and time'].apply(convert_to_datetime)
        # self.AR_df['Entry date and time_ver1'] = convert_to_datetime(self.AR_df['Entry date and time'])

        self.AR_df['DocumentNo'] = self.AR_df['DocumentNo'].str.split(
            ".").str.get(0)
        self.AR_df['Sp.G/L ass'] = self.format_string(self.AR_df['Sp.G/L ass'])
        self.AR_df['Corp Account'] = np.where(self.AR_df['Account'].isin(
            set(self.AR_df['Account'])), self.AR_df['Account'], self.AR_df['Offst.acct'])
        self.AR_df['Corp Account Name'] = self.AR_df.loc[:, 'Corp Account'].apply(
            lambda x: self.mydict2.get(x).get("Local Account Name_Eng") if self.mydict2.get(
                x) is not None else None)

        self.AR_df['Doc. Date'] = np.where(
            self.AR_df['Doc. Date'].astype('datetime64[ns]').dt.year == 2200,
            self.AR_df['Pstng Date'], self.AR_df['Doc. Date'])
        self.AR_df['Group Account Number'] = self.AR_df.loc[:, 'Corp Account'].apply(
            lambda x: self.mydict2.get(x).get("Consolidation Account") if self.mydict2.get(
                x) is not None else None)
        self.AR_df['Group Account Name'] = self.AR_df.loc[:, 'Corp Account'].apply(
            lambda x: self.mydict2.get(x).get("Consolidation Account Name") if self.mydict2.get(
                x) is not None else None)
        # self.AR_df['Group Account Name_Korean'] = self.AR_df.loc[:, 'Corp Account'].apply(
        #     lambda x: self.mydict2.get(x).get("Consolidation Account Korean Name") if self.mydict2.get(
        #         x) is not None else None)
        self.AR_df['Transaction Type'] = "Initial Accounting"
        self.AR_df['Category'] = self.AR_df['Corp Account'].apply(lambda x: self.mydict2.get(x).get("Category")
        if self.mydict2.get(x) is not None else None)
        self.AR_df['FS Line name'] = self.AR_df['Corp Account'].apply(lambda x: self.mydict2.get(x).get("FS Line name")
        if self.mydict2.get(x) is not None else None)
        self.AR_df['FS Sub Line name'] = self.AR_df['Corp Account'].apply(
            lambda x: self.mydict2.get(x).get("FS Sub Line name")
            if self.mydict2.get(x) is not None else None)
        # self.AR_df = self.AR_df[self.AR_df['Category'] != 'not applicable for ARAP']
        conds = [
            (self.AR_df["Customer"].str.len() == 0) & (
                    self.AR_df["Vendor"].str.len() != 0),
            (self.AR_df["Customer"].str.len() == 0) & (
                    self.AR_df["Vendor"].str.len() == 0),
        ]
        choices = [self.AR_df["Vendor"], "not applicable"]

        self.AR_df["Company_code"] = np.select(
            conds, choices, self.AR_df["Customer"])

        conds_2 = [
            (self.AR_df['Rap Account'].isin(['94.01.01', '94.01.02', '75.01.01', '58.01.03'])) &
            (pd.to_datetime(self.AR_df["Pstng Date"]).dt.year < 2020)

        ]

        choices_2 = [False]

        self.AR_df = self.AR_df[np.select(conds_2, choices_2, default=True)]
        cols_to_drop = (
            ['Account', 'Offst.acct', 'Doc. Date', 'Customer', 'Clearing', 'LCurr',
             'Assign.', 'Entry Date', 'Time', 'Sp.G/L ass', 'Vendor', 'Clrng doc.', 'ClgI',
             'Entry date and time']
        )
        self.AR_df = self.AR_df.drop(columns=cols_to_drop)
        self.AR_df["Company_code"] = (
            self.AR_df["Company_code"].astype(str).str.split(".").str.get(0)
        )
        self.AR_df["Company_name"] = self.AR_df["Company_code"].apply(
            lambda x: self.get_name(x)
        )

        self.AR_df['Deferred_Payment_Days'] = self.AR_df.apply(
            lambda row: self.get_days(row), axis=1)
        self.AR_df['Deferred_Payment_Days'] = self.AR_df['Deferred_Payment_Days'].apply(
            lambda x: int(str(x).split('.')[0]) if pd.notna(x) else 0)
        self.AR_df['Due Date'] = self.offset_date(self.AR_df['Pstng Date'],
                                                  self.AR_df['Deferred_Payment_Days'])

        self.AR_df['Overdue days'] = (
                pd.to_datetime(self.report_date) - pd.to_datetime(self.AR_df["Due Date"])).apply(
            lambda x: x.days)

        bins = [-1000, 0, 31, 61, 90, 20000]
        group_names = ['Before due date', '0-30',
                       '31-60', '61-90', 'over 90 days']

        self.AR_df['Param'] = pd.cut(
            self.AR_df['Overdue days'], bins=bins, labels=group_names)

        self.AR_df['Company_name'] = self.AR_df.apply(
            lambda row: self.translated.get(row['Company_code'], {}).get(
                "Translated", row['Company_name']),
            axis=1
        )

        self.AR_df = self.AR_df[self.AR_df['FS Line name'].isin(
            ['Accounts Receivable', 'Other Receivables'])]
        self.AR_df.reset_index(drop=True, inplace=True)
        return self.AR_df


if __name__ == '__main__':
    vendors = GetVendors(filepath=r'V:\Findep\Incoming\test\DevOps\References\LFA1 26012024.txt',
                         value='LIFNR').further_process().set_index("LIFNR").T.to_dict()
    customers = GetCustomers(filepath=r'V:\Findep\Incoming\test\DevOps\References\KNA1 26012024.txt',
                             value='KUNNR').further_process().set_index("KUNNR").T.to_dict()
    translated = Translated().dataframe.set_index("Company_code").T.to_dict()
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

    obj1 = Initials(
        AR_filepath=r'V:\Findep\Incoming\test\DevOps\ARAP Project\Project\Accounting Input Data\YTD12_2023\12m2023_AR.txt',
        report_date='12/31/2023',
        master_data=master_data,
        vendors=vendors, customers=customers, translated=translated)
    obj1.make_ar_df().to_clipboard()
