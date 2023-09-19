FROM python:3.9.7

# We define a default DJANGO_SECRET_KEY value that you must override by a docker env variable
ARG DJANGO_SECRET_KEY=DefineHereAUniqueSecretKey

ENV DJANGO_DEBUG=False
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

WORKDIR /var/www/webtool
#RUN apk add git && \

RUN apt-get -y install git && \
    git clone https://github.com/nfourniol/whereismyvm.git && \
    cp whereismyvm/config.yaml.sample whereismyvm/config.yaml && \
    cp whereismyvm/hypervisor.yaml.sample whereismyvm/hypervisor.yaml && \
    echo "workers = 4" >> whereismyvm/gunicorn_config.py && \
    echo 'bind = "0.0.0.0:7777"' >> whereismyvm/gunicorn_config && \
    echo 'chdir = "/var/www/webtool/whereismyvm"' >> whereismyvm/gunicorn_config && \
    echo 'module = "whereismyvm.wsgi:application"' >> whereismyvm/gunicorn_config
WORKDIR /var/www/webtool/whereismyvm
RUN pip install --no-cache-dir -r requirements.txt

#COPY ./config.yaml.sample /var/www/webtool/whereismyvm/config.yaml
#COPY ./hypervisor.yaml.sample /var/www/webtool/whereismyvm/hypervisor.yaml

EXPOSE 7777
#RUN python manage.py migrate
#CMD ["gunicorn", "--config", "gunicorn_config.py", "whereismyvm.wsgi:application"]
CMD ["gunicorn", "whereismyvm.wsgi", "--bind", "127.0.0.1:7777"]
