from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from hospApp.models import Employee

class Tbluserpermission(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)

    permission = models.TextField(blank=True, null=True)
    isactive = models.BooleanField(default=False)
    app_permission = models.BooleanField(default=False)
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='permissions', null=True, blank=True)
    empid = models.CharField(max_length=50, blank=True, null=True)
    empname = models.CharField(max_length=60, blank=True, null=True)
    empdesig = models.CharField(max_length=60, blank=True, null=True)
    # e.g., ADMIN / USER
    mainrole = models.ForeignKey('tblRoles', on_delete=models.SET_NULL, null=True, blank=True)

    # Use lowercase 'department' (CharField is better for short choices)
    department = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'tblUserPermission'

    def __str__(self):
        return self.username