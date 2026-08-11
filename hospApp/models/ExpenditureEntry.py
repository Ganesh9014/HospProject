

from django.db import models
from hospApp.models import Expenditure
from django.utils import timezone
class ExpenditureEntry(models.Model):
    sno = models.AutoField(primary_key=True)

    expenditure = models.ForeignKey(
        Expenditure,
        on_delete=models.CASCADE
    )

    bill_no = models.IntegerField(unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    towards = models.CharField(max_length=255)
   

    created_at = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    active = models.CharField(max_length=1, default='Y', blank=True)
    reason=models.CharField(max_length=255, null=True, blank=True)
    user=models.CharField(max_length=255, null=True, blank=True)   
    selecteduser=models.CharField(max_length=255, null=True, blank=True)     


    def __str__(self):
        return f"{self.expenditure_id} - {self.amount}"