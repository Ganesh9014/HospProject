from django.db import models

class RoomTypeMaster(models.Model):
    roomtypeid = models.AutoField(primary_key=True)
    roomtype = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=50, null=True, blank=True)
    roomrent = models.IntegerField(null=True, blank=True)
    active = models.CharField(max_length=5, null=True, blank=True)
    invest = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'room_type_master'

    def __str__(self):
        return f"{self.roomtype or ''} - {self.roomrent or ''}"
