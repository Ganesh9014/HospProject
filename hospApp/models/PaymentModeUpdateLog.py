
from django.db import models
from django.utils import timezone
class PaymentModeUpdateLog(models.Model):


        uhid = models.CharField(max_length=50)
        patient_name = models.CharField(max_length=150)

        bill_no = models.CharField(max_length=50)
        bill_type = models.CharField(max_length=50)

        old_online_mode = models.CharField(
            max_length=100,
            null=True,
            blank=True
        )

        new_online_mode = models.CharField(
            max_length=100,
            null=True,
            blank=True
        )

        old_reference = models.CharField(
            max_length=200,
            null=True,
            blank=True
        )

        new_reference = models.CharField(
            max_length=200,
            null=True,
            blank=True
        )

        updated_by = models.CharField(max_length=50)

        updated_on = models.DateTimeField(auto_now_add=True)

      