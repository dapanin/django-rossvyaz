from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand, CommandError

from django_rossvyaz.conf import ROSSVYAZ_SOURCE_URLS
from django_rossvyaz.updater import do_update, UpdateError


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--phone-type', type=str)
        parser.add_argument('--clean-region', type=bool, default=False)
        parser.add_argument('--filename', type=str, default=None)
        parser.add_argument('--encoding', type=str, default=None)

    def handle(self, *args, **options):

        phone_type = options['phone_type']
        with_clean = options['clean_region']
        filename = options['filename']
        coding = options['encoding']

        if filename is None:
            source_url = ROSSVYAZ_SOURCE_URLS[phone_type]
            print(f'Download csv-file: {source_url}...')
            import_file = urlopen(Request(source_url))
        else:
            print(f'Open csv-file: {filename}...')
            import_file = open(filename, 'rb')

        try:
            do_update(import_file, phone_type, with_clean, coding)
        except UpdateError as exc:
            raise CommandError(exc)

