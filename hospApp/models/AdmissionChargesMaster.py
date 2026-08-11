
from django.db import models
from django.utils import timezone
class Report(models.Model):
    reportid = models.AutoField(primary_key=True)
    rptname = models.CharField(max_length=40, null=True, blank=True)
    cost = models.IntegerField(null=True, blank=True)
    active = models.CharField(max_length=2, null=True, blank=True)
    userid = models.CharField(max_length=20, null=True, blank=True)
    createddate = models.DateTimeField(null=True, blank=True)
    updatedby = models.CharField(max_length=20, null=True, blank=True)
    updateddate = models.DateTimeField(null=True, blank=True)

    class Meta:
        
        db_table = "tblReport"

    def __str__(self):
        return self.rptname if self.rptname else str(self.reportid)
