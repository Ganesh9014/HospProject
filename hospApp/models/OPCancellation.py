from django.db import models

class TblOpCancellation(models.Model):
    uhid = models.CharField(max_length=50)
    billno = models.IntegerField()
    billdate = models.DateTimeField(null=True, blank=True)

    patname = models.CharField(max_length=150, null=True, blank=True)
    opno = models.CharField(max_length=1, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)

    address = models.CharField(max_length=150, null=True, blank=True)
    phoneno = models.CharField(max_length=20, null=True, blank=True)

    floorid = models.CharField(max_length=20, null=True, blank=True)
    roomid = models.CharField(max_length=20, null=True, blank=True)
    bedid = models.CharField(max_length=20, null=True, blank=True)

    totalamt = models.IntegerField()

    Reason = models.CharField(max_length=150, null=True, blank=True)
    userid = models.CharField(max_length=50)

    createddate = models.DateTimeField(null=True, blank=True)
    regdate = models.CharField(max_length=30, null=True, blank=True)
    type = models.CharField(max_length=20, null=True, blank=True)

    concessionamt = models.IntegerField(null=True, blank=True)
    amtpaid = models.IntegerField(null=True, blank=True)
    refundamt = models.IntegerField(null=True, blank=True)
    bal = models.IntegerField(null=True, blank=True)

    createdby = models.CharField(max_length=40, null=True, blank=True)

    class Meta:
        db_table = 'tblOpCancellation'

    def __str__(self):
        return f"{self.uhid} - {self.billno}"
