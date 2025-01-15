import httpx
import streamlit as st

# ``GET /riders/<id>``
def get_rider(id):
    header = {'Authorization':st.secrets['api']['key']}
    url = f'https://zwift-ranking.herokuapp.com/public/riders/{id}'

    response = httpx.get(url, headers=header, timeout=30)
    response.raise_for_status()

    data = response.json()
    
    return data


# ``GET /riders/<id>/<time>``
# e.g. data from 30 days ago (converts 30 days ago into seconds since now): print(get_rider_at_time(4598636, time.time() - (30 * (60*60*24))))
def get_rider_at_time(id, time):
    header = {'Authorization':st.secrets['api']['key']}
    url = f'https://zwift-ranking.herokuapp.com/public/riders/{id}/{time}'

    response = httpx.get(url, headers=header, timeout=30)
    response.raise_for_status()
    
    return response.json()


# ``GET /clubs/<id>``
def get_club(id):
    header = {'Authorization':st.secrets['api']['key']}
    url = f'https://zwift-ranking.herokuapp.com/public/clubs/{id}'

    response = httpx.get(url, headers=header, timeout=30)
    response.raise_for_status()

    return response.json()


# ``GET /clubs/<id>/<riderId>``
def get_club_from_rider(club, rider):
    header = {'Authorization':st.secrets['api']['key']}
    url = f'https://zwift-ranking.herokuapp.com/public/clubs/{club}/{rider}'

    response = httpx.get(url, headers=header, timeout=30)
    response.raise_for_status()

    return response.json()


#- ``GET /results/<id>``
def get_event_results(id):
    header = {'Authorization':st.secrets['api']['key']}
    url = f'https://zwift-ranking.herokuapp.com/public/results/{id}'

    response = httpx.get(url, headers=header, timeout=30)
    response.raise_for_status()

    return response.json()


# Get ALL club riders (combo of get_club() and get_club_from_rider())
def get_club_riders(id):
    riders = get_club(id)['riders']
    page_length = len(riders)
    while page_length==1000:
        next_riders = get_club_from_rider(id, 1 + riders[-1]['riderId'])['riders']
        page_length = len(next_riders)
        for rider in next_riders:
            riders.append(rider)

    return riders