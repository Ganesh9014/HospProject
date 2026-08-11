from django.db import models
from django.utils import timezone

class CaseTypeMaster(models.Model):
    sno = models.AutoField(primary_key=True)
    casetype = models.CharField(max_length=100, null=True, blank=True)
    active = models.CharField(max_length=2, null=True, blank=True, default='Y')
    createdby = models.CharField(max_length=50, null=True, blank=True)
    createdtime = models.DateTimeField(default=timezone.now)
    updatedby = models.CharField(max_length=50, null=True, blank=True)
    updatedtime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.casetype or ''

    class Meta:
        db_table = 'case_type_master'
