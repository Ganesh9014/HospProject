
from django.db import models
class RoomMaster(models.Model):
    roomid = models.AutoField(primary_key=True)
    roomno = models.CharField(max_length=20, null=True, blank=True)
    floorid = models.ForeignKey('MainFloorMaster', on_delete=models.SET_NULL, null=True, blank=True)
    roomtypeid = models.ForeignKey('RoomTypeMaster', on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.CharField(max_length=100, null=True, blank=True)
    orderno = models.IntegerField(null=True, blank=True)
    active = models.CharField(max_length=5, null=True, blank=True)

    class Meta:
        db_table = 'room_master'

    def __str__(self):
        return f"{self.roomno or ''}"
