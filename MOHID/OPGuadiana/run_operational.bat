::@echo off

cd F:
cd F:\OperationalModels\OPGuadiana
call C:\ProgramData\anaconda3\envs\opguadiana_env\python.exe run_operational.py > operational.log
::call C:\ProgramData\anaconda3\envs\opguadiana_env\python.exe run_operational.py

:: delete old files
:: set min age of files and folders to delete
set max_days=60

:: set folder path
set dump_path=\\thredds\thredds\MOHID_Land\Watersheds\Guadiana
:: remove files from %dump_path%
forfiles -p "%dump_path%" -m *.* -d -%max_days% -c "cmd /c if exist @path del /q @path" 2>nul
:: remove sub directories from %dump_path%
forfiles -p "%dump_path%" -d -%max_days% -c "cmd /c IF @isdir == TRUE if exist @path rd /S /Q @path" 2>nul

:: set folder path
set dump_path=F:\OperationalModels\OPGuadiana\Results\Restart
:: remove files from %dump_path%
forfiles -p "%dump_path%" -m *.* -d -%max_days% -c "cmd /c if exist @path del /q @path" 2>nul
:: remove sub directories from %dump_path%
forfiles -p "%dump_path%" -d -%max_days% -c "cmd /c IF @isdir == TRUE if exist @path rd /S /Q @path" 2>nul

:: set folder path
set dump_path=F:\OperationalModels\OPGuadiana\Results\Timeseries
:: remove files from %dump_path%
forfiles -p "%dump_path%" -m *.* -d -%max_days% -c "cmd /c if exist @path del /q @path" 2>nul
:: remove sub directories from %dump_path%
forfiles -p "%dump_path%" -d -%max_days% -c "cmd /c IF @isdir == TRUE if exist @path rd /S /Q @path" 2>nul

echo Finished!

::pause