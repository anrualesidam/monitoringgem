from django import forms

class ArchivoForm(forms.Form):
    archivo = forms.FileField()

class ContactForm(forms.Form): 
    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    content = forms.CharField(widget=forms.Textarea)