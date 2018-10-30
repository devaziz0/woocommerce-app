from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from .models import *

class ProfileForm(ModelForm):
    photo = forms.ImageField(required=False)

    class Meta:
        model = Profil
        fields = ['photo', 'birthday','gender', 'mailing_Address']
        widgets = {
                'password':forms.PasswordInput(),
                'birthday': forms.DateInput(attrs={'type':'date','class':'form-control'}),
                'mailing_Address':forms.TextInput(attrs= {'class':'form-control'}),


        }

class UserForm(ModelForm):

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
                'password':forms.PasswordInput(attrs= {'class':'form-control'}),
                'username' : forms.TextInput(attrs= {'class':'form-control'}),
                'first_name' : forms.TextInput(attrs= {'class':'form-control'}),
                'last_name' : forms.TextInput(attrs= {'class':'form-control'}),
                'email' : forms.TextInput(attrs= {'class':'form-control'}),
                'gender' : forms.Select(attrs= {'class': 'form-control'})



        }
        help_texts = {
            'username': '20 characters or fewer. Letters, digits and @/./+/-/_ only.',
        }
class ScheduleForm(ModelForm):

    class Meta:
        model= Schedule
        fields = ['AliExpress_key',
                    'AliExpress_Id',
                    #'AliExpress_fields',
                    'AliExpress_keywords',
                    'AliExpress_category',
                    'AliExpress_Currency',
                    'AliExpress_Increment',
                    'AliExpress_language',
                    'AliExpress_highquality',
                    'woocommerce_url',
                    'woocommerce_consumer_key',
                    'woocommerce_secret_key',

                    ]
        widgets = {
                'AliExpress_key' : forms.TextInput(attrs= {'class':'form-control'}),
                'AliExpress_Id' : forms.TextInput(attrs= {'class':'form-control'}),
                'AliExpress_keywords' : forms.TextInput(attrs= {'class':'form-control'}),
                'AliExpress_category' : forms.Select(attrs= {'class':'form-control'}),
                'AliExpress_highquality' : forms.Select(attrs= {'class':'form-control'}),
                'AliExpress_Currency' : forms.Select(attrs= {'class':'form-control'}),
                'AliExpress_language' : forms.Select(attrs= {'class':'form-control'}),
                'AliExpress_Increment' : forms.TextInput(attrs= {'class':'form-control'}),
                'woocommerce_url' : forms.TextInput(attrs= {'class':'form-control','placeholder':'http://www.example.com/'}),
                'woocommerce_consumer_key' : forms.TextInput(attrs= {'class':'form-control'}),
                'woocommerce_secret_key' : forms.TextInput(attrs= {'class':'form-control'}),


        }
