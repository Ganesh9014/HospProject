from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
class BedMaster(models.Model):
    bedid = models.AutoField(primary_key=True)
    # link to RoomMaster if you have it (nullable)
    room = models.ForeignKey('RoomMaster', on_delete=models.SET_NULL, null=True, blank=True)
    bedno = models.CharField(max_length=50, null=True, blank=True)
    ord = models.IntegerField(null=True, blank=True)
    remarks = models.CharField(max_length=50, null=True, blank=True)
    active = models.CharField(max_length=2, null=True, blank=True)
    filled = models.CharField(max_length=10, null=True, blank=True)
    bedcolor = models.CharField(max_length=50, null=True, blank=True)
    bedcharges = models.IntegerField(null=True, blank=True)
    chargeble = models.CharField(max_length=10, null=True, blank=True)  # e.g. 'Y'/'N'
    othercharges = models.IntegerField(null=True, blank=True)
    bedstatus = models.CharField(max_length=10, null=True, blank=True)

    # keep floor and roomtype references for easy display/search
    floor = models.ForeignKey('MainFloorMaster', on_delete=models.SET_NULL, null=True, blank=True)
    roomtype = models.ForeignKey('RoomTypeMaster', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'bed_master'
        ordering = ['bedid']

    def __str__(self):
        return f"{self.room.roomno if self.room else ''} / {self.bedno or ''}"
