import csv
import io
from pathlib import Path, PosixPath

import xlrd
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.encoding import force_str

CSV_ARGS = {"delimiter": ";", "quotechar": '"'}
DEFAULT_EXT = ".csv"


class XlsToCsvConverter:
    def convert(self, fl) -> io.StringIO:
        file_contents = None if type(fl) == PosixPath else fl.getvalue()
        wb = xlrd.open_workbook(fl, file_contents=file_contents)
        result = self._process_workbook(wb)

        buff = io.StringIO()
        csvwriter = csv.writer(buff, **CSV_ARGS)
        csvwriter.writerows(result)
        buff.seek(0)
        return buff

    def _process_workbook(self, wb) -> list[list[str]]:
        sheet = wb.sheets()[0]
        return self._process_sheet(sheet)

    def _process_sheet(self, sheet) -> list[list[str]]:
        sheet_rows = []
        header_col_map = {sheet.cell(0, col).value: col for col in range(sheet.ncols)}
        for row in range(sheet.nrows):
            row_vals = self._process_row(sheet, row, header_col_map)
            sheet_rows.append(row_vals)
        return sheet_rows

    def _process_row(
        self, sheet, row: int, header_col_map: dict[str, int]
    ) -> list[str]:
        row_vals = [
            self._process_cell(sheet.cell(row, col).value) for col in range(sheet.ncols)
        ]

        operator = sheet.cell(row, header_col_map["Оператор связи"]).value
        if operator == '"Т2 Мобайл" ООО':
            row_vals[header_col_map["MNC"]] = "20"
        if operator == '"Ростелеком" ПАО':
            row_vals[header_col_map["MNC"]] = "39"

        return row_vals

    def _process_cell(self, cell_val) -> str:
        if type(cell_val) is float:
            cell_val = repr(cell_val).split(".")[0]
        return force_str(cell_val)


CONVERTERS = {
    ".xls": XlsToCsvConverter(),
}


def _is_skipped(extension):
    if extension not in CONVERTERS.keys():
        print("Skip convert to csv")
        return True
    print(f"Start convert {extension} to csv")
    return False


def convert_to_csv(fl):
    is_file = type(fl) == InMemoryUploadedFile
    fp = Path(fl.name) if is_file else Path(fl)
    ext = fp.suffix
    if _is_skipped(ext):
        content = fl if is_file else open(fl, "r")
    else:
        fn = CONVERTERS.get(ext)
        file_content = io.BytesIO(fl.read()) if is_file else fp
        content = fn.convert(file_content)  # type: ignore

    return content
