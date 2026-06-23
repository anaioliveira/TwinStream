# Developed by: Ana Ramos Oliveira
# Date: 03/02/2026
# Developed to own work

#!/usr/bin/python
# -*- coding: utf-8 -*-

# imports
import os, sys, subprocess
import requests
import datetime
import smtplib
from email.message import EmailMessage
from pathlib import Path

# user's definition
baseDirectory = 'D:\MLDATA02\Meteo\WRF_MeteoGalicia'
domains =  {'d01':'36km','d02':'12km', 'd03':'04km'}
base_url = 'https://thredds.meteogalicia.gal/thredds/fileServer/'
convertPath = '.\ConvertToHDF5'
extractorPath= '.\HDF5Extractor'
forecast_nDays = 4 #used to divide original file into days

# code
currentDay = datetime.datetime.combine(datetime.datetime.today(), datetime.datetime.min.time())
currentDayStrDownload = currentDay.strftime('%Y%m%d')

def send_email(text):
    
    msg = EmailMessage()
    msg["From"] = 'operacionaismohidland@gmail.com'
    msg["To"] = 'anaramosoliveira@tecnico.ulisboa.pt'
    msg["Subject"] = 'Error in MeteoGalicia.'
    msg.set_content(text)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login('***********', '***********')
        server.send_message(msg)
    
    return

def download_meteo_ncfile():
    
    outfile_list_nc = []
    
    # iterate all domains
    for key, value in domains.items():
        
        # create url and out file for the file of 12 pm
        url = f'{base_url}/wrf_2d_{value}/fmrc/files/{currentDayStrDownload}/wrf_arw_det_history_{key}_{currentDayStrDownload}_1200.nc4'
        outfile = f'{baseDirectory}/{key}/nc/wrf_arw_det_history_{key}_{currentDayStrDownload}_0000.nc4'
        outfile_list_nc.append(outfile)
        
        # check if file already exists
        try:
            #response = urllib.request.urlopen(url)
            r = requests.get(url, timeout=60, stream=True)
            r.raise_for_status()  # raises HTTPError for 4xx/5xx

            # write to file in chunks (safe for large files)
            with open(outfile, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive chunks
                        f.write(chunk)
        except requests.exceptions.RequestException as e:
            text = f'Error downloading file {url}: {e}.'
            send_email(text)
            sys.exit()
    
    return outfile_list_nc

def nc_to_hdf(outfile_list_nc):
    
    os.chdir(convertPath)
    in_file = 'ConvertToHDF5Action_NetCDFToHDF.dat'
    out_file = 'ConvertToHDF5Action.dat'
    outfile_list_hdf = []
    
    # loop downloaded nc files
    for nc_file in outfile_list_nc:
        lines_list = []
        nc_directory, nc_filename = os.path.split(nc_file)
        # open input template file for converter
        with open(in_file, 'r') as fin:
            # check lines in template file and change those needed
            for line in fin:
                if 'output_hdf_file' in line:
                    hdf_directory = nc_directory.replace('nc', '')
                    hdf_filename = nc_filename.replace('.nc4', '.hdf5')
                    outfile_list_hdf.append(os.path.join(hdf_directory, hdf_filename))
                    line = line.replace('output_hdf_file', os.path.join(hdf_directory, hdf_filename))
                    lines_list.append(line)
                elif 'output_grid_file' in line:
                    grid_directory = nc_directory.replace('nc', 'hdf')
                    grid_filename = nc_filename.replace('.nc4', '.dat')
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

    return outfile_list_hdf

def daily_hdf(outfile_list_hdf):
    
    os.chdir(extractorPath)
    in_file = 'HDF5Extractor_temp.dat'
    out_file = 'HDF5Extractor.dat'
    start_date = currentDay+datetime.timedelta(days=1) # the first day does not have the first 12h
    
    for hdf_file in outfile_list_hdf:
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
                        line = line.replace('input_file', hdf_file)
                        lines_list.append(line)
                    elif 'output_file' in line:
                        output_file_directory = os.path.dirname(hdf_file)
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
                text = 'Error extracting daily files from '+hdf_file+'.'
                send_email(text)
            
            # reset the start date
            start_date = end_date
        
        # restart date for the next hdf file
        start_date = currentDay+datetime.timedelta(days=1) # the first day does not have the first 12h
        
        os.remove(hdf_file)

    os.chdir('..')

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

outfile_list_nc = download_meteo_ncfile()
outfile_list_hdf = nc_to_hdf(outfile_list_nc)
daily_hdf(outfile_list_hdf)
delete_old_files()