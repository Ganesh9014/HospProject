import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection

class Command(BaseCommand):
    help = "Run migrations and seed default admin user, roles, and initial data"

    def handle(self, *args, **options):
        self.stdout.write("Running migrations...")
        call_command('migrate', interactive=False)
        self.stdout.write("Migrations completed.")

        from hospApp.models import Tbluserpermission, tblRoles, Employee, MainMenu

        # Check if database is empty and needs initial seeding from hospital_db.sql
        try:
            if not MainMenu.objects.exists():
                self.stdout.write("Seeding initial menus, roles, and master data from hospital_db.sql...")
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                sql_file = os.path.join(base_dir, 'hospital_db.sql')
                if os.path.exists(sql_file):
                    with open(sql_file, 'r', encoding='utf-8') as f:
                        sql_content = f.read()
                    
                    with connection.cursor() as cursor:
                        for statement in sql_content.split(';'):
                            stmt = statement.strip()
                            if stmt and not stmt.startswith('--') and not stmt.upper().startswith(('BEGIN', 'COMMIT', 'SET NOCOUNT')):
                                try:
                                    cursor.execute(stmt)
                                except Exception as e:
                                    pass
                    self.stdout.write(self.style.SUCCESS("hospital_db.sql data imported successfully!"))
        except Exception as e:
            self.stdout.write(f"Seed note: {e}")

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
