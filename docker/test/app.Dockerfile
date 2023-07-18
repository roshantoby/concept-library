FROM python:3.9-slim-bullseye

ARG server_name

ENV SERVER_NAME $server_name
ENV PYTHONUNBUFFERED 1
ENV LC_ALL=C.UTF-8

# Update packages
RUN \
  apt-get update -y -q && \
  apt-get upgrade -y -q && \
  apt-get install -y -q --no-install-recommends apt-utils && \
  apt-get install -y -q ssh apache2 && \
  apt-get install -y -q libapache2-mod-wsgi-py3 && \
  apt-get install -y -q wget && \
  apt-get -y -q install sudo nano && \
  apt-get install -y -q dos2unix && \
  apt-get install -y -q curl && \
  apt-get install -y -q ca-certificates

# Install LDAP deps
RUN apt-get install -y -q libsasl2-dev libldap2-dev libssl-dev

# Install npm
RUN apt-get update && apt-get install -y \
    software-properties-common \
    npm

# Install esbuild
RUN npm install -g config set user root \
    npm install -g esbuild

# Instantiate log dir
RUN ["mkdir", "-p", "/home/config_cll/cll_srvr_logs"]
RUN ["chmod", "750", "/home/config_cll/cll_srvr_logs"]

# Set main workdir
WORKDIR /var/www

# Install & upgrade pip
RUN \
  apt-get install -y -q python3-pip

RUN \
  pip install --upgrade pip

# Copy & Install requirements
RUN mkdir -p /var/www/concept_lib_sites/v1
COPY ./requirements /var/www/concept_lib_sites/v1/requirements
RUN ["chown", "-R" , "www-data:www-data", "/var/www/concept_lib_sites/"]

RUN pip --no-cache-dir install -r /var/www/concept_lib_sites/v1/requirements/production.txt

# Utility scripts
RUN ["chown" , "-R" , "www-data:www-data" , "/var/www/"]

COPY ./development/scripts/wait-for-it.sh /bin/wait-for-it.sh
RUN ["chmod", "u+x", "/bin/wait-for-it.sh"]
RUN ["dos2unix", "/bin/wait-for-it.sh"]

# Deploy scripts
COPY ./production/scripts/init-app.sh /home/config_cll/init-app.sh
COPY ./production/scripts/worker-start.sh /home/config_cll/worker-start.sh
COPY ./production/scripts/beat-start.sh /home/config_cll/beat-start.sh

RUN ["chmod" , "+x" , "/home/config_cll/worker-start.sh"]
RUN ["chmod" , "+x" , "/home/config_cll/beat-start.sh"]
RUN ["chmod", "a+x", "/home/config_cll/init-app.sh"]

# Config apache and enable site
RUN echo $(printf 'export SERVER_NAME=%s' "$SERVER_NAME") >> /etc/apache2/envvars
RUN echo $(printf 'ServerName %s' "$SERVER_NAME") >> /etc/apache2/apache2.conf
ADD ./production/cll.conf /etc/apache2/sites-available/cll.conf

RUN a2ensite \
    cll.conf && \
  a2enmod \
    wsgi \
    env \
    rewrite \
    headers \
    expires && \
  a2dissite 000-default
