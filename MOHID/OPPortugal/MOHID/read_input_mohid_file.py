##################################################################
#
#     Developed by: Ana Isabel Oliveira
#     Project: Water4Ever
#     Date: MARETEC IST, 16/07/2018
#
##################################################################


#!/usr/bin/python
# -*- coding: utf-8 -*-

# Imports
import os
import sys

def read_file(input_file):

    fin = open(input_file)

    for lin in fin:
    
        try:
            if not lin.strip() or lin.strip().startswith('#'):
                continue
                
            aux_line = lin.split(':', 1)
            keyword = aux_line[0].strip()
            value = aux_line[1].split('#')[0].strip()

            if "MOHID_DATA_FOLDER" in keyword:
                global mohid_data_folder
                mohid_data_folder = value.lower()
                
            elif "MOHID_EXE_FOLDER" in keyword:
                global mohid_exe_folder
                mohid_exe_folder = value.lower()
                
            elif "MOHID_RES_FOLDER" in keyword:
                global mohid_res_folder
                mohid_res_folder = value.lower()
                
            elif "HDF_BACKUP_FOLDER" in keyword:
                global hdf_backup_folder
                hdf_backup_folder = value.lower()
                
            elif "TIMESERIES_BACKUP_FOLDER" in keyword:
                global timeseries_backup_folder
                timeseries_backup_folder = value.lower()
                
            elif "RESTART_BACKUP_FOLDER" in keyword:
                global restart_backup_folder
                restart_backup_folder = value.lower()
            
            # INTERNATIONAL DISCHARGE ACTIVATION FLAG
            if "INTERNATIONAL_BASIN" == keyword:
                global international_basin_active
                international_basin_active = (value.strip() == '1')
                                
            elif "BASINS_NAMES" == keyword:
                global basin_names
                basin_names = [x.strip() for x in value.split(',')]
                #print(f"International basins ---> {basin_names}")
            
            elif keyword.startswith("BASIN"):
                var_name = keyword.lower() # transforma BASIN1 em basin1
                globals()[var_name] = value.strip()
                
            elif "MAIN_MODEL_FOLDER" in keyword:
                global main_model_folder
                main_model_folder = value.strip()
                
            else:
                    pass
        except:
            pass

    fin.close()
    
    return

def check_variables():

    if not 'mohid_data_folder' in globals():
        print ('\n   ERROR:      Please define keyword MOHID_DATA_FOLDER. \n')
        sys.exit()
        
    if not 'mohid_exe_folder' in globals():
        print ('\n   ERROR:      Please define keyword MOHID_EXE_FOLDER. \n')
        sys.exit()
        
    if not 'mohid_res_folder' in globals():
        print ('\n   ERROR:      Please define keyword MOHID_RES_FOLDER. \n')
        sys.exit()
        
    if not 'hdf_backup_folder' in globals():
        print ('\n   ERROR:      Please define keyword HDF_BACKUP_FOLDER. \n')
        sys.exit()
        
    if not 'timeseries_backup_folder' in globals():
        print ('\n   ERROR:      Please define keyword TIMESERIES_BACKUP_FOLDER. \n')
        sys.exit()
        
    if not 'restart_backup_folder' in globals():
        print ('\n   ERROR:      Please define keyword RESTART_BACKUP_FOLDER. \n')
        sys.exit()
        
    else:
        pass

    return
    
def init():

    input_file = 'input_mohid.dat'
    
    # Define_global_variables()
    read_file(input_file)
    check_variables()