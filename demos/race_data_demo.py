import httpx
import os
import json 


def get_event(id: int):
    header = {'Authorization':os.getenv("ZRAPP_API_KEY")}
    url = f'https://zwift-ranking.herokuapp.com/public/results/{id}'

    response = httpx.get(url, headers=header)
    response.raise_for_status()

    data = response.json()

    return data


def get_riders(ids: list[int]):
    header = {'Authorization':os.getenv("ZRAPP_API_KEY")}
    url = f'https://zwift-ranking.herokuapp.com/public/riders/'

    response = httpx.post(url,
                          headers=header, 
                          json=ids, 
                          timeout=30)
    response.raise_for_status()

    content = response.content
    decoded = content.decode(encoding='utf-8')
    data = json.loads(decoded)

    return data


def get_zp_results(id:int):
    header = {'Authorization':os.getenv("ZRAPP_API_KEY")}
    url = f'https://zwift-ranking.herokuapp.com/public/zp/{id}/results'
    response = httpx.get(url, headers=header)
    response.raise_for_status()
    data = response.json()
    return data


if __name__=="__main__":
    # First approach:
    # Get the riders that took part in the event
    riders = get_event(5144359)

    # Get the ids oft hose riders into a list of integers
    ids = [rider["riderId"] for rider in riders]

    # Pass the list of integers as payload for POST request to riders endopint
    detailed_riders = get_riders(ids)
    
    print(detailed_riders)

    # Alternative:
    riders = get_zp_results(5144359)
    print(riders)
    for rider in riders:
        print(rider.get("male"))