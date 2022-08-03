import io
import csv
from pathlib import Path, PosixPath

import xlrd
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.encoding import force_str


CSV_ARGS = {'delimiter': ';', 'quotechar': '"'}
DEFAULT_EXT = '.csv'


def _fmt_cell_val(val):
    if type(val) is float:
        val = repr(val).split(".")[0]
    return force_str(val)


def xls_converter(fl):
    file_contents = None if type(fl) == PosixPath else fl.getvalue()

    wb = xlrd.open_workbook(fl, file_contents=file_contents)
    result = []
    for s in wb.sheets()[:1]:
        for row in range(s.nrows):
            result.append(
                [_fmt_cell_val(s.cell(row, col).value) for col in range(s.ncols)])
    buff = io.StringIO()
    csvwriter = csv.writer(buff, **CSV_ARGS)
    csvwriter.writerows(result)
    buff.seek(0)
    return buff


CONVERTERS = {
    '.xls': xls_converter,
}


def _is_skipped(extension):
    if extension not in CONVERTERS.keys():
        print('Skip convert to csv')
        return True
    print(f'Start convert {extension} to csv')
    return False


def convert_to_csv(fl):
    is_file = type(fl) == InMemoryUploadedFile
    fp = Path(fl.name) if is_file else Path(fl)
    ext = fp.suffix
    if _is_skipped(ext):
        content = fl if is_file else open(fl, 'r')
    else:
        fn = CONVERTERS.get(ext)
        file_content = io.BytesIO(fl.read()) if is_file else fp
        content = fn(file_content)  # type: ignore

    return content
