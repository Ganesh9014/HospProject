from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import F, Sum, Min
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from hospApp.models import RefDoctorMaster, OpPayment, InvestigationReport, DoctorMaster, OpPatientRegistration, HospitalMaster
from hospApp.models.InvestigationDetails import tblInvestigationDetails
from hospApp.models.InvestigationMaster import InvestigationMaster
from hospApp.models.NewInvMaster import NewInvMaster
from datetime import datetime, timedelta
import json
import re


@login_required(login_url='login')
def LabEntry(request):
    return render(request, 'hospApp/Lab/LabEntry.html')


@login_required(login_url='login')
def get_lab_entries_by_date(request):
    from_date = request.GET.get('from_date')
    to_date   = request.GET.get('to_date')

    if not from_date or not to_date:
        return JsonResponse({'data': []})

    start_date = timezone.make_aware(datetime.strptime(from_date, "%Y-%m-%d"))
    end_date   = timezone.make_aware(datetime.strptime(to_date,   "%Y-%m-%d")) + timedelta(days=1)

    bills = (
        tblInvestigationDetails.objects
        .filter(generateddate__gte=start_date, generateddate__lt=end_date, active="Y")
        .values('billno', 'uhid')
        .annotate(generateddate=Min('generateddate'))
        .order_by('billno')
    )

    result = []
    for row in bills:
        patient  = OpPatientRegistration.objects.filter(uhid=row['uhid']).values('patname', 'phone').first()
        local_dt = timezone.localtime(row['generateddate'])
        result.append({
            'billno':        row['billno'],
            'uhid':          row['uhid'],
            'patname':       patient['patname'] if patient else '—',
            'phone':         patient['phone']   if patient else '—',
            'generateddate': local_dt.strftime("%d-%m-%Y %H:%M")
        })

    return JsonResponse({'data': result})


@login_required(login_url='login')
def get_investigations_by_bill(request):
    billno = request.GET.get('billno')

    if not billno:
        return JsonResponse({'status': 'invalid', 'message': 'Invalid bill number'})

    src = tblInvestigationDetails.objects.filter(billno=billno, active="Y").aggregate(
        total=Sum("cost"), base_paid=Min("paidamt"), base_conc=Min("concessionamt")
    )
    op = OpPayment.objects.filter(billno=billno, active="Y").aggregate(
        paid=Sum("patamt"), conc=Sum("concession")
    )

    total      = src["total"]      or 0
    paid       = (src["base_paid"] or 0) + (op["paid"] or 0)
    concession = (src["base_conc"] or 0) + (op["conc"] or 0)
    due        = total - (paid + concession)

    inv_rows = tblInvestigationDetails.objects.filter(billno=billno, active="Y").values('invname', 'cost')

    if not inv_rows.exists():
        return JsonResponse({'status': 'invalid', 'message': 'Invalid or inactive bill number'})

    inv_ids    = [row['invname'] for row in inv_rows if row['invname']]
    masters    = InvestigationMaster.objects.filter(ino__in=inv_ids).values('ino', 'invname')
    master_map = {str(m['ino']): m['invname'] for m in masters}

    inv_data = []
    for row in inv_rows:
        inv_data.append({
            'inv_master_id': row['invname'],
            'inv_name':      master_map.get(str(row['invname']), row['invname']),
            'cost':          row['cost']
        })

    return JsonResponse({
        'data': inv_data,
        'payment': {'total': total, 'paid': paid, 'concession': concession, 'due': due}
    })


@login_required(login_url='login')
def get_patient_by_bill(request):
    billno = request.GET.get('billno')

    if not billno:
        return JsonResponse({'data': None})

    inv = tblInvestigationDetails.objects.filter(
        billno=billno, active="Y"
    ).values('uhid', 'generateddate', 'doc').first()

    if not inv:
        return JsonResponse({'data': None})

    patient = OpPatientRegistration.objects.filter(uhid=inv['uhid']).values(
        'patname', 'uhid', 'phone', 'age', 'gender', 'agetype'
    ).first()

    if not patient:
        return JsonResponse({'data': None})

    local_dt = timezone.localtime(inv['generateddate'])

    return JsonResponse({
        'data': {
            'billno':        billno,
            'patname':       patient['patname'],
            'uhid':          patient['uhid'],
            'phone':         patient['phone'],
            'age':           patient['age'],
            'gender':        patient['gender'],
            'agetype':       patient['agetype'],
            'generateddate': local_dt.strftime("%d-%m-%Y %H:%M"),
            'doc':           inv['doc']
        },
        'generateddate_raw': inv['generateddate'].isoformat()
    })


@login_required(login_url='login')
@login_required(login_url='login')
def get_report_entries(request):
    inv_id = request.GET.get('inv_id')
    billno = request.GET.get('billno')

    if not inv_id:
        return JsonResponse({'data': []})

    inv_master = InvestigationMaster.objects.filter(ino=inv_id).first()
    inv_name   = inv_master.invname if inv_master else ""

    dept_id      = None
    is_radiology = False
    try:
        from hospApp.models import DepartmentPhotoMaster
        if inv_master and inv_master.department:
            dept         = DepartmentPhotoMaster.objects.filter(department=inv_master.department).first()
            dept_id      = dept.dno if dept else None
            is_radiology = "radiology" in (dept.department.lower() if dept else "")
    except Exception:
        pass

    # ── Look up patient gender/age once, from the bill ──────────
    gender  = ""
    age     = 0
    agetype = ""
    if billno:
        inv_row = tblInvestigationDetails.objects.filter(billno=billno, active="Y").values('uhid').first()
        if inv_row:
            patient = OpPatientRegistration.objects.filter(uhid=inv_row['uhid']).values('gender', 'age', 'agetype').first()
            if patient:
                gender  = (patient['gender']  or "").strip().lower()
                age     = patient['age']      or 0
                agetype = (patient['agetype'] or "").strip().lower()

    def is_child(cutoff):
        cutoff = cutoff or 12
        if agetype.startswith("month") or agetype.startswith("day"):
            return True
        return age < cutoff

    data = (
        NewInvMaster.objects
        .filter(invname=inv_id)
        .order_by('sno')
        .values('sno', 'test', 'units', 'normal', 'method', 'submethod', 'header', 'defaults',
                 'result_type', 'male_low', 'male_high', 'female_low', 'female_high',
                 'child_low', 'child_high', 'child_age_cutoff', 'abnormal_values')
    )

    data_list = []
    for row in data:
        low = high = None
        abnormal_values = []
        result_type = row['result_type'] or 'numeric'

        if result_type == 'numeric':
            if is_child(row['child_age_cutoff']) and row['child_low'] is not None:
                low, high = row['child_low'], row['child_high']
            elif gender in ('m', 'male') and row['male_low'] is not None:
                low, high = row['male_low'], row['male_high']
            elif gender in ('f', 'female') and row['female_low'] is not None:
                low, high = row['female_low'], row['female_high']
            else:
                low  = row['male_low']  or row['female_low']  or row['child_low']
                high = row['male_high'] or row['female_high'] or row['child_high']

        elif result_type == 'text_choice' and row['abnormal_values']:
            abnormal_values = [v.strip().lower() for v in row['abnormal_values'].split(',') if v.strip()]

        data_list.append({
            'sno': row['sno'], 'test': row['test'], 'units': row['units'],
            'normal': row['normal'], 'method': row['method'], 'submethod': row['submethod'],
            'header': row['header'], 'defaults': row['defaults'],
            'result_type': result_type,
            'low': low, 'high': high,
            'abnormal_values': abnormal_values,
        })

    return JsonResponse({
        'investigation': inv_name,
        'department_id': dept_id,
        'data':          data_list,
        'is_radiology':  is_radiology,
    })
@login_required(login_url='login')
def ReportEntry(request):
    
    return render(request, "hospApp/Lab/ReportEntry.html")


@login_required(login_url='login')
def FinalReportView(request):
    hospital = HospitalMaster.objects.filter(active='a').first()

    billno = request.GET.get("billno")
    inv_id = request.GET.get("inv_id")

    reports = InvestigationReport.objects.filter(
        billno=billno,
        inv_id=inv_id,
        is_active=True
    ).order_by("id")

    inv = InvestigationMaster.objects.filter(
        ino=inv_id
    ).select_related('department').first()

    inv_time = tblInvestigationDetails.objects.filter(
        billno=billno,
        invname=inv_id,
        active="Y"
    ).values_list("generateddate", flat=True).first()

    doctor_name = ""
    department = ""
    department_photo = ""
    speciality = ""
    qualification = ""

    if inv and inv.department:
        department = inv.department.department

        try:
            from hospApp.models import DepartmentPhotoMaster

            dept_photo_obj = DepartmentPhotoMaster.objects.filter(
                department__iexact=inv.department.department
            ).first()

            if dept_photo_obj and dept_photo_obj.phote:
                department_photo = dept_photo_obj.phote.url

        except Exception:
            pass

    if reports.exists() and reports[0].doc:
        doctor = DoctorMaster.objects.filter(
            docid=reports[0].doc
        ).first()

        if doctor:
            speciality = doctor.speciality
            doctor_name = doctor.docname
            qualification = doctor.qualification

    pat = None
    if reports.exists():
        pat = OpPatientRegistration.objects.filter(
            uhid=reports[0].uhid
        ).first()

    has_normal = reports.filter(
        normal__isnull=False
    ).exclude(
        normal=''
    ).exists()

    # ==========================
    # Signature + Name + Reg No
    # ==========================
    signature_url = ""
    sign_name = ""
    sign_regno = ""

    try:
        from hospApp.models import DepartmentPhotoMaster

        sig_dept = None

        if inv and inv.department:
            dept_name = inv.department.department.lower()

            # Radiology -> own signature
            if "radiology" in dept_name:
                sig_dept = DepartmentPhotoMaster.objects.filter(
                    department__iexact=inv.department.department
                ).first()

            # All others -> Pathology signature
            else:
                sig_dept = DepartmentPhotoMaster.objects.filter(
                    department__icontains="pathology"
                ).first()

            if sig_dept and sig_dept.signature:
                signature_url = sig_dept.signature.url
                sign_name = sig_dept.name or ""
                sign_regno = sig_dept.regno or ""

    except Exception:
        pass

    return render(
        request,
        "hospApp/Lab/FinalReport.html",
        {
            "inv": inv,
            "reports": reports,
            "doctor_name": doctor_name,
            "inv_name": inv.invname if inv else "",
            "department": department,
            "department_photo": department_photo,
            "investigation_time": inv_time,
            "pat": pat,
            "hospital": hospital,
            "speciality": speciality,
            "qualification": qualification,
            "has_normal": has_normal,
            "signature_url": signature_url,
            "sign_name": sign_name,
            "sign_regno": sign_regno,
            "is_radiology": (
                "radiology" in (
                    inv.department.department.lower()
                    if inv and inv.department
                    else ""
                )
            ),
        }
    )

@login_required(login_url='login')
@csrf_exempt
def save_report_entries(request):

    # ✅ helper — strip leading spaces from each line
    def clean_text(text):
        return "\n".join(line.strip() for line in (text or "").splitlines())

    data = json.loads(request.body)

    report_dt_str = data.get("report_datetime")
    if report_dt_str:
        report_dt = datetime.fromisoformat(report_dt_str)
        if timezone.is_naive(report_dt):
            report_dt = timezone.make_aware(report_dt)
    else:
        report_dt = timezone.now()

    billno = data["billno"]
    inv_id = data["inv_id"]

    existing     = InvestigationReport.objects.filter(billno=billno, inv_id=inv_id, is_active=True)
    existing_map = {r.test: r for r in existing}
    incoming_tests = []

    for r in data["rows"]:
        test       = r["test"]
        is_check   = r.get("is_check", False)
        impression = clean_text(r.get("impression", ""))   # ✅ cleaned
        incoming_tests.append(test)

        if test in existing_map:
            obj               = existing_map[test]
            obj.result        = clean_text(r["result"])    # ✅ cleaned
            obj.normal        = r["normal"]
            obj.units         = r.get("units")
            obj.header        = r.get("header")
            obj.method        = r.get("method")
            obj.submethod     = r.get("submethod")
            obj.is_check      = is_check
            obj.impression    = impression
            obj.generateddate = report_dt
            obj.save()
        else:
            InvestigationReport.objects.create(
                billno        = billno,
                uhid          = data["uhid"],
                patname       = data["patname"],
                age           = data.get("age"),
                agetype       = data.get("agetype"),
                gender        = data.get("gender"),
                doc           = data.get("doc"),
                inv_id        = inv_id,
                test          = test,
                result        = clean_text(r["result"]),   # ✅ cleaned
                units         = r.get("units"),
                normal        = r["normal"],
                header        = r.get("header"),
                method        = r.get("method"),
                submethod     = r.get("submethod"),
                impression    = impression,
                userid        = data["userid"],
                generateddate = report_dt,
                is_active     = True,
                is_check      = is_check,
            )

    # soft delete removed rows
    for r in existing:
        if r.test not in incoming_tests:
            r.is_active = False
            r.save()

    return JsonResponse({"status": "success"})


@login_required(login_url='login')
def check_report_exists(request):
    billno = request.GET.get("billno")
    inv_id = request.GET.get("inv_id")

    exists = InvestigationReport.objects.filter(
        billno=billno, inv_id=inv_id
    ).exists()

    return JsonResponse({"exists": exists})