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
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

# user's definition
baseDirectory = 'D:\MLDATA02\Meteo\WRF_MARETEC\Forecast'
base_url = 'http://caboruivo.tecnico.ulisboa.pt:64106/thredds/fileServer/pt_3km_forecast'
convertPath = '.\ConvertToHDF5'
extractorPath= '.\HDF5Extractor'
forecast_nDays = 7 #used to divide original file into days

# code
currentDay = datetime.datetime.combine(datetime.datetime.today(), datetime.datetime.min.time())
currentDayStrDownload = currentDay.strftime('%Y%m%d')

def send_email(text):
    
    msg = EmailMessage()
    msg["From"] = 'operacionaismohidland@gmail.com'
    msg["To"] = 'anaramosoliveira@tecnico.ulisboa.pt'
    msg["Subject"] = 'Error in WRF MARETEC.'
    msg.set_content(text)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login('***********', '***********')
        server.send_message(msg)
    
    return

def download_meteo_ncfile():
    
    url = f'{base_url}/wrfout_last_zip.nc'
    outfile_nc = f'{baseDirectory}/nc/wrfout_last_zip.nc'
    
    with requests.Session() as session:
        session.auth = HTTPBasicAuth('***********', '***********')
        
        try:
            r = session.get(url, stream=True, allow_redirects=True)
            
            # Fallback to Digest Auth if needed
            if r.status_code in [401, 403] and isinstance(session.auth, HTTPBasicAuth):
                session.auth = HTTPDigestAuth('***********', '***********')
                r = session.get(url, stream=True, allow_redirects=True)

            if r.status_code != 200:
                text = 'Error downloading file '+url+'.'
                send_email(text)
                sys.exit()

            # Prep output and progress tracking
            total_size = int(r.headers.get('content-length', 0))
            chunk_size = 128 * 1024 # 128 KB
            
            with open(outfile_nc, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)

        except Exception as e:
            text = 'Error downloading file '+url+'.'
            send_email(text)
            sys.exit()
    
    return outfile_nc

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
                hdf_directory = nc_directory.replace('nc', 'hdf')
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

    os.chdir('..')

    return outfile_hdf

def daily_hdf(outfile_hdf):
    
    os.chdir(extractorPath)
    in_file = 'HDF5Extractor_temp.dat'
    out_file = 'HDF5Extractor.dat'
    start_date = currentDay+datetime.timedelta(days=1) # the first day does not have the first 6h
    
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
                    line = line.replace('output_file', os.path.join(output_file_directory, output_file_filename))
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

outfile_nc = download_meteo_ncfile()
outfile_hdf = nc_to_hdf(outfile_nc)
daily_hdf(outfile_hdf)
delete_old_files()