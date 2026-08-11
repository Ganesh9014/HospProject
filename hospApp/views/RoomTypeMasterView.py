from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from hospApp.models import RoomTypeMaster as MainRoomTypeMaster
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def RoomTypeMasterView(request):

    operation = None
    roomtypes = None
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
            roomtype = (request.POST.get('roomtype') or '').strip()
            roomrent = request.POST.get('roomrent')

            if not roomtype:
                messages.error(request, "Please enter Room Type.")
                return redirect(request.path + "?operation=add")

            if MainRoomTypeMaster.objects.filter(
                roomtype__iexact=roomtype,
                active='Y'
            ).exists():
                messages.error(
                    request,
                    f"Room type '{roomtype}' already exists."
                )
                return redirect(request.path + "?operation=add")

            try:
                roomrent_val = float(roomrent) if roomrent else 0
            except (ValueError, TypeError):
                messages.error(request, "Room rent must be a number.")
                return redirect(request.path + "?operation=add")

            MainRoomTypeMaster.objects.create(
                roomtype=roomtype,
                roomrent=roomrent_val,
                active='Y',
            )

            messages.success(
                request,
                f"Room type '{roomtype}' added successfully."
            )
            return redirect(request.path + "?operation=add")

        # -------------------------
        # ADD MODE
        # -------------------------
        if operation == 'add':

            roomtype = (request.POST.get('roomtype') or '').strip()
            roomrent = request.POST.get('roomrent')

            if not roomtype:
                messages.error(request, "Please enter Room Type.")
                return redirect(request.path + "?operation=add")

            if MainRoomTypeMaster.objects.filter(
                roomtype__iexact=roomtype,
                active='Y'
            ).exists():
                messages.error(
                    request,
                    f"Room type '{roomtype}' already exists."
                )
                return redirect(request.path + "?operation=add")

            try:
                roomrent_val = float(roomrent) if roomrent else 0
            except (ValueError, TypeError):
                messages.error(request, "Room rent must be a number.")
                return redirect(request.path + "?operation=add")

            MainRoomTypeMaster.objects.create(
                roomtype=roomtype,
                roomrent=roomrent_val,
                active='Y',
            )

            messages.success(
                request,
                f"Room type '{roomtype}' added successfully."
            )
            return redirect(request.path + "?operation=add")

        # -------------------------
        # MODIFY MODE
        # -------------------------
        if operation == 'modify' and update_id:

            try:
                room = MainRoomTypeMaster.objects.get(pk=update_id)
                new_rent = request.POST.get(f'roomrent_{update_id}')

                if not new_rent:
                    messages.error(request, "Room rent is required.")
                    return redirect(request.path + "?operation=modify")

                try:
                    room.roomrent = float(new_rent)
                except (ValueError, TypeError):
                    messages.error(request, "Room rent must be numeric.")
                    return redirect(request.path + "?operation=modify")

                room.save()
                messages.success(
                    request,
                    f"Room Type '{room.roomtype}' updated successfully."
                )

            except MainRoomTypeMaster.DoesNotExist:
                messages.error(request, "Room type not found.")

            return redirect(request.path + "?operation=modify")

        # -------------------------
        # DELETE MODE
        # -------------------------
        if operation == 'delete' and update_id:

            try:
                room = MainRoomTypeMaster.objects.get(pk=update_id)
                room.active = 'N'
                room.save()

                messages.success(
                    request,
                    f"Room type '{room.roomtype}' deleted successfully."
                )

            except MainRoomTypeMaster.DoesNotExist:
                messages.error(request, "Room type not found.")

            return redirect(request.path + "?operation=delete")

    # =========================
    # GET HANDLING
    # =========================
    operation = request.GET.get('operation', 'add')
    search_term = (request.GET.get('search') or '').strip()

    if operation == 'modify':
        if search_term:
            roomtypes = MainRoomTypeMaster.objects.filter(
                roomtype__icontains=search_term,
                active='Y'
            ).order_by('roomtypeid')
            searched = True
        else:
            roomtypes = MainRoomTypeMaster.objects.filter(
                active='Y'
            ).order_by('roomtypeid')

    elif operation == 'delete':
        if search_term:
            roomtypes = MainRoomTypeMaster.objects.filter(
                roomtype__icontains=search_term,
                active='Y'
            ).order_by('roomtypeid')
            searched = True
        else:
            roomtypes = MainRoomTypeMaster.objects.filter(
                active='Y'
            ).order_by('roomtypeid')

    else:  # add
        roomtypes = MainRoomTypeMaster.objects.filter(
            active='Y'
        ).order_by('roomtypeid')

    return render(request, 'hospApp/Admin/RoomTypeMaster.html', {
        'roomtypes': roomtypes,
        'operation': operation,
        'search_term': search_term,
        'searched': searched,
    })
