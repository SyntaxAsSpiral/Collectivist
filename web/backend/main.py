#!/usr/bin/env python3
"""
Collectivist Web Backend
FastAPI server providing complete REST API for non-terminal users
"""

import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Import our pipeline components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'collectivist-portable' / 'src'))

from pipeline import run_full_pipeline, load_collection_config, get_workflow_config_from_collection
from analyzer import CollectionAnalyzer
from organic import ContentProcessor
from events import EventEmitter, PipelineEvent
from llm import create_client_from_config, test_llm_connection, LLMClient
from config import config_manager, LLMProviderConfig


# Pydantic Models
class CollectionCreate(BaseModel):
    name: str
    path: str
    force_type: Optional[str] = None

class CollectionUpdate(BaseModel):
    name: Optional[str] = None
    categories: Optional[List[str]] = None
    exclude_hidden: Optional[bool] = None
    scanner_config: Optional[Dict[str, Any]] = None

class CollectionResponse(BaseModel):
    id: str
    name: str
    path: str
    collection_type: str
    categories: List[str]
    last_scan: Optional[datetime] = None
    status: str = "idle"  # idle, scanning, describing, error

class PipelineRunRequest(BaseModel):
    skip_analyze: bool = False
    skip_scan: bool = False
    skip_describe: bool = False
    skip_readme: bool = False
    skip_process_new: bool = False
    auto_file: bool = False
    confidence_threshold: float = 0.7
    workflow_mode: str = "manual"

class PipelineRunResponse(BaseModel):
    run_id: str
    status: str
    collection_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

class ScheduleConfig(BaseModel):
    enabled: bool = False
    interval_days: int = 7
    operations: List[str] = ["scan", "describe", "render"]
    auto_file: bool = False
    confidence_threshold: float = 0.8

class LLMConfig(BaseModel):
    provider: str  # openai, anthropic, openrouter, local, etc.
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 2000


# FastAPI App
app = FastAPI(
    title="Collectivist API",
    description="Universal collection indexing system with LLM-powered analysis",
    version="1.0.0"
)

# CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (will be replaced with SQLite later)
collections: Dict[str, Dict[str, Any]] = {}
pipeline_runs: Dict[str, Dict[str, Any]] = {}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # Connection closed, remove it
                self.active_connections.remove(connection)

manager = ConnectionManager()


# Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Collection Management Endpoints
@app.get("/collections", response_model=List[CollectionResponse])
async def list_collections():
    """List all registered collections"""
    return [
        CollectionResponse(
            id=coll_id,
            name=coll_data["name"],
            path=coll_data["path"],
            collection_type=coll_data["collection_type"],
            categories=coll_data["categories"],
            last_scan=coll_data.get("last_scan"),
            status=coll_data.get("status", "idle")
        )
        for coll_id, coll_data in collections.items()
    ]


@app.get("/collections/{collection_id}", response_model=CollectionResponse)
async def get_collection(collection_id: str):
    """Get collection details"""
    if collection_id not in collections:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    coll_data = collections[collection_id]
    return CollectionResponse(
        id=collection_id,
        name=coll_data["name"],
        path=coll_data["path"],
        collection_type=coll_data["collection_type"],
        categories=coll_data["categories"],
        last_scan=coll_data.get("last_scan"),
        status=coll_data.get("status", "idle")
    )


@app.post("/collections", response_model=CollectionResponse)
async def create_collection(collection: CollectionCreate, background_tasks: BackgroundTasks):
    """Register new collection and run analyzer"""
    collection_id = str(uuid.uuid4())
    collection_path = Path(collection.path)
    
    if not collection_path.exists():
        raise HTTPException(status_code=400, detail="Collection path does not exist")
    
    # Store collection info
    collections[collection_id] = {
        "name": collection.name,
        "path": collection.path,
        "collection_type": "unknown",  # Will be determined by analyzer
        "categories": [],
        "status": "analyzing",
        "created_at": datetime.now()
    }
    
    # Run analyzer in background
    background_tasks.add_task(
        run_analyzer_task,
        collection_id,
        collection_path,
        collection.force_type
    )
    
    return CollectionResponse(
        id=collection_id,
        name=collection.name,
        path=collection.path,
        collection_type="unknown",
        categories=[],
        status="analyzing"
    )


@app.put("/collections/{collection_id}", response_model=CollectionResponse)
async def update_collection(collection_id: str, update: CollectionUpdate):
    """Update collection configuration"""
    if collection_id not in collections:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    coll_data = collections[collection_id]
    
    # Update fields
    if update.name is not None:
        coll_data["name"] = update.name
    
    # Update collection.yaml if needed
    if any([update.categories, update.exclude_hidden, update.scanner_config]):
        try:
            collection_path = Path(coll_data["path"])
            config = load_collection_config(collection_path)
            
            if update.categories is not None:
                config["categories"] = update.categories
                coll_data["categories"] = update.categories
            
            if update.exclude_hidden is not None:
                config["exclude_hidden"] = update.exclude_hidden
            
            if update.scanner_config is not None:
                config["scanner_config"] = update.scanner_config
            
            # Save updated config
            import yaml
            config_path = collection_path / 'collection.yaml'
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update collection config: {e}")
    
    return CollectionResponse(
        id=collection_id,
        name=coll_data["name"],
        path=coll_data["path"],
        collection_type=coll_data["collection_type"],
        categories=coll_data["categories"],
        last_scan=coll_data.get("last_scan"),
        status=coll_data.get("status", "idle")
    )


@app.delete("/collections/{collection_id}")
async def delete_collection(collection_id: str):
    """Remove collection from registry"""
    if collection_id not in collections:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    del collections[collection_id]
    return {"message": "Collection deleted successfully"}


# Pipeline Execution Endpoints
@app.post("/collections/{collection_id}/run", response_model=PipelineRunResponse)
async def run_pipeline(
    collection_id: str, 
    run_request: PipelineRunRequest, 
    background_tasks: BackgroundTasks
):
    """Run full pipeline on collection"""
    if collection_id not in collections:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    coll_data = collections[collection_id]
    if coll_data["status"] != "idle":
        raise HTTPException(status_code=409, detail="Collection is already being processed")
    
    # Create run record
    run_id = str(uuid.uuid4())
    run_data = {
        "run_id": run_id,
        "collection_id": collection_id,
        "status": "queued",
        "started_at": datetime.now(),
        "completed_at": None,
        "error": None,
        "request": run_request.dict()
    }
    pipeline_runs[run_id] = run_data
    
    # Update collection status
    collections[collection_id]["status"] = "running"
    
    # Run pipeline in background
    background_tasks.add_task(
        run_pipeline_task,
        run_id,
        collection_id,
        run_request
    )
    
    return PipelineRunResponse(
        run_id=run_id,
        status="queued",
        collection_id=collection_id,
        started_at=run_data["started_at"]
    )


@app.get("/runs/{run_id}", response_model=PipelineRunResponse)
async def get_run_status(run_id: str):
    """Get pipeline run status"""
    if run_id not in pipeline_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    
    run_data = pipeline_runs[run_id]
    return PipelineRunResponse(
        run_id=run_data["run_id"],
        status=run_data["status"],
        collection_id=run_data["collection_id"],
        started_at=run_data["started_at"],
        completed_at=run_data["completed_at"],
        error=run_data["error"]
    )


# Scheduling Endpoints
@app.get("/collections/{collection_id}/schedule", response_model=ScheduleConfig)
async def get_schedule(collection_id: str):
    """Get collection scheduling configuration"""
    if collection_id not in collections:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    try:
        coll_data = collections[collection_id]
        collection_path = Path(coll_data["path"])
        config = load_collection_config(collection_path)
        schedule = config.get("schedule", {})
        
        return ScheduleConfig(
            enabled=schedule.get("enabled", False),
            interval_days=schedule.get("interval_days", 7),
            operations=schedule.get("operations", ["scan", "describe", "render"]),
            auto_file=schedule.get("auto_file", False),
            confidence_threshold=schedule.get("confidence_threshold", 0.8)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load schedule config: {e}")


@app.put("/collections/{collection_id}/schedule")
async def update_schedule(collection_id: str, schedule: ScheduleConfig):
    """Update collection scheduling configuration"""
    if collection_id not in collections:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    try:
        coll_data = collections[collection_id]
        collection_path = Path(coll_data["path"])
        config = load_collection_config(collection_path)
        
        # Update schedule configuration
        config["schedule"] = {
            "enabled": schedule.enabled,
            "interval_days": schedule.interval_days,
            "operations": schedule.operations,
            "auto_file": schedule.auto_file,
            "confidence_threshold": schedule.confidence_threshold
        }
        
        # Save updated config
        import yaml
        config_path = collection_path / 'collection.yaml'
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        return {"message": "Schedule updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update schedule: {e}")


# LLM Configuration Endpoints
@app.get("/config/llm")
async def get_llm_config():
    """Get current LLM provider configuration"""
    return config_manager.get_llm_config()


@app.put("/config/llm")
async def update_llm_config(config: LLMProviderConfig):
    """Update LLM provider configuration"""
    try:
        config_manager.update_llm_config(config)
        return {"message": "LLM configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update LLM config: {e}")


@app.post("/config/llm/test")
async def test_llm_config():
    """Test current LLM configuration"""
    result = config_manager.test_llm_connection()
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.get("/config/llm/providers")
async def get_llm_providers():
    """Get available LLM provider presets"""
    return config_manager.get_provider_presets()


# WebSocket endpoint for real-time events
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Background Tasks
async def run_analyzer_task(collection_id: str, collection_path: Path, force_type: Optional[str]):
    """Background task to run analyzer on collection"""
    try:
        # Create event emitter that broadcasts to WebSocket
        def event_callback(event: PipelineEvent):
            asyncio.create_task(manager.broadcast({
                "type": "pipeline_event",
                "collection_id": collection_id,
                "event": event.to_dict()
            }))
        
        emitter = EventEmitter(callback=event_callback)
        
        # Create LLM client and analyzer
        llm_client = create_client_from_config()
        analyzer = CollectionAnalyzer(llm_client, emitter)
        
        # Run analyzer
        config_path = analyzer.create_collection(collection_path, force_type=force_type)
        
        # Load the generated config
        config = load_collection_config(collection_path)
        
        # Update collection data
        collections[collection_id].update({
            "collection_type": config["collection_type"],
            "categories": config["categories"],
            "status": "idle"
        })
        
        # Broadcast completion
        await manager.broadcast({
            "type": "analyzer_complete",
            "collection_id": collection_id,
            "collection_type": config["collection_type"]
        })
        
    except Exception as e:
        collections[collection_id]["status"] = "error"
        await manager.broadcast({
            "type": "analyzer_error",
            "collection_id": collection_id,
            "error": str(e)
        })


async def run_pipeline_task(run_id: str, collection_id: str, run_request: PipelineRunRequest):
    """Background task to run pipeline"""
    try:
        # Update run status
        pipeline_runs[run_id]["status"] = "running"
        
        # Create event emitter that broadcasts to WebSocket
        def event_callback(event: PipelineEvent):
            asyncio.create_task(manager.broadcast({
                "type": "pipeline_event",
                "run_id": run_id,
                "collection_id": collection_id,
                "event": event.to_dict()
            }))
        
        emitter = EventEmitter(callback=event_callback)
        
        # Get collection path
        coll_data = collections[collection_id]
        collection_path = Path(coll_data["path"])
        
        # Run pipeline
        run_full_pipeline(
            collection_path=collection_path,
            skip_analyze=run_request.skip_analyze,
            skip_scan=run_request.skip_scan,
            skip_describe=run_request.skip_describe,
            skip_readme=run_request.skip_readme,
            skip_process_new=run_request.skip_process_new,
            auto_file=run_request.auto_file,
            confidence_threshold=run_request.confidence_threshold,
            event_emitter=emitter,
            workflow_mode=run_request.workflow_mode
        )
        
        # Update run status
        pipeline_runs[run_id].update({
            "status": "completed",
            "completed_at": datetime.now()
        })
        
        # Update collection status and last scan time
        collections[collection_id].update({
            "status": "idle",
            "last_scan": datetime.now()
        })
        
        # Broadcast completion
        await manager.broadcast({
            "type": "pipeline_complete",
            "run_id": run_id,
            "collection_id": collection_id
        })
        
    except Exception as e:
        # Update run status
        pipeline_runs[run_id].update({
            "status": "failed",
            "completed_at": datetime.now(),
            "error": str(e)
        })
        
        # Update collection status
        collections[collection_id]["status"] = "error"
        
        # Broadcast error
        await manager.broadcast({
            "type": "pipeline_error",
            "run_id": run_id,
            "collection_id": collection_id,
            "error": str(e)
        })


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )