
from django.shortcuts import render
from hospApp.models import CaseTypeMaster,ProMaster
from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def OpModify(request):
    case_types = CaseTypeMaster.objects.filter(active='Y').order_by('casetype')
    pros = ProMaster.objects.filter(active='Y').order_by('pro_name')
    

    context = {
        'case_types': case_types,
        'pros': pros
    }

    return render(request, 'hospApp/frontoffice/OpModify.html', context)

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from hospApp.models import OpPatientRegistration, ProMaster


@login_required(login_url='login')
def get_patient_details_simple(request):
    uhid = request.GET.get('uhid')

    if not uhid:
        return JsonResponse({'success': False, 'error': 'UHID not provided'}, status=400)

    try:
        patient = OpPatientRegistration.objects.get(uhid=uhid)
    except OpPatientRegistration.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No patient found'}, status=404)
    except Exception as ex:
        return JsonResponse({'success': False, 'error': str(ex)}, status=500)

    # ✅ Ref Doctor
    
    refdoctor_obj = patient.refdoctor

    refdoctor_name = refdoctor_obj.docname if refdoctor_obj else ""
    refdoctor_id = refdoctor_obj.docid if refdoctor_obj else ""

    # ✅ PRO
    pro_name = ""
    pro_id = ""

    if patient.pro_id:
        try:
            pro = ProMaster.objects.get(proid=patient.pro_id, active='Y')
            pro_name = pro.pro_name
            pro_id = pro.proid
        except:
            pass

    # ✅ ONLY REGISTRATION DATA
    data = {
        'patname': patient.patname,
        'age': patient.age,
        'agetype': patient.agetype,
        'gender': patient.gender,
        'fname': patient.fname,
        'phone': patient.phone,
        'refdoctor': refdoctor_name,
        'patid': patient.patid,
        'pro_name': pro_name,
        'pro_id': pro_id,
        'refdoctor_id': refdoctor_id,
        'address': patient.address if hasattr(patient, 'address') else ""
    }

    return JsonResponse({'success': True, 'data': data})    

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from hospApp.models import OpPatientRegistration, DoctorConsultation
from hospApp.models import Tbluserpermission
 

from django.http import JsonResponse
from django.utils import timezone
from hospApp.models import Tbluserpermission, OpPatientRegistration, DoctorConsultation

@login_required(login_url='login')
def update_consultation(request):

    if request.method == "POST":

        entered_pass = request.POST.get("usercode", "").strip()
        logged_user = request.session.get("username")

        user = Tbluserpermission.objects.filter(
            username=logged_user,
            isactive=True
        ).first()

        # ❌ INVALID USER CODE
        if not user or entered_pass != user.password:
            return JsonResponse({
                "status": "error",
                "message": "❗ Invalid User Code"
            })

        # ✅ VALID → PROCESS
        uhid = request.POST.get("uhid")
        patient = OpPatientRegistration.objects.filter(uhid=uhid).first()

        if not patient:
            return JsonResponse({
                "status": "error",
                "message": "❗ UHID not found"
            })
        
        gender = request.POST.get("gender", "").strip()

        # -------------------------------
        # SET TITLE FROM GENDER
        # -------------------------------
        if gender == "Male":
            title = "MR"
        elif gender == "Female":
            title = "MRS"
        else:
            title = ""

        # ---- update registration ----
        patient.patname = request.POST.get("patname")
        patient.age = request.POST.get("age")
        patient.agetype = request.POST.get("agetype")
        patient.gender = request.POST.get("gender")
        patient.phone = request.POST.get("phone")
        patient.address = request.POST.get("address")
        patient.fname = request.POST.get("fname")
        patient.updatedtime = timezone.now()
        patient.pro_id = request.POST.get("pro_id")
        patient.title = title 
        patient.refdoctor_id = request.POST.get("refdoctor_id")
        patient.save()

        # ---- update consultation ----
        consultation = DoctorConsultation.objects.filter(uhid=uhid).first()

        if consultation:
            consultation.patname = patient.patname
            consultation.age = patient.age
            consultation.agetype = patient.agetype
            consultation.gender = patient.gender
            consultation.phone = patient.phone
            consultation.address = patient.address
            consultation.gardian = patient.fname
          

            consultation.promaster_id = request.POST.get("pro_id")
            consultation.refdoctor_id = request.POST.get("refdoctor_id")
            consultation.save()

        return JsonResponse({
            "status": "success",
            "message": "✅ Updated successfully"
        })

    return JsonResponse({"status": "error", "message": "Invalid request"})
from hospApp.models import RefDoctorMaster
@login_required(login_url='login')
def suggest_refdoctors1(request):
    query = request.GET.get('term', '').strip()
    results = []

    if query:
        docs = RefDoctorMaster.objects.filter(
            docname__icontains=query,
            active='Y'
        )[:10]

        results = [
            {
                "id": d.docid,
                "name": d.docname
            }
            for d in docs
        ]

    return JsonResponse(results, safe=False)