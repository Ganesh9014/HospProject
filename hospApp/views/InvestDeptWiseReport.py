


from django.shortcuts import render
from hospApp.models import DepartmentPhotoMaster
from django.contrib.auth.decorators import login_required   
@login_required(login_url='login')
def InvestDeptWiseReport(request):
    department=DepartmentPhotoMaster.objects.filter(active='Y').order_by('department')  
    return render(request, "hospApp/reports/InvestDeptWiseReport.html")




from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from hospApp.models import DepartmentPhotoMaster
from django.utils import timezone


@login_required(login_url='login')
def search_department(request):
    q = request.GET.get("q", "").strip()

    if not q:
        return JsonResponse({"results": []})

    departments = (
        DepartmentPhotoMaster.objects
        .filter(active='Y', department__icontains=q)
        .order_by("department")[:20]
    )

    data = []
    for d in departments:
        data.append({
            "id": d.dno,
            "name": d.department,
            "photo": d.signature.url if d.signature else ""
        })

    return JsonResponse({"results": data})



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from hospApp.models import InvestigationMaster, DepartmentPhotoMaster,HospitalMaster

@login_required(login_url='login')
def InvestDeptWiseReportResult(request):
    dept_id   = request.GET.get("dept_id", "").strip()
    dept_name = request.GET.get("dept_name", "").strip()
    hospital = HospitalMaster.objects.filter(active='a').first()

    investigations = []
    department_obj = None

    total_cost     = 0                          # ← add this

    if dept_id:
        try:
            department_obj = DepartmentPhotoMaster.objects.get(dno=dept_id, active='Y')
            investigations = list(               # ← list() so we can iterate twice
                InvestigationMaster.objects
                .filter(department=department_obj, active='Y')
                .order_by('invname')
            )
            total_cost = sum(i.cost for i in investigations if i.cost)   # ← sum
        except DepartmentPhotoMaster.DoesNotExist:
            department_obj = None
    logged_user = request.session.get("username")
    context = {
        "investigations": investigations,
        "dept_name":       dept_name,
        "department_obj":  department_obj,
        "dept_id":         dept_id,
        "logged_user": logged_user,
        "print_time": timezone.now(),
        'hospital':hospital,
        "total_cost": total_cost
    }
    return render(request, "hospApp/reports/InvestDeptWiseReportResult.html", context)