# hospApp/models.py
from django.db import models

class FullPrescription(models.Model):
    patient_name = models.CharField(max_length=100)
    
    # Main typed prescription text
    typed_text = models.TextField(blank=True)
    
    # Optional audio file + its transcription
    audio = models.FileField(upload_to='prescriptions/audio/', blank=True, null=True)
    audio_text = models.TextField(blank=True)
    
    # Optional handwritten / drawn image of prescription
    image = models.ImageField(upload_to='prescriptions/images/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.patient_name} ({self.id})"
