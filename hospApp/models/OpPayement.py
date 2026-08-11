from django.db import models

class OpPayment(models.Model):

    uhid = models.CharField(max_length=50)  # NOT NULL

    num = models.CharField(max_length=50, null=True, blank=True)
    patname = models.CharField(max_length=150, null=True, blank=True)

    age = models.IntegerField(null=True, blank=True)
    agetype = models.CharField(max_length=20, null=True, blank=True)

    gender = models.CharField(max_length=10, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

    billdate = models.DateTimeField(null=True, blank=True)

    totalamt = models.IntegerField(null=True, blank=True)
    paidamt = models.IntegerField(null=True, blank=True)
    balance = models.IntegerField(null=True, blank=True)
    patamt = models.IntegerField(null=True, blank=True)

    userid = models.CharField(max_length=50, null=True, blank=True)
    updatedby = models.CharField(max_length=50, null=True, blank=True)
    updateddate = models.DateTimeField(null=True, blank=True)

    billno = models.IntegerField(null=True, blank=True)
    due = models.IntegerField(null=True, blank=True)
    invbillno = models.IntegerField(null=True, blank=True)

    cardname = models.CharField(max_length=100, null=True, blank=True)
    paymentmode = models.CharField(max_length=20, null=True, blank=True)

    concreason = models.CharField(max_length=50, null=True, blank=True)

    concession = models.IntegerField(null=True, blank=True)
    preconcession = models.IntegerField(null=True, blank=True)

    towords = models.CharField(max_length=30, null=True, blank=True)
    recordno = models.IntegerField(null=True, blank=True)
    active = models.CharField(max_length=1, null=True, blank=True) 
    cash_amt       = models.IntegerField(default=0)
    online_amt     = models.IntegerField(default=0)
    online_mode    = models.CharField(max_length=50,  null=True, blank=True)
    online_details = models.CharField(max_length=100, null=True, blank=True) 
    
    class Meta:
        db_table = "opPayments"   # IMPORTANT for existing table
