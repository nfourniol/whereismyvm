FROM python:3.9.7

# We define a default DJANGO_SECRET_KEY value that you must override by a docker env variable
ARG DJANGO_SECRET_KEY=DefineHereAUniqueSecretKey

ENV DJANGO_DEBUG=False
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

WORKDIR /var/www/webtool

RUN apt-get -y install git && \
    git clone https://github.com/nfourniol/whereismyvm.git
#    echo "workers = 4" >> whereismyvm/gunicorn_config.py && \
#    echo 'bind = "0.0.0.0:7777"' >> whereismyvm/gunicorn_config.py && \
#    echo 'chdir = "/var/www/webtool/whereismyvm"' >> whereismyvm/gunicorn_config.py && \
#    echo 'module = "whereismyvm.wsgi:application"' >> whereismyvm/gunicorn_config.py

WORKDIR /var/www/webtool/whereismyvm
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7777

CMD ["gunicorn", "--bind", "0.0.0.0:7777", "whereismyvm.wsgi:application", "--timeout", "90" ]