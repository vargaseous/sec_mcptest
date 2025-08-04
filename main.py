import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import st_folium

def main():
    st.header("Singapore Health Facilities Explorer")  # Added header

    # Load GeoJSON data
    gdf = gpd.read_file("data/health_sg.geojson")

    # Get unique 'fclass' values
    fclass_values = gdf['fclass'].unique()
    if len(fclass_values) == 0:
        st.error("No 'fclass' values found.")
        return

    selected_fclasses = st.multiselect("Select fclass(es)", fclass_values, default=list(fclass_values))

    # Filter GeoDataFrame
    filtered_gdf = gdf[gdf['fclass'].isin(selected_fclasses)]

    if filtered_gdf.empty:
        st.warning("No data for selected fclass(es).")
        return

    # Create Folium map based on extent of filtered GeoDataFrame
    m = folium.Map(
        location=[filtered_gdf.geometry.centroid.y.mean(), filtered_gdf.geometry.centroid.x.mean()],
        zoom_start=12,
        tiles="CartoDB positron"
    )

    # Add polygons to the map
    for _, row in filtered_gdf.iterrows():
        folium.GeoJson(
            row['geometry'],
            style_function=lambda x: {
                'fillColor': 'blue',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.5
            },
            tooltip=row['name']
        ).add_to(m)

    st_folium(m, width="100%", height=500)

if __name__ == "__main__":
    main()
