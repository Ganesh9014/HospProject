from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from hospApp.models import BedMaster, MainFloorMaster, RoomMaster
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def BedMasterView(request):

    # -----------------------------
    # POST HANDLING (NO RENDER HERE)
    # -----------------------------
    if request.method == 'POST':

        operation = request.POST.get('operation', 'add')
        floorid = request.POST.get('floorid') or ''
        roomid = request.POST.get('roomid') or ''
        bedno = (request.POST.get('bedno') or '').strip()

        # ---------- ADD ----------
        if 'add_btn' in request.POST:

            chargeable = 'Y' if request.POST.get('chargeable') else 'N'
            bedcharges = request.POST.get('bedcharges') or None
            remarks = (request.POST.get('remarks') or '').strip()

            if not floorid:
                messages.error(request, "Please select Floor.")
            elif not roomid:
                messages.error(request, "Please select Room.")
            elif not bedno:
                messages.error(request, "Please enter Bed Number.")
            elif BedMaster.objects.filter(
                bedno__iexact=bedno,
                floor_id=floorid,
                room_id=roomid,
                active='Y'
            ).exists():
                messages.error(
                    request,
                    f"Bed '{bedno}' already exists for this Floor and Room."
                )
            else:
                # default charges if not chargeable
                if chargeable != 'Y':
                    try:
                        room = RoomMaster.objects.get(pk=roomid, active='Y')
                        bedcharges = room.roomtypeid.roomrent if room.roomtypeid else 0
                    except Exception:
                        bedcharges = 0
                else:
                    try:
                        bedcharges = int(bedcharges) if bedcharges else None
                    except Exception:
                        bedcharges = None

                BedMaster.objects.create(
                    bedno=bedno,
                    floor_id=floorid,
                    room_id=roomid,
                    chargeble=chargeable,
                    bedcharges=bedcharges,
                    active='Y',
                    remarks=remarks,
                )

                messages.success(request, f"Bed '{bedno}' added successfully.")

            return redirect(
                f"{request.path}?operation=add&floorid={floorid}&roomid={roomid}"
            )

        # ---------- DELETE ----------
        if 'delete_btn' in request.POST:
            delete_id = request.POST.get('delete_btn')

            try:
                bed = BedMaster.objects.get(pk=delete_id, active='Y')
                bed.active = 'N'
                bed.save()
                messages.success(
                    request,
                    f"Bed '{bed.bedno}' marked as inactive (deleted)."
                )
            except BedMaster.DoesNotExist:
                messages.error(request, "Bed not found.")

            return redirect(request.path + "?operation=delete")

        # ---------- SEARCH ----------
        if 'search_btn' in request.POST:
            qs = f"?operation={operation}"
            if floorid:
                qs += f"&floorid={floorid}"
            if roomid:
                qs += f"&roomid={roomid}"
            if bedno:
                qs += f"&search={bedno}"
            return redirect(request.path + qs)

    # -----------------------------
    # GET HANDLING (ONLY RENDER)
    # -----------------------------
    operation = request.GET.get('operation', 'add')
    search_term = (request.GET.get('search') or '').strip()
    floorid = request.GET.get('floorid') or ''
    roomid = request.GET.get('roomid') or ''

    floors = MainFloorMaster.objects.filter(active='Y').order_by('orderno', 'floorno')
    rooms = RoomMaster.objects.filter(active='Y').order_by('roomid')

    beds_qs = None
    searched = False

    if operation in ['add', 'delete']:
        beds_qs = BedMaster.objects.select_related(
            'room', 'floor'
        ).filter(active='Y')

        if floorid:
            beds_qs = beds_qs.filter(floor_id=floorid)
        if roomid:
            beds_qs = beds_qs.filter(room_id=roomid)
        if search_term:
            beds_qs = beds_qs.filter(bedno__icontains=search_term)

        beds_qs = beds_qs.order_by('bedid')
        searched = True

    return render(request, 'hospApp/Admin/BedMaster.html', {
        'floors': floors,
        'rooms': rooms,
        'beds': beds_qs,
        'operation': operation,
        'searched': searched,
        'search_term': search_term,
        'selected_floorid': floorid,
        'selected_roomid': roomid,
    })

@login_required(login_url='login')
def rooms_by_floor(request):
    floorid = request.GET.get('floorid')
    if floorid:
        qs = RoomMaster.objects.filter(
            floorid_id=floorid, active='Y'
        ).values('roomid', 'roomno').order_by('roomno')
    else:
        qs = RoomMaster.objects.filter(
            active='Y'
        ).values('roomid', 'roomno').order_by('roomno')
    return JsonResponse(list(qs), safe=False)
