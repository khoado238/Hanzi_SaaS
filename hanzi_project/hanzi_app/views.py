import hmac
import hashlib
import subprocess
import urllib.request
import urllib.parse
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import PartnerRegistrationForm
from .models import PartnerProfile

# 1. TRANG ĐĂNG KÝ
def register_view(request):
    success = False
    if request.method == 'POST':
        form = PartnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False
            user.save()
            PartnerProfile.objects.create(
                user=user,
                watermark_text=form.cleaned_data['watermark']
            )
            success = True

            # --- ĐOẠN CODE GỬI THÔNG BÁO TELEGRAM ---
            bot_token = '8705917707:AAEGbjtzg8Co-KD8pJqqSnmnduqcSIT3qXM'
            chat_id = '1334036104'
            message = f"🚨 CÓ ĐỐI TÁC MỚI ĐĂNG KÝ!\n\n👤 Username: {user.username}\n📝 Watermark: {form.cleaned_data['watermark']}\n\n👉 Vào trang /admin để duyệt ngay sếp nhé!"
            
            try:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                data = urllib.parse.urlencode({'chat_id': chat_id, 'text': message}).encode('utf-8')
                req = urllib.request.Request(url, data=data)
                urllib.request.urlopen(req, timeout=5)
            except Exception as e:
                pass # Nếu lỗi gửi tin thì web vẫn cứ đăng ký thành công, không báo lỗi cho người dùng
            # ----------------------------------------

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

# 3. TRANG CÔNG CỤ
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
    secret_key = 'HanziSaaS2026' 
    
    github_signature = request.META.get('HTTP_X_HUB_SIGNATURE_256')
    if not github_signature:
        return HttpResponseForbidden('Không có quyền truy cập!')

    signature = github_signature.replace('sha256=', '')
    mac = hmac.new(secret_key.encode(), msg=request.body, digestmod=hashlib.sha256)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        return HttpResponseForbidden('Sai mật mã!')

    if request.method == 'POST':
        try:
            # Cố gắng kéo code về, nếu lỗi sẽ bắt lại thông báo của Git
            subprocess.run(
                ['git', 'pull'], 
                cwd='/home/ddkhoa238/hanzi_project', 
                capture_output=True, 
                text=True, 
                check=True
            )
            subprocess.run(['touch', '/var/www/ddkhoa238_pythonanywhere_com_wsgi.py'], check=True)
            return HttpResponse('Đã cập nhật code và khởi động lại Server!', status=200)
        except subprocess.CalledProcessError as e:
            # Trả thẳng lỗi Git về GitHub để xem
            return HttpResponse(f"Git báo lỗi: {e.stderr}", status=500)
        except Exception as e:
            return HttpResponse(f"Lỗi hệ thống: {str(e)}", status=500)
    
    return HttpResponseForbidden('Phương thức không hợp lệ.')