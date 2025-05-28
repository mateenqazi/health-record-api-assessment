#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings
from django.core.management import call_command

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_record_api.settings')
    django.setup()
    call_command('collectstatic', '--noinput')
