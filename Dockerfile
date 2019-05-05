FROM python:3.7

RUN pip install supervisor uwsgi
RUN apt update
RUN apt install --yes nginx p7zip-full mysql-client

ADD docker/supervisord.conf /etc/supervisord.conf
ADD docker/nginx.conf /etc/nginx/sites-enabled/default
ADD docker/update_app.py /app/update_app.py
ADD docker/start_with_update.sh /app/start_with_update.sh
ADD docker/boot.sh /boot.sh
RUN chmod +x /app/start_with_update.sh
RUN chmod +x /boot.sh

ADD . /app

RUN pip install -r /app/requirements.txt
RUN cd /app; python manage.py collectstatic --noinput

EXPOSE 8000
ENV DEBUG=FALSE

ENTRYPOINT ["/boot.sh"]
