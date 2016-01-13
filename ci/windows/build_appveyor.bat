@echo off

ECHO activating VS command prompt
IF /I "%platform%"=="x64" ECHO x64 && CALL "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\vcvarsall.bat" amd64
IF /I "%platform%"=="x86" ECHO x86 && CALL "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\vcvarsall.bat" x86
IF %ERRORLEVEL% NEQ 0 GOTO ERROR

ECHO Downloading boost ...
curl -o boost.exe -fsS "http://iweb.dl.sourceforge.net/project/boost/boost-binaries/1.59.0/boost_1_59_0-msvc-14.0-%platform%".exe
echo launching
boost.exe /DIR=C:\libs\boost_1_59_0 /verysilent
set BOOST_ROOT="C:/libs/boost_1_9_0"

echo Running cmake...
cd c:\projects\tempus
cmake -G "NMake Makefiles" -DCMAKE_BUILD_TYPE=RelWithDebInfo -DBUILD_DOC=OFF -DBUILD_OSM2SHP=OFF -DBUILD_QGIS_PLUGIN=OFF -DBUILD_WPS=OFF

nmake

GOTO DONE



:ERROR
ECHO ~~~~~~~~~~~~~~~~~~~~~~ ERROR %~f0 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
ECHO ERRORLEVEL^: %ERRORLEVEL%
SET EL=%ERRORLEVEL%

:DONE
ECHO ~~~~~~~~~~~~~~~~~~~~~~ DONE %~f0 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
ECHO build started^: %NODE_GDAL_BUILD_START_TIME%
ECHO build finished^: %NODE_GDAL_BUILD_FINISH_TIME%

EXIT /b %EL%