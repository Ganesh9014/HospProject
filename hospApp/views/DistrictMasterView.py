from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from hospApp.models import DistrictMaster, StateMaster
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def DistrictMasterView(request):

    # ============================
    # POST HANDLING (NO RENDER)
    # ============================
    if request.method == 'POST':

        operation = request.POST.get('operation', 'add')
        search_term = (request.POST.get('search_term') or '').strip()

        # ---------- ADD ----------
        if 'add_btn' in request.POST and operation == 'add':
            state_id = request.POST.get('state_name')
            district_name = (request.POST.get('district_name') or '').strip()

            if not state_id or not district_name:
                messages.error(request, "Please select a State and enter a District Name.")
            else:
                try:
                    state = StateMaster.objects.get(pk=state_id)
                    if DistrictMaster.objects.filter(
                        district_name__iexact=district_name,
                        state_name=state
                    ).exists():
                        messages.error(
                            request,
                            f"District '{district_name}' already exists for state '{state.statename}'."
                        )
                    else:
                        DistrictMaster.objects.create(
                            state_name=state,
                            district_name=district_name,
                            active='Y',
                            createdby=request.user.username if request.user.is_authenticated else 'System',
                            createdtime=timezone.now()
                        )
                        messages.success(
                            request,
                            f"District '{district_name}' added successfully."
                        )
                except StateMaster.DoesNotExist:
                    messages.error(request, "Invalid State selected.")

            return redirect(request.path + "?operation=add")

        # ---------- MODIFY ----------
        if 'update_btn' in request.POST and operation == 'modify':
            update_id = request.POST.get('update_btn')
            district_name = (request.POST.get(f'district_name_{update_id}') or '').strip()
            state_id = request.POST.get(f'state_name_{update_id}')

            try:
                district = DistrictMaster.objects.get(pk=update_id)
                state = StateMaster.objects.get(pk=state_id)

                if DistrictMaster.objects.filter(
                    district_name__iexact=district_name,
                    state_name=state
                ).exclude(pk=update_id).exists():
                    messages.error(
                        request,
                        f"District '{district_name}' already exists for state '{state.statename}'."
                    )
                else:
                    district.district_name = district_name
                    district.state_name = state
                    district.updatedby = request.user.username if request.user.is_authenticated else 'System'
                    district.updatetime = timezone.now()
                    district.save()
                    messages.success(request, "District updated successfully.")

            except (DistrictMaster.DoesNotExist, StateMaster.DoesNotExist):
                messages.error(request, "Record not found.")

            qs = "?operation=modify"
            if search_term:
                qs += f"&search_term={search_term}"
            return redirect(request.path + qs)

        # ---------- DELETE ----------
        if 'delete_btn' in request.POST and operation == 'delete':
            delete_id = request.POST.get('delete_btn')

            try:
                district = DistrictMaster.objects.get(pk=delete_id)
                district.delete()
                messages.success(
                    request,
                    f"District '{district.district_name}' deleted successfully."
                )
            except DistrictMaster.DoesNotExist:
                messages.error(request, "District not found.")

            return redirect(request.path + "?operation=delete")

        # ---------- SEARCH (POST fallback) ----------
        if 'search_btn' in request.POST:
            qs = f"?operation={operation}"
            if search_term:
                qs += f"&search_term={search_term}"
            return redirect(request.path + qs)

    # ============================
    # GET HANDLING (ONLY RENDER)
    # ============================
    operation = request.GET.get('operation', 'add')
    search_term = (request.GET.get('search_term') or '').strip()

    states = StateMaster.objects.all().order_by('statename')

    districts = DistrictMaster.objects.all().select_related(
        'state_name'
    ).order_by('state_name__statename', 'district_name')

    searched = False
    if search_term:
        districts = districts.filter(
            Q(district_name__icontains=search_term) |
            Q(state_name__statename__icontains=search_term)
        )
        searched = True

    return render(request, 'hospApp/Admin/DistrictMaster.html', {
        'operation': operation,
        'states': states,
        'districts': districts,
        'search_term': search_term,
        'searched': searched,
    })
