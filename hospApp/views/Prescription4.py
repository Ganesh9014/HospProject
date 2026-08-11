import base64
import uuid
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from hospApp.models import FullPrescription
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def create_full_prescription(request):
    """
    Single page to create a prescription consisting of:
     - patient name
     - optional audio recording (saved) + browser-side transcription (saved)
     - optional handwritten/drawn canvas (saved as image)
    """
    if request.method == "POST":
        patient_name = request.POST.get("patient_name", "").strip()
        audio_file = request.FILES.get("audio")
        audio_text = request.POST.get("audio_text", "").strip()
        image_data = request.POST.get("image", "").strip()  # base64 dataURL or empty

        if not patient_name:
            messages.error(request, "Patient name is required.")
            return redirect(reverse("create_full_prescription"))

        presc = FullPrescription(patient_name=patient_name, audio_text=audio_text or "")

        if audio_file:
            presc.audio = audio_file

        # Save canvas image if present (data URL)
        if image_data and image_data.startswith("data:"):
            try:
                header, imgstr = image_data.split(";base64,")
                ext = header.split("/")[-1]
                filename = f"{uuid.uuid4()}.{ext}"
                presc.image = ContentFile(base64.b64decode(imgstr), name=filename)
            except Exception:
                # don't block save if image fails; notify user
                messages.warning(request, "Handwritten image could not be decoded. Image not saved.")

        presc.save()
        messages.success(request, "Prescription saved.")
        return redirect(reverse("view_full_prescription", args=[presc.id]))

    return render(request, "hospApp/Admin/prescription_full.html")


@login_required(login_url='login')
def view_full_prescription(request, prescription_id):
    presc = get_object_or_404(FullPrescription, id=prescription_id)
    return render(request, "hospApp/Admin/view_full_prescription.html", {"prescription": presc})