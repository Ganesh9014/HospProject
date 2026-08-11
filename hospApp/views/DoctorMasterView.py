from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse

from hospApp.models import DoctorMaster, SpecialityMaster
from django.contrib.auth.decorators import login_required   
@login_required(login_url='login')
def DoctorMasterView(request):
    # Determine operation (default = add)
    operation = request.GET.get('operation', 'add')
    specialities = SpecialityMaster.objects.filter(active='Y').order_by('speciality')

    # ----------------------------------------------------------------------
    # HELPER: COMMON QUERY

    
    def get_doctor_queryset(search_value):
        qs = DoctorMaster.objects.filter(active='Y').order_by('docname')
        if search_value:
            qs = qs.filter(docname__icontains=search_value)
        return qs
    # ----------------------------------------------------------------------

    # ============================================================
    # 1. ADD OPERATION
    # ============================================================
    if operation == 'add':
        if request.method == 'POST':
            docname = request.POST.get('docname', '').strip()
            speciality_id = request.POST.get('speciality')
            phoneno = request.POST.get('phoneno', '').strip()
            consultfee = request.POST.get('consultfee')
            ipconsultfee = request.POST.get('ipconsultfee') or 0
            emrfee = request.POST.get('emrfee') or 0
            revisittime = request.POST.get('revisittime')

            # ---- Validation ----
            if not docname:
                messages.error(request, "Please enter Doctor Name.")
                return redirect('DoctorMasterView')

            if not speciality_id:
                messages.error(request, "Please select Speciality.")
                return redirect('DoctorMasterView')

            if not phoneno.isdigit():
                messages.error(request, "Please enter a valid Phone Number (digits only).")
                return redirect('DoctorMasterView')

            if not consultfee or not consultfee.isdigit():
                messages.error(request, "Please enter a valid Consultation Fee.")
                return redirect('DoctorMasterView')

            # ---- Save ----
            try:
                speciality = SpecialityMaster.objects.get(pk=speciality_id)
                speciality_name = speciality.speciality.upper().strip()

                # Auto-format Dr. NAME (SPECIALITY)
                formatted_name = docname
                if not formatted_name.lower().startswith("dr"):
                    formatted_name = f"Dr {formatted_name.strip()}"


                DoctorMaster.objects.create(
                    docname=formatted_name,
                    speciality=speciality,
                    phoneno=phoneno,
                    consultfee=int(consultfee),
                    ipconsultfee=int(ipconsultfee),
                    emrfee=int(emrfee),
                    revisittime=revisittime,
                    active='Y',
                    createdtime=timezone.now(),
                    qualification=request.POST.get('qualification', '').strip(),
                    regno=request.POST.get('regno', '').strip(),


                )

                messages.success(request, f"Doctor '{formatted_name}' added successfully.")
                return redirect('DoctorMasterView')

            except SpecialityMaster.DoesNotExist:
                messages.error(request, "Invalid Speciality.")
                return redirect('DoctorMasterView')

        # GET request → show blank add page
        doctors = DoctorMaster.objects.filter(active='Y').order_by('docname')

    # ============================================================
    # 2. MODIFY OPERATION
    # ============================================================
    elif operation == 'modify':
        search_value = request.GET.get('docname') or request.POST.get('docname') or ''
        doctors = get_doctor_queryset(search_value)

        if request.method == 'POST' and 'update_btn' in request.POST:
            update_id = request.POST.get('update_btn')
            try:
                doctor = DoctorMaster.objects.get(pk=update_id)

                doctor.docname = request.POST.get(f'docname_{update_id}', '').strip()
                doctor.phoneno = request.POST.get(f'phoneno_{update_id}', '').strip()
                doctor.consultfee = int(request.POST.get(f'consultfee_{update_id}', 0))
                doctor.revisittime = request.POST.get(f'revisittime_{update_id}')
                doctor.ipconsultfee = int(request.POST.get(f'ipconsultfee_{update_id}', 0))
                doctor.emrfee = int(request.POST.get(f'emrfee_{update_id}', 0))
                doctor.regno = request.POST.get(f'regno_{update_id}', '').strip()
                doctor.qualification = request.POST.get(f'qualification_{update_id}', '').strip()

                doctor.updatedby = request.user.username
                doctor.updatedtime = timezone.now()
                doctor.save()

                messages.success(request, f"Doctor '{doctor.docname}' updated successfully.")
                return redirect(reverse('DoctorMasterView') + "?operation=modify")

            except DoctorMaster.DoesNotExist:
                messages.error(request, "Doctor not found.")
                return redirect(reverse('DoctorMasterView') + "?operation=modify")

    # ============================================================
    # 3. DELETE OPERATION
    # ============================================================
    elif operation == 'delete':
        search_value = request.GET.get('docname') or request.POST.get('docname') or ''
        doctors = get_doctor_queryset(search_value)

        if request.method == 'POST' and 'delete_btn' in request.POST:
            delete_id = request.POST.get('delete_btn')
            try:
                doctor = DoctorMaster.objects.get(pk=delete_id)
                doctor.active = 'N'
                doctor.updatedtime = timezone.now()
                doctor.save()
                messages.success(request, f"Doctor '{doctor.docname}' deleted successfully.")
                return redirect(reverse('DoctorMasterView') + "?operation=delete")

            except DoctorMaster.DoesNotExist:
                messages.error(request, "Doctor not found.")
                return redirect(reverse('DoctorMasterView') + "?operation=delete")

    # ============================================================
    # DEFAULT DISPLAY (Add screen)
    # ============================================================
    else:
        operation = 'add'
        doctors = DoctorMaster.objects.filter(active='Y').order_by('docname')

    # ----------------------------------------------------------------------
    # RENDER
    # ----------------------------------------------------------------------
    context = {
        'specialities': specialities,
        'doctors': doctors,
        'operation': operation,
        'searched': request.method == 'GET' and bool(request.GET),
    }

    return render(request, 'hospApp/Admin/DoctorMaster.html', context)
