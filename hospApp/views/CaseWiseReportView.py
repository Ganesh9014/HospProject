from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from hospApp.models import (
    DoctorConsultation,
    CaseTypeMaster,
    OpPatientRegistration,
    DoctorMaster,
    HospitalMaster
)


@login_required(login_url='login')
def CaseWiseReportView(request):
    cases = CaseTypeMaster.objects.filter(active='Y').order_by('casetype')
    return render(request, 'hospApp/reports/CaseWiseReport.html', {'cases': cases})


@login_required(login_url='login')
def CaseWiseReportResultView(request):

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    casetype_id = request.GET.get("casetype")

    hospital = HospitalMaster.objects.filter(active='a').first()

    if not from_date or not to_date:
        return render(request, 'hospApp/reports/CaseWiseReport.html')

    fd = timezone.make_aware(datetime.strptime(from_date, "%Y-%m-%d"))
    td = timezone.make_aware(datetime.strptime(to_date, "%Y-%m-%d")) + timedelta(days=1)

    # ================= CASETYPE NAME =================
    selected_casetype_name = "ALL"
    if casetype_id and casetype_id != "ALL":
        case_obj = CaseTypeMaster.objects.filter(sno=casetype_id).first()
        if case_obj:
            selected_casetype_name = case_obj.casetype

    # ================= CONSULTATION QUERY =================
    consultation_qs = DoctorConsultation.objects.filter(
        createddate__gte=fd,
        createddate__lt=td,
        isactive="Y"
    ).select_related('casetypemaster', 'doctor')

    if casetype_id and casetype_id != "ALL":
        consultation_qs = consultation_qs.filter(casetypemaster_id=casetype_id)

    # ================= COLLECT UHIDS =================
    uhid_list = list(set(
        consultation_qs.values_list('uhid', flat=True)
    ))

    # ================= PATIENT MAP =================
    # ✅ personal details from OpPatientRegistration
    patient_map = {
        p.uhid: p
        for p in OpPatientRegistration.objects.filter(
            uhid__in=uhid_list
        ).select_related('pro', 'refdoctor')
    }


    
   
    def patient_info(uhid):
        p = patient_map.get(uhid)
        return {
            "patname": p.patname if p else "",
            "phone":   p.phone if p else "",
            "address": p.address if p else "",
        }

    # ================= BUILD REPORT DATA =================
    report_data = []

    for i, c in enumerate(consultation_qs, start=1):
        info = patient_info(c.uhid)
        report_data.append({
            "sno":      i,
            "uhid":     c.uhid,
            "opno":     c.opno or "-",
            "patname":  info["patname"],
            "phone":    info["phone"],
            "address":  info["address"],
            "doctor":   c.doctor.docname if c.doctor else "-",
            "casetype": c.casetypemaster.casetype if c.casetypemaster else "-",
            'date':     c.createddate,
        })

    return render(request, 'hospApp/reports/CaseWiseReportResult.html', {
        "report_data":          report_data,
        "total_count":          len(report_data),
        "hospital":             hospital,
        "selected_casetype":    selected_casetype_name,
        "from_date":            datetime.strptime(from_date, "%Y-%m-%d"),
        "to_date":              datetime.strptime(to_date,   "%Y-%m-%d"),
        "print_time":           timezone.now(),
        "logged_user":          request.session.get("username"),
    })