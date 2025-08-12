from hmcis_packs import ExcelParser


class Mapping:
    """
        This class should be dealing with Mapping
    """

    def __init__(self, ):
        self.df = ExcelParser(
            r'\\int.hmcis.ru\public\Findep\Incoming\test\DevOps\Data Structures\Mapping_updated.xlsx',
            'Mapping',
            'Cost Ctr'
        ).read_data()

    def further_process(self):
        self.df['Cost Ctr'] = self.df['Cost Ctr'].astype(str).str.split(".").str.get(0)
        self.df['Cost Elem.'] = self.df['Cost Elem.'].astype(str).str.split(".").str.get(0)
        return self.df


if __name__ == '__main__':
    x = Mapping()
    x.further_process().to_clipboard()
