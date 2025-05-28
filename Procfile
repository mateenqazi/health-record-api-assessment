web: python manage.py collectstatic --noinput && python manage.py migrate && gunicorn health_record_api.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A health_record_api worker --loglevel=info
