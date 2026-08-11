from django.db import models


class TblRefund(models.Model):
    uhid = models.CharField(
        db_column='uhid',
        max_length=20,
        null=False,
        blank=False
    )
    patno = models.CharField(
        db_column='patno',
        max_length=10,
        null=True,
        blank=True
    )
    patname = models.CharField(
        db_column='patname',
        max_length=50,
        null=True,
        blank=True
    )
    billno = models.IntegerField(
        db_column='billno',
        null=True,
        blank=True
    )
    billtime = models.DateTimeField(
        db_column='billtime',
        null=True,
        blank=True
    )
    totalamt = models.IntegerField(
        db_column='totalamt',
        null=True,
        blank=True
    )
    refund = models.IntegerField(
        db_column='refund',
        null=True,
        blank=True
    )
    amtpaid = models.IntegerField(
        db_column='amtpaid',
        null=True,
        blank=True
    )
    balance = models.IntegerField(
        db_column='balance',
        null=True,
        blank=True
    )
    reason = models.CharField(
        db_column='reason',
        max_length=150,
        null=True,
        blank=True
    )
    usercode = models.CharField(
        db_column='usercode',
        max_length=50,
        null=False,
        blank=False
    )
    createdtime = models.DateTimeField(
        db_column='createdtime',
        null=True,
        blank=True
    )
    updatedby = models.CharField(
        db_column='updatedby',
        max_length=50,
        null=True,
        blank=True
    )
    updatedtime = models.DateTimeField(
        db_column='updatedtime',
        null=True,
        blank=True
    )
    type = models.CharField(
        db_column='type',
        max_length=20,
        null=True,
        blank=True
    )
    towords = models.CharField(
        db_column='towords',
        max_length=15,
        null=True,
        blank=True
    )
    createdby = models.CharField(
        db_column='createdby',
        max_length=30,
        null=True,
        blank=True
    )
    id_pk = models.IntegerField(
        db_column='id_pk',
        primary_key=True
    )


    class Meta:
        db_table = 'tblRefund'
