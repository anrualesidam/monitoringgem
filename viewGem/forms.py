from django import forms

class ArchivoForm(forms.Form):
    archivo = forms.FileField()