import base64, uuid
from django.core.files.base import ContentFile
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from hospApp.models import Prescription, Prescription3, DoctorConsultation, OpPatientRegistration,DoctorMaster,PatientVitals,HospitalMaster

from django.shortcuts import redirect
# ===================== WRITING PRESCRIPTION =====================
from django.contrib.auth.decorators import login_required
# views/create_prescription.py
from hospApp.services.handwriting import recognize_handwriting
@login_required(login_url='login')
def create_prescription(request):
    hospital = HospitalMaster.objects.filter(active='a').first()

    # ✅ GET consult_id safely from BOTH GET and POST
    consult_id = request.GET.get("consult_id") or request.POST.get("consult_id")

    if not consult_id:
        return render(request, "hospApp/Admin/error.html", {
            "error": "Consultation ID missing. Please select patient again."
        })

    consult = get_object_or_404(DoctorConsultation, id=consult_id)

    if request.method == "POST":
        patient_name = request.POST.get("patient_name")
        image_data = request.POST.get("image")
        stroke_data = request.POST.get("stroke_data")
        recognized_text = request.POST.get("recognized_text", "").strip() or None
        if not recognized_text and stroke_data:
            recognized_text = recognize_handwriting(stroke_data_json=stroke_data)

        uhid = request.POST.get("uhid")
        patid = request.POST.get("patid")
        TEMP=request.POST.get("temp")   
        BP=request.POST.get("bp")
        PR=request.POST.get("pr")
        SPO2=request.POST.get("spo2")
        WEIGHT=request.POST.get("weight")

        if not image_data:
            return render(request, "hospApp/Admin/prescription.html", {
                "consult": consult,
                "error": "Prescription image is missing."
            })

        try:
            format, imgstr = image_data.split(';base64,')
        except ValueError:
            return render(request, "hospApp/Admin/prescription.html", {
                "consult": consult,
                "error": "Invalid image format."
            })

        ext = format.split('/')[-1]
        file_name = f"{uuid.uuid4()}.{ext}"
        file = ContentFile(base64.b64decode(imgstr), name=file_name)
             

        new_obj = Prescription.objects.create(
            patient_name=patient_name,
            image=file,
            uhid=uhid,
            patid=patid,
            consult=consult,
            stroke_data=stroke_data,

            # ✅ SAVE VITALS HERE
            temp=request.POST.get("temp"),
            bp=request.POST.get("bp"),
            pr=request.POST.get("pr"),
            spo2=request.POST.get("spo2"),
            weight=request.POST.get("weight"),
            recognized_text=recognized_text,

            # ✅ SAVE NEXT VISIT DATE
            next_visit_date=request.POST.get("next_visit_date") or None,
        )


        return JsonResponse({
            "status": "success",
            "print_url": reverse("print_prescription", args=[new_obj.id]),
            "recognized_text": recognized_text,
        })
    vitals = PatientVitals.objects.filter(consultation=consult).first()
    return render(request, "hospApp/Admin/prescription.html", {
        "consult": consult,
        "vitals": vitals,
              
    })

 
from django.shortcuts import get_object_or_404


@login_required(login_url='login')
def print_prescription(request, prescription_id):
    hospital = HospitalMaster.objects.filter(active='a').first()

    prescription = get_object_or_404(Prescription, id=prescription_id)

    patient = get_object_or_404(
        OpPatientRegistration,
        uhid=prescription.uhid
    )

    consult = prescription.consult

    doctor = get_object_or_404(
        DoctorMaster,
        docid=consult.doctor_id,
        active='Y'
    )

    consult.is_prescription_done = True
    consult.save()
    valid_upto = prescription.created_at + timedelta(days=7)
    return render(
        request,
        "hospApp/Admin/prescription_print.html",
        {
            "prescription": prescription,
            "patient": patient,
            "doctor": doctor,
            "consult": consult,
            "hospital": hospital  ,
            'valid_upto':valid_upto
        }
    )
# ===================== AUDIO PRESCRIPTION =====================
from django.utils import timezone

@login_required(login_url='login')
def create_audio_prescription_ajax(request):
    hospital=HospitalMaster.objects.filter(active='a').first()
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request"}, status=405)

    consult_id = request.POST.get("consult_id")
    patient_name = request.POST.get("patient_name", "").strip()
    audio_text = request.POST.get("audio_text", "").strip()
    audio_file = request.FILES.get("audio")

    if not consult_id:
        return JsonResponse({
            "status": "error",
            "message": "Consultation ID missing"
        }, status=400)

    consult = get_object_or_404(DoctorConsultation, id=consult_id)

    if not audio_text and not audio_file:
        return JsonResponse({
            "status": "error",
            "message": "Please record audio or enter text"
        }, status=400)

    pres = Prescription3.objects.create(
        consult=consult,
        patient_name=patient_name,
        audio_text=audio_text if audio_text else None,
        audio=audio_file if audio_file else None,
        created_at=timezone.now(),

        # ✅ SAVE VITALS HERE
        temp=request.POST.get("temp_hidden"),
        bp=request.POST.get("bp_hidden"),
        pr=request.POST.get("pr_hidden"),
        spo2=request.POST.get("spo2_hidden"),
        weight=request.POST.get("weight_hidden"),

        # ✅ SAVE NEXT VISIT DATE
        next_visit_date=request.POST.get("next_visit_date") or None,
    )



    return JsonResponse({
        "status": "success",
        
        "print_url": reverse("print_audio_prescription", args=[pres.id])
    })

from datetime import timedelta


@login_required(login_url='login')
def print_audio_prescription(request, pres_id):
    hospital=HospitalMaster.objects.filter(active='a').first()

    pres = get_object_or_404(Prescription3, id=pres_id)
    # docconsult=get_object_or_404(DoctorConsultation,id=pres.consult_id) 
    consult = pres.consult   # ✅ correct link
    doctor = get_object_or_404(
        DoctorMaster,
        docid=consult.doctor_id,
        active='Y'
    )
    consult.is_prescription_done = True
    consult.save()

    patient = get_object_or_404(OpPatientRegistration, uhid=consult.uhid)
    valid_upto = consult.regdt + timedelta(days=7)

    return render(request, "hospApp/Admin/print_audio_prescription.html", {
        "pres": pres,
        "patient": patient,
        "prescription": pres,
        "doctor": doctor,
        'hospital':hospital,
        "consult": consult  ,
        'valid_upto':valid_upto
    })

@login_required(login_url='login')
def revisit_prescription(request, consult_id):

    consult = get_object_or_404(DoctorConsultation, id=consult_id)
    prescription = Prescription.objects.filter(consult=consult).last()

    if not prescription:
        return render(request, "hospApp/Admin/error.html", {
            "error": "No prescription found for this consultation"
        })

    if request.method == "POST":

        # ✅ UPDATE STROKES (for editing)
        stroke_data = request.POST.get("stroke_data")
        if stroke_data:
            prescription.stroke_data = stroke_data

        # ✅ UPDATE IMAGE (IF RE-DRAWN)
        image_data = request.POST.get("image")
        if image_data:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            file_name = f"{uuid.uuid4()}.{ext}"
            prescription.image = ContentFile(
                base64.b64decode(imgstr),
                name=file_name
            )


        # ✅ ONLY UPDATE VITALS IF VALUE PRESENT
        for field in ["temp", "bp", "pr", "spo2", "weight"]:
            val = request.POST.get(field, "").strip()
            if val != "":          # only overwrite if user actually sent something
                setattr(prescription, field, val)

        prescription.save()

        consult.is_revisit = True
        consult.save()

        return JsonResponse({
            "status": "success",
            "print_url": reverse("print_prescription", args=[prescription.id])
        })
    valid_upto = prescription.updated_at + timedelta(days=7)

    return render(request, "hospApp/Admin/revisit_prescription.html", {
        "consult": consult,
        "prescription": prescription,
        'valid_upto':valid_upto
    })


@login_required(login_url='login')
def revisit_audio_prescription(request, consult_id):

    consult = get_object_or_404(DoctorConsultation, id=consult_id)
    pres = Prescription3.objects.filter(consult=consult).last()

    if not pres:
        return render(request, "hospApp/Admin/error.html", {
            "error": "No audio prescription found"
        })

    if request.method == "POST":

        # ✅ ✅ ✅ APPEND OLD + NEW AUDIO TEXT
        new_audio_text = request.POST.get("audio_text", "").strip()

        if new_audio_text:
            if pres.audio_text:
                pres.audio_text = pres.audio_text.strip() + "\n" + new_audio_text
            else:
                pres.audio_text = new_audio_text

        # ✅ UPDATE AUDIO FILE (OPTIONAL)
        audio_file = request.FILES.get("audio")
        if audio_file:
            pres.audio = audio_file

        # ✅ UPDATE VITALS
        pres.temp = request.POST.get("temp")
        pres.bp = request.POST.get("bp")
        pres.pr = request.POST.get("pr")
        pres.spo2 = request.POST.get("spo2")
        pres.weight = request.POST.get("weight")

        pres.save()

        consult.is_revisit = True
        consult.save()

        return JsonResponse({
            "status": "success",
            "print_url": reverse("print_audio_prescription", args=[pres.id])
        })
    

    return render(request, "hospApp/Admin/revisit_audio.html", {
        "pres": pres,
        "consult": consult
    })

@login_required(login_url='login')
def smart_revisit_redirect(request, consult_id):

    consult = get_object_or_404(DoctorConsultation, id=consult_id)

    # ✅ Check which prescription exists
    image_pres = Prescription.objects.filter(consult=consult).exists()
    audio_pres = Prescription3.objects.filter(consult=consult).exists()

    if image_pres:
        return redirect("revisit_prescription", consult_id=consult.id)

    if audio_pres:
        return redirect("revisit_audio_prescription", consult_id=consult.id)

    return render(request, "hospApp/Admin/error.html", {
        "error": "No prescription found for revisit."
    })
@login_required(login_url='login')
def previous_prescription_view(request, pk):
    consult = get_object_or_404(DoctorConsultation, pk=pk)

    # No previous consultation linked
    if not consult.previous_consult:
        return redirect("SearchConsultationUHIDView1")  # or show safe message

    prev = consult.previous_consult

    # 1️⃣ CHECK WRITTEN PRESCRIPTION
    written = Prescription.objects.filter(consult=prev).first()
    if written:
        return redirect("print_prescription", prescription_id=written.id)

    # 2️⃣ CHECK AUDIO PRESCRIPTION
    audio = Prescription3.objects.filter(consult=prev).first()
    if audio:
        return redirect("print_audio_prescription", pres_id=audio.id)

    # 3️⃣ IF NOTHING FOUND
    return redirect("SearchConsultationUHIDView1")


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required(login_url='login')
def recognize_handwriting_ajax(request):
    if request.method == "POST":
        stroke_data = request.POST.get("stroke_data")
        if stroke_data:
            result = recognize_handwriting(stroke_data_json=stroke_data)
            if result:
                return JsonResponse({
                    "status": "success",
                    "recognized_text": result.get("full_text", ""),
                    "lines": result.get("lines", [])   # list of {text, x, y, width, height}
                })
        return JsonResponse({"status": "success", "recognized_text": "", "lines": []})
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
