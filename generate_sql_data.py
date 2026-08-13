import os
import sys
import django

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HospProject.settings")
django.setup()

from django.db import connection

# Ensure console handles UTF-8 for emojis
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Master tables in dependency order (to ensure foreign key resolution)
MASTER_TABLES = [
    'state_master',
    'hospApp_state',
    'hospApp_district',
    'hospApp_districtmaster',
    'hospApp_city',
    'employee',
    'tblroles',
    'hospApp_mainmenu',
    'hospApp_submenu',
    'hospApp_childsubmenu',
    'tblroles_pages',
    'tblUserPermission',
    'BankMaster',
    'hospital_Master',
    'department_photo_master',
    'case_type_master',
    'hospApp_promaster',
    'inv_group_master',
    'investigation_master',
    'refdoc_master',
    'service_type_master',
    'speciality_master',
    'doctor_master',
    'tblInvestigationDetails',
    'tblservices',
    'bed_master',
    'main_department_master',
    'main_floor_master',
    'newinvmaster',
    'room_master',
    'room_type_master',
    'service_master',
]

def get_identity_tables(cursor):
    """Retrieve tables that have identity columns in SQL Server"""
    try:
        cursor.execute("""
            SELECT OBJECT_NAME(object_id) AS TableName
            FROM sys.identity_columns
        """)
        return {row[0].lower() for row in cursor.fetchall()}
    except Exception:
        return set()

def dump_sql():
    sql_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hospital_db.sql')
    print(f"Generating SQL data to {sql_path}...")
    
    with connection.cursor() as cursor:
        # Get active tables in DB (case-insensitive dictionary mapping)
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        db_tables = {row[0].lower(): row[0] for row in cursor.fetchall()}
        
        identity_tables = get_identity_tables(cursor)
        
        lines = [
            "-- ============================================================",
            "-- SQL Server INSERT script — Hospital Database",
            "-- Generated automatically from live database",
            "-- Run AFTER: python manage.py migrate",
            "-- Open in SSMS and execute (F5)",
            "-- ============================================================\n",
            "SET NOCOUNT ON;",
            "BEGIN TRANSACTION;\n"
        ]
        
        for table_key in MASTER_TABLES:
            if table_key.lower() not in db_tables:
                print(f"[WARN] Table '{table_key}' not found in database, skipping.")
                continue
            
            actual_table_name = db_tables[table_key.lower()]
            
            qn = connection.ops.quote_name
            # Select all rows
            cursor.execute(f"SELECT * FROM {qn(actual_table_name)}")
            rows = cursor.fetchall()
            
            if not rows:
                print(f"[INFO] Table '{actual_table_name}' is empty, skipping.")
                continue
            
            # Get columns
            columns = [col[0] for col in cursor.description]
            
            lines.append(f"-- ---- [{actual_table_name}]  ({len(rows)} rows) ----")
            
            has_identity = actual_table_name.lower() in identity_tables
            if has_identity:
                lines.append(f"SET IDENTITY_INSERT {qn(actual_table_name)} ON;")
            
            for row in rows:
                values_formatted = []
                for val in row:
                    if val is None:
                        values_formatted.append("NULL")
                    elif isinstance(val, bool):
                        values_formatted.append("1" if val else "0")
                    elif isinstance(val, (int, float)):
                        values_formatted.append(str(val))
                    else:
                        # String/Date/Time: escape single quotes and wrap in quotes
                        val_str = str(val).replace("'", "''")
                        values_formatted.append(f"'{val_str}'")
                
                cols_str = ", ".join([qn(col) for col in columns])
                vals_str = ", ".join(values_formatted)
                lines.append(f"INSERT INTO {qn(actual_table_name)} ({cols_str}) VALUES ({vals_str});")
            
            if has_identity:
                lines.append(f"SET IDENTITY_INSERT {qn(actual_table_name)} OFF;")
            
            lines.append("") # blank line between tables
            print(f"[OK] Dumped {len(rows)} rows from '{actual_table_name}'")
            
        lines.append("COMMIT TRANSACTION;")
        
        with open(sql_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines) + "\n")
            
    print(f"[SUCCESS] SQL generation complete! File saved at {sql_path}")

if __name__ == "__main__":
    dump_sql()
