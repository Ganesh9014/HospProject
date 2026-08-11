
from django.db import models    
class BillMaster(models.Model):
    billno = models.BigAutoField(primary_key=True)
    bill_date = models.DateField(auto_now_add=True)

    BILL_TYPE_CHOICES = (
        ('CONSULTATION', 'Consultation'),
        ('INVESTIGATION', 'Investigation'),
        ('PHARMACY', 'Pharmacy'),
    )

    bill_type = models.CharField(max_length=20, choices=BILL_TYPE_CHOICES)

    uhid = models.CharField(max_length=50)
    created_by = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.CharField(max_length=1, default='Y', blank=True)


    class Meta:
        db_table = "bill_master"
