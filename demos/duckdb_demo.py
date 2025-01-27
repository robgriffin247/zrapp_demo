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

    print(con.sql('select column_name from (describe staging.stg_riders)').fetchall())