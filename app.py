# ================================================================
# MINE-BASED GEOTHERMAL SCREENING TOOL
# Complete Streamlit application
# ================================================================

import os
import glob
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
    initial_sidebar_state="expanded",
)


# ================================================================
# 2. CUSTOM STYLE
# ================================================================

st.markdown(
    """
<style>
.block-container {
    max-width: 1650px;
    padding-top: 1.2rem;
    padding-bottom: 2.5rem;
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
    font-size: 2.15rem;
    font-weight: 700;
    margin: 0;
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
</style>
""",
    unsafe_allow_html=True,
)


# ================================================================
# 3. DATA FILE
# ================================================================
# If you know the exact data filename, put it here, for example:
# DATA_FILE = "Sensitivity Analysis - Copy.xlsx"
# Otherwise leave it as None and the app will look for CSV/Excel files.

DATA_FILE = None


def find_data_file():
    if DATA_FILE is not None and os.path.exists(DATA_FILE):
        return DATA_FILE

    candidate_files = []
    for pattern in ["*.csv", "*.xlsx", "*.xls"]:
        candidate_files.extend(glob.glob(pattern))

    candidate_files = [
        f for f in candidate_files
        if not os.path.basename(f).startswith("~$")
    ]

    if not candidate_files:
        return None

    # Prefer CSV, then Excel.
    csv_files = sorted(
        [f for f in candidate_files if f.lower().endswith(".csv")]
    )
    if csv_files:
        return csv_files[0]

    return sorted(candidate_files)[0]


selected_file = find_data_file()

if selected_file is None:
    st.error("No CSV or Excel dataset was found in the application folder.")
    st.info(
        "Upload your mine dataset to the GitHub repository or set DATA_FILE "
        "to the exact filename in app.py."
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
    st.error(f"Unable to load the dataset: {error}")
    st.stop()


# ================================================================
# 5. COLUMN IDENTIFICATION
# ================================================================

def find_column(dataframe, possible_names):
    lower_lookup = {
        str(col).strip().lower(): col
        for col in dataframe.columns
    }

    for name in possible_names:
        key = name.strip().lower()
        if key in lower_lookup:
            return lower_lookup[key]

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
        key = (
            name.strip()
            .lower()
            .replace("_", "")
            .replace(" ", "")
            .replace("-", "")
        )
        if key in simplified_lookup:
            return simplified_lookup[key]

    return None


MINE_NAME = find_column(
    df,
    ["Mine_Name", "Mine Name", "NAME", "MINE_NAME", "Mine", "SITE_NAME", "Site Name"],
)

LATITUDE = find_column(
    df,
    ["Latitude", "LATITUDE", "LAT", "latitude"],
)

LONGITUDE = find_column(
    df,
    ["Longitude", "LONGITUDE", "LON", "LONG", "longitude"],
)

STATE = find_column(
    df,
    ["State", "STATE", "State_Name", "STATE_NAME"],
)

STATUS = find_column(
    df,
    ["Mine_Status", "Mine Status", "STATUS", "Status", "MINESTATUS"],
)

COMMODITY = find_column(
    df,
    ["Commodity", "COMMODITY", "Commodity_Name", "COMMODITIES", "Commodities"],
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

RANK = find_column(
    df,
    ["Rank", "RANK", "TOPSIS_Rank", "TOPSIS Rank"],
)


# ================================================================
# 6. STUDY CRITERIA COLUMNS
# ================================================================
# Exact column names supplied by the user.

TEMPERATURE_COLUMN = "C1_Temperature"
RAINFALL_COLUMN = "C2_Rainfall"

PROXIMITY_COLUMNS = {
    "Faults": "C3_Faults",
    "Direct Use": "C4_Direct_Use",
    "Roads": "C5_Roads",
    "Railways": "C6_Railways",
    "Powerlines": "C7_Powerlines",
    "Ports": "C8_Ports",
    "Health": "C9_Health",
    "Manufacturing": "C10_Manufacturing",
    "Agriculture": "C11_Agriculture",
    "Education": "C12_Education",
    "Data Centres": "C13_Data_Centres",
    "Built-up Areas": "C14_Built_Up",
}

# Only keep criterion fields that really exist in the loaded dataset.
PROXIMITY_COLUMNS = {
    label: column
    for label, column in PROXIMITY_COLUMNS.items()
    if column in df.columns
}


# ================================================================
# 7. VERIFY REQUIRED COLUMNS
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
    st.error("The application could not identify these required fields:")
    st.write(missing)
    st.write("Columns currently available in your dataset:")
    st.code("\n".join(str(column) for column in df.columns))
    st.stop()


# ================================================================
# 8. CLEAN DATA
# ================================================================

for numeric_column in [LATITUDE, LONGITUDE, TOPSIS]:
    df[numeric_column] = pd.to_numeric(
        df[numeric_column],
        errors="coerce",
    )

# Convert criteria to numeric where possible.
for criterion_column in [TEMPERATURE_COLUMN, RAINFALL_COLUMN, *PROXIMITY_COLUMNS.values()]:
    if criterion_column in df.columns:
        df[criterion_column] = pd.to_numeric(
            df[criterion_column],
            errors="coerce",
        )

if RANK is not None:
    df[RANK] = pd.to_numeric(df[RANK], errors="coerce")


df = df.dropna(
    subset=[LATITUDE, LONGITUDE, TOPSIS]
).copy()

# Remove impossible coordinates.
df = df[
    df[LATITUDE].between(-90, 90)
    & df[LONGITUDE].between(-180, 180)
].copy()

# Stable internal ID for map selection.
df = df.reset_index(drop=True)
df["_APP_ROW_ID"] = np.arange(len(df))


# ================================================================
# 9. HEADER
# ================================================================

st.markdown(
    "<div class='hero'>"
    "<div class='hero-title'>Mine-Based Geothermal Screening Tool</div>"
    "<div class='hero-subtitle'>Interactive screening of Australian mine sites "
    "for mine-based geothermal energy opportunities</div>"
    "</div>",
    unsafe_allow_html=True,
)


# ================================================================
# 10. SIDEBAR FILTERS
# ================================================================

st.sidebar.header("Mine Screening Filters")

mine_search = st.sidebar.text_input(
    "Search by mine name",
    placeholder="Enter a mine name",
)

state_options = sorted(
    df[STATE].dropna().astype(str).unique()
)
selected_states = st.sidebar.multiselect(
    "State",
    options=state_options,
    default=state_options,
)

status_options = sorted(
    df[STATUS].dropna().astype(str).unique()
)
selected_status = st.sidebar.multiselect(
    "Mine status",
    options=status_options,
    default=status_options,
)

selected_commodities = []
if COMMODITY is not None:
    commodity_options = sorted(
        df[COMMODITY].dropna().astype(str).unique()
    )
    selected_commodities = st.sidebar.multiselect(
        "Commodity",
        options=commodity_options,
        placeholder="Choose options",
    )

minimum_score = float(df[TOPSIS].min())
maximum_score = float(df[TOPSIS].max())

selected_score = st.sidebar.slider(
    "TOPSIS score range",
    min_value=minimum_score,
    max_value=maximum_score,
    value=(minimum_score, maximum_score),
    step=0.001,
    format="%.3f",
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Adjust the filters to explore mine locations and their screening results."
)


# ================================================================
# 11. APPLY FILTERS
# ================================================================

filtered_df = df.copy()

if mine_search.strip():
    filtered_df = filtered_df[
        filtered_df[MINE_NAME]
        .astype(str)
        .str.contains(mine_search.strip(), case=False, na=False)
    ]

if selected_states:
    filtered_df = filtered_df[
        filtered_df[STATE].astype(str).isin(selected_states)
    ]

if selected_status:
    filtered_df = filtered_df[
        filtered_df[STATUS].astype(str).isin(selected_status)
    ]

if COMMODITY is not None and selected_commodities:
    filtered_df = filtered_df[
        filtered_df[COMMODITY].astype(str).isin(selected_commodities)
    ]

filtered_df = filtered_df[
    filtered_df[TOPSIS].between(selected_score[0], selected_score[1])
].copy()


# ================================================================
# 12. SCREENING SUMMARY
# ================================================================

st.subheader("Screening Summary")

metric1, metric2, metric3, metric4 = st.columns(4)

metric1.metric(
    "Mine Sites",
    f"{len(filtered_df):,}",
)

metric2.metric(
    "States Represented",
    f"{filtered_df[STATE].nunique():,}",
)

if not filtered_df.empty:
    metric3.metric(
        "Highest TOPSIS Score",
        f"{filtered_df[TOPSIS].max():.4f}",
    )
else:
    metric3.metric("Highest TOPSIS Score", "-")

inactive_count = 0
if not filtered_df.empty:
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
# 13. MAP + SELECTED MINE PANEL
# ================================================================

st.subheader("Explore Australian Mine Sites")
st.markdown(
    "<div class='section-description'>Select a mine location on the map to "
    "explore its screening characteristics and proximity to key infrastructure "
    "and end-user facilities.</div>",
    unsafe_allow_html=True,
)

# This variable is available to later sections.
selected_row_id = st.session_state.get("selected_mine_row", None)

if filtered_df.empty:
    st.warning("No mine sites match the selected filters.")

else:
    map_column, detail_column = st.columns(
        [2.75, 1.25],
        gap="large",
    )

    # ------------------------------------------------------------
    # MAP
    # ------------------------------------------------------------
    with map_column:
        map_center = {
            "lat": float(filtered_df[LATITUDE].mean()),
            "lon": float(filtered_df[LONGITUDE].mean()),
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

        fig = px.scatter_map(
            filtered_df,
            lat=LATITUDE,
            lon=LONGITUDE,
            hover_name=MINE_NAME,
            hover_data=hover_data,
            custom_data=["_APP_ROW_ID"],
            center=map_center,
            zoom=3.15,
            height=680,
            map_style="open-street-map",
        )

        # Same symbol and colour for all mine locations.
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
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
        )

        map_selection = st.plotly_chart(
            fig,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key="mine_map",
        )

    # ------------------------------------------------------------
    # GET CLICKED MINE ID
    # ------------------------------------------------------------
    try:
        points = map_selection.selection.points

        if points:
            selected_point = points[0]
            customdata = selected_point.get("customdata")

            if customdata is not None:
                if isinstance(customdata, (list, tuple)):
                    new_selected_id = int(customdata[0])
                else:
                    new_selected_id = int(customdata)

                selected_row_id = new_selected_id
                st.session_state["selected_mine_row"] = selected_row_id

    except Exception:
        # If no new point is clicked, keep the session-state selection.
        selected_row_id = st.session_state.get("selected_mine_row", None)

    # If filters removed the currently selected mine, clear the selection.
    if selected_row_id is not None:
        selected_exists = (
            filtered_df["_APP_ROW_ID"] == selected_row_id
        ).any()

        if not selected_exists:
            selected_row_id = None
            st.session_state.pop("selected_mine_row", None)

    # ------------------------------------------------------------
    # SELECTED MINE DETAILS
    # ------------------------------------------------------------
    with detail_column:
        st.subheader("Selected Mine")

        if selected_row_id is None:
            with st.container(border=True):
                st.info("Click a mine point on the map to view its details.")

        else:
            selected_rows = filtered_df[
                filtered_df["_APP_ROW_ID"] == selected_row_id
            ]

            if selected_rows.empty:
                with st.container(border=True):
                    st.info(
                        "The selected mine is outside the current filters."
                    )
            else:
                mine = selected_rows.iloc[0]

                with st.container(border=True):
                    st.markdown(f"### {mine[MINE_NAME]}")

                    info_left, info_right = st.columns(2)

                    with info_left:
                        st.caption("State")
                        st.markdown(f"**{mine[STATE]}**")

                        st.caption("Mine status")
                        st.markdown(f"**{mine[STATUS]}**")

                    with info_right:
                        if COMMODITY is not None:
                            commodity_value = (
                                mine[COMMODITY]
                                if pd.notna(mine[COMMODITY])
                                else "-"
                            )
                            st.caption("Commodity")
                            st.markdown(f"**{commodity_value}**")

                score_col, rank_col = st.columns(2)

                score_col.metric(
                    "TOPSIS Score",
                    f"{float(mine[TOPSIS]):.4f}",
                )

                if RANK is not None and pd.notna(mine[RANK]):
                    rank_value = mine[RANK]
                    if float(rank_value).is_integer():
                        rank_value = int(rank_value)
                    rank_col.metric("Rank", str(rank_value))
                else:
                    rank_col.metric("Rank", "-")

                # Geothermal characteristics
                geo_values_available = (
                    TEMPERATURE_COLUMN in df.columns
                    or RAINFALL_COLUMN in df.columns
                )

                if geo_values_available:
                    with st.container(border=True):
                        st.markdown("#### Geothermal Characteristics")

                        geo1, geo2 = st.columns(2)

                        if TEMPERATURE_COLUMN in df.columns:
                            temperature_value = mine.get(TEMPERATURE_COLUMN)
                            geo1.caption("Temperature")
                            if pd.notna(temperature_value):
                                geo1.markdown(f"**{float(temperature_value):.2f} °C**")
                            else:
                                geo1.markdown("**-**")

                        if RAINFALL_COLUMN in df.columns:
                            rainfall_value = mine.get(RAINFALL_COLUMN)
                            geo2.caption("Rainfall")
                            if pd.notna(rainfall_value):
                                geo2.markdown(f"**{float(rainfall_value):.2f}**")
                            else:
                                geo2.markdown("**-**")

                # Coordinates
                with st.container(border=True):
                    st.markdown("#### Location")
                    loc1, loc2 = st.columns(2)

                    loc1.caption("Latitude")
                    loc1.write(f"{float(mine[LATITUDE]):.5f}")

                    loc2.caption("Longitude")
                    loc2.write(f"{float(mine[LONGITUDE]):.5f}")

                # Other attributes
                with st.expander("View additional mine attributes"):
                    excluded_columns = {
                        "_APP_ROW_ID",
                        MINE_NAME,
                        LATITUDE,
                        LONGITUDE,
                        STATE,
                        STATUS,
                        TOPSIS,
                        TEMPERATURE_COLUMN,
                        RAINFALL_COLUMN,
                        *PROXIMITY_COLUMNS.values(),
                    }

                    if COMMODITY is not None:
                        excluded_columns.add(COMMODITY)
                    if RANK is not None:
                        excluded_columns.add(RANK)

                    attribute_rows = []

                    for column in df.columns:
                        if column in excluded_columns:
                            continue

                        value = mine.get(column)
                        if pd.isna(value):
                            continue

                        if isinstance(value, (float, np.floating)):
                            value = f"{float(value):,.4f}"

                        attribute_rows.append(
                            {
                                "Attribute": column,
                                "Value": value,
                            }
                        )

                    if attribute_rows:
                        st.dataframe(
                            pd.DataFrame(attribute_rows),
                            hide_index=True,
                            use_container_width=True,
                        )
                    else:
                        st.caption("No additional attributes are available.")


# ================================================================
# 14. PROXIMITY ANALYSIS
# ================================================================
# IMPORTANT: this section uses proximity_mine only. It does not use
# selected_mine, so the earlier NameError cannot occur here.

if selected_row_id is not None and not filtered_df.empty:
    proximity_selected_rows = filtered_df[
        filtered_df["_APP_ROW_ID"] == selected_row_id
    ]

    if not proximity_selected_rows.empty and PROXIMITY_COLUMNS:
        proximity_mine = proximity_selected_rows.iloc[0]

        proximity_data = []

        for label, column in PROXIMITY_COLUMNS.items():
            value = pd.to_numeric(
                pd.Series([proximity_mine.get(column)]),
                errors="coerce",
            ).iloc[0]

            if pd.notna(value):
                proximity_data.append(
                    {
                        "Criterion": label,
                        "Distance": float(value),
                    }
                )

        if proximity_data:
            st.divider()
            st.subheader("Proximity Analysis")
            st.caption(
                "Distance from the selected mine to key geological, infrastructure "
                "and end-user features. Lower values indicate closer proximity."
            )

            proximity_df = pd.DataFrame(proximity_data).sort_values(
                "Distance",
                ascending=True,
            )

            proximity_graph_col, comparison_graph_col = st.columns(
                2,
                gap="large",
            )

            # ----------------------------------------------------
            # GRAPH 1: SELECTED MINE PROXIMITY PROFILE
            # ----------------------------------------------------
            with proximity_graph_col:
                st.markdown("#### Selected Mine Proximity Profile")

                fig_proximity = px.bar(
                    proximity_df,
                    x="Distance",
                    y="Criterion",
                    orientation="h",
                    text_auto=".1f",
                    labels={
                        "Distance": "Distance (km)",
                        "Criterion": "",
                    },
                )

                fig_proximity.update_layout(
                    height=530,
                    margin=dict(l=20, r=20, t=20, b=20),
                    showlegend=False,
                )

                # Nearest feature appears at the top.
                fig_proximity.update_yaxes(
                    categoryorder="array",
                    categoryarray=proximity_df["Criterion"].tolist()[::-1],
                )

                st.plotly_chart(
                    fig_proximity,
                    use_container_width=True,
                )

            # ----------------------------------------------------
            # GRAPH 2: SELECTED MINE VS FILTERED-MINE MEDIAN
            # ----------------------------------------------------
            comparison_data = []

            for label, column in PROXIMITY_COLUMNS.items():
                selected_value = pd.to_numeric(
                    pd.Series([proximity_mine.get(column)]),
                    errors="coerce",
                ).iloc[0]

                population_values = pd.to_numeric(
                    filtered_df[column],
                    errors="coerce",
                ).dropna()

                if population_values.empty:
                    continue

                median_value = population_values.median()

                if pd.notna(selected_value) and pd.notna(median_value):
                    comparison_data.append(
                        {
                            "Criterion": label,
                            "Selected Mine": float(selected_value),
                            "Filtered Mine Median": float(median_value),
                        }
                    )

            with comparison_graph_col:
                st.markdown("#### Selected Mine vs Current Selection")

                if comparison_data:
                    comparison_df = pd.DataFrame(comparison_data)

                    comparison_long = comparison_df.melt(
                        id_vars="Criterion",
                        value_vars=[
                            "Selected Mine",
                            "Filtered Mine Median",
                        ],
                        var_name="Mine Group",
                        value_name="Distance",
                    )

                    fig_compare = px.bar(
                        comparison_long,
                        x="Distance",
                        y="Criterion",
                        color="Mine Group",
                        barmode="group",
                        orientation="h",
                        labels={
                            "Distance": "Distance (km)",
                            "Criterion": "",
                            "Mine Group": "",
                        },
                    )

                    fig_compare.update_layout(
                        height=530,
                        margin=dict(l=20, r=20, t=20, b=20),
                        legend_title_text="",
                    )

                    st.plotly_chart(
                        fig_compare,
                        use_container_width=True,
                    )
                else:
                    st.info(
                        "There are not enough proximity values to create the comparison graph."
                    )


# ================================================================
# 15. HIGHEST-RANKED MINES TABLE
# ================================================================

st.write("")

with st.expander("View highest-ranked mines in the current selection"):
    if filtered_df.empty:
        st.info("No mines are available for the current filters.")
    else:
        table_columns = [
            MINE_NAME,
            STATE,
            STATUS,
        ]

        if COMMODITY is not None:
            table_columns.append(COMMODITY)

        table_columns.append(TOPSIS)

        if RANK is not None:
            table_columns.append(RANK)

        # Remove duplicates while preserving order.
        table_columns = list(dict.fromkeys(table_columns))

        ranked_mines = (
            filtered_df[table_columns]
            .sort_values(TOPSIS, ascending=False)
            .head(25)
            .copy()
        )

        ranked_mines[TOPSIS] = ranked_mines[TOPSIS].round(4)

        st.dataframe(
            ranked_mines,
            hide_index=True,
            use_container_width=True,
        )


# ================================================================
# 16. DOWNLOAD FILTERED DATA
# ================================================================

csv_data = (
    filtered_df
    .drop(columns=["_APP_ROW_ID"], errors="ignore")
    .to_csv(index=False)
    .encode("utf-8")
)

st.download_button(
    label="Download filtered mine data",
    data=csv_data,
    file_name="filtered_mine_screening_results.csv",
    mime="text/csv",
)


# ================================================================
# 17. TOPSIS INFORMATION
# ================================================================

st.divider()

st.subheader("About the Mine Suitability Score")

st.markdown(
    """
**TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)**
is a multi-criteria decision-making method used to compare and rank mine sites
according to their relative suitability for mine-based geothermal energy
development.

In this screening framework, multiple criteria representing **geothermal
potential and mine-water characteristics, infrastructure accessibility, and
end-user demand** are combined. Criterion weights are derived using the
integrated **AHP–CRITIC weighting approach**.

TOPSIS compares each mine with two theoretical reference conditions: a
**positive ideal solution**, representing the most favourable combination of
criterion values, and a **negative ideal solution**, representing the least
favourable combination. A mine receives a higher TOPSIS score when it is
relatively closer to the positive ideal solution and farther from the negative
ideal solution.
"""
)


# ================================================================
# 18. TOPSIS CALCULATION
# ================================================================

with st.expander("How is the TOPSIS score calculated?"):
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
\left(v_{ij}-v_j^{+}\right)^2
}
"""
    )

    st.markdown("The distance from the negative ideal solution is:")

    st.latex(
        r"""
S_i^{-}
=
\sqrt{
\sum_{j=1}^{n}
\left(v_{ij}-v_j^{-}\right)^2
}
"""
    )

    st.markdown("The final **closeness coefficient** or TOPSIS score is:")

    st.latex(
        r"""
C_i
=
\frac{S_i^{-}}
{S_i^{+}+S_i^{-}}
"""
    )

    st.markdown(
        r"""
where:

- **$S_i^{+}$** is the distance of mine *i* from the positive ideal solution;
- **$S_i^{-}$** is the distance from the negative ideal solution; and
- **$C_i$** is the final TOPSIS closeness coefficient.

The score generally ranges between **0 and 1**. A higher value indicates
greater relative suitability within the evaluated mine dataset.
"""
    )


# ================================================================
# 19. DISCLAIMER
# ================================================================

st.info(
    """
The results presented in this application are intended for preliminary
screening and prioritisation of potential mine-based geothermal sites. The
TOPSIS score represents relative suitability within the evaluated dataset and
should not be considered a substitute for detailed site-specific geological,
hydrogeological, geotechnical, environmental, technical or economic feasibility
assessment.
"""
)


# ================================================================
# 20. FOOTER
# ================================================================

st.caption(
    "Mine-Based Geothermal Screening Tool | "
    "Developed for preliminary assessment of Australian mine sites"
)
