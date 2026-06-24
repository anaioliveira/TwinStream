##################################################################
#
#     Developed by: Ana Isabel Oliveira
#     Project: Soil4Ever
#     Date: MARETEC IST, 25/11/2020
#
##################################################################


#!/usr/bin/python
# -*- coding: utf-8 -*-

# Imports
import os
import sys
import datetime
import importlib
import smtplib
from email.message import EmailMessage
import read_input_operational_file

def send_email(receivers, text):

    msg = EmailMessage()
    msg["From"] = '**********'
    msg["To"] = receivers
    msg["Subject"] = 'Error in OPMaranhao.'
    msg.set_content(text)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login('**********', '**********')
        server.send_message(msg)
    
    return

if __name__ == '__main__':

    read_input_operational_file.init()
    
    ####### Get keywords values #######
    hindcast = read_input_operational_file.hindcast
    forecast = read_input_operational_file.forecast
    
    pre_processing_scripts = read_input_operational_file.pre_scripts
    mohid_script = read_input_operational_file.mohid_script
    pos_processing_scripts = read_input_operational_file.pos_scripts
    
    # Emails to send information
    emails = read_input_operational_file.emails
    
    # Loop with dates
    today_date = datetime.date.today()
    actual_date = today_date - datetime.timedelta(hindcast)
    end_date = today_date + datetime.timedelta(forecast)

    while actual_date <= end_date:
    
        begin_sim_date = actual_date
        end_sim_date = actual_date + datetime.timedelta(1)
        
        print ('        ------------ ' + str (begin_sim_date) + ' ------------')
        
        # Pre processing scripts
        for pre_s in pre_processing_scripts:
            path = pre_s.rsplit('/', 1)[0]
            mod = pre_s.rsplit('/', 1)[-1]
        
            sys.path.insert(1, path)
            module = importlib.import_module(mod)
            
            success = module.init(begin_sim_date, end_sim_date, path)
            
            if success == 0:
                message = 'Error in pre processing script ' + mod + '. Day: ' + str(actual_date) + '. Simulation aborted.'
                print (message)
                send_email(emails, message)
                sys.exit()
                
        #MOHID script
        for moh_s in mohid_script:
            path = moh_s.rsplit('/', 1)[0]
            mod = moh_s.rsplit('/', 1)[-1]
        
            sys.path.insert(1, path)
            module = importlib.import_module(mod)
            
            success = module.init(begin_sim_date, end_sim_date, path)
            
            if success == 0:
                message = 'Error in MOHID script ' + mod + '. Day: ' + str(actual_date) + '. Simulation aborted.'
                print (message)
                send_email(emails, message)
                sys.exit()
        
        #Pos processing scripts
        for pos_s in pos_processing_scripts:
            path = pos_s.rsplit('/', 1)[0]
            mod = pos_s.rsplit('/', 1)[-1]
        
            sys.path.insert(1, path)
            module = importlib.import_module(mod)
            
            success = module.init(begin_sim_date, end_sim_date, path)
            
            if success == 0:
                message = 'Roxo: Error in pos processing script ' + mod + '. Day: ' + str(actual_date) + '. Simulation aborted.'
                print (message)
                send_email(emails, message)
                sys.exit()

        actual_date = actual_date + datetime.timedelta(1)