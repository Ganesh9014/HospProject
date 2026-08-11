from django.db import models

class BankMaster(models.Model):
    sno = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, null=True, blank=True)
    createddate = models.DateTimeField(null=True, blank=True)
    createdby = models.CharField(max_length=20, null=True, blank=True)
    active = models.CharField(max_length=1, null=True, blank=True, default='Y')

    class Meta:
        db_table = 'BankMaster'

    def __str__(self):
        return self.name or ""
