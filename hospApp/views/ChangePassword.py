from django.shortcuts import render, redirect
from django.contrib import messages
from hospApp.models import Tbluserpermission
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def ChangePassword(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Validate fields
        if not username or not current_password or not new_password or not confirm_password:
            messages.error(request, "All fields are required.")
            return redirect('ChangePassword')

        try:
            user = Tbluserpermission.objects.get(username=username)
        except Tbluserpermission.DoesNotExist:
            messages.error(request, "Username not found.")
            return redirect('ChangePassword')

        # Plain-text password check
        if user.password != current_password:
            messages.error(request, "Current password is incorrect.")
            return redirect('ChangePassword')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('ChangePassword')

        # Update password directly
        user.password = new_password
        user.save()
        messages.success(request, "Password changed successfully!")
        return redirect('login')
    UserNameDrop = request.user.username

    return render(request, 'hospApp/Admin/ChangePassword.html', {'UserNameDrop':UserNameDrop}   )
