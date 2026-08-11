from django.utils import timezone
from datetime import timedelta, datetime, time
from django.shortcuts import render
from hospApp.models import OpPatientRegistration,DoctorConsultation
from django.db.models import Q
from django.contrib.auth.decorators import login_required   
from hospApp.utils import filter_by_date_range
from hospApp.models import Tbluserpermission, HospitalMaster,tblInvestigationDetails, DoctorConsultation, TblServices, OpPayment, OpPatientRegistration
@login_required(login_url='login')
def SearchUHIDView(request):
    today = timezone.localtime().date()

    selected_date = request.GET.get("date")
    if selected_date:
        from_date_str = selected_date
        to_date_str   = selected_date
    else:
        from_date_str = request.GET.get('from_date', str(today))
        to_date_str   = request.GET.get('to_date',   str(today))

    name      = request.GET.get('name', '').strip()
    phone     = request.GET.get('phone', '').strip()
    towards   = request.GET.get('towards', '').strip()
    return_to = request.GET.get('return', '')

    try:
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
    except:
        from_date = today
    try:
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
    except:
        to_date = today

    # ✅ NO start_datetime / end_datetime needed anymore

    patients = OpPatientRegistration.objects.none()

    if return_to in ['OpPayment', 'Refund', 'SittingsPage'] and towards:
        if name or phone:
            if towards == 'Consultation':
                qs = DoctorConsultation.objects.filter(isactive='Y')
            elif towards == 'Investigation':
                qs = tblInvestigationDetails.objects.all()
            elif towards == 'Procedures':
                qs = TblServices.objects.filter(isactive='Y')
            else:
                qs = DoctorConsultation.objects.none()

            uhids    = qs.values_list('uhid', flat=True).distinct()
            patients = OpPatientRegistration.objects.filter(uhid__in=uhids)
            if name:
                patients = patients.filter(patname__icontains=name)
            if phone:
                patients = patients.filter(phone__icontains=phone)

        else:
            # ✅ ALL using filter_by_date_range now
            if towards == 'Consultation':
                uhids = filter_by_date_range(
                    DoctorConsultation.objects.filter(isactive='Y'),
                    'createddate', from_date, to_date
                ).values_list('uhid', flat=True).distinct()

            elif towards == 'Investigation':
                uhids = filter_by_date_range(
                    tblInvestigationDetails.objects.all(),
                    'generateddate', from_date, to_date
                ).values_list('uhid', flat=True).distinct()

            elif towards == 'Procedures':
                uhids = filter_by_date_range(
                    TblServices.objects.filter(isactive='Y'),
                    'generateddate', from_date, to_date
                ).values_list('uhid', flat=True).distinct()

            else:
                uhids = []

            patients = OpPatientRegistration.objects.filter(uhid__in=uhids)

    else:
        if name or phone:
            patients = OpPatientRegistration.objects.all()
        else:
            # ✅ Already correct
            patients = filter_by_date_range(
                OpPatientRegistration.objects.all(),
                'createdtime', from_date, to_date
            )
        if name:
            patients = patients.filter(patname__icontains=name)
        if phone:
            patients = patients.filter(phone__icontains=phone)

    patients = patients.order_by('-createdtime')[:300]

    return render(request, 'hospApp/Admin/SearchUHID.html', {
        'patients':  patients,
        'from_date': from_date_str,
        'to_date':   to_date_str,
        'name':      name,
        'phone':     phone,
        'towards':   towards,
        'return':    return_to,
    })
@login_required(login_url='login')
def SearchConsultationUHIDView(request):
    

    today = timezone.localtime().date()

    selected_date = request.GET.get("date")
    if selected_date:
        from_date_str = selected_date
        to_date_str = selected_date
    else:
        from_date_str = request.GET.get('from_date', str(today))
        to_date_str = request.GET.get('to_date', str(today))

    name  = request.GET.get('name', '').strip()
    phone = request.GET.get('phone', '').strip()
    uhid  = request.GET.get('uhid', '').strip()

    try:
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
    except:
        from_date = today
    try:
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
    except:
        to_date = today

    # ✅ If name or phone given — search whole table, no date filter
    if name or phone:
        qs = DoctorConsultation.objects.filter(isactive='Y')
    else:
        # Date range only when no name/phone
        qs = filter_by_date_range(
            DoctorConsultation.objects.filter(isactive='Y'),
            'createddate', from_date, to_date
        )

    if uhid:
        qs = qs.filter(uhid__icontains=uhid)
    if name:
        qs = qs.filter(patname__icontains=name)
    if phone:
        qs = qs.filter(phone__icontains=phone)

    qs = qs.order_by('-createddate')[:300]

    return render(request, 'hospApp/Admin/SearchConsultationUHID.html', {
        'patients':  qs,
        'from_date': from_date_str,
        'to_date':   to_date_str,
        'name':      name,
        'phone':     phone,
        'return':    request.GET.get("return", ""),
    })
