from django.shortcuts import render, redirect
from django.contrib import messages
from hospApp.models import MainFloorMaster
from django.utils import timezone
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def FloorMasterView(request):

    operation = None
    floors = None
    search_term = ''
    searched = False

    # =========================
    # POST HANDLING
    # =========================
    if request.method == 'POST':

        operation = request.POST.get('operation')
        update_id = request.POST.get('update_id')
        search_term = (request.POST.get('search_term') or '').strip()

        # -------------------------
        # DEFAULT ADD (NO RADIO)
        # -------------------------
        if not operation and not update_id:

            floorno = (request.POST.get('floorno') or '').strip()

            if not floorno:
                messages.error(request, "Please enter a Floor Number.")
                return redirect(request.path + "?operation=add")

            if MainFloorMaster.objects.filter(
                floorno__iexact=floorno, active='Y'
            ).exists():
                messages.error(
                    request,
                    f"A floor with number '{floorno}' already exists."
                )
                return redirect(request.path + "?operation=add")

            MainFloorMaster.objects.create(
                floorno=floorno,
                remarks=(request.POST.get('remarks') or '').strip(),
                orderno=request.POST.get('orderno') or None,
                active='Y',
                userid='admin',
                createddate=timezone.now(),
                updateddate=timezone.now()
            )

            messages.success(request, f"Floor '{floorno}' added successfully.")
            return redirect(request.path + "?operation=add")

        # -------------------------
        # ADD MODE
        # -------------------------
        if operation == 'add':

            floorno = (request.POST.get('floorno') or '').strip()

            if not floorno:
                messages.error(request, "Please enter a Floor Number.")
                return redirect(request.path + "?operation=add")

            if MainFloorMaster.objects.filter(
                floorno__iexact=floorno, active='Y'
            ).exists():
                messages.error(
                    request,
                    f"A floor with number '{floorno}' already exists."
                )
                return redirect(request.path + "?operation=add")

            MainFloorMaster.objects.create(
                floorno=floorno,
                remarks=(request.POST.get('remarks') or '').strip(),
                orderno=request.POST.get('orderno') or None,
                active='Y',
                userid='admin',
                createddate=timezone.now(),
                updateddate=timezone.now()
            )

            messages.success(request, f"Floor '{floorno}' added successfully.")
            return redirect(request.path + "?operation=add")

        # -------------------------
        # MODIFY MODE
        # -------------------------
        if operation == 'modify' and update_id:

            floorno = (request.POST.get(f'floorno_{update_id}') or '').strip()
            remarks = (request.POST.get(f'remarks_{update_id}') or '').strip()
            orderno = request.POST.get(f'orderno_{update_id}')

            if not floorno:
                messages.error(request, "Please enter Floor Number to update.")
                return redirect(request.path + "?operation=modify")

            try:
                fl = MainFloorMaster.objects.get(pk=update_id)

                duplicate = MainFloorMaster.objects.filter(
                    floorno__iexact=floorno,
                    active='Y'
                ).exclude(pk=update_id).exists()

                if duplicate:
                    messages.error(
                        request,
                        f"Floor '{floorno}' already exists."
                    )
                    return redirect(request.path + "?operation=modify")

                fl.floorno = floorno
                fl.remarks = remarks
                fl.orderno = orderno or None
                fl.updateddate = timezone.now()
                fl.save()

                messages.success(
                    request,
                    f"Floor '{floorno}' updated successfully."
                )

            except MainFloorMaster.DoesNotExist:
                messages.error(request, "Floor not found.")

            return redirect(request.path + "?operation=modify")

        # -------------------------
        # DELETE MODE
        # -------------------------
        if operation == 'delete' and update_id:

            try:
                fl = MainFloorMaster.objects.get(pk=update_id)
                fl.active = 'N'
                fl.updateddate = timezone.now()
                fl.save()

                messages.success(
                    request,
                    f"Floor '{fl.floorno}' deleted successfully."
                )

            except MainFloorMaster.DoesNotExist:
                messages.error(request, "Floor not found.")

            return redirect(request.path + "?operation=delete")

    # =========================
    # GET HANDLING
    # =========================
    operation = request.GET.get('operation', 'add')
    search_term = (request.GET.get('search') or '').strip()

    if operation == 'modify':
        if search_term:
            floors = MainFloorMaster.objects.filter(
                floorno__icontains=search_term,
                active='Y'
            ).order_by('floorid')
            searched = True
        else:
            floors = MainFloorMaster.objects.filter(
                active='Y'
            ).order_by('floorid')

    elif operation == 'delete':
        if search_term:
            floors = MainFloorMaster.objects.filter(
                floorno__icontains=search_term,
                active='Y'
            ).order_by('floorid')
            searched = True
        else:
            floors = MainFloorMaster.objects.filter(
                active='Y'
            ).order_by('floorid')

    else:  # add
        floors = MainFloorMaster.objects.filter(
            active='Y'
        ).order_by('floorid')

    return render(request, 'hospApp/Admin/FloorMaster.html', {
        'floors': floors,
        'operation': operation,
        'search_term': search_term,
        'searched': searched,
    })
