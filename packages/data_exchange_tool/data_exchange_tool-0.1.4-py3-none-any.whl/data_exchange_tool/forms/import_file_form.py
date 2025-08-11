from django import forms


class ImportFileForm(forms.Form):
    file = forms.FileField(label="Fichero de importación")
