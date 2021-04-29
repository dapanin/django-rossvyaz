import traceback

from django.core.mail import mail_admins
from django.db import connection, transaction

from django_rossvyaz.conf import ROSSVYAZ_CODING, ROSSVYAZ_SEND_MESSAGE_FOR_ERRORS
from django_rossvyaz.logic import (
    clean_region,
    clean_operator,
    CleanRegionError,
)
from django_rossvyaz.models import PhoneCode


DELETE_SQL = "DELETE FROM django_rossvyaz_phonecode WHERE phone_type='{}'"

INSERT_SQL = """
INSERT INTO django_rossvyaz_phonecode
(first_code, from_code, to_code, block_size, operator, region, mnc, phone_type)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

ERROR_SUBJECT = 'Error of command rossvyaz_update'
send_message = ROSSVYAZ_SEND_MESSAGE_FOR_ERRORS


avail_types = {item[0] for item in PhoneCode.PHONE_TYPE_CHOICES}


class UpdateError(Exception):
    pass


def do_update(import_file, phone_type, with_clean, coding):
    if coding is None:
        coding = ROSSVYAZ_CODING

    if phone_type not in avail_types:
        _handle_error(
            f'Bad phone_type={repr(phone_type)} (Avail only: {repr(avail_types)}. '
            'Add new type to django_rossvyaz.models.PhoneCode.PHONE_TYPE_CHOICES'
            ')')

    import_file.readline()  # First line is titles row
    print('Start updating...')
    lines = _get_phonecode_lines(import_file, phone_type, coding, with_clean)
    import_file.close()
    cursor = connection.cursor()
    try:
        with transaction.atomic():
            _execute_sql(cursor, lines, phone_type)
    except Exception as e:
        _handle_error(e)
    return 'Table rossvyaz phonecode is update.\n'


def _get_phonecode_lines(phonecode_file, phone_type, coding, with_clean):
    ret = []
    for l in phonecode_file:
        line = l.decode(coding).strip()
        if not line:
            continue
        rossvyaz_row = line.split(';')
        rossvyaz_row = [v.strip().strip('\'"').strip() for v in rossvyaz_row]
        operator = rossvyaz_row[-2]
        region_name = rossvyaz_row[-1]

        if with_clean:
            rossvyaz_row[-2] = clean_operator(operator)
            try:
                rossvyaz_row[-1] = clean_region(region_name)
            except CleanRegionError as e:
                _handle_error(e)

        row = rossvyaz_row + [phone_type]
        ret.append(row)
    return ret


def _execute_sql(cursor, lines, phone_type):
    print('Delete old rows in table rossvyaz phonecodes...')
    cursor.execute(DELETE_SQL.format(phone_type))
    print('Write new data...')

    cursor.executemany(INSERT_SQL, [l for l in lines if l])


def _handle_error(e):
    message = f'The data not updated: {traceback.format_exception(e)}'
    if send_message:
        mail_admins(subject=ERROR_SUBJECT, message=message)
    raise UpdateError(message)
