from django.db import models
from django.utils import timezone   
from .Tbluserpermission import Tbluserpermission
class Login(models.Model):
    user = models.ForeignKey(Tbluserpermission, on_delete=models.CASCADE, related_name='logins')
    logintime = models.DateTimeField(default=timezone.now)
    logouttime = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'login'

    def __str__(self):
        return f"{self.user.username} logged in at {self.logintime}"