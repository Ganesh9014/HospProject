from django.db import models
from .DoctorMaster import DoctorMaster
from .RefDoctorMaster import RefDoctorMaster
from .ProMaster import ProMaster
from .CaseTypeMaster import CaseTypeMaster

class DoctorConsultation(models.Model):

    patid = models.CharField(max_length=50, null=True, blank=True)
    uhid = models.CharField(max_length=50, null=True, blank=True)
    opno = models.CharField(max_length=20, null=True, blank=True)

    patname = models.CharField(max_length=50, null=False)

    dob = models.DateTimeField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    agetype = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    gardian = models.CharField(max_length=50, null=True, blank=True)

    casetypemaster = models.ForeignKey(
        CaseTypeMaster, on_delete=models.PROTECT,
        null=True, blank=True, db_column="casetype_id"
    )

    address = models.CharField(max_length=250, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    visittype = models.CharField(max_length=20, null=True, blank=True)
    consulttype = models.CharField(max_length=20, null=True, blank=True)

    promaster = models.ForeignKey(ProMaster, on_delete=models.PROTECT, null=True, blank=True)
    refdoctor = models.ForeignKey(RefDoctorMaster, on_delete=models.PROTECT, null=True, blank=True)
    doctor = models.ForeignKey(DoctorMaster, on_delete=models.PROTECT, null=True, blank=True)

    consulfee = models.IntegerField(null=True, blank=True)
    paidamt = models.IntegerField(null=True, blank=True)
    due = models.IntegerField(null=True, blank=True)
    concession = models.IntegerField(null=True, blank=True)
    concreason = models.CharField(max_length=150, null=True, blank=True)

    paymenttype = models.CharField(max_length=50, null=True, blank=True)
    paymode = models.CharField(max_length=50, null=True, blank=True)
    cardname = models.CharField(max_length=100, null=True, blank=True)

    tokenno = models.IntegerField(null=True, blank=True)
    is_prescription_done = models.BooleanField(default=False)
    is_revisit = models.BooleanField(default=False)

    billno = models.IntegerField(null=True, blank=True, default=0)

    regdt = models.DateTimeField(null=True, blank=True)
    createddate = models.DateTimeField(null=True, blank=True)

    userid = models.CharField(max_length=50, null=True, blank=True)
    isactive = models.CharField(max_length=2, null=True, blank=True)
    previous_consult = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="revisit_records"
    )
    cash_amt = models.IntegerField(default=0)
    online_amt = models.IntegerField(default=0)
    online_mode = models.CharField(max_length=50, null=True, blank=True)
    online_details = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "doctor_consultation"

    def __str__(self):
        return f"{self.patname} ({self.uhid})"
