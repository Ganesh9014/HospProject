
from django.http import JsonResponse    
from django.contrib.auth.decorators import login_required
from hospApp.models.InvestigationMaster import InvestigationMaster
from hospApp.models.InvestigationDetails import tblInvestigationDetails 

from hospApp.models.InvestigationDetails import tblInvestigationDetails
from hospApp.models.InvestigationMaster import InvestigationMaster  
from hospApp.models.InvestigationReport import InvestigationReport  
from django.shortcuts import render 

@login_required(login_url='login')
def Modifylab(request):
    return render(request, 'hospApp/Lab/Modifylab.html')    
@login_required(login_url='login')
def get_investigations_with_date(request):
    billno = request.GET.get('billno')

    if not billno:
        return JsonResponse({'status': 'invalid'})

    inv_rows = tblInvestigationDetails.objects.filter(
        billno=billno,
        active="Y"
    ).values(
        'invname',
        'generateddate'   # ✅ IMPORTANT CHANGE
    )

    inv_ids = [row['invname'] for row in inv_rows if row['invname']]

    masters = InvestigationMaster.objects.filter(
        ino__in=inv_ids
    ).values('ino', 'invname')

    master_map = {
        str(m['ino']): m['invname']
        for m in masters
    }

    from django.utils import timezone

    inv_data = []
    for row in inv_rows:

        if row['generateddate']:
            local_dt = timezone.localtime(row['generateddate'])
            formatted_date = local_dt.strftime("%d-%m-%Y %H:%M")
        else:
            formatted_date = ""

        inv_data.append({
            'inv_master_id': row['invname'],
            'inv_name': master_map.get(str(row['invname']), row['invname']),
            'generateddate': formatted_date
        })

    return JsonResponse({'data': inv_data})
@login_required(login_url='login')
def get_existing_report(request):
    billno = request.GET.get("billno")
    inv_id = request.GET.get("inv_id")

    # ── Pull patient gender/age to compute the correct low/high ranges ──────
    from hospApp.models import OpPatientRegistration
    from hospApp.models.NewInvMaster import NewInvMaster

    gender  = ""
    age     = 0
    agetype = ""
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

    # ── Build a lookup from test name → NewInvMaster row ───────────────────
    nim_rows = NewInvMaster.objects.filter(invname=inv_id).values(
        'test', 'result_type', 'male_low', 'male_high',
        'female_low', 'female_high', 'child_low', 'child_high',
        'child_age_cutoff', 'abnormal_values'
    )
    nim_map = {r['test']: r for r in nim_rows}

    # ── Saved report rows ───────────────────────────────────────────────────
    report_rows = InvestigationReport.objects.filter(
        billno=billno,
        inv_id=inv_id,
        is_active=True
    ).values(
        'test', 'result', 'units', 'normal',
        'header', 'method', 'submethod', 'is_check', 'impression'
    )

    enriched = []
    for row in report_rows:
        nim = nim_map.get(row['test'], {})
        result_type     = nim.get('result_type') or 'numeric'
        low = high      = None
        abnormal_values = []

        if result_type == 'numeric':
            if is_child(nim.get('child_age_cutoff')) and nim.get('child_low') is not None:
                low, high = nim['child_low'], nim['child_high']
            elif gender in ('m', 'male') and nim.get('male_low') is not None:
                low, high = nim['male_low'], nim['male_high']
            elif gender in ('f', 'female') and nim.get('female_low') is not None:
                low, high = nim['female_low'], nim['female_high']
            else:
                low  = nim.get('male_low')  or nim.get('female_low')  or nim.get('child_low')
                high = nim.get('male_high') or nim.get('female_high') or nim.get('child_high')

        elif result_type == 'text_choice' and nim.get('abnormal_values'):
            abnormal_values = [v.strip().lower() for v in nim['abnormal_values'].split(',') if v.strip()]

        enriched.append({
            **row,
            'result_type':     result_type,
            'low':             low,
            'high':            high,
            'abnormal_values': abnormal_values,
        })

    dept_id      = None
    is_radiology = False
    try:
        from hospApp.models import DepartmentPhotoMaster
        inv_master = InvestigationMaster.objects.filter(ino=inv_id).first()
        if inv_master and inv_master.department:
            dept = DepartmentPhotoMaster.objects.filter(
                department=inv_master.department
            ).first()
            dept_id      = dept.dno if dept else None
            is_radiology = "radiology" in (dept.department.lower() if dept else "")
    except Exception:
        pass

    return JsonResponse({
        'data':          enriched,
        'department_id': dept_id,
        'is_radiology':  is_radiology,
    })
@login_required(login_url='login')
def ReportsPage(request):
    return render(request, 'hospApp/Lab/ReportsPage.html')    

@login_required(login_url='login')
def get_completed_investigations(request):
    billno = request.GET.get('billno')

    if not billno:
        return JsonResponse({'status': 'invalid'})

    from hospApp.models import InvestigationReport
    from django.utils import timezone

    # ✅ ONLY completed reports
    valid_inv_ids = InvestigationReport.objects.filter(
        billno=billno,
        is_active=True
    ).values_list("inv_id", flat=True)

    inv_rows = tblInvestigationDetails.objects.filter(
        billno=billno,
        active="Y",
        invname__in=valid_inv_ids
    ).values(
        'invname',
        'generateddate'
    )

    inv_ids = [row['invname'] for row in inv_rows if row['invname']]

    masters = InvestigationMaster.objects.filter(
        ino__in=inv_ids
    ).values('ino', 'invname')

    master_map = {
        str(m['ino']): m['invname']
        for m in masters
    }

    inv_data = []
    for row in inv_rows:

        if row['generateddate']:
            local_dt = timezone.localtime(row['generateddate'])
            formatted_date = local_dt.strftime("%d-%m-%Y %H:%M")
        else:
            formatted_date = ""

        inv_data.append({
            'inv_master_id': row['invname'],
            'inv_name': master_map.get(str(row['invname']), row['invname']),
            'generateddate': formatted_date
        })

    return JsonResponse({'data': inv_data})