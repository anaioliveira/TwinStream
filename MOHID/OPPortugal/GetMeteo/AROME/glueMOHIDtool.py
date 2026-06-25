##################################################################
#
#     Developed by: Ana Isabel Oliveira
#     Project: HazRunoff
#     Date: MARETEC IST, 29/10/2019
#
##################################################################

#!/usr/bin/python

import sys
import os
import shutil
import subprocess

def write_convert_file(template_file, files_to_glue, output_file):

    #Input file
    fin = open(template_file, 'r')

    #Output file
    file_to_write = os.path.split(template_file)[0] + '/ConvertToHDF5Action.dat'
    fout = open(file_to_write, 'w')

    lines = fin.readlines()

    for l in lines:
        if 'output_file' in l:
            l = l.replace('output_file', output_file)
            fout.writelines(l)
        elif 'files_to_glue' in l:
            l = l.replace('files_to_glue', files_to_glue)
            fout.writelines(l)
        else:
            fout.writelines(l)

    fin.close()
    fout.close()

    return

def write_log_file(log_file, log_text):

    fin = open(log_file, 'w')
    fin.write(log_text.decode("utf-8"))
    fin.close()
    
    return

############## MAIN FUNCTION #############
def init(begin_date, end_date, working_dir, origin_folder, file_prefix, convert_tool):

    print ("        --> Glueing meteorological files.")
    
    # Change directory to glue script
    os.chdir(working_dir)
    
    # Get names of files to glue
    meteo_files = []
    for root, dirs, files in os.walk(origin_folder):
        for basename in files:
            meteo_files.append(os.path.join(root, basename))
    
    # Format dates
    date1 = begin_date.strftime('%Y%m%d')
    date2 = end_date.strftime('%Y%m%d')
    
    selected_files = []
    for m in meteo_files:
        filename = os.path.basename(m)
        if filename.endswith('.hdf5'):
            if filename.startswith(file_prefix) == True and date1 in m:
                selected_files.append(m)
            elif filename.startswith(file_prefix) == True and date2 in m:
                selected_files.append(m)
    selected_files.sort()
    
    if selected_files == []:
        print ("            -> No meteorological files were found.")
        commandResult = 0
        return commandResult
    else:
        for f in selected_files:
            shutil.copy(f, convert_tool + os.path.basename(f))

    files_to_glue = '\n'.join(selected_files)
    
    #Glue files
    os.chdir(convert_tool)
    write_convert_file(convert_tool + 'ConvertToHDF5Action_glue.dat', files_to_glue, convert_tool + 'EntireDomainMeteo.hdf5')
    proc = subprocess.Popen("ConvertToHDF5.exe", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = proc.communicate()
    write_log_file(working_dir + '\LogsGlue\glue_' + date1 + '.log', stdout)
    if 'error' in str(stdout).lower() or 'err' in str(stdout).lower():
        commandResult = 0
    else:
        commandResult = 1

    for f in selected_files:
        os.remove(convert_tool + os.path.basename(f))
    
    return commandResult