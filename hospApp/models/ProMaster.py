from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator   
class ProMaster(models.Model):
    proid = models.AutoField(primary_key=True)
    pro_name = models.CharField(max_length=50, null=True, blank=True)
    specialized = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    phone = models.BigIntegerField(
        
        validators=[RegexValidator(r'^\d{10}$', 'Phone number must be exactly 10 digits.')],
        blank=False,
        null=False,
        
    )

    active = models.CharField(max_length=3, null=True, blank=True, default='Y')
    userid = models.CharField(max_length=10, null=True, blank=True)
    createdby = models.CharField(max_length=50, null=True, blank=True)
    updatedby = models.CharField(max_length=50, null=True, blank=True)
    createddate = models.DateTimeField(default=timezone.now)
    updateddate = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.pro_name or ''
