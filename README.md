# ZwiftRacing.app API

> ZwiftRacing is a cutting-edge web application designed for avid cyclists and competitive racing enthusiasts who use Zwift, the popular online cycling platform. With ZwiftRacing (ZR), you can take your virtual cycling experience to the next level by participating in organized races using the first result-based categorization system ever made for indoor cycling. &mdash; [zwiftracing.app](https://www.zwiftracing.app/docs)




### ZRapp API

ZwiftRacing.app also has an API providing endpoints that allow users to programmatically fetch ZRapp data. This includes data on riders, clubs and events. The API is hsoted at [https://zwift-ranking.herokuapp.com/public/](https://zwift-ranking.herokuapp.com/public/). You may encounter another ZRapp API address &mdash; please don't use that one, it is used by the ZwiftRacing.app and needs to be kept free from unnecessary traffic!

To get access to the ZRapp API, you first need to join the ZRapp Discord server, then send Tim Hanson a message to request access to the API. Tim will then give you an API key. Store this key in a ``.env`` file in the root directory of your project or, if using streamlit, in `.streamlit/secrets.toml`. Note that my code is all written for use with Streamlit so, if using ``.env``, you will need to switch those parts out accordingly (from calling ``st.secrets['api']['key']`` to ``os.getenv('key')``).

**Be careful to add the ``.env`` and/or ``.streamlit/secrets.toml`` paths to your ``.gitignore`` file if using Git. Do not share the API key &mdash; it is yours and should be handled with respsect.**

- ``.gitignore``

    ```
    .env
    .streamlit/secrets.toml
    ```

- ``.env``

    ```
    key=myapikey12345
    ```

- ``./.streamlit/secrets.toml``

    ```{yaml}
    [api]
    key="myapikey12345"
    ```




### Endpoints

|Endpoint|Type|Description|
|-----|-----|-----|
|``/riders/<id>``|``Get``|Returns details about a rider.|
|``/riders/<id>/<time>``|``Get``|Returns details about a rider at a specific point in time.|
|``/riders``|``Post``|Returns rider details for a list of riders. List is sent as the body of the request.|
|``/clubs/<id>``|``Get``|Returns details for a club, including (up to) 1000 active riders.|
|``/clubs/<id>/<riderId>``|``Get``|Returns details for a club, including (up to) 1000 active riders, starting from a given rider - rider data is stored in order of ascending ``riderId``.|
|``/results/<id>``|``Get``|Returns details for an event.|

You can find my functions to query each ``GET`` endpoint, plus a function combining ``/clubs/<id>`` and ``/clubs/<id>/<riderId>`` to get *all* riders in a club, in [``zrapp/endpoints.py``](https://github.com/robgriffin247/zrapp_demo/blob/main/zrapp/endpoints.py). The function for the ``POST`` request to ``riders`` is on its way.



## Demos

### Get data from ZRapp API

This function demonstrates the use of the ZRapp API to get the data for a specific rider, given by rider ID. 

- ``./demos/request.py``

    ```{python } 
    import httpx
    import streamlit as st

    def get_rider(id):
        header = {'Authorization':st.secrets['api']['key']}
        url = f'https://zwift-ranking.herokuapp.com/public/riders/{id}'

        response = httpx.get(url, headers=header, timeout=30)
        response.raise_for_status()

        return response.json()

    print(get_rider(4598636))
    ```

- Output:

    ```
    {'club': {'id': 20650, 'name': 'Tea & Scone'},
     'country': 'se',
     'gender': 'M',
     'handicaps': {'profile': {'flat': 57.48481100417995,
                             'hilly': 12.318173786610082,
                             'mountainous': -61.13099044501623,
                             'rolling': 39.00755032426495}},
     'height': 185,
     'name': 'Rob Griffin',
     'phenotype': {'bias': 5.6000000000000085,
                 'scores': {'climber': 85.5,
                             'puncheur': 93.1,
                             'pursuiter': 89.7,

                            ....
        
     'zpCategory': 'B',
     'zpFTP': 308}
                            
    ```




### Load data using DLT

[DLT](https://dlthub.com/docs/intro) eases the process of transforming nested json files into tables. DLT automatically unnests the data into suitable tables and loads them into a duckdb database. This demo shows how DLT can be used to unpack the nested json data received from a request to get all club riders.

- ``./demos/dlt.py``

    ```{python}
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

    ```

- Output:

    ```{bash}
    ┌──────────┬──────────────────────┬─────────┬─────────┬────────┬───┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐
    │ rider_id │         name         │ gender  │ country │ height │ … │ race__current__wom…  │ race__max30__women…  │ race__max30__women…  │ race__max90__women…  │ race__max90__women…  │
    │  int64   │       varchar        │ varchar │ varchar │ int64  │   │        int64         │       varchar        │        int64         │       varchar        │        int64         │
    ├──────────┼──────────────────────┼─────────┼─────────┼────────┼───┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
    │  1234567 │ fake_name 1          │ M       │ us      │    177 │ … │                 NULL │ NULL                 │                 NULL │ NULL                 │                 NULL │
    │  2345678 │ fake_name 2          │ F       │ ca      │    170 │ … │                    7 │ Gold                 │                    7 │ Gold                 │   ...    
    ```




### Transform data with DuckDB

Once data is staged to the local DuckDB database, the `duckdb` module can be used to query the database with SQL.

```{python}
import duckdb

with duckdb.connect('zrapp.duckdb') as con:
    data = con.sql(f'''
                    with 
                        source as (select * from staging.stg_riders),
                        
                        fix_weight as (
                            select * exclude(weight),
                                -- DLT issue: loads floats as ints if round to .0
                                coalesce(weight, weight__v_double) as weight
                            from source
                        ),

                        select_variables as (
                            select 
                                rider_id,
                                name as rider,
                                weight,
                                power__w5 as watts_5,
                                power__w60 as watts_60,
                                power__w300 as watts_300
                            from fix_weight),
                        
                        derive_wkg as (
                            select *,
                                watts_5/weight as wkg_5,
                                watts_60/weight as wkg_60,
                                watts_300/weight as wkg_300
                            from select_variables
                        )
                    
                    select * from derive_wkg
                    
                    ''').pl()
    con.sql('create schema if not exists core')
    con.sql('create or replace table core.dim_riders as select * from data')
    

print(con.sql('select * from core.dim_riders'))
print(con.sql('describe staging.stg_riders'))
```




<!-- 
### Create a dashboard in Streamlit
-->
