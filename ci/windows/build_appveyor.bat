@echo off

echo Running cmake...
cd c:\projects\tempus
cmake -G "NMake Makefiles" -DCMAKE_BUILD_TYPE=RelWithDebInfo -DBUILD_DOC=OFF -DBUILD_OSM2SHP=OFF -DBUILD_QGIS_PLUGIN -DBUILD_WPS=OFF

nmake