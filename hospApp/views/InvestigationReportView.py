
from django.shortcuts import render


from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def InvestigationReportView(request):
    return render(request, 'hospApp/reports/InvestigationReportView.html')      


from django.shortcuts import render
from django.db.models import Q
from hospApp.models import tblInvestigationDetails, InvestigationMaster, OpPatientRegistration

from datetime import datetime, timedelta
from django.utils import timezone

from django.shortcuts import render
from hospApp.models import tblInvestigationDetails, InvestigationMaster, OpPatientRegistration, HospitalMaster
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum

from django.shortcuts import render
from hospApp.models import tblInvestigationDetails, InvestigationMaster, OpPatientRegistration, HospitalMaster
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum


from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def investigation_report(request):

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    inv_id = request.GET.get("inv_id")

    # 🔹 Base Query
    data = tblInvestigationDetails.objects.filter(active="Y")
    hospital = HospitalMaster.objects.filter(active='a').first()

    inv_obj = None

    # 🔹 Investigation Filter
    if inv_id:
        inv_id = int(inv_id)
        data = data.filter(invname=str(inv_id))

        inv_obj = InvestigationMaster.objects.filter(
            active="Y",
            ino=inv_id
        ).first()

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

    if from_date:
        from_date = datetime.strptime(from_date, "%Y-%m-%d")

    if to_date:
        to_date = datetime.strptime(to_date, "%Y-%m-%d")

    # 🔹 Get ALL UHIDs
    uhids = data.values_list('uhid', flat=True).distinct()

    # 🔹 Fetch Patient Details (MASTER SOURCE)
    patients = OpPatientRegistration.objects.filter(uhid__in=uhids)

    # 🔹 Create Map
    patient_map = {p.uhid: p for p in patients}

    # 🔥 Attach Patient + Override Fields
    for row in data:
        patient = patient_map.get(row.uhid)

        row.patient = patient  # full object

        # ✅ FORCE correct values (important)
        row.patname = patient.patname if patient else ""
        row.pro = patient.pro.pro_name if patient and patient.pro else ""
        row.refdoc = patient.refdoctor.docname if patient and patient.refdoctor else ""

    logged_user = request.session.get("username")

    total_cost = data.aggregate(total=Sum('cost'))['total'] or 0

    return render(request, "hospApp/reports/investigation_report.html", {
        "data": data,
        "inv_obj": inv_obj,
        "hospital": hospital,
        "from_date": from_date,
        "to_date": to_date,
        "logged_user": logged_user,
        "print_time": timezone.now(),
        "total_cost": total_cost
    })