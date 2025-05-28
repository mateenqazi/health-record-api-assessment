web: python manage.py collectstatic --noinput && gunicorn health_record_api.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate
