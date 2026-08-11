from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from hospApp.models import DepartmentPhotoMaster
from hospApp.models.InvestigationMaster import InvestigationMaster
from hospApp.models.InvGroupMaster import InvGroupMaster


@login_required(login_url='login')
def InvestigationMasterView(request):

    operation = request.GET.get("operation", "add")
    search_term = request.GET.get("search", "").strip()

    departments = DepartmentPhotoMaster.objects.filter(active='Y').order_by('department')
    groups = InvGroupMaster.objects.filter(active='Y').order_by('gname')

    # ============================
    # POST HANDLING
    # ============================
    if request.method == "POST":

        operation = request.POST.get("operation", "add")

        # ---------- ADD ----------
        if operation == "add":
            invname = request.POST.get("invname", "").strip()
            dept_id = request.POST.get("department")
            grp = request.POST.get("groups", "").strip()
            cost = request.POST.get("cost", "0").strip()
            ip = request.POST.get("ip", "0").strip()

            if not invname:
                messages.error(request, "Please enter Investigation Name.")

            elif InvestigationMaster.objects.filter(
                invname__iexact=invname, active='Y'
            ).exists():
                messages.error(request, f"Investigation '{invname}' already exists.")

            else:
                try:
                    department_obj = DepartmentPhotoMaster.objects.get(dno=dept_id)
                except DepartmentPhotoMaster.DoesNotExist:
                    messages.error(request, "Invalid Department selected.")
                    return redirect(request.path + "?operation=add")

                InvestigationMaster.objects.create(
                    invname=invname,
                    department=department_obj,   # ✅ FK
                    groups=grp,
                    cost=cost,
                    ip=ip,
                    active='Y',
                    createdby=request.user.username,
                    createddate=timezone.now(),
                )

                messages.success(
                    request,
                    f"Investigation '{invname}' added successfully."
                )

            return redirect(request.path + "?operation=add")

        # ---------- MODIFY ----------
        if operation == "modify" and request.POST.get("update_id"):
            update_id = request.POST.get("update_id")
            new_name = request.POST.get(f"invname_{update_id}", "").strip()
            new_cost = request.POST.get(f"cost_{update_id}", "").strip()

            try:
                inv = InvestigationMaster.objects.get(ino=update_id, active='Y')

                if InvestigationMaster.objects.filter(
                    invname__iexact=new_name, active='Y'
                ).exclude(ino=update_id).exists():
                    messages.error(request, "Another investigation already uses this name.")
                else:
                    inv.invname = new_name
                    inv.cost = new_cost
                    inv.updatedby = request.user.username
                    inv.updateddate = timezone.now()
                    inv.save()

                    messages.success(request, "Investigation updated successfully.")

            except InvestigationMaster.DoesNotExist:
                messages.error(request, "Investigation not found.")

            return redirect(
                request.path + f"?operation=modify&search={search_term}"
            )

        # ---------- DELETE ----------
        if operation == "delete" and request.POST.get("delete_id"):
            delete_id = request.POST.get("delete_id")

            try:
                inv = InvestigationMaster.objects.get(ino=delete_id, active='Y')
                inv.active = 'N'
                inv.updatedby = request.user.username
                inv.updateddate = timezone.now()
                inv.save()

                messages.success(
                    request,
                    f"Investigation '{inv.invname}' deleted."
                )

            except InvestigationMaster.DoesNotExist:
                messages.error(request, "Investigation not found.")

            return redirect(
                request.path + f"?operation=delete&search={search_term}"
            )

        return redirect(request.path + f"?operation={operation}")

    # ============================
    # GET HANDLING
    # ============================
    records = None

    if operation in ["add", "modify", "delete"]:
        records = InvestigationMaster.objects.filter(active='Y')\
                    .select_related('department')  # 🚀 performance

        if search_term:
            records = records.filter(invname__icontains=search_term)

        records = records.order_by('invname')

    return render(
        request,
        "hospApp/Admin/InvestigationMaster.html",
        {
            "operation": operation,
            "search_term": search_term,
            "records": records,
            "departments": departments,
            "groups": groups,
        }
    )