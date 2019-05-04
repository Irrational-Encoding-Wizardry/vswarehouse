#!/bin/bash
python manage.py update_warehouse
exec uwsgi --socket /tmp/app.sock --plugin python --wsgi-file VSWarehouse/wsgi.py --master --processes 4 --uid www-data --gid www-data
