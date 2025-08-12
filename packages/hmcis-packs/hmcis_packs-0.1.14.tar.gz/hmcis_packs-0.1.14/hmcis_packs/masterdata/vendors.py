from hmcis_packs.parsers.txtdata import TxtParser


class GetVendors:
    def __init__(self, filepath, value):
        self.dataframe = TxtParser(filepath, value).read_data()

    def further_process(self):
        df = self.dataframe.copy()
        df = df[~df['LOEVM'].isin(["X"])]
        cols_to_select = ['LIFNR', 'LAND1', 'NAME1', 'NAME2', 'MCOD1', 'MCOD2', 'MCOD3', 'ANRED',
                          'ERDAT', 'ERNAM', 'SPRAS', 'STCD1', 'STCEG', 'STCD3', 'UPDAT',
                          'UPTIM']
        df = df[df['LAND1'].apply(lambda x: len(str(x)) == 2)]
        df = df.loc[:, cols_to_select]
        return df


if __name__ == '__main__':
    parse_data = GetVendors(filepath=r'V:\Findep\Incoming\test\DevOps\References\LFA1 26012024.txt',
                            value='LIFNR').further_process().set_index("LIFNR").T.to_dict()

    print(parse_data.get("106498"))
