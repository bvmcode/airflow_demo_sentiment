FROM apache/airflow:2.6.3-python3.8
COPY requirements.txt requirements.txt
USER root
RUN apt update
RUN apt install git -y
RUN apt-get install build-essential python3-dev libldap2-dev libsasl2-dev slapd ldap-utils tox lcov valgrind -y
USER airflow
RUN pip3.8 install --upgrade pip setuptools wheel
RUN pip3.8 install -r requirements.txt