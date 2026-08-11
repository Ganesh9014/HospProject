from django.db import models


class SittingsPage(models.Model):
    sno = models.AutoField(primary_key=True)
    uhid = models.CharField(max_length=50)
    billno = models.CharField(max_length=50)
    sitting = models.CharField(max_length=100, blank=True, null=True)
    sdate = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=150, blank=True, null=True)
    next_sitting_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.uhid} - {self.billno} (Sitting: {self.sitting})"