from django.shortcuts import render 
from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def InvestigationDetailsMaster(request):
    return render(request, 'hospApp/Admin/InvestigationDetailsMaster.html')   
# views.py
from django.http import JsonResponse
from hospApp.models import NewInvMaster, InvestigationMaster



@login_required(login_url='login')
def get_investigation_details(request):
    inv_id = request.GET.get("inv_id")

    tests = (
        NewInvMaster.objects
        .filter(invname=inv_id)
        .values("sno", "test", "normal", "units", "header", "method")
        .order_by("sno")
    )

    return JsonResponse({
        "tests": list(tests)
    })
