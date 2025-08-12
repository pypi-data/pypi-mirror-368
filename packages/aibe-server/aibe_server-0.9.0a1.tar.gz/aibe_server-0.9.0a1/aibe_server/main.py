"""
FastAPI Browser-AI Interface Server
Direct port from Node.js server.cjs with exact functional parity
Maintains all 25+ endpoints with identical behavior
"""

import os
import sys
import asyncio
import uuid
import uvicorn
import json
import uuid
import time
import asyncio
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, Request, Response, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

# Local imports
from .session_manager import SessionManager
from .models.events import BrowserEvent, EventResponse, EventsListResponse
from .models.commands import ActorCommand, CommandsListRequest, CommandResponse, CommandsListResponse
from .models.sessions import (
    TabIdentity, SessionInfo, SessionStatus, SessionInitResponse, 
    SessionsListResponse, ErrorResponse
)
from .middleware.session_middleware import (
    setup_session_middleware, get_session_from_request, get_session_id_from_request,
    add_event_to_session, clear_all_events, add_actor_command, get_pending_actor_commands,
    get_session_status
)
from .utils.logging import initialize_logger, log, log_debug, log_info, log_warn, log_error, get_log_file
from .utils.process_management import ProcessManager, setup_signal_handlers


# Parse command line arguments (exact match with Node.js)
def parse_args():
    args = sys.argv[1:]
    return {
        'debug': '--debug' in args,
        'detached': '--detached' in args
    }


# Configuration constants (exact match with Node.js)
PORT = 3001
MAX_UNPROCESSED_EVENTS = 50
MAX_PROCESSED_EVENTS = 1000
MAX_COMMANDS_PER_SESSION = 100


# Global variables (minimal initialization for CLI)
app_config = parse_args()
server_dir = Path(__file__).parent.parent
session_manager = None  # Will be initialized when server starts
process_manager = None  # Will be initialized when server starts


# Create FastAPI app (lifespan defined below)
app = FastAPI(
    title="Browser-AI Interface Server", 
    description="HTTP server for browser automation and AI interaction",
    version="0.9.0a1"
)

# Middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Session middleware will be set up when server starts


# Background task for session cleanup
async def cleanup_task():
    """Periodic task to clean up expired sessions"""
    while True:
        try:
            # Run every 5 minutes
            await asyncio.sleep(300)
            
            # Clean up sessions older than 30 minutes without activity
            expired_count = session_manager.cleanup_expired_sessions(
                max_age_ms=30 * 60 * 1000  # 30 minutes
            )
            
            if expired_count > 0:
                log(f"Cleaned up {expired_count} expired sessions")
                
        except Exception as e:
            log(f"Error in cleanup task: {e}")




# Helper functions
def generate_unique_id() -> str:
    """Generate unique ID for commands"""
    return 'cmd_' + str(uuid.uuid4()).replace('-', '')[:12] + '_' + str(int(datetime.now().timestamp() * 1000))


def enrich_command(command: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich command with metadata (exact match with Node.js)"""
    return {
        **command,
        "id": generate_unique_id(),
        "timestamp": datetime.now().isoformat(),
        "queuedAt": datetime.now().isoformat(),
        "status": "queued"
    }


def validate_session_dependency(session_id: str, request: Request):
    """Dependency for session validation"""
    result = session_manager.validate_session(session_id)
    if result["error"]:
        raise HTTPException(
            status_code=404,
            detail={
                "error": result["error"]["message"],
                "availableSessions": result["error"]["availableSessions"]
            }
        )
    return result


# ========================================================================
# SESSION-BASED ENDPOINTS (Primary API)
# ========================================================================

@app.put("/sessions/init", response_model=SessionInitResponse)
async def sessions_init(tab_identity: TabIdentity, request: Request):
    """Initialize new session"""
    try:
        if not tab_identity.tabId or not tab_identity.url:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Missing required fields: tabId and url are required",
                    "received": tab_identity.dict()
                }
            )
        
        log_info(f"Session Init: Registering session {tab_identity.tabId} - {tab_identity.url}")
        
        # Create session data structure in session_store
        session_manager.get_or_create_session(tab_identity.tabId)
        
        # Register session metadata in active_sessions registry
        session_manager.register_session(tab_identity.tabId, {
            "tabId": tab_identity.tabId,
            "url": tab_identity.url,
            "title": tab_identity.title or "Untitled",
            "windowId": tab_identity.windowId,
            "index": tab_identity.index,
            "capabilities": ["observer", "actor"]
        })
        
        return SessionInitResponse(
            success=True,
            sessionId=tab_identity.tabId,
            message=f"Session {tab_identity.tabId} registered successfully"
        )
        
    except HTTPException:
        raise
    except Exception as error:
        log_error(f"Session Init: Error registering session: {error}")
        raise HTTPException(status_code=500, detail={"error": str(error)})


@app.get("/sessions", response_model=List[SessionInfo])
async def sessions_list():
    """List all active sessions"""
    try:
        sessions = session_manager.get_session_registry()
        log(f"Session Discovery: Retrieved {len(sessions)} active sessions")
        return sessions  # Return array directly for Node.js compatibility
    except Exception as error:
        log(f"Session Discovery: Error retrieving sessions: {error}")
        raise HTTPException(status_code=500, detail={"error": str(error)})


@app.post("/sessions/close")
async def sessions_close(request: Request):
    """Close session when tab is closed"""
    try:
        session_id = get_session_id_from_request(request)
        
        if session_manager.has_session(session_id):
            log(f"Explicit close request for session {session_id}")
            session_manager.close_session(session_id)
            return {"success": True, "message": f"Session {session_id} closed"}
        else:
            return {"success": False, "message": f"Session {session_id} not found"}
    except Exception as error:
        log(f"Error closing session: {error}")
        return {"success": False, "error": str(error)}


@app.post("/sessions/{session_id}/heartbeat")
async def sessions_heartbeat(session_id: str, request: Request):
    """Update session activity timestamp"""
    try:
        if session_manager.has_session(session_id):
            session_manager.update_session_activity(session_id)
            log(f"Heartbeat received for session {session_id}", True)  # Log but skip console
            return {"success": True}
        return {"success": False, "error": "Session not found"}
    except Exception as error:
        log(f"Error processing heartbeat for {session_id}: {error}")
        return {"success": False, "error": str(error)}


@app.post("/sessions/{session_id}/events", response_model=EventResponse)
async def sessions_events_post(session_id: str, event: BrowserEvent, request: Request):
    """Submit new browser event to specific session"""
    session_data = validate_session_dependency(session_id, request)
    session = session_data["session"]
    
    try:
        event_data = event.dict()
        if not event_data or not isinstance(event_data, dict):
            raise HTTPException(status_code=400, detail={"error": "Invalid event data"})
        
        # Add timestamp if not present
        if not event_data.get("timestamp"):
            event_data["timestamp"] = datetime.now().isoformat()
        
        # Reduced verbosity - only log important events or errors, not routine processing
        if event_data.get('type') not in ['log', 'screen_status', 'heartbeat']:
            # Only log non-routine event types
            log_debug(f"Session Event [{session_id}]: Processing event type={event_data.get('type')}")
        
        # Add event to session
        add_event_to_session(session, event_data)
        
        # Update session activity
        session_manager.update_session_activity(session_id)
        
        return EventResponse(
            success=True,
            sessionId=session_id,
            message="Event processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as error:
        log_error(f"Session Event Post [{session_id}]: Error posting event: {error}")
        raise HTTPException(status_code=500, detail={"error": str(error)})


@app.get("/sessions/{session_id}/events/recent")
async def sessions_events_recent(session_id: str, request: Request, limit: int = Query(50)):
    """Get recent events for session"""
    session_data = validate_session_dependency(session_id, request)
    session = session_data["session"]
    
    try:
        # Get recent events from both processed and unprocessed
        all_events = session.get("processedEvents", []) + session.get("unprocessedEvents", [])
        events = all_events[-limit:] if limit > 0 else all_events
        
        log(f"Session Events Recent [{session_id}]: Retrieved {len(events)} recent events")
        return events  # Return array directly for Node.js TestingFramework compatibility
        
    except Exception as error:
        log(f"Session Events Recent [{session_id}]: Error retrieving events: {error}")
        raise HTTPException(status_code=500, detail={"error": str(error)})


@app.get("/sessions/{session_id}/events/consume")
async def sessions_events_consume(session_id: str, request: Request):
    """Consume unprocessed events for session (FIFO Queue)"""
    session_data = validate_session_dependency(session_id, request)
    session = session_data["session"]
    
    try:
        # Get events to consume
        events_to_consume = session.get("unprocessedEvents", []).copy()
        
        # Move unprocessed to processed
        session.setdefault("processedEvents", []).extend(session.get("unprocessedEvents", []))
        session["unprocessedEvents"] = []
        
        # Maintain processed events limit
        if len(session["processedEvents"]) > MAX_PROCESSED_EVENTS:
            excess = len(session["processedEvents"]) - MAX_PROCESSED_EVENTS
            session["processedEvents"] = session["processedEvents"][excess:]
        
        # Update session activity
        session_manager.update_session_activity(session_id)
        
        log_debug(f"Session Events Consume [{session_id}]: Consumed {len(events_to_consume)} events, {len(session['processedEvents'])} total processed")
        return events_to_consume  # Return array directly for Node.js TestingFramework compatibility
        
    except Exception as error:
        log_error(f"Session Events Consume [{session_id}]: Error consuming events: {error}")
        raise HTTPException(status_code=500, detail={"error": str(error)})


@app.get("/sessions/{session_id}/events/unprocessed")
async def sessions_events_unprocessed(session_id: str, request: Request):
    """View unprocessed events for session"""
    session_data = validate_session_dependency(session_id, request)
    session = session_data["session"]
    
    try:
        unprocessed_events = session.get("unprocessedEvents", [])
        log(f"Session Events Unprocessed [{session_id}]: Viewing {len(unprocessed_events)} unprocessed events")
        return unprocessed_events  # Return array directly for Node.js TestingFramework compatibility
        
    except Exception as error:
        log(f"Session Events Unprocessed [{session_id}]: Error viewing unprocessed events: {error}")
        raise HTTPException(status_code=500, detail={"error": str(error)})


@app.get("/sessions/{session_id}/events/processed")
async def sessions_events_processed(session_id: str, request: Request, limit: int = Query(50)):
    """View processed events for session"""
    session_data = validate_session_dependency(session_id, request)
    session = session_data["session"]
    
    try:
        processed_events = session.get("processedEvents", [])
        recent_processed = processed_events[-limit:] if limit > 0 else processed_events
        
        log(f"Session Events Processed [{session_id}]: Viewing {len(recent_processed)} processed events")
        return recent_processed  # Return array directly for Node.js TestingFramework compatibility
        
    except Exception as error:
        log(f"Session Events Processed [{session_id}]: Error viewing processed events: {error}")
        raise HTTPException(status_code=500, detail={"error": str(error)})


@app.post("/sessions/{session_id}/actor/send")
async def sessions_actor_send(session_id: str, request: Request):
    """Send Actor command to session"""
    session_data = validate_session_dependency(session_id, request)
    session = session_data["session"]
    
    try:
        # Get raw JSON body to handle both single commands and arrays (matching Node.js)
        input_data = await request.json()
        
        # Handle both single commands and arrays
        if isinstance(input_data, list):
            commands_data = input_data
        else:
            commands_data = [input_data]
        
        log_debug(f"Session Actor [{session_id}]: Queueing {len(commands_data)} commands")
        
        # Validate and enrich commands
        results = []
        for command_data in commands_data:
            if not command_data.get("type"):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "All commands must have a type field",
                        "invalidCommand": command_data
                    }
                )
            
            enriched_command = enrich_command(command_data)
            add_actor_command(session, enriched_command)
            
            log_debug(f"Session Actor [{session_id}]: Queued command {enriched_command['id']} of type {enriched_command['type']}")
            
            results.append({
                "commandId": enriched_command["id"],
                "type": enriched_command["type"],
                "status": "queued"
            })
        
        # Update session activity
        session_manager.update_session_activity(session_id)
        
        return {
            "success": True,
            "sessionId": session_id,
            "commandsQueued": len(results),
            "commands": results,
            "message": f"{len(results)} command(s) queued for session {session_id}"
        }
        
    except HTTPException:
        raise
    except Exception as error:
        log_error(f"Session Actor [{session_id}]: Error queueing commands: {error}")
        raise HTTPException(status_code=400, detail={"error": str(error)})


@app.get("/sessions/{session_id}/actor/commands")
async def sessions_actor_commands(session_id: str, request: Request):
    """Poll Actor commands for session"""
    session_data = validate_session_dependency(session_id, request)
    session = session_data["session"]
    
    try:
        # Get pending commands and clear queue
        commands = get_pending_actor_commands(session)
        
        # Only log when there are commands to report - reduces chattiness
        if commands:
            log(f"Session Commands [{session_id}]: Retrieved {len(commands)} pending commands")
        
        # Update session activity
        session_manager.update_session_activity(session_id)
        
        # Return just the commands array directly to match JS server behavior
        # This is what the extension expects (not an object with a commands property)
        return commands
        
    except Exception as error:
        log(f"Session Commands [{session_id}]: Error retrieving commands: {error}")
        raise HTTPException(status_code=500, detail={"error": str(error)})


@app.get("/sessions/{session_id}/actor/retrieved")
async def sessions_actor_retrieved(session_id: str, request: Request, limit: int = Query(50)):
    """View retrieved Actor commands from specific session"""
    session_data = validate_session_dependency(session_id, request)
    session = session_data["session"]
    
    try:
        retrieved_commands = session.get("retrievedActorCommands", [])
        recent_retrieved = retrieved_commands[-limit:] if limit > 0 else retrieved_commands
        
        session_manager.update_session_activity(session_id)
        
        log(f"Session Actor Retrieved [{session_id}]: Viewing {len(recent_retrieved)} recent retrieved commands (limit: {limit})")
        return {"commands": recent_retrieved, "total": len(recent_retrieved), "sessionId": session_id}
        
    except Exception as error:
        log(f"Session Actor Retrieved [{session_id}]: Error viewing retrieved commands: {error}")
        raise HTTPException(status_code=500, detail={"error": str(error)})


@app.get("/sessions/{session_id}/status", response_model=SessionStatus)
async def sessions_status(session_id: str, request: Request):
    """Get status for specific session"""
    session_data = validate_session_dependency(session_id, request)
    session = session_data["session"]
    session_info = session_data["sessionInfo"]
    
    try:
        status = get_session_status(session)
        status["sessionId"] = session_id
        status["created"] = session.get("created")
        
        # Add session registry info to status (matching Node.js behavior)
        if session_info:
            status["registryInfo"] = {
                "tabId": session_info.get("tabId"),
                "url": session_info.get("url"),
                "title": session_info.get("title"),
                "windowId": session_info.get("windowId"),  
                "index": session_info.get("index"),
                "lastActivity": session_info.get("lastActivity"),
                "capabilities": session_info.get("capabilities", [])
            }
        
        log(f"Session Status [{session_id}]: Status retrieved")
        return status
        
    except Exception as error:
        log(f"Session Status [{session_id}]: Error retrieving status: {error}")
        raise HTTPException(status_code=500, detail={"error": str(error)})


# ========================================================================
# LEGACY ENDPOINTS (Non-session based for backward compatibility)
# ========================================================================

@app.post("/event", response_model=EventResponse)
async def event_post(event: BrowserEvent, request: Request):
    """Submit new browser event (legacy endpoint)"""
    session = get_session_from_request(request)
    session_id = get_session_id_from_request(request)
    
    try:
        event_data = event.dict()
        log(f"app.post/event [{session_id}]: Processing event: type={event_data.get('type')}")
        
        add_event_to_session(session, event_data)
        
        log(f"app.post/event [{session_id}]: Event processed successfully: type={event_data.get('type')}")
        return EventResponse(success=True, sessionId=session_id)
        
    except Exception as error:
        log(f"app.post/event [{session_id}]: Error processing event: {error}")
        raise HTTPException(status_code=400, detail={"error": str(error)})


@app.post("/events/clear")
async def events_clear(request: Request):
    """Clear all stored events (legacy endpoint)"""
    session = get_session_from_request(request)
    session_id = get_session_id_from_request(request)
    
    try:
        log(f"app.post/events/clear [{session_id}]: Clearing all events")
        clear_all_events(session)
        log(f"app.post/events/clear [{session_id}]: Events cleared successfully")
        return {"success": True, "sessionId": session_id}
        
    except Exception as error:
        log(f"app.post/events/clear [{session_id}]: Error clearing events: {error}")
        raise HTTPException(status_code=400, detail={"error": str(error)})


@app.get("/events/recent")
async def events_recent(request: Request, limit: int = Query(50)):
    """Get recent events (legacy endpoint)"""
    session = get_session_from_request(request)
    session_id = get_session_id_from_request(request)
    
    try:
        all_events = session.get("processedEvents", []) + session.get("unprocessedEvents", [])
        events = all_events[-limit:] if limit > 0 else all_events
        
        log(f"app.get/events/recent [{session_id}]: Retrieving {len(events)} recent events")
        return events  # Return array directly for Node.js TestingFramework compatibility
        
    except Exception as error:
        log(f"app.get/events/recent [{session_id}]: Error retrieving events: {error}")
        raise HTTPException(status_code=500, detail={"error": str(error)})


@app.get("/events/unbroadcast")
async def events_unbroadcast(request: Request):
    """Get unbroadcast events (legacy endpoint for compatibility)"""
    session_id = get_session_id_from_request(request)
    log(f"app.get/events/unbroadcast [{session_id}]: Retrieving unbroadcast events data (legacy endpoint)")
    return []  # Legacy endpoint - return empty array for compatibility


# ========================================================================
# ACTOR CHANNEL ENDPOINTS - Commands flowing FROM server TO browser
# ========================================================================

@app.get("/actor/commands")
async def actor_commands(request: Request):
    """Poll for pending Actor commands (legacy endpoint)"""
    session = get_session_from_request(request)
    session_id = get_session_id_from_request(request)
    
    try:
        commands = get_pending_actor_commands(session)
        
        # Only log when commands are actually delivered (reduces polling noise)
        if commands:
            log(f"Actor Commands [{session_id}]: Delivered {len(commands)} commands to browser")
        
        # Return just the commands array directly to match JS server behavior
        # This is what the extension expects (not an object with a commands property)
        log(f"Actor Commands [{session_id}]: Returning commands array directly for extension compatibility")
        return commands
        
    except Exception as error:
        log(f"Actor Commands [{session_id}]: Error retrieving commands: {error}")
        raise HTTPException(status_code=500, detail={"error": str(error)})


@app.post("/actor/send")
async def actor_send(request: Request):
    """Queue new Actor command(s) for browser execution"""
    session = get_session_from_request(request)
    session_id = get_session_id_from_request(request)
    
    try:
        # Get raw JSON body to handle both single commands and arrays (matching Node.js)
        input_data = await request.json()
        
        # Handle both single commands and arrays
        if isinstance(input_data, list):
            commands_data = input_data
        else:
            commands_data = [input_data]
        
        log(f"Actor Send [{session_id}]: Queueing {len(commands_data)} commands")
        
        # Validate and enrich commands
        results = []
        for command_data in commands_data:
            if not command_data.get("type"):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "All commands must have a type field",
                        "invalidCommand": command_data
                    }
                )
            
            enriched_command = enrich_command(command_data)
            add_actor_command(session, enriched_command)
            
            log(f"Actor Send [{session_id}]: Queued command {enriched_command['id']} of type {enriched_command['type']}")
            
            results.append({
                "commandId": enriched_command["id"],
                "type": enriched_command["type"],
                "status": "queued"
            })
        
        return {
            "success": True,
            "commandsQueued": len(results),
            "commands": results,
            "message": f"{len(results)} command(s) queued for browser execution"
        }
        
    except HTTPException:
        raise
    except Exception as error:
        log(f"Actor Send [{session_id}]: Error queueing commands: {error}")
        raise HTTPException(status_code=400, detail={"error": str(error)})


@app.get("/actor/test")
async def actor_test(request: Request):
    """Send test command to verify Actor channel functionality"""
    session = get_session_from_request(request)
    session_id = get_session_id_from_request(request)
    
    try:
        test_command = {
            "type": "test_actor_channel",
            "target": {
                "label": {
                    "control": "Test Element",
                    "control_id": "actor-test"
                }
            },
            "data": {
                "message": "Hello from Actor channel!",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        enriched_command = enrich_command(test_command)
        add_actor_command(session, enriched_command)
        log(f"Actor Test [{session_id}]: Queued test command {enriched_command['id']}")
        
        return {
            "success": True,
            "message": "Test command queued for browser execution",
            "command": enriched_command,
            "instructions": "Check browser console and Observer channel for test command execution"
        }
        
    except Exception as error:
        log(f"Actor Test [{session_id}]: Error creating test command: {error}")
        raise HTTPException(status_code=500, detail={"error": str(error)})


@app.get("/status")
async def status(request: Request):
    """Server status and statistics"""
    session = get_session_from_request(request)
    session_id = get_session_id_from_request(request)
    
    if session:
        # Session-based status (exact match with Node.js)
        session_status = get_session_status(session)
        
        # Get installation location
        import aibe_server
        installation_path = str(Path(aibe_server.__file__).parent.absolute())
        
        status_data = {
            "version": "0.9.0a1",
            "uptime": time.time() - process_manager.start_time,
            
            # Session info
            "sessionId": session_id,
            "sessionBased": True,
            
            # Observer Channel status (session-scoped)
            "eventCount": session_status["eventCount"],
            "unprocessedEventCount": session_status["unprocessedEventCount"],
            "processedEventCount": session_status["processedEventCount"],
            "clientCount": 0,  # No real-time connections
            "lastEventSent": -1,  # Legacy field for compatibility
            "unbroadcastCount": session_status["unprocessedEventCount"],  # Now shows actual unprocessed count
            
            # Actor Channel status (session-scoped)
            "pendingActorCommands": session_status["pendingCommandCount"],
            "maxCommandCapacity": MAX_COMMANDS_PER_SESSION,
            "oldestPendingCommand": session_status["oldestCommand"],
            
            # Server status
            "mode": "DEBUG" if app_config['debug'] else "NORMAL",
            "detached": app_config['detached'],
            "pid": os.getpid(),
            "nodeVersion": sys.version,  # Python version instead of Node version
            "startTime": datetime.fromtimestamp(process_manager.start_time).isoformat(),
            "platform": platform.system(),  # Windows, Linux, Darwin, etc.
            "installationPath": installation_path
        }
    else:
        # Legacy status for requests without session context
        
        # Get installation location
        import aibe_server
        installation_path = str(Path(aibe_server.__file__).parent.absolute())
        
        status_data = {
            "version": "0.9.0a1",
            "uptime": time.time() - process_manager.start_time,
            
            # Server info
            "sessionBased": False,
            "note": "Session-based architecture active - status shown is server-wide only",
            
            # Server status
            "mode": "DEBUG" if app_config['debug'] else "NORMAL",
            "detached": app_config['detached'],
            "pid": os.getpid(),
            "nodeVersion": sys.version,  # Python version instead of Node version
            "startTime": datetime.fromtimestamp(process_manager.start_time).isoformat(),
            "platform": platform.system(),  # Windows, Linux, Darwin, etc.
            "installationPath": installation_path
        }
    
    print(f"app.get/status [{session_id}]: Status retrieved")
    return status_data


@app.get("/api/status")
async def api_status(request: Request):
    """API-style status endpoint"""
    return await status(request)


# ========================================================================
# STATIC FILE ENDPOINTS
# ========================================================================

@app.get("/favicon.svg")
async def favicon():
    """Server favicon"""
    favicon_path = server_dir / "aibe_server" / "static" / "favicon.svg"
    if favicon_path.exists():
        return FileResponse(
            str(favicon_path),
            media_type="image/svg+xml",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    raise HTTPException(status_code=404, detail="Favicon not found")


@app.get("/TestingFramework.js")
async def testing_framework_js():
    """Testing framework JavaScript library"""
    js_path = server_dir / "aibe_server" / "static" / "TestingFramework.js"
    if js_path.exists():
        return FileResponse(
            str(js_path),
            media_type="application/javascript",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    raise HTTPException(status_code=404, detail="TestingFramework.js not found")


@app.get("/GenericElementTest.js")
async def generic_element_test_js():
    """Generic element testing library"""
    js_path = server_dir / "aibe_server" / "static" / "GenericElementTest.js"
    if js_path.exists():
        return FileResponse(
            str(js_path),
            media_type="application/javascript",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    raise HTTPException(status_code=404, detail="GenericElementTest.js not found")


@app.get("/DataDrivenTestRunner.js")
async def data_driven_test_runner_js():
    """Data-driven test runner library"""
    js_path = server_dir / "aibe_server" / "static" / "DataDrivenTestRunner.js"
    if js_path.exists():
        return FileResponse(
            str(js_path),
            media_type="application/javascript",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    raise HTTPException(status_code=404, detail="DataDrivenTestRunner.js not found")


# ========================================================================
# CHROME EXTENSION FILE ENDPOINTS
# ========================================================================

@app.get("/extension/manifest.json")
async def extension_manifest():
    """Chrome extension manifest file"""
    manifest_path = server_dir / "extension" / "manifest.json"
    if manifest_path.exists():
        return FileResponse(
            str(manifest_path),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=manifest.json"}
        )
    raise HTTPException(status_code=404, detail="Extension manifest not found")


@app.get("/extension/content.js")
async def extension_content_js():
    """Chrome extension content script"""
    content_path = server_dir / "extension" / "content.js"
    if content_path.exists():
        return FileResponse(
            str(content_path),
            media_type="application/javascript",
            headers={"Content-Disposition": "attachment; filename=content.js"}
        )
    raise HTTPException(status_code=404, detail="Extension content.js not found")


@app.get("/extension/background.js")
async def extension_background_js():
    """Chrome extension background script"""
    background_path = server_dir / "extension" / "background.js"
    if background_path.exists():
        return FileResponse(
            str(background_path),
            media_type="application/javascript",
            headers={"Content-Disposition": "attachment; filename=background.js"}
        )
    raise HTTPException(status_code=404, detail="Extension background.js not found")


@app.get("/extension/popup.js")
async def extension_popup_js():
    """Chrome extension popup script"""
    popup_js_path = server_dir / "extension" / "popup.js"
    if popup_js_path.exists():
        return FileResponse(
            str(popup_js_path),
            media_type="application/javascript",
            headers={"Content-Disposition": "attachment; filename=popup.js"}
        )
    raise HTTPException(status_code=404, detail="Extension popup.js not found")


@app.get("/extension/popup.html")
async def extension_popup_html():
    """Chrome extension popup HTML"""
    popup_html_path = server_dir / "extension" / "popup.html"
    if popup_html_path.exists():
        return FileResponse(
            str(popup_html_path),
            media_type="text/html",
            headers={"Content-Disposition": "attachment; filename=popup.html"}
        )
    raise HTTPException(status_code=404, detail="Extension popup.html not found")


@app.get("/extension/install")
async def extension_install_guide():
    """Chrome extension installation guide"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>AIBE Chrome Extension Installation</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
        .download-links { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .download-links a { display: inline-block; margin: 10px 15px 10px 0; padding: 8px 16px; 
                           background: #007cba; color: white; text-decoration: none; border-radius: 4px; }
        .download-links a:hover { background: #005a87; }
        ol { line-height: 1.6; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>🤖 AIBE Chrome Extension Installation</h1>
    
    <h2>Step 1: Download Extension Files</h2>
    <div class="download-links">
        <a href="/extension/manifest.json">manifest.json</a>
        <a href="/extension/content.js">content.js</a>
        <a href="/extension/background.js">background.js</a>
        <a href="/extension/popup.js">popup.js</a>
        <a href="/extension/popup.html">popup.html</a>
    </div>
    
    <h2>Step 2: Create Extension Directory</h2>
    <ol>
        <li>Create a new folder on your computer (e.g., <code>aibe-extension</code>)</li>
        <li>Download all 5 files above into this folder</li>
        <li>Make sure all files are in the same directory</li>
    </ol>
    
    <h2>Step 3: Install in Chrome</h2>
    <ol>
        <li>Open Chrome and go to <code>chrome://extensions/</code></li>
        <li>Enable "Developer mode" (toggle in top right corner)</li>
        <li>Click "Load unpacked"</li>
        <li>Select the folder containing your extension files</li>
        <li>The AIBE extension should appear in your extensions list</li>
    </ol>
    
    <h2>Step 4: Verify Installation</h2>
    <p>The extension will automatically connect to this server at <code>localhost:3001</code>. 
    Check the <a href="/status">server status</a> to see connected sessions.</p>
    
    <h2>Troubleshooting</h2>
    <ul>
        <li>Make sure the AIBE server is running on port 3001</li>
        <li>Check that all 5 extension files are in the same directory</li>
        <li>Ensure "Developer mode" is enabled in Chrome extensions</li>
        <li>If the extension doesn't load, check Chrome's extension error messages</li>
    </ul>
    
    <p><a href="/">← Back to Server Home</a></p>
</body>
</html>"""
    return HTMLResponse(content=html_content)


# ========================================================================
# HTML TEST INTERFACE ENDPOINTS
# ========================================================================

@app.get("/test-inputs", response_class=HTMLResponse)
async def test_inputs():
    """Input fields test page"""
    html_path = server_dir / "tests" / "pages" / "test-inputs.html"
    if html_path.exists():
        return FileResponse(str(html_path), media_type="text/html")
    raise HTTPException(status_code=404, detail="test-inputs.html not found")


@app.get("/test-controls", response_class=HTMLResponse) 
async def test_controls():
    """Comprehensive controls test page"""
    html_path = server_dir / "tests" / "pages" / "test-controls.html"
    if html_path.exists():
        return FileResponse(str(html_path), media_type="text/html")
    raise HTTPException(status_code=404, detail="test-controls.html not found")


@app.get("/test-runner", response_class=HTMLResponse)
async def test_runner():
    """Web-based test runner interface"""
    html_path = server_dir / "tests" / "web-runner.html"
    if html_path.exists():
        return FileResponse(str(html_path), media_type="text/html")
    raise HTTPException(status_code=404, detail="test-runner-web.html not found")


@app.get("/TestingFramework.js")
async def testing_framework_js():
    """Testing framework JavaScript library"""
    js_path = server_dir / "tests" / "framework" / "TestingFramework.js"
    if js_path.exists():
        return FileResponse(
            str(js_path),
            media_type="application/javascript",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    raise HTTPException(status_code=404, detail="TestingFramework.js not found")


@app.get("/framework/TestingFramework.js")
async def framework_testing_framework_js():
    """Testing framework JavaScript library (framework path)"""
    js_path = server_dir / "tests" / "framework" / "TestingFramework.js"
    if js_path.exists():
        return FileResponse(
            str(js_path),
            media_type="application/javascript",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    raise HTTPException(status_code=404, detail="TestingFramework.js not found")


@app.get("/DataDrivenTestRunner.js")
async def data_driven_test_runner_js():
    """Data driven test runner JavaScript library"""
    js_path = server_dir / "tests" / "framework" / "DataDrivenTestRunner.js"
    if js_path.exists():
        return FileResponse(
            str(js_path),
            media_type="application/javascript",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    raise HTTPException(status_code=404, detail="DataDrivenTestRunner.js not found")


@app.get("/framework/DataDrivenTestRunner.js")
async def framework_data_driven_test_runner_js():
    """Data driven test runner JavaScript library (framework path)"""
    js_path = server_dir / "tests" / "framework" / "DataDrivenTestRunner.js"
    if js_path.exists():
        return FileResponse(
            str(js_path),
            media_type="application/javascript",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    raise HTTPException(status_code=404, detail="DataDrivenTestRunner.js not found")


@app.get("/GenericElementTest.js")
async def generic_element_test_js():
    """Generic element testing library"""
    js_path = server_dir / "tests" / "framework" / "GenericElementTest.js"
    if js_path.exists():
        return FileResponse(
            str(js_path),
            media_type="application/javascript",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    raise HTTPException(status_code=404, detail="GenericElementTest.js not found")


@app.get("/framework/GenericElementTest.js")
async def framework_generic_element_test_js():
    """Generic element testing library (framework path)"""
    js_path = server_dir / "tests" / "framework" / "GenericElementTest.js"
    if js_path.exists():
        return FileResponse(
            str(js_path),
            media_type="application/javascript",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    raise HTTPException(status_code=404, detail="GenericElementTest.js not found")


@app.get("/test-suites-config")
async def test_suites_config():
    """Test suites configuration data - loaded from JSON file"""
    try:
        # Load complete test suite data from JSON file (proper data/code separation)
        json_path = server_dir / "test-suites.json"
        
        if not json_path.exists():
            log(f"Test Suites Config: JSON file not found at {json_path}")
            raise HTTPException(status_code=404, detail="Test suites configuration file not found")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            test_suites_data = json.load(f)
        
        # Validate that we have the expected structure
        if "TEST_SUITES" not in test_suites_data:
            log("Test Suites Config: Invalid JSON structure - missing TEST_SUITES key")
            raise HTTPException(status_code=500, detail="Invalid test suites configuration format")
        
        suites_count = len(test_suites_data["TEST_SUITES"])
        log(f"Test Suites Config: Serving {suites_count} test suites from JSON file")
        
        return test_suites_data
        
    except FileNotFoundError:
        log("Test Suites Config: Test suites JSON file not found")
        raise HTTPException(status_code=404, detail="Test suites configuration file not found")
    except json.JSONDecodeError as e:
        log(f"Test Suites Config: Invalid JSON format: {e}")
        raise HTTPException(status_code=500, detail="Invalid JSON format in test suites configuration")
    except Exception as error:
        log(f"Test Suites Config: Error loading test suites: {error}")
        raise HTTPException(status_code=500, detail="Failed to load test suites configuration")


@app.get("/test-result", response_class=HTMLResponse)
async def test_result(action: str = Query("unknown")):
    """Test result endpoint for button/link click testing"""
    timestamp = datetime.now().isoformat()
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Result - {action}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
        .result {{ background: #e8f5e8; border: 2px solid #4caf50; border-radius: 8px; padding: 20px; }}
        .action {{ font-size: 24px; font-weight: bold; color: #2e7d32; }}
        .timestamp {{ color: #666; font-size: 14px; }}
        .back-link {{ margin-top: 20px; }}
        .back-link a {{ color: #1976d2; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="result">
        <div class="action">✅ Test Action: {action}</div>
        <div class="timestamp">Timestamp: {timestamp}</div>
        <p>This page confirms that the button/link click was successfully detected and processed.</p>
        <div class="back-link">
            <a href="/test-controls">← Back to Test Controls</a>
        </div>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.get("/sessions/explorer", response_class=HTMLResponse)
async def sessions_explorer():
    """Interactive session exploration interface"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sessions Explorer - Browser-AI Interface</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 1000px; 
            margin: 20px auto; 
            padding: 20px; 
            line-height: 1.6; 
        }
        .header {
            background: linear-gradient(135deg, #e8f5e8 0%, #f0f8ff 100%);
            border: 2px solid #4caf50;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .controls {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #007cba;
        }
        .session-selector {
            margin-bottom: 15px;
        }
        select {
            padding: 8px 12px;
            font-size: 14px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: white;
            min-width: 300px;
        }
        button {
            background-color: #007cba;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin: 2px;
            font-size: 14px;
        }
        button:hover {
            background-color: #005a87;
        }
        button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        .action-buttons {
            margin-top: 10px;
        }
        .results {
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-top: 20px;
            min-height: 200px;
        }
        .results h3 {
            margin-top: 0;
            color: #333;
        }
        .json-data {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 10px;
            font-family: monospace;
            font-size: 12px;
            white-space: pre-wrap;
            overflow-x: auto;
            max-height: 400px;
            overflow-y: auto;
        }
        .error {
            color: #dc3545;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .success {
            color: #155724;
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .loading {
            color: #007cba;
            font-style: italic;
        }
        a {
            color: #007cba;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔗 Sessions Explorer</h1>
        <p><strong>Interactive Browser Session Management</strong></p>
        <p>Explore and manage active browser sessions, view events, send Actor commands, and monitor session state.</p>
        <p><a href="/">← Back to Server Home</a></p>
    </div>

    <div class="controls">
        <div class="session-selector">
            <label for="sessionSelect"><strong>Select Session:</strong></label><br>
            <select id="sessionSelect">
                <option value="">Loading sessions...</option>
            </select>
            <button onclick="refreshSessions()">🔄 Refresh Sessions</button>
        </div>
        
        <div class="action-buttons">
            <strong>Session Actions:</strong><br>
            <button onclick="viewRecentEvents()" disabled id="btn-recent">📡 Recent Events</button>
            <button onclick="viewUnprocessedEvents()" disabled id="btn-unprocessed">📥 Unprocessed Events</button>
            <button onclick="viewProcessedEvents()" disabled id="btn-processed">📤 Processed Events</button>
            <button onclick="consumeEvents()" disabled id="btn-consume">🍽️ Consume Events</button>
            <button onclick="viewActorCommands()" disabled id="btn-actor-commands">🎯 Pending Actor Commands</button>
            <button onclick="viewActorRetrieved()" disabled id="btn-actor-retrieved">📜 Retrieved Actor Commands</button>
            <button onclick="viewActorSummary()" disabled id="btn-actor-summary">📊 Actor Command Status</button>
            <button onclick="viewSessionStatus()" disabled id="btn-status">📋 Session Status</button>
        </div>
    </div>

    <div class="results" id="results">
        <h3>Results</h3>
        <p>Select a session and choose an action to explore session data.</p>
    </div>

    <script>
        let currentSessionId = null;
        
        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            refreshSessions();
            
            // Set up session selector change handler
            document.getElementById('sessionSelect').addEventListener('change', function() {
                currentSessionId = this.value;
                updateButtonStates();
                clearResults();
            });
        });
        
        function updateButtonStates() {
            const hasSession = currentSessionId && currentSessionId !== '';
            const buttons = ['btn-recent', 'btn-unprocessed', 'btn-processed', 'btn-consume', 'btn-actor-commands', 'btn-actor-retrieved', 'btn-actor-summary', 'btn-status'];
            buttons.forEach(id => {
                const btn = document.getElementById(id);
                if (btn) btn.disabled = !hasSession;
            });
        }
        
        function clearResults() {
            document.getElementById('results').innerHTML = '<h3>Results</h3><p>Select a session and choose an action to explore session data.</p>';
        }
        
        function showLoading(message = 'Loading...') {
            document.getElementById('results').innerHTML = `<h3>Results</h3><p class="loading">${message}</p>`;
        }
        
        function showError(message) {
            document.getElementById('results').innerHTML = `<h3>Results</h3><div class="error">❌ Error: ${message}</div>`;
        }
        
        function showSuccess(title, data) {
            let content = `<h3>${title}</h3>`;
            if (typeof data === 'object') {
                content += `<div class="json-data">${JSON.stringify(data, null, 2)}</div>`;
            } else {
                content += `<div class="success">${data}</div>`;
            }
            document.getElementById('results').innerHTML = content;
        }
        
        async function refreshSessions() {
            showLoading('Refreshing sessions...');
            try {
                const response = await fetch('/sessions');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const sessionsResponse = await response.json();
                const sessions = sessionsResponse.sessions || sessionsResponse; // Handle both response formats
                
                const select = document.getElementById('sessionSelect'); 
                select.innerHTML = '<option value="">-- Select a session --</option>';
                
                if (!sessions || sessions.length === 0) {
                    select.innerHTML += '<option value="" disabled>No active sessions found</option>';
                    showError('No active browser sessions found. Make sure the Chrome extension is loaded and browse to localhost:3001 in a tab.');
                } else {
                    sessions.forEach(session => {
                        const option = document.createElement('option');
                        option.value = session.sessionId || session.tabId;
                        // Handle different possible session data structures
                        const url = session.tabInfo?.url || session.url || 'Unknown URL';
                        const sessionId = session.sessionId || session.tabId;
                        option.textContent = `${sessionId} (${url})`;
                        select.appendChild(option);
                    });
                    showSuccess('Sessions Loaded', `Found ${sessions.length} active session(s). Select one to explore.`);
                }
                
                currentSessionId = null;
                updateButtonStates();
                
            } catch (error) {
                showError(`Failed to load sessions: ${error.message}`);
                console.error('Session refresh error:', error);
            }
        }
        
        async function makeSessionRequest(endpoint, action) {
            if (!currentSessionId) {
                showError('No session selected');
                return;
            }
            
            showLoading(`${action}...`);
            try {
                const url = `/sessions/${currentSessionId}${endpoint}`;
                const response = await fetch(url);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                showSuccess(action, data);
                
            } catch (error) {
                showError(`${action} failed: ${error.message}`);
                console.error(`${action} error:`, error);
            }
        }
        
        function viewRecentEvents() {
            makeSessionRequest('/events/recent?limit=20', 'Recent Events (Last 20)');
        }
        
        function viewUnprocessedEvents() {
            makeSessionRequest('/events/unprocessed', 'Unprocessed Events');
        }
        
        function viewProcessedEvents() {
            makeSessionRequest('/events/processed?limit=20', 'Processed Events (Last 20)');
        }
        
        function consumeEvents() {
            makeSessionRequest('/events/consume', 'Consume Events (FIFO)');
        }
        
        function viewActorCommands() {
            makeSessionRequest('/actor/commands', 'Pending Actor Commands');
        }
        
        function viewActorRetrieved() {
            makeSessionRequest('/actor/retrieved', 'Retrieved Actor Commands');
        }
        
        function viewActorSummary() {
            if (!currentSessionId) {
                showError('No session selected');
                return;
            }
            
            showLoading('Loading Actor command status...');
            
            // Fetch both pending and retrieved commands to create a summary
            Promise.all([
                fetch(`/sessions/${currentSessionId}/actor/commands`),
                fetch(`/sessions/${currentSessionId}/actor/retrieved`)
            ])
            .then(responses => {
                if (!responses[0].ok || !responses[1].ok) {
                    throw new Error('Failed to retrieve Actor command data');
                }
                return Promise.all(responses.map(r => r.json()));
            })
            .then(([pendingData, retrievedData]) => {
                // For pending commands, we get a direct array from our endpoint now
                const pendingCommands = Array.isArray(pendingData) ? pendingData : [];
                
                // For retrieved commands, we get an object with a commands property
                const retrievedCommands = retrievedData.commands || [];
                
                // Create a summary object
                const summary = {
                    pending: {
                        count: pendingCommands.length,
                        commands: pendingCommands.map(cmd => ({
                            id: cmd.id,
                            type: cmd.type,
                            timestamp: cmd.timestamp
                        }))
                    },
                    retrieved: {
                        count: retrievedCommands.length,
                        recentCommands: retrievedCommands.slice(-5).map(cmd => ({
                            id: cmd.id,
                            type: cmd.type,
                            timestamp: cmd.timestamp
                        }))
                    },
                    sessionId: currentSessionId,
                    status: pendingCommands.length > 0 ? 'Active' : 'Idle'
                };
                
                showSuccess('Actor Command Status Summary', summary);
            })
            .catch(error => {
                showError(`Failed to create Actor command summary: ${error.message}`);
                console.error('Actor summary error:', error);
            });
        }
        
        function viewSessionStatus() {
            makeSessionRequest('/status', 'Session Status');
        }
    </script>

</body>
</html>"""
    return HTMLResponse(content=html_content)


# ========================================================================
# ROOT ENDPOINT - Server documentation
# ========================================================================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Server help page and documentation"""
    try:
        # Get server status for display
        status_response = await status(request)
        
        # Generate endpoint listing organized by categories (matching Node.js)
        endpoints_html = """
        <h3>📡 Observer Channel (Browser → Server)</h3>
        <div class="endpoint-line"><span class="method">POST</span> <code>/event</code> - Submit new browser event</div>
        <div class="endpoint-line"><span class="method">GET</span> <code>/sessions/:sessionId/events/recent</code> - Recent events for specific session</div>
        <div class="endpoint-line"><span class="method">GET</span> <a href="/events/unbroadcast"><code>/events/unbroadcast</code></a> - Unbroadcast events (legacy)</div>
        <div class="endpoint-line"><span class="method">POST</span> <code>/events/clear</code> - Clear all stored events</div>

        <h3>🎯 Actor Channel (Server → Browser)</h3>
        <div class="endpoint-line"><span class="method">GET</span> <code>/actor/commands</code> - Poll for pending Actor commands</div>
        <div class="endpoint-line"><span class="method">POST</span> <code>/actor/send</code> - Queue new Actor command</div>
        <div class="endpoint-line"><span class="method">GET</span> <a href="/actor/test"><code>/actor/test</code></a> - Test Actor channel functionality</div>

        <h3>📊 Server Status & Control</h3>
        <div class="endpoint-line"><span class="method">GET</span> <a href="/status"><code>/status</code></a> - Server status and statistics</div>
        <div class="endpoint-line"><span class="method">GET</span> <a href="/api/status"><code>/api/status</code></a> - Server status (API format)</div>
        <div class="endpoint-line"><span class="method">GET</span> <a href="/"><code>/</code></a> - Server help page and documentation</div>

        <h3>🧪 Development & Testing</h3>
        <div class="endpoint-line"><span class="method">GET</span> <a href="/test-inputs"><code>/test-inputs</code></a> - Input fields test page</div>
        <div class="endpoint-line"><span class="method">GET</span> <a href="/test-controls"><code>/test-controls</code></a> - Comprehensive controls test page</div>
        <div class="endpoint-line"><span class="method">GET</span> <a href="/test-runner"><code>/test-runner</code></a> - Web-based test runner interface</div>
        <div class="endpoint-line"><span class="method">GET</span> <a href="/test-suites-config"><code>/test-suites-config</code></a> - Test suites configuration data</div>

        <h3>🔗 Session Management</h3>
        <div class="endpoint-line"><span class="method">PUT</span> <code>/sessions/init</code> - Initialize new session</div>
        <div class="endpoint-line"><span class="method">GET</span> <a href="/sessions"><code>/sessions</code></a> - List all active sessions (JSON)</div>
        <div class="endpoint-line"><span class="method">GET</span> <a href="/sessions/explorer"><code>/sessions/explorer</code></a> - Interactive session exploration</div>
        <div class="endpoint-line"><span class="method">POST</span> <code>/sessions/:sessionId/events</code> - Submit event to specific session</div>
        <div class="endpoint-line"><span class="method">GET</span> <code>/sessions/:sessionId/events/recent</code> - Recent events for session</div>
        <div class="endpoint-line"><span class="method">GET</span> <code>/sessions/:sessionId/events/consume</code> - Consume unprocessed events (FIFO)</div>
        <div class="endpoint-line"><span class="method">GET</span> <code>/sessions/:sessionId/events/unprocessed</code> - View unprocessed events</div>
        <div class="endpoint-line"><span class="method">GET</span> <code>/sessions/:sessionId/events/processed</code> - View processed events</div>
        <div class="endpoint-line"><span class="method">POST</span> <code>/sessions/:sessionId/actor/send</code> - Send Actor command to session</div>
        <div class="endpoint-line"><span class="method">GET</span> <code>/sessions/:sessionId/actor/commands</code> - Poll Actor commands for session</div>
        <div class="endpoint-line"><span class="method">GET</span> <code>/sessions/:sessionId/actor/retrieved</code> - View retrieved Actor commands</div>
        <div class="endpoint-line"><span class="method">GET</span> <code>/sessions/:sessionId/status</code> - Status for specific session</div>

        <h3>📄 Static Resources</h3>
        <div class="endpoint-line"><span class="method">GET</span> <a href="/favicon.svg"><code>/favicon.svg</code></a> - Server favicon</div>
        <div class="endpoint-line"><span class="method">GET</span> <a href="/TestingFramework.js"><code>/TestingFramework.js</code></a> - TestingFramework.js library</div>
        <div class="endpoint-line"><span class="method">GET</span> <a href="/GenericElementTest.js"><code>/GenericElementTest.js</code></a> - GenericElementTest.js library</div>
        <div class="endpoint-line"><span class="method">GET</span> <a href="/DataDrivenTestRunner.js"><code>/DataDrivenTestRunner.js</code></a> - DataDrivenTestRunner.js library</div>
        """
        
        # Extract status information for display
        uptime = int(status_response.get("uptime", 0))
        event_count = status_response.get("eventCount", 0)
        pending_commands = status_response.get("pendingActorCommands", 0)
        mode = status_response.get("mode", "NORMAL")
        installation_path = status_response.get("installationPath", "Unknown")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Browser-AI Interface Server</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            max-width: 900px; 
            margin: 20px auto; 
            padding: 20px; 
            line-height: 1.4; 
        }}
        .status {{ 
            background-color: #e8f5e8; 
            padding: 15px; 
            border-radius: 5px; 
            margin-bottom: 25px; 
            border-left: 4px solid #4caf50;
        }}
        .endpoint-line {{ 
            padding: 4px 0; 
            font-family: monospace;
            font-size: 14px;
        }}
        .method {{ 
            font-weight: bold; 
            color: #007cba; 
            width: 50px;
            display: inline-block;
        }}
        code {{ 
            background-color: #f0f0f0; 
            padding: 2px 4px; 
            border-radius: 3px; 
        }}
        a {{ 
            color: #007cba; 
            text-decoration: none; 
        }}
        a:hover {{ 
            text-decoration: underline; 
        }}
        h3 {{
            color: #333;
            margin-top: 25px;
            margin-bottom: 10px;
        }}
        .quick-links {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #007cba;
        }}
    </style>
</head>
<body>
    <h1>🤖 Browser-AI Interface Server</h1>
    
    <div class="status">
        <strong>Status:</strong> Running ✅ | 
        <strong>Version:</strong> 0.9.0a1 | 
        <strong>Uptime:</strong> {uptime}s | 
        <strong>Events:</strong> {event_count} | 
        <strong>Pending Commands:</strong> {pending_commands} | 
        <strong>Mode:</strong> {mode} |
        <strong>Python Implementation:</strong> Full Node.js Parity<br>
        <strong>Installation:</strong> {installation_path}
    </div>
    
    <div class="quick-links">
        <strong>🚀 Quick Links:</strong>
        <a href="/sessions/explorer">Sessions Explorer</a> | 
        <a href="/test-runner">Unified Test Runner</a>
    </div>

    <h2>📋 API Endpoints</h2>
{endpoints_html}
    
    <h2>💡 Quick Start</h2>
    <ul>
        <li>Install the Chrome extension</li>
        <li>Use <strong><a href="/sessions/explorer">Sessions Explorer</a></strong> to interact with browser sessions</li>
        <li>Use the <a href="/test-runner">unified test runner</a> for automated validation</li>
        <li>Monitor events via <a href="/sessions/explorer">Sessions Explorer</a> for session-specific data</li>
    </ul>

</body>
</html>"""
        
        return HTMLResponse(content=html_content)
        
    except Exception as error:
        log(f"Root endpoint error: {error}")
        # Fallback simple version if status fails
        simple_html = """
<!DOCTYPE html>
<html>
<head><title>Browser-AI Interface Server</title></head>
<body>
    <h1>🤖 Browser-AI Interface Server</h1>
    <p><strong>Status:</strong> Running (Python Implementation)</p>
    <p><a href="/status">View Status</a> | <a href="/sessions/explorer">Sessions Explorer</a> | <a href="/test-runner">Test Runner</a></p>
</body>
</html>"""
        return HTMLResponse(content=simple_html)


# ========================================================================
# APPLICATION LIFECYCLE
# ========================================================================

def run_server():
    """Run the server with uvicorn"""
    global session_manager, process_manager
    
    # Initialize server components when actually starting server
    session_manager = SessionManager()
    process_manager = ProcessManager(str(server_dir), app_config['detached'])
    
    # Set up session middleware now that session_manager is initialized
    session_middleware = setup_session_middleware(session_manager)
    app.middleware("http")(session_middleware)
    
    # Initialize logging
    initialize_logger(str(server_dir), app_config['detached'])
    
    # Startup logging (exact match with Node.js)
    log("main.py: === NEW SERVER SESSION STARTED ===", True)
    log("main.py: Starting Browser-AI Interface Server...", True)
    log(f"main.py: Mode: {'DEBUG' if app_config['debug'] else 'NORMAL'}", True)
    log(f"main.py: Detached: {'YES' if app_config['detached'] else 'NO'}", True)
    log(f"main.py: Working directory: {os.getcwd()}", True)
    log(f"main.py: Python version: {sys.version}", True)
    log(f"main.py: PID: {os.getpid()}", True)

    print("main.py: === NEW SERVER SESSION STARTED ===")
    print("main.py: Starting Browser-AI Interface Server...")
    print(f"main.py: Mode: {'DEBUG' if app_config['debug'] else 'NORMAL'}")
    print(f"main.py: Detached: {'YES' if app_config['detached'] else 'NO'}")
    print(f"main.py: Working directory: {os.getcwd()}")
    print(f"main.py: Python version: {sys.version}")
    print(f"main.py: PID: {os.getpid()}")
    
    # Check for existing server and save PID
    process_manager.check_existing_server()
    process_manager.save_pid()
    
    # Get installation location
    import aibe_server
    installation_path = Path(aibe_server.__file__).parent.absolute()
    
    log(f"Starting server on port {PORT}")
    print(f"Starting server on port {PORT}")
    print(f"Installation location: {installation_path}")
    log(f"Installation location: {installation_path}")
    
    # Set up signal handlers now that we're ready to start the server
    setup_signal_handlers(process_manager)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info" if app_config['debug'] else "warning"
    )


def main():
    """Main CLI entry point with subcommand support"""
    import argparse
    import sys
    import os
    import subprocess
    import requests
    import json
    import platform
    import time
    from datetime import datetime
    
    # Import server manager functions
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    try:
        from server_manager import start_server, stop_server, restart_server, status_command, get_server_status
        server_manager_available = True
    except ImportError:
        server_manager_available = False
    
    parser = argparse.ArgumentParser(
        description="AI Browser Extension Interface Server",
        prog="aibe-server"
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar='{run,start,stop,restart,status}'
    )
    
    # 'run' command (start server)
    run_parser = subparsers.add_parser('run', help='Start the server in foreground')
    run_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # 'start' command - always background
    start_parser = subparsers.add_parser('start', help='Start the server in background')
    start_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # 'stop' command
    stop_parser = subparsers.add_parser('stop', help='Stop the running server')
    
    # 'restart' command  
    restart_parser = subparsers.add_parser('restart', help='Restart the server')
    restart_parser.add_argument('--detached', action='store_true', help='Run in background after restart')
    restart_parser.add_argument('--debug', action='store_true', help='Enable debug mode after restart')
    
    # 'status' command
    status_parser = subparsers.add_parser('status', help='Check server status')
    
    args = parser.parse_args()
    
    # If no command provided, show help
    if not args.command:
        parser.print_help()
        return
    
    # Handle commands
    if args.command == 'run':
        # Foreground mode - set debug if requested
        if hasattr(args, 'debug') and args.debug:
            app_config['debug'] = True
        # Always run directly in foreground
        run_server()
        
    elif args.command == 'start':
        # Background mode - set debug if requested
        if hasattr(args, 'debug') and args.debug:
            app_config['debug'] = True
        # Use server_manager for background startup
        if server_manager_available:
            success = start_server()
            sys.exit(0 if success else 1)
        else:
            print("Error: Background startup not available - use 'run' command instead")
            sys.exit(1)
            
    elif args.command == 'stop':
        if server_manager_available:
            success = stop_server()
            sys.exit(0 if success else 1)
        else:
            print("Error: Server management not available. Kill the process manually.")
            sys.exit(1)
            
    elif args.command == 'restart':
        if server_manager_available:
            # Set debug config if requested
            if hasattr(args, 'debug') and args.debug:
                app_config['debug'] = True
                
            success = restart_server()
            sys.exit(0 if success else 1)
        else:
            print("Error: Server management not available.")
            sys.exit(1)
            
if __name__ == "__main__":
    run_server()