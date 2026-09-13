from django import forms
from django.contrib.auth.models import User

class PartnerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu")
    watermark = forms.CharField(max_length=100, label="Tên Watermark (Thương hiệu)")

    class Meta:
        model = User
        fields = ['username', 'password']
        labels = {
            'username': 'Tên đăng nhập'
        }