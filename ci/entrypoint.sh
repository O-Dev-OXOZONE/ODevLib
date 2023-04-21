#!/bin/sh

service postgresql start
sleep 5

# setup the database
su postgres -c "psql -c \"CREATE ROLE odevlib_example LOGIN SUPERUSER PASSWORD 'odevlib_example';"\"
su postgres -c 'psql -c "CREATE DATABASE odevlib_example owner odevlib_example;"'

pytest --cov=odevlib --cov-report=xml --cov-report=term-missing

service postgresql stop
