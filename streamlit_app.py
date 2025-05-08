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
df = df[df["pandstatus"] == "Pand in gebruik"]
# Manual Dutch number formatter

def format_dutch_number(number, decimal_places=0):
    """Format number with thousands separated by '.' and decimals (if any) separated by ','"""
    if isinstance(number, str):
        return number
    try:
        if decimal_places > 0:
            number = float(round(float(number), decimal_places))
            integer_part, decimal_part = str(number).replace(',', '.').split('.')
            integer_part = f"{int(integer_part):,}".replace(",", ".")
            return f"{integer_part},{decimal_part.ljust(decimal_places, '0')}"
        else:
            integer_part = int(round(float(number), 0))
            return f"{integer_part:,}".replace(",", ".")
    except:
        return str(number)

# Filter and prepare data
df = df[["latitude", "longitude", "kWh_per_m2", "gemiddeld_jaarverbruik_mWh",
         "mWh_tot_scenario_1", "mWh_tot_scenario_2", "mWh_tot_scenario_3", "mWh_tot_scenario_4"]]


# # *** Color Configuration ***
# colorbrewer_colors = [
#     [247, 251, 255, 255],  # <25
#     [200, 220, 240, 255],  # 25–100
#     [150, 190, 230, 255],  # 100–500
#     [100, 160, 200, 255],  # 500–1000
#     [80, 120, 180, 255],   # 1000–2000
#     [60, 80, 160, 255],    # 2000–5000
#     [40, 40, 140, 255]     # >5000
# ]

# colorbrewer_colors = [
#     [254, 224, 139, 255],  # Yellow-Orange
#     [255, 255, 191, 255],  # Light Yellow
#     [230, 245, 152, 255],  # Light Lime
#     [171, 221, 164, 255],  # Light Green
#     [102, 194, 165, 255],  # Green
#     [50, 136, 189, 255],   # Blue-Green
#     [94, 79, 162, 255]     # Purple
# ]

colorbrewer_colors = [
    [255, 255, 255, 255],  # Light Lime
    [255, 255, 191, 255],  # Light Yellow
    [254, 224, 139, 255],  # Yellow-Orange
    [253, 174, 97, 255],   # Light Orange
    [244, 109, 67, 255],   # Orange-Red
    [213, 62, 79, 255],    # Red
    [158, 1, 66, 255],     # Dark Red-Purple

]

def get_color(value):
    if value < 25:
        return colorbrewer_colors[0]
    elif 25 <= value < 100:
        return colorbrewer_colors[1]
    elif 100 <= value < 500:
        return colorbrewer_colors[2]
    elif 500 <= value < 1000:
        return colorbrewer_colors[3]
    elif 1000 <= value < 2000:
        return colorbrewer_colors[4]
    elif 2000 <= value < 5000:
        return colorbrewer_colors[5]
    else:
        return colorbrewer_colors[6]

# *** Streamlit UI ***
st.markdown("<h1 style='font-size: 35px;'>Scenario's Heat Demand Fryslân</h1>" \
            "<h2 style='font-size: 18px;color: #555'>Missende energieklassen zijn geschat en scenarios zijn gebaseerd op beschikbare en geschatte energieklassen</h2>"
            , unsafe_allow_html=True)



# *** Sidebar Configuration ***
with st.sidebar:
    st.header("Configuratie")
    
    # *** Kies een kaartstijl ***
    map_style = st.sidebar.selectbox(
        "Kies een kaartstijl:",
        options=["dark", "light", "streets", "outdoors", "satellite", "satellite-streets"],
        format_func=lambda x: x.capitalize()
    )

    map_style_url = f"mapbox://styles/mapbox/{map_style}-v9"
    
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
    
        # Info about hexagon size
    st.markdown("""
        <style>
            .info-icon {
                display: inline-block;
                width: 20px;
                height: 20px;
                background-color: #0078D7;
                color: white;
                text-align: center;
                border-radius: 50%;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                margin-left: 10px;
                margin-bottom: 40px;
            }
            .tooltip-text {
                visibility: hidden;
                width: 250px;
                background: #333;
                color: #fff;
                text-align: left;
                border-radius: 4px;
                padding: 8px;
                position: absolute;
                z-index: 1000;
                top: 0; 
                left: 110%;
                margin-left: -10px;
                opacity: 0;
                transition: opacity 0.3s;
                font-size: 12px;
            }
            .info-icon:hover + .tooltip-text {
                visibility: visible;
                opacity: 1;
            }
        </style>

        <div style="position: relative; display: inline-block;">
            <span class="info-icon" title="">i</span>
            <div class="tooltip-text">
                Elke hexagon op de kaart heeft een oppervlakte van ongeveer 1 hectare.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 3D toggle
    # extruded = st.toggle("3D Weergave", value=False)


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

   # Color assignment using fixed bins
    grouped["color"] = grouped[scenario_column].apply(get_color)

    grouped["rounded_value"] = grouped[scenario_column].round(0)
    
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
                <h2 style='margin: 0;'>{format_dutch_number(total_demand, 0)} mWh</h2>
                <p style='margin: 0;'>Totale Heat Demand (in mWh)</p>
            </div>
        """, unsafe_allow_html=True)


    # Create layers
    base_layer = pdk.Layer(
        "H3HexagonLayer",
        grouped,
        pickable=True,
        filled=True,
        extruded=False,
        get_hexagon="h3_index",
        get_fill_color="color",
        # get_elevation=f"{scenario_column}/100" if extruded else 0,
        # elevation_scale=50 if extruded else 0,
        elevation_range=[0, 1000],
        coverage=1,
        opacity=0.5
    )


    # View state configuration
    view_state = pdk.ViewState(
        latitude=df_clean["latitude"].mean(),
        longitude=df_clean["longitude"].mean(),
        zoom=8.5,
        # pitch=40.5 if extruded else 0,
        bearing=0
    )

    # Render the map
    st.pydeck_chart(pdk.Deck(
        layers=[base_layer],
        initial_view_state=view_state,
        map_style=map_style_url,
        tooltip={
            "html": f"""<b>Scenario:</b> {selected_scenario}<br>
                    <b>Heat Demand (in mWh):</b> {{rounded_value}} mWh<br>
                    <b>Aantal panden:</b> {{aantal_huizen}}""",
            "style": {"backgroundColor": "white", "color": "black"}
        }
    ), height=600)

    # Add the legend as an overlay in the bottom-right corner
    st.markdown(f"""
        </div>
        <div style="
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ddd;
            font-family: Arial, sans-serif;
            font-size: 12px;
            z-index: 10;
            box-shadow: 0px 0px 5px rgba(0,0,0,0.2);
            max-width: 250px;
        ">
            <h4 style="margin-top: 0; font-size: 14px;">Legenda Heat Demand</h4>
            <div><span style="background: #ffffff; width: 15px; height: 15px; display: inline-block;"></span> < 25 mWh</div>
            <div><span style="background: #ffffbf; width: 15px; height: 15px; display: inline-block;"></span> 25 - 100 mWh</div>
            <div><span style="background: #fee08b; width: 15px; height: 15px; display: inline-block;"></span> 100 - 500 mWh</div>
            <div><span style="background: #fdce61; width: 15px; height: 15px; display: inline-block;"></span> 500 - 1.000 mWh</div>
            <div><span style="background: #f46d43; width: 15px; height: 15px; display: inline-block;"></span> 1.000 - 2.000 mWh</div>
            <div><span style="background: #d53e4f; width: 15px; height: 15px; display: inline-block;"></span> 2.000 - 5.000 mWh</div>
            <div><span style="background: #9e0142; width: 15px; height: 15px; display: inline-block;"></span> > 5.000 mWh</div>
        </div>
    """, unsafe_allow_html=True)