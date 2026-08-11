from django.db import models
from django.utils import timezone

class MainFloorMaster(models.Model):
    floorid = models.AutoField(primary_key=True)
    floorno = models.CharField(max_length=50, null=True, blank=True)
    remarks = models.CharField(max_length=50, null=True, blank=True)
    floorcolor = models.CharField(max_length=50, null=True, blank=True)
    userid = models.CharField(max_length=50, null=True, blank=True)
    active = models.CharField(max_length=2, null=True, blank=True)
    orderno = models.IntegerField(null=True, blank=True)
    createddate = models.DateTimeField(default=timezone.now, null=True, blank=True)
    updateddate = models.DateTimeField(default=timezone.now, null=True, blank=True)

    class Meta:
        db_table = 'main_floor_master'
        ordering = ['orderno', 'floorid']

    def __str__(self):
        return f"{self.floorno or 'Unnamed Floor'}"
