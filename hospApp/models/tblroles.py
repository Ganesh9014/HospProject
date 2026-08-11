from django.db import models
from hospApp.models.menus import SubMenu


class tblRoles(models.Model):
    roleid = models.AutoField(db_column='RoleId', primary_key=True)
    rolename = models.CharField(db_column='RoleName', max_length=50, blank=True, null=True)

    # 🔴 OLD (KEEP TEMPORARILY)
    rolepages = models.TextField(db_column='RolePages', blank=True, null=True)

    # 🟢 NEW (USE THIS)
    pages = models.ManyToManyField(
        SubMenu,
        related_name='roles',
        blank=True
    )

    # 🟢 NEW FOR HEADER LINKS
    header_pages = models.ManyToManyField(
        SubMenu,
        related_name='header_roles',
        blank=True
    )

    mainrole = models.CharField(max_length=5, blank=True, null=True)
    roletables = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'tblroles'

    def __str__(self):
        return self.rolename
