"""
URL configuration for hanzi_project project.
"""
from django.contrib import admin
from django.urls import path
from hanzi_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.hanzi_tool_view, name='hanzi_tool'), # Đường dẫn trang chủ sẽ vào thẳng công cụ
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
]