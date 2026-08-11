from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from hospApp.models import RefDoctorMaster, SpecialityMaster
import re


@login_required(login_url='login')
def RefDoctorMasterView(request):

    # ============================
    # POST HANDLING (NO RENDER)
    # ============================
    if request.method == 'POST':

        operation = request.POST.get('operation', 'add')

        # helper: mobile validation
        def is_valid_mobile(number: str) -> bool:
            if not re.fullmatch(r'\d{10}', number):
                return False
            if len(set(number)) == 1:
                return False
            if not number.startswith(('6', '7', '8', '9')):
                return False
            return True

        # ---------- ADD ----------
        if operation == 'add':
            docname = (request.POST.get('docname') or '').strip()
            phoneno = (request.POST.get('phoneno') or '').strip()
            speciality_id = request.POST.get('specialized')

            if not docname:
                messages.error(request, "Please enter Doctor Name.")
            elif not speciality_id:
                messages.error(request, "Please select Speciality.")
            elif not is_valid_mobile(phoneno):
                messages.error(
                    request,
                    "Enter a valid 10-digit mobile number starting with 6, 7, 8, or 9."
                )
            elif RefDoctorMaster.objects.filter(
                docname__iexact=docname,
                phoneno__iexact=phoneno,
                active='Y'
            ).exists():
                messages.error(request, "This Doctor already exists.")
            else:
                try:
                    speciality = SpecialityMaster.objects.get(pk=speciality_id)
                    RefDoctorMaster.objects.create(
                        docname=docname,
                        phoneno=phoneno,
                        specialized=speciality,
                        active='Y',
                        createdby=request.user.username if request.user.is_authenticated else 'system',
                        createdtime=timezone.now(),
                    )
                    messages.success(request, f"Doctor '{docname}' added successfully.")
                except SpecialityMaster.DoesNotExist:
                    messages.error(request, "Invalid Speciality selected.")

            return redirect(request.path + "?operation=add")

        # ---------- MODIFY ----------
        if operation == 'modify' and 'update_btn' in request.POST:
            update_id = request.POST.get('update_btn')

            try:
                doctor = RefDoctorMaster.objects.get(pk=update_id, active='Y')
                new_docname = (request.POST.get(f'docname_{update_id}') or '').strip()
                new_phone = (request.POST.get(f'phoneno_{update_id}') or '').strip()

                if not new_docname:
                    messages.error(request, "Doctor Name cannot be empty.")
                elif not is_valid_mobile(new_phone):
                    messages.error(
                        request,
                        "Enter a valid 10-digit mobile number starting with 6, 7, 8, or 9."
                    )
                else:
                    doctor.docname = new_docname
                    doctor.phoneno = new_phone
                    doctor.updatedby = request.user.username if request.user.is_authenticated else 'system'
                    doctor.updatedtime = timezone.now()
                    doctor.save()
                    messages.success(
                        request,
                        f"Doctor '{doctor.docname}' updated successfully."
                    )

            except RefDoctorMaster.DoesNotExist:
                messages.error(request, "Doctor not found.")

            return redirect(request.path + "?operation=modify")

        # ---------- DELETE ----------
        if operation == 'delete' and 'delete_btn' in request.POST:
            delete_id = request.POST.get('delete_btn')

            try:
                doctor = RefDoctorMaster.objects.get(pk=delete_id, active='Y')
                doctor.active = 'N'
                doctor.updatedby = request.user.username if request.user.is_authenticated else 'system'
                doctor.updatedtime = timezone.now()
                doctor.save()
                messages.success(
                    request,
                    f"Doctor '{doctor.docname}' deleted successfully."
                )
            except RefDoctorMaster.DoesNotExist:
                messages.error(request, "Doctor not found.")

            return redirect(request.path + "?operation=delete")

        # ---------- SEARCH POST FALLBACK ----------
        search_text = request.POST.get('docname', '').strip()
        qs = f"?operation={operation}"
        if search_text:
            qs += f"&docname={search_text}"
        return redirect(request.path + qs)

    # ============================
    # GET HANDLING (ONLY RENDER)
    # ============================
    operation = request.GET.get('operation', 'add')
    search_text = request.GET.get('docname', '').strip()

    specialities = SpecialityMaster.objects.filter(active='Y').order_by('speciality')

    doctors = RefDoctorMaster.objects.filter(active='Y').order_by('docname')

    if search_text:
        doctors = doctors.filter(docname__icontains=search_text)

    return render(request, 'hospApp/Admin/RefDoctorMaster.html', {
        'specialities': specialities,
        'doctors': doctors,
        'operation': operation,
        'searched': True,
    })
