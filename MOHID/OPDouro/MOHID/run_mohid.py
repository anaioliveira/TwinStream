##################################################################
#
#     Developed by: Ana Isabel Oliveira
#     Project: HazRunoff
#     Date: MARETEC IST, 29/10/2019
#
##################################################################


#!/usr/bin/python
# -*- coding: utf-8 -*-

# Imports
import os
import sys
import shutil
import subprocess
import datetime
import read_input_mohid_file

def check_active_modules(mohid_data_folder):

    fin = open(mohid_data_folder + 'Basin_1' + '.dat', 'r')
    
    for lin in fin:
        try:
            module = [x.strip() for x in lin.split(':')][0]
            value = [x.strip() for x in lin.split(':')][1]
            if module == "POROUS_MEDIA":
                global porous_media
                porous_media = int(value)
            elif module == "RUN_OFF":
                global run_off
                run_off = int(value)
            elif module == "DRAINAGE_NET":
                global drainage_network
                drainage_network = int(value)
            elif module == "VEGETATION":
                global vegetation
                vegetation = int(value)
            elif module == "POROUS_MEDIA_PROPERTIES":
                global porous_media_prop
                porous_media_prop = int(value)
            elif module == "RUN_OFF_PROPERTIES":
                global run_off_prop
                run_off_prop = int(value)
            elif module == "RESERVOIRS":
                global reservoirs
                reservoirs = int(value)
            elif module == "IRRIGATION":
                global irrigation
                irrigation = int(value)
            else:
                continue
                
            global basin
            basin = 1
            
        except:
            pass
    
    fin.close()

    return

def change_model_file(mohid_data_folder, date1, date2):

    fin_template = open(mohid_data_folder + 'Model.dat', 'r')
    fin_model = open(mohid_data_folder + 'Model_1' + '.dat', 'w')
    
    template = fin_template.readlines()
    
    for lin in template:
        if "begin_date" in lin:
            lin = lin.replace("begin_date", date1)
            fin_model.writelines(lin)
            
        elif "end_date" in lin:
            lin = lin.replace("end_date", date2)
            fin_model.writelines(lin)
        
        else:
            fin_model.writelines(lin)

    fin_template.close()
    fin_model.close()

    return

def manage_nomfich_file(mohid_data_folder, mohid_exe_folder, date1, restart_backup_folder):
    
    # Define source and destination
    source_file = mohid_data_folder + 'Nomfich_1' + '.dat'
    destination_file = mohid_exe_folder + 'nomfich.dat'
    
    # Copy nomfich file
    shutil.copyfile(source_file, destination_file)
    
    # Copy restart files from the folder that contains last simulation
    if not os.path.isdir(restart_backup_folder + date1):
        print ()
        print ('Folder ' + restart_backup_folder + date1 + ' does not exist!')
        sys.exit()
        
    # Change nomfich file
    fin = open(destination_file, 'a')
    
    fin.writelines('BASIN_INI                 : ' + restart_backup_folder + date1 + r'\Basin_1' + '.fin\n')
    
    if porous_media == 1:
        fin.writelines('POROUS_INI                : ' + restart_backup_folder + date1 + r'\PorousMedia_1' + '.fin\n')
    
    if run_off == 1:
        fin.writelines('RUNOFF_INI                : ' + restart_backup_folder + date1 + r'\RunOff_1' + '.fin\n')
    
    if drainage_network == 1:
        fin.writelines('DRAINAGE_NETWORK_INI      : ' + restart_backup_folder + date1 + r'\DrainageNetwork_1' + '.fin\n')
    
    if vegetation == 1:
        fin.writelines('VEGETATION_INI            : ' + restart_backup_folder + date1 + r'\Vegetation_1' + '.fin\n')
    
    if porous_media_prop == 1:
        fin.writelines('POROUS_PROP_INI           : ' + restart_backup_folder + date1 + r'\PorousMediaProperties_1' + '.fin\n')
    
    if run_off_prop == 1:
        fin.writelines('RUNOFF_PROP_INI           : ' + restart_backup_folder + date1 + r'\RunOffProperties_1' + '.fin\n')
    
    if reservoirs == 1:
        fin.writelines('RESERVOIRS_INI            : ' + restart_backup_folder + date1 + r'\Reservoirs_1' + '.fin\n')
        
    if irrigation == 1:
        fin.writelines('IRRIGATION_INI            : ' + restart_backup_folder + date1 + r'\Irrigation_1' + '.fin\n')

    fin.close()

    return

def copy_files_to_back_up(mohid_res_folder, hdf_backup_folder, timeseries_backup_folder, restart_backup_folder, date_folder_backup):

    hdf_folder = hdf_backup_folder + date_folder_backup.split('_')[0]    # specific for thredds twinstream
    hdf_folder = hdf_folder.replace('-','')       # specific for thredds twinstream
    timeseries_folder = timeseries_backup_folder + date_folder_backup
    restart_folder = restart_backup_folder + date_folder_backup
    
    if not os.path.isdir(hdf_folder):
        os.mkdir(hdf_folder)
    if not os.path.isdir(timeseries_folder):
        os.mkdir(timeseries_folder)
    if not os.path.isdir(restart_folder):
        os.mkdir(restart_folder)
    
    for filename in os.listdir(mohid_res_folder):
        if ".hdf5" in filename:
            source = mohid_res_folder + filename
            destination = hdf_folder + '/' + filename
            shutil.copyfile(source, destination)
        
        if ".fin" in filename:
            source = mohid_res_folder + filename
            destination = restart_folder + '/' + filename
            shutil.copyfile(source, destination)
            
    sub_dir = mohid_res_folder + 'Run1' + '/'
    for filename in os.listdir(sub_dir):
        source = sub_dir + filename
        destination = timeseries_folder + '/' + filename
        shutil.copyfile(source, destination)

    return

def write_log_file(log_file, log_text):

    fin = open(log_file, 'w')
    fin.write(log_text.decode("utf-8"))
    fin.close()
    
    return
    
def init(begin_date, end_date, working_dir):

    print ("--> Running MOHID Land.")
    
    # Change directory to glue script
    os.chdir(working_dir)

    ####### Get keywords values #######
    read_input_mohid_file.init()
    mohid_data_folder = read_input_mohid_file.mohid_data_folder
    mohid_exe_folder = read_input_mohid_file.mohid_exe_folder
    mohid_res_folder = read_input_mohid_file.mohid_res_folder
    
    hdf_backup_folder = read_input_mohid_file.hdf_backup_folder
    timeseries_backup_folder = read_input_mohid_file.timeseries_backup_folder
    restart_backup_folder = read_input_mohid_file.restart_backup_folder
    
    # Format dates
    date1 = begin_date.strftime('%Y %m %d' + ' 00 00 00')
    date2 = end_date.strftime('%Y %m %d' + ' 00 00 00')
    
    date1_ = begin_date.strftime('%Y%m%d')
    
    # Check active modules
    check_active_modules(mohid_data_folder)

    # Change dates in model file
    change_model_file(mohid_data_folder, date1, date2)
    
    #Manage the nomfich file according with continuous keyword
    sim_date_before_py = begin_date - datetime.timedelta(1)
    sim_date_before = sim_date_before_py.strftime('%Y-%m-%d')+'_'+begin_date.strftime('%Y-%m-%d')
    manage_nomfich_file(mohid_data_folder, mohid_exe_folder, sim_date_before, restart_backup_folder)
    
    # Run MOHID
    os.chdir(mohid_exe_folder)
    proc = subprocess.Popen("MOHIDLand.exe", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = proc.communicate()
    write_log_file(working_dir + r'\Logs\mohid_' + date1_ + '.log', stdout)
    if 'error' in str(stdout).lower() or 'err' in str(stdout).lower():
        commandResult = 0
        return commandResult

    # Copy results files to backup folders
    back_up_folder_dates = begin_date.strftime('%Y-%m-%d')+'_'+end_date.strftime('%Y-%m-%d')
    
    copy_files_to_back_up(mohid_res_folder, hdf_backup_folder, timeseries_backup_folder, restart_backup_folder, back_up_folder_dates)
    
    commandResult = 1
    return commandResult