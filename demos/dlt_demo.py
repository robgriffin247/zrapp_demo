import streamlit as st
import httpx
import dlt
import duckdb

# Raw Data: JSON data from ZRapp API -------------------------------------------
def get_club_riders(id):
    header = {'Authorization':st.secrets['api']['key']}
    url = f'https://zwift-ranking.herokuapp.com/public/clubs/{id}'
    response = httpx.get(url, headers=header)
    response.raise_for_status()
    return response.json()['riders']

data = get_club_riders(20650)


# DLT --------------------------------------------------------------------------
# DLT loads data from a (nested) json object into a duckdb database
pipeline = dlt.pipeline(
    pipeline_name='zrapp',  # Name of the .duckdb file to be created/used
    destination='duckdb',   # Type of database
    dataset_name='staging', # Schema name
)

# Run the pipeline
load_info = pipeline.run(data,
                         table_name='stg_riders',
                         write_disposition='merge', # Will merge data on to table keeping the most recent
                         primary_key='rider_id')    # Key for merging

# Check the run
print(load_info)

# Verification: using duckdb to view the data
with duckdb.connect('zrapp.duckdb') as con:
    print(con.sql('select * from staging.stg_riders'))
