

from hospApp.models import Tbluserpermission
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import login as django_login, get_user_model
from hospApp.forms import LoginForm
from hospApp.models.Login import Login
from hospApp.models.menus import MainMenu
from django.contrib.auth.decorators import login_required
from django.urls import reverse, NoReverseMatch 
from hospApp.models.tblroles import tblRoles
from hospApp.forms.EmpForms import EmployeeForm
import json

from django.views.decorators.cache import never_cache
from django.views.decorators.cache import never_cache

@login_required(login_url='login')
@never_cache
def add_employee(request):

    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.emp_id = generate_empid()   
            employee.createdby = request.user.username
            employee.creaddate = timezone.now()
            employee.save()

            messages.success(request, "Employee added successfully!")
            return redirect('empRegistration')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EmployeeForm(initial={
            'emp_id': generate_empid()   
        })

    return render(request, 'hospApp/empRegistration.html', {
        'form': form,
    })


def generate_empid():
    from hospApp.models import HospitalMaster, Employee

    hospital = HospitalMaster.objects.first()
    initial = hospital.initial.upper()   # 'sh'

    last_emp = (
        Employee.objects
        .filter(emp_id__startswith=initial)
        .order_by('-emp_id')
        .first()
    )

    if last_emp:
        last_number = int(last_emp.emp_id.replace(initial, ''))
        next_number = last_number + 1
    else:
        next_number = 1

    return f"{initial}{next_number:02d}"   # sh0001, sh1000
