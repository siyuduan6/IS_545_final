import streamlit as st
import pandas as pd
from folium import plugins
import numpy as np
import matplotlib.pyplot as plt
import folium
import altair as alt
import pydeck as deck
import time
from streamlit_folium import folium_static

@st.cache(suppress_st_warning=True) 
def doc(f):
    rl_vio = pd.read_csv(
        "https://gist.githubusercontent.com/siyuduan6/068654ee0ee0e4ed401155df7063d3b3/raw/d945fed2395cb4d6dab7b5eec97d932129c3d49a/Crash.csv")
    rl_vio1 = pd.read_csv(
        "https://gist.githubusercontent.com/siyuduan6/d120e6170e8013068b7e36ac1ce9a6d9/raw/286b35bc519075b926d1170c7a1ecfce4e281df4/Red_Light.csv")
    rl_vio2 = pd.read_csv(
        "https://gist.githubusercontent.com/siyuduan6/28d9ceb3e4789ef7456ce4c3183d6b62/raw/43c81cb16a34d14db3b760dab1ea02b64cf51962/Speed.csv")
    crash = pd.read_csv("https://gist.githubusercontent.com/siyuduan6/67d4bcb2a15af7f462c58a18b252e332/raw/7e11d168762c30f1e0bbd08fda2ad0191fcc9c34/Traffic_Crashes.csv")
    rl_lo = pd.read_csv("https://data.cityofchicago.org/api/views/7mgr-iety/rows.csv?accessType=DOWNLOAD")
    s_loc = pd.read_csv("https://data.cityofchicago.org/api/views/4i42-qv3h/rows.csv?accessType=DOWNLOAD")
    s_loc["ADDRESS"] = s_loc["ADDRESS"].str.split("(", expand=True).iloc[:, 0]
    r_la = list(rl_lo["LATITUDE"])
    r_lo = list(rl_lo["LONGITUDE"])
    
    file_list = [rl_vio, rl_vio1, rl_vio2, rl_lo, s_loc, r_la, r_lo, crash]
    return file_list[f]

#def split_date1(df):
#    df = df.dropna(subset=['VIOLATION DATE'])
#    df['YEAR'] = pd.DatetimeIndex(df['VIOLATION DATE']).year
#    df['MONTH'] = pd.DatetimeIndex(df['VIOLATION DATE']).month
#    return df

def split_date2(df):
    df = df.dropna(subset=['CRASH_DATE'])
    df['YEAR'] = pd.DatetimeIndex(df['CRASH_DATE']).year
    df['MONTH'] = pd.DatetimeIndex(df['CRASH_DATE']).month
    return df


def chicago_map():
    latitude = 41.8781
    longitude = -87.6298
    chi_m = folium.Map(location=[latitude, longitude], zoom_start=12, tiles='OpenStreetMap')
    return chi_m


def icon_adder(df, color, shape, info):
    latitude = 41.8781
    longitude = -87.6298
    chi_map = folium.Map(location=[latitude, longitude], zoom_start=12, tiles='OpenStreetMap')
    r_la = list(df["LATITUDE"])
    r_lo = list(df["LONGITUDE"])
    labels = list(info)
    incidents = folium.map.FeatureGroup(opacity=0.5)
    for la, lo, label in zip(r_la, r_lo, labels):
        folium.Marker([la, lo], popup=label, icon=folium.Icon(color=color, icon=shape), tooltip="Show me").add_to(
            chi_map)
    return chi_map


def icon_adder_re(map1, df2, color2, shape2, info2):
    r_la = list(df2["LATITUDE"])
    r_lo = list(df2["LONGITUDE"])
    labels = list(info2)
    incidents = folium.map.FeatureGroup(opacity=0.5)
    for la, lo, label in zip(r_la, r_lo, labels):
        folium.Marker([la, lo], popup=label, icon=folium.Icon(color=color2, icon=shape2), tooltip="Show me").add_to(
            map1)

    return map1


def point_adder(df, info):
    latitude = 41.8781
    longitude = -87.6298
    chi_map1 = folium.Map(location=[latitude, longitude], zoom_start=12, tiles='OpenStreetMap')
    r_la = list(df["LATITUDE"])
    r_lo = list(df["LONGITUDE"])
    labels = list(info)
    incidents = plugins.MarkerCluster().add_to(chi_map1)
    for la, lo, label in zip(r_la, r_lo, labels):
        folium.Marker([la, lo], popup=label, icon=None, tooltip="Show me").add_to(incidents)
    chi_map1.add_child(incidents)
    return folium_static(chi_map1)


def year_pick():
    crash = split_date2(doc(7))
    year_list = [2016, 2017, 2018, 2019, 2020, 2021]
    file = crash.dropna(subset=["LOCATION"])
    st.sidebar.title("Number of car crashes at each block?")
    options = st.sidebar.multiselect('View Car Crash by Years', year_list)
    if options:
        file = crash[crash["YEAR"].isin(options)].dropna(subset=["LOCATION"])
    return point_adder(file, file["LOCATION"])

def vio_year():
    rl_vio1 = doc(1).dropna(subset=["MONTH"])
    rl_vio2 = doc(2).dropna(subset=["MONTH"])
    rl_vio1["DATE"] = pd.to_datetime(rl_vio1["YEAR"].astype("str").str.cat(rl_vio1["MONTH"].astype("str")),format="%Y%m")
    rl_vio2["DATE"] = pd.to_datetime(rl_vio2["YEAR"].astype("str").str.cat(rl_vio2["MONTH"].astype("str")),format="%Y%m")

    vio3 =pd.DataFrame(rl_vio1).merge(pd.DataFrame(rl_vio2), on = "DATE").rename(
    columns={"VIOLATIONS_x": "Red Light", "VIOLATIONS_y": "Speed"})
    st.area_chart(vio3.set_index("DATE")[["Red Light", "Speed"]], width =850) 
    st.text("Slide the slider to view the number of violations in Chicago.")
    year = st.select_slider("Year", options=[2015, 2016, 2017, 2018, 2019, 2020, 2021], value=2018)
    vio1 = rl_vio1[rl_vio1["YEAR"] == year].groupby("MONTH")["VIOLATIONS"].sum()
    vio2 = rl_vio2[rl_vio2["YEAR"] == year].groupby("MONTH")["VIOLATIONS"].sum()
    vio = pd.DataFrame(vio1).merge(pd.DataFrame(vio2), left_index=True, right_index=True).rename(
        columns={"VIOLATIONS_x": "Red Light", "VIOLATIONS_y": "Speed"})


    fig = plt.figure(figsize=(7, 4))  # Create matplotlib figure
    ax = fig.add_subplot(111)  # Create matplotlib axes
    ax2 = ax.twinx()  # Create another axes that shares the same x-axis as ax.
    width = 0.8
    vio.plot(kind='bar', ax=ax, width=width, rot=0, color=["#e7ba52", "#1f77b4"])
    ax.set_ylabel('Red Light Violation Cases')
    ax2.set_ylabel('Speed Violation Cases')
    ax.set_xlabel("Month")
    plt.grid(False)
    plt.xticks(rotation=45)
           
    return fig

def stack_bar_chart():
    rl_vio = doc(0)
    #rl_vio["YEAR"] = rl_vio["YEAR"].astype("int")
    source = rl_vio[rl_vio["YEAR"]>2014]
    crash_type = ["FAILING TO REDUCE SPEED TO AVOID CRASH",
                  "FAILING TO YIELD RIGHT-OF-WAY",
                  "FOLLOWING TOO CLOSELY",
                  "IMPROPER LANE USAGE", "IMPROPER OVERTAKING/PASSING"]
    st.sidebar.title("What causes the accidents?")
    select1 = st.sidebar.selectbox("Choose the crash type: ", crash_type)
    select2 = st.sidebar.selectbox("Choose the year: ", [2015,2016,2017,2018,2019,2020,2021])
    st.text("Go back to see all types of causes? Click 'View All'!")
    if st.button("View All"):
        cha = alt.Chart(source).mark_bar(size=20).encode(
            alt.Tooltip(["YEAR:O", "MONTH:O", "sum(RECORDS)"]),
            alt.Y('YEAR:O', title="Year",axis=alt.Axis(grid=False, labelAngle=0)),
            alt.X('sum(RECORDS)', axis=alt.Axis(grid=False, labelAngle=0), title="Records"),
            color="CAUSE",
            order=alt.Order(
                # Sort the segments of the bars by this field
                'CAUSE',
                sort='ascending'
            )).properties(
            height=400,
            width=850).transform_filter(
            alt.FieldOneOfPredicate(field='CAUSE', oneOf=crash_type)
        ).interactive()
    else:   
        if select1 in crash_type:
            cha = alt.Chart(source).mark_bar(size=20).encode(
                alt.Tooltip(["CAUSE:N", "sum(RECORDS)"]),
                alt.Y('YEAR:O', axis=alt.Axis(grid=False, labelAngle=0), title="Year"),
                alt.X('sum(RECORDS)', axis=alt.Axis(grid=False, labelAngle=0,tickMinStep = 1), title="Records"),
                color=alt.value("#e7ba52")
            ).properties(
                height=400,
                width=600
            ).transform_filter(
                alt.datum.CAUSE == select1
            )
            if select2:
                cha = alt.Chart(source).mark_bar(size=20).encode(
                    alt.Tooltip(["YEAR:O", "MONTH:O", "sum(RECORDS)"]),
                    alt.Y('MONTH:O', axis=alt.Axis(grid=False, labelAngle=0), title="Month"),
                    alt.X('sum(RECORDS)', axis=alt.Axis(grid=False, labelAngle=0,tickMinStep = 1), title="Records"),
                    color=alt.value("darkgray")
                ).properties(
                    height=400,
                    width=600).transform_filter(
                    alt.datum.CAUSE == select1).transform_filter(alt.datum.YEAR == select2)
                
    return cha


def summary():
    rl_vio = doc(0)
    source = rl_vio[rl_vio["YEAR"] > 2015]
    crash_type = ["FAILING TO REDUCE SPEED TO AVOID CRASH",
                  "FAILING TO YIELD RIGHT-OF-WAY",
                  "FOLLOWING TOO CLOSELY",
                  "IMPROPER LANE USAGE", "IMPROPER OVERTAKING/PASSING"]
    cha = alt.Chart(source).mark_bar(size=20).encode(
        alt.Tooltip(["YEAR:O","sum(RECORDS)","CAUSE","DAMAGE"]),
        alt.X('YEAR:O', axis=alt.Axis(grid=False, labelAngle=0), title="Year"),
        alt.Y('sum(RECORDS)', axis=alt.Axis(grid=False, labelAngle=0), title="Records"),
        alt.Row("CAUSE",title="Cause of Accidents"),
        alt.Column("DAMAGE", title="Damage")
    ).properties(
        width=200
    ).transform_filter(
        alt.FieldOneOfPredicate(field='CAUSE', oneOf=crash_type)
    ).interactive()
    sum = alt.vconcat(
        cha,
        title="Summary of Car Crash Accidents"
    )
    return sum

 
def summary_rl():
    alt.data_transformers.enable('default', max_rows=None)
    source1 = doc(1).dropna(subset=["MONTH"])
    source2 = doc(2).dropna(subset=["MONTH"])        
    selection = alt.selection_interval()
    scale = alt.Scale(domain=[2015, 2016, 2017, 2018, 2019, 2020],
                      range=["#e7ba52", "#c7c7c7", "#aec7e8", "#659CCA", "#1f77b4", "#9467bd"])
    color = alt.condition(selection,
                          alt.Color('YEAR:O', scale=scale),
                          alt.value('darkgray'))
    rl = alt.Chart(source1).mark_bar(size=20).encode(
        alt.Tooltip(["YEAR:O", "MONTH:O", "sum(VIOLATIONS):Q"]),
        alt.X('MONTH:O',title="Month",
              axis=alt.Axis(grid=False, labelAngle=0)),
        alt.Y('sum(VIOLATIONS):Q', title="Red Light Violation Number", axis=alt.Axis(grid=False, labelAngle=0)),
        color=color
    ).properties(
        width=350
    )

    speed = alt.Chart(source2).mark_bar(size=20).encode(
        alt.Tooltip(["YEAR:O", "MONTH:O", "sum(VIOLATIONS):Q"]),
        alt.X('MONTH:O', axis=alt.Axis(grid=False, labelAngle=0), title="Month"),
        alt.Y('sum(VIOLATIONS):Q', title="Speed Violation Number", axis=alt.Axis(grid=False, labelAngle=0)),
        color=color
    ).properties(
        width=350
    )
    
    legend = alt.Chart(source1).mark_rect().encode(
        alt.Y('YEAR:O'),
        color=color
    ).transform_filter(
    alt.FieldOneOfPredicate(field = "YEAR", oneOf= [2015, 2016, 2017, 2018, 2019, 2020])
    ).add_selection(
        selection
    )
    vio = alt.hconcat(
        rl,
        speed, legend,
        title="Summary of Violations: Red Light Violations and Speed Violations"
    )

    return vio

def int_vega():
    rl_vio = doc(0)
    rl_vio["YEAR"] = rl_vio["YEAR"].astype("int")
    source = rl_vio[rl_vio["YEAR"] > 2015]
    source2 = source
    scale = alt.Scale(domain=[2016, 2017, 2018, 2019, 2020, 2021],
                      range=["#e7ba52", "#c7c7c7", "#aec7e8", "#659CCA", "#1f77b4", "#9467bd"])
    color = alt.Color('YEAR:O', scale=scale)
    click = alt.selection_multi(encodings=['color'])
    brush = alt.selection_interval()

    st.text("How about damage level? Click 'Show Damage Level'!")
    if st.button("Show Damage Level"):
        points = alt.Chart(source).mark_point().encode(
            alt.Tooltip(["YEAR:O", "MONTH:O", "sum(RECORDS):Q", "sum(INJURIES):Q"]),
            alt.X('MONTH:O', title='Month',
                  axis=alt.Axis(
                      offset=10,
                      labelAngle=0,
                      ticks=True,
                      minExtent=30,
                      grid=False
                  )
                  ),
            alt.Y('sum(RECORDS):Q',
                  scale=alt.Scale(domain=[0, 6000]),
                  axis=alt.Axis(
                      offset=10,
                      ticks=True,
                      minExtent=30,
                      grid=False,
                  ), title="Records"),
            color=alt.condition(brush, color, alt.value('darkgray')),
            size="DAMAGE:N"
        ).properties(
            width=650,
            height=400,
        ).add_selection(
            brush
        ).transform_filter(
            click
        )

        lines = alt.Chart(source2).mark_circle().encode(
            alt.Tooltip(["YEAR:O", "MONTH:O", "sum(RECORDS):Q", "sum(INJURIES):Q"]),
            alt.X('MONTH:O',title="Month",
                  axis=alt.Axis(
                      offset=10,
                      ticks=True,
                      labelAngle=0,
                      minExtent=30,
                      grid=False
                  )),
            alt.Y("sum(INJURIES):Q",
                  title="Injuries",
                  axis=alt.Axis(
                      offset=10,
                      ticks=True,
                      minExtent=30,
                      grid=False,
                  )), color=alt.condition(brush, color, alt.value('red')),
            size="DAMAGE:N"
        ).transform_filter(
            brush
        ).properties(
            width=650,
        ).add_selection(
            click
        )
        vega = alt.vconcat(
            points,
            lines,
            title="Cases VS Injured"
        )
    else:
        points = alt.Chart(source).mark_point().encode(
        alt.Tooltip(["YEAR:O", "MONTH:O", "sum(RECORDS):Q", "sum(INJURIES):Q"]),
        alt.X('MONTH:O', title='Month',
              axis=alt.Axis(
                  offset=10,
                  labelAngle=0,
                  ticks=True,
                  minExtent=30,
                  grid=False
              )
              ),
        alt.Y('sum(RECORDS):Q',
              scale=alt.Scale(domain=[0, 12000]),
              axis=alt.Axis(
                  offset=10,
                  ticks=True,
                  minExtent=30,
                  grid=False,
              ), title="Records"),
        color=alt.condition(brush, color, alt.value('darkgray')),
        size=alt.value(80)
    ).properties(
        width=750,
        height=400,
    ).add_selection(
        brush
    ).transform_filter(
        click
    )

    lines = alt.Chart(source2).mark_circle().encode(
        alt.Tooltip(["YEAR:O", "MONTH:O", "sum(RECORDS):Q", "sum(INJURIES):Q"]),
        alt.X('MONTH:O',title="Month",
              axis=alt.Axis(
                  offset=10,
                  ticks=True,
                  labelAngle=0,
                  minExtent=30,
                  grid=False
              )),
        alt.Y("sum(INJURIES):Q",
              title="Injuries",
              axis=alt.Axis(
                  offset=10,
                  ticks=True,
                  minExtent=30,
                  grid=False,
              )), color=alt.condition(brush, color, alt.value('red')),
        size= alt.value(80)
    ).transform_filter(
        brush
    ).properties(
        width=750,
    ).add_selection(
        click
    )
    vega = alt.vconcat(
        points,
        lines,
        title="Cases VS Injuries"
    )
    return vega


if __name__ == '__main__':
    st.title(" Welcome to Drive Safe in Chicago")
    st.text("When you are on the road, drive safe is the priority." 
            "\nHowever, traffic law violations and traffic accidents are happening all the time."
            "\nHere, you can get the locations of traffic cameras and the basic statistic of "
            "red light \nviolations, speed violations and car crash cases in Chicago from 2015 to April 2021."
            "\nNot only for displaying numbers, but also for alarming you to beware of the danger" 
            "\nand letting you be aware of the importance to obey traffic rules.\n"
            "Drive Safely and Carefullly!\n")
    st.write("(The data are from [Chicago Data Portal](https://data.cityofchicago.org/))")
    st.header(" The Location of Traffic Cameras")
    st.text("Choose what you want to do by the check box.\nMove the map by your mouse and click the markers to view the locations of traffic cameras.")
    rl = doc(3)
    s = doc(4)
    st.sidebar.title("Want to find the locations of traffic cameras?")
    sc = st.sidebar.checkbox("Want to see the speed camera locations?", False)
    rlc = st.sidebar.checkbox("Want to see the red light camera locations?", False)
    if rlc and not sc:
        chi_m = icon_adder(rl, "red", "info-sign", rl["INTERSECTION"])
    elif sc and not rlc:
        chi_m = icon_adder(s, "blue", "glyphicon glyphicon-warning-sign", s["ADDRESS"])
    elif sc and rlc:
        chi_rl = icon_adder(rl, "red", "info-sign", rl["INTERSECTION"])
        chi_m = icon_adder_re(chi_rl, s, "blue", "glyphicon glyphicon-warning-sign", s["ADDRESS"])
    else:
        chi_m = chicago_map()
    folium_static(chi_m)
    st.header(" Car Crash Accidents in Chicago ")
    st.text("How many car crashes happened on each block? Select years by drop-down!\nNote: some records of car crashes would not be counted due to no address information.")
    year_pick()
    st.header("*Summary*")
    st.text("Damages and causes of car accidents by year.")
    st.write(summary())
    st.text("Choose an interval on the year bar and get the data!")
    st.write(summary_rl())
    st.header("Top 5 Causes of Car Crash Accidents")
    st.text("Select a type of causes and gain the summary!")
    st.write(stack_bar_chart())
    st.header("Crashes and Injuries in the same period")
    st.text("Try to brush on the \"Cases\" chart and click on the \"Injuries\" chart to find some trends!")
    st.write(int_vega())
    st.header("Violation Cases in Chicago Per Month")
    vio = vio_year()
    st.write(vio)
