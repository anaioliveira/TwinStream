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
    fin_lines = fin.readlines()

    lin_i = 0

    while lin_i < len(fin_lines):
    
        lin = fin_lines[lin_i]
        
        try:
            aux_line = lin.split(':', 1)
            keyword = aux_line[0]
            if keyword[0] == '#':
                pass
            else:
                value = aux_line[1].replace('\n','')
                value = value.split(' ', 1)[-1]
                if '#' in value:
                    value = value.split('#')[0]

                if "NUMBER_OF_METEO_SOLUTIONS" in keyword:
                    global meteo_solutions
                    meteo_solutions = int(value)
                    
                elif "PATH_TO_BOUNDARY_CONDITIONS" in keyword:
                    global bound_cond
                    bound_cond = str(value)
                    
                elif "METEO_FILENAME_TO_MOHID" in keyword:
                    global final_meteo_name
                    final_meteo_name = str(value)

                else:
                    pass
        except:
            pass
            
        lin_i = lin_i + 1

    fin.close()
    
    return

def read_block_variables(block):

    fin_lines = block

    lin_i = 0

    while lin_i < len(fin_lines):
    
        lin = fin_lines[lin_i]
        
        try:
            aux_line = lin.split(':', 1)
            keyword = aux_line[0]
            if keyword[0] == '#':
                pass
            else:
                value = aux_line[1].replace('\n','')
                value = value.split(' ', 1)[-1]
                if '#' in value:
                    value = value.split('#')[0]

                if "GLUE" in keyword:
                    global glue
                    glue = int(value)
                    
                elif "INTERPOLATE" in keyword:
                    global interpolate
                    interpolate = int(value)
                    
                elif "WORKING_DIRECTORY" in keyword:
                    global working_dir
                    working_dir = str(value)
                    
                elif "ORIGIN_METEO_FOLDER" in keyword:
                    global origin_folder
                    origin_folder = str(value)
                    
                elif "FILE_PREFIX" in keyword:
                    global file_prefix
                    if not value:
                        file_prefix = ''
                    else:
                        file_prefix = str(value)
                    
                elif "FATHER_GRID" in keyword:
                    global father_grid
                    father_grid = str(value)
                    
                elif "CONVERT_PATH" in keyword:
                    global convert_tool
                    convert_tool = str(value)

                else:
                    pass
        except:
            pass
            
        lin_i = lin_i + 1
    
    return

def extract_meteo_blocks(input_file, meteo_solution):

    fin = open(input_file)
    fin_lines = fin.readlines()

    lin_i = 0

    while lin_i < len(fin_lines):
    
        lin = fin_lines[lin_i]
        
        if '#' in lin:
            pass
        else:
            try:
                if "::begin_meteo"+str(meteo_solution) in lin:
                    begin_block_line = lin_i+1
                elif "::end_meteo"+str(meteo_solution) in lin:
                    end_block_line = lin_i
                else:
                    pass
            except:
                pass
    
        lin_i = lin_i + 1

    if 'begin_block_line' in vars() and 'end_block_line' in vars():
        block = fin_lines[begin_block_line:end_block_line]
        read_block_variables(block)
    else:
        print ("\n   ERROR:      Meteorological block number " + str(meteo_solution) + " doesn't exist or has a problem. \n")
        sys.exit()
    
    fin.close()

    return

def check_variables(block_read):

    if not 'meteo_solutions' in globals():
        print ('\n   ERROR:      Please define keyword NUMBER_OF_METEO_SOLUTIONS. \n')
        sys.exit()
        
    if not 'bound_cond' in globals():
        print ('\n   ERROR:      Please define keyword PATH_TO_BOUNDARY_CONDITIONS. \n')
        sys.exit()
        
    if not 'final_meteo_name' in globals():
        print ('\n   ERROR:      Please define keyword METEO_FILENAME_TO_MOHID. \n')
        sys.exit()
        
    else:
        pass
        
    if block_read:
        if not 'glue' in globals():
            print ('\n   ERROR:      Please define keyword GLUE. \n')
            sys.exit()
            
        if not 'interpolate' in globals():
            print ('\n   ERROR:      Please define keyword INTERPOLATE. \n')
            sys.exit()
            
        if not 'working_dir' in globals():
            print ('\n   ERROR:      Please define keyword WORKING_DIR. \n')
            sys.exit()
        
        if not 'origin_folder' in globals():
            print ('\n   ERROR:      Please define keyword ORIGIN_METEO_FOLDER. \n')
            sys.exit()
            
        if not 'file_prefix' in globals():
            print ('\n   ERROR:      Please define keyword FILE_PREFIX. \n')
            sys.exit()
            
        if not 'father_grid' in globals():
            print ('\n   ERROR:      Please define keyword FATHER_GRID. \n')
            sys.exit()
            
        if not 'convert_tool' in globals():
            print ('\n   ERROR:      Please define keyword CONVERT_PATH. \n')
            sys.exit()

    return
    
def init(read_blocks, meteo_sol):

    input_file = 'input_meteo.dat'
    
    if read_blocks == 0:
        # Define_global_variables()
        read_file(input_file)
        check_variables(False)
    else:
        extract_meteo_blocks(input_file, meteo_sol)
        check_variables(True)