from django.db import models
from django.utils import timezone

class HospitalMaster(models.Model):
    sno = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    createdby = models.CharField(max_length=20, null=True, blank=True)
    creaddate = models.DateTimeField(default=timezone.now, null=True, blank=True)
    updatedby = models.CharField(max_length=20, null=True, blank=True)
    updatedtime = models.DateTimeField(null=True, blank=True)
    active = models.CharField(max_length=5, null=True, blank=True)
    initial = models.CharField(max_length=10, null=True, blank=True)
    header = models.CharField(max_length=1, null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    email = models.CharField(max_length=40, null=True, blank=True)
    img = models.CharField(max_length=1, null=True, blank=True)

    class Meta:
        db_table = 'hospital_Master'  

    def __str__(self):
        return self.name or f"Record #{self.sno}"
