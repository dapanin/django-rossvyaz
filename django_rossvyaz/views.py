from django.shortcuts import render

from django_rossvyaz.forms import ImportForm
from django_rossvyaz.updater import do_update, UpdateError


def rossvyaz_update(request):
    form = ImportForm(data=request.POST or None, files=request.FILES or None)

    errors = ''
    success = None
    if form.is_valid():
        import_file = form.cleaned_data['import_file']
        phone_type = form.cleaned_data['phone_type']
        with_clean = form.cleaned_data['with_clean_region']
        coding = form.cleaned_data['coding']
        try:
            do_update(import_file, phone_type, with_clean, coding)
        except UpdateError as exc:
            errors = str(exc)
        else:
            success = True

    context = {
        'form': form,
        'errors': errors,
        'success': success,
    }
    return render(request, 'django_rossvyaz/import.html', context)
