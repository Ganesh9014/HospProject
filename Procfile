web: sh -c "python manage.py collectstatic --no-input && python manage.py setup_db && gunicorn HospProject.wsgi:application"
