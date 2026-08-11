from django.db import models
from django.utils import timezone
from hospApp.models import SpecialityMaster
class RefDoctorMaster(models.Model):
    docid = models.AutoField(primary_key=True)
    docname = models.CharField(max_length=50, null=True, blank=True)
    specialized = models.ForeignKey(SpecialityMaster, on_delete=models.SET_NULL, null=True, blank=True)
    phoneno = models.CharField(max_length=50, null=True, blank=True)
    active = models.CharField(max_length=1, default='Y')
    createdby = models.CharField(max_length=50, null=True, blank=True)
    createdtime = models.DateTimeField(default=timezone.now, null=True, blank=True)
    updatedby = models.CharField(max_length=50, null=True, blank=True)
    updatedtime = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'refdoc_master'

    def __str__(self):
        return self.docname or ''
