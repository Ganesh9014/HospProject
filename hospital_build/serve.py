import os
import sys

# Ensure console output handles UTF-8 characters if possible
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HospProject.settings')

# Log startup attempts
log_file = os.path.join(BASE_DIR, 'startup_log.txt')
def log_message(msg):
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

log_message("Server startup initiated.")

try:
    from django.core.wsgi import get_wsgi_application
    from whitenoise import WhiteNoise
    from waitress import serve
    from django.db import connections
    from django.db.utils import OperationalError

    # Retry database connection (up to 30 seconds) to wait for SQL Server to boot on restart
    db_conn_ok = False
    for attempt in range(1, 7):
        try:
            log_message(f"Checking database connection (attempt {attempt}/6)...")
            connection = connections['default']
            connection.ensure_connection()
            db_conn_ok = True
            log_message("Database connection verified successfully.")
            break
        except OperationalError as e:
            log_message(f"Database not ready: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            log_message(f"Unexpected database check error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

    if not db_conn_ok:
        log_message("WARNING: Database connection check failed/timed out. Starting server anyway.")

    application = get_wsgi_application()
    application = WhiteNoise(application, 
                             root=os.path.join(BASE_DIR, 'staticfiles'), 
                             prefix='static')
    application.add_files(os.path.join(BASE_DIR, 'media'), prefix='media')

    # Only print if a real console is attached (not pythonw.exe)
    if sys.stdout is not None:
        print("=" * 50)
        print("  [HOSPITAL MANAGEMENT SYSTEM]")
        print("=" * 50)
        print("  * Server is starting...")
        print("  * Open browser: http://localhost:8000")
        print("  * Network access: http://YOUR-IP:8000")
        print("  * To stop: Close this window")
        print("=" * 50)
        sys.stdout.flush()

    log_message("Starting Waitress server on 0.0.0.0:8000...")
    serve(application, host='0.0.0.0', port=8000, threads=4)

except Exception as e:
    import traceback
    error_msg = f"CRITICAL STARTUP ERROR:\n{traceback.format_exc()}"
    log_message(error_msg)
    try:
        with open(os.path.join(BASE_DIR, 'startup_error.log'), 'w', encoding='utf-8') as f:
            f.write(error_msg)
    except Exception:
        pass
    sys.exit(1)
