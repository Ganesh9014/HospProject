from django.db import models
from django.utils import timezone

class ServiceTypeMaster(models.Model):
    serviceid = models.AutoField(primary_key=True)
    servicename = models.CharField(max_length=150, null=True, blank=True)
    servicetypename = models.CharField(max_length=150, null=True, blank=True)
    servicecode = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    charge = models.IntegerField(null=True, blank=True)
    labservices = models.CharField(max_length=100, null=True, blank=True)
    active = models.CharField(max_length=1, default='Y')
    createdby = models.CharField(max_length=50, null=True, blank=True)
    createdtime = models.DateTimeField(default=timezone.now)
    updatedby = models.CharField(max_length=50, null=True, blank=True)
    updatedtime = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'service_type_master'

    def __str__(self):
        return self.servicename or ''
