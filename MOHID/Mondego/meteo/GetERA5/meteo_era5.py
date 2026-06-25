##################################################################
#
#     Developed by: Ana Isabel Oliveira
#     Project: TwinStream
#     Date: MARETEC IST, 01/09/2025
#
##################################################################

#!/usr/bin/python

import sys, os, shutil, datetime, subprocess, numpy, cdsapi, glob, netCDF4
from dateutil.relativedelta import relativedelta
sys.path.insert(0, '../GetERA5/aux_scripts')
import change_coordinates, calculate_new_fields, write_converttohdfaction_file

def get_dates_py(d_str):

    d_py = datetime.datetime.strptime(d_str, "%d/%m/%Y")

    return d_py

def get_date_string(d_py):

    d_str = d_py.strftime('%d/%m/%Y')

    return d_str

def change_date_to_era5(date_to_print):

    d1 = date_to_print.split("/")
    day = d1[0]
    month = d1[1]
    year = d1[2]
    d_era5 = year + '-' + month + '-' +  day

    return d_era5

def getERA5(date, parameters, w, suffix):

    year = date.split('-')[0]
    month = date.split('-')[1]
    day = date.split('-')[2]

    dataset = "reanalysis-era5-single-levels"
    request = {"product_type": ['reanalysis'],
                "variable": parameters,
                "year": year,
                "month": month,
                "day": day,
                "time": [
                    "00:00", "01:00", "02:00",
                    "03:00", "04:00", "05:00",
                    "06:00", "07:00", "08:00",
                    "09:00", "10:00", "11:00",
                    "12:00", "13:00", "14:00",
                    "15:00", "16:00", "17:00",
                    "18:00", "19:00", "20:00",
                    "21:00", "22:00", "23:00"
                ],
                "data_format": "netcdf",
                "download_format": "unarchived",
                "area": w
            }
    
    client = cdsapi.Client()
    client.retrieve(dataset, request).download(date+'_'+suffix + '.nc')

    return

def join_netcdfs(date):
    
    nc_files = glob.glob(work_folder+'*.nc')
    
    shutil.copyfile(nc_files[0], date+'.nc')
    
    # open file to copy
    fin = netCDF4.Dataset(nc_files[1], 'r')
    
    # open file to receive variables
    fout = netCDF4.Dataset(date+'.nc', 'r+')
    
    # Copy variables
    for v_name, varin in fin.variables.items():
        if 'time' in v_name or 'lon' in v_name or 'lat' in v_name or 'number' in v_name or 'expver' in v_name:
            pass
        else:
            outVar = fout.createVariable(v_name, varin.datatype, varin.dimensions)
        
            # Copy variable attributes
            outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
            
            outVar[:] = varin[:]
    
    fin.close()
    fout.close()
    
    for ncf in nc_files:
        os.remove(ncf)
    
    return

def get_father_grid(grid_input_file, interpolate_folder):

    begin_data_line = 0
    end_data_line = 0
    
    with open(grid_input_file, 'r') as fin:
        with open(interpolate_folder+'/ERA5_grid.dat', 'w') as fout:
            for line in fin:
                if '<BeginGridData2D>' in line:
                    begin_data_line = 1
                elif '<EndGridData2D>' in line:
                    end_data_line = 1
                else:
                    pass
                
                if begin_data_line == 1 and end_data_line == 0 and '<BeginGridData2D>' in line:
                    fout.write(line)
                elif begin_data_line == 1 and end_data_line == 0:
                    fout.write('1\n')
                else:
                    fout.write(line)

    return

############# MAIN FUNCTION #############
if __name__ == '__main__':

    begin_date = "25/12/2025"
    end_date = "01/05/2026"
    parameters_inst = ['10m_u_component_of_wind',
        '10m_v_component_of_wind',
        '2m_dewpoint_temperature',
        '2m_temperature',
        'total_cloud_cover',
        'snow_albedo',
        'snow_depth']
    parameters_acc = ['total_precipitation',
        'surface_solar_radiation_downwards']
    window = [45, -14, 33, 2] #N/W/S/E
    casestudy_grid = 'ERA5_Minho.dat'
    #######
    get_meteo_files = 0
    convert_and_interpolate = 1
    transform_wind_to_2m = 1

    #Define folders
    work_folder = '../GetERA5/'
    original_netcdf_ERA5 = '../ERA5OriginalFiles/'
    interpolated_files = '../InterpolatedFiles/'
    convert_folder = '../ConvertToHDF5_Convert/'
    interpolate_folder = '../ConvertToHDF5_Interpolate/'

    #Define template files location
    convert_netcdftohdf = 'ConvertToHDF5Action_NetCDFToHDF.dat'
    interpolate = 'ConvertToHDF5Action_Interpolate.dat'

    # Initialize variables
    end_date_py = get_dates_py(end_date)
    actual_date_py = get_dates_py(begin_date)

    #Start
    while actual_date_py <= end_date_py:
        date_to_print = get_date_string(actual_date_py)

        print
        print('\x1b[0;33;40m' + "# # # # # # # # # # # # # # # # # # # #" + '\x1b[0m')
        print('\x1b[0;33;40m' + "        Doing " + date_to_print + " ..." + '\x1b[0m')
        print('\x1b[0;33;40m' + "# # # # # # # # # # # # # # # # # # # #" + '\x1b[0m')

        date = change_date_to_era5(date_to_print)
        # Get ERA 5 file
        if get_meteo_files == 1:
            getERA5(date, parameters_inst, window, 'inst')
            getERA5(date, parameters_acc, window, 'acc')
            join_netcdfs(date)
            shutil.move(date + '.nc ', original_netcdf_ERA5 + date + '.nc')

        # Get ERA 5 file
        if convert_and_interpolate == 1:
            shutil.copy(original_netcdf_ERA5 + date + '.nc', work_folder + date + '.nc')

            print ('\x1b[0;36;40m Making adjustments in fields... \x1b[0m')
            #Modify longitude coordinates to [-180,180]
            change_coordinates.change_coord(work_folder + date + '.nc')

            #Calculate new_fields
            calculate_new_fields.calculate_fields(work_folder + date + '.nc', work_folder + date + '_.nc', transform_wind_to_2m)

            #Convert NetCDF to HDF5 (with MOHID tool)
            os.chdir(convert_folder)
            print ('\x1b[0;36;40m Converting NetCDF to HDF5... \x1b[0m')
            write_converttohdfaction_file.write_file(convert_folder + convert_netcdftohdf, work_folder + date + '_.nc', 'convert')
            os.system(convert_folder + "ConvertToHDF5.exe")
            
            #Get father grid
            if actual_date_py == get_dates_py(begin_date):
                get_father_grid(convert_folder+'/Batim.dat', interpolate_folder)

            #Interpolate HDF5 file
            os.chdir(interpolate_folder)
            print ('\x1b[0;36;40m Interpolating HDF5... \x1b[0m')
            write_converttohdfaction_file.write_file(interpolate_folder + interpolate, work_folder + date + '_.hdf5', 'interpolate', actual_date_py, casestudy_grid)
            os.system(interpolate_folder + "ConvertToHDF5.exe")
            shutil.move(work_folder + date + '__interpolated.hdf5', interpolated_files + date.replace('-', '') + '.hdf5')

            #Delete auxiliar files
            os.chdir(work_folder)
            for item in os.listdir(work_folder):
                if item.endswith(".hdf5") or item.endswith(".nc"):
                    os.remove(os.path.join(work_folder, item))

        actual_date_py += relativedelta(days=1)