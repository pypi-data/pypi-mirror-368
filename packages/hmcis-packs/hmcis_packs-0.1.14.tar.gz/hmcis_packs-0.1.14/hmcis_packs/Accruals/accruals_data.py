import re

import numpy as np
import pandas as pd

from hmcis_packs import ExcelParser, GetCustomers, GetVendors, MasterData, Translated


class ParseAccruals:
    def __init__(
            self,
            filepath,
            sht,
            index,
            report_date,
            master_data: pd.DataFrame = None,
            vendors: dict = None,
            customers=None,
            translated: dict = None,
    ) -> None:
        self.filepath = filepath
        self.sht = sht
        self.index = index
        self.report_date = report_date
        self.dataframe = ExcelParser(self.filepath, self.sht, self.index).read_data()
        self.dataframe["Дт"] = self.dates_to_strings(self.dataframe["Дт"].astype(str))
        self.dataframe["Кт"] = self.dates_to_strings(self.dataframe["Кт"].astype(str))
        self.dataframe["МВЗ"] = (
            self.dataframe["МВЗ"].astype(str).str.split(".").str.get(0)
        )
        self.dataframe = self.dataframe.astype(str).reset_index(drop=True)
        self.CoA = master_data
        self.CoA = self.CoA.drop_duplicates(subset="Rus Account", keep="first")

        self.mydict = self.CoA.set_index("Rus Account").T.to_dict()
        self.mydict2 = self.CoA.set_index("Local Account Code").T.to_dict()
        self.vendors = vendors
        self.customers = customers
        self.translated = translated

    def define_corp_acc(self, x):
        if self.mydict.get(x):
            return self.mydict.get(x).get("Local Account Code")
        else:
            return "not applicable"

    def get_name(self, code):
        # pass
        if self.vendors.get(code) is not None:
            return self.vendors.get(code, {}).get("NAME1")
        else:
            return self.customers.get(code, {}).get("NAME1")

    @staticmethod
    @np.vectorize
    def offset_date(x, y):
        return x + pd.offsets.Day(y)

    @staticmethod
    @np.vectorize
    def lines_to_duplicate(x, y):
        if x != "not applicable" and y != "not applicable":
            return "we have to duplicate this line"
        if x == "not applicable" and y != "not applicable":
            return y
        if x != "not applicable" and y == "not applicable":
            return x

    def get_days(self, row):
        x = row["Company_code"]
        y = row["Rap Account"]
        z = row["Описание операции"]
        a = self.customers.get(x)
        if a:
            if (
                    a.get("channel") == "AS_Retail"
                    and y == "62.01.05"
                    and not str(z).__contains__("опт")
            ):
                return a.get("Отсрочка платежа, дни, розница")
            elif (
                    a.get("channel") == "AS_WholeSales"
                    and y == "62.01.05"
                    and not str(z).__contains__("опт")
            ):
                return a.get("Отсрочка платежа, дни, розница")
            elif (
                    a.get("channel") == "AS_WholeSales"
                    and y == "62.01.05"
                    and str(z).__contains__("опт")
            ):
                return a.get("Отсрочка платежа, дни, опт")
            elif a.get("channel") == "Mobility channel":
                return a.get("Отсрочка платежа (дн.)")
            elif a.get("channel") == "not applicable":
                return 0
        else:
            return 0

        # pass

    @staticmethod
    @np.vectorize
    def get_counterparty(x: pd.Series, y: pd.Series) -> pd.Series:
        if x in [None, "None", ""]:
            return y
        elif y in [None, "None", ""]:
            return x
        elif y not in [None, "None", ""] and x not in [None, "None", ""]:
            return x

    def further_process(self):
        self.dataframe["Corp Account_Dr"] = self.dataframe.apply(
            lambda row: self.define_corp_acc(row["Дт"]), axis=1
        )
        self.dataframe["Corp Account_Cr"] = self.dataframe.apply(
            lambda row: self.define_corp_acc(row["Кт"]), axis=1
        )

        self.dataframe["FS Sub Line name_Dr"] = self.dataframe["Corp Account_Dr"].apply(
            lambda x: self.mydict2.get(x).get("FS Sub Line name")
            if self.mydict2.get(x)
            else x
        )

        self.dataframe["FS Line name_Dr"] = self.dataframe["Corp Account_Dr"].apply(
            lambda x: self.mydict2.get(x).get("FS Line name")
            if self.mydict2.get(x)
            else x
        )
        self.dataframe["Balance_or_PnL_Dr"] = self.dataframe["Corp Account_Dr"].apply(
            lambda x: self.mydict2.get(x).get("Balance or PnL")
            if self.mydict2.get(x)
            else x
        )
        self.dataframe["Balance_or_PnL_Cr"] = self.dataframe["Corp Account_Cr"].apply(
            lambda x: self.mydict2.get(x).get("Balance or PnL")
            if self.mydict2.get(x)
            else x
        )

        self.dataframe["FS Sub Line name_Cr"] = self.dataframe["Corp Account_Cr"].apply(
            lambda x: self.mydict2.get(x).get("FS Sub Line name")
            if self.mydict2.get(x)
            else x
        )

        self.dataframe["FS Line name_Cr"] = self.dataframe["Corp Account_Cr"].apply(
            lambda x: self.mydict2.get(x).get("FS Line name")
            if self.mydict2.get(x)
            else x
        )

        conds = [
            (
                    (self.dataframe["FS Line name_Dr"].isin(["", None]))
                    & (self.dataframe["Corp Account_Dr"].str.startswith(("1", "2", "3")))
            ),
            (
                    (self.dataframe["FS Line name_Dr"].isin(["", None]))
                    & (
                        self.dataframe["Corp Account_Dr"].str.startswith(
                            ("4", "5", "6", "7")
                        )
                    )
            ),
        ]

        conds_2 = [
            (
                    (self.dataframe["FS Line name_Cr"].isin(["", None, "not applicable"]))
                    & (self.dataframe["Corp Account_Cr"].str.startswith(("1", "2", "3")))
            ),
            (
                    (self.dataframe["FS Line name_Cr"].isin(["", None, "not applicable"]))
                    & (
                        self.dataframe["Corp Account_Cr"].str.startswith(
                            ("4", "5", "6", "7")
                        )
                    )
            ),
        ]

        choices = ["BS", "PL"]

        self.dataframe["Balance_or_PnL_Dr"] = np.select(
            conds, choices, default=self.dataframe["Balance_or_PnL_Dr"]
        )
        self.dataframe["Balance_or_PnL_Cr"] = np.select(
            conds_2, choices, default=self.dataframe["Balance_or_PnL_Cr"]
        )

        return self.dataframe

    def make_bs_data(self, ag_dr="BS", ag_cr="BS"):
        df = self.further_process().copy()
        df = df[
            df.apply(
                lambda row: True
                if row["Balance_or_PnL_Dr"] == ag_dr
                   or row["Balance_or_PnL_Cr"] == ag_cr
                else False,
                axis=1,
            )
        ]

        return df

    def make_pnl_data(self, ag_dr="PL", ag_cr="PL"):
        df = self.further_process().copy()
        conds = [
            (df["Balance_or_PnL_Dr"] == ag_dr) & (df["Balance_or_PnL_Cr"] == ag_cr),
            (df["Balance_or_PnL_Dr"] != ag_dr) & (df["Balance_or_PnL_Cr"] == ag_cr),
            (df["Balance_or_PnL_Dr"] == ag_dr) & (df["Balance_or_PnL_Cr"] != ag_cr),
        ]
        choices = [True, True, True]
        df = df[np.select(conds, choices, default=False)]
        df.reset_index(drop=True, inplace=True)

        conds_2 = [
            (df["Balance_or_PnL_Dr"] == ag_dr) & (df["Balance_or_PnL_Cr"] == ag_cr),
            (df["Balance_or_PnL_Dr"] != ag_dr) & (df["Balance_or_PnL_Cr"] == ag_cr),
            (df["Balance_or_PnL_Dr"] == ag_dr) & (df["Balance_or_PnL_Cr"] != ag_cr),
        ]
        choices_2 = [
            "duplicate this line",
            df["Corp Account_Cr"],
            df["Corp Account_Dr"],
        ]
        df["Corp Account"] = np.select(conds_2, choices_2, default=None)
        sp_idx = df[(df == "duplicate this line").any(axis=1)].index

        for item in sp_idx:
            s = df.iloc[item, :].values
            s = [
                str(item) + "_make a dup of_" if item == "duplicate this line" else item
                for item in s
            ]
            df.loc[len(df)] = s

        condslast = [
            df.loc[:, "Corp Account"].isin(["duplicate this line"]),
            df.loc[:, "Corp Account"].isin(["duplicate this line_make a dup of_"]),
        ]

        choiceslast = [
            df.loc[:, "Corp Account_Dr"],
            df.loc[:, "Corp Account_Cr"],
        ]

        df["Corp Account"] = np.select(
            condslast, choiceslast, default=df["Corp Account"]
        )

        conds = [
            (df["Balance_or_PnL_Cr"] == "PL")
            & (df["Balance_or_PnL_Dr"] == "PL")
            & (df["Corp Account"].str.startswith("4")),
            (df["Balance_or_PnL_Cr"] == "PL")
            & (df["Balance_or_PnL_Dr"] == "PL")
            & (df["Corp Account"].str.startswith("5")),
            df["Balance_or_PnL_Cr"] == "PL",
        ]
        choices = [
            df["Сумма"].astype(float),
            df["Сумма"].astype(float) * -1,
            df["Сумма"].astype(float) * -1,
        ]
        df["Сумма"] = np.select(conds, choices, default=df["Сумма"])

        df.drop(
            columns=[
                "Corp Account_Dr",
                "Corp Account_Cr",
                "FS Sub Line name_Dr",
                "FS Line name_Dr",
                "FS Line name_Cr",
                "FS Sub Line name_Cr",
                "Код НДС",
            ],
            inplace=True,
        )
        df["FS line"] = df["Corp Account"].apply(
            lambda x: self.mydict2.get(x).get("FS Line name")
            if self.mydict2.get(x)
            else x
        )
        df["Report line"] = df["Corp Account"].apply(
            lambda x: self.mydict2.get(x).get("Category") if self.mydict2.get(x) else x
        )
        df["Период, к которому относятся расходы"] = pd.to_datetime(
            self.report_date
        ).date()
        df["Corp Account Name"] = df["Corp Account"].apply(
            lambda x: self.mydict2.get(x).get("Local Account Name_Eng")
            if self.mydict2.get(x)
            else x
        )

        df["Group Account Code"] = df["Corp Account"].apply(
            lambda x: self.mydict2.get(x).get("Consolidation Account")
            if self.mydict2.get(x)
            else x
        )
        df["Group Account Code Name"] = df["Corp Account"].apply(
            lambda x: self.mydict2.get(x).get("Consolidation Account Name")
            if self.mydict2.get(x)
            else x
        )

        df["Кредитор/дебитор ДТ"] = (
            df["Кредитор/дебитор ДТ"].astype(str).str.split(".").str.get(0)
        )
        df["Кредитор/дебитор КТ"] = (
            df["Кредитор/дебитор КТ"].astype(str).str.split(".").str.get(0)
        )

        df["CounterParty SAP code"] = self.get_counterparty(
            df["Кредитор/дебитор ДТ"], df["Кредитор/дебитор КТ"]
        )

        conds_3 = [
            df["Описание операции"].str.contains("для HMC", flags=re.I),
            df["CounterParty SAP code"].isin([None, "None", "без кредитора"]),
        ]

        choices_3 = ["SBC3", "not applicable"]

        df["CounterParty SAP code"] = np.select(
            conds_3, choices_3, default=df["CounterParty SAP code"]
        )
        df["CounterParty SAP name"] = df["CounterParty SAP code"].apply(
            lambda x: self.get_name(x)
        )

        return df

    def make_accruals_for_ARAP(self, ag_dr="bs", ag_cr="bs"):
        df = self.further_process().copy()
        conds_1 = [
            df["FS Line name_Dr"].isin(
                [
                    "Accounts Receivable",
                    "Other Receivables",
                    "Trade and Other Payables, Current",
                    "Trade and Other Payables, Current_Other AP"
                ]
            ),
            df["FS Line name_Cr"].isin(
                [
                    "Accounts Receivable",
                    "Other Receivables",
                    "Trade and Other Payables, Current",
                    "Trade and Other Payables, Current_Other AP"
                ]
            ),
        ]
        choices_1 = [df["Corp Account_Dr"], df["Corp Account_Cr"]]

        df["Corp Account"] = np.select(conds_1, choices_1, default=None)
        df = df[pd.notna(df["Corp Account"])]

        conds_2 = [
            df["FS Line name_Cr"].isin(
                ["Trade and Other Payables, Current", "Trade and Other Payables, Current_Other AP"]),
            df["FS Line name_Dr"].isin(["Accounts Receivable", "Other Receivables"]),
            df["FS Line name_Dr"].isin(
                ["Trade and Other Payables, Current", "Trade and Other Payables, Current_Other AP"]),
            df["FS Line name_Cr"].isin(["Accounts Receivable", "Other Receivables"]),
        ]
        choices_2 = [
            df["Сумма"].astype(float) * -1,
            df["Сумма"].astype(float) * 1,
            df["Сумма"].astype(float) * 1,
            df["Сумма"].astype(float) * -1,
        ]
        df["Сумма"] = np.select(conds_2, choices_2, default=df["Сумма"])

        conds_3 = [
            (
                df["FS Line name_Dr"].isin(
                    [
                        "Accounts Receivable",
                        "Other Receivables",
                        "Trade and Other Payables, Current",
                        "Trade and Other Payables, Current_Other AP"
                    ]
                )
            )
            & (
                df["FS Line name_Cr"].isin(
                    [
                        "Accounts Receivable",
                        "Other Receivables",
                        "Trade and Other Payables, Current",
                        "Trade and Other Payables, Current_Other AP"
                    ]
                )
            )
        ]
        choices_3 = [
            "duplicate this line",
        ]

        df["Corp Account"] = np.select(conds_3, choices_3, default=df["Corp Account"])
        df.reset_index(drop=True, inplace=True)

        sp_idx = df[(df == "duplicate this line").any(axis=1)].index

        for item in sp_idx:
            s = df.iloc[item, :].values
            s = [
                str(item) + "_make a dup of_" if item == "duplicate this line" else item
                for item in s
            ]
            df.loc[len(df)] = s

        condslast = [
            df.loc[:, "Corp Account"].isin(["duplicate this line"]),
            df.loc[:, "Corp Account"].isin(["duplicate this line_make a dup of_"]),
        ]

        choiceslast = [
            df.loc[:, "Corp Account_Dr"],
            df.loc[:, "Corp Account_Cr"],
        ]

        df["Corp Account"] = np.select(
            condslast, choiceslast, default=df["Corp Account"]
        )

        conds_4 = [
            (
                df["FS Line name_Dr"].isin(
                    [
                        "Accounts Receivable",
                        "Other Receivables",
                        "Trade and Other Payables, Current",
                        "Trade and Other Payables, Current_Other AP"
                    ]
                )
            )
            & (
                df["FS Line name_Cr"].isin(
                    [
                        "Accounts Receivable",
                        "Other Receivables",
                        "Trade and Other Payables, Current",
                        "Trade and Other Payables, Current_Other AP"
                    ]
                )
            )
            & (df["Corp Account"].str.startswith(("2", "3"))),
            (
                df["FS Line name_Dr"].isin(
                    [
                        "Accounts Receivable",
                        "Other Receivables",
                        "Trade and Other Payables, Current",
                        "Trade and Other Payables, Current_Other AP"
                    ]
                )
            )
            & (
                df["FS Line name_Cr"].isin(
                    [
                        "Accounts Receivable",
                        "Other Receivables",
                        "Trade and Other Payables, Current",
                        "Trade and Other Payables, Current_Other AP"
                    ]
                )
            )
            & (df["Corp Account"].str.startswith("1")),
        ]
        choices_4 = [df["Сумма"], df["Сумма"] * -1]
        df["Сумма"] = np.select(conds_4, choices_4, default=df["Сумма"])
        cols_to_drop = [
            # "НОМЕР ROA",
            "Corp Account_Dr",
            "Corp Account_Cr",
            "FS Sub Line name_Dr",
            "FS Line name_Dr",
            "FS Sub Line name_Cr",
            "FS Line name_Cr",
        ]
        df.drop(columns=cols_to_drop, inplace=True)
        df.loc[:, "Corp Account Name"] = df["Corp Account"].apply(
            lambda x: self.mydict2.get(x).get("Local Account Name_Eng")
            if self.mydict2.get(x)
            else x
        )
        df.loc[:, "Rap Account"] = df["Corp Account"].apply(
            lambda x: self.mydict2.get(x).get("Rus Account")
            if self.mydict2.get(x)
            else x
        )
        df.loc[:, "Group Account Number"] = df.loc[:, "Corp Account"].apply(
            lambda x: self.mydict2.get(x).get("Consolidation Account")
            if self.mydict2.get(x)
            else x
        )
        df.loc[:, "Group Account Name"] = df.loc[:, "Corp Account"].apply(
            lambda x: self.mydict2.get(x).get("Consolidation Account Name")
            if self.mydict2.get(x)
            else x
        )
        # df.loc[:, "Group Account Name_Korean"] = df.loc[:, "Corp Account"].apply(
        #     lambda x: self.mydict2.get(x).get("Consolidation Account Korean Name") if self.mydict2.get(x) else x)

        df["Кредитор/дебитор ДТ"] = (
            df["Кредитор/дебитор ДТ"].astype(str).str.split(".").str.get(0)
        )
        df["Кредитор/дебитор КТ"] = (
            df["Кредитор/дебитор КТ"].astype(str).str.split(".").str.get(0)
        )
        df["Company_code"] = self.get_counterparty(
            df["Кредитор/дебитор ДТ"], df["Кредитор/дебитор КТ"]
        )

        conds_4 = [
            df["Описание операции"].str.contains("для HMC", flags=re.I),
            df["Company_code"].isin([None, "None", "без кредитора"]),
        ]

        choices_4 = ["SBC3", "not applicable"]

        df["Company_code"] = np.select(conds_4, choices_4, default=df["Company_code"])

        df["Company_code"] = df["Company_code"].astype(str).str.split(".").str.get(0)
        df["Company_name"] = df["Company_code"].apply(lambda x: self.get_name(x))
        df["Период, к которому относятся расходы"] = pd.to_datetime(
            self.report_date
        ).date()
        cols_to_drop = [
            "Кредитор/дебитор ДТ",
            "Кредитор/дебитор КТ",
            "Код НДС",
            "Дт",
            "Кт",
        ]
        df.drop(columns=cols_to_drop, inplace=True)
        df["Deferred_Payment_Days"] = df.apply(lambda row: self.get_days(row), axis=1)
        df["Deferred_Payment_Days"] = df["Deferred_Payment_Days"].apply(
            lambda x: int(str(x).split(".")[0]) if pd.notna(x) else 0
        )
        df["Due Date"] = self.offset_date(
            df["Период, к которому относятся расходы"], df["Deferred_Payment_Days"]
        )
        df["Overdue days"] = (
                pd.to_datetime(self.report_date) - pd.to_datetime(df["Due Date"])
        ).apply(lambda x: x.days)
        df["Transaction Type"] = "Accruals"
        bins = [-1000, 0, 31, 61, 90, 20000]
        group_names = ["Before due date", "0-30", "31-60", "61-90", "over 90 days"]

        df["Param"] = pd.cut(df["Overdue days"], bins=bins, labels=group_names)
        df.rename(
            columns={
                "Период, к которому относятся расходы": "Pstng Date",
                "Сумма": "Amount in LC",
                "Ответственный отдел в ОБО": "DocumentNo",
                "Описание операции": "Text",
            },
            inplace=True,
        )

        df["Company_name"] = df.apply(
            lambda row: self.translated.get(row["Company_code"], {}).get(
                "Translated", row["Company_name"]
            ),
            axis=1,
        )
        df["Category"] = df["Corp Account"].apply(
            lambda x: self.mydict2.get(x).get("Category") if self.mydict2.get(x) else x
        )
        df["FS Line name"] = df["Corp Account"].apply(
            lambda x: self.mydict2.get(x).get("FS Line name") if self.mydict2.get(x) else x
        )
        df["FS Sub Line name"] = df["Corp Account"].apply(
            lambda x: self.mydict2.get(x).get("FS Sub Line name") if self.mydict2.get(x) else x
        )

        # conds_5 = [ df['category'].isin(['AP', 'Other AP'])  ]
        # choices_5 = [ df['Amount in LC'] * -1 ]
        #
        # df['Amount in LC'] = np.select(conds_5, choices_5, default=df['Amount in LC'])
        # df = df[pd.notna(df['corp account'])]

        return df

    @staticmethod
    @np.vectorize
    def dates_to_strings(col: pd.Series):
        if len(col) == 8:
            return col
        elif col in [None, "None"]:
            return None
        elif len(col) == 5:
            return col
        else:
            return pd.to_datetime(col, dayfirst=False).strftime("%d.%m.%y")


if __name__ == "__main__":
    vendors = (
        GetVendors(
            filepath=r"V:\Findep\Incoming\test\DevOps\References\LFA1 26012024.txt",
            value="LIFNR",
        )
        .further_process()
        .set_index("LIFNR")
        .T.to_dict()
    )
    customers = (
        GetCustomers(
            filepath=r"V:\Findep\Incoming\test\DevOps\References\KNA1 26012024.txt",
            value="KUNNR",
        )
        .further_process()
        .set_index("KUNNR")
        .T.to_dict()
    )
    translated = Translated().dataframe.set_index("Company_code").T.to_dict()

    obj1 = ParseAccruals(
        r"V:\Findep\Work\FINDEP HMCIS\PL\Preliminary\2023\12 December\TB from Accounting\Final\!Начисление МСФО_декабрь 2023.xlsx",
        "для IF загрузки",
        "Отдел инициатор",
        "12/31/2023",
        master_data=MasterData().further_process(),
        customers=customers,
        vendors=vendors,
        translated=translated,
    )
    obj1.make_accruals_for_ARAP().to_clipboard()
