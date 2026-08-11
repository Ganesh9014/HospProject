
from django.db import models    

class Expenditure(models.Model):
    sno = models.AutoField(primary_key=True)
    expenditure_name = models.CharField(max_length=100)
    active = models.CharField(max_length=5, null=True, blank=True, default='Y')

    def __str__(self):
        return self.expenditure_name