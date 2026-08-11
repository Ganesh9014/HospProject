from django.db import models


class DepartmentPhotoMaster(models.Model):
    dno = models.AutoField(primary_key=True)
    
    department = models.CharField(max_length=50, null=False)

    active = models.CharField(max_length=5, null=True, blank=True, default='Y')

    createdby = models.CharField(max_length=50, null=True, blank=True)
    createddate = models.DateTimeField(null=True, blank=True)

    updatedby = models.CharField(max_length=50, null=True, blank=True)
    updatedtime = models.DateTimeField(null=True, blank=True)

    # Image-related fields (all included as you requested)
    phote = models.ImageField(upload_to="department_photos/", null=True, blank=True)
    signature = models.ImageField(upload_to="department_signatures/", null=True, blank=True)
    photos = models.BinaryField(null=True, blank=True)
    name=models.CharField(max_length=250, null=True, blank=True)
    regno=models.CharField(max_length=250, null=True, blank=True)

    contenttype = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "department_photo_master"

    def __str__(self):
        return self.department
