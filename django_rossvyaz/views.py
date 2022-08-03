from django.shortcuts import render

from django_rossvyaz.forms import ImportForm
from django_rossvyaz.updater import do_update, UpdateError
from django_rossvyaz.utils import CONVERTERS, DEFAULT_EXT, convert_to_csv


def rossvyaz_update(request):
    form = ImportForm(data=request.POST or None, files=request.FILES or None)

    errors = ''
    success = None
    update_result = ''
    if form.is_valid():
        phone_type = form.cleaned_data['phone_type']
        coding = form.cleaned_data['coding']
        import_file = form.cleaned_data['import_file']
        with_clean = form.cleaned_data['with_clean']
        skip_header = form.cleaned_data['skip_header']
        dry_run = form.cleaned_data['dry_run']

        try:
            with import_file:
                update_result = do_update(convert_to_csv(import_file), phone_type, with_clean, coding, skip_header, dry_run)
        except UpdateError as exc:
            errors = str(exc)
        else:
            success = True

    context = {
        'form': form,
        'errors': errors,
        'success': success,
        'update_result': update_result,
        'supported_extensions': ", ".join([DEFAULT_EXT] + list(CONVERTERS.keys()))
    }
    return render(request, 'django_rossvyaz/import.html', context)
