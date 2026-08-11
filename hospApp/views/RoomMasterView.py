from django.shortcuts import render, redirect
from django.contrib import messages
from hospApp.models import RoomMaster, MainFloorMaster, RoomTypeMaster
from django.utils import timezone
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def RoomMasterView(request):

    # ============================
    # POST HANDLING (NO RENDER)
    # ============================
    if request.method == 'POST':

        operation = request.POST.get('operation', 'add')

        # ---------- ADD ----------
        if 'add_btn' in request.POST:
            roomno = (request.POST.get('roomno') or '').strip()
            floorid = request.POST.get('floorid')
            roomtypeid = request.POST.get('roomtypeid')
            orderno = request.POST.get('orderno')
            remarks = (request.POST.get('remarks') or '').strip()

            if not roomno:
                messages.error(request, "Room Number is required.")
            elif not floorid or not roomtypeid:
                messages.error(request, "Please select both Floor and Room Type.")
            elif RoomMaster.objects.filter(
                roomno__iexact=roomno,
                floorid_id=floorid,
                roomtypeid_id=roomtypeid,
                active='Y'
            ).exists():
                messages.error(
                    request,
                    f"Room number '{roomno}' already exists for this Floor and Room Type."
                )
            else:
                RoomMaster.objects.create(
                    roomno=roomno,
                    floorid_id=floorid,
                    roomtypeid_id=roomtypeid,
                    remarks=remarks,
                    orderno=orderno or None,
                    active='Y',
                )
                messages.success(request, f"Room '{roomno}' added successfully.")

            return redirect(request.path + "?operation=add")

        # ---------- MODIFY ----------
        if 'update_btn' in request.POST:
            update_id = request.POST.get('update_btn')

            try:
                room = RoomMaster.objects.get(pk=update_id, active='Y')
                new_roomno = (request.POST.get(f'roomno_{update_id}') or '').strip()
                new_remarks = (request.POST.get(f'remarks_{update_id}') or '').strip()
                new_orderno = request.POST.get(f'orderno_{update_id}') or None

                if not new_roomno:
                    messages.error(request, "Room Number is required.")
                elif RoomMaster.objects.filter(
                    roomno__iexact=new_roomno,
                    floorid_id=room.floorid_id,
                    roomtypeid_id=room.roomtypeid_id,
                    active='Y'
                ).exclude(pk=update_id).exists():
                    messages.error(
                        request,
                        f"Room number '{new_roomno}' already exists for this Floor and Room Type."
                    )
                else:
                    room.roomno = new_roomno
                    room.remarks = new_remarks
                    room.orderno = new_orderno
                    room.updateddate = timezone.now()
                    room.save()
                    messages.success(
                        request,
                        f"Room '{room.roomno}' updated successfully."
                    )

            except RoomMaster.DoesNotExist:
                messages.error(request, "Room not found.")

            return redirect(request.path + "?operation=modify")

        # ---------- DELETE ----------
        if 'delete_btn' in request.POST:
            delete_id = request.POST.get('delete_btn')

            try:
                room = RoomMaster.objects.get(pk=delete_id, active='Y')
                room.active = 'N'
                room.updateddate = timezone.now()
                room.save()
                messages.success(
                    request,
                    f"Room '{room.roomno}' marked as inactive (deleted)."
                )
            except RoomMaster.DoesNotExist:
                messages.error(request, "Room not found.")

            return redirect(request.path + "?operation=delete")

        # ---------- SEARCH ----------
        if 'search_btn' in request.POST:
            search_term = (request.POST.get('search_term') or '').strip()
            qs = f"?operation={operation}"
            if search_term:
                qs += f"&search_term={search_term}"
            return redirect(request.path + qs)

    # ============================
    # GET HANDLING (ONLY RENDER)
    # ============================
    operation = request.GET.get('operation', 'add')
    search_term = (request.GET.get('search_term') or '').strip()

    floors = MainFloorMaster.objects.filter(active='Y')
    roomtypes = RoomTypeMaster.objects.filter(active='Y')

    roomdata = RoomMaster.objects.select_related(
        'floorid', 'roomtypeid'
    ).filter(active='Y')

    searched = False
    if operation in ['modify', 'delete'] and search_term:
        roomdata = roomdata.filter(roomno__icontains=search_term)
        searched = True

    roomdata = roomdata.order_by('roomid')

    return render(request, 'hospApp/Admin/RoomMaster.html', {
        'floors': floors,
        'roomtypes': roomtypes,
        'roomdata': roomdata,
        'operation': operation,
        'searched': searched,
        'search_term': search_term,
    })
