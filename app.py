import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="MBGES Screening Tool",
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="auto"
)


# ---------------------------------------------------------
# Responsive design
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    /* Main application area */
    .block-container {
        max-width: 100%;
        padding-top: 1.5rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }

    /* Allow Streamlit columns to wrap */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap;
        gap: 1rem;
    }

    [data-testid="column"] {
        min-width: 210px;
        flex: 1 1 210px;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        width: 100%;
        overflow: visible;
        padding: 1rem;
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 10px;
        background-color: rgba(128, 128, 128, 0.05);
    }

    [data-testid="stMetricValue"] {
        font-size: clamp(1.25rem, 3vw, 2rem);
        white-space: normal;
        overflow-wrap: anywhere;
    }

    [data-testid="stMetricLabel"] {
        white-space: normal;
        overflow-wrap: anywhere;
    }

    /* Responsive headings */
    h1 {
        font-size: clamp(1.7rem, 4vw, 2.7rem) !important;
        line-height: 1.2 !important;
    }

    h2 {
        font-size: clamp(1.3rem, 3vw, 2rem) !important;
    }

    h3 {
        font-size: clamp(1.1rem, 2.5vw, 1.5rem) !important;
    }

    /* Responsive tables */
    [data-testid="stDataFrame"] {
        width: 100%;
        overflow-x: auto;
    }

    /* Small screens */
    @media screen and (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
            padding-right: 0.75rem;
            padding-left: 0.75rem;
            padding-bottom: 1rem;
        }

        [data-testid="stHorizontalBlock"] {
            gap: 0.5rem;
        }

        [data-testid="column"] {
            min-width: 100%;
            width: 100%;
            flex: 1 1 100%;
        }

        [data-testid="stMetric"] {
            padding: 0.75rem;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.4rem;
        }

        .stButton > button,
        .stDownloadButton > button {
            width: 100%;
        }
    }

    /* Very small screens */
    @media screen and (max-width: 480px) {
        .block-container {
            padding-right: 0.4rem;
            padding-left: 0.4rem;
        }

        [data-testid="stMetric"] {
            padding: 0.6rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------
@st.cache_data
def load_data():
    data = pd.read_csv("mbges_mine_data.csv")

    # Fill missing descriptive information
    data["Mine_Name"] = data["Mine_Name"].fillna(
        data["Mine_ID"].apply(lambda value: f"Unnamed Mine {value}")
    )

    data["Mine_Status"] = data["Mine_Status"].fillna("Unknown")
    data["Substatus"] = data["Substatus"].fillna("Unknown")
    data["Commodity"] = data["Commodity"].fillna("Not specified")
    data["Suitability_Class"] = data["Suitability_Class"].fillna(
        "Unknown"
    )

    # Ensure numeric columns are correctly formatted
    numeric_columns = [
        "Latitude",
        "Longitude",
        "TOPSIS_Score",
        "Rank"
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # Remove records without valid map coordinates
    data = data.dropna(
        subset=[
            "Latitude",
            "Longitude",
            "TOPSIS_Score"
        ]
    )

    return data


df = load_data()


# ---------------------------------------------------------
# Application title
# ---------------------------------------------------------
st.title(
    "Australian Mine-Based Geothermal Energy Screening Tool"
)

st.markdown(
    """
    This interactive GIS-based decision-support tool allows users to
    explore and screen Australian mine sites according to their
    potential suitability for mine-based geothermal energy development.
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

state_options = sorted(
    df["State"].dropna().unique().tolist()
)

selected_states = st.sidebar.multiselect(
    "State",
    options=state_options,
    default=state_options
)

status_options = sorted(
    df["Mine_Status"].dropna().unique().tolist()
)

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

commodity_options = sorted(
    df["Commodity"].dropna().unique().tolist()
)

selected_commodities = st.sidebar.multiselect(
    "Commodity",
    options=commodity_options,
    help="Leave this empty to include all commodities."
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

st.sidebar.markdown("---")

reset_message = st.sidebar.caption(
    "Clear a selection or refresh the page to reset the filters."
)


# ---------------------------------------------------------
# Apply filters
# ---------------------------------------------------------
filtered_df = df[
    df["State"].isin(selected_states)
    & df["Mine_Status"].isin(selected_statuses)
    & df["Suitability_Class"].isin(selected_suitability)
    & df["TOPSIS_Score"].between(
        score_range[0],
        score_range[1]
    )
].copy()

if selected_commodities:
    filtered_df = filtered_df[
        filtered_df["Commodity"].isin(selected_commodities)
    ]

if mine_search.strip():
    filtered_df = filtered_df[
        filtered_df["Mine_Name"].str.contains(
            mine_search.strip(),
            case=False,
            na=False,
            regex=False
        )
    ]


# ---------------------------------------------------------
# Check filtered results
# ---------------------------------------------------------
if filtered_df.empty:
    st.warning(
        "No mine sites match the selected filters. "
        "Please change or clear one or more filters."
    )

    st.stop()


# ---------------------------------------------------------
# Summary indicators
# ---------------------------------------------------------
st.subheader("Screening Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Mine Sites",
        value=f"{len(filtered_df):,}"
    )

with col2:
    suitable_count = (
        filtered_df["Suitability_Class"] == "Suitable"
    ).sum()

    st.metric(
        label="Suitable Mines",
        value=f"{suitable_count:,}"
    )

with col3:
    st.metric(
        label="Highest TOPSIS Score",
        value=f"{filtered_df['TOPSIS_Score'].max():.4f}"
    )

with col4:
    st.metric(
        label="States Represented",
        value=f"{filtered_df['State'].nunique():,}"
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
    height=620
)

map_figure.update_traces(
    marker={
        "size": 6,
        "opacity": 0.70
    }
)

map_figure.update_layout(
    autosize=True,
    margin={
        "r": 0,
        "t": 0,
        "l": 0,
        "b": 0
    },
    legend={
        "title": {
            "text": "Suitability Class"
        },
        "orientation": "h",
        "yanchor": "bottom",
        "y": 1.01,
        "xanchor": "left",
        "x": 0
    }
)

st.plotly_chart(
    map_figure,
    use_container_width=True,
    config={
        "responsive": True,
        "displayModeBar": True,
        "scrollZoom": True
    }
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
    },
    text="Number of Mines"
)

distribution_figure.update_traces(
    textposition="outside",
    cliponaxis=False
)

distribution_figure.update_layout(
    autosize=True,
    showlegend=False,
    xaxis_title="Suitability Class",
    yaxis_title="Number of Mine Sites",
    margin={
        "r": 10,
        "t": 30,
        "l": 10,
        "b": 10
    }
)

distribution_figure.update_xaxes(
    tickangle=-20,
    automargin=True
)

st.plotly_chart(
    distribution_figure,
    use_container_width=True,
    config={
        "responsive": True,
        "displayModeBar": False
    }
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
        by=[
            "Rank",
            "TOPSIS_Score"
        ],
        ascending=[
            True,
            False
        ]
    )
    .reset_index(drop=True)
)

st.caption(
    "The table shows the 100 highest-ranked mine sites matching "
    "the selected filters. Scroll horizontally on smaller screens."
)

st.dataframe(
    ranked_table.head(100),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Rank": st.column_config.NumberColumn(
            "Rank",
            format="%d",
            width="small"
        ),
        "Mine_ID": st.column_config.NumberColumn(
            "Mine ID",
            format="%d",
            width="small"
        ),
        "Mine_Name": st.column_config.TextColumn(
            "Mine Name",
            width="large"
        ),
        "Mine_Status": st.column_config.TextColumn(
            "Mine Status",
            width="medium"
        ),
        "TOPSIS_Score": st.column_config.NumberColumn(
            "TOPSIS Score",
            format="%.6f",
            width="medium"
        ),
        "Suitability_Class": st.column_config.TextColumn(
            "Suitability Class",
            width="medium"
        )
    }
)


# ---------------------------------------------------------
# Download filtered results
# ---------------------------------------------------------
download_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Filtered Mine Data",
    data=download_data,
    file_name="filtered_mbges_mines.csv",
    mime="text/csv",
    use_container_width=True
)


# ---------------------------------------------------------
# Methodology information
# ---------------------------------------------------------
with st.expander("About the methodology"):
    st.markdown(
        """
        Mine-site suitability was evaluated using 14 spatial criteria
        representing geothermal potential and mine-water characteristics,
        infrastructure availability, and proximity to potential end users.

        The Analytic Hierarchy Process (AHP) and CRiteria Importance
        Through Intercriteria Correlation (CRITIC) were used as subjective
        and objective weighting methods, respectively. TOPSIS was then
        applied to calculate the suitability score and rank of each mine.

        The mines were classified into four suitability categories:

        - Suitable
        - Moderately Suitable
        - Moderately Unsuitable
        - Unsuitable
        """
    )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")

st.caption(
    "MBGES Screening Tool | Interactive GIS-based preliminary "
    "assessment of Australian mine sites"
)
