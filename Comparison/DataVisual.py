import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time
from datetime import time as tm
from datetime import datetime as dtm
import numpy as np
from sqlalchemy import create_engine
import queue as qu
import plotly.express as px

### Set up databases
# Connection variables
host_address ="192.168.1.90"
username = "seto_db_user"
password = "seto_db_pwd"
port = "5488"

success = False
while not success:
    try:
        engine_comparison = create_engine('postgresql://'+username+':'+password+'@'+host_address+':'+port+'/setocomparisondb')
        success = True
    except:
        print("Could not connect to the database. Retrying...")
        time.sleep(1)

# Set the page configuration
st.set_page_config(
    page_title="Power Value Dashboard",
    page_icon="✅",
    layout="wide",
)

data_queue = qu.Queue()

success = False
while not success:
    try:
        last_update_time = pd.read_sql('SELECT MAX("simTime") FROM result', engine_comparison).iloc[0, 0]
        print(last_update_time)
        df = pd.read_sql('SELECT * FROM result', engine_comparison)
        #df.sort_values(by='simTime', inplace=True)
        success = True
        #time.sleep(5)
    except:
        print("Could not load data from the database. Retrying...")
        time.sleep(5)


df['NodeType'] = df['NodeType'].astype('category')
df['Phase'] = df['Phase'].astype('category')



page = st.sidebar.radio("Choose a page", ["Dashboard", "Node Comparison"])

if page == "Dashboard":

    st.title("Real-Time Node Dashboard")

    placeholder = st.empty()

    df_current = df[(df.simTime == last_update_time)]

    with placeholder.container():

        kpi1_1, kpi1_2, kpi1_3, kpi1_4 = st.columns(4)

        kpi1_1.metric(
            label = "Current simulation time",
            value = str(df_current.simTime.iloc[-1]),
            delta = (f'15 mins per  step')
        )

        kpi1_2.metric(
            label = "Time Step",
            value = df_current.TimeStep.iloc[-1]
        )

        kpi1_3.metric(
            label = "Tracking Step",
            value = df_current.TrackingStep.iloc[-1]
        )

        kpi1_4.metric(
            label = "Total Amount of Nodes",
            value = len(df.BusName.unique()),
            delta = len(df.BusName.unique()) - len(df_current.BusName.unique()) 
        )

        kpi2_1, kpi2_2, kpi2_3, kpi2_4 = st.columns(4)

        kpi2_1.metric(
            label = "Active Components",
            value = df_current.shape[0]
        )

        kpi2_2.metric(
            label = "Diesel Generators",
            value = df_current[df_current.NodeType == 2].shape[0]
        )

        kpi2_3.metric(
            label = "Loads",
            value = df_current[df_current.NodeType == 3].shape[0]
        )

        kpi2_4.metric(
            label = "Batterys",
            value = df_current[df_current.NodeType == 4].shape[0]
        )
        
        st.subheader("Combined Power of all Diesel Generators")

        fig1_1, fig1_2, fig1_3 = st.columns(3)

        df_type1 = df[df.NodeType == 2]
        df_type1 = df_type1[['simTime', 'P_matlab', 'Q_matlab', 'P_opendss', 'Q_opendss', 'P_delta', 'Q_delta']]
        df_type1 = df_type1.groupby('simTime').sum().reset_index()

        with fig1_1:
            fig1_1 = px.line(df_type1, x='simTime', y=['P_matlab', 'Q_matlab'], title='Matlab Power')
            fig1_1.update_layout(yaxis_title='Power [W]', xaxis_title='Node')
            st.plotly_chart(fig1_1)

        with fig1_2:
            fig1_2 = px.line(df_type1, x='simTime', y=['P_opendss', 'Q_opendss'], title='OpenDSS Power')
            fig1_2.update_layout(yaxis_title='Power [W]', xaxis_title='Node')
            st.plotly_chart(fig1_2)

        with fig1_3:
            fig1_3 = px.line(df_type1, x='simTime', y=['P_delta', 'Q_delta'], title='Difference Power')
            if df_type1.P_delta.abs().max() < 1 and df_type1.Q_delta.abs().max() < 1:
                fig1_3.update_yaxes(range=[-1, 1])
            fig1_3.update_layout(yaxis_title='Power [W]', xaxis_title='Node')
            st.plotly_chart(fig1_3)

        st.subheader("Combined Power of all Loads")

        fig2_1, fig2_2, fig2_3 = st.columns(3)

        df_type2 = df[df.NodeType == 3]
        df_type2 = df_type2[['simTime', 'P_matlab', 'Q_matlab', 'P_opendss', 'Q_opendss', 'P_delta', 'Q_delta']]
        df_type2 = df_type2.groupby('simTime').sum().reset_index()
        
        with fig2_1:
            fig2_1 = px.line(df_type2, x='simTime', y=['P_matlab', 'Q_matlab'], title='Matlab Power')
            fig2_1.update_layout(yaxis_title='Power [W]', xaxis_title='Node')
            st.plotly_chart(fig2_1)

        with fig2_2:
            fig2_2 = px.line(df_type2, x='simTime', y=['P_opendss', 'Q_opendss'], title='OpenDSS Power')
            fig2_2.update_layout(yaxis_title='Power [W]', xaxis_title='Node')
            st.plotly_chart(fig2_2)

        with fig2_3:
            fig2_3 = px.line(df_type2, x='simTime', y=['P_delta', 'Q_delta'], title='Difference Power')
            if df_type2.P_delta.abs().max() < 1 and df_type2.Q_delta.abs().max() < 1:
                fig2_3.update_yaxes(range=[-1, 1])
            fig2_3.update_layout(yaxis_title='Power [W]', xaxis_title='Node')
            st.plotly_chart(fig2_3)

        st.subheader("Combined Power of all Batteries")

        fig3_1, fig3_2, fig3_3 = st.columns(3)

        df_type3 = df[df.NodeType == 4]
        df_type3 = df_type3[['simTime', 'P_matlab', 'Q_matlab', 'P_opendss', 'Q_opendss', 'P_delta', 'Q_delta']]
        df_type3 = df_type3.groupby('simTime').sum().reset_index()

        with fig3_1:
            fig3_1 = px.line(df_type3, x='simTime', y=['P_matlab', 'Q_matlab'], title='Matlab Power')
            fig3_1.update_layout(yaxis_title='Power [W]', xaxis_title='Node')
            st.plotly_chart(fig3_1)

        with fig3_2:
            fig3_2 = px.line(df_type3, x='simTime', y=['P_opendss', 'Q_opendss'], title='OpenDSS Power')
            fig3_2.update_layout(yaxis_title='Power [W]', xaxis_title='Node')
            st.plotly_chart(fig3_2)

        with fig3_3:
            fig3_3 = px.line(df_type3, x='simTime', y=['P_delta', 'Q_delta'], title='Difference Power')
            if df_type3.P_delta.abs().max() < 1 and df_type3.Q_delta.abs().max() < 1:
                fig3_3.update_yaxes(range=[-1, 1])
            fig3_3.update_layout(yaxis_title='Power [W]', xaxis_title='Node')
            st.plotly_chart(fig3_3)











if page == "Node Comparison":
        
    st.title("Node Comparison")

    placeholder = st.empty()

    with placeholder.container():

        ### Dropdowns
        # Default values
        dropdown_type = 'Diesel Generator'
        dropdown_col = 'Bus Name'

        #dropdown_col, dropdown_node, dropdown_phase = st.columns(3)

        types = {
                'Diesel Generator': 2,
                'Loads': 3,
                'Battery Storage': 4
            }
        dropdown_type = st.selectbox(
            "Select a Node Type to filter by",
            list(types.keys()),
        )
        selected_type = types[dropdown_type]
        df_data = df[(df.NodeType == selected_type)]
        
        colNames = {
            'Bus Name': 'BusName',
            'Loads and Sources': 'LoadName',
            'Bus Number': 'BusNumber'
        }
        dropdown_col = st.selectbox(
            "Select a column to filter by",
            list(colNames.keys())
        )
        selected_col = colNames[dropdown_col]
        df_data = df_data[[selected_col, 'simTime', 'Phase', 'P_matlab', 'Q_matlab', 'P_opendss', 'Q_opendss', 'P_delta', 'Q_delta']]

        dropdown_node_list = df_data[selected_col].unique().tolist()
        dropdown_node_list.sort()
        dropdown_node = dropdown_node_list[0]
        dropdown_node = st.selectbox(
            "Select a node",
            dropdown_node_list
        )
        df_data = df_data[(df_data[selected_col] == dropdown_node)]

        dropdown_phase = df_data[df_data[selected_col] == dropdown_node].Phase.unique()[0]
        dropdown_phase = st.selectbox(
            "Select a phase",
            df_data.Phase.unique().tolist()
        )

        df_data = df_data[(df.Phase == dropdown_phase)]

        ### Plots
        fig_col1, fig_col2, fig_col3 = st.columns(3)
        
        # Left plot
        with fig_col1:
            fig_col1 = px.line(df_data, x='simTime', y=['P_matlab', 'Q_matlab'], title='Matlab Values')
            fig_col1.update_layout(yaxis_title='Power [kW, kVar]', xaxis_title='Time')
            st.plotly_chart(fig_col1)

        # Middle plot
        with fig_col2:
            fig_col2 = px.line(df_data, x='simTime', y=['P_opendss', 'Q_opendss'], title='OpenDSS Values')
            fig_col2.update_layout(yaxis_title='Power [kW, kVar]', xaxis_title='Time')
            st.plotly_chart(fig_col2)

        # Right plot
        with fig_col3:
            fig_col3 = px.line(df_data, x='simTime', y=['P_delta', 'Q_delta'], title='Difference Values')
            if df_data.P_delta.abs().max() < 1 and df_data.Q_delta.abs().max() < 1:
                fig_col3.update_yaxes(range=[-1, 1])
            fig_col3.update_layout(yaxis_title='Power [kW, kVar]', xaxis_title='Time')
            st.plotly_chart(fig_col3)


#Check if the data has been updated
while True:
    success = False
    while not success:
        try:
            current_update_time = pd.read_sql('SELECT MAX("simTime") FROM result', engine_comparison).iloc[0, 0]
            success = True
        except:
            print("Could not load data from the database. Retrying...")
            time.sleep(5)
            continue
    if current_update_time != last_update_time:
        #df = pd.read_sql('SELECT * FROM result', engine_comparison)
        #current_df = df[(df.simTime == df.simTime.max())]
        #last_update_time = current_update_time
        #print("Data updated")
        #time.sleep(5)
        # Close the current connection
        engine_comparison.dispose()
        st.rerun()
    time.sleep(5)
        