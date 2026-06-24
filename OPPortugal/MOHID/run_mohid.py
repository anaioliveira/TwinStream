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
import re
import shutil
import subprocess
from datetime import datetime, timedelta
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

# ---------------- INTERNATIONAL DISCHARGE FUNCTIONS ----------------
def get_portugal_nodes_map(ts_loc_path):
    """
    Lê o ficheiro de localizações de Portugal e cria um mapa {Nome: ID}.
    """
    node_map = {}
    
    # Verifica se o ficheiro existe no caminho exato recebido
    if os.path.exists(ts_loc_path):
        with open(ts_loc_path, 'r') as f:
            content = f.read()
            # Regex para blocos de TimeSerie
            blocks = re.findall(r'<BeginNodeTimeSerie>(.*?)<EndNodeTimeSerie>', content, re.DOTALL)
            
            for block in blocks:
                # Procura o ID e o NAME dentro do bloco
                node_id_match = re.search(r'NODE_ID\s+:\s+(\d+)', block)
                name_match = re.search(r'NAME\s+:\s+([^\n\r!]+)', block)
                
                if node_id_match and name_match:
                    node_id = node_id_match.group(1).strip()
                    name = name_match.group(1).strip()
                    node_map[name] = node_id
    else:
        print(f"        ERROR: File not found at {ts_loc_path}")
        
    return node_map
    
def international_discharge(target_date_obj):   
    is_active = getattr(read_input_mohid_file, 'international_basin_active', False)
    if not is_active: return

    # 1. Obter nomes e caminhos das bacias de Espanha
    names = getattr(read_input_mohid_file, 'basin_names', [])
    basins_config = {names[i-1]: getattr(read_input_mohid_file, f"basin{i}") for i in range(1, len(names)+1)}
    
    main_folder = getattr(read_input_mohid_file, 'main_model_folder', None)
    date_str = target_date_obj.strftime('%Y%m%d')
    discharge_folder = os.path.join(main_folder, "GeneralData", "Discharge")
    if not os.path.exists(discharge_folder): os.makedirs(discharge_folder)
    
    # 2. Mapear Nodes de Portugal {Nome: ID}
    print("        --> Mapping Portugal Node IDs by Name.")
    pt_path = os.path.normpath(os.path.join(main_folder, "NodeTimeSeriesLocation_Portugal.dat"))
    print(pt_path)
    portugal_map = get_portugal_nodes_map(pt_path)
    #print(f"        Found {len(portugal_map)} nodes in map.")
    
    dat_file_path = os.path.join(main_folder, "data", "Discharge_1.dat")
    
    tomorrow_obj = target_date_obj + timedelta(days=1)
    # Formato: 2026-04-19_2026-04-20
    ts_folder_name = f"{target_date_obj.strftime('%Y-%m-%d')}_{tomorrow_obj.strftime('%Y-%m-%d')}"
    print(f"        --> Searching in folder pattern: {ts_folder_name}")
    
# ---------------- EXTRACTION, DISCHARGE FILE AND TIMESERIES ----------------  
    with open(dat_file_path, 'w') as mohid_dat:
        for basin_name, ts_root_dir in basins_config.items():
            day_folder = os.path.join(ts_root_dir.strip(), ts_folder_name)
            
            if not os.path.exists(day_folder):
                print(f"        NOT FOUND: Timeseries folder for {basin_name} ({ts_folder_name})")
                continue
            print(f"        --> Processing files for Basin: {basin_name} in {day_folder}")          
            srn_files = [f for f in os.listdir(day_folder) if f.endswith('.srn')]
            # Formato esperado no cabeçalho: "2026.  4. 18." ou similar
            # Vamos capturar o Ano e o Mês para uma validação segura
            current_year = target_date_obj.strftime('%Y')
            current_month = str(int(target_date_obj.strftime('%m'))) # Remove zero à esquerda (ex: "04" vira "4")
            current_day = str(int(target_date_obj.strftime('%d')))
            
            for srn_file in srn_files:
                file_label = os.path.splitext(srn_file)[0]
                srn_path = os.path.join(day_folder, srn_file)
                
                # 1. IGNORAR FICHEIROS GENÉRICOS QUE NÃO SÃO NODES
                if not file_label.startswith("Node_"):
                    continue # Salta DT.srn, channel flow.srn, etc.
                
                # --- VALIDAÇÃO DE DATA INTERNA DO ARQUIVO ---
                valid_date = False
                try:
                    with open(srn_path, 'r') as f_check:
                        head = [next(f_check) for _ in range(15)]
                        for line in head:
                            if "SERIE_INITIAL_DATA" in line:
                                date_parts = re.findall(r'\d+', line)
                                if date_parts:
                                    file_year = date_parts[0]
                                    file_month = date_parts[1]
                                    file_day = date_parts[2]
                                    
                                    if file_year == current_year and file_month == current_month and file_day == current_day:
                                        valid_date = True
                                    else:
                                        print(f"        REJECTED: {srn_file} internal date is {file_year}-{file_month}-{file_day}, but we need {current_year}-{current_month}-{current_day}!")
                                break
                except Exception as e:
                    print(f"        ERROR checking internal date for {srn_file}: {e}")
                    continue

                # AQUI CORRIGE O FLUXO: Se não for válida, para MESMO aqui e vai para o próximo arquivo
                if not valid_date:
                    continue
                    
                matched = False  
                for pt_name, ptid in portugal_map.items():
                    if pt_name in file_label:
                        print(f"        MATCH: {srn_file} linked to Portugal Node {pt_name} (ID: {ptid})")
                        
                        shutil.copy2(srn_path, discharge_folder)
                        
                        mohid_dat.write(f"<begindischarge>\n")
                        mohid_dat.write(f"NAME : {file_label}\n")
                        mohid_dat.write(f"NODE_ID : {ptid}\n")
                        mohid_dat.write(f"DATA_BASE_FILE : ../GeneralData/Discharge/{srn_file}\n")
                        mohid_dat.write(f"FLOW_COLUMN : 14\n")
                        mohid_dat.write(f"<enddischarge>\n\n")
                        
                        matched = True
                        break
    print("--> International basin processing completed.")

def init(begin_date, end_date, working_dir):

    print ("--> Initializing MOHID Land.")
    
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
    
    # Só executa se a flag no arquivo for 1   
    if getattr(read_input_mohid_file, 'international_basin_active', False):
        print("--> International Basin feature is ON. Starting extraction...")
        international_discharge(begin_date)
    else:
        print("--> International Basin feature is OFF. Skipping extraction.")
    
    # Format dates
    date1 = begin_date.strftime('%Y %m %d' + ' 00 00 00')
    date2 = end_date.strftime('%Y %m %d' + ' 00 00 00')
    
    date1_ = begin_date.strftime('%Y%m%d')
    
    # Check active modules
    check_active_modules(mohid_data_folder)

    # Change dates in model file
    change_model_file(mohid_data_folder, date1, date2)
        
    #Manage the nomfich file according with continuous keyword
    #sim_date_before_py = begin_date - datetime.timedelta(1)
    sim_date_before_py = begin_date - timedelta(days=1)
    sim_date_before = sim_date_before_py.strftime('%Y-%m-%d')+'_'+begin_date.strftime('%Y-%m-%d')
    manage_nomfich_file(mohid_data_folder, mohid_exe_folder, sim_date_before, restart_backup_folder)
    
    print ("--> Now Running MOHID Land.")
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