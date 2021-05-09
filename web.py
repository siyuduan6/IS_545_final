import streamlit as st
import pandas as pd
from folium import plugins
import numpy as np
import matplotlib.pyplot as plt
import folium
import altair as alt
import pydeck as deck
import time


st.text(" Welcome to Drive Safe in Chicago")
rl_vio = pd.read_csv("https://gist.githubusercontent.com/siyuduan6/4a84c17af99103f5b5d91a538804c328/raw/47ff26d3cae44b06fe124357ef68db8b0fb5996a/crashes.csv")
rl_vio1 = pd.read_csv("https://gist.githubusercontent.com/siyuduan6/4e46bffd955eb7d0fad85d03a7b25729/raw/4071e08a6521225856ac4ee837e71b1eb88ef7c1/red_light_violation.csv")
rl_vio2 = pd.read_csv("https://gist.githubusercontent.com/siyuduan6/0af6a745ce42054d6e14627a54e91301/raw/5f1003274760cfa0abfaf76af9971e5102bd3cbf/Speed_Camera_Violations.csv")
rl_lo = pd.read_csv("https://data.cityofchicago.org/api/views/7mgr-iety/rows.csv?accessType=DOWNLOAD")
s_loc =pd.read_csv("https://data.cityofchicago.org/api/views/4i42-qv3h/rows.csv?accessType=DOWNLOAD")
s_loc["ADDRESS"] = s_loc["ADDRESS"].str.split("(",expand=True).iloc[:,0]
r_la = list(rl_lo["LATITUDE"])
r_lo = list(rl_lo["LONGITUDE"])


latitude = 41.8781
longitude = -87.6298



def icon_adder(df, color, shape, info):
    chi_map = folium.Map(location=[latitude, longitude], zoom_start=12, tiles='OpenStreetMap')
    r_la = list(df["LATITUDE"])
    r_lo = list(df["LONGITUDE"])
    labels = list(info)
    incidents = folium.map.FeatureGroup(opacity=0.5)
    for la, lo, label in zip(r_la, r_lo, labels):
        folium.Marker([la, lo],popup =label,icon=folium.Icon(color = color, icon = shape), tooltip="Show me").add_to(chi_map)
    chi_map.add_child(incidents)

    return folium_static(chi_map)

def point_adder(df, info):
    chi_map1 = folium.Map(location=[latitude, longitude], zoom_start=12,tiles='OpenStreetMap')
    r_la = list(df["LATITUDE"])
    r_lo = list(df["LONGITUDE"])
    labels = list(info)
    incidents = plugins.MarkerCluster().add_to(chi_map1)
    for la, lo, label in zip(r_la, r_lo, labels):
        folium.Marker([la, lo],popup =label,icon=None, tooltip="Show me").add_to(incidents)
    chi_map1.add_child(incidents)

    return folium_static(chi_map1)

def year_pick():
    st.text(" Car Crash Accident in Chicago ")
    crash = rl_vio[rl_vio["YEAR"] > 2015].groupby("YEAR")
    crash1, crash2, crash3, crash4, crash5, crash6 = [(x, crash.get_group(x)) for x in crash.groups]
    year_list = [2016, 2017, 2018, 2019, 2020, 2021]
    file_list = [crash1, crash2, crash3, crash4, crash5, crash6]
    options = st.multiselect('Year',year_list)
    if options in year_list:
        index = year_list.index(options)
        file = file_list[index][1].dropna(subset=["LOCATION"])
        return point_adder(file, file["LOCATION"])
    else:
        index = 5
        file = file_list[index][1].dropna(subset=["LOCATION"])
        return point_adder(file, file["LOCATION"])

@st.cache
def vio_year():
    st.text("Violation Cases in Chicago Per Month")
    year = st.select_slider("Year", options=[2015, 2016, 2017, 2018, 2019, 2020], value=2020)
    vio1 = rl_vio1[rl_vio1["YEAR"] == year].groupby("MONTH")["VIOLATIONS"].sum()
    vio2 = rl_vio2[rl_vio2["YEAR"] == year].groupby("MONTH")["VIOLATIONS"].sum()
    vio = pd.DataFrame(vio1).merge(pd.DataFrame(vio2), left_index=True, right_index=True).rename(
        columns={"VIOLATIONS_x": "Red Light", "VIOLATIONS_y": "Speed"})
    fig = plt.figure(figsize=(8, 4))  # Create matplotlib figure
    ax = fig.add_subplot(111)  # Create matplotlib axes
    ax2 = ax.twinx()  # Create another axes that shares the same x-axis as ax.
    width = 0.8
    vio.plot(kind='bar', ax=ax, width=width, rot=0, cmap='tab10')
    ax.set_ylabel('Red Light Violation Cases')
    ax2.set_ylabel('Speed Violation Cases')
    ax.set_xlabel("Month")
    plt.grid(False)
    plt.xticks(rotation=45)
    return fig

@st.cache
def stack_bar_chart():
    st.text("Top 5 Causes of Car Crash Accident")
    source = rl_vio[rl_vio["YEAR"] > 2015]
    crash_type = ["FAILING TO REDUCE SPEED TO AVOID CRASH",
                  "FAILING TO YIELD RIGHT-OF-WAY",
                  "FOLLOWING TOO CLOSELY",
                  "IMPROPER LANE USAGE", "IMPROPER OVERTAKING/PASSING"]
    cha = alt.Chart(source).mark_bar(size=20).encode(
        alt.Y('YEAR'),
        alt.X('count(CRASH_RECORD_ID)'),
        color="PRIM_CONTRIBUTORY_CAUSE",
        order=alt.Order(
            # Sort the segments of the bars by this field
            'PRIM_CONTRIBUTORY_CAUSE',
            sort='ascending'
        )).transform_filter(
        alt.FieldOneOfPredicate(field='PRIM_CONTRIBUTORY_CAUSE', oneOf=crash_type)
    ).interactive()

    select1 = st.sidebar.selectbox("Choose the crash type: ",crash_type)
    select2 = st.sidebar.selectbox("Choose the year: ",source["YEAR"].unique())
    select3 = st.sidebar.multiselect("Choose the month:",source["MONTH"].unique(),
                                  value=source["MONTH"])
    if select1 in crash_type:
        alt.Chart(source).mark_bar().encode(
            y='YEAR',
            x='count(CRASH_RECORD_ID)'
            ).transform_filter(
            alt.datum.PRIM_CONTRIBUTORY_CAUSE == select1
        )
        if select2:
            alt.Chart(source).mark_bar().encode(
                y='MONTH',
                x='count(CRASH_RECORD_ID)'
            ).transform_filter(
                (alt.datum.PRIM_CONTRIBUTORY_CAUSE == select1) & (alt.datum.YEAR == select2)&
                (alt.FieldOneOfPredicate(field='MONTH', oneOf=select3))
            )
@st.cache
def summary():
    st.text("Summary of Car Crashes")
    source = rl_vio[rl_vio["YEAR"] > 2015]
    crash_type = ["FAILING TO REDUCE SPEED TO AVOID CRASH",
                  "FAILING TO YIELD RIGHT-OF-WAY",
                  "FOLLOWING TOO CLOSELY",
                  "IMPROPER LANE USAGE", "IMPROPER OVERTAKING/PASSING"]
    cha = alt.Chart(source).mark_bar().encode(
        alt.X('YEAR'),
        alt.Y('count(CRASH_RECORD_ID)'),
        row="PRIM_CONTRIBUTORY_CAUSE",
        column="DAMAGE"
    ).transform_filter(
        alt.FieldOneOfPredicate(field='PRIM_CONTRIBUTORY_CAUSE', oneOf=crash_type)
    ).interactive()

    st.text("Summary of Violatons")
    alt.data_transformers.enable('default', max_rows=None)
    source1 = rl_vio1
    source2 = rl_vio2
    selection = alt.selection_interval()

    scale = alt.Scale(domain=[2015, 2016, 2017, 2018, 2019, 2020],
                      range=["#e7ba52", "#c7c7c7", "#aec7e8", "#659CCA", "#1f77b4", "#9467bd"])
    color = alt.condition(selection,
                          alt.Color('YEAR:O', scale=scale),
                          alt.value('darkgray'))
    rl = alt.Chart(source1).mark_bar(size=20).encode(
        alt.Tooltip(["YEAR:O", "MONTH:O", "sum(VIOLATIONS):Q"]),
        alt.X('MONTH',
              axis=alt.Axis(grid=False)),
        alt.Y('sum(VIOLATIONS):Q', title="Red Light Violation Number", axis=alt.Axis(grid=False)),
        color=color
    )

    speed = alt.Chart(source2).mark_bar(size=20).encode(
        alt.X('MONTH', axis=alt.Axis(grid=False)),
        alt.Y('sum(VIOLATIONS):Q', title="Speed Violation Number", axis=alt.Axis(grid=False)),
        color=color
    )
    legend = alt.Chart(source1).mark_rect().encode(
        alt.Y('YEAR:O'),
        color=color
    ).add_selection(
        selection
    )
    alt.hconcat(
        rl,
        speed, legend,
        title="Red Light Violations and Speed Violations"
    )




@st.cache
def int_vega():
    st.text("Crashes and Injures in the same period")
    source = rl_vio[rl_vio["YEAR"] > 2015]
    source2 = source.dropna(subset=["INJURIES_TOTAL"])
    scale = alt.Scale(domain=[2016, 2017, 2018, 2019, 2020, 2021],
                      range=["#e7ba52", "#c7c7c7", "#aec7e8", "#659CCA", "#1f77b4", "#9467bd"])
    color = alt.Color('YEAR:O', scale=scale)
    click = alt.selection_multi(encodings=['color'])

    # Top panel is scatter plot of temperature vs time
    points = alt.Chart(source).mark_point().encode(
        alt.Tooltip(["YEAR:O", "MONTH:O", "count(CRASH_RECORD_ID):Q", "sum(INJURIES_TOTALL):Q"]),
        alt.X('MONTH:O', title='Month',
              axis=alt.Axis(
                  offset=10,
                  labelAngle=0,
                  ticks=True,
                  minExtent=30,
                  grid=False
              )
              ),
        alt.Y('count(CRASH_RECORD_ID):Q',
              scale=alt.Scale(domain=[0, 200]),
              axis=alt.Axis(
                  offset=10,
                  ticks=True,
                  minExtent=30,
                  grid=False,
              )),
        color=alt.condition(brush, color, alt.value('darkgray')),
        size=alt.SizeValue(75)

    ).properties(
        width=550,
        height=300,
    ).add_selection(
        brush
    ).transform_filter(
        click
    )

    lines = alt.Chart(source2).mark_circle().encode(
        alt.Tooltip(["YEAR:O", "MONTH:O", "count(CRASH_RECORD_ID):Q", "sum(INJURIES_TOTAL):Q"]),
        alt.X('MONTH:O',
              axis=alt.Axis(
                  offset=10,
                  ticks=True,
                  labelAngle=0,
                  minExtent=30,
                  grid=False
              )),
        alt.Y("sum(INJURIES_TOTAL):Q",
              title="Injured Number",
              axis=alt.Axis(
                  offset=10,
                  ticks=True,
                  minExtent=30,
                  grid=False,
              )), color=alt.condition(brush, color, alt.value('red')),
        size=alt.SizeValue(75)
    ).transform_filter(
        brush
    ).properties(
        width=550,
    ).add_selection(
        click
    )
    alt.hconcat(
        points,
        lines,
        title="Cases VS Injured"
    )


if __name__ == '__main__':
    st.write(summary())
    vio = vio_year()
    st.write(vio)
    st.write(stack_bar_chart())
    st.write(int_vega())
    chi_map_rl = icon_adder(rl_lo,"red","info-sign", rl_lo["INTERSECTION"])
    chi_map_v = icon_adder(s_loc,"blue","glyphicon glyphicon-warning-sign",s_loc["ADDRESS"])
    crash = year_pick()
    sc = st.sidebar.checkbox("See the speed camera location?", False)
    rlc = st.sidebar.checkbox("See the red light camera location?", False)
    if sc:
        time.sleep(5)
        st.write(chi_map_v)
    if rlc:
        time.sleep(5)
        st.write(chi_map_rl)

    st.write(crash)

