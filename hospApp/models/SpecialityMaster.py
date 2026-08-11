from django.db import models
from django.utils import timezone

class SpecialityMaster(models.Model):
    sno = models.AutoField(primary_key=True)
    speciality = models.CharField(max_length=100, null=True, blank=True)
    userid = models.CharField(max_length=50, null=True, blank=True)
    insertedtime = models.DateTimeField(default=timezone.now)
    updatedby = models.CharField(max_length=50, null=True, blank=True)
    updatedtime = models.DateTimeField(null=True, blank=True)
    active = models.CharField(max_length=2, null=True, blank=True, default='Y')

    def __str__(self):
        return self.speciality or ''

    class Meta:
        db_table = 'speciality_master'