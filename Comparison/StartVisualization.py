### Author: Bodo Baumann
### github: github.com/sarkspasst
### Organization: UNC Charlotte EPIC
### Date: 06/10/2024

# Script for postprocessing the results of the OpenDSS and Matlab simulations for visualization
# The script fetches the results from the databases, compares them and uploads the results to the comparison database
# Mishmash of two sql libraries, psycopg2 and sqlalchemy, because bugs (or features) in psycopg2

import psycopg2 as pg
import pandas as pd
import numpy as np
import AddedFunctions as af
import operator as op
import time
from io import StringIO
from sqlalchemy import create_engine
from datetime import time as tm
from datetime import datetime as dtm

### Set up databases
# Connection variables
host_address ="192.168.1.90"
username = "seto_db_user"
password = "seto_db_pwd"
port = "5488"

#Upload the files for the transition of OpenDSS to Matlab and vice versa
af.uploadTransitionFiles(host_address, username, password, port, "setocomparisondb")

# Connect to the databases
conn_matlab, cursor_matlab = af.connectToDatabase(host_address, username, password, port, "setomatlabdb")
conn_opendss, cursor_opendss = af.connectToDatabase(host_address, username, password, port, "setoopendssdb")
conn_comparison, cursor_comparison = af.connectToDatabase(host_address, username, password, port, "setocomparisondb")
engine_comparison = create_engine('postgresql://'+username+':'+password+'@'+host_address+':'+port+'/setocomparisondb')

# Reset the result table
engine_comparison.execute("DROP TABLE IF EXISTS result")

### Fetch tables
df_loadname_busname = af.fetchTable(cursor_comparison, "loadname_busname")
df_busname_busnumber = af.fetchTable(cursor_comparison, "busname_busnumber")

### Set up simulation parameters
trackSteps = 4
timeSteps = 24
date = dtm.now().date()

for i in range(1, timeSteps+1):
    for k in range (1, trackSteps+1):
        success = False
        trys = 0
        while not success:
            try:
                cursor_matlab.execute("SELECT * FROM result_all WHERE timeStep = " + str(i) + " AND trackingStep = " + str(k))
                df_matlab = pd.DataFrame(cursor_matlab.fetchall(), columns=[desc[0] for desc in cursor_matlab.description])
                cursor_opendss.execute("SELECT * FROM opendssdata WHERE timeStep = " + str(i) + " AND trackingStep = " + str(k))
                df_opendss = pd.DataFrame(cursor_opendss.fetchall(), columns=[desc[0] for desc in cursor_opendss.description])
                #print("Data loaded for time step", i, "and tracking step", k)
            except:
                print("Could not load data for time step", i, "and tracking step", k, ". Retrying...")
                time.sleep(1)
                continue
            if df_matlab.empty or df_opendss.empty:
                trys += 1
                if trys % 10 == 0:
                    print("Could not load data for time step", i, "and tracking step", k, ". Watiting for Matlab and OpenDSS to finish the next Tracking Step.")
                time.sleep(1)
            else:
                success = True

        # Build the result dataframe
        df_result = pd.DataFrame(columns=['BusName', 'LoadName', 'BusNumber', 'simTime', 'TimeStep', 'TrackingStep', 'Phase', 'NodeType', 'P_matlab', 'Q_matlab', 'P_opendss', 'Q_opendss', 'P_delta', 'Q_delta'])

        busnumber = 0
        busname = 0
        err_count = 0
        for index, row in df_opendss.iterrows():
            try:
                loadname_phase = str(row['busname'])
                phase = str(loadname_phase[-1])
                loadname = str(loadname_phase[:-2])
                busname = int(df_loadname_busname[df_loadname_busname['Load_name'] == loadname_phase.upper()]['Bus_name'].values[0])
                #print(busname)
                busnumber = int(df_busname_busnumber[df_busname_busnumber['f1c1'] == str(busname)]['f1c2'].values[0])
                simTime = int((row['timestep'] -1) * 60 + row['trackingstep'] * 15)
                simTime = dtm.combine(date, tm(simTime // 60, simTime % 60, 0))
                #simTime = tm(simTime // 60, simTime % 60, 0)
                P_opendss = float(row['p'])
                Q_opendss = float(row['q'])
                
                #Check which phase the load is connected to
                if phase.upper() == 'A':
                    P_matlab = float(df_matlab[df_matlab['busnumber'] == busnumber]['p1_kw'].values[0] * 1000)
                    Q_matlab = float(df_matlab[df_matlab['busnumber'] == busnumber]['q1_kvar'].values[0] * 1000)
                elif phase.upper() == 'B':
                    P_matlab = float(df_matlab[df_matlab['busnumber'] == busnumber]['p2_kw'].values[0] * 1000)
                    Q_matlab = float(df_matlab[df_matlab['busnumber'] == busnumber]['q2_kvar'].values[0] * 1000)
                elif phase.upper() == 'C':
                    P_matlab = float(df_matlab[df_matlab['busnumber'] == busnumber]['p3_kw'].values[0] * 1000)
                    Q_matlab = float(df_matlab[df_matlab['busnumber'] == busnumber]['q3_kvar'].values[0] * 1000)
                else:
                    print("Error 69")
                    quit()
                NodeType = str(df_matlab[df_matlab['busnumber'] == busnumber]['type'].values[0])
                P_delta = float(P_matlab - P_opendss)
                Q_delta = float(Q_matlab - Q_opendss)
                #df_temp.iloc[0:0]
                df_temp = pd.DataFrame([[busname, loadname, busnumber, simTime, i, k, phase, NodeType, P_matlab, Q_matlab, P_opendss, Q_opendss, P_delta, Q_delta]], columns=['BusName', 'LoadName', 'BusNumber', 'simTime', 'TimeStep', 'TrackingStep', 'Phase', 'NodeType', 'P_matlab', 'Q_matlab', 'P_opendss', 'Q_opendss', 'P_delta', 'Q_delta'])
                df_result = pd.concat([df_result, df_temp], ignore_index=True)
            except:
                # If you want an error count, uncomment the following lines
                err_count += 1
                #print("Error 420")
                #print("Errorcount", err_count, "Busname", busname, "Busnumber", busnumber)
                continue
        
        df_result.to_csv('result.csv', index=False)
        #exit()


        # Upload the result to the database
        success = False
        trys = 0
        while not success:
            try:
                df_result.to_sql('result', engine_comparison, if_exists='append')
                success = True
            except:
                trys += 1
                if trys % 10 == 0:
                    print("Could not upload data for time step", i, "and tracking step", k, ". Retrying...")
                time.sleep(1)
                continue
        
        print("Data uploaded for time step", i, "and tracking step", k)

# Commit the changes
conn_comparison.commit()

# Close the connections
cursor_matlab.close()
cursor_opendss.close()
cursor_comparison.close()
conn_matlab.close()
conn_opendss.close()
conn_comparison.close()
print("All data uploaded successfully!")

 