from django.db import models
from django.utils import timezone
from hospApp.models import StateMaster  # assuming same app name


class DistrictMaster(models.Model):
    sno = models.AutoField(primary_key=True)
    district_name = models.CharField(max_length=50, null=True, blank=True)
    state_name = models.ForeignKey(StateMaster, on_delete=models.CASCADE, null=True, blank=True)
    active = models.CharField(max_length=2, null=True, blank=True, default='Y')
    createdby = models.CharField(max_length=50, null=True, blank=True)
    createdtime = models.DateTimeField(default=timezone.now, null=True, blank=True)
    updatedby = models.CharField(max_length=50, null=True, blank=True)
    updatetime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.district_name} ({self.state_name})"
