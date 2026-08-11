from django.db import models

class NewInvMaster(models.Model):
    sno = models.AutoField(primary_key=True)   # existing auto-increment
    invname = models.IntegerField()
    test = models.CharField(max_length=50, null=True, blank=True)
    units = models.CharField(max_length=20, null=True, blank=True)
    normal = models.TextField(null=True, blank=True)
    method = models.CharField(max_length=200, null=True, blank=True)
    header = models.CharField(max_length=50, null=True, blank=True)
    impression = models.TextField(null=True, blank=True)
    defaults = models.TextField(null=True, blank=True)
    submethod = models.CharField(max_length=100, null=True, blank=True)
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('numeric', 'Numeric'),
            ('text_choice', 'Text Choice'),
            ('free_text', 'Free Text'),
        ],
        default='numeric'
    )

    # Numeric ranges — nullable, only used when result_type = numeric
    male_low    = models.FloatField(null=True, blank=True)
    male_high   = models.FloatField(null=True, blank=True)
    female_low  = models.FloatField(null=True, blank=True)
    female_high = models.FloatField(null=True, blank=True)
    child_low   = models.FloatField(null=True, blank=True)
    child_high  = models.FloatField(null=True, blank=True)
    child_age_cutoff = models.FloatField(null=True, blank=True, default=12)  # years

    # For text_choice tests (e.g. culture, serology)
    abnormal_values = models.CharField(max_length=255, null=True, blank=True)


    class Meta:
        db_table = 'newinvmaster'
           # 🔴 VERY IMPORTANT

    def __str__(self):
        return str(self.sno)
