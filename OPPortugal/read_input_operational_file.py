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

                if "HINDCAST" in keyword:
                    global hindcast
                    hindcast = int(value)
                    
                elif "FORECAST" in keyword:
                    global forecast
                    forecast = int(value)

                else:
                    pass
        except:
            if "::begin_preprocessment_scripts" in lin:
                begin_pre_line = lin_i
                
            elif "::end_preprocessment_scripts" in lin:
                end_pre_line = lin_i
                
            elif "::begin_mohid_script" in lin:
                begin_mohid_line = lin_i
                
            elif "::end_mohid_script" in lin:
                end_mohid_line = lin_i
                
            elif "::begin_posprocessment_scripts" in lin:
                begin_pos_line = lin_i
            
            elif "::end_posprocessment_scripts" in lin:
                end_pos_line = lin_i
                
            elif "::begin_emails" in lin:
                begin_emails = lin_i
            
            elif "::end_emails" in lin:
                end_emails = lin_i
                
            else:
                pass
            
        lin_i = lin_i + 1

    fin.close()
    
    global pre_scripts, mohid_script, pos_scripts, emails
    pre_scripts = fin_lines[begin_pre_line+1:end_pre_line]
    pre_scripts = [s.rstrip() for s in pre_scripts]
    
    mohid_script = fin_lines[begin_mohid_line+1:end_mohid_line]
    mohid_script = [s.rstrip() for s in mohid_script]
    
    pos_scripts = fin_lines[begin_pos_line+1:end_pos_line]
    pos_scripts = [s.rstrip() for s in pos_scripts]
    
    emails = fin_lines[begin_emails+1:end_emails]
    emails = [s.rstrip() for s in emails]
    
    return

def check_variables():

    if not 'hindcast' in globals():
        print ('\n   ERROR:      Please define keyword HINDCAST. \n')
        sys.exit()
        
    if not 'forecast' in globals():
        print ('\n   ERROR:      Please define keyword FORECAST. \n')
        sys.exit()
        
    if not 'pre_scripts' in globals():
        print ('\n   WARNING:      No scripts defined to pre processement. \n')
        
    if not 'mohid_script' in globals():
        print ('\n   ERROR:      No path to script that runs MOHID. \n')
        sys.exit()
        
    if not 'pos_scripts' in globals():
        print ('\n   WARNING:      No scripts defined to pos processement. \n')
        sys.exit()
        
    if not 'emails' in globals():
        print ('\n   WARNING:      No emails defined. \n')
        sys.exit()

    else:
        pass

    return
    
def init():

    print ('\n   WARNING: Be careful!!! Do not use spaces and special characters in the names and directories!!!\n')
    
    input_file = 'input_operational.dat'
    
    # Define_global_variables()
    read_file(input_file)
    check_variables()