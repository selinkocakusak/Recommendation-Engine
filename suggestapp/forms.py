from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm
from .models import reader

MY_CHOICES = [('Algorithms', 'Algorithms'),
              ('Artificial Intelligence', 'Artificial Intelligence'),
              ('Networking', 'Networking'),
              ('Wireless Communication', 'Wireless Communication'),
              ('Data Science', 'Data Science')]


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


# class ProfileForm(forms.Form):
#     # id = forms.IntegerField()
#     email = forms.EmailField(max_length=150)
#     keywords = forms.MultipleChoiceField(
#         required=False,
#         widget=forms.CheckboxSelectMultiple,
#         choices=MY_CHOICES,
#     )

#     class Meta:
#         fields = ('email', 'keywords')


# class ProfileForm(SignUpForm):

#     keywords = forms.MultipleChoiceField(
#         required=False,
#         widget=forms.CheckboxSelectMultiple,
#         choices=MY_CHOICES,
#     )

#     class Meta(SignUpForm.Meta):
#         fields = SignUpForm.Meta.fields + ('keywords',)
# class UserForm(forms.ModelForm):

#     class Meta():
#         model = User
#         fields = ('email', 'id')
# class UserRegisterForm(forms.Form):
#     email = forms.EmailField(label='E-Mail')
# #     # keywords = models.CharField(max_length=200, null=True)
# #     # date = models.DateField(default=datetime.now)

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         if User.objects.filter(email__iexact=email).exists():
#             raise forms.ValidationError(
#                 'A user has already registered using this email')
#         return email

# class Meta():
#     model = User
#     fields = ('id', 'email')
