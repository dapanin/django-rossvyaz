from django import forms


class ImportForm(forms.Form):

    import_file = forms.FileField()
    phone_type = forms.CharField(initial='def')
    coding = forms.CharField(initial='utf-8')
    with_clean = forms.BooleanField(required=False, initial=False)
    skip_header = forms.BooleanField(required=False, initial=True)
    dry_run = forms.BooleanField(required=False, initial=False)
