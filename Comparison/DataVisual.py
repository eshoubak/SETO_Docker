import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time
import numpy as np
from sqlalchemy import create_engine

### Set up databases
# Connection variables
host_address ="192.168.1.90"
username = "seto_db_user"
password = "seto_db_pwd"
port = "5488"

engine_comparison = create_engine('postgresql://'+username+':'+password+'@'+host_address+':'+port+'/setocomparisondb')

def check_database():
    while True:
        # Query the database
        df = pd.read_sql('SELECT * FROM my_table', engine_comparison)

        # Check if the DataFrame is empty
        if df.empty:
            print('No data found.')
        else:
            print('Data found.')

        # Wait for the specified amount of time before checking again
        time.sleep(5)

# Start the database checking task in a separate thread
threading.Thread(target=check_database).start()

# Set the page configuration
st.set_page_config(
    page_title="Power Value Dashboard",
    page_icon="✅",
    layout="wide",
)

st.title("Real-Time Power Node Dashboard")

placeholder = st.empty()

'''
with placeholder.container():

    kpi1, kpi2, kpi3 = st.columns(3)

    kpi1.metric(
        label = "Nodes",
        value = num_csv
        #delta = num_csv - num_csv_old
        #num_csv_old = num_csv #update number of csv for delta calculation of next round
    )

    kpi2.metric(
        label = "Number of timeslots",
        #timeslots = pd.read_csv('value_0.csv')
        value = pd.read_csv('./DataVisual/results/3000.csv').shape[0],
        delta = (f'+1 / 60s')
    )

    kpi3.metric(
        label = "Time alive in sec",
        value = pd.read_csv('./DataVisual/results/3000.csv').shape[0] * mult #time alive in seconds
    )
'''