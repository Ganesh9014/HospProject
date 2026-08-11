
from django.shortcuts import render 
from hospApp.models import Tbluserpermission


from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def CancellationReport(request):
    users = Tbluserpermission.objects.filter(isactive=True).order_by('username')
    return render(request, "hospApp/reports/CancellationReport.html", {"users": users})


from django.shortcuts import render
from hospApp.models import TblOpCancellation
from datetime import datetime, timedelta


from django.shortcuts import render
from hospApp.models import TblOpCancellation
from datetime import datetime, timedelta


from collections import defaultdict
from django.shortcuts import render
from hospApp.models import TblOpCancellation,HospitalMaster
from datetime import datetime, timedelta

from django.shortcuts import render
from hospApp.models import TblOpCancellation, HospitalMaster, OpPatientRegistration
from datetime import datetime, timedelta
from django.utils import timezone   



def parse_date(value):
    if "T" in value:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    else:
        return datetime.strptime(value, "%Y-%m-%d")


from django.contrib.auth.decorators import login_required

from hospApp.models import TblOpCancellation, HospitalMaster, OpPatientRegistration, ExpenditureEntry

@login_required(login_url='login')
def CancellationReportResult(request):

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    username = request.GET.get("username")
    services = request.GET.getlist("services[]")

    data = TblOpCancellation.objects.all()
    hospital = HospitalMaster.objects.filter(active='a').first()

    # ================= DATE FILTER =================
    if from_date and to_date:
        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_dt = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)
        data = data.filter(createddate__gte=from_dt, createddate__lt=to_dt)

    # ================= USER FILTER =================
    if username:
        data = data.filter(createdby=username)

    fd = parse_date(from_date)
    td = parse_date(to_date)

    # ================= TYPE FILTER =================
    type_mapping = {
        "OP Consultation": "Consultation",
        "OP Procedures": "Procedure",
        "OP Payments": "OpPayment",
        "OP Investigations": "Investigation",
    }
    mapped_services = [type_mapping.get(s) for s in services if s in type_mapping]
    if mapped_services:
        data = data.filter(type__in=mapped_services)

    # ================= FETCH PATIENT MAP =================
    uhids = data.values_list('uhid', flat=True).distinct()
    patients = OpPatientRegistration.objects.filter(uhid__in=uhids)
    patient_map = {p.uhid: p for p in patients}

    for row in data:
        p = patient_map.get(row.uhid)
        row.patname = p.patname if p else ""
        row.pro = p.pro.pro_name if p and p.pro else ""
        row.refdoc = p.refdoctor.docname if p and p.refdoctor else ""

    # ================= SPLIT DATA =================
    consultation = [r for r in data if r.type == "Consultation"]
    procedure    = [r for r in data if r.type == "Procedure"]
    investigation = [r for r in data if r.type == "Investigation"]
    payments     = [r for r in data if r.type == "OpPayment"]

    # ================= EXPENDITURE (separate model) =================
    expenditure_data = []
    total_exp = 0

    if "EXPENDITURE" in services:
        exp_qs = ExpenditureEntry.objects.filter(active='N')

        # Date filter
        if from_date and to_date:
            exp_qs = exp_qs.filter(created_at__gte=from_dt, created_at__lt=to_dt)

        # User filter
        if username:
            exp_qs = exp_qs.filter(username=username)

        expenditure_data = list(exp_qs)
        total_exp = sum(e.amount or 0 for e in expenditure_data)

    # ================= TOTALS =================
    total_cons = sum(i.amtpaid or 0 for i in consultation)
    total_proc = sum(i.amtpaid or 0 for i in procedure)
    total_inv  = sum(i.amtpaid or 0 for i in investigation)
    total_pay  = sum(i.amtpaid or 0 for i in payments)

    grand_total = total_cons + total_proc + total_inv + total_pay + total_exp

    context = {
        "consultation": consultation,
        "procedure": procedure,
        "investigation": investigation,
        "payments": payments,
        "expenditure_data": expenditure_data,   # ✅ new

        "total_cons": total_cons,
        "total_proc": total_proc,
        "total_inv":  total_inv,
        "total_pay":  total_pay,
        "total_exp":  total_exp,                # ✅ new

        "grand_total": grand_total,

        "from_date": fd,
        "to_date": td,
        "username": username,
        "hospital": hospital,
        "print_time": timezone.now(),
        "logged_user": request.session.get("username"),
    }

    return render(request, "hospApp/reports/CancellationReportResult.html", context)