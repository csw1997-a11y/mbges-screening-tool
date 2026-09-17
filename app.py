# ============================================================
# MINE-BASED GEOTHERMAL ENERGY SCREENING TOOL
# Streamlit Web Application
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Mine-Based Geothermal Screening Tool",
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main application width */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1650px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f7f9fc;
        border-right: 1px solid #e5e7eb;
    }

    [data-testid="stSidebar"] h2 {
        color: #16324f;
    }

    /* Main title banner */
    .app-header {
        padding: 1.6rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.6rem;
        background: linear-gradient(
            120deg,
            #0a2942,
            #126782
        );
        color: white;
        box-shadow: 0px 4px 14px rgba(0,0,0,0.08);
    }

    .app-header h1 {
        margin: 0;
        font-size: 2.1rem;
        font-weight: 700;
    }

    .app-header p {
        margin-top: 0.45rem;
        margin-bottom: 0;
        font-size: 1rem;
        opacity: 0.92;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e5e9ef;
        padding: 16px;
        border-radius: 14px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.04);
    }

    [data-testid="stMetricLabel"] {
        font-weight: 600;
    }

    /* Section headings */
    .section-title {
        font-size: 1.45rem;
        font-weight: 700;
        color: #17324d;
        margin-bottom: 0.2rem;
    }

    .section-subtitle {
        color: #637083;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }

    /* Selected mine card */
    .mine-card {
        background: #ffffff;
        border: 1px solid #e1e7ee;
        border-radius: 15px;
        padding: 1.2rem 1.3rem;
        box-shadow: 0px 3px 12px rgba(0,0,0,0.05);
        margin-top: 0.4rem;
    }

    .mine-name {
        font-size: 1.35rem;
        font-weight: 700;
        color: #13334c;
        margin-bottom: 0.8rem;
    }

    .small-label {
        color: #6b7280;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    .large-value {
        color: #172b3a;
        font-size: 1rem;
        font-weight: 600;
    }

    /* TOPSIS information */
    .info-box {
        background: #f7fafc;
        border: 1px solid #dde6ee;
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin-top: 1rem;
    }

    /* Remove unnecessary top whitespace */
    header[data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 3. DATA FILE
# ============================================================

# ------------------------------------------------------------
# CHANGE THIS FILE NAME IF NECESSARY
# ------------------------------------------------------------

DATA_FILE = "mine_screening_data.csv"


# ============================================================
# 4. LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    if DATA_FILE.lower().endswith(".csv"):

        df = pd.read_csv(DATA_FILE)

    elif DATA_FILE.lower().endswith((".xlsx", ".xls")):

        df = pd.read_excel(DATA_FILE)

    else:

        raise ValueError(
            "The dataset must be a CSV or Excel file."
        )

    return df


try:

    df = load_data()

except Exception as e:

    st.error(
        f"Unable to load the dataset: {e}"
    )

    st.stop()


# ============================================================
# 5. COLUMN CONFIGURATION
# ============================================================

# ------------------------------------------------------------
# IMPORTANT:
#
# Change the values on the RIGHT SIDE if your column names
# are different.
#
# Example:
#
# MINE_NAME = "NAME"
#
# instead of:
#
# MINE_NAME = "Mine_Name"
# ------------------------------------------------------------


MINE_NAME = "Mine_Name"

MINE_ID = "Mine_ID"

LATITUDE = "Latitude"

LONGITUDE = "Longitude"

STATE = "State"

STATUS = "Mine_Status"

COMMODITY = "Commodity"

TOPSIS = "TOPSIS_Score"

SUITABILITY = "Suitability"

RANK = "Rank"


# ------------------------------------------------------------
# Optional columns
#
# These can be changed to match your database.
# If they do not exist, the application simply does not
# display them.
# ------------------------------------------------------------

TEMPERATURE = "Temperature"

RECHARGE = "Recharge"

ROAD = "Road_Distance"

RAIL = "Rail_Distance"

POWERLINE = "Powerline_Distance"

PORT = "Port_Distance"

DATA_CENTRE = "DataCentre_Distance"

BUILTUP = "BuiltUp_Distance"

MANUFACTURING = "Manufacturing_Distance"

HEALTH = "Health_Distance"

EDUCATION = "Education_Distance"

AGRICULTURE = "Agriculture_Distance"


# ============================================================
# 6. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [

    MINE_NAME,
    LATITUDE,
    LONGITUDE,
    STATE,
    STATUS,
    TOPSIS

]


missing_columns = [

    col
    for col in required_columns
    if col not in df.columns

]


if missing_columns:

    st.error(
        "The following required columns are missing from "
        "the dataset:"
    )

    st.write(missing_columns)

    st.info(
        "Please update the column names in Section 5 "
        "of app.py so that they match your dataset."
    )

    st.stop()


# ============================================================
# 7. CLEAN DATA
# ============================================================

df[LATITUDE] = pd.to_numeric(
    df[LATITUDE],
    errors="coerce"
)

df[LONGITUDE] = pd.to_numeric(
    df[LONGITUDE],
    errors="coerce"
)

df[TOPSIS] = pd.to_numeric(
    df[TOPSIS],
    errors="coerce"
)


df = df.dropna(
    subset=[
        LATITUDE,
        LONGITUDE,
        TOPSIS
    ]
).copy()


# Generate a Mine ID if one is not already available
if MINE_ID not in df.columns:

    df[MINE_ID] = np.arange(
        1,
        len(df) + 1
    )


# ============================================================
# 8. HEADER
# ============================================================

st.markdown(
    """
    <div class="app-header">

        <h1>
        Mine-Based Geothermal Screening Tool
        </h1>

        <p>
        Interactive screening of Australian mine sites for
        mine-based geothermal energy opportunities
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 9. SIDEBAR FILTERS
# ============================================================

st.sidebar.markdown(
    "## Mine Screening Filters"
)


# ------------------------------------------------------------
# Mine search
# ------------------------------------------------------------

mine_search = st.sidebar.text_input(
    "Search by mine name",
    placeholder="Enter a mine name"
)


# ------------------------------------------------------------
# State
# ------------------------------------------------------------

state_options = sorted(
    df[STATE]
    .dropna()
    .astype(str)
    .unique()
)


selected_states = st.sidebar.multiselect(

    "State",

    options=state_options,

    default=state_options
)


# ------------------------------------------------------------
# Mine status
# ------------------------------------------------------------

status_options = sorted(
    df[STATUS]
    .dropna()
    .astype(str)
    .unique()
)


selected_status = st.sidebar.multiselect(

    "Mine status",

    options=status_options,

    default=status_options
)


# ------------------------------------------------------------
# Commodity
# ------------------------------------------------------------

if COMMODITY in df.columns:

    commodity_options = sorted(
        df[COMMODITY]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_commodity = st.sidebar.multiselect(

        "Commodity",

        options=commodity_options
    )

else:

    selected_commodity = []


# ------------------------------------------------------------
# TOPSIS range
# ------------------------------------------------------------

min_score = float(
    df[TOPSIS].min()
)

max_score = float(
    df[TOPSIS].max()
)


selected_score = st.sidebar.slider(

    "TOPSIS score range",

    min_value=min_score,

    max_value=max_score,

    value=(
        min_score,
        max_score
    ),

    step=0.001,

    format="%.3f"
)


# ============================================================
# 10. APPLY FILTERS
# ============================================================

filtered_df = df.copy()


if mine_search:

    filtered_df = filtered_df[

        filtered_df[MINE_NAME]
        .astype(str)
        .str.contains(
            mine_search,
            case=False,
            na=False
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
    COMMODITY in filtered_df.columns
    and selected_commodity
):

    filtered_df = filtered_df[

        filtered_df[COMMODITY]
        .astype(str)
        .isin(selected_commodity)

    ]


filtered_df = filtered_df[

    filtered_df[TOPSIS]
    .between(
        selected_score[0],
        selected_score[1]
    )

]


# ============================================================
# 11. SCREENING SUMMARY
# ============================================================

st.markdown(
    """
    <div class="section-title">
    Screening Summary
    </div>
    """,
    unsafe_allow_html=True
)


metric_1, metric_2, metric_3, metric_4 = st.columns(4)


with metric_1:

    st.metric(
        "Mine Sites",
        f"{len(filtered_df):,}"
    )


with metric_2:

    states_count = filtered_df[
        STATE
    ].nunique()

    st.metric(
        "States Represented",
        f"{states_count:,}"
    )


with metric_3:

    if len(filtered_df) > 0:

        highest_score = filtered_df[
            TOPSIS
        ].max()

        st.metric(
            "Highest TOPSIS Score",
            f"{highest_score:.4f}"
        )

    else:

        st.metric(
            "Highest TOPSIS Score",
            "-"
        )


with metric_4:

    if COMMODITY in filtered_df.columns:

        commodity_count = filtered_df[
            COMMODITY
        ].nunique()

        st.metric(
            "Commodities",
            f"{commodity_count:,}"
        )

    else:

        st.metric(
            "Commodities",
            "-"
        )


st.write("")


# ============================================================
# 12. MAP SECTION
# ============================================================

st.markdown(
    """
    <div class="section-title">
    Explore Australian Mine Sites
    </div>

    <div class="section-subtitle">
    Select a mine location on the map to explore its
    geothermal potential, infrastructure accessibility,
    end-user demand and screening characteristics.
    </div>
    """,
    unsafe_allow_html=True
)


if len(filtered_df) == 0:

    st.warning(
        "No mine sites match the selected filters."
    )

else:

    # --------------------------------------------------------
    # MAP + DETAILS LAYOUT
    # --------------------------------------------------------

    map_col, detail_col = st.columns(
        [3.4, 1.25],
        gap="large"
    )


    # ========================================================
    # MAP
    # ========================================================

    with map_col:

        # Determine map centre from currently visible mines
        map_center = {

            "lat":
                filtered_df[LATITUDE].mean(),

            "lon":
                filtered_df[LONGITUDE].mean()

        }


        # Build hover information
        hover_dict = {

            LATITUDE: False,

            LONGITUDE: False,

            TOPSIS: ":.4f",

            STATE: True,

            STATUS: True

        }


        if COMMODITY in filtered_df.columns:

            hover_dict[
                COMMODITY
            ] = True


        fig = px.scatter_map(

            filtered_df,

            lat=LATITUDE,

            lon=LONGITUDE,

            hover_name=MINE_NAME,

            hover_data=hover_dict,

            custom_data=[
                MINE_ID
            ],

            center=map_center,

            zoom=3.1,

            map_style="open-street-map",

            height=650

        )


        # ----------------------------------------------------
        # SAME SYMBOL FOR ALL MINES
        # ----------------------------------------------------

        fig.update_traces(

            marker=dict(

                size=7,

                color="#1976D2",

                opacity=0.72

            ),

            selected=dict(

                marker=dict(

                    size=12,

                    opacity=1

                )

            ),

            unselected=dict(

                marker=dict(

                    opacity=0.55

                )

            )

        )


        fig.update_layout(

            margin=dict(
                l=0,
                r=0,
                t=0,
                b=0
            ),

            showlegend=False

        )


        # ----------------------------------------------------
        # INTERACTIVE SELECTION
        # ----------------------------------------------------

        map_event = st.plotly_chart(

            fig,

            use_container_width=True,

            on_select="rerun",

            selection_mode="points",

            key="mine_map"

        )


    # ========================================================
    # DETERMINE SELECTED MINE
    # ========================================================

    selected_mine_id = None


    try:

        if (
            map_event
            and map_event.selection
            and map_event.selection.points
        ):

            selected_point = (
                map_event.selection.points[0]
            )


            custom_data = selected_point.get(
                "customdata"
            )


            if custom_data:

                selected_mine_id = (
                    custom_data[0]
                )


                st.session_state[
                    "selected_mine_id"
                ] = selected_mine_id


    except Exception:

        pass


    # Keep previous selection
    if selected_mine_id is None:

        selected_mine_id = (
            st.session_state.get(
                "selected_mine_id"
            )
        )


    # ========================================================
    # DETAILS PANEL
    # ========================================================

    with detail_col:

        st.markdown(
            "### Selected Mine"
        )


        if selected_mine_id is not None:

            mine_selection = filtered_df[

                filtered_df[MINE_ID]
                == selected_mine_id

            ]


            if len(mine_selection) > 0:

                mine = (
                    mine_selection.iloc[0]
                )


                mine_name = str(
                    mine.get(
                        MINE_NAME,
                        "Unknown Mine"
                    )
                )


                state_value = str(
                    mine.get(
                        STATE,
                        "-"
                    )
                )


                status_value = str(
                    mine.get(
                        STATUS,
                        "-"
                    )
                )


                commodity_value = str(
                    mine.get(
                        COMMODITY,
                        "-"
                    )
                )


                topsis_value = mine.get(
                    TOPSIS,
                    np.nan
                )


                # ------------------------------------------------
                # MINE SUMMARY CARD
                # ------------------------------------------------

                st.markdown(
                    f"""
                    <div class="mine-card">

                        <div class="mine-name">
                        {mine_name}
                        </div>

                        <div class="small-label">
                        State
                        </div>

                        <div class="large-value">
                        {state_value}
                        </div>

                        <br>

                        <div class="small-label">
                        Mine Status
                        </div>

                        <div class="large-value">
                        {status_value}
                        </div>

                        <br>

                        <div class="small-label">
                        Commodity
                        </div>

                        <div class="large-value">
                        {commodity_value}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


                st.write("")


                # ------------------------------------------------
                # TOPSIS SCORE
                # ------------------------------------------------

                if pd.notna(
                    topsis_value
                ):

                    st.metric(

                        "TOPSIS Score",

                        f"{float(topsis_value):.4f}"

                    )


                # ------------------------------------------------
                # RANK
                # ------------------------------------------------

                if RANK in mine.index:

                    rank_value = (
                        mine.get(RANK)
                    )

                    if pd.notna(
                        rank_value
                    ):

                        st.metric(
                            "Rank",
                            f"{rank_value}"
                        )


                # ------------------------------------------------
                # OPTIONAL SUITABILITY
                #
                # Suitability is shown as INFORMATION ONLY.
                # It does not control map colour.
                # ------------------------------------------------

                if SUITABILITY in mine.index:

                    suitability_value = (
                        mine.get(
                            SUITABILITY
                        )
                    )

                    if pd.notna(
                        suitability_value
                    ):

                        st.write(
                            "**Suitability:**",
                            suitability_value
                        )


                # ------------------------------------------------
                # GEOTHERMAL CHARACTERISTICS
                # ------------------------------------------------

                geothermal_items = []


                if TEMPERATURE in mine.index:

                    value = mine.get(
                        TEMPERATURE
                    )

                    if pd.notna(value):

                        geothermal_items.append(
                            (
                                "Temperature",
                                value,
                                "°C"
                            )
                        )


                if RECHARGE in mine.index:

                    value = mine.get(
                        RECHARGE
                    )

                    if pd.notna(value):

                        geothermal_items.append(
                            (
                                "Recharge",
                                value,
                                ""
                            )
                        )


                if geothermal_items:

                    st.markdown(
                        "#### Geothermal"
                    )

                    for label, value, unit in geothermal_items:

                        try:

                            value_display = (
                                f"{float(value):,.2f}"
                            )

                        except:

                            value_display = str(
                                value
                            )


                        st.write(
                            f"**{label}:** "
                            f"{value_display} {unit}"
                        )


                # ------------------------------------------------
                # INFRASTRUCTURE PROXIMITY
                # ------------------------------------------------

                infrastructure_columns = [

                    (
                        "Road",
                        ROAD
                    ),

                    (
                        "Rail",
                        RAIL
                    ),

                    (
                        "Powerline",
                        POWERLINE
                    ),

                    (
                        "Port",
                        PORT
                    )

                ]


                available_infrastructure = [

                    (
                        label,
                        column
                    )

                    for label, column
                    in infrastructure_columns

                    if column
                    in mine.index
                    and pd.notna(
                        mine.get(column)
                    )

                ]


                if available_infrastructure:

                    st.markdown(
                        "#### Infrastructure"
                    )


                    for (
                        label,
                        column
                    ) in available_infrastructure:

                        value = mine.get(
                            column
                        )


                        try:

                            display = (
                                f"{float(value):,.2f} km"
                            )

                        except:

                            display = str(
                                value
                            )


                        st.write(
                            f"**{label}:** "
                            f"{display}"
                        )


                # ------------------------------------------------
                # END-USER DEMAND
                # ------------------------------------------------

                demand_columns = [

                    (
                        "Data Centre",
                        DATA_CENTRE
                    ),

                    (
                        "Built-up Area",
                        BUILTUP
                    ),

                    (
                        "Manufacturing",
                        MANUFACTURING
                    ),

                    (
                        "Health",
                        HEALTH
                    ),

                    (
                        "Education",
                        EDUCATION
                    ),

                    (
                        "Agriculture",
                        AGRICULTURE
                    )

                ]


                available_demand = [

                    (
                        label,
                        column
                    )

                    for label, column
                    in demand_columns

                    if column
                    in mine.index
                    and pd.notna(
                        mine.get(column)
                    )

                ]


                if available_demand:

                    st.markdown(
                        "#### End-user Demand"
                    )


                    for (
                        label,
                        column
                    ) in available_demand:

                        value = mine.get(
                            column
                        )


                        try:

                            display = (
                                f"{float(value):,.2f} km"
                            )

                        except:

                            display = str(
                                value
                            )


                        st.write(
                            f"**{label}:** "
                            f"{display}"
                        )


                # ------------------------------------------------
                # COORDINATES
                # ------------------------------------------------

                with st.expander(
                    "Location information"
                ):

                    st.write(
                        "**Latitude:**",
                        f"{mine[LATITUDE]:.6f}"
                    )

                    st.write(
                        "**Longitude:**",
                        f"{mine[LONGITUDE]:.6f}"
                    )


            else:

                st.info(
                    "The previously selected mine "
                    "is outside the current filters."
                )


        else:

            st.info(
                "Click a mine point on the map "
                "to view detailed information."
            )


# ============================================================
# 13. OPTIONAL TOP MINES TABLE
# ============================================================

st.write("")

with st.expander(
    "View highest-ranked mines in current selection"
):

    display_columns = [

        MINE_NAME,
        STATE,
        STATUS,
        TOPSIS

    ]


    if COMMODITY in filtered_df.columns:

        display_columns.insert(
            3,
            COMMODITY
        )


    if SUITABILITY in filtered_df.columns:

        display_columns.append(
            SUITABILITY
        )


    top_mines = (

        filtered_df[
            display_columns
        ]

        .sort_values(
            TOPSIS,
            ascending=False
        )

        .head(20)

    )


    st.dataframe(

        top_mines,

        use_container_width=True,

        hide_index=True

    )


# ============================================================
# 14. ABOUT TOPSIS
# ============================================================

st.markdown("---")


st.markdown(
    """
    <div class="section-title">
    About the Mine Suitability Score
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="info-box">

    <b>TOPSIS</b> stands for
    <b>Technique for Order Preference by Similarity to Ideal Solution</b>.
    It is a multi-criteria decision-making method used in this screening
    framework to compare and rank mine sites according to their relative
    suitability for mine-based geothermal energy development.

    <br><br>

    The assessment considers multiple criteria representing
    <b>geothermal potential</b>,
    <b>infrastructure accessibility</b>, and
    <b>end-user energy demand</b>.
    Criterion weights are obtained using the integrated
    <b>AHP–CRITIC weighting approach</b>.

    <br><br>

    TOPSIS identifies a
    <b>positive ideal solution</b>, representing the most favourable
    combination of criterion values, and a
    <b>negative ideal solution</b>, representing the least favourable
    combination. Each mine is evaluated according to its relative
    distance from these two reference solutions.

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 15. TOPSIS CALCULATION
# ============================================================

with st.expander(
    "How is the TOPSIS score calculated?"
):

    st.markdown(
        """
        The TOPSIS procedure involves four main stages:

        1. Normalising the criterion values.
        2. Applying the criterion weights.
        3. Identifying the positive and negative ideal solutions.
        4. Calculating the distance of each mine from the two
           ideal reference solutions.

        The final closeness coefficient is calculated as:
        """
    )


    st.latex(
        r"""
        C_i =
        \frac{S_i^-}
        {S_i^+ + S_i^-}
        """
    )


    st.markdown(
        """
        where:

        - **Cᵢ** = TOPSIS closeness coefficient for mine *i*
        - **Sᵢ⁺** = distance from the positive ideal solution
        - **Sᵢ⁻** = distance from the negative ideal solution

        The score normally ranges between **0 and 1**.
        A higher value indicates that the mine is closer to the
        positive ideal solution and therefore has a higher relative
        suitability within the screening framework.
        """
    )


# ============================================================
# 16. DISCLAIMER
# ============================================================

st.info(
    """
    The TOPSIS score represents relative suitability within the
    evaluated mine dataset. The results are intended for preliminary
    screening and prioritisation and should not be interpreted as a
    substitute for detailed site-specific geological, hydrogeological,
    engineering, environmental or economic feasibility assessment.
    """
)


# ============================================================
# END OF APPLICATION
# ============================================================
