

from django.db import models    
class Prescription1(models.Model):
    patient_name = models.CharField(max_length=100)
    text_content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
