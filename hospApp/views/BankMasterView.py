from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from hospApp.models import BankMaster


@login_required(login_url='login')
def BankMasterView(request):
    """
    Payee / Bank Master
    - Add / Modify / Delete
    - Soft delete
    - Case-insensitive duplicate prevention
    - PRG compliant (NO POST RENDER)
    """

    # =========================
    # POST HANDLING (NO RENDER)
    # =========================
    if request.method == 'POST':

        operation = request.POST.get('operation') or 'add'
        update_id = request.POST.get('update_id')
        search_term = (request.POST.get('search_term') or '').strip()

        # ---------- ADD ----------
        if operation == 'add' and not update_id:
            bank_name = (request.POST.get('name') or '').strip()

            if not bank_name:
                messages.error(request, "Please enter Payee Name.")
            elif BankMaster.objects.filter(
                name__iexact=bank_name, active='Y'
            ).exists():
                messages.error(request, f"Payee '{bank_name}' already exists.")
            else:
                BankMaster.objects.create(
                    name=bank_name,
                    active='Y',
                    createdby=request.user.username,
                    createddate=timezone.now()
                )
                messages.success(request, f"Payee '{bank_name}' added successfully.")

            return redirect(request.path + "?operation=add")

        # ---------- MODIFY ----------
        if operation == 'modify' and update_id:
            bank_name = (request.POST.get(f'name_{update_id}') or '').strip()

            if not bank_name:
                messages.error(request, "Please enter Payee Name.")
            elif BankMaster.objects.filter(
                name__iexact=bank_name,
                active='Y'
            ).exclude(pk=update_id).exists():
                messages.error(request, f"Payee '{bank_name}' already exists.")
            else:
                try:
                    bank = BankMaster.objects.get(pk=update_id, active='Y')
                    bank.name = bank_name
                    bank.updatedby = request.user.username
                    bank.updateddate = timezone.now()
                    bank.save()
                    messages.success(
                        request,
                        f"Payee '{bank_name}' updated successfully."
                    )
                except BankMaster.DoesNotExist:
                    messages.error(request, "Payee not found.")

            return redirect(
                request.path + f"?operation=modify&search={search_term}"
            )

        # ---------- DELETE ----------
        if operation == 'delete' and update_id:
            try:
                bank = BankMaster.objects.get(pk=update_id, active='Y')
                bank.active = 'N'
                bank.updatedby = request.user.username
                bank.updateddate = timezone.now()
                bank.save()
                messages.success(
                    request,
                    f"Payee '{bank.name}' deleted successfully."
                )
            except BankMaster.DoesNotExist:
                messages.error(request, "Payee not found.")

            return redirect(
                request.path + f"?operation=delete&search={search_term}"
            )

        return redirect(request.path)

    # =========================
    # GET HANDLING (ONLY RENDER)
    # =========================
    operation = request.GET.get('operation', 'add')
    search_term = (request.GET.get('search') or '').strip()

    if operation in ['modify', 'delete'] and search_term:
        banks = BankMaster.objects.filter(
            name__icontains=search_term,
            active='Y'
        ).order_by('name')
        searched = True
    else:
        banks = BankMaster.objects.filter(
            active='Y'
        ).order_by('name')
        searched = False

    return render(request, 'hospApp/Admin/BankMaster.html', {
        'banks': banks,
        'operation': operation,
        'search_term': search_term,
        'searched': searched,
    })
