from django.db import models

class InvestigationReport(models.Model):
    id = models.AutoField(primary_key=True)

    # ---------------- PATIENT INFO SNAPSHOT ----------------
    billno = models.CharField(max_length=20)
    uhid = models.CharField(max_length=20)
    patname = models.CharField(max_length=100)

    age = models.IntegerField(null=True, blank=True)
    agetype = models.CharField(max_length=10, null=True, blank=True)   # Years / Months / Days
    gender = models.CharField(max_length=10, null=True, blank=True)

    doc = models.CharField(max_length=100, null=True, blank=True)

    # ---------------- INVESTIGATION ----------------
    inv_id = models.IntegerField()   # InvestigationMaster.ino
    test = models.TextField()

    result = models.TextField(null=True, blank=True)
    units = models.CharField(max_length=50, null=True, blank=True)
    normal = models.TextField(null=True, blank=True)

    # ---------------- AUDIT ----------------
    userid = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    method = models.CharField(max_length=200, null=True, blank=True)
    header = models.CharField(max_length=50, null=True, blank=True)
    impression = models.TextField(null=True, blank=True)
    defaults = models.TextField(null=True, blank=True)
    submethod = models.CharField(max_length=100, null=True, blank=True)
    generateddate = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True) 
    is_check = models.BooleanField(default=False) 



    class Meta:
        db_table = "investigation_report"

    def __str__(self):
        return f"{self.billno} - {self.test}"
