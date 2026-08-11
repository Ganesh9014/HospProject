from django.db import models
from hospApp.models import DoctorMaster
class TblServices(models.Model):
    id = models.AutoField(db_column='ID_PK', primary_key=True)

    uhid = models.CharField(max_length=20)
    services = models.CharField(max_length=100)
    services_typename = models.CharField(max_length=100, null=True, blank=True)

    amount = models.IntegerField(null=True, blank=True)

    generateddate = models.DateTimeField(null=True, blank=True)
    generatedtime = models.DateTimeField(null=True, blank=True)

    createdby = models.CharField(max_length=50, null=True, blank=True)
    createddate = models.DateTimeField(null=True, blank=True)

    updatedby = models.CharField(max_length=100, null=True, blank=True)
    updateddate = models.DateTimeField(null=True, blank=True)

    billno = models.IntegerField(null=True, blank=True)

    pattype = models.CharField(max_length=15, null=True, blank=True)
    type = models.CharField(max_length=20, null=True, blank=True)

    concessionamt = models.IntegerField(null=True, blank=True)
    concreason = models.CharField(max_length=150, null=True, blank=True)

    paidamt = models.IntegerField(null=True, blank=True)
    due = models.IntegerField(null=True, blank=True)
    qty = models.IntegerField(null=True, blank=True)

    ipno = models.CharField(max_length=20, null=True, blank=True)

    isactive = models.CharField(max_length=1, null=True, blank=True)

    cardname = models.CharField(max_length=100, null=True, blank=True)
    paymentmode = models.CharField(max_length=20, null=True, blank=True)
    doctor=models.CharField(max_length=100, null=True, blank=True)
    doc = models.ForeignKey(
        DoctorMaster,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    cash_amt       = models.IntegerField(default=0)
    online_amt     = models.IntegerField(default=0)
    online_mode    = models.CharField(max_length=50,  null=True, blank=True)
    online_details = models.CharField(max_length=100, null=True, blank=True)


    class Meta:
        db_table = 'tblservices'
