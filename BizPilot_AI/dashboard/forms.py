from django import forms

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="Select Business CSV File",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )