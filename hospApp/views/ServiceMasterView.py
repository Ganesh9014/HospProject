from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from hospApp.models import ServiceMaster, RoomTypeMaster
from django.contrib.auth.decorators import login_required   


@login_required(login_url='login')
def ServiceMasterView(request):

    # ============================
    # POST HANDLING (NO RENDER)
    # ============================
    if request.method == 'POST':

        operation = request.POST.get('operation', 'add')
        selected_roomtype = request.POST.get('roomtypeid')

        # ---------- ADD ----------
        if 'add_btn' in request.POST:
            roomtypeid = request.POST.get('roomtypeid')
            servicename = (request.POST.get('servicename') or '').strip()
            cost_raw = (request.POST.get('charge') or '').strip()

            if not roomtypeid:
                messages.error(request, "Please select Room Type.")
            elif not servicename:
                messages.error(request, "Please enter Service Name.")
            else:
                try:
                    cost = Decimal(cost_raw) if cost_raw != '' else Decimal('0.00')
                    if cost < 0:
                        raise InvalidOperation
                except (InvalidOperation, ValueError):
                    messages.error(request, "Please enter a valid non-negative Cost.")
                else:
                    if ServiceMaster.objects.filter(
                        servicename__iexact=servicename,
                        roomtype_id=roomtypeid,
                        active='Y'
                    ).exists():
                        messages.error(
                            request,
                            f"Service '{servicename}' already exists for this Room Type."
                        )
                    else:
                        ServiceMaster.objects.create(
                            servicename=servicename,
                            charge=cost,
                            roomtype_id=roomtypeid,
                            active='Y'
                        )
                        messages.success(
                            request,
                            f"Service '{servicename}' added successfully."
                        )

            qs = "?operation=add"
            if roomtypeid:
                qs += f"&roomtypeid={roomtypeid}"
            return redirect(request.path + qs)

        # ---------- MODIFY ----------
        if 'update_btn' in request.POST:
            update_id = request.POST.get('update_btn')

            try:
                service = ServiceMaster.objects.get(pk=update_id, active='Y')
                new_cost_raw = (request.POST.get(f'charge_{update_id}') or '').strip()

                try:
                    new_cost = Decimal(new_cost_raw) if new_cost_raw != '' else Decimal('0.00')
                    if new_cost < 0:
                        raise InvalidOperation
                except (InvalidOperation, ValueError):
                    messages.error(request, "Please enter a valid non-negative Cost.")
                else:
                    service.charge = new_cost
                    service.updateddate = timezone.now()
                    service.save()
                    messages.success(
                        request,
                        f"Cost for service '{service.servicename}' updated successfully."
                    )

            except ServiceMaster.DoesNotExist:
                messages.error(request, "Service not found.")

            qs = "?operation=modify"
            if selected_roomtype:
                qs += f"&roomtypeid={selected_roomtype}"
            return redirect(request.path + qs)

        # ---------- DELETE ----------
        if 'delete_btn' in request.POST:
            delete_id = request.POST.get('delete_btn')

            try:
                service = ServiceMaster.objects.get(pk=delete_id, active='Y')
                service.active = 'N'
                service.updateddate = timezone.now()
                service.save()
                messages.success(
                    request,
                    f"Service '{service.servicename}' marked as inactive (deleted)."
                )
            except ServiceMaster.DoesNotExist:
                messages.error(request, "Service not found.")

            qs = "?operation=delete"
            if selected_roomtype:
                qs += f"&roomtypeid={selected_roomtype}"
            return redirect(request.path + qs)

    # ============================
    # GET HANDLING (ONLY RENDER)
    # ============================
    operation = request.GET.get('operation', 'add')
    selected_roomtype = request.GET.get('roomtypeid')

    roomtypes = RoomTypeMaster.objects.filter(active='Y').order_by('roomtypeid')

    servicelist = ServiceMaster.objects.select_related(
        'roomtype'
    ).filter(active='Y').order_by('serviceid')

    if selected_roomtype:
        servicelist = servicelist.filter(roomtype_id=selected_roomtype)

    return render(request, 'hospApp/Admin/ServiceMaster.html', {
        'operation': operation,
        'roomtypes': roomtypes,
        'servicelist': servicelist,
        'selected_roomtype': selected_roomtype or '',
    })
