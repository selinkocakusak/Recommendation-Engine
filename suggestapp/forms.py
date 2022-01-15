from django import forms
from django.forms import ModelForm
from .models import reader

MY_CHOICES = [('Algorithms', 'Algorithms'),
              ('Artificial Intelligence', 'Artificial Intelligence'),
              ('Networking', 'Networking'),
              ('Wireless Communication', 'Wireless Communication'),
              ('Data Science', 'Data Science'),
              ('Molecular Communication', 'Molecular Communication'),
              ('Computer Science', 'Computer Science')]


class readerForm(forms.ModelForm):
    email = forms.EmailField(max_length=150)
    keywords = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=MY_CHOICES,
    )

    class Meta:
        model = reader
        fields = ('email', 'keywords')
