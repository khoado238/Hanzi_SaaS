from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import PartnerProfile

# 1. Nhúng phần Watermark vào chung với trang của User
class PartnerProfileInline(admin.StackedInline):
    model = PartnerProfile
    can_delete = False
    verbose_name_plural = 'Thông tin Đối tác (Watermark)'

# 2. Tạo giao diện quản lý User mới, trực quan hơn
class CustomUserAdmin(UserAdmin):
    # Khai báo các cột sẽ hiển thị ở bảng tổng sắp
    list_display = ('username', 'email', 'get_watermark', 'is_active', 'is_staff', 'date_joined')
    
    # Thêm bộ lọc ở cột bên phải
    list_filter = ('is_active', 'is_staff', 'date_joined')
    
    # Nhúng giao diện Watermark vào
    inlines = (PartnerProfileInline, )

    # Hàm kéo tên Watermark từ Database ra để hiển thị thành 1 cột
    def get_watermark(self, instance):
        try:
            return instance.partnerprofile.watermark_text
        except:
            return "---"
    get_watermark.short_description = 'Tên Watermark'

# 3. Gỡ giao diện User mặc định và áp dụng giao diện Custom này
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)