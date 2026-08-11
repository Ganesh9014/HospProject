from django.db import models
from django.utils import timezone
from hospApp.models import SpecialityMaster


class DoctorMaster(models.Model):
    docid = models.AutoField(primary_key=True)
    docname = models.CharField(max_length=100, null=True, blank=True)
    speciality = models.ForeignKey(
        SpecialityMaster, on_delete=models.SET_NULL,
        null=True, blank=True, db_column='speciality'
    )
    address = models.CharField(max_length=250, null=True, blank=True)
    phoneno = models.CharField(max_length=10, null=True, blank=True)
    consultfee = models.IntegerField(null=True, blank=True)
    revisittime = models.IntegerField(null=True, blank=True)
    ipconsultfee = models.IntegerField(null=True, blank=True)
    emrfee = models.IntegerField(null=True, blank=True)
    active = models.CharField(max_length=2, null=True, blank=True, default='Y')
    createdby = models.CharField(max_length=20, null=True, blank=True)
    createdtime = models.DateTimeField(default=timezone.now)
    updatedby = models.CharField(max_length=20, null=True, blank=True)
    updatedtime = models.DateTimeField(null=True, blank=True)
    qualification=models.CharField(max_length=150, null=True, blank=True)
    regno=models.CharField(max_length=50, null=True, blank=True)    

    class Meta:
        db_table = 'doctor_master'

    def __str__(self):
        return self.docname or ''
