from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import redis
import json
import uvicorn

app = FastAPI(title="Streamlit Health Facilities API")
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class AppState(BaseModel):
    selected_fclasses: List[str]
    map_center: Optional[List[float]] = None
    zoom_level: Optional[int] = 12

class MapUpdate(BaseModel):
    center: List[float]
    zoom: int

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

@app.post("/state")
async def set_state(state: AppState):
    """Set complete app state"""
    try:
        redis_client.set("app_state", state.json())
        return {"status": "success", "state": state.dict()}
    except redis.RedisError:
        raise HTTPException(status_code=500, detail="Redis connection error")

@app.post("/filters")
async def set_filters(fclasses: List[str]):
    """Set selected facility classes"""
    try:
        current_state = await get_state()
        current_state["selected_fclasses"] = fclasses
        redis_client.set("app_state", json.dumps(current_state))
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
        return {"status": "success", "map": map_update.dict()}
    except redis.RedisError:
        raise HTTPException(status_code=500, detail="Redis connection error")

@app.delete("/state")
async def reset_state():
    """Reset app to default state"""
    try:
        redis_client.delete("app_state")
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