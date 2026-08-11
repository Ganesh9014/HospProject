from django.db import models


class MainDepartmentMaster(models.Model):
    dno = models.AutoField(primary_key=True)
    department = models.CharField(max_length=50)
    active = models.CharField(max_length=5, null=True, blank=True)
    createdby = models.CharField(max_length=50, null=True, blank=True)
    createddate = models.DateTimeField(null=True, blank=True)
    updatedby = models.CharField(max_length=50, null=True, blank=True)
    updatedtime = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'main_department_master'   
        

    def __str__(self):
        return self.department
