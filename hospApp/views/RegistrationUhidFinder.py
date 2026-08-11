
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta, datetime, time
from django.shortcuts import render
from hospApp.models import OpPatientRegistration,DoctorConsultation
from django.db.models import Q
from django.contrib.auth.decorators import login_required   


@login_required(login_url='login')
def RegistrationUhidFinder(request):
    today = timezone.localtime().date()
    default_from = today

    selected_date = request.GET.get("date")

    if selected_date:
        from_date_str = selected_date
        to_date_str = selected_date
    else:
        from_date_str = request.GET.get('from_date', str(default_from))
        to_date_str = request.GET.get('to_date', str(today))

    name = request.GET.get('name', '').strip()
    phone = request.GET.get('phone', '').strip()
    uhid = request.GET.get('uhid', '').strip()

    try:
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
    except:
        from_date = default_from

    try:
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
    except:
        to_date = today

    start_dt = timezone.make_aware(datetime.combine(from_date, time.min))
    end_dt = timezone.make_aware(datetime.combine(to_date, time.max))

    qs = OpPatientRegistration.objects.filter(
        entrydate__range=[start_dt, end_dt]
    )
    

    if uhid:
        qs = qs.filter(uhid__icontains=uhid)
    if name:
        qs = qs.filter(patname__icontains=name)
    if phone:
        qs = qs.filter(phone__icontains=phone)

    qs = qs.order_by('-entrydate')[:300]
    return render(request, 'hospApp/frontoffice/RegistrationUhidFinder.html', {
    'patients': qs,
    'from_date': from_date_str,
    'to_date': to_date_str,
    'name': name,
    'phone': phone
})