
from django.db import models    
from hospApp.models.DoctorConsultation import DoctorConsultation
class PatientVitals(models.Model):
    consultation = models.OneToOneField(
        DoctorConsultation,
        on_delete=models.CASCADE,
        related_name='vitals'
    )

    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    bp = models.CharField(max_length=10, null=True, blank=True)
    pulse = models.IntegerField(null=True, blank=True)
    spo2 = models.IntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
