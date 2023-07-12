FROM python:3.9-slim

# Install and update packages
RUN apt-get update -y -q && \
    apt-get upgrade -y -q && \
    apt-get install dos2unix

# Install LDAP header files
RUN apt-get install -y -q libsasl2-dev libldap2-dev libssl-dev

# Install npm
RUN apt-get update && apt-get install -y \
    software-properties-common \
    npm

# Install esbuild
RUN npm install -g config set user root \
    npm install -g esbuild

# Install pip
RUN apt-get install -y -q python3-pip 

# Install Python packages
COPY ./requirements/ /home/requirements/
RUN pip install -r /home/requirements/local.txt

COPY ./development/scripts/wait-for-it.sh /bin/wait-for-it.sh
RUN chmod u+x /bin/wait-for-it.sh
RUN dos2unix /bin/wait-for-it.sh
