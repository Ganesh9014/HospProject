
from django.db import models

class InvestigationMaster(models.Model):
    ino = models.AutoField(primary_key=True)

    invname = models.CharField(max_length=150, null=True, blank=True)

    department = models.ForeignKey(
        'hospApp.DepartmentPhotoMaster',
        on_delete=models.CASCADE
    )

    groups = models.CharField(max_length=30, null=True, blank=True)

    cost = models.IntegerField(null=True, blank=True)
    ip = models.IntegerField(null=True, blank=True)

    active = models.CharField(max_length=10, default='Y', null=True, blank=True)

    createdby = models.CharField(max_length=50, null=True, blank=True)
    createddate = models.DateTimeField(null=True, blank=True)
    updatedby = models.CharField(max_length=50, null=True, blank=True)
    updateddate = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "investigation_master"