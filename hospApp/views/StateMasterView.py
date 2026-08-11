from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from hospApp.models import StateMaster
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def StateMasterView(request):

    # ============================
    # POST HANDLING (NO RENDER)
    # ============================
    if request.method == 'POST':

        operation = request.POST.get('operation', 'add')
        search_term = (request.POST.get('search_term') or '').strip()

        # ---------- ADD ----------
        if 'add_btn' in request.POST and operation == 'add':
            statename = (request.POST.get('statename') or '').strip()

            if not statename:
                messages.error(request, "Please enter State Name.")
            elif StateMaster.objects.filter(statename__iexact=statename).exists():
                messages.error(request, f"State '{statename}' already exists.")
            else:
                StateMaster.objects.create(statename=statename)
                messages.success(request, f"State '{statename}' added successfully.")

            return redirect(request.path + "?operation=add")

        # ---------- MODIFY ----------
        if 'update_btn' in request.POST and operation == 'modify':
            update_id = request.POST.get('update_btn')
            statename = (request.POST.get(f'statename_{update_id}') or '').strip()

            try:
                state = StateMaster.objects.get(pk=update_id)
                if not statename:
                    messages.error(request, "Please enter State Name.")
                elif StateMaster.objects.filter(
                    statename__iexact=statename
                ).exclude(pk=update_id).exists():
                    messages.error(request, f"State '{statename}' already exists.")
                else:
                    state.statename = statename
                    state.save()
                    messages.success(request, f"State '{statename}' updated successfully.")
            except StateMaster.DoesNotExist:
                messages.error(request, "State not found.")

            qs = "?operation=modify"
            if search_term:
                qs += f"&search_term={search_term}"
            return redirect(request.path + qs)

        # ---------- DELETE ----------
        if 'delete_btn' in request.POST and operation == 'delete':
            delete_id = request.POST.get('delete_btn')

            try:
                state = StateMaster.objects.get(pk=delete_id)
                state.delete()
                messages.success(request, f"State '{state.statename}' deleted successfully.")
            except StateMaster.DoesNotExist:
                messages.error(request, "State not found.")

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

    states = StateMaster.objects.all().order_by('sno')
    searched = False

    if search_term:
        states = states.filter(Q(statename__icontains=search_term))
        searched = True

    return render(request, 'hospApp/Admin/StateMaster.html', {
        'operation': operation,
        'states': states,
        'searched': searched,
        'search_term': search_term,
    })
