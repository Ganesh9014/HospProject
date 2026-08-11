

from django.shortcuts import render    
from hospApp.models import OpPatientRegistration , CaseTypeMaster, ProMaster    
from django.http import JsonResponse
from hospApp.models import DoctorMaster
from django.db.models import Q
from django.contrib.auth.decorators import login_required   

@login_required(login_url='login')
def IpRegistrationView(request):
    uhid = request.GET.get("uhid")
    case_types = CaseTypeMaster.objects.filter(active='Y').order_by('casetype')
    pro_list = ProMaster.objects.filter(active='Y').order_by('pro_name')
    patient = None
    
    if uhid:
        patient = OpPatientRegistration.objects.filter(uhid=uhid).first()

    return render(request, "HospApp/Admin/IpRegistration.html", {"patient": patient, "case_types": case_types, "pro_list": pro_list })



@login_required(login_url='login')
def search_doctors1(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        doctors = DoctorMaster.objects.filter(
            Q(docname__icontains=query),
            active='Y'
        ).order_by('docname')[:10]
        for d in doctors:
            results.append({'name': d.docname})
    return JsonResponse({'results': results})
