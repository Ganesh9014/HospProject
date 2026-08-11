from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from hospApp.models import ServiceTypeMaster
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def ServiceTypeMasterView(request):

    # ============================
    # POST HANDLING (NO RENDER)
    # ============================
    if request.method == 'POST':

        operation = request.POST.get('operation', 'add')

        # ---------- ADD ----------
        if 'add_btn' in request.POST and operation == 'add':
            servicename = (request.POST.get('servicename') or '').strip()
            charge_raw = (request.POST.get('charge') or '').strip()

            if not servicename:
                messages.error(request, "Please enter Service Name.")
            else:
                try:
                    charge = Decimal(charge_raw) if charge_raw != '' else Decimal('0.00')
                    if charge < 0:
                        raise InvalidOperation
                except (InvalidOperation, ValueError):
                    messages.error(request, "Please enter a valid non-negative charge.")
                else:
                    if ServiceTypeMaster.objects.filter(
                        servicename__iexact=servicename, active='Y'
                    ).exists():
                        messages.error(request, f"Service '{servicename}' already exists.")
                    else:
                        ServiceTypeMaster.objects.create(
                            servicename=servicename,
                            charge=charge,
                            active='Y'
                        )
                        messages.success(
                            request,
                            f"Service '{servicename}' added successfully."
                        )

            return redirect(request.path + "?operation=add")

        # ---------- UPDATE ----------
        if 'update_btn' in request.POST and operation == 'modify':
            update_id = request.POST.get('update_btn')

            try:
                service = ServiceTypeMaster.objects.get(pk=update_id, active='Y')
                new_name = (request.POST.get(f'servicename_{update_id}') or '').strip()
                new_charge_raw = (request.POST.get(f'charge_{update_id}') or '').strip()

                try:
                    new_charge = Decimal(new_charge_raw) if new_charge_raw != '' else Decimal('0.00')
                    if new_charge < 0:
                        raise InvalidOperation
                except (InvalidOperation, ValueError):
                    messages.error(request, "Please enter a valid non-negative charge.")
                else:
                    if not new_name:
                        messages.error(request, "Service Name cannot be empty.")
                    else:
                        service.servicename = new_name
                        service.charge = new_charge
                        service.updatedtime = timezone.now()
                        service.save()
                        messages.success(
                            request,
                            f"Service '{new_name}' updated successfully."
                        )

            except ServiceTypeMaster.DoesNotExist:
                messages.error(request, "Service not found.")

            return redirect(request.path + "?operation=modify")

        # ---------- DELETE ----------
        if 'delete_btn' in request.POST and operation == 'delete':
            delete_id = request.POST.get('delete_btn')

            try:
                service = ServiceTypeMaster.objects.get(pk=delete_id, active='Y')
                service.active = 'N'
                service.updatedtime = timezone.now()
                service.save()
                messages.success(
                    request,
                    f"Service '{service.servicename}' deleted successfully."
                )
            except ServiceTypeMaster.DoesNotExist:
                messages.error(request, "Service not found.")

            return redirect(request.path + "?operation=delete")

        # ---------- SEARCH (POST fallback) ----------
        search_name = (request.POST.get('servicename') or '').strip()
        qs = f"?operation={operation}"
        if search_name:
            qs += f"&servicename={search_name}"

        return redirect(request.path + qs)

    # ============================
    # GET HANDLING (ONLY RENDER)
    # ============================
    operation = request.GET.get('operation', 'add')
    search_name = (request.GET.get('servicename') or '').strip()

    servicelist = ServiceTypeMaster.objects.filter(active='Y').order_by('serviceid')

    if search_name:
        servicelist = servicelist.filter(servicename__icontains=search_name)

    return render(request, 'hospApp/Admin/ServiceTypeMaster.html', {
        'operation': operation,
        'servicelist': servicelist,
    })
