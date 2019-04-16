FROM python:3.7

RUN pip install supervisor uwsgi
RUN apt update
RUN apt install --yes nginx p7zip-full

ADD docker/supervisord.conf /etc/supervisord.conf
ADD docker/nginx.conf /etc/nginx/sites-enabled/default
ADD docker/update_app.py /app/update_app.py

ADD . /app

RUN pip install -r /app/requirements.txt
RUN cd /app; python manage.py collectstatic --noinput
RUN cd /app; python manage.py migrate
RUN cd /app; python manage.py update_warehouse

EXPOSE 8000
ENV DEBUG=FALSE

ENTRYPOINT ["supervisord", "-c", "/etc/supervisord.conf"]
