from django.db import models
from django.utils import timezone
from hospApp.models import HospitalMaster ,ProMaster,RefDoctorMaster # ✅ Make sure this import exists


class OpPatientRegistration(models.Model):
    patid = models.CharField(max_length=20, null=True, blank=True)
    entrydate = models.DateTimeField(default=timezone.now, blank=True, null=True)
    entrytime = models.DateTimeField(default=timezone.now, blank=True, null=True)
    uhid = models.CharField(max_length=50, unique=True, editable=True, null=True, blank=True)

    TITLE_CHOICES = [
    ('Mr', 'Mr.'),
    ('Mrs', 'Mrs.'),
    ('Ms', 'Ms.'),
    ('Miss', 'Miss.'),
    
    ('Baby', 'Baby'),
    
    
    ]
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, default='Mr')

    patname = models.CharField(max_length=200)
    fname = models.CharField(max_length=100, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    agetype = models.CharField(max_length=20, null=True, blank=True)
    doctor = models.CharField(max_length=100, null=True, blank=True)
    refdoctor = models.ForeignKey(RefDoctorMaster, on_delete=models.PROTECT, null=True, blank=True)


    address = models.CharField(max_length=500, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    district= models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    area = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    remarks = models.CharField(max_length=500, null=True, blank=True)
    userid = models.CharField(max_length=50, null=True, blank=True)
    updatedby = models.CharField(max_length=50, null=True, blank=True)
    fee = models.IntegerField(null=True, blank=True)
    billno = models.IntegerField(null=True, blank=True)
    updatedtime = models.DateTimeField(null=True, blank=True)
    cname = models.CharField(max_length=30, null=True, blank=True)
    crelation = models.CharField(max_length=10, null=True, blank=True)
    cAddress = models.CharField(max_length=100, null=True, blank=True)
    cPhone = models.CharField(max_length=15, null=True, blank=True)
    empid = models.CharField(max_length=15, null=True, blank=True)
    designation = models.CharField(max_length=20, null=True, blank=True)
    compname = models.CharField(max_length=20, null=True, blank=True)
    off1 = models.CharField(max_length=20, null=True, blank=True)
    off2 = models.CharField(max_length=20, null=True, blank=True)
    bloodgroup = models.CharField(max_length=20, null=True, blank=True)
    occupation = models.CharField(max_length=20, null=True, blank=True)
    education = models.CharField(max_length=20, null=True, blank=True)
    identmarks1 = models.CharField(max_length=100, null=True, blank=True)
    identmarks2 = models.CharField(max_length=100, null=True, blank=True)
    notes = models.CharField(max_length=100, null=True, blank=True)
    drugallergies = models.CharField(max_length=100, null=True, blank=True)
    foodallergies = models.CharField(max_length=100, null=True, blank=True)
    otherallergies = models.CharField(max_length=100, null=True, blank=True)
    isop = models.CharField(max_length=2, null=True, blank=True)
    pro = models.ForeignKey(ProMaster, on_delete=models.PROTECT, null=True, blank=True)
    organisations = models.CharField(max_length=100, null=True, blank=True)
    organisation = models.CharField(max_length=50, null=True, blank=True)
    types = models.CharField(max_length=50, null=True, blank=True)
    createdtime = models.DateTimeField(default=timezone.now, null=True, blank=True)
    alternatephone = models.CharField(max_length=15, null=True, blank=True)

    class Meta:
        db_table = 'oppatient_registration'


    def __str__(self):
        return f"{self.title} {self.patname} ({self.uhid})"

    def save(self, *args, **kwargs):
        """Auto-generate UHID and PATID dynamically."""
        # ✅ Auto-generate UHID
        if not self.uhid:
            # Get hospital initial (e.g. "MH")
            hospital = HospitalMaster.objects.filter(active='a').first()
            hospital_initial = hospital.initial if hospital and hospital.initial else "HSP"

            # Current year
            current_year = timezone.now().year

            # UHID prefix like "MH2025"
            prefix = f"{hospital_initial}{current_year}"

            # Find last UHID starting with prefix
            last_record = OpPatientRegistration.objects.filter(uhid__startswith=prefix).order_by('-uhid').first()

            if last_record:
                try:
                    last_num = int(last_record.uhid.replace(prefix, ""))
                except ValueError:
                    last_num = 0
                next_num = last_num + 1
            else:
                next_num = 1

            # Generate new UHID (MH20250001, MH20250002, ...)
            self.uhid = f"{prefix}{next_num:04d}"

        # ✅ Auto-generate PATID
        if not self.patid:
            last_pat = OpPatientRegistration.objects.exclude(patid__isnull=True).exclude(patid='').order_by('-id').first()
            if last_pat and last_pat.patid and last_pat.patid.startswith('P'):
                try:
                    last_num = int(last_pat.patid.replace('P', ''))
                except ValueError:
                    last_num = 1000
                next_num = last_num + 1
            else:
                next_num = 1001
            self.patid = f"P{next_num}"

        super().save(*args, **kwargs)
