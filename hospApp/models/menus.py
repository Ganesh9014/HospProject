from django.db import models
class MainMenu(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class SubMenu(models.Model):
    main_menu = models.ForeignKey(MainMenu, on_delete=models.CASCADE, related_name='sublinks')
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    display_order = models.PositiveIntegerField(default=0)  
    is_header = models.BooleanField(default=False)
    