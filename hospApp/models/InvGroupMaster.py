from django.db import models


class InvGroupMaster(models.Model):
    sno = models.AutoField(primary_key=True)  # PK
    gname = models.CharField(max_length=100, null=True, blank=True)
    userid = models.CharField(max_length=50, null=True, blank=True)
    insertedtime = models.DateTimeField(null=True, blank=True)
    updatedby = models.CharField(max_length=50, null=True, blank=True)
    updatedtime = models.DateTimeField(null=True, blank=True)
    active = models.CharField(max_length=2, null=True, blank=True)

    class Meta:
        db_table = 'inv_group_master'

    def __str__(self):
        return self.gname or ""
