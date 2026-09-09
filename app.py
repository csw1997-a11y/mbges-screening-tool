import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="MBGES Screening Tool",
    page_icon="🌏",
    layout="wide"
)


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------
@st.cache_data
def load_data():
    data = pd.read_csv("mbges_mine_data.csv")

    data["Mine_Name"] = data["Mine_Name"].fillna("Unnamed Mine")
    data["Mine_Status"] = data["Mine_Status"].fillna("Unknown")
    data["Substatus"] = data["Substatus"].fillna("Unknown")
    data["Commodity"] = data["Commodity"].fillna("Not specified")
    data["Suitability_Class"] = data["Suitability_Class"].fillna("Unknown")

    return data


df = load_data()


# ---------------------------------------------------------
# Application title
# ---------------------------------------------------------
st.title("Australian Mine-Based Geothermal Energy Screening Tool")

st.markdown(
    """
    This interactive GIS-based decision-support tool allows users to explore
    and screen Australian mine sites according to their potential suitability
    for mine-based geothermal energy development.
    """
)


# ---------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------
st.sidebar.header("Mine Screening Filters")

mine_search = st.sidebar.text_input(
    "Search by mine name",
    placeholder="Enter a mine name"
)

state_options = sorted(df["State"].dropna().unique())

selected_states = st.sidebar.multiselect(
    "State",
    options=state_options,
    default=state_options
)

status_options = sorted(df["Mine_Status"].dropna().unique())

selected_statuses = st.sidebar.multiselect(
    "Mine status",
    options=status_options,
    default=status_options
)

suitability_order = [
    "Suitable",
    "Moderately Suitable",
    "Moderately Unsuitable",
    "Unsuitable"
]

available_suitability = [
    category
    for category in suitability_order
    if category in df["Suitability_Class"].unique()
]

selected_suitability = st.sidebar.multiselect(
    "Suitability class",
    options=available_suitability,
    default=available_suitability
)

commodity_options = sorted(df["Commodity"].dropna().unique())

selected_commodities = st.sidebar.multiselect(
    "Commodity",
    options=commodity_options,
    help="Leave empty to include all commodities."
)

minimum_score = float(df["TOPSIS_Score"].min())
maximum_score = float(df["TOPSIS_Score"].max())

score_range = st.sidebar.slider(
    "TOPSIS score range",
    min_value=minimum_score,
    max_value=maximum_score,
    value=(minimum_score, maximum_score),
    step=0.001,
    format="%.3f"
)


# ---------------------------------------------------------
# Apply filters
# ---------------------------------------------------------
filtered_df = df[
    df["State"].isin(selected_states)
    & df["Mine_Status"].isin(selected_statuses)
    & df["Suitability_Class"].isin(selected_suitability)
    & df["TOPSIS_Score"].between(score_range[0], score_range[1])
].copy()

if selected_commodities:
    filtered_df = filtered_df[
        filtered_df["Commodity"].isin(selected_commodities)
    ]

if mine_search:
    filtered_df = filtered_df[
        filtered_df["Mine_Name"].str.contains(
            mine_search,
            case=False,
            na=False
        )
    ]


# ---------------------------------------------------------
# Summary indicators
# ---------------------------------------------------------
st.subheader("Screening Summary")

if filtered_df.empty:
    st.warning("No mine sites match the selected filters.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Mine Sites",
    f"{len(filtered_df):,}"
)

col2.metric(
    "Suitable Mines",
    f"{(filtered_df['Suitability_Class'] == 'Suitable').sum():,}"
)

col3.metric(
    "Highest TOPSIS Score",
    f"{filtered_df['TOPSIS_Score'].max():.4f}"
)

col4.metric(
    "States Represented",
    filtered_df["State"].nunique()
)


# ---------------------------------------------------------
# Interactive map
# ---------------------------------------------------------
st.subheader("Interactive Mine Suitability Map")

suitability_colours = {
    "Suitable": "#1a9850",
    "Moderately Suitable": "#91cf60",
    "Moderately Unsuitable": "#fdae61",
    "Unsuitable": "#d73027"
}

map_figure = px.scatter_map(
    filtered_df,
    lat="Latitude",
    lon="Longitude",
    color="Suitability_Class",
    color_discrete_map=suitability_colours,
    category_orders={
        "Suitability_Class": suitability_order
    },
    hover_name="Mine_Name",
    hover_data={
        "Mine_ID": True,
        "State": True,
        "Mine_Status": True,
        "Substatus": True,
        "Commodity": True,
        "TOPSIS_Score": ":.6f",
        "Rank": True,
        "Latitude": ":.4f",
        "Longitude": ":.4f",
        "Suitability_Class": False
    },
    map_style="open-street-map",
    center={
        "lat": -25.5,
        "lon": 134.0
    },
    zoom=3,
    height=650
)
map_figure.update_traces(
    marker={
        "size": 6,
        "opacity": 0.70
    }
)

map_figure.update_layout(
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    legend_title_text="Suitability"
)

st.plotly_chart(
    map_figure,
    use_container_width=True
)


# ---------------------------------------------------------
# Suitability distribution
# ---------------------------------------------------------
st.subheader("Suitability Distribution")

distribution = (
    filtered_df["Suitability_Class"]
    .value_counts()
    .reindex(suitability_order, fill_value=0)
    .reset_index()
)

distribution.columns = [
    "Suitability Class",
    "Number of Mines"
]

distribution_figure = px.bar(
    distribution,
    x="Suitability Class",
    y="Number of Mines",
    color="Suitability Class",
    color_discrete_map=suitability_colours,
    category_orders={
        "Suitability Class": suitability_order
    }
)

distribution_figure.update_layout(
    showlegend=False,
    xaxis_title="Suitability Class",
    yaxis_title="Number of Mine Sites"
)

st.plotly_chart(
    distribution_figure,
    use_container_width=True
)


# ---------------------------------------------------------
# Ranked mine table
# ---------------------------------------------------------
st.subheader("Highest-Ranked Mine Sites")

table_columns = [
    "Rank",
    "Mine_ID",
    "Mine_Name",
    "State",
    "Mine_Status",
    "Substatus",
    "Commodity",
    "TOPSIS_Score",
    "Suitability_Class"
]

ranked_table = (
    filtered_df[table_columns]
    .sort_values(
        by=["Rank", "TOPSIS_Score"],
        ascending=[True, False]
    )
    .reset_index(drop=True)
)

st.dataframe(
    ranked_table.head(100),
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# Download filtered results
# ---------------------------------------------------------
download_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Mine Data",
    data=download_data,
    file_name="filtered_mbges_mines.csv",
    mime="text/csv"
)


# ---------------------------------------------------------
# Methodology information
# ---------------------------------------------------------
with st.expander("About the methodology"):
    st.markdown(
        """
        Mine-site suitability was evaluated using 14 spatial criteria
        representing geothermal potential, mine-water characteristics,
        infrastructure availability and end-user demand.

        AHP and CRITIC were used to represent subjective and objective
        weighting approaches. The integrated criteria weights were subsequently
        incorporated into TOPSIS to calculate the suitability score and rank
        of each mine site.
        """
    )
