
from django.db import models    

class Prescription3(models.Model):
    patient_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='prescriptions/', null=True, blank=True)
    audio = models.FileField(upload_to='audio_prescriptions/', null=True, blank=True)
    audio_text = models.TextField(null=True, blank=True)
   

    consult = models.ForeignKey(
        'DoctorConsultation',
        related_name='audio_prescriptions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    temp = models.CharField(max_length=20, null=True, blank=True)
    bp = models.CharField(max_length=20, null=True, blank=True)
    pr = models.CharField(max_length=20, null=True, blank=True)
    spo2 = models.CharField(max_length=20, null=True, blank=True)
    weight = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    next_visit_date = models.DateField(null=True, blank=True)

    



        