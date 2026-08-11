from django.shortcuts import render
from hospApp.models import TblServices, HospitalMaster, OpPatientRegistration
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def ServiceReportView(request):
    return render(request, 'hospApp/reports/ServiceReport.html')

@login_required(login_url='login')
def ServiceReportResultView(request):
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    ser_id = request.GET.get("ser_id")
    ser_name = request.GET.get("ser_name")

    # 🔹 Base Query — only active records
    data = TblServices.objects.filter(isactive="Y")
    hospital = HospitalMaster.objects.filter(active='a').first()

    # 🔹 Service Filter — services field stores ID as string
    if ser_id:
        data = data.filter(services=str(ser_id))

    # 🔹 Date Filter
    if from_date and to_date:
        start = datetime.strptime(from_date, "%Y-%m-%d")
        end = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)

        start = timezone.make_aware(start)
        end = timezone.make_aware(end)

        data = data.filter(
            generateddate__gte=start,
            generateddate__lt=end
        )

    from_date_obj = datetime.strptime(from_date, "%Y-%m-%d") if from_date else None
    to_date_obj = datetime.strptime(to_date, "%Y-%m-%d") if to_date else None

    # 🔹 Fetch all UHIDs and build patient map
    uhids = data.values_list('uhid', flat=True).distinct()
    patients = OpPatientRegistration.objects.filter(uhid__in=uhids)
    patient_map = {p.uhid: p for p in patients}

    # 🔹 Attach patient info to each row
    for row in data:
        patient = patient_map.get(row.uhid)
        row.patient = patient
        row.patname = patient.patname if patient else ""
        row.age = patient.age if patient else ""
        row.refdoc = patient.refdoctor.docname if patient and patient.refdoctor else ""

    logged_user = request.session.get("username")
    total_amount = data.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, "hospApp/reports/ServiceReportResult.html", {
        "data": data,
        "hospital": hospital,
        "from_date": from_date_obj,
        "to_date": to_date_obj,
        "ser_name": ser_name,
        "logged_user": logged_user,
        "print_time": timezone.now(),
        "total_amount": total_amount,
    })