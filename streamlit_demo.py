import streamlit as st
import pandas as pd
import polars as pl
import numpy as np
import re
import plotly.express as px

from zrapp.endpoints import get_riders


# DATA ======================================================================================================================
# Converts text string into list of ints needed for get_riders() call
def string_to_ids(id_string):
        output = [int(i) for i in re.sub(r'\D+', ',', id_string).split(',') if i != '']
        return output


rider_id_string = st.text_area('Enter Rider IDs', help='''Enter one or more rider ID numbers &mdash; all numbers will be parsed as IDs, 
                               everything else will be removed, so you can add IDs, urls with IDs in etc. as long as all numbers are IDs 
                               and all IDs are separated by a non-numeric character!''')

rider_ids = string_to_ids(rider_id_string)


riders = get_riders(rider_ids=rider_ids)

# Extract data of interest - I'll be making power curves to compare riders
data = []
for rider in riders:
    rider_data = {
            'name':str(rider['name']) if 'name' in rider.keys() else None,
            'id':int(rider['riderId']) if 'riderId' in rider.keys() else None,
            'watts_5':int(rider['power']['w5']) if 'power' in rider.keys() and 'w5' in rider['power'].keys() else None,
            'watts_15':int(rider['power']['w15']) if 'power' in rider.keys() and 'w15' in rider['power'].keys() else None,
            'watts_30':int(rider['power']['w30']) if 'power' in rider.keys() and 'w30' in rider['power'].keys() else None,
            'watts_60':int(rider['power']['w60']) if 'power' in rider.keys() and 'w60' in rider['power'].keys() else None,
            'watts_120':int(rider['power']['w120']) if 'power' in rider.keys() and 'w120' in rider['power'].keys() else None,
            'watts_300':int(rider['power']['w300']) if 'power' in rider.keys() and 'w300' in rider['power'].keys() else None,
            'watts_1200':int(rider['power']['w1200']) if 'power' in rider.keys() and 'w1200' in rider['power'].keys() else None,
            'wkg_5':float(rider['power']['wkg5']) if 'power' in rider.keys() and 'wkg5' in rider['power'].keys() else None,
            'wkg_15':float(rider['power']['wkg15']) if 'power' in rider.keys() and 'wkg15' in rider['power'].keys() else None,
            'wkg_30':float(rider['power']['wkg30']) if 'power' in rider.keys() and 'wkg30' in rider['power'].keys() else None,
            'wkg_60':float(rider['power']['wkg60']) if 'power' in rider.keys() and 'wkg60' in rider['power'].keys() else None,
            'wkg_120':float(rider['power']['wkg120']) if 'power' in rider.keys() and 'wkg120' in rider['power'].keys() else None,
            'wkg_300':float(rider['power']['wkg300']) if 'power' in rider.keys() and 'wkg300' in rider['power'].keys() else None,
            'wkg_1200':float(rider['power']['wkg1200']) if 'power' in rider.keys() and 'wkg1200' in rider['power'].keys() else None,
            }
    
    data.append(rider_data)

if len(data)>0:
    df = pl.DataFrame(data)

    wkg = st.toggle('W/kg', value=False)


    if wkg:
        selected_df = df[['name', 'id'] + [column for column in df.columns if 'wkg' in column]]
    else:
        selected_df = df[['name', 'id'] + [column for column in df.columns if 'watts' in column]]


    # OUTPUT ========================================================================================================================
    # - switch to pandas for pandas.styler
    styled_df = pd.DataFrame(selected_df, columns=selected_df.columns).style.background_gradient(
        axis=None, cmap='YlOrRd', 
        subset=[i for i in selected_df.columns if 'watts' in i or 'wkg' in i],)

    # Show data
    # - Table of power values
    st.dataframe(styled_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    'name':st.column_config.TextColumn('Rider'),
                    'id':st.column_config.NumberColumn('Rider ID', format='%i'),
                    'watts_5':st.column_config.NumberColumn('5s', format='%i'),
                    'watts_15':st.column_config.NumberColumn('15s', format='%i'),
                    'watts_30':st.column_config.NumberColumn('30s', format='%i'),
                    'watts_60':st.column_config.NumberColumn('1m', format='%i'),
                    'watts_120':st.column_config.NumberColumn('2m', format='%i'),
                    'watts_300':st.column_config.NumberColumn('5m', format='%i'),
                    'watts_1200':st.column_config.NumberColumn('20m', format='%i'),
                    'wkg_5':st.column_config.NumberColumn('5s', format='%.2f'),
                    'wkg_15':st.column_config.NumberColumn('15s', format='%.2f'),
                    'wkg_30':st.column_config.NumberColumn('30s', format='%.2f'),
                    'wkg_60':st.column_config.NumberColumn('1m', format='%.2f'),
                    'wkg_120':st.column_config.NumberColumn('2m', format='%.2f'),
                    'wkg_300':st.column_config.NumberColumn('5m', format='%.2f'),
                    'wkg_1200':st.column_config.NumberColumn('20m', format='%.2f'),
                })

    # - Graph
    rotated = selected_df.unpivot(index=['id', 'name'])
    rotated = rotated.with_columns(pl.col('variable').str.split_exact('_', 1).struct.rename_fields(['unit', 'seconds'])).unnest('variable')
    rotated = rotated.with_columns(log_seconds=pl.col('seconds').log())

    fig = px.line(rotated, 
                  title='Power Curves', 
                  x='log_seconds', 
                  y='value', 
                  color='name', 
                  line_dash='name', 
                  markers=True,
                  labels={'log_seconds':'Duration',
                          'value':f'Power ({"W/kg" if wkg else "W"})',
                          'name':'Rider',})

    fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis = dict(
            tickmode = 'array',
            tickvals = [np.log(i) for i in [5,15,30,60,120,300,1200]],
            ticktext = ['5s', '15s', '30s', '1m', '2m', '5m', '20m']
        ))

    st.plotly_chart(fig)