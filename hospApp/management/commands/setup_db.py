from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection

class Command(BaseCommand):
    help = "Run migrations and seed default admin user and roles"

    def handle(self, *args, **options):
        self.stdout.write("Running migrations...")
        call_command('migrate', interactive=False)
        self.stdout.write("Migrations completed.")

        from hospApp.models import Tbluserpermission, tblRoles, Employee

        if not tblRoles.objects.filter(roleid=1).exists():
            tblRoles.objects.create(
                roleid=1,
                rolename='AdminRole',
                mainrole='yes',
                rolepages='Admin,Front Office,OP,Lab,Reports,Registration,Consultation'
            )
            self.stdout.write("Created default AdminRole.")

        if not Employee.objects.filter(id=1).exists():
            Employee.objects.create(
                id=1,
                emp_id='MH01',
                emp_name='Admin',
                designation='AdminRole',
                age=28,
                doj='2026-01-01',
                address='Hospital',
                phone=9999999999
            )
            self.stdout.write("Created default Admin employee.")

        if not Tbluserpermission.objects.filter(username='admin').exists():
            role = tblRoles.objects.get(roleid=1)
            emp = Employee.objects.get(id=1)
            Tbluserpermission.objects.create(
                username='admin',
                password='admin',
                permission='ALL',
                isactive=True,
                app_permission=True,
                emp=emp,
                empname='Admin',
                empdesig='AdminRole',
                mainrole=role
            )
            self.stdout.write("Created default admin user (username: admin, password: admin).")

        self.stdout.write(self.style.SUCCESS("Database setup & seeding completed successfully!"))
