@echo off

echo Populating test db ...
SET PGUSER=postgres
SET PGPASSWORD=Password12!
SET PATH=C:\Program Files\PostgreSQL\9.3\bin;%PATH%
SET PGHOST=localhost
echo create db
createdb tempus_test_db
echo postgis
psql -c "create extension postgis;" tempus_test_db
7z x data\tempus\tempus_test_db\tempus_test_db.sql.zip -o tempus_test_db.sql -y
psql tempus_test_db < tempus_test_db.sql
psql tempus_test_db < data\tempus\tempus_test_db\patch.001.sql
psql tempus_test_db < data\tempus\tempus_test_db\patch.002.sql
psql tempus_test_db < data\tempus\tempus_test_db\patch.003.sql

