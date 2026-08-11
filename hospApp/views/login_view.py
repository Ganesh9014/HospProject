from hospApp.models import Tbluserpermission
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import login as django_login, get_user_model
from hospApp.forms import LoginForm
from hospApp.models.Login import Login
from django.contrib.auth.hashers import check_password

from django.http import HttpResponse
from django.utils import timezone
import json, base64

def login_view(request):
    # ── Auto-fill from remember_me cookie ──────────────────────────────
    remembered = {}
    if 'remember_me' in request.COOKIES:
        try:
            remembered = json.loads(
                base64.b64decode(request.COOKIES['remember_me']).decode()
            )
        except Exception:
            remembered = {}
    # ───────────────────────────────────────────────────────────────────

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']
            remember_me = request.POST.get('remember_me')

            try:
                user = Tbluserpermission.objects.get(
                    username=username,
                    password=password,
                    isactive=True
                )
            except Tbluserpermission.DoesNotExist:
                messages.error(request, "Invalid username or password.")
                return redirect('login')

            Login.objects.create(
                user=user,
                name=user.empname,
                logintime=timezone.now()
            )

            request.session['username'] = user.username
            request.session['empname'] = getattr(user, 'empname', '')
            request.session['role_id'] = getattr(user.mainrole, 'roleid', None)
            request.session['role_name'] = getattr(user.mainrole, 'rolename', None)

            UserModel = get_user_model()
            django_user, _ = UserModel.objects.get_or_create(username=user.username)
            django_login(request, django_user)

            response = redirect('home')

            if remember_me:
                # Store username in a cookie for 30 days (password never stored)
                payload = base64.b64encode(
                    json.dumps({'username': username}).encode()
                ).decode()
                response.set_cookie(
                    'remember_me',
                    payload,
                    max_age=60 * 60 * 24 * 30,  # 30 days
                    httponly=True,
                    samesite='Lax'
                )
            else:
                # Clear any existing remember_me cookie
                response.delete_cookie('remember_me')

            return response

    else:
        # Pre-fill username if cookie exists
        initial = {'username': remembered.get('username', '')}
        form = LoginForm(initial=initial)

    return render(request, 'hospApp/login.html', {
        'form': form,
        'remembered_username': remembered.get('username', '')
    })
from django.contrib.auth import logout as django_logout

def logout_view(request):
    username = request.session.get('username')

    if username:
        try:
            user = Tbluserpermission.objects.get(username=username)
            latest_login = Login.objects.filter(user=user).order_by('-logintime').first()
            if latest_login:
                latest_login.logouttime = timezone.now()
                latest_login.save()
        except Tbluserpermission.DoesNotExist:
            pass

    django_logout(request)
    request.session.flush()

    response = redirect('login')
    response.delete_cookie('remember_me')  # ← clear on explicit logout
    return response