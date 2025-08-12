from hmcis_packs.parsers.exceldata import ExcelParser


class Translated:
    def __init__(self):
        self.dataframe = ExcelParser(r"V:\Findep\Incoming\test\DevOps\References\Translation.xlsx",
                                     "Sheet1",
                                     "Company_code").read_data()
        self.dataframe.loc[:, 'Company_code'] = self.dataframe.loc[:, 'Company_code'].astype(str).str.split(
            ".").str.get(0)


if __name__ == '__main__':
    parse_data = Translated()
    print(parse_data.dataframe)
