from django.shortcuts import render, redirect
from django.utils import timezone   
from datetime import datetime
from hospApp.models import DoctorConsultation
from hospApp.utils import filter_by_date_range
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from hospApp.models.PatientVitals import PatientVitals

@login_required(login_url='login')
def check_basic(request):

    today = timezone.localtime().date()

    selected_date = request.GET.get("date")
    if selected_date:
        from_date_str = selected_date
        to_date_str   = selected_date
    else:
        from_date_str = request.GET.get('from_date', str(today))
        to_date_str   = request.GET.get('to_date',   str(today))

    name  = request.GET.get('name',  '').strip()
    phone = request.GET.get('phone', '').strip()
    uhid  = request.GET.get('uhid',  '').strip()

    try:
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
    except:
        from_date = today
    try:
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
    except:
        to_date = today

    # ✅ Name or phone → search whole table, no date filter
    if name or phone:
        qs = DoctorConsultation.objects.filter(vitals__isnull=True)
    else:
        qs = filter_by_date_range(
            DoctorConsultation.objects.filter(vitals__isnull=True),
            'createddate', from_date, to_date
        )

    if uhid:
        qs = qs.filter(uhid__icontains=uhid)
    if name:
        qs = qs.filter(patname__icontains=name)
    if phone:
        qs = qs.filter(phone__icontains=phone)

    qs = qs.order_by('-createddate')[:300]

    return render(request, 'hospApp/Admin/check_basic.html', {
        'patients':  qs,
        'from_date': from_date_str,
        'to_date':   to_date_str,
        'name':      name,
        'phone':     phone,
        'return':    request.GET.get("return", ""),
    }) 



@login_required(login_url='login')    
def values_insert(request):
    return render(request, "hospApp/Admin/values_insert.html", {})  

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def get_patient_details_for_insert(request):
    """
    Fetch latest DoctorConsultation for UHID (OP path). Returns extra doctor/ref info.
    """
    uhid = request.GET.get('uhid', '').strip()
    if not uhid:
        return JsonResponse({'success': False, 'error': 'UHID not provided'}, status=400)

    consult = DoctorConsultation.objects.filter(uhid=uhid).order_by('-createddate').first()

    if not consult:
        return JsonResponse({'success': False, 'error': 'No consultation found'}, status=404)

    # safe access to related objects
     # depends how you store it

    doctor = getattr(consult, 'doctor', None)
    doctor_name = doctor.docname if doctor else ""
    doctor_id = doctor.docid if doctor else ""

    data = {
        'patname': consult.patname,
        'patid': consult.patid,
        'age': consult.age,
        'agetype': consult.agetype,
        'gender': consult.gender,
        'phone': consult.phone,
        'gardian': consult.gardian,
        
        'doc_name': doctor_name,
        'doc_id': doctor_id,
        'uhid': consult.uhid,
        # keep paymenttype key to help JS but backend will read 'paymentmode' on submit
        'paymenttype': getattr(consult, 'paymenttype', 'Cash'),
    }

    return JsonResponse({'success': True, 'data': data})

from django.shortcuts import render, redirect
from django.contrib import messages
from hospApp.models import DoctorConsultation
from hospApp.models.PatientVitals import PatientVitals
from django.utils import timezone


@login_required(login_url='login')
def values_insert(request):
    if request.method == "POST":
        uhid = request.POST.get("uhid")

        # 1️⃣ Find latest consultation for this UHID
        consultation = DoctorConsultation.objects.filter(
            uhid=uhid
        ).order_by("-createddate").first()

        if not consultation:
            messages.error(request, "No consultation found for this patient")
            return redirect("values_insert")

        # 2️⃣ Create or Update vitals (OneToOne safe)
        vitals, created = PatientVitals.objects.update_or_create(
            consultation=consultation,
            defaults={
                "temperature": request.POST.get("temp") or None,
                "bp": request.POST.get("bp") or None,
                "pulse": request.POST.get("pr") or None,
                "spo2": request.POST.get("spo2") or None,
                "weight": request.POST.get("weight") or None,
            }
        )

        messages.success(request, "Vitals saved successfully ✅")
        return redirect("check_basic")  # or any page you want

    return render(request, "hospApp/Admin/values_insert.html")
