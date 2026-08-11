from django.db import models

class StateMaster(models.Model):
    sno = models.AutoField(primary_key=True, db_column='sno')
    statename = models.CharField(max_length=30, null=True, db_column='statename')

    class Meta:
        db_table = 'state_master'

    def __str__(self):
        return self.statename or ""
