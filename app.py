import streamlit as st
import pandas as pd
import geopandas as gpd
from streamlit_folium import folium_static
import folium

# make df
datasource_url="https://www.fhwa.dot.gov/bridge/nbi/2021/delimited/NJ21.txt"
df = pd.read_csv(datasource_url)

# filter by county
df = df.loc[df['COUNTY_CODE_003'] == 17]

# convert degrees,minutes, seconds to decimal degrees
df['lat_deg'] = df['LAT_016'].apply(lambda x: str(x)[0:2])
df['lat_min'] = df['LAT_016'].apply(lambda x: str(x)[2:4])
df['lat_sec'] = df['LAT_016'].apply(lambda x: str(x)[4:6])
df['lat_hem'] = df['LAT_016'].apply(lambda x: str(x)[6:8])
df['lon_deg'] = df['LONG_017'].apply(lambda x: str(x)[0:2])
df['lon_min'] = df['LONG_017'].apply(lambda x: str(x)[2:4])
df['lon_sec'] = df['LONG_017'].apply(lambda x: str(x)[4:6])
df['lon_hem'] = df['LONG_017'].apply(lambda x: str(x)[6:8])
def lat_dms2dd(row):
    dd = float(row.lat_deg) + float(row.lat_min)/60 + float(row.lat_sec)/(60*60)
    return dd
def lon_dms2dd(row):
    dd = float(row.lon_deg) + float(row.lon_min)/60 + float(row.lon_sec)/(60*60)
    dd *= -1
    return dd
df['lat'] = df.apply(lambda x: lat_dms2dd(x), axis=1)
df['lon'] = df.apply(lambda x: lon_dms2dd(x), axis=1)

# drop weird outliers
indexNames = df[ (df.lon > -70) ].index
df.drop(indexNames , inplace=True)
indexNames = df[ (df.lon < -80) ].index
df.drop(indexNames , inplace=True)

# create map
map = folium.Map(location=[40.7178, -74.10], zoom_start=12, tiles ='Stamen Toner')

# populate popups
def render_popup(row):
    #FIXME: the weird line at the top
    html_data = [f"<tr><td>{label}</td><td>{value}</td></tr>" for (label, value) in row.items()]
    html=f"""
    <h3> {row.FEATURES_DESC_006A.strip("'")} ({row.STRUCTURE_NUMBER_008})</h3>
    <h4> Structural evaluation rating {row.STRUCTURAL_EVAL_067} out of 9</h4>
    <table>
    {''.join([str(x) for x in html_data])}
    </table>
    """
    iframe = folium.IFrame(html=html, width=500, height=300)
    return folium.Popup(iframe, max_width=500)

# create markers
for index, row in df.iterrows():
    tooltip = f"Structure No.{row.STRUCTURE_NUMBER_008} built in {row.YEAR_BUILT_027}. Structural rating {row.STRUCTURAL_EVAL_067} out of 9."
    structural_rating = int(row.STRUCTURAL_EVAL_067)
    if structural_rating <= 3:
        folium.CircleMarker([row["lat"],row["lon"]],
                    color='red',
                    radius=3,
                    popup=render_popup(row),  
                    tooltip=tooltip
                    ).add_to(map)
    elif structural_rating in range(4,5):
        folium.CircleMarker([row["lat"],row["lon"]],
                    color='yellow',
                    radius=3,
                    popup=render_popup(row), 
                    tooltip=tooltip
                    ).add_to(map)
    else:
        folium.CircleMarker([row["lat"],row["lon"]],
                    color='gray',
                    radius=3,
                    popup=render_popup(row), 
                    tooltip=tooltip
                    ).add_to(map)


# header
st.header("The Bridges of Hudson County")
st.write("The map below indicates the location of each bridge in the [National Bridge Inventory](https://www.fhwa.dot.gov/bridge/nbi/2021/delimited/NJ21.txt). You can click on a circle to view that bridge's records, or browse the data table below. Documentation is [here](https://www.fhwa.dot.gov/bridge/nbi/131216_a1.pdf).")

# call to render Folium map in Streamlit
folium_static(map)

# table
st.dataframe(df)
