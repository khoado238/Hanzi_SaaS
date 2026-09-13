# hanzi_app/models.py
from django.db import models
from django.contrib.auth.models import User

class PartnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Tài khoản đối tác")
    watermark_text = models.CharField(max_length=100, verbose_name="Nội dung Watermark", blank=True, null=True)

    def __str__(self):
        return f"Cài đặt của: {self.user.username}"