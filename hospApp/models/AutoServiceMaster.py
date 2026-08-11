from django.db import models

class ServiceMaster(models.Model):
    serviceid = models.AutoField(primary_key=True)
    servicename = models.CharField(max_length=200, null=True, blank=True)
    servicetypename = models.CharField(max_length=100, null=True, blank=True)
    servicecode = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    labservices = models.CharField(max_length=5, null=True, blank=True)
    active = models.CharField(max_length=5, null=True, blank=True)
    roomtype = models.ForeignKey(
        'RoomTypeMaster',  # ✅ no circular import
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='roomtype_id'
    )

    class Meta:
        db_table = 'service_master'  # ✅ optional but good practice

    def __str__(self):
        return self.servicename or ''
