from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from hospApp.models import SpecialityMaster
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def SpecialityMasterView(request):

    # ============================
    # POST HANDLING (NO RENDER)
    # ============================
    if request.method == 'POST':

        operation = request.POST.get('operation', 'add')

        # ---------- ADD ----------
        if 'add_btn' in request.POST and operation == 'add':
            speciality = (request.POST.get('speciality') or '').strip()

            if not speciality:
                messages.error(request, "Please enter a speciality name.")
            elif SpecialityMaster.objects.filter(
                speciality__iexact=speciality, active='Y'
            ).exists():
                messages.error(request, f"'{speciality}' already exists.")
            else:
                SpecialityMaster.objects.create(
                    speciality=speciality,
                    userid=request.user.username if request.user.is_authenticated else 'system',
                    insertedtime=timezone.now(),
                    active='Y'
                )
                messages.success(request, f"'{speciality}' added successfully.")

            return redirect(request.path + "?operation=add")

        # ---------- UPDATE ----------
        if 'update_btn' in request.POST and operation == 'modify':
            update_id = request.POST.get('update_btn')
            try:
                spec = SpecialityMaster.objects.get(pk=update_id, active='Y')
                new_speciality = (request.POST.get(f'speciality_{update_id}') or '').strip()

                if not new_speciality:
                    messages.error(request, "Speciality name cannot be blank.")
                else:
                    spec.speciality = new_speciality
                    spec.updatedby = request.user.username if request.user.is_authenticated else 'system'
                    spec.updatedtime = timezone.now()
                    spec.save()
                    messages.success(request, f"'{new_speciality}' updated successfully.")

            except SpecialityMaster.DoesNotExist:
                messages.error(request, "Record not found.")

            return redirect(request.path + "?operation=modify")

        # ---------- DELETE ----------
        if 'delete_btn' in request.POST and operation == 'delete':
            delete_id = request.POST.get('delete_btn')
            try:
                spec = SpecialityMaster.objects.get(pk=delete_id, active='Y')
                spec.active = 'N'
                spec.updatedby = request.user.username if request.user.is_authenticated else 'system'
                spec.updatedtime = timezone.now()
                spec.save()
                messages.success(request, f"'{spec.speciality}' deleted successfully.")
            except SpecialityMaster.DoesNotExist:
                messages.error(request, "Record not found.")

            return redirect(request.path + "?operation=delete")

        # ---------- SEARCH (POST fallback) ----------
        search_text = (
            request.POST.get('search_text')
            or request.POST.get('speciality')
            or ''
        ).strip()

        qs = f"?operation={operation}"
        if search_text:
            qs += f"&search_text={search_text}"

        return redirect(request.path + qs)

    # ============================
    # GET HANDLING (ONLY RENDER)
    # ============================
    operation = request.GET.get('operation', 'add')
    search_text = (request.GET.get('search_text') or '').strip()

    records = SpecialityMaster.objects.filter(active='Y').order_by('sno')

    if search_text:
        records = records.filter(speciality__icontains=search_text)

    return render(request, 'hospApp/Admin/SpecialityMaster.html', {
        'operation': operation,
        'records': records,
        'search_text': search_text,
    })
