# # hospApp/views.py
# from django.shortcuts import render, redirect, get_object_or_404
# from django.http import JsonResponse, HttpResponseForbidden
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib import messages
# from hospApp.models import Prescription3, Prescription
# from hospApp.models import DoctorConsultation

# def create_audio_prescription_ajax(request):
#     # Accept only POST from authenticated users (you can apply @login_required)
#     if request.method != "POST":
#         return JsonResponse({"status":"error", "message":"Invalid method"}, status=405)

#     # CSRF is required (we will send token from client). If you want to exempt, use @csrf_exempt (not recommended).
#     consult_id = request.POST.get("consult_id")  # hidden field in the form
#     patient_name = request.POST.get("patient_name", "").strip()
#     audio_text = request.POST.get("audio_text", "").strip()
#     audio_file = request.FILES.get("audio")

#     if not patient_name:
#         return JsonResponse({"status":"error","message":"Patient name required"}, status=400)

#     if not audio_text and not audio_file:
#         return JsonResponse({"status":"error","message":"Provide audio or transcription"}, status=400)

#     consult = None
#     if consult_id:
#         try:
#             consult = DoctorConsultation.objects.get(pk=int(consult_id))
#         except DoctorConsultation.DoesNotExist:
#             consult = None

#     # Save the Prescription3
#     pres = Prescription3.objects.create(
#         consult=consult,
#         patient_name=patient_name,
#         audio=audio_file if audio_file else None,
#         audio_text=audio_text if audio_text else None
#     )

#     # Return JSON with ids for opener to update
#     return JsonResponse({
#         "status": "success",
#         "prescription3_id": pres.id,
#         "consult_id": consult.id if consult else None,
#     })


# def print_audio_prescription(request, pres_id):
#     pres = get_object_or_404(Prescription3, pk=pres_id)
#     # Render a simple print-friendly page using pres.audio_text and link to audio file
#     return render(request, "hospApp/admin/print_audio_prescription.html", {"pres": pres})
