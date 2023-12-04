"""
Author: Awang Mulya Nugrawan
Date: 04/12/2023
This is the app.py module.
Usage:
- Initiate all functions for streamlit dashboard
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

plt.style.use("dark_background")

# air quality dataset
air_quality_df = pd.read_csv("dataset/air_quality_df.csv")
air_quality_df.sort_values(by="datetime", inplace=True)
air_quality_df.reset_index(inplace=True)
air_quality_df["datetime"] = pd.to_datetime(air_quality_df["datetime"])

# Highest CO wanshouxigong station dataset
wanshouxigong_timeseries_df = pd.read_csv("dataset\HighestCO_timeseries_df.csv")
wanshouxigong_timeseries_df.sort_values(by="datetime", inplace=True)
wanshouxigong_timeseries_df.reset_index(inplace=True)
wanshouxigong_timeseries_df["datetime"] = pd.to_datetime(
    wanshouxigong_timeseries_df["datetime"]
)

# Highest NO2 wanliu station dataset
wanliu_timeseries_df = pd.read_csv("dataset\HighestNO2_timeseries_df.csv")
wanliu_timeseries_df.sort_values(by="datetime", inplace=True)
wanliu_timeseries_df.reset_index(inplace=True)
wanliu_timeseries_df["datetime"] = pd.to_datetime(wanliu_timeseries_df["datetime"])


def calculate_mean_df(df, parameter):
    columns = [col for col in df.columns if col.startswith(f"{parameter}_")]
    mean_df = df[columns].copy()
    mean_df = mean_df.describe().loc["mean"]
    mean_df = mean_df.reset_index()
    mean_df = mean_df.rename(columns={"index": "station", "mean": f"{parameter} mean"})
    mean_df["station"] = mean_df["station"].str.replace(
        f"{parameter}_", "", regex=False
    )
    return mean_df


def create_monthly_df(df, station_name):
    monthly_df = df.reset_index()
    monthly_df = monthly_df.resample(rule="M", on="datetime").agg(
        {"PM10": "mean", "PM2.5": "mean"}
    )
    monthly_df.index = monthly_df.index.strftime("%Y %B")
    monthly_df = monthly_df.reset_index()
    monthly_df["station"] = station_name

    return monthly_df


def create_station_df(df, station_name):
    station_df = df.resample(rule="D", on="datetime").agg(
        {"PM2.5": "mean", "PM10": "mean", "CO": "mean"}
    )
    station_df["station"] = station_name

    return station_df


# Mean average highest CO and NO2
mean_CO_df = calculate_mean_df(air_quality_df, "CO")
mean_NO2_df = calculate_mean_df(air_quality_df, "NO2")
result_df = pd.merge(mean_CO_df, mean_NO2_df, on="station")
sorted_mean_NO2_df = result_df.sort_values(by="NO2 mean", ascending=False)
sorted_mean_CO_df = result_df.sort_values(by="CO mean", ascending=False)

# Mean average PM 10 and PM 2.5
mean_PM25_df = calculate_mean_df(air_quality_df, "PM2.5")
mean_PM10_df = calculate_mean_df(air_quality_df, "PM10")
PM_df = pd.merge(mean_PM25_df, mean_PM10_df, on="station")
sorted_mean_PM25_df = PM_df.sort_values(by="PM2.5 mean", ascending=True)
sorted_mean_PM10_df = PM_df.sort_values(by="PM10 mean", ascending=True)


# set min dan max datetime
min_date = air_quality_df["datetime"].min()
max_date = air_quality_df["datetime"].max()

# sidebar
with st.sidebar:
    st.title("Air Quality Dashboard")
    st.divider()
    st.image("https://media.giphy.com/media/VgwSabQUnRyn1Dw6nS/giphy.gif")
    st.divider()
    # Mengambil start_date & end_date dari input
    start_date, end_date = st.date_input(
        label="Date Range",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )
    st.divider()
    st.caption("Copyright (C) Awang Nugrawan 2023")

air_quality_df = air_quality_df[
    (air_quality_df["datetime"] >= str(start_date))
    & (air_quality_df["datetime"] <= str(end_date))
]
wanshouxigong_timeseries_range_df = wanshouxigong_timeseries_df[
    (wanshouxigong_timeseries_df["datetime"] >= str(start_date))
    & (wanshouxigong_timeseries_df["datetime"] <= str(end_date))
]
wanliu_timeseries_range_df = wanliu_timeseries_df[
    (wanliu_timeseries_df["datetime"] >= str(start_date))
    & (wanliu_timeseries_df["datetime"] <= str(end_date))
]


wanshouxigong_monthly_df = create_monthly_df(
    wanshouxigong_timeseries_df, "Wanshouxigong"
)
wanshouxigong_df = create_station_df(wanshouxigong_timeseries_range_df, "Wanshouxigong")
wanliu_monthly_df = create_monthly_df(wanliu_timeseries_df, "Wanliu")
wanliu_df = create_station_df(wanliu_timeseries_range_df, "Wanliu")


# header dashboard
header_text = """
# 🌍 Air Quality Dashboard
## Visualization of Air Quality at The 12 Station
"""

# Menampilkan header yang telah dibuat
st.markdown(header_text)

# Bar Chart Rata-Rata Karbon Monoksida (CO) Tertinggi dan Terendah pada Stasiun
st.divider()
st.subheader(
    "Highest Average Carbon Monoxide (CO) and Nitrogen Dioxide (NO2) at the Station"
)
col1, col2 = st.columns(2)
with col1:
    maxCO_station = sorted_mean_CO_df.iat[0, 0]
    st.metric(
        "Highest CO", value=maxCO_station, help="Station with the highest CO levels"
    )
with col2:
    maxNO2_station = sorted_mean_NO2_df.iat[0, 0]
    st.metric(
        "Highest NO2", value=maxNO2_station, help="Station with the highest NO2 levels"
    )
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(60, 30))
sns.barplot(
    x="CO mean",
    y="station",
    data=sorted_mean_CO_df.head(),
    palette=["b", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"],
    ax=ax[0],
)
ax[0].set_ylabel("Station", fontsize=30)
ax[0].set_xlabel("Average Carbon Monoxide (CO)", fontsize=30)
ax[0].set_title("Highest Average Carbon Monoxide (CO)", fontsize=50)
ax[0].tick_params(axis="y", labelsize=30)
ax[0].tick_params(axis="x", labelsize=30)
sns.barplot(
    x="CO mean",
    y="station",
    data=sorted_mean_NO2_df.head(),
    palette=["r", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"],
    ax=ax[1],
)
ax[1].set_ylabel("Station", fontsize=30)
ax[1].set_xlabel("Average Nitrogen Dioxide (NO2)", fontsize=30)
ax[1].set_title("Highest Average Nitrogen Dioxide (NO2)", fontsize=50)
ax[1].tick_params(axis="y", labelsize=30)
ax[1].tick_params(axis="x", labelsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
st.pyplot(fig)

with st.expander("See Explanation"):
    st.write(
        "Based on the results of data visualization using a bar chart, it is known that the station with the highest average pollution level of Carbon Monoxide (CO) is Wanshouxigong with an average value of 1373.6. While the station with the highest average pollution level of Nitrogen dioxide (NO2) is Wanliu station with an average value of 65.6."
    )


# Display PM2.5 and PM 10 metrics
st.divider()
st.subheader(
    "Average Monthly PM 2.5 and 10 at Station with the Highest CO and NO2 Levels Last 12 Months"
)
(
    tab1,
    tab2,
) = st.tabs(["CO", "NO2"])

with tab1:
    last_1_year = wanshouxigong_monthly_df.tail(12)
    sorted_last_1_year = last_1_year.sort_values(by="PM2.5")

    # Display metrics for PM2.5
    col1, col2 = st.columns(2)
    with col1:
        max_PM2 = round(sorted_last_1_year["PM2.5"].max(), 3)
        mon_max_PM2 = sorted_last_1_year.loc[sorted_last_1_year["PM2.5"].idxmax()][
            "datetime"
        ]
        st.metric("Highest PM2.5", value=max_PM2, help=f"At {mon_max_PM2}")

    with col2:
        min_PM2 = round(sorted_last_1_year["PM2.5"].min(), 3)
        mon_min_PM2 = sorted_last_1_year.loc[sorted_last_1_year["PM2.5"].idxmin()][
            "datetime"
        ]
        st.metric("Lowest PM2.5", value=min_PM2, help=f"At {mon_min_PM2}")

    # Display metrics for PM10
    col3, col4 = st.columns(2)
    with col3:
        max_PM10 = round(sorted_last_1_year["PM10"].max(), 3)
        mon_max_PM10 = sorted_last_1_year.loc[sorted_last_1_year["PM10"].idxmax()][
            "datetime"
        ]
        st.metric("Highest PM10", value=max_PM10, help=f"At {mon_max_PM10}")

    with col4:
        min_PM10 = round(sorted_last_1_year["PM10"].min(), 3)
        mon_min_PM10 = sorted_last_1_year.loc[sorted_last_1_year["PM10"].idxmin()][
            "datetime"
        ]
        st.metric("Lowest PM10", value=min_PM10, help=f"At {mon_min_PM10}")

    # Plotting Line Chart
    fig, ax = plt.subplots(figsize=(16, 8))

    ax.plot(
        last_1_year["datetime"],
        last_1_year["PM2.5"],
        marker="o",
        linewidth=2,
        color="r",
        label="PM2.5",
    )
    ax.plot(
        last_1_year["datetime"],
        last_1_year["PM10"],
        marker="o",
        linewidth=2,
        color="b",
        label="PM10",
    )

    ax.set_title(
        "Average Monthly PM 2.5 and PM 10 at Wanshouxigong Station (Last 12 Months)"
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("PM Level")
    ax.tick_params(axis="y", labelsize=11)
    ax.tick_params(axis="x", labelsize=11, rotation=45)
    ax.grid(True, linestyle="--", linewidth=0.5, which="both", color="gray")
    ax.legend()

    st.pyplot(fig)

    with st.expander("See Explanation"):
        st.write(
            "The station with the highest level of CO pollution is Wanshouxigong station. From the results of data visualization using the line chart, it is known that the data for the last 1 year on PM 10 and PM 2.5 levels tend to fluctuate. The lowest levels occurred in August 2016 and peaked in December 2016. The increase in PM 10 and PM 2.5 levels occurred from August to December 2016. However, it decreased again in January-February 2017."
        )
with tab2:
    last_1_year = wanliu_monthly_df.tail(12)
    sorted_last_1_year = last_1_year.sort_values(by="PM2.5")

    # Display metrics for PM2.5
    col1, col2 = st.columns(2)
    with col1:
        max_PM2 = round(sorted_last_1_year["PM2.5"].max(), 3)
        mon_max_PM2 = sorted_last_1_year.loc[sorted_last_1_year["PM2.5"].idxmax()][
            "datetime"
        ]
        st.metric("Highest PM2.5", value=max_PM2, help=f"At {mon_max_PM2}")

    with col2:
        min_PM2 = round(sorted_last_1_year["PM2.5"].min(), 3)
        mon_min_PM2 = sorted_last_1_year.loc[sorted_last_1_year["PM2.5"].idxmin()][
            "datetime"
        ]
        st.metric("Lowest PM2.5", value=min_PM2, help=f"At {mon_min_PM2}")

    # Display metrics for PM10
    col3, col4 = st.columns(2)
    with col3:
        max_PM10 = round(sorted_last_1_year["PM10"].max(), 3)
        mon_max_PM10 = sorted_last_1_year.loc[sorted_last_1_year["PM10"].idxmax()][
            "datetime"
        ]
        st.metric("Highest PM10", value=max_PM10, help=f"At {mon_max_PM10}")

    with col4:
        min_PM10 = round(sorted_last_1_year["PM10"].min(), 3)
        mon_min_PM10 = sorted_last_1_year.loc[sorted_last_1_year["PM10"].idxmin()][
            "datetime"
        ]
        st.metric("Lowest PM10", value=min_PM10, help=f"At {mon_min_PM10}")

    # Plotting Line Chart
    fig, ax = plt.subplots(figsize=(16, 8))

    ax.plot(
        last_1_year["datetime"],
        last_1_year["PM2.5"],
        marker="o",
        linewidth=2,
        color="r",
        label="PM2.5",
    )
    ax.plot(
        last_1_year["datetime"],
        last_1_year["PM10"],
        marker="o",
        linewidth=2,
        color="b",
        label="PM10",
    )

    ax.set_title("Average Monthly PM 2.5 and PM 10 at Wanliu Station (Last 12 Months)")
    ax.set_xlabel("Date")
    ax.set_ylabel("PM Level")
    ax.tick_params(axis="y", labelsize=11)
    ax.tick_params(axis="x", labelsize=11, rotation=45)
    ax.grid(True, linestyle="--", linewidth=0.5, which="both", color="gray")
    ax.legend()

    st.pyplot(fig)

    with st.expander("See Explanation"):
        st.write(
            "The station that has the highest NO2 pollution level is Wanliu station. Based on the results of data visualization using line charts, it is known that the data for the last 1 year on PM 10 and PM 2.5 levels tend to fluctuate. The increase in PM 10 and PM 2.5 levels occurred from August-December 2016. However, it decreased again in January-February 2017. The lowest level occurred in August 2016 and the peak in December 2016."
        )


st.divider()
st.subheader("Order of Average Particulate Matter PerStation (Low to High)")
(
    tab1,
    tab2,
) = st.tabs(["PM 2.5", "PM 10"])

with tab1:
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(7, 7))
    sns.barplot(x="PM2.5 mean", y="station", data=sorted_mean_PM25_df)
    ax.set_ylabel("Station", fontsize=13)
    ax.set_xlabel("Average PM 2.5", fontsize=13)
    ax.set_title("Order of Average PM 2.5 Per Station (Low to High)", fontsize=15)
    ax.tick_params(axis="y", labelsize=11)
    ax.tick_params(axis="x", labelsize=11)
    st.pyplot(fig)


with tab2:
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(7, 7))
    sns.barplot(x="PM10 mean", y="station", data=sorted_mean_PM10_df)
    ax.set_ylabel("Station", fontsize=13)
    ax.set_xlabel("Average PM10", fontsize=13)
    ax.set_title("Order of Average PM10 Per Station (Low to High)", fontsize=15)
    ax.tick_params(axis="y", labelsize=11)
    ax.tick_params(axis="x", labelsize=11)
    st.pyplot(fig)
