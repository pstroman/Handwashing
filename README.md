import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="Mortality Rate by Clinic", layout="wide")

# Title
st.title("Mortality Rate by Clinic")

# Body text under title
st.write("Handwashing began in 1847.")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("yearly_deaths_by_clinic-1.csv")
    return df

df = load_data()

# Make column names easier to work with
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# Rename columns if needed to standard names
column_map = {}
for col in df.columns:
    if "year" in col:
        column_map[col] = "year"
    elif "clinic" in col:
        column_map[col] = "clinic"
    elif "birth" in col:
        column_map[col] = "births"
    elif "death" in col:
        column_map[col] = "deaths"

df = df.rename(columns=column_map)

# Create mortality rate percentage
df["mortality_rate_pct"] = (df["deaths"] / df["births"]) * 100

# Sidebar filters
st.sidebar.header("Filters")

clinic_options = sorted(df["clinic"].dropna().unique().tolist())
selected_clinics = st.sidebar.multiselect(
    "Select Clinic(s)",
    options=clinic_options,
    default=clinic_options
)

min_year = int(df["year"].min())
max_year = int(df["year"].max())

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Filter data
filtered_df = df[
    (df["clinic"].isin(selected_clinics)) &
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
]

# Graph
if not filtered_df.empty:
    line_chart = alt.Chart(filtered_df).mark_line(point=True).encode(
        x=alt.X("year:Q", title="Year"),
        y=alt.Y("mortality_rate_pct:Q", title="Mortality Rate (%)"),
        color=alt.Color("clinic:N", title="Clinic"),
        tooltip=["year", "clinic", alt.Tooltip("mortality_rate_pct:Q", format=".2f")]
    ).properties(
        width=900,
        height=450,
        title="Mortality Rate Percentage by Year"
    )

    handwashing_line = alt.Chart(pd.DataFrame({"year": [1847]})).mark_rule(
        strokeDash=[8, 4],
        size=2
    ).encode(
        x="year:Q"
    )

    handwashing_label = alt.Chart(pd.DataFrame({
        "year": [1847],
        "label": ["Handwashing began (1847)"]
    })).mark_text(
        align="left",
        dx=5,
        dy=-200
    ).encode(
        x="year:Q",
        text="label:N"
    )

    final_chart = line_chart + handwashing_line + handwashing_label
    st.altair_chart(final_chart, use_container_width=True)
else:
    st.warning("No data available for the selected filters.")

# Text under graph
st.write("This shows clinic 1 and 2.")

# Raw data table title
st.subheader("Raw Data")

# Show exact csv file data
raw_df = pd.read_csv("yearly_deaths_by_clinic-1.csv")
st.dataframe(raw_df, use_container_width=True)
