from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from hospApp.models.InvGroupMaster import InvGroupMaster


@login_required(login_url='login')
def InvGroupMasterView(request):
    """
    Group Master:
    - Default: ADD mode
    - Three modes: add / modify / delete
    - Case-insensitive duplicate checks
    """

    # ============================
    # POST HANDLING (NO RENDER)
    # ============================
    if request.method == "POST":

        operation = request.POST.get("operation") or request.GET.get("operation", "add")
        search_term = (request.POST.get("search") or request.GET.get("search") or "").strip()

        # ---------- ADD ----------
        if operation == "add":
            gname = (request.POST.get("gname") or "").strip()

            if not gname:
                messages.error(request, "Please enter Group Name.")
            elif InvGroupMaster.objects.filter(
                gname__iexact=gname, active='Y'
            ).exists():
                messages.error(
                    request,
                    f"Group '{gname}' already exists (case-insensitive)."
                )
            else:
                InvGroupMaster.objects.create(
                    gname=gname,
                    userid=request.user.username,
                    insertedtime=timezone.now(),
                    active='Y'
                )
                messages.success(
                    request,
                    f"Group '{gname}' added successfully."
                )

            return redirect(request.path + "?operation=add")

        # ---------- MODIFY ----------
        if operation == "modify" and request.POST.get("update_id"):
            update_id = request.POST.get("update_id")
            new_name = (request.POST.get(f"gname_{update_id}") or "").strip()

            if not new_name:
                messages.error(request, "Group Name cannot be empty.")
            elif InvGroupMaster.objects.filter(
                gname__iexact=new_name,
                active='Y'
            ).exclude(sno=update_id).exists():
                messages.error(
                    request,
                    f"Another group with name '{new_name}' already exists."
                )
            else:
                try:
                    grp = InvGroupMaster.objects.get(sno=update_id, active='Y')
                    grp.gname = new_name
                    grp.updatedby = request.user.username
                    grp.updatedtime = timezone.now()
                    grp.save()
                    messages.success(request, "Group updated successfully.")
                except InvGroupMaster.DoesNotExist:
                    messages.error(request, "Group not found for update.")

            return redirect(
                request.path + f"?operation=modify&search={search_term}"
            )

        # ---------- DELETE ----------
        if operation == "delete" and request.POST.get("delete_id"):
            delete_id = request.POST.get("delete_id")
            try:
                grp = InvGroupMaster.objects.get(sno=delete_id, active='Y')
                grp.active = 'N'
                grp.updatedby = request.user.username
                grp.updatedtime = timezone.now()
                grp.save()
                messages.success(
                    request,
                    f"Group '{grp.gname}' deleted (soft delete)."
                )
            except InvGroupMaster.DoesNotExist:
                messages.error(request, "Group not found for deletion.")

            return redirect(
                request.path + f"?operation=delete&search={search_term}"
            )

        return redirect(request.path + f"?operation={operation}")

    # ============================
    # GET HANDLING (ONLY RENDER)
    # ============================
    operation = request.GET.get("operation", "add")
    search_term = (request.GET.get("search") or "").strip()

    if search_term:
        records = InvGroupMaster.objects.filter(
            gname__icontains=search_term,
            active='Y'
        ).order_by('gname')
    else:
        records = InvGroupMaster.objects.filter(
            active='Y'
        ).order_by('gname')

    return render(request, "hospApp/Admin/InvGroupMaster.html", {
        "operation": operation,
        "search_term": search_term,
        "records": records,
    })
