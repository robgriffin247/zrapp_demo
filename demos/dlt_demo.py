import streamlit as st
import httpx
import dlt
import duckdb


# Get ALL club riders (combo of get_club() and get_club_from_rider())
def get_club_riders(id):

    def get_club(id):
        header = {'Authorization':st.secrets['api']['key']}
        url = f'https://zwift-ranking.herokuapp.com/public/clubs/{id}'

        response = httpx.get(url, headers=header, timeout=30)
        response.raise_for_status()

        return response.json()


    def get_club_from_rider(club, rider):
        header = {'Authorization':st.secrets['api']['key']}
        url = f'https://zwift-ranking.herokuapp.com/public/clubs/{club}/{rider}'

        response = httpx.get(url, headers=header, timeout=30)
        response.raise_for_status()

        return response.json()
    

    riders = get_club(id)['riders']
    page_length = len(riders)
    while page_length==1000:
        next_riders = get_club_from_rider(id, 1 + riders[-1]['riderId'])['riders']
        page_length = len(next_riders)
        for rider in next_riders:
            riders.append(rider)

    return riders

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
