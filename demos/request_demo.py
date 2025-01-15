import httpx
import streamlit as st

def get_rider(id):
    header = {'Authorization':st.secrets['api']['key']}
    url = f'https://zwift-ranking.herokuapp.com/public/riders/{id}'

    response = httpx.get(url, headers=header)
    response.raise_for_status()

    data = response.json()
    
    return data

print(get_rider(4598636))
