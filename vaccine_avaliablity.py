import requests
import os
import json
import pathlib
import pandas as pd 
import numpy as np 
import streamlit as st 
import datetime
from datetime import date


# os.path.dirname(os.path.abspath(__file__))


today = date.today()
today_date = today.strftime("%d-%m-%Y") # dd/mm/YY


"""
# Vaccine centers in India.

Source: [Github](https://github.com/misalraj/vaccine_availability_info)
"""


df_states = pd.read_csv("data/states.csv")
states_list = df_states['state_name'].to_list()


st.sidebar.title("Please select Options")
st.text(" \n\n") #break line

selected_state = st.sidebar.selectbox(
        "Select State",
        options=sorted(states_list),
)

df_district_all = pd.read_csv("data/districts.csv")
df_district = df_district_all.loc[df_district_all["state_name"]== selected_state]
district_list = df_district["district_name"].tolist()

selected_district = st.sidebar.selectbox(
        "Select District",
        options=sorted(district_list),
)


district_id = df_district_all.loc[df_district_all['district_name'] == selected_district, "district_id"].item()

URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={}&date={}" \
      .format(district_id,today_date)
res = requests.get(URL)

calender_df = pd.DataFrame(json.loads(res.text)["centers"])
district_pincode_list = calender_df.loc[calender_df['district_name'] == selected_district, "pincode"]

if 'vaccine_fees' in calender_df.columns:
    calender_df = calender_df[['name','pincode', 'fee_type','vaccine_fees']]
else:
    calender_df = calender_df[['name', 'pincode', 'fee_type']]

# district_pincode_list.tolist()
selected_pincode = None
agree = st.checkbox('Filter by Pincode')
if agree: 
    selected_pincode = st.selectbox(
        "Pincode",
        options=sorted(set(district_pincode_list.tolist())),
        )
    st.success("Results: " + "Pincode" + ": " + str(selected_pincode) +",   "+ str(selected_district)+ ", "+ str(selected_state)) 
else:
    st.success("Results: " +  str(selected_district)+ ", "+ str(selected_state), ) 

date = st.sidebar.date_input('select date', today)

st.table(calender_df)