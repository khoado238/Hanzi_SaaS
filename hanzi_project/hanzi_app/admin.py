# hanzi_app/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import PartnerProfile

class PartnerProfileInline(admin.StackedInline):
    model = PartnerProfile
    can_delete = False
    verbose_name_plural = 'CÀI ĐẶT WATERMARK NHƯỢNG QUYỀN'
    classes = ('collapse', ) 

class CustomUserAdmin(UserAdmin):
    inlines = (PartnerProfileInline, )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)