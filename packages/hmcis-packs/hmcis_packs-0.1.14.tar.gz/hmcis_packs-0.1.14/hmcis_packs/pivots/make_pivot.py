import xlwings as xw
from xlwings import constants as cs

# xw.Book(r'V:\Findep\Incoming\test\DevOps\updated_ARAP\updated_ARAP.xlsm').set_mock_caller()

class MakePivots:
    def __init__(self, wb:str=None,data_source_sheet:str=None):
        self.book = xw.Book(wb)
        self.book.set_mock_caller()
        self.wkb = self.book.caller()
        self.data_source_sheet = data_source_sheet
        self.ws = self.wkb.sheets[self.data_source_sheet]

    def clear_pt(self, ws: str = None):
        for pt in self.wkb.sheets[ws].api.PivotTables():
            pt.TableRange2.Clear()

    def create_pt_sheet(self, pt_sheet_name: str = None):
        self.wkb.sheets.add(name=pt_sheet_name, after=self.wkb.sheets.count)

    def create_pt_table(self, pt_sheet_name: str = None, pt_name: str = None, exclude_items: tuple = None):
        target_rng = self.ws.range("c11").current_region.api
        pt_cache = self.wkb.api.PivotCaches().Create(1,
                                                     self.ws.api.Range(
                                                         target_rng.Address))

        pt = pt_cache.CreatePivotTable(self.wkb.sheets[pt_sheet_name].api.Range("a2"), pt_name)
        self.insert_pt_field(pt)
        pt.PivotFields("FS Line name").Orientation = 3
        pt.PivotFields("FS Line name").Position = 1
        pt.PivotFields("FS Line name").PivotItems(exclude_items[0]).Visible = False
        pt.PivotFields("FS Line name").PivotItems(exclude_items[1]).Visible = False
        pt.PivotFields("FS Line name").PivotItems(exclude_items[2]).Visible = False

        pt.PivotFields("Group Account Number").AutoSort(Order=cs.SortOrder.xlDescending, Field="Sum of Amount in LC")
        pt.PivotFields("Group Account Name").AutoSort(Order=cs.SortOrder.xlDescending, Field="Sum of Amount in LC")
        pt.PivotFields("Corp Account").AutoSort(Order=cs.SortOrder.xlDescending, Field="Sum of Amount in LC")
        pt.PivotFields("Corp Account Name").AutoSort(Order=cs.SortOrder.xlDescending, Field="Sum of Amount in LC")
        pt.PivotFields("Company_code").AutoSort(Order=cs.SortOrder.xlDescending, Field="Sum of Amount in LC")
        pt.PivotFields("Company_name").AutoSort(Order=cs.SortOrder.xlDescending, Field="Sum of Amount in LC")
        pt.PivotFields("Pstng Date").AutoSort(Order=cs.SortOrder.xlDescending, Field="Sum of Amount in LC")
        pt.PivotFields("Deferred_Payment_Days").AutoSort(Order=cs.SortOrder.xlDescending, Field="Sum of Amount in LC")
        pt.PivotFields("Due Date").AutoSort(Order=cs.SortOrder.xlDescending, Field="Sum of Amount in LC")
        pt.TableStyle2 = "PivotStyleDark12"

        self.wkb.sheets[pt_sheet_name]["a4"].current_region.api.Font.Name = "Hyundai Sans Text"
        self.wkb.sheets[pt_sheet_name]["a4"].current_region.api.HorizontalAlignment = cs.Constants.xlLeft
        self.wkb.sheets[pt_sheet_name]["a4"].current_region.api.VerticalAlignment = cs.Constants.xlTop
        self.wkb.sheets[pt_sheet_name]["A:H"].api.ColumnWidth = 25
        # self.wkb.sheets[pt_sheet_name]["D:E"].api.ColumnWidth = 25
        # self.wkb.sheets[pt_sheet_name]["T:U"].api.ColumnWidth = 30
        # self.wkb.sheets[pt_sheet_name]["H:H"].api.ColumnWidth = 20
        self.wkb.sheets[pt_sheet_name]["I:N"].api.ColumnWidth = 15
        self.wkb.api.ShowPivotTableFieldList = False

        return pt

    @staticmethod
    def insert_pt_field(pt):
        field_rows = {"Consolidation acc": pt.PivotFields("Group Account Number"),
                      "Consolidation acc name": pt.PivotFields("Group Account Name"),
                      "Local Account": pt.PivotFields("Corp Account"),
                      "Local Account Name": pt.PivotFields("Corp Account Name"),
                      "Company code": pt.PivotFields("Company_code"), "Company Name": pt.PivotFields("Company_name"),
                      "Pstng Date": pt.PivotFields("Pstng Date"),
                      "Deferred payment_days": pt.PivotFields("Deferred_Payment_Days"),
                      "Due Date": pt.PivotFields("Due Date")}

        field_values = {"Total Amount in RUB": pt.PivotFields("Amount in LC"),
                        "Group Acc number": pt.PivotFields("Amount in LC")}
        # field_values["Total Amount in KRW"] = pt.PivotFields("Amt in KRW")
        # field_values["Group Acc number_1"] = pt.PivotFields("Amt in KRW")

        field_cols = {"bins": pt.PivotFields("Param")}

        field_rows["Consolidation acc"].Orientation = 1
        field_rows["Consolidation acc"].Position = 1

        field_rows["Consolidation acc name"].Orientation = 1
        field_rows["Consolidation acc name"].Position = 2

        field_rows["Local Account"].Orientation = 1
        field_rows["Local Account"].Position = 3

        field_rows["Local Account Name"].Orientation = 1
        field_rows["Local Account Name"].Position = 4

        field_rows["Company Name"].Orientation = 1
        field_rows["Company Name"].Position = 5

        field_rows["Company code"].Orientation = 1
        field_rows["Company code"].Position = 6

        field_rows["Pstng Date"].Orientation = 1
        field_rows["Pstng Date"].Position = 7

        field_rows["Deferred payment_days"].Orientation = 1
        field_rows["Deferred payment_days"].Position = 8

        field_rows["Due Date"].Orientation = 1
        field_rows["Due Date"].Position = 9

        field_values["Group Acc number"].Orientation = 4
        field_values["Group Acc number"].Function = -4157
        field_values["Group Acc number"].NumberFormat = "#,##0"
        # field_values["Group Acc number_1"].Orientation = 4
        # field_values["Group Acc number_1"].Function = -4157
        # field_values["Group Acc number_1"].NumberFormat = "#,##0"

        field_cols["bins"].Orientation = 2
        field_cols["bins"].Position = 1
        field_cols["bins"].PivotItems("Before due date").Position = 1


if __name__ == "__main__":
    # xw.Book(r'V:\Findep\Incoming\test\DevOps\updated_ARAP\updated_ARAP.xlsm').set_mock_caller()
    # wb = xw.Book.caller()
    x = MakePivots(r'V:\Findep\Incoming\test\DevOps\updated_ARAP\updated_ARAP.xlsm','Data_Source')