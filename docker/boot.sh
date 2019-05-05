#!/bin/bash
if [[ "$DB_ENGINE" == "mysql" ]]; then
  while ! mysqladmin ping -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" --silent; do
    echo Failed to connect to MySQL Server
    sleep 1
  done
fi

pushd /app
python manage.py migrate
popd

exec supervisord -c /etc/supervisord.conf