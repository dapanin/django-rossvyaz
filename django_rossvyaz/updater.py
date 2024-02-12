import csv
import sys
import traceback
from smtplib import SMTPAuthenticationError
from typing import Optional

from django.core.mail import mail_admins
from django.db import connection, transaction

from django_rossvyaz.conf import ROSSVYAZ_CODING, ROSSVYAZ_SEND_MESSAGE_FOR_ERRORS
from django_rossvyaz.logic import CleanRegionError, clean_operator, clean_region
from django_rossvyaz.models import PhoneCode
from django_rossvyaz.utils import CSV_ARGS


ORIGINAL_TABLE_NAME = 'django_rossvyaz_phonecode'
COPY_TABLE_NAME = 'django_rossvyaz_phonecode_v2'
TEMP_TABLE_NAME = 'django_rossvyaz_phonecode_temp'

CREATE_COPY_TABLE_SQL = f"""
    CREATE TABLE {COPY_TABLE_NAME} AS
    SELECT * FROM {ORIGINAL_TABLE_NAME}
    WHERE phone_type<>'{{}}';
"""

INSERT_SQL = f"""
    INSERT INTO {COPY_TABLE_NAME}
    (first_code, from_code, to_code, block_size, operator, region, mnc, phone_type)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

RENAME_TABLE_SQL = """
    ALTER TABLE {} RENAME TO {};
"""

DROP_TABLE_SQL = """
    DROP TABLE IF EXISTS {};
"""
ERROR_SUBJECT = "Error of command rossvyaz_update"
send_message = ROSSVYAZ_SEND_MESSAGE_FOR_ERRORS

avail_types = {item[0] for item in PhoneCode.PHONE_TYPE_CHOICES}

OPERATOR_INDEX = 4
REGION_INDEX = 5
MNC_INDEX = 6
COLS_COUNT = INSERT_SQL.count("%") - 1


class UpdateError(Exception):
    pass


def do_update(
    import_file,
    phone_type,
    with_clean: bool = False,
    coding: Optional[str] = None,
    skip_header: bool = False,
    dry_run: bool = False,
) -> str:
    if coding is None:
        coding = ROSSVYAZ_CODING

    if phone_type not in avail_types:
        _handle_error(
            f"Bad phone_type={repr(phone_type)} (Avail only: {repr(avail_types)}. "
            "Add new type to django_rossvyaz.models.PhoneCode.PHONE_TYPE_CHOICES"
            ")"
        )

    def csv_iter():
        for line in import_file:
            try:
                line = line.decode(coding).strip()
            except AttributeError:
                line = line.strip()
            if line:
                yield line

    phonecode_reader = csv.reader(csv_iter(), **CSV_ARGS)

    print("Start updating...")
    lines = _get_phonecode_lines(phonecode_reader, phone_type, with_clean, skip_header)
    dry_run_msg = "[DRY RUN] "
    if not dry_run:
        dry_run_msg = ""
        try:
            cursor = connection.cursor()
            _execute_sql(cursor, lines, phone_type)
        except Exception:
            _handle_error()
    return f"{dry_run_msg}Table rossvyaz phonecode is updated with {len(lines)} lines.\n"


def _get_phonecode_lines(phonecode_reader, phone_type, with_clean, skip_header):
    ret = []
    for rossvyaz_row in phonecode_reader:
        rossvyaz_row = rossvyaz_row[:COLS_COUNT]

        operator = rossvyaz_row[OPERATOR_INDEX]
        if operator == '"Т2 Мобайл" ООО':
            rossvyaz_row[MNC_INDEX] = "20"
        elif operator == '"Ростелеком" ПАО':
            rossvyaz_row[MNC_INDEX] = "39"

        if with_clean:
            operator = rossvyaz_row[OPERATOR_INDEX]
            region_name = rossvyaz_row[REGION_INDEX]

            rossvyaz_row[OPERATOR_INDEX] = clean_operator(operator)
            try:
                rossvyaz_row[REGION_INDEX] = clean_region(region_name)
            except CleanRegionError:
                _handle_error()

        row = rossvyaz_row + [phone_type]
        ret.append(row)
    return ret[int(skip_header) :]


def _execute_sql(cursor, lines, phone_type):
    print("Create new table from select...")
    cursor.execute(DROP_TABLE_SQL.format(TEMP_TABLE_NAME))
    cursor.execute(DROP_TABLE_SQL.format(COPY_TABLE_NAME))
    cursor.execute(CREATE_COPY_TABLE_SQL.format(phone_type))

    print("Write new data...")
    cursor.executemany(INSERT_SQL, [l for l in lines if l])

    print("Replace names...")
    with transaction.atomic():
        cursor.execute(RENAME_TABLE_SQL.format(ORIGINAL_TABLE_NAME, TEMP_TABLE_NAME))
        cursor.execute(RENAME_TABLE_SQL.format(COPY_TABLE_NAME, ORIGINAL_TABLE_NAME))

    print("Drop old table...")
    cursor.execute(DROP_TABLE_SQL.format(TEMP_TABLE_NAME))


def _handle_error():
    message = f"The data not updated: {traceback.format_exception(*sys.exc_info())}"
    if send_message:
        try:
            mail_admins(subject=ERROR_SUBJECT, message=message)
        except SMTPAuthenticationError as err:
            message = f"{message}. Send email failed cause {repr(err)}"
    raise UpdateError(message)
