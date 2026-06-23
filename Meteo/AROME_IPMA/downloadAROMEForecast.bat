@echo off
cd D:\MLDATA02\Meteo\AROME_IPMA

call C:\ProgramData\anaconda3\Scripts\activate.bat

conda run -n meteo_env python downloadAROMEForecast.py > downloadAROMEForecast.log 2>&1

::pause