from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from author.form import UserForm


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect('/')
            else:
                return render(request, 'layouts/login.html', {'form': user})
        else:
            return render(request, 'layouts/login.html', {'error': 'Tài khoản hoặc mật khẩu không đúng'})
    return render(request, 'layouts/login.html', {})


def user_logout(request):
    logout(request)
    return redirect('/accounts/login')


def user_register(request):
    register = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            register = True
        else:
            return render(request, 'layouts/register.html', {'user_form': user_form.errors})
    else:
        user_form = UserForm()
    return render(request, 'layouts/register.html', {'user_form': user_form, 'register': register})
