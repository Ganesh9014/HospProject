from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from hospApp.models.DepartmentPhotoMaster import DepartmentPhotoMaster


@login_required(login_url='login')
def InvDepartmentMasterView(request):

    operation = request.GET.get("operation", "add")
    search_term = request.GET.get("search", "").strip()

    # ============================
    # POST HANDLING (NO RENDER)
    # ============================
    if request.method == "POST":

        operation = request.POST.get("operation", "add")

        # ---------- ADD ----------
        if operation == "add":
            dept = (request.POST.get("department") or "").strip()
            name = (request.POST.get("name") or "").strip()
            regno = (request.POST.get("reg_no") or "").strip()
            signature_file = request.FILES.get("signature")

            if not dept:
                messages.error(request, "Please enter Department Name.")
            elif DepartmentPhotoMaster.objects.filter(
                department__iexact=dept, active='Y'
            ).exists():
                messages.error(request, f"Department '{dept}' already exists.")
            else:
                DepartmentPhotoMaster.objects.create(
                    department=dept,
                    name=name,
                    regno=regno,
                    signature=signature_file,
                    active='Y',
                    createdby=request.user.username,
                    createddate=timezone.now(),
                )
                messages.success(
                    request,
                    f"Department '{dept}' added successfully."
                )

            return redirect(request.path + "?operation=add")

        # ---------- MODIFY ----------
        # ---------- MODIFY ----------
        if operation == "modify" and request.POST.get("update_id"):
            update_id = request.POST.get("update_id")
            new_department = (request.POST.get(f"department_{update_id}") or "").strip()
            new_name = (request.POST.get(f"name_{update_id}") or "").strip()
            new_regno = (request.POST.get(f"regno_{update_id}") or "").strip()
            new_signature = request.FILES.get(f"signature_{update_id}")
            if not new_department:
                messages.error(request, "Department name cannot be empty.")
            elif DepartmentPhotoMaster.objects.filter(
                department__iexact=new_department,
                active='Y'
            ).exclude(dno=update_id).exists():
                messages.error(request, "Another department already uses this name.")
            else:
                try:
                    dep = DepartmentPhotoMaster.objects.get(
                        dno=update_id,
                        active='Y'
                    )

                    dep.department = new_department
                    dep.name = new_name
                    dep.regno = new_regno

                    if new_signature:               # ← ADD this block
                        dep.signature = new_signature

                    dep.updatedby = request.user.username
                    dep.updatedtime = timezone.now()
                    dep.save()

                    messages.success(
                        request,
                        "Department updated successfully."
                    )

                except DepartmentPhotoMaster.DoesNotExist:
                    messages.error(request, "Department not found.")

            return redirect(request.path + f"?operation=modify&search={search_term}")

        # ---------- DELETE ----------
        if operation == "delete" and request.POST.get("delete_id"):
            delete_id = request.POST.get("delete_id")

            try:
                dep = DepartmentPhotoMaster.objects.get(dno=delete_id, active='Y')
                dep.active = 'N'
                dep.updatedby = request.user.username
                dep.updatedtime = timezone.now()
                dep.save()
                messages.success(
                    request,
                    f"Department '{dep.department}' deleted."
                )
            except DepartmentPhotoMaster.DoesNotExist:
                messages.error(request, "Department not found.")

            return redirect(
                request.path + f"?operation=delete&search={search_term}"
            )

        return redirect(request.path + f"?operation={operation}")

    # ============================
    # GET HANDLING (ONLY RENDER)
    # ============================
    records = None

    if operation in ["add", "modify", "delete"]:
        records = DepartmentPhotoMaster.objects.filter(active='Y')

        if search_term:
            records = records.filter(department__icontains=search_term)

        records = records.order_by('department')

    return render(
        request,
        "hospApp/Admin/InvDepartmentMaster.html",
        {
            "operation": operation,
            "search_term": search_term,
            "records": records,
        }
    )
