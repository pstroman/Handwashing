import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="Mortality Rate by Clinic", layout="wide")

# Title
st.title("Mortality Rate by Clinic")

# Body text under title
st.write("A look into the work of Dr. Ingaz Semmelweis, surrounding his studies into handwashing - which later led to the discovery of germs.")

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

# Ensure numeric columns are correct
df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
df["births"] = pd.to_numeric(df["births"], errors="coerce")
df["deaths"] = pd.to_numeric(df["deaths"], errors="coerce")

# Drop bad rows if needed
df = df.dropna(subset=["year", "births", "deaths", "clinic"])

# Convert year back to standard int for charting
df["year"] = df["year"].astype(int)

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
        x=alt.X(
            "year:Q",
            title="Year",
            axis=alt.Axis(format="d", tickMinStep=1)
        ),
        y=alt.Y("mortality_rate_pct:Q", title="Mortality Rate (%)"),
        color=alt.Color("clinic:N", title="Clinic"),
        tooltip=[
            alt.Tooltip("year:Q", format="d", title="Year"),
            "clinic:N",
            alt.Tooltip("mortality_rate_pct:Q", format=".2f", title="Mortality Rate (%)")
        ]
    ).properties(
        width=900,
        height=450,
        title="Mortality Rate Percentage by Year"
    )

    # Bright orange vertical line at 1847
    handwashing_line = alt.Chart(pd.DataFrame({"year": [1847]})).mark_rule(
        color="orange",
        strokeWidth=3,
        strokeDash=[8, 4]
    ).encode(
        x=alt.X("year:Q")
    )

    # Label for the 1847 line
    handwashing_label = alt.Chart(pd.DataFrame({
        "year": [1847],
        "label": ["Handwashing Introduction"]
    })).mark_text(
        color="orange",
        align="left",
        dx=8,
        dy=-180,
        fontSize=13,
        fontWeight="bold"
    ).encode(
        x=alt.X("year:Q"),
        text="label:N"
    )

    final_chart = line_chart + handwashing_line + handwashing_label
    st.altair_chart(final_chart, use_container_width=True)
else:
    st.warning("No data available for the selected filters.")

# Text under graph
st.write("This graph shows the mortality rate of two similar clinics. The biggest difference being that clinic 1 is a full clinic that includes cadavers, where as clinic 2 focuses only on midwifery. As shown in the graph there is a dramatic drop in deaths in 1847 in clinic 1. This is due to the introduction of handwashing. Dr. Semmelweis discovered clinic 1 had more deaths and attributed it to the presence of cadavers, and a lack of cleanliness of hands when moving between cadavers and births. As you can see his introduction of handwashing decreased deaths in clinic 1, later attributed to the spread of germs.")

# Raw data table title
st.subheader("Raw Data")

# Show exact csv file data
raw_df = pd.read_csv("yearly_deaths_by_clinic-1.csv")
st.dataframe(raw_df, use_container_width=True)