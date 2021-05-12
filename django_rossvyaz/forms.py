from django import forms


class ImportForm(forms.Form):

    import_file = forms.FileField()
    phone_type = forms.CharField(initial='def')
    with_clean = forms.NullBooleanField()
    coding = forms.CharField(initial='utf-8')
