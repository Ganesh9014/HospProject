from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from hospApp.models import ProMaster
from django.db import models
from django.contrib.auth.decorators import login_required
import re


@login_required(login_url='login')
def ProMasterView(request):

    # ============================
    # Helper: Mobile validation
    # ============================
    def is_valid_mobile(number: str) -> bool:
        if not number:
            return False
        if not re.fullmatch(r'\d{10}', number):
            return False
        if len(set(number)) == 1:
            return False
        if not number.startswith(('6', '7', '8', '9')):
            return False
        return True

    # ============================
    # POST HANDLING (NO RENDER)
    # ============================
    if request.method == 'POST':

        operation = request.POST.get('operation', 'add')
        search_text = (request.POST.get('search_text') or '').strip()

        # ---------- ADD ----------
        if 'add_btn' in request.POST and operation == 'add':
            pro_name = (request.POST.get('pro_name') or '').strip()
            phone = (request.POST.get('phone') or '').strip()

            if not pro_name:
                messages.error(request, "Please enter Professional Name.")
            elif not phone:
                messages.error(request, "Please enter Phone Number.")
            elif not is_valid_mobile(phone):
                messages.error(
                    request,
                    "Please enter a valid 10-digit mobile number starting with 6/7/8/9 and not all identical digits."
                )
            elif ProMaster.objects.filter(
                pro_name__iexact=pro_name,
                phone__iexact=phone,
                active='Y'
            ).exists():
                messages.error(request, "This Professional already exists.")
            else:
                ProMaster.objects.create(
                    pro_name=pro_name,
                    phone=phone,
                    active='Y',
                    createdby=request.user.username if request.user.is_authenticated else 'system'
                )
                messages.success(request, f"Professional '{pro_name}' added successfully.")

            return redirect(request.path + "?operation=add")

        # ---------- UPDATE ----------
        if 'update_btn' in request.POST and operation == 'modify':
            update_id = request.POST.get('update_btn')

            try:
                pro = ProMaster.objects.get(pk=update_id, active='Y')
                new_name = (request.POST.get(f'pro_name_{update_id}') or '').strip()
                new_phone = (request.POST.get(f'phone_{update_id}') or '').strip()

                if not new_name:
                    messages.error(request, "Please enter Professional Name.")
                elif not is_valid_mobile(new_phone):
                    messages.error(
                        request,
                        "Please enter a valid 10-digit mobile number starting with 6/7/8/9 and not all identical digits."
                    )
                else:
                    pro.pro_name = new_name
                    pro.phone = new_phone
                    pro.updatedby = request.user.username if request.user.is_authenticated else 'system'
                    pro.updateddate = timezone.now()
                    pro.save()
                    messages.success(request, f"'{pro.pro_name}' updated successfully.")

            except ProMaster.DoesNotExist:
                messages.error(request, "Record not found.")

            qs = "?operation=modify"
            if search_text:
                qs += f"&search_text={search_text}"
            return redirect(request.path + qs)

        # ---------- DELETE ----------
        if 'delete_btn' in request.POST and operation == 'delete':
            delete_id = request.POST.get('delete_btn')

            try:
                pro = ProMaster.objects.get(pk=delete_id, active='Y')
                pro.active = 'N'
                pro.updatedby = request.user.username if request.user.is_authenticated else 'system'
                pro.updateddate = timezone.now()
                pro.save()
                messages.success(request, f"'{pro.pro_name}' deleted successfully.")
            except ProMaster.DoesNotExist:
                messages.error(request, "Record not found.")

            return redirect(request.path + "?operation=delete")

    # ============================
    # GET HANDLING (ONLY RENDER)
    # ============================
    operation = request.GET.get('operation', 'add')
    search_text = (request.GET.get('search_text') or '').strip()

    promaster_list = ProMaster.objects.filter(active='Y').order_by('pro_name')

    if search_text:
        promaster_list = promaster_list.filter(
            models.Q(pro_name__icontains=search_text) |
            models.Q(phone__icontains=search_text)
        )

    return render(request, 'hospApp/Admin/ProMaster.html', {
        'operation': operation,
        'promaster_list': promaster_list,
        'search_text': search_text,
    })
