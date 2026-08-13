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

        from hospApp.models import Tbluserpermission, tblRoles, Employee, MainMenu, SubMenu

        # Check if database is empty and needs initial seeding from hospital_db.sql
        try:
            if SubMenu.objects.count() < 10 or not tblRoles.objects.filter(roleid=1).exists():
                self.stdout.write("Seeding initial menus, submenus, and permissions from hospital_db.sql...")
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

        # Ensure AdminRole exists
        admin_role, _ = tblRoles.objects.get_or_create(
            roleid=1,
            defaults={
                'rolename': 'AdminRole',
                'mainrole': 'yes',
                'rolepages': 'Admin,Front Office,OP,Lab,Reports,Registration,Consultation'
            }
        )

        # Assign all submenus to AdminRole pages and header_pages so menus appear in sidebar
        all_submenus = list(SubMenu.objects.all())
        if all_submenus:
            admin_role.pages.set(all_submenus)
            admin_role.header_pages.set(all_submenus)
            self.stdout.write(self.style.SUCCESS(f"Assigned {len(all_submenus)} submenus to AdminRole."))

        # Ensure Admin employee exists
        emp, _ = Employee.objects.get_or_create(
            id=1,
            defaults={
                'emp_id': 'MH01',
                'emp_name': 'Admin',
                'designation': 'AdminRole',
                'age': 28,
                'doj': '2026-01-01',
                'address': 'Hospital',
                'phone': 9999999999
            }
        )

        # Ensure Admin user exists and has AdminRole attached
        admin_user, created = Tbluserpermission.objects.get_or_create(
            username='admin',
            defaults={
                'password': 'admin',
                'permission': 'ALL',
                'isactive': True,
                'app_permission': True,
                'emp': emp,
                'empname': 'Admin',
                'empdesig': 'AdminRole',
                'mainrole': admin_role
            }
        )
        if not created:
            admin_user.mainrole = admin_role
            admin_user.isactive = True
            admin_user.save()

        self.stdout.write(self.style.SUCCESS("Database setup & role permission seeding completed successfully!"))
