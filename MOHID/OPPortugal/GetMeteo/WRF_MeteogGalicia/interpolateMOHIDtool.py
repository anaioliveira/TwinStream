##################################################################
#
#     Developed by: Ana Isabel Oliveira
#     Project: HazRunoff
#     Date: MARETEC IST, 29/10/2019
#
##################################################################

#!/usr/bin/python

import sys, os
import datetime, subprocess, numpy, h5py, shutil

def avoid_negative_meteo_values(hdf_file):

    print ('        --> Correcting negative meteorological values.')
    
    if not os.path.exists(hdf_file):
        print(f"            !!! Erro: Arquivo {hdf_file} não encontrado para correção.")
        return
        
    # Open HDF file
    fin_hdf = h5py.File(hdf_file, 'r+')

    # Define variables to correct
    meteo_var = ['precipitation', 'solar radiation', 'relative humidity']
    
    for var in meteo_var:
        # Get precipitation, solar radiation and relative humidity
        var_k = fin_hdf['Results'][var].keys()
        
        n = 0
        for k in var_k:
            k_values = fin_hdf['Results'][var][k][()]
            
            if numpy.min(k_values) < 0:
                k_values [k_values<0] = 0

                dset = fin_hdf['Results'][var][k]
                dset[:,:] = k_values
                if n == 0:
                    print ("            Negative values in " + var + " were corrected.")
                n = n + 1

    fin_hdf.close()
    
    return

def write_interpolate_file(template_file, d1, d2, in_file, father_grid, out_file):
    in_file = in_file.replace('\\', '/')
    father_grid = father_grid.replace('\\', '/')
    out_file = out_file.replace('\\', '/')
    
    # Input file
    fin = open(template_file, 'r')

    #Output file
    file_to_write = os.path.split(template_file)[0] + '/ConvertToHDF5Action.dat'
    fout = open(file_to_write, 'w')

    lines = fin.readlines()

    for l in lines:
        if 'begin_date' in l:
            l = l.replace('begin_date', d1)
            fout.writelines(l)
        elif 'end_date' in l:
            l = l.replace('end_date', d2)
            fout.writelines(l)
        elif 'input_file' in l:
            l = l.replace('input_file', in_file)
            fout.writelines(l)
        elif 'father_grid' in l:
            l = l.replace('father_grid', father_grid)
            fout.writelines(l)
        elif 'output_file' in l:
            l = l.replace('output_file', out_file)
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
    
############# MAIN FUNCTION #############
def init(begin_date,end_date,working_dir,father_grid,convert_tool,boundary_cond_folder,mohid_meteo_filename,origin_folder,file_prefix,glue_option):

    print ("        --> Interpolating meteorological files.")
    
    # Change directory to glue script
    os.chdir(working_dir)
    
    # Format dates
    date1_file = begin_date.strftime('%Y%m%d')
    
    if glue_option == 0:
        meteo_files = []
        for root, dirs, files in os.walk(origin_folder):
            for basename in files:
                meteo_files.append(os.path.join(root, basename))
        
        for m in meteo_files:
            filename = os.path.basename(m)
            if filename.endswith('.hdf5'):
                if filename.startswith(file_prefix) == True and date1_file in m:
                    shutil.copy(m ,convert_tool + 'EntireDomainMeteo.hdf5')
    
    # Format dates
    date1 = begin_date.strftime('%Y %m %d' + ' 00 00 00')
    date2 = end_date.strftime('%Y %m %d' + ' 00 00 00')
    #Interpolate files
    os.chdir(convert_tool)
    
    input_file = convert_tool + 'EntireDomainMeteo.hdf5'
    output_file = boundary_cond_folder + mohid_meteo_filename + '.hdf5'
    write_interpolate_file(convert_tool + 'ConvertToHDF5Action_Interpolate.dat', date1, date2, input_file, father_grid, output_file)
    
    proc = subprocess.Popen("ConvertToHDF5.exe", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = proc.communicate()
    write_log_file(working_dir + r'\LogsInterpolate\interpolate_' + date1_file + '.log', stdout)
    
    if 'error' in str(stdout).lower() or 'err' in str(stdout).lower():
        commandResult = 0
    else:
        avoid_negative_meteo_values(output_file)
        commandResult = 1
    
    return commandResult
    