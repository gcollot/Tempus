cd c:\projects\tempus
echo Populating test db ...
SET PGUSER=postgres
SET PGPASSWORD=Password12!
SET PATH=C:\Program Files\PostgreSQL\9.3\bin;%PATH%
SET PGHOST=localhost
createdb tempus_test_db
psql -c "create extension postgis;" tempus_test_db
cd data\tempus\tempus_test_db
7z x tempus_test_db.sql.zip -o tempus_test_db.sql -y
psql tempus_test_db < tempus_test_db.sql
for /r %%i in (patch.???.sql) do psql tempus_test_db < %%i
cd c:\projects\tempus

ctest -VV
