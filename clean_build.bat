@echo off
echo Cleaning old CMake files...
if exist CMakeFiles rmdir /s /q CMakeFiles
if exist cmake_install.cmake del /f cmake_install.cmake
if exist CMakeCache.txt del /f CMakeCache.txt
if exist Makefile del /f Makefile

echo Generating new CMake files...
cmake -G "MinGW Makefiles" .
mingw32-make
