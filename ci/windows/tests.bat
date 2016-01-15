cd c:\projects\tempus
SET PGUSER=postgres
SET PGPASSWORD=Password12!
SET PATH=C:\Program Files\PostgreSQL\9.3\bin;%PATH%
SET PGHOST=localhost

echo create db
createdb tempus_test_db
echo install postgis extension
psql -c "create extension postgis" tempus_test_db
echo populate test db
cd data\tempus_test_db
psql -f c:tempus_test_db.sql tempus_test_db
echo apply patches
for /r %%i in (patch.???.sql) do psql tempus_test_db < %%i
cd c:\projects\tempus

echo run tests ...
ctest -VV
