import requests
import json
import pandas as pd 
import numpy as np 
import streamlit as st 
import datetime
from datetime import date

# today date

today = date.today()
today_date = today.strftime("%d-%m-%Y") # dd/mm/YY


proxies = {
 "http": "http://223.30.190.74:8080",
 "https": "https://223.30.190.74:8080"
}

"""
# Vaccine centers in India.

Source: [Github](https://github.com/misalraj/vaccine_availability_info)
"""


res1 = requests.get("https://cdn-api.co-vin.in/api/v2/admin/location/states", proxies=proxies)
states = pd.DataFrame(json.loads(res1.text)["states"])
states_list = states["state_name"].tolist()


st.sidebar.title("About")
st.text(" \n\n") #break line
# st.sidebar.info(
#      
#     )
selected_state = st.sidebar.selectbox(
        "Select State",
        options=sorted(states_list),
)
state_id = states.loc[states['state_name'] == selected_state, "state_id"].item()


res2 = requests.get("https://cdn-api.co-vin.in/api/v2/admin/location/districts/{}".format(state_id),proxies=proxies)
df_district = pd.DataFrame(json.loads(res2.text)["districts"])
district_list = df_district["district_name"].tolist()

selected_district = st.sidebar.selectbox(
        "Select District",
        options=sorted(district_list),
)

#Select date
date = st.sidebar.date_input('select date', today)

district_id = df_district.loc[df_district['district_name'] == selected_district, "district_id"].item()

URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={}&date={}" \
      .format(district_id,today_date)
res = requests.get(URL, proxies=proxies)

calender_df = pd.DataFrame(json.loads(res.text)["centers"])
if 'vaccine_fees' in calender_df.columns:
    calender_df = calender_df[['name','pincode', 'fee_type','vaccine_fees']]
else:
    calender_df = calender_df[['name', 'pincode', 'fee_type']]


if (st.sidebar.button("Fetch deatils")):
    st.success("info: ")
    st.table(calender_df)