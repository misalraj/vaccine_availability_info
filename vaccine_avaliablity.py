import requests
import os
import json
import pandas as pd
import streamlit as st
from datetime import date


today = date.today()
today_date = today.strftime("%d-%m-%Y")  # dd/mm/YY

st.set_page_config(page_title="Vaccine Avaliablity" , page_icon=":syringe:",layout='wide', initial_sidebar_state='collapsed')

st.markdown('# Slots availability for COVID Vaccine :syringe::syringe:')

"""
 Source: [Github](https://github.com/misalraj/vaccine_availability_info) :star:
"""

df_states = pd.read_csv("data/states.csv")
states_list = df_states['state_name'].to_list()

st.text(" \n\n")  # break line

left_column_1, center_column_1, right_column_1 = st.beta_columns(3)

with left_column_1:
    selected_state = st.selectbox(
    "Select State",
    options=sorted(states_list),
    )

df_district_all = pd.read_csv("data/districts.csv")
df_district = df_district_all.loc[df_district_all["state_name"] == selected_state]
district_list = df_district["district_name"].tolist()

with center_column_1:
    selected_district = st.selectbox(
    "Select District",
    options=sorted(district_list),
    )

district_id = df_district_all.loc[df_district_all['district_name'] == selected_district, "district_id"].item()

try:
    URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={}&date={}" \
        .format(district_id, today_date)
    res = requests.get(URL)

    calender_df = pd.DataFrame(json.loads(res.text)["centers"])
    district_pincode_list = calender_df.loc[calender_df['district_name'] == selected_district, "pincode"]

    calender_df["from"] = pd.to_datetime(calender_df["from"]).dt.strftime('%H:%M')
    calender_df["to"] = pd.to_datetime(calender_df["to"]).dt.strftime('%H:%M')
    calender_df["Timing"] = calender_df["from"] + " - " + calender_df["to"]
    calender_df.rename(columns={'name': 'Name', 'pincode': 'Pincode',
                                'fee_type': 'Fee type', 'vaccine_fees': "Vaccine charge"}, inplace=True)

    new_df =calender_df.explode("sessions")
    new_df['Min Age Limit'] = new_df.sessions.apply(lambda x: x['min_age_limit'])
    new_df['Available Capacity'] = new_df.sessions.apply(lambda x: x['available_capacity'])
    new_df['Date'] = new_df.sessions.apply(lambda x: x['date'])

    if 'vaccine_fees' in new_df.columns:
        new_df = new_df[['Date','Available Capacity', 'Min Age Limit',  'Name', 'Pincode', 'Timing', 'Fee type', 'Vaccine charge']]
    else:
        new_df = new_df[['Date','Available Capacity', 'Min Age Limit','Name', 'Pincode', 'Timing', 'Fee type']]

    selected_pincode = None

    with right_column_1:
        min_age_limit = st.radio('Min age limit', [18, 45])


    agree = st.checkbox('Filter by Pincode')

    if agree:
        selected_pincode = st.selectbox(
        "Select Pincode",
        options=sorted(set(district_pincode_list.tolist())),
        )
        calender_df_pin = new_df[new_df["Pincode"] == selected_pincode]
        st.success("Results: " + "Pincode" + ": " + str(selected_pincode) + ",   " + str(selected_district) + ", " + str(
            selected_state))
        st.table(calender_df_pin)
    else:
        st.success("Results: " + str(selected_district) + ", " + str(selected_state), )
        calender_df_age = new_df[new_df["Min Age Limit"] == min_age_limit]
        st.table(calender_df_age)
except:
    st.error('Unable to fetch data. Try after a few minutes')
