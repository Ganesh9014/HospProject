from django.db import models

class tblInvestigationDetails(models.Model):
    uhid = models.CharField(max_length=50)
    invname = models.CharField(max_length=150, null=True, blank=True)
    cost = models.IntegerField(null=True, blank=True)
    generateddate = models.DateTimeField(auto_now_add=True)

    createdby = models.CharField(max_length=50, null=True, blank=True)
    updatedby = models.CharField(max_length=50, null=True, blank=True)
    updatedtime = models.DateTimeField(null=True, blank=True)
    billno = models.IntegerField(null=True, blank=True)
    ipno = models.CharField(max_length=20, null=True, blank=True)
    patname = models.CharField(max_length=150, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    agetype = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    doc = models.CharField(max_length=100, null=True, blank=True)
    refdoc = models.CharField(max_length=100, null=True, blank=True)

    ID_PK = models.AutoField(primary_key=True)

    type = models.CharField(max_length=30, null=True, blank=True)
    concessionamt = models.IntegerField(null=True, blank=True)
    concreason = models.CharField(max_length=150, null=True, blank=True)
    paidamt = models.IntegerField(null=True, blank=True)
    due = models.IntegerField(null=True, blank=True)
    refundate = models.DateTimeField(null=True, blank=True)
    refund = models.CharField(max_length=2, null=True, blank=True)
    paymentmode = models.CharField(max_length=20, null=True, blank=True)
    cardname = models.CharField(max_length=100, null=True, blank=True)
    active = models.CharField(max_length=1, null=True, blank=True)
    cancelreson = models.CharField(max_length=30, null=True, blank=True)
    dept = models.CharField(max_length=20, null=True, blank=True)
    phone=models.BigIntegerField(null=True, blank=True) 
    doctor=models.CharField(max_length=100, null=True, blank=True)
    cash_amt       = models.IntegerField(default=0)
    online_amt     = models.IntegerField(default=0)
    online_mode    = models.CharField(max_length=50,  null=True, blank=True)
    online_details = models.CharField(max_length=100, null=True, blank=True)
    class Meta:
        db_table = 'tblInvestigationDetails'  # Use exact same SQL table name
