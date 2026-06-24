# Developed by: Ana Ramos Oliveira
# Date: 03/02/2026
# Developed to own work

#!/usr/bin/python
# -*- coding: utf-8 -*-

# imports
import os, sys, subprocess
import urllib.request
import datetime
import smtplib
from email.message import EmailMessage
from pathlib import Path
import paramiko, stat, shutil
import xarray as xr

# user's definitions
person_in_charge = '***********'

baseDirectory = 'D:\MLDATA02\Meteo\AROME_IPMA'
ftp_key = '***********'
convertPath = '.\ConvertToHDF5'
extractorPath= '.\HDF5Extractor'
forecast_nDays = 2 #used to divide original file into days

download_historical = False
date_to_dowload = '02/03/2026' #day/month/year if historical is True

# code
if not download_historical:
    currentDay = datetime.datetime.combine(datetime.datetime.today(), datetime.datetime.min.time())
else:
    currentDay = datetime.datetime.strptime(date_to_dowload, '%d/%m/%Y')

currentDayStrDownload = currentDay.strftime('%Y%m%d')

def send_email(text):
    
    msg = EmailMessage()
    msg["From"] = 'operacionaismohidland@gmail.com'
    msg["To"] = person_in_charge
    msg["Subject"] = 'Error in AROME.'
    msg.set_content(text)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login('***********', '***********')
        server.send_message(msg)    
    
    return

def download_meteo_ncfile():
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(
            hostname='***********',
            username='***********',
            key_filename=ftp_key)

        sftp = ssh.open_sftp()

        out_dir = f'{baseDirectory}/nc/{currentDayStrDownload}'
        os.makedirs(f'{baseDirectory}/nc/{currentDayStrDownload}', exist_ok=True)
        
        if not download_historical:
            sftp_dir = f'AROME/{currentDayStrDownload}12/'
        else:
            sftp_dir = f'AROME/historico/{currentDayStrDownload}12/'
        
        for item in sftp.listdir_attr(sftp_dir):
            remote_item = f'{sftp_dir}{item.filename}'
            local_item = os.path.join(out_dir, item.filename)
            if not stat.S_ISDIR(item.st_mode):
                sftp.get(remote_item, local_item)
            else:
                text = 'Error downloading file '+remote_item+'.'
                send_email(text)
                sys.exit()
        
        sftp.close()
        ssh.close()
    except:
        text = 'Error connecting the ftp or downloading files.'
        send_email(text)
        sys.exit()
    
    return out_dir

def deaccumulate(var, var_name):

    # subtract each step from the previous one
    var_instant = var.diff(dim='step')

    # first timestep has no previous — keep it as-is or set to NaN
    var_instant = xr.concat([var.isel(step=0), var_instant], dim='step')

    # clip negative values (can occur at midnight/reset points)
    var_instant = var_instant.clip(min=0)
    
    # reorder dims
    var_instant = var_instant.transpose("step", "latitude", "longitude")

    # transform to dataset
    var_instant = var_instant.rename({'unknown': var_name})
    
    if var_name == 'swavr':
        var_instant = var_instant / 3600 # hourly data as this case
        var_instant.attrs["units"] = "W m**-2"
    
    return var_instant

def glue_nc_arome_files(out_dir):
    
    outfile_nc = ''
    try:
        outfile_nc = f'{baseDirectory}/nc/{currentDayStrDownload}.nc'
        
        # Open each file and get specific variable
        tp = xr.open_dataset(f'{out_dir}/AROME_OPER_SF_PT2_025_{currentDayStrDownload}12_tp', engine='cfgrib', backend_kwargs={'indexpath': ''})
        tp_var = tp[['unknown']]
        tp_var = deaccumulate(tp_var, 'tp')
        tp.close()
        t2 = xr.open_dataset(f'{out_dir}/AROME_OPER_SF_PT2_025_{currentDayStrDownload}12_2t', engine='cfgrib', backend_kwargs={'indexpath': ''})
        t2_var = t2[['t2m']]
        t2.close()
        u10 = xr.open_dataset(f'{out_dir}/AROME_OPER_SF_PT2_025_{currentDayStrDownload}12_10u', engine='cfgrib', backend_kwargs={'indexpath': ''})
        u10_var = u10[['u10']]
        u10.close()
        v10 = xr.open_dataset(f'{out_dir}/AROME_OPER_SF_PT2_025_{currentDayStrDownload}12_10v', engine='cfgrib', backend_kwargs={'indexpath': ''})
        v10_var = v10[['v10']]
        v10.close()
        rh = xr.open_dataset(f'{out_dir}/AROME_OPER_SF_PT2_025_{currentDayStrDownload}12_r', engine='cfgrib', backend_kwargs={'indexpath': ''})
        rh_var = rh[['r']]/100
        rh.close()
        sr = xr.open_dataset(f'{out_dir}/AROME_OPER_SF_PT2_025_{currentDayStrDownload}12_swavr', engine='cfgrib', backend_kwargs={'indexpath': ''})
        sr_var = sr[['unknown']]
        sr_var = deaccumulate(sr_var, 'swavr')
        sr.close()
        
        # Merge all into one
        merged = xr.merge([tp_var, t2_var, u10_var, v10_var, rh_var, sr_var], compat='override')
    
        # Save
        merged.to_netcdf(outfile_nc)
        
        # delete directory
        shutil.rmtree(out_dir)
        
        return outfile_nc
    except:
        text = 'Error glueing netcdf files.'
        send_email(text)
        sys.exit()

def nc_to_hdf(nc_file):
    
    os.chdir(convertPath)
    in_file = 'ConvertToHDF5Action_NetCDFToHDF.dat'
    out_file = 'ConvertToHDF5Action.dat'

    lines_list = []
    nc_directory, nc_filename = os.path.split(nc_file)
    # open input template file for converter
    with open(in_file, 'r') as fin:
        # check lines in template file and change those needed
        for line in fin:
            if 'output_hdf_file' in line:
                hdf_directory = nc_directory.replace('nc', '')
                hdf_filename = nc_filename.replace('.nc', '.hdf5')
                outfile_hdf = os.path.join(hdf_directory, hdf_filename)
                line = line.replace('output_hdf_file', outfile_hdf)
                lines_list.append(line)
            elif 'output_grid_file' in line:
                grid_directory = nc_directory.replace('nc', 'hdf')
                grid_filename = nc_filename.replace('.nc', '.dat')
                line = line.replace('output_grid_file', os.path.join(grid_directory, grid_filename))
                lines_list.append(line)
            elif 'input_nc_file' in line:
                line = line.replace('input_nc_file', nc_file)
                lines_list.append(line)
            else:
                lines_list.append(line)
    
    # write converter file
    with open(out_file, 'w') as fout:
        fout.writelines(f'{item}' for item in lines_list)
    
    # run converter and check errors
    out = subprocess.run(['ConvertToHDF5.exe'], stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE, text=True,
    creationflags=subprocess.CREATE_NO_WINDOW).stdout
    if not 'successfully' in out.lower():
        text = 'Error converting file '+nc_file+'.'
        send_email(text)
        sys.exit()

    os.chdir('..')

    return outfile_hdf

def daily_hdf(outfile_hdf):
    
    os.chdir(extractorPath)
    in_file = 'HDF5Extractor_temp.dat'
    out_file = 'HDF5Extractor.dat'
    start_date = currentDay+datetime.timedelta(days=1) # the first day does not have the first 12h
    
    while start_date <= currentDay+datetime.timedelta(days=forecast_nDays):
        # create end date for mohid
        end_date = start_date+datetime.timedelta(days=1)
        
        # create mohid date strings
        start_date_str = start_date.strftime('%Y %m %d %H %M %S')
        end_date_str = end_date.strftime('%Y %m %d %H %M %S')
        lines_list = []
        
        # read template file and change lines
        with open(in_file, 'r') as fin:
            for line in fin:
                if 'input_file' in line:
                    line = line.replace('input_file', outfile_hdf)
                    lines_list.append(line)
                elif 'output_file' in line:
                    output_file_directory = os.path.dirname(outfile_hdf)
                    output_file_filename = start_date.strftime('%Y%m%d')+'.hdf5'
                    line = line.replace('output_file', os.path.join(output_file_directory+'/hdf/', output_file_filename))
                    lines_list.append(line)
                elif 'start_date' in line:
                    line = line.replace('start_date', start_date_str)
                    lines_list.append(line)
                elif 'end_date' in line:
                    line = line.replace('end_date', end_date_str)
                    lines_list.append(line)
                else:
                    lines_list.append(line)

        # write extractor input file
        with open(out_file, 'w') as fout:
            fout.writelines(f'{item}' for item in lines_list)
        
        # run extractor and check errors
        out = subprocess.run(['HDF5Extractor.exe'], stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, text=True,
        creationflags=subprocess.CREATE_NO_WINDOW).stdout
        if not 'successfully' in out.lower():
            text = 'Error extracting daily files from '+outfile_hdf+'.'
            send_email(text)
            sys.exit()
        
        # reset the start date
        start_date = end_date

    os.chdir('..')
    os.remove(outfile_hdf)

    return

def delete_old_files():
    
    base_dir = Path(baseDirectory)
    files = [f for f in base_dir.rglob("*") if f.suffix.lower() in [".nc4", ".hdf5"]]

    olderDate = currentDay-datetime.timedelta(days=30)
    for f in files:
        f_time = datetime.datetime.fromtimestamp(f.stat().st_mtime)
        if f_time < olderDate:
            os.remove(f)

    return None

out_dir = download_meteo_ncfile()
outfile_nc = glue_nc_arome_files(out_dir)
outfile_hdf = nc_to_hdf(outfile_nc)
daily_hdf(outfile_hdf)
delete_old_files()