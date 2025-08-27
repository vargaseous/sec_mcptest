import asyncio
import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import st_folium
import requests
import json
import redis
import threading
import time

def get_app_state():
    """Get current app state from API server"""
    try:
        response = requests.get("http://localhost:8000/state", timeout=2)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return {"selected_fclasses": [], "map_center": None, "zoom_level": 12}

def update_app_state(state):
    """Update app state via API server"""
    try:
        requests.post("http://localhost:8000/state", json=state, timeout=2)
    except requests.exceptions.RequestException:
        pass

@st.cache_resource
def get_redis_subscription():
    """Get Redis subscriber for state change notifications"""
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        pubsub = redis_client.pubsub()
        pubsub.subscribe("app_state_changes")
        return pubsub
    except redis.RedisError:
        return None


async def poll_for_updates():
    """Check for Redis pub/sub updates and trigger rerun if needed"""
    while True:
        pubsub = get_redis_subscription()

        if pubsub:
            try:
                message = pubsub.get_message(timeout=0.01)  # Non-blocking check
                if message and message["type"] == "message":
                    print("Triggering rerun!")
                    st.rerun()
            except (redis.RedisError, TypeError) as e:
                st.write(f"Redis error: {e}")

        await asyncio.sleep(1)


def main():
    st.header("Singapore Health Facilities Explorer")

    # Load GeoJSON data
    gdf = gpd.read_file("data/health_sg.geojson")
    
    # Get unique 'fclass' values
    fclass_values = gdf['fclass'].unique()
    if len(fclass_values) == 0:
        st.error("No 'fclass' values found.")
        return
    
    # Get current state from API
    current_state = get_app_state()
    
    # Use API state if available, otherwise default to all values
    default_selection = current_state.get("selected_fclasses", [])
    if not default_selection:
        default_selection = list(fclass_values)
    
    selected_fclasses = st.multiselect(
        "Select fclass(es)", 
        fclass_values, 
        default=default_selection,
        key="fclass_selector"
    )
    
    # Update state when selection changes
    if selected_fclasses != current_state.get("selected_fclasses", []):
        new_state = current_state.copy()
        new_state["selected_fclasses"] = selected_fclasses
        update_app_state(new_state)
    
    # Filter GeoDataFrame
    filtered_gdf = gdf[gdf['fclass'].isin(selected_fclasses)]
    
    if filtered_gdf.empty:
        st.warning("No data for selected fclass(es).")
        return
    
    # Determine map center and zoom
    map_center = current_state.get("map_center")
    zoom_level = current_state.get("zoom_level", 12)
    
    if map_center is None:
        map_center = [filtered_gdf.geometry.centroid.y.mean(), filtered_gdf.geometry.centroid.x.mean()]
    
    # Create Folium map
    m = folium.Map(
        location=map_center,
        zoom_start=zoom_level,
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
    
    # Display map and capture interactions
    map_data = st_folium(m, width="100%", height=500, key="folium_map")
    
    # Update map state if user interacted with map
    if map_data and "center" in map_data and map_data["center"]:
        new_center = [map_data["center"]["lat"], map_data["center"]["lng"]]
        new_zoom = map_data.get("zoom", zoom_level)
        
        if (new_center != map_center or new_zoom != zoom_level):
            new_state = current_state.copy()
            new_state["map_center"] = new_center
            new_state["zoom_level"] = new_zoom
            update_app_state(new_state)

    # Poll for updates in redis, this needs to be at the end of the streamlit code
    asyncio.run(poll_for_updates())


if __name__ == "__main__":
    st.set_page_config(
        page_title="Singapore Health Facilities Explorer", layout="wide", page_icon="🏥"
    )
    main()
