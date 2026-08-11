from django.db import models

class Prescription(models.Model):
    patient_name = models.CharField(max_length=200)
    patid = models.CharField(max_length=50, blank=True, null=True)
    uhid = models.CharField(max_length=50, blank=True, null=True)

    consult = models.ForeignKey(
        'DoctorConsultation',
        related_name='prescriptions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    stroke_data = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='prescriptions/')

    # ✅ VITALS
    temp = models.CharField(max_length=20, null=True, blank=True)
    bp = models.CharField(max_length=20, null=True, blank=True)
    pr = models.CharField(max_length=20, null=True, blank=True)
    spo2 = models.CharField(max_length=20, null=True, blank=True)
    weight = models.CharField(max_length=20, null=True, blank=True)

    # ✅ TIMESTAMPS (CORRECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    recognized_text = models.TextField(blank=True, null=True)
    next_visit_date = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.patient_name
