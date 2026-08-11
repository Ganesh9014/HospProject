import base64
import pytesseract
from PIL import Image
from io import BytesIO
from django.shortcuts import render, redirect
from django.contrib import messages
from hospApp.models import Prescription1    # <-- FIXED

import os

if os.name == 'nt' and os.path.exists(r"C:/Program Files/Tesseract-OCR/tesseract.exe"):
    pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def create_text_from_canvas(request):
    if request.method == "POST":
        patient_name = request.POST.get("patient_name", "").strip()
        image_data = request.POST.get("image", "")

        if not patient_name:
            messages.error(request, "Patient name is required.")
            return redirect("create_text_prescription")

        if not image_data:
            messages.error(request, "No handwriting found.")
            return redirect("create_text_prescription")

        try:
            format, imgstr = image_data.split(';base64,')
            img_bytes = base64.b64decode(imgstr)

            image = Image.open(BytesIO(img_bytes))

            extracted_text = pytesseract.image_to_string(image)

        except Exception as e:
            messages.error(request, f"OCR failed: {e}")
            return redirect("create_text_prescription")

        Prescription1.objects.create(        # <-- FIXED
            patient_name=patient_name,
            text_content=extracted_text
        )

        messages.success(request, "Prescription saved with handwriting extracted.")
        

    return render(request, "hospApp/Admin/Prescription1.html")

def view_prescription1(request, prescription_id):
    prescription = Prescription1.objects.get(id=prescription_id)
    return render(request, "hospApp/Admin/view_prescription1.html", {"prescription": prescription})

