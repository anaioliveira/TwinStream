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
import importlib
import read_input_meteo_file

############## MAIN FUNCTION #############
def init(begin_date, end_date, meteo_working_dir):

    print ("--> Working on meteorological files.")
    
    # Change directory to glue script
    os.chdir(meteo_working_dir)
    
    ####### Get keywords values #######
    read_input_meteo_file.init(0, 0)
    meteo_solutions = read_input_meteo_file.meteo_solutions
    boundary_cond_folder = (read_input_meteo_file.bound_cond).replace(os.sep, '/')
    mohid_meteo_filename = read_input_meteo_file.final_meteo_name
    
    for meteo_sol in range(1, meteo_solutions+1):
        os.chdir(meteo_working_dir)
        print('    --> Working on meteo solution '+ str(meteo_sol) + '.')
        read_input_meteo_file.init(1, meteo_sol)
        glue = read_input_meteo_file.glue
        interpolate = read_input_meteo_file.interpolate
        working_dir = (read_input_meteo_file.working_dir).replace(os.sep, '/')
        origin_folder = (read_input_meteo_file.origin_folder).replace(os.sep, '/')
        file_prefix = read_input_meteo_file.file_prefix
        father_grid = (read_input_meteo_file.father_grid).replace(os.sep, '/')
        convert_tool = (read_input_meteo_file.convert_tool).replace(os.sep, '/')
        
        if glue == 1:
            sys.path.insert(0, working_dir)
            glueMOHIDtool=importlib.import_module('glueMOHIDtool')
            success_glue=glueMOHIDtool.init(begin_date,end_date,working_dir,origin_folder,file_prefix,convert_tool)
            # remove imported script after use
            del glueMOHIDtool
            sys.modules.pop('glueMOHIDtool', None)
            if success_glue==0:
                continue
        else:
            success_glue=1
        
        if interpolate == 1:
            sys.path.insert(1, working_dir)
            interpolateMOHIDtool = importlib.import_module('interpolateMOHIDtool')
            success_interp=interpolateMOHIDtool.init(begin_date,end_date,working_dir,father_grid,convert_tool,boundary_cond_folder,mohid_meteo_filename,origin_folder,file_prefix,glue)
            # remove imported script after use
            del interpolateMOHIDtool
            sys.modules.pop('interpolateMOHIDtool', None)
            if success_interp==0:
                continue
                
        if success_glue==1 and success_interp==1:
            commandResult = 1
            return commandResult
    return 0