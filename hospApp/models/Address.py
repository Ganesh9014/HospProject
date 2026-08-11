# hospApp/models.py
from django.db import models

class State(models.Model):
    statename = models.CharField(max_length=100, unique=True)
    

    def __str__(self):
        return self.statename


class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='districts')
    districtname = models.CharField(max_length=100)

    def __str__(self):
        return self.districtname


class City(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='cities')
    cityname = models.CharField(max_length=100)

    def __str__(self):
        return self.cityname
