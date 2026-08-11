from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
class Employee(models.Model):
    
    emp_id = models.CharField(
        max_length=15,
        unique=True,
        blank=False,  # Required in forms
        null=False    # Required in DB
    )

    emp_name = models.CharField(
        max_length=250,
        blank=False,  # Required in forms
        null=False    # Cannot be NULL in DB
    )

    designation = models.CharField(
        max_length=50,
        
        blank=False,  # Must choose from options
        null=False
    )

    age = models.IntegerField(
        
        validators=[MinValueValidator(18), MaxValueValidator(65)],
        blank=False,  # Must enter age
        null=False
    )

    doj = models.DateField(
        blank=False,  # Must enter date
        null=False    # Stored as a date type
    )

    address = models.CharField(
        max_length=250,
        blank=True,   # Optional
        null=True
    )

    phone = models.BigIntegerField(
        
        validators=[RegexValidator(r'^\d{10}$', 'Phone number must be exactly 10 digits.')],
        blank=False,
        null=False,
        
    )

    createdby = models.CharField(max_length=50, blank=True, null=True)
    createddate = models.DateTimeField(blank=True, null=True)
    updatedby = models.CharField(max_length=50, blank=True, null=True)
    updatedtime = models.DateTimeField(blank=True, null=True)
    active = models.CharField(max_length=3, blank=True, null=True)
    empid = models.CharField(max_length=250, blank=True, null=True)
    empname = models.CharField(max_length=250, blank=True, null=True)
    empdesig = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        db_table = 'employee'

    def __str__(self):
        return  self.emp_id
