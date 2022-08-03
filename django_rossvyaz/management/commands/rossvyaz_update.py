from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand, CommandError

from django_rossvyaz.conf import ROSSVYAZ_SOURCE_URLS
from django_rossvyaz.updater import do_update, UpdateError
from django_rossvyaz.utils import convert_to_csv


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--phone-type', type=str)
        parser.add_argument('--filename', type=str, default=None)
        parser.add_argument('--encoding', type=str, default=None)
        parser.add_argument('--with-clean', dest='feature_with_clean', action='store_true')
        parser.add_argument('--skip-header', dest='feature_skip_header', action='store_true')
        parser.add_argument('--dry-run', dest='feature_dry_run', action='store_true')
        parser.set_defaults(feature_with_clean=False)
        parser.set_defaults(feature_skip_header=False)
        parser.set_defaults(feature_dry_run=False)

    def handle(self, *args, **options):

        phone_type = options['phone_type']
        filename = options['filename']
        coding = options['encoding']
        with_clean = options['feature_with_clean']
        skip_header = options['feature_skip_header']
        dry_run = options['feature_dry_run']

        if filename is None:
            source_url = ROSSVYAZ_SOURCE_URLS[phone_type]
            print(f'Download csv-file: {source_url}...')
            import_file = urlopen(Request(source_url))
        else:
            print(f'Open file: {filename}...')
            import_file = convert_to_csv(filename)

        try:
            with import_file:
                update_result = do_update(import_file, phone_type, with_clean, coding, skip_header, dry_run)
                print(update_result)
        except UpdateError as exc:
            raise CommandError(exc)
