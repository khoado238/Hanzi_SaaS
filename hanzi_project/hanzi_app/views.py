import hmac
import hashlib
import subprocess
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import PartnerRegistrationForm
from .models import PartnerProfile

# 1. TRANG ĐĂNG KÝ (Dành cho đối tác mới)
def register_view(request):
    success = False
    if request.method == 'POST':
        form = PartnerRegistrationForm(request.POST)
        if form.is_valid():
            # Tạo tài khoản nhưng KHÓA LẠI chờ phê duyệt
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False # Mấu chốt là dòng này
            user.save()

            # Lưu Watermark vào Database
            PartnerProfile.objects.create(
                user=user,
                watermark_text=form.cleaned_data['watermark']
            )
            success = True
    else:
        form = PartnerRegistrationForm()
    
    return render(request, 'register.html', {'form': form, 'success': success})

# 2. TRANG ĐĂNG NHẬP
def login_view(request):
    error_message = None
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        
        if user is not None:
            login(request, user)
            return redirect('hanzi_tool')
        else:
            # Kiểm tra xem có phải do chưa được duyệt không
            try:
                from django.contrib.auth.models import User
                check_user = User.objects.get(username=u)
                if not check_user.is_active and check_user.check_password(p):
                    error_message = "Tài khoản của bạn đang chờ Admin phê duyệt!"
                else:
                    error_message = "Sai tài khoản hoặc mật khẩu."
            except:
                error_message = "Sai tài khoản hoặc mật khẩu."

    return render(request, 'login.html', {'error': error_message})

# 3. TRANG CÔNG CỤ (Giữ nguyên như cũ)
@login_required(login_url='/login/') 
def hanzi_tool_view(request):
    watermark_text = request.user.username 
    if hasattr(request.user, 'partnerprofile'):
        if request.user.partnerprofile.watermark_text:
            watermark_text = request.user.partnerprofile.watermark_text
    context = {'watermark_text': watermark_text}
    return render(request, 'hanzi_generator.html', context)

# 4. WEBHOOK TỰ ĐỘNG CẬP NHẬT CODE
@csrf_exempt
def github_webhook(request):
    # Mật mã bảo mật (Bạn có thể đổi thành chữ khác nếu muốn)
    secret_key = 'HanziSaaS2026' 
    
    # Kiểm tra xem có phải GitHub gọi không
    github_signature = request.META.get('HTTP_X_HUB_SIGNATURE_256')
    if not github_signature:
        return HttpResponseForbidden('Không có quyền truy cập!')

    # Xác thực mật mã
    signature = github_signature.replace('sha256=', '')
    mac = hmac.new(secret_key.encode(), msg=request.body, digestmod=hashlib.sha256)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        return HttpResponseForbidden('Sai mật mã!')

    # Nếu đúng mật mã, ra lệnh tự động Pull và Reload
    if request.method == 'POST':
        try:
            # 1. Kéo code về
            subprocess.run(['git', 'pull'], cwd='/home/ddkhoa238/hanzi_project', check=True)
            # 2. Khởi động lại Server
            subprocess.run(['touch', '/var/www/ddkhoa238_pythonanywhere_com_wsgi.py'], check=True)
            return HttpResponse('Đã cập nhật code và khởi động lại Server!', status=200)
        except subprocess.CalledProcessError:
            return HttpResponse('Có lỗi xảy ra khi kéo code.', status=500)
    
    return HttpResponseForbidden('Phương thức không hợp lệ.')