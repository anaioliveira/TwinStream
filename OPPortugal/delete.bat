@echo off
:: set min age of files and folders to delete
set max_days=60

:::: set folder path
::set dump_path=F:\OperationalModels\OPMaranhao\Results\HDF
:::: remove files from %dump_path%
::forfiles -p %dump_path% -m *.* -d -%max_days% -c "cmd  /c del /q @path"
:::: remove sub directories from %dump_path%
::forfiles -p %dump_path% -d -%max_days% -c "cmd /c IF @isdir == TRUE rd /S /Q @path"

:::: set folder path
::set dump_path=E:\Lucian\OPMaranhao\Results\Restart
:::: remove files from %dump_path%
::forfiles -p %dump_path% -m *.* -d -%max_days% -c "cmd  /c del /q @path"
:::: remove sub directories from %dump_path%
::forfiles -p %dump_path% -d -%max_days% -c "cmd /c IF @isdir == TRUE rd /S /Q @path"

:: set folder path
set dump_path=F:\OperationalModels\OPGuadiana\Results\Timeseries
:: remove files from %dump_path%
forfiles -p %dump_path% -m *.* -d -%max_days% -c "cmd  /c del /q @path"
:: remove sub directories from %dump_path%
forfiles -p %dump_path% -d -%max_days% -c "cmd /c IF @isdir == TRUE rd /S /Q @path"