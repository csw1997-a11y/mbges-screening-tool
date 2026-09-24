# ================================================================
# MINE-BASED GEOTHERMAL SCREENING TOOL
# Complete Streamlit Application
# ================================================================

import os
import glob
import json
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# ================================================================
# 1. PAGE SETTINGS
# ================================================================

st.set_page_config(
    page_title="Mine-Based Geothermal Screening Tool",
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="auto",
)


# ================================================================
# 2. CUSTOM PAGE STYLE
# ================================================================

st.markdown(
    """
<style>
.block-container {
    max-width: 100%;
    padding-top: 1.2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    padding-bottom: 2.5rem;
}

/* Allow dashboard columns to wrap instead of overflowing. */
[data-testid="stHorizontalBlock"] {
    flex-wrap: wrap;
    gap: 1rem;
}

[data-testid="column"] {
    min-width: 210px;
    flex: 1 1 210px;
}

[data-testid="stSidebar"] {
    background-color: #f5f7fa;
    border-right: 1px solid #e5e7eb;
}

[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #e4e9ef;
    border-radius: 14px;
    padding: 15px 18px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

[data-testid="stMetricLabel"] {
    font-weight: 600;
    white-space: normal;
    overflow-wrap: anywhere;
}

[data-testid="stMetricValue"] {
    font-size: clamp(1.25rem, 3vw, 2rem);
    white-space: normal;
    overflow-wrap: anywhere;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 15px;
}

.hero {
    background: linear-gradient(115deg, #0b3048 0%, #126782 100%);
    padding: 25px 30px;
    border-radius: 18px;
    margin-bottom: 22px;
    box-shadow: 0 5px 16px rgba(0,0,0,0.08);
}

.hero-title {
    color: white;
    font-size: clamp(1.55rem, 4vw, 2.15rem);
    font-weight: 700;
    margin: 0;
    line-height: 1.2;
    overflow-wrap: anywhere;
}

.hero-subtitle {
    color: rgba(255,255,255,0.90);
    font-size: 1rem;
    margin-top: 7px;
    margin-bottom: 0;
}

.section-description {
    color: #677382;
    margin-top: -8px;
    margin-bottom: 15px;
}

.small-note {
    color: #6b7280;
    font-size: 0.86rem;
}

/* Keep charts and tables inside the available screen width. */
[data-testid="stPlotlyChart"],
[data-testid="stDataFrame"] {
    width: 100%;
    max-width: 100%;
    overflow-x: auto;
}

@media screen and (max-width: 768px) {
    .block-container {
        padding-top: 0.8rem;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
        padding-bottom: 1.25rem;
    }

    [data-testid="stHorizontalBlock"] {
        gap: 0.6rem;
    }

    [data-testid="column"] {
        min-width: 100%;
        width: 100%;
        flex: 1 1 100%;
    }

    [data-testid="stMetric"] {
        padding: 0.75rem 0.9rem;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.4rem;
    }

    .hero {
        padding: 18px 16px;
        border-radius: 13px;
        margin-bottom: 16px;
    }

    .hero-subtitle {
        font-size: 0.92rem;
        line-height: 1.45;
    }

    .section-description {
        margin-top: -4px;
        line-height: 1.45;
    }

    .stButton > button,
    .stDownloadButton > button {
        width: 100%;
    }
}

@media screen and (max-width: 480px) {
    .block-container {
        padding-left: 0.4rem;
        padding-right: 0.4rem;
    }

    .hero {
        padding: 16px 13px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# ================================================================
# 3. DATA FILE
# ================================================================
#
# If you know the exact file name, put it here.
#
# Example:
#
# DATA_FILE = "Sensitivity Analysis - Copy.xlsx"
#
# If DATA_FILE = None, the application will automatically search
# the repository for a CSV or Excel file.
# ================================================================

DATA_FILE = None


def find_data_file():

    if DATA_FILE is not None and os.path.exists(DATA_FILE):
        return DATA_FILE

    candidate_files = []

    for pattern in ["*.csv", "*.xlsx", "*.xls"]:
        candidate_files.extend(glob.glob(pattern))

    # Ignore temporary Excel files
    candidate_files = [
        f for f in candidate_files
        if not os.path.basename(f).startswith("~$")
    ]

    if len(candidate_files) == 0:
        return None

    # Prefer CSV when available
    csv_files = [
        f for f in candidate_files
        if f.lower().endswith(".csv")
    ]

    if csv_files:
        return csv_files[0]

    return candidate_files[0]


selected_file = find_data_file()


if selected_file is None:

    st.error(
        "No CSV or Excel dataset was found in the application folder."
    )

    st.info(
        "Upload your mine dataset to the GitHub repository, "
        "or specify its filename in DATA_FILE."
    )

    st.stop()


# ================================================================
# 4. LOAD DATA
# ================================================================

@st.cache_data
def load_data(file_path):

    if file_path.lower().endswith(".csv"):
        return pd.read_csv(file_path)

    if file_path.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(file_path)

    raise ValueError("Unsupported data format.")


try:
    df = load_data(selected_file)

except Exception as error:

    st.error(
        f"Unable to load the dataset: {error}"
    )

    st.stop()

# ================================================================
# MINE LEASE BOUNDARY LAYER
# ================================================================

LEASE_BOUNDARY_FILE = "data/mine_lease_boundaries.geojson"


@st.cache_data
def load_geojson(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


lease_boundary_available = os.path.exists(
    LEASE_BOUNDARY_FILE
)
# ================================================================
# 5. AUTOMATIC COLUMN IDENTIFICATION
# ================================================================

def find_column(dataframe, possible_names):

    lower_lookup = {
        str(col).strip().lower(): col
        for col in dataframe.columns
    }

    # Exact case-insensitive match
    for name in possible_names:

        key = name.strip().lower()

        if key in lower_lookup:
            return lower_lookup[key]

    # Simplified match
    simplified_lookup = {
        str(col)
        .strip()
        .lower()
        .replace("_", "")
        .replace(" ", "")
        .replace("-", ""): col

        for col in dataframe.columns
    }

    for name in possible_names:

        simplified_name = (
            name.strip()
            .lower()
            .replace("_", "")
            .replace(" ", "")
            .replace("-", "")
        )

        if simplified_name in simplified_lookup:
            return simplified_lookup[simplified_name]

    return None


MINE_NAME = find_column(
    df,
    [
        "Mine_Name",
        "Mine Name",
        "NAME",
        "MINE_NAME",
        "Mine",
        "SITE_NAME",
        "Site Name",
    ],
)

LATITUDE = find_column(
    df,
    [
        "Latitude",
        "LATITUDE",
        "LAT",
        "Y",
        "latitude",
    ],
)

LONGITUDE = find_column(
    df,
    [
        "Longitude",
        "LONGITUDE",
        "LON",
        "LONG",
        "X",
        "longitude",
    ],
)

STATE = find_column(
    df,
    [
        "State",
        "STATE",
        "State_Name",
        "STATE_NAME",
    ],
)

STATUS = find_column(
    df,
    [
        "Mine_Status",
        "Mine Status",
        "STATUS",
        "Status",
        "MINESTATUS",
    ],
)

COMMODITY = find_column(
    df,
    [
        "Commodity",
        "COMMODITY",
        "Commodity_Name",
        "COMMODITIES",
        "Commodities",
    ],
)

TOPSIS = find_column(
    df,
    [
        "TOPSIS_Score",
        "TOPSIS Score",
        "TOPSIS",
        "Ci",
        "CI",
        "C_i",
        "Closeness Coefficient",
        "Closeness_Coefficient",
    ],
)

SUITABILITY = find_column(
    df,
    [
        "Suitability",
        "SUITABILITY",
        "Suitability_Class",
        "Suitability Class",
        "CLASS",
    ],
)

RANK = find_column(
    df,
    [
        "Rank",
        "RANK",
        "TOPSIS_Rank",
        "TOPSIS Rank",
    ],
)

# ================================================================
# PROXIMITY COLUMNS
# ================================================================

PROXIMITY_COLUMNS = {
    "Major Roads": "C5_Roads",
    "Railway Lines": "C6_Railways",
    "Electricity Transmission Lines": "C7_Powerlines",
    "Ports": "C8_Ports",
    "Health Facilities": "C9_Health",
    "Manufacturing Facilities": "C10_Manufacturing",
    "Agriculture and Farming": "C11_Agriculture",
    "Educational Centres": "C12_Education",
    "Data Centres": "C13_Data_Centres",
    "Built-up Areas": "C14_Built_Up",
}

# Remove criteria that were not found in the dataset
PROXIMITY_COLUMNS = {
    label: column
    for label, column in PROXIMITY_COLUMNS.items()
    if column in df.columns
}
# ================================================================
# 6. VERIFY ESSENTIAL COLUMNS
# ================================================================

essential_columns = {
    "Mine name": MINE_NAME,
    "Latitude": LATITUDE,
    "Longitude": LONGITUDE,
    "State": STATE,
    "Mine status": STATUS,
    "TOPSIS score": TOPSIS,
}


missing = [
    label
    for label, column in essential_columns.items()
    if column is None
]


if missing:

    st.error(
        "The application could not identify these required fields:"
    )

    st.write(missing)

    st.write("Columns currently available in your dataset:")

    st.code(
        "\n".join(
            [str(column) for column in df.columns]
        )
    )

    st.stop()


# ================================================================
# 7. CLEAN DATA
# ================================================================

df[LATITUDE] = pd.to_numeric(
    df[LATITUDE],
    errors="coerce",
)

df[LONGITUDE] = pd.to_numeric(
    df[LONGITUDE],
    errors="coerce",
)

df[TOPSIS] = pd.to_numeric(
    df[TOPSIS],
    errors="coerce",
)


df = df.dropna(
    subset=[
        LATITUDE,
        LONGITUDE,
        TOPSIS,
    ]
).copy()


# Remove impossible coordinates
df = df[
    df[LATITUDE].between(-90, 90)
    &
    df[LONGITUDE].between(-180, 180)
].copy()


# Generate unique internal identifier
df["_APP_ROW_ID"] = np.arange(
    len(df)
)


# ================================================================
# 8. TITLE
# ================================================================

# Kept on one line to prevent Markdown interpreting HTML as code.

st.markdown(
    "<div class='hero'><div class='hero-title'>Mine-Based Geothermal Screening Tool</div><div class='hero-subtitle'>Interactive screening of Australian mine sites for mine-based geothermal energy opportunities</div></div>",
    unsafe_allow_html=True,
)


# ================================================================
# 9. SIDEBAR
# ================================================================

st.sidebar.header(
    "Mine Screening Filters"
)


# ------------------------------------------------
# Search
# ------------------------------------------------

mine_search = st.sidebar.text_input(
    "Search by mine name",
    placeholder="Enter a mine name",
)


# ------------------------------------------------
# State
# ------------------------------------------------

state_options = sorted(
    df[STATE]
    .dropna()
    .astype(str)
    .unique()
)


selected_states = st.sidebar.multiselect(
    "State",
    options=state_options,
    default=state_options,
)


# ------------------------------------------------
# Mine status
# ------------------------------------------------

status_options = sorted(
    df[STATUS]
    .dropna()
    .astype(str)
    .unique()
)


selected_status = st.sidebar.multiselect(
    "Mine status",
    options=status_options,
    default=status_options,
)


# ------------------------------------------------
# Commodity
# ------------------------------------------------

selected_commodities = []


if COMMODITY is not None:

    commodity_options = sorted(
        df[COMMODITY]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_commodities = st.sidebar.multiselect(
        "Commodity",
        options=commodity_options,
        placeholder="Choose options",
    )


# ------------------------------------------------
# TOPSIS score
# ------------------------------------------------

minimum_score = float(
    df[TOPSIS].min()
)

maximum_score = float(
    df[TOPSIS].max()
)


selected_score = st.sidebar.slider(
    "TOPSIS score range",
    min_value=minimum_score,
    max_value=maximum_score,
    value=(
        minimum_score,
        maximum_score,
    ),
    step=0.001,
    format="%.3f",
)


st.sidebar.markdown("---")

st.sidebar.caption(
    "Adjust the filters to explore mine locations "
    "and their screening results."
)


# ================================================================
# 10. FILTER DATA
# ================================================================

filtered_df = df.copy()


if mine_search.strip():

    filtered_df = filtered_df[
        filtered_df[MINE_NAME]
        .astype(str)
        .str.contains(
            mine_search.strip(),
            case=False,
            na=False,
        )
    ]


if selected_states:

    filtered_df = filtered_df[
        filtered_df[STATE]
        .astype(str)
        .isin(selected_states)
    ]


if selected_status:

    filtered_df = filtered_df[
        filtered_df[STATUS]
        .astype(str)
        .isin(selected_status)
    ]


if (
    COMMODITY is not None
    and selected_commodities
):

    filtered_df = filtered_df[
        filtered_df[COMMODITY]
        .astype(str)
        .isin(selected_commodities)
    ]


filtered_df = filtered_df[
    filtered_df[TOPSIS].between(
        selected_score[0],
        selected_score[1],
    )
]

st.sidebar.subheader("GIS Layers")

show_lease_boundaries = st.sidebar.checkbox(
    "Mine Lease Boundaries",
    value=False,
    disabled=not lease_boundary_available
)

if not lease_boundary_available:
    st.sidebar.caption(
        "Mine lease boundary file was not found."
    )
# ================================================================
# 11. SCREENING SUMMARY
# ================================================================

st.subheader(
    "Screening Summary"
)


metric1, metric2, metric3, metric4 = st.columns(
    4
)


# Mine sites
metric1.metric(
    "Mine Sites",
    f"{len(filtered_df):,}",
)


# States
metric2.metric(
    "States Represented",
    f"{filtered_df[STATE].nunique():,}",
)


# Highest TOPSIS
if len(filtered_df) > 0:

    metric3.metric(
        "Highest TOPSIS Score",
        f"{filtered_df[TOPSIS].max():.4f}",
    )

else:

    metric3.metric(
        "Highest TOPSIS Score",
        "-",
    )


# Inactive mines
inactive_count = 0

if len(filtered_df) > 0:

    inactive_count = (
        filtered_df[STATUS]
        .astype(str)
        .str.lower()
        .str.contains("inactive", na=False)
        .sum()
    )


metric4.metric(
    "Inactive Mines",
    f"{inactive_count:,}",
)


st.write("")


# ================================================================
# 12. MAP HEADING
# ================================================================

st.subheader(
    "Explore Australian Mine Sites"
)

st.markdown(
    "<div class='section-description'>Select a mine location on the map to explore its geothermal potential, infrastructure accessibility, end-user demand and screening characteristics.</div>",
    unsafe_allow_html=True,
)


# ================================================================
# 13. MAP + SELECTED MINE PANEL
# ================================================================

if filtered_df.empty:

    st.warning(
        "No mine sites match the selected filters."
    )

else:

    map_column, detail_column = st.columns(
        [2.75, 1.25],
        gap="large",
    )


    # ============================================================
    # MAP
    # ============================================================

    with map_column:

        map_center = {
            "lat": filtered_df[LATITUDE].mean(),
            "lon": filtered_df[LONGITUDE].mean(),
        }


        hover_data = {
            LATITUDE: False,
            LONGITUDE: False,
            TOPSIS: ":.4f",
            STATE: True,
            STATUS: True,
        }


        if COMMODITY is not None:
            hover_data[COMMODITY] = True
map_layers = []

if show_lease_boundaries:
    mine_lease_geojson = load_geojson(
        LEASE_BOUNDARY_FILE
    )

    map_layers.append(
        {
            "source": mine_lease_geojson,
            "type": "line",
            "color": "#ff7800",
            "line": {
                "width": 1.5
            },
            "opacity": 0.85
        }
    )

        fig = px.scatter_map(
            filtered_df,
            lat=LATITUDE,
            lon=LONGITUDE,
            hover_name=MINE_NAME,
            hover_data=hover_data,
            custom_data=[
                "_APP_ROW_ID"
            ],
            center=map_center,
            zoom=3.15,
            height=680,
            map_style="open-street-map",
        )


        # --------------------------------------------------------
        # ONE SYMBOL / ONE COLOUR FOR ALL MINES
        # --------------------------------------------------------

        fig.update_traces(
            marker=dict(
                size=7,
                color="#1f77d0",
                opacity=0.72,
            ),
            selected=dict(
                marker=dict(
                    size=12,
                    opacity=1,
                )
            ),
            unselected=dict(
                marker=dict(
                    opacity=0.45,
                )
            ),
        )


        fig.update_layout(
    map_layers=map_layers,
    margin=dict(
        l=0,
        r=0,
        t=0,
        b=0,
    ),
    showlegend=False,
))


        map_selection = st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "responsive": True,
                "displayModeBar": True,
                "scrollZoom": True,
            },
            on_select="rerun",
            selection_mode="points",
            key="mine_map",
        )


    # ============================================================
    # IDENTIFY CLICKED MINE
    # ============================================================

    selected_row_id = None


    try:

        points = map_selection.selection.points

        if points:

            selected_point = points[0]

            customdata = selected_point.get(
                "customdata"
            )

            if customdata is not None:

                if isinstance(
                    customdata,
                    (list, tuple),
                ):

                    selected_row_id = int(
                        customdata[0]
                    )

                else:

                    selected_row_id = int(
                        customdata
                    )


                st.session_state[
                    "selected_mine_row"
                ] = selected_row_id

    except Exception:
        pass


    # Keep selected mine after rerun
    if selected_row_id is None:

        selected_row_id = (
            st.session_state.get(
                "selected_mine_row"
            )
        )


    # ============================================================
    # SELECTED MINE DETAILS
    # ============================================================

    with detail_column:

        st.subheader(
            "Selected Mine"
        )

        if selected_row_id is None:

            with st.container(
                border=True
            ):

                st.info(
                    "Click a mine point on the map "
                    "to view its details."
                )

        else:

            selected_rows = filtered_df[
                filtered_df["_APP_ROW_ID"] == selected_row_id
            ]

            if selected_rows.empty:

                with st.container(
                    border=True
                ):

                    st.info(
                        "The previously selected mine "
                        "is outside the current filters."
                    )

            else:

                mine = selected_rows.iloc[0]

                # ------------------------------------------------
                # MAIN MINE INFORMATION
                # ------------------------------------------------

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### {mine[MINE_NAME]}"
                    )

                    info_left, info_right = st.columns(
                        2
                    )

                    with info_left:

                        st.caption(
                            "State"
                        )

                        st.markdown(
                            f"**{mine[STATE]}**"
                        )

                        st.caption(
                            "Mine status"
                        )

                        st.markdown(
                            f"**{mine[STATUS]}**"
                        )

                    with info_right:

                        if COMMODITY is not None:

                            st.caption(
                                "Commodity"
                            )

                            commodity_value = (
                                mine[COMMODITY]
                                if pd.notna(
                                    mine[COMMODITY]
                                )
                                else "-"
                            )

                            st.markdown(
                                f"**{commodity_value}**"
                            )

                        if SUITABILITY is not None:

                            st.caption(
                                "Suitability class"
                            )

                            suitability_value = (
                                mine[SUITABILITY]
                                if pd.notna(
                                    mine[SUITABILITY]
                                )
                                else "-"
                            )

                            st.markdown(
                                f"**{suitability_value}**"
                            )

                # ------------------------------------------------
                # TOPSIS + RANK
                # ------------------------------------------------

                score_col, rank_col = st.columns(
                    2
                )

                score_col.metric(
                    "TOPSIS Score",
                    f"{float(mine[TOPSIS]):.4f}",
                )

                if (
                    RANK is not None
                    and pd.notna(
                        mine[RANK]
                    )
                ):

                    rank_col.metric(
                        "Rank",
                        str(mine[RANK]),
                    )

                else:

                    rank_col.metric(
                        "Rank",
                        "-",
                    )

                # ------------------------------------------------
                # COORDINATES
                # ------------------------------------------------

                with st.container(
                    border=True
                ):

                    st.markdown(
                        "#### Location"
                    )

                    loc1, loc2 = st.columns(
                        2
                    )

                    loc1.caption(
                        "Latitude"
                    )

                    loc1.write(
                        f"{float(mine[LATITUDE]):.5f}"
                    )

                    loc2.caption(
                        "Longitude"
                    )

                    loc2.write(
                        f"{float(mine[LONGITUDE]):.5f}"
                    )

                # ------------------------------------------------
                # ADDITIONAL ATTRIBUTES
                # ------------------------------------------------

                with st.expander(
                    "View additional mine attributes"
                ):

                    excluded_columns = {
                        "_APP_ROW_ID",
                        MINE_NAME,
                        LATITUDE,
                        LONGITUDE,
                        STATE,
                        STATUS,
                        TOPSIS,
                    }

                    if COMMODITY is not None:
                        excluded_columns.add(
                            COMMODITY
                        )

                    if SUITABILITY is not None:
                        excluded_columns.add(
                            SUITABILITY
                        )

                    if RANK is not None:
                        excluded_columns.add(
                            RANK
                        )

                    attribute_rows = []

                    for column in df.columns:

                        if column in excluded_columns:
                            continue

                        value = mine.get(
                            column
                        )

                        if pd.isna(value):
                            continue

                        if isinstance(
                            value,
                            float,
                        ):

                            value = (
                                f"{value:,.4f}"
                            )

                        attribute_rows.append(
                            {
                                "Attribute": column,
                                "Value": value,
                            }
                        )

                    if attribute_rows:

                        attributes_df = pd.DataFrame(
                            attribute_rows
                        )

                        st.dataframe(
                            attributes_df,
                            hide_index=True,
                            use_container_width=True,
                        )

                    else:

                        st.caption(
                            "No additional attributes are available."
                        )

    # ============================================================
    # PROXIMITY ANALYSIS
    # ============================================================

    if selected_row_id is not None:

        selected_rows = filtered_df[
            filtered_df["_APP_ROW_ID"] == selected_row_id
        ]

        if not selected_rows.empty:

            mine = selected_rows.iloc[0]

            proximity_data = []

            for label, column in PROXIMITY_COLUMNS.items():

                value = pd.to_numeric(
                    pd.Series([mine[column]]),
                    errors="coerce"
                ).iloc[0]

                if pd.notna(value):

                    proximity_data.append(
                        {
                            "Criterion": label,
                            "Distance_km": float(value)
                        }
                    )

            if proximity_data:

                st.divider()

                st.subheader(
                    "Proximity Analysis"
                )

                st.caption(
                    "Distance of the selected mine from key infrastructure "
                    "and potential end-user facilities. Lower values indicate "
                    "closer proximity."
                )

                proximity_df = pd.DataFrame(
                    proximity_data
                ).sort_values(
                    "Distance_km",
                    ascending=True
                )

                fig_proximity = px.bar(
                    proximity_df,
                    x="Distance_km",
                    y="Criterion",
                    orientation="h",
                    text_auto=".1f",
                    labels={
                        "Distance_km": "Distance (km)",
                        "Criterion": ""
                    }
                )

                fig_proximity.update_layout(
                    height=450,
                    margin=dict(
                        l=20,
                        r=20,
                        t=20,
                        b=20
                    ),
                    showlegend=False
                )

                fig_proximity.update_yaxes(
                    categoryorder="total ascending"
                )

                st.plotly_chart(
                    fig_proximity,
                    use_container_width=True,
                    config={
                        "responsive": True,
                        "displayModeBar": False,
                    },
                )

# ================================================================
# 14. HIGHEST-RANKED MINES TABLE
# ================================================================

st.write("")


with st.expander(
    "View highest-ranked mines in the current selection"
):

    table_columns = [
        MINE_NAME,
        STATE,
        STATUS,
    ]


    if COMMODITY is not None:

        table_columns.append(
            COMMODITY
        )


    table_columns.append(
        TOPSIS
    )


    if SUITABILITY is not None:

        table_columns.append(
            SUITABILITY
        )


    ranked_mines = (
        filtered_df[
            table_columns
        ]
        .sort_values(
            TOPSIS,
            ascending=False,
        )
        .head(25)
        .copy()
    )


    ranked_mines[TOPSIS] = (
        ranked_mines[TOPSIS]
        .round(4)
    )


    st.dataframe(
        ranked_mines,
        hide_index=True,
        use_container_width=True,
    )


# ================================================================
# 15. DOWNLOAD FILTERED DATA
# ================================================================

csv_data = filtered_df.drop(
    columns=["_APP_ROW_ID"],
    errors="ignore",
).to_csv(
    index=False
).encode(
    "utf-8"
)


st.download_button(
    label="Download filtered mine data",
    data=csv_data,
    file_name="filtered_mine_screening_results.csv",
    mime="text/csv",
    use_container_width=True,
)


# ================================================================
# 16. TOPSIS INFORMATION
# ================================================================

st.divider()


st.subheader(
    "About the Mine Suitability Score"
)


st.markdown(
    """
**TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)**
is a multi-criteria decision-making method used to compare and rank mine
sites according to their relative suitability for mine-based geothermal
energy development.

In this screening framework, multiple criteria representing **geothermal
potential and mine-water characteristics, infrastructure accessibility,
and end-user demand** are combined. The criterion weights are derived using
the integrated **AHP–CRITIC weighting approach**.

TOPSIS compares each mine with two theoretical reference conditions:

- a **positive ideal solution**, representing the most favourable combination
  of criteria; and
- a **negative ideal solution**, representing the least favourable combination.

A mine receives a higher TOPSIS score when it is relatively closer to the
positive ideal solution and farther from the negative ideal solution.
"""
)


# ================================================================
# 17. TOPSIS CALCULATION
# ================================================================

with st.expander(
    "How is the TOPSIS score calculated?"
):

    st.markdown(
        """
First, the criterion values are normalised and multiplied by their respective
weights. Positive and negative ideal solutions are then identified from the
weighted decision matrix.

The Euclidean distance of each mine from the positive ideal solution is:
"""
    )


    st.latex(
        r"""
S_i^{+}
=
\sqrt{
\sum_{j=1}^{n}
\left(
v_{ij}-v_j^{+}
\right)^2
}
"""
    )


    st.markdown(
        """
The distance from the negative ideal solution is:
"""
    )


    st.latex(
        r"""
S_i^{-}
=
\sqrt{
\sum_{j=1}^{n}
\left(
v_{ij}-v_j^{-}
\right)^2
}
"""
    )


    st.markdown(
        """
The final **closeness coefficient** or TOPSIS score is:
"""
    )


    st.latex(
        r"""
C_i
=
\frac{S_i^{-}}
{S_i^{+}+S_i^{-}}
"""
    )


    st.markdown(
        """
where:

- **Sᵢ⁺** is the distance of mine *i* from the positive ideal solution;
- **Sᵢ⁻** is the distance from the negative ideal solution; and
- **Cᵢ** is the final TOPSIS closeness coefficient.

The score generally ranges between **0 and 1**. A higher value indicates
greater relative suitability within the evaluated mine dataset.
"""
    )


# ================================================================
# 18. SCREENING DISCLAIMER
# ================================================================

st.info(
    """
The results presented in this application are intended for preliminary
screening and prioritisation of potential mine-based geothermal sites.
The TOPSIS score represents relative suitability within the evaluated
dataset and should not be considered a substitute for detailed
site-specific geological, hydrogeological, geotechnical, environmental,
technical or economic feasibility assessment.
"""
)


# ================================================================
# 19. FOOTER
# ================================================================

st.caption(
    "Mine-Based Geothermal Screening Tool | "
    "Developed for preliminary assessment of Australian mine sites"
)
