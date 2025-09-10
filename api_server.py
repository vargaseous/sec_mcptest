from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import redis
import json
import uvicorn
from pathlib import Path

app = FastAPI(title="Streamlit Health Facilities API")
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
DATA_PATH = (Path(__file__).parent / "data" / "health_sg.geojson").resolve()

def notify_state_change():
    """Publish state change notification to Redis"""
    try:
        redis_client.publish("app_state_changes", "state_updated")
    except redis.RedisError:
        pass  # Don't fail API calls if pub/sub fails

class AppState(BaseModel):
    selected_fclasses: List[str]
    map_center: Optional[List[float]] = None
    zoom_level: Optional[int] = 12

class MapUpdate(BaseModel):
    center: List[float]
    zoom: int

def load_fclasses() -> List[str]:
    """Load available fclass values from GeoJSON data file."""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            gj = json.load(f)
        values = []
        for feat in gj.get("features", []):
            props = feat.get("properties", {}) or {}
            val = props.get("fclass")
            if isinstance(val, str):
                values.append(val)
        # unique, stable order
        seen = set()
        uniq = []
        for v in values:
            if v not in seen:
                seen.add(v)
                uniq.append(v)
        return uniq
    except Exception as e:
        # On failure, return empty list; endpoints will handle as error
        return []

@app.get("/state")
async def get_state():
    """Get current app state"""
    try:
        state_json = redis_client.get("app_state")
        if state_json:
            return json.loads(state_json)
        return {"selected_fclasses": [], "map_center": None, "zoom_level": 12}
    except redis.RedisError:
        raise HTTPException(status_code=500, detail="Redis connection error")

@app.get("/fclasses")
async def get_fclasses():
    """Return the list of available facility classes from the dataset."""
    fclasses = load_fclasses()
    if not fclasses:
        raise HTTPException(status_code=500, detail="Failed to load fclasses from data file")
    return {"fclasses": fclasses}

@app.post("/state")
async def set_state(state: AppState):
    """Set complete app state"""
    try:
        redis_client.set("app_state", state.model_dump_json())
        notify_state_change()
        return {"status": "success", "state": state.model_dump()}
    except redis.RedisError:
        raise HTTPException(status_code=500, detail="Redis connection error")

@app.post("/filters")
async def set_filters(fclasses: List[str]):
    """Set selected facility classes"""
    try:
        current_state = await get_state()
        current_state["selected_fclasses"] = fclasses
        redis_client.set("app_state", json.dumps(current_state))
        notify_state_change()
        return {"status": "success", "selected_fclasses": fclasses}
    except redis.RedisError:
        raise HTTPException(status_code=500, detail="Redis connection error")

@app.post("/map")
async def update_map(map_update: MapUpdate):
    """Update map center and zoom"""
    try:
        current_state = await get_state()
        current_state["map_center"] = map_update.center
        current_state["zoom_level"] = map_update.zoom
        redis_client.set("app_state", json.dumps(current_state))
        notify_state_change()
        return {"status": "success", "map": map_update.model_dump()}
    except redis.RedisError:
        raise HTTPException(status_code=500, detail="Redis connection error")

@app.delete("/state")
async def reset_state():
    """Reset app to default state"""
    try:
        redis_client.delete("app_state")
        notify_state_change()
        return {"status": "success", "message": "State reset to defaults"}
    except redis.RedisError:
        raise HTTPException(status_code=500, detail="Redis connection error")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except redis.RedisError:
        return {"status": "unhealthy", "redis": "disconnected"}

def main():
    """Entry point for uv script"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
