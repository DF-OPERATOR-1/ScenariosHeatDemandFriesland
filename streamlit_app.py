

# import gdown
# import streamlit as st
# import pydeck as pdk
# import pandas as pd
# import h3

# # *** Data loading with caching ***
# @st.cache_data
# def load_data():
#     file_id = "1p7oJsCZ4l8V3MXLX8kWg64RlQbdMTeuA"
#     url = f"https://drive.google.com/uc?export=download&id={file_id}"
#     output = "data_kWh.csv"
#     gdown.download(url, output, quiet=False)
#     return pd.read_csv(output)

# df = load_data()

# # Manual formatter
# def format_dutch_number(num, decimals=2):
#     if isinstance(num, int):
#         return f"{num:,}".replace(",", ".")
#     return f"{num:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")

# # Filter and prepare data
# df = df[["latitude", "longitude", "kWh_per_m2", "gemiddeld_jaarverbruik_mWh",
#          "mWh_tot_scenario_1", "mWh_tot_scenario_2", "mWh_tot_scenario_3", "mWh_tot_scenario_4"]]

# # *** Updated Color Mapping ***
# colorbrewer_colors = [
#     [69, 117, 180, 255],   # Dark blue
#     [254, 224, 144, 255],  # Light orange
#     [215, 48, 39, 255]     # Red
# ]

# def get_color(value, percentiles):
#     if value < percentiles[25]:
#         return colorbrewer_colors[2]
#     elif percentiles[25] <= value <= percentiles[75]:
#         return colorbrewer_colors[1]
#     else:
#         return colorbrewer_colors[0]

# # *** Streamlit UI ***
# st.markdown('<h1 style="font-size: 35px;">Friese Warmtevraagkaart (Heat Demand)</h1>', unsafe_allow_html=True)

# # *** Sidebar elements ***
# with st.sidebar:
#     st.header("Configuratie")
    
#     # Scenario selection
#     scenario_options = {
#         "Current (2024)": "gemiddeld_jaarverbruik_mWh",
#         "Scenario 1": "mWh_tot_scenario_1",
#         "Scenario 2": "mWh_tot_scenario_2", 
#         "Scenario 3": "mWh_tot_scenario_3",
#         "Scenario 4": "mWh_tot_scenario_4"
#     }
#     selected_scenario = st.selectbox("Kies Energie Scenario", options=list(scenario_options.keys()))
#     scenario_column = scenario_options[selected_scenario]

#     # 3D toggle
#     extruded = st.toggle("3D Weergave", value=False)

# # Map creation button
# if st.sidebar.button("Maak Kaart"):
#     # Process data
#     resolution = 9
#     df_clean = df.dropna(subset=[scenario_column])  # Remove rows with missing values
    
#     # Add H3 index
#     df_clean["h3_index"] = df_clean.apply(
#         lambda row: h3.latlng_to_cell(row["latitude"], row["longitude"], resolution), 
#         axis=1
#     )
    
#     # Group by hexagon
#     grouped = df_clean.groupby("h3_index").agg({
#         scenario_column: "sum",
#         "h3_index": "count"
#     }).rename(columns={"h3_index": "aantal_huizen"}).reset_index()
    
#     # Calculate percentiles for dynamic coloring
#     percentiles = {
#         25: grouped[scenario_column].quantile(0.25),
#         75: grouped[scenario_column].quantile(0.75)
#     }
    
#     # Apply color based on scenario values
#     grouped["color"] = grouped[scenario_column].apply(
#         lambda x: get_color(x, percentiles)
#     )
#     # Add rounded column for tooltip
#     grouped["rounded_scenario_value"] = grouped[scenario_column].round(1)

#     # Calculate metrics
#     total_houses = grouped["aantal_huizen"].sum()
#     total_demand = grouped[scenario_column].sum()
    
#     # Create tiles
#     col1, col2 = st.columns(2)
#     with col1:
#         st.metric("Aantal panden", format_dutch_number(total_houses, 0))
#     with col2:
#         st.metric("Totale Heat Demand", f"{format_dutch_number(total_demand, 0)} mWh")

#     # Create map
#     view_state = pdk.ViewState(
#         latitude=df_clean["latitude"].mean(),
#         longitude=df_clean["longitude"].mean(),
#         zoom=10,
#         pitch=40.5 if extruded else 0,
#         bearing=0
#     )

#     layer = pdk.Layer(
#         "H3HexagonLayer",
#         grouped,
#         pickable=True,
#         filled=True,
#         extruded=extruded,
#         get_hexagon="h3_index",
#         get_fill_color="color",
#         get_elevation=f"{scenario_column}/100" if extruded else 0,
#         elevation_scale=50 if extruded else 0,
#         elevation_range=[0, 1000],
#         coverage=1,
#         opacity=0.2
#     )

#     # Display the map in main area
#     st.pydeck_chart(pdk.Deck(
#         layers=[layer],
#         initial_view_state=view_state,
#         tooltip={
#             "html": f"""<b>Scenario:</b> {selected_scenario}<br>
#                       <b>Heat Demand:</b> {{rounded_scenario_value}} mWh<br>
#                       <b>Huizen:</b> {{aantal_huizen}}""",
#             "style": {"backgroundColor": "white", "color": "black"}
#         }
#     ))

#     # Dynamic legend
#     st.markdown(f"""
#     <div style="background: white; padding: 10px; border-radius: 5px; margin-top: 20px;">
#         <h4>Heat Demand Ranges ({selected_scenario})</h4>
#         <div><span style="background: #4575b4; width: 15px; height: 15px; display: inline-block;"></span> &lt; {format_dutch_number(percentiles[25], 0)} mWh</div>
#         <div><span style="background: #fee090; width: 15px; height: 15px; display: inline-block;"></span> {format_dutch_number(percentiles[25], 0)} - {format_dutch_number(percentiles[75], 0)} mWh</div>
#         <div><span style="background: #d73027; width: 15px; height: 15px; display: inline-block;"></span> &gt; {format_dutch_number(percentiles[75], 0)} mWh</div>
#     </div>
#     """, unsafe_allow_html=True)

import gdown
import streamlit as st
import pydeck as pdk
import pandas as pd
import h3

# *** Data loading with caching ***
@st.cache_data
def load_data():
    file_id = "1p7oJsCZ4l8V3MXLX8kWg64RlQbdMTeuA"
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    output = "data_kWh.csv"
    gdown.download(url, output, quiet=False)
    return pd.read_csv(output)

df = load_data()

# Manual Dutch number formatter
def format_dutch_number(num, decimals=2):
    if isinstance(num, int):
        return f"{num:,}".replace(",", ".")
    return f"{num:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", "")

# Filter and prepare data
df = df[["latitude", "longitude", "kWh_per_m2", "gemiddeld_jaarverbruik_mWh",
         "mWh_tot_scenario_1", "mWh_tot_scenario_2", "mWh_tot_scenario_3", "mWh_tot_scenario_4"]]

# *** Color Configuration ***
colorbrewer_colors = [
    [69, 117, 180, 255],   # Dark blue (Lowest usage)
    [254, 224, 144, 255],  # Light orange (Medium usage)
    [215, 48, 39, 255],    # Red (Highest usage)
    [26, 152, 80, 255]     # Green (Threshold exceedance)
]

def get_color(value, percentiles, threshold):
    if value > threshold:
        return colorbrewer_colors[3]  # Green for threshold exceedance
    elif value < percentiles[25]:
        return colorbrewer_colors[2]  # Red
    elif percentiles[25] <= value <= percentiles[75]:
        return colorbrewer_colors[1]  # Orange
    else:
        return colorbrewer_colors[0]  # Blue

# *** Streamlit UI ***
st.markdown("<h1 style='font-size: 35px;'>Scenario's Heatdemand Friesland</h1>" \
            "<h2 style='font-size: 18px;color: #555'>Missende energieklassen zijn geschat en scenarios zijn gebasserd op energieklasse</h2>"
            , unsafe_allow_html=True)



# *** Sidebar Configuration ***
with st.sidebar:
    st.header("Configuratie")
    
    with st.sidebar.expander("ℹ️ Scenario's"):
        st.markdown("""
        <style>
            .scenario-block {
                padding: 5px 0;
                margin-bottom: 8px;
            }
            .scenario-title {
                font-weight: bold;
                color: #336699;
            }
        </style>

        <div class="scenario-block">
            <div class="scenario-title">Scenario 1</div>
            <div>Alle energieklasses 1 label omhoog.</div>
        </div>

        <div class="scenario-block">
            <div class="scenario-title">Scenario 2</div>
            <div>Alle energieklasses 3 labels omhoog.</div>
        </div>

        <div class="scenario-block">
            <div class="scenario-title">Scenario 3</div>
            <div>Alle energieklasses minimaal label B.</div>
        </div>

        <div class="scenario-block">
            <div class="scenario-title">Scenario 4</div>
            <div>Alle energieklasses minimaal label A.</div>
        </div>

        <div class="scenario-block">
            <div class="scenario-title">Algemeen</div>
            <div>In alle scenario's blijven panden met energieklasse A of hoger (bijv. A+ of A++) ongewijzigd.</div>
        </div>
        """, unsafe_allow_html=True)

    # Scenario selection
    scenario_options = {
        "Huidig": "gemiddeld_jaarverbruik_mWh",
        "Scenario 1": "mWh_tot_scenario_1",
        "Scenario 2": "mWh_tot_scenario_2", 
        "Scenario 3": "mWh_tot_scenario_3",
        "Scenario 4": "mWh_tot_scenario_4"
    }
    selected_scenario = st.selectbox("Kies Energie Scenario", options=list(scenario_options.keys()))
    scenario_column = scenario_options[selected_scenario]
    
    # Threshold configuration
    grenswaarde = st.number_input(
        "Stel minimale grenswaarde in (mWh):",
        min_value=0,
        value=2000,  # Default threshold
        step=100
    )
    
    # 3D toggle
    extruded = st.toggle("3D Weergave", value=False)

# Main map creation
if st.sidebar.button("Maak Kaart"):
    # Data processing
    resolution = 9
    df_clean = df.dropna(subset=[scenario_column])
    
    # H3 indexing
    df_clean["h3_index"] = df_clean.apply(
        lambda row: h3.latlng_to_cell(row["latitude"], row["longitude"], resolution), 
        axis=1
    )
    
    # Aggregation
    grouped = df_clean.groupby("h3_index").agg({
        scenario_column: "sum",
        "h3_index": "count"
    }).rename(columns={"h3_index": "aantal_huizen"}).reset_index()

    # Percentile calculation
    percentiles = {
        25: grouped[scenario_column].quantile(0.25),
        75: grouped[scenario_column].quantile(0.75)
    }
    
    # Color assignment
    grouped["color"] = grouped[scenario_column].apply(
        lambda x: get_color(x, percentiles, grenswaarde)
    )
    grouped["rounded_value"] = grouped[scenario_column].round(0)
    
    # Create separate dataset for threshold exceedance
    threshold_df = grouped[grouped[scenario_column] > grenswaarde].copy()
    # threshold_df["color"] = colorbrewer_colors[3]
    threshold_df["color"] = [colorbrewer_colors[3]] * len(threshold_df)


    # Metrics calculation
    total_houses = grouped["aantal_huizen"].sum()
    total_demand = grouped[scenario_column].sum()
    
    # Display metrics
    col1, col2 = st.columns(2)
    with col1:
        # col1.metric("Aantal panden", format_dutch_number(total_houses, 0))
        st.markdown(f"""
            <div style='background-color: #f9f9f9; padding: 10px; border-radius: 10px;
                        border: 1px solid #ddd; text-align: center;margin-bottom: 20px;'>
                <h2 style='margin: 0;'>{format_dutch_number(total_houses, 0)}</h2>
                <p style='margin: 0;'>Aantal panden</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # col2.metric("Totale Warmtevraag", f"{format_dutch_number(total_demand, 0)} mWh")
        st.markdown(f"""
            <div style='background-color: #f9f9f9; padding: 10px; border-radius: 10px;
                        border: 1px solid #ddd; text-align: center;margin-bottom: 20px;'>
                <h2 style='margin: 0;'>{format_dutch_number(total_demand, 0)}</h2>
                <p style='margin: 0;'>Totale Warmtevraag</p>
            </div>
        """, unsafe_allow_html=True)


    # Create layers
    base_layer = pdk.Layer(
        "H3HexagonLayer",
        grouped,
        pickable=True,
        filled=True,
        extruded=extruded,
        get_hexagon="h3_index",
        get_fill_color="color",
        get_elevation=f"{scenario_column}/100" if extruded else 0,
        elevation_scale=50 if extruded else 0,
        elevation_range=[0, 1000],
        coverage=1,
        opacity=0.2
    )

    threshold_layer = pdk.Layer(
        "H3HexagonLayer",
        threshold_df,
        pickable=True,
        filled=True,
        extruded=extruded,
        get_hexagon="h3_index",
        get_fill_color="color",
        get_elevation=f"{scenario_column}/100" if extruded else 0,
        elevation_scale=50 if extruded else 0,
        elevation_range=[0, 1000],
        coverage=1,
        opacity=0.2
    )

    # View state configuration
    view_state = pdk.ViewState(
        latitude=df_clean["latitude"].mean(),
        longitude=df_clean["longitude"].mean(),
        zoom=10,
        pitch=40.5 if extruded else 0,
        bearing=0
    )

    # Display the map
    st.pydeck_chart(pdk.Deck(
        layers=[base_layer, threshold_layer],
        initial_view_state=view_state,
        tooltip={
            "html": f"""<b>Scenario:</b> {selected_scenario}<br>
                      <b>Warmtevraag:</b> {{rounded_value}} mWh<br>
                      <b>Aantal panden:</b> {{aantal_huizen}}""",
            "style": {"backgroundColor": "white", "color": "black"}
        }
    ))

    # Dynamic legend with threshold
    st.markdown(f"""
    <div style="background: white; padding: 10px; border-radius: 5px; margin-top: 20px; border: 1px solid #ddd;">
        <h4 style="margin-top: 0;">Legenda Warmtevraag ({selected_scenario})</h4>
        <div><span style="background: #4575b4; width: 20px; height: 20px; display: inline-block; vertical-align: middle;"></span> Laagste 25% (&lt; {format_dutch_number(percentiles[25], 0)} mWh)</div>
        <div><span style="background: #fee090; width: 20px; height: 20px; display: inline-block; vertical-align: middle;"></span> Midden 50% ({format_dutch_number(percentiles[25], 0)} - {format_dutch_number(percentiles[75], 0)} mWh)</div>
        <div><span style="background: #d73027; width: 20px; height: 20px; display: inline-block; vertical-align: middle;"></span> Hoogste 25% (&gt; {format_dutch_number(percentiles[75], 0)} mWh)</div>
        <div><span style="background: #1a9850; width: 20px; height: 20px; display: inline-block; vertical-align: middle;"></span> Grenswaarde overschreden (&gt; {format_dutch_number(grenswaarde, 0)} mWh)</div>
    </div>
    """, unsafe_allow_html=True)