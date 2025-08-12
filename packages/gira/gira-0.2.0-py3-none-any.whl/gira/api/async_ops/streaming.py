"""Progress streaming for real-time updates via WebSocket/SSE."""

import asyncio
import json
import threading
from datetime import datetime
from queue import Queue, Empty
from typing import Any, Dict, List, Optional, Set

from gira.api.async_ops.progress import ProgressCallback, ProgressUpdate


class StreamConnection:
    """Represents a streaming connection."""
    
    def __init__(self, connection_id: str, operation_ids: Optional[Set[str]] = None):
        """Initialize stream connection.
        
        Args:
            connection_id: Unique connection ID
            operation_ids: Set of operation IDs to subscribe to
        """
        self.connection_id = connection_id
        self.operation_ids = operation_ids or set()
        self.queue: Queue[Dict[str, Any]] = Queue()
        self.active = True
    
    def subscribe(self, operation_id: str) -> None:
        """Subscribe to an operation."""
        self.operation_ids.add(operation_id)
    
    def unsubscribe(self, operation_id: str) -> None:
        """Unsubscribe from an operation."""
        self.operation_ids.discard(operation_id)
    
    def send_update(self, update: Dict[str, Any]) -> None:
        """Queue an update for sending."""
        if self.active:
            try:
                self.queue.put_nowait(update)
            except:
                # Queue full, drop update
                pass
    
    def get_update(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Get next update from queue."""
        try:
            return self.queue.get(timeout=timeout)
        except Empty:
            return None
    
    def close(self) -> None:
        """Close the connection."""
        self.active = False


class ProgressStreamer(ProgressCallback):
    """Streams progress updates to connected clients."""
    
    def __init__(self):
        """Initialize progress streamer."""
        self.connections: Dict[str, StreamConnection] = {}
        self._lock = threading.Lock()
    
    def create_connection(
        self,
        connection_id: str,
        operation_ids: Optional[List[str]] = None
    ) -> StreamConnection:
        """Create a new streaming connection.
        
        Args:
            connection_id: Unique connection ID
            operation_ids: Initial operation IDs to subscribe to
            
        Returns:
            Stream connection
        """
        connection = StreamConnection(
            connection_id,
            set(operation_ids) if operation_ids else set()
        )
        
        with self._lock:
            self.connections[connection_id] = connection
        
        # Send initial connection message
        connection.send_update({
            "event": "connection_established",
            "data": {
                "connection_id": connection_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
        return connection
    
    def close_connection(self, connection_id: str) -> None:
        """Close a streaming connection.
        
        Args:
            connection_id: Connection ID to close
        """
        with self._lock:
            connection = self.connections.pop(connection_id, None)
            if connection:
                connection.close()
    
    def subscribe_to_operation(
        self,
        connection_id: str,
        operation_id: str
    ) -> bool:
        """Subscribe a connection to an operation.
        
        Args:
            connection_id: Connection ID
            operation_id: Operation ID to subscribe to
            
        Returns:
            True if subscribed
        """
        with self._lock:
            connection = self.connections.get(connection_id)
            if connection:
                connection.subscribe(operation_id)
                return True
        return False
    
    def unsubscribe_from_operation(
        self,
        connection_id: str,
        operation_id: str
    ) -> bool:
        """Unsubscribe a connection from an operation.
        
        Args:
            connection_id: Connection ID
            operation_id: Operation ID to unsubscribe from
            
        Returns:
            True if unsubscribed
        """
        with self._lock:
            connection = self.connections.get(connection_id)
            if connection:
                connection.unsubscribe(operation_id)
                return True
        return False
    
    def on_progress(self, update: ProgressUpdate) -> None:
        """Handle progress update - send to subscribed connections."""
        message = {
            "event": "progress_update",
            "data": update.to_dict()
        }
        
        self._broadcast_to_subscribers(update.operation_id, message)
    
    def on_step_change(self, operation_id: str, step: str) -> None:
        """Handle step change - send to subscribers."""
        message = {
            "event": "step_change",
            "data": {
                "operation_id": operation_id,
                "step": step,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        self._broadcast_to_subscribers(operation_id, message)
    
    def on_item_complete(self, operation_id: str, item_id: str, success: bool) -> None:
        """Handle item completion - send to subscribers."""
        message = {
            "event": "item_complete",
            "data": {
                "operation_id": operation_id,
                "item_id": item_id,
                "success": success,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        self._broadcast_to_subscribers(operation_id, message)
    
    def on_operation_complete(self, operation_id: str, status: str) -> None:
        """Handle operation completion - send to subscribers."""
        message = {
            "event": "operation_complete",
            "data": {
                "operation_id": operation_id,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        self._broadcast_to_subscribers(operation_id, message)
    
    def _broadcast_to_subscribers(
        self,
        operation_id: str,
        message: Dict[str, Any]
    ) -> None:
        """Broadcast message to all subscribers of an operation."""
        with self._lock:
            for connection in self.connections.values():
                if operation_id in connection.operation_ids:
                    connection.send_update(message)


class SSEStreamer:
    """Server-Sent Events (SSE) streamer."""
    
    def __init__(self, streamer: ProgressStreamer):
        """Initialize SSE streamer.
        
        Args:
            streamer: Progress streamer
        """
        self.streamer = streamer
    
    async def stream_events(
        self,
        connection_id: str,
        operation_ids: Optional[List[str]] = None
    ):
        """Stream events as SSE.
        
        Args:
            connection_id: Connection ID
            operation_ids: Operation IDs to subscribe to
            
        Yields:
            SSE formatted events
        """
        # Create connection
        connection = self.streamer.create_connection(connection_id, operation_ids)
        
        try:
            while connection.active:
                # Get next update
                update = connection.get_update(timeout=30)
                
                if update:
                    # Format as SSE
                    yield f"event: {update.get('event', 'message')}\n"
                    yield f"data: {json.dumps(update.get('data', {}))}\n\n"
                else:
                    # Send heartbeat
                    yield f"event: heartbeat\n"
                    yield f"data: {json.dumps({'timestamp': datetime.utcnow().isoformat()})}\n\n"
                
                # Allow other tasks to run
                await asyncio.sleep(0)
                
        finally:
            # Clean up connection
            self.streamer.close_connection(connection_id)


class WebSocketStreamer:
    """WebSocket streamer for real-time updates."""
    
    def __init__(self, streamer: ProgressStreamer):
        """Initialize WebSocket streamer.
        
        Args:
            streamer: Progress streamer
        """
        self.streamer = streamer
    
    async def handle_connection(self, websocket, path):
        """Handle WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            path: Connection path
        """
        connection_id = str(id(websocket))
        connection = None
        
        try:
            # Create connection
            connection = self.streamer.create_connection(connection_id)
            
            # Send initial connection info
            await websocket.send(json.dumps({
                "type": "connection",
                "connection_id": connection_id
            }))
            
            # Handle messages
            async def receive_messages():
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        await self._handle_message(connection_id, data, websocket)
                    except Exception as e:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": str(e)
                        }))
            
            # Send updates
            async def send_updates():
                while connection.active:
                    update = connection.get_update(timeout=1)
                    if update:
                        await websocket.send(json.dumps(update))
                    else:
                        # Send ping
                        await websocket.ping()
                    
                    await asyncio.sleep(0.1)
            
            # Run both tasks concurrently
            await asyncio.gather(
                receive_messages(),
                send_updates()
            )
            
        finally:
            # Clean up
            if connection:
                self.streamer.close_connection(connection_id)
    
    async def _handle_message(
        self,
        connection_id: str,
        data: Dict[str, Any],
        websocket
    ) -> None:
        """Handle incoming WebSocket message."""
        msg_type = data.get("type")
        
        if msg_type == "subscribe":
            operation_id = data.get("operation_id")
            if operation_id:
                if self.streamer.subscribe_to_operation(connection_id, operation_id):
                    await websocket.send(json.dumps({
                        "type": "subscribed",
                        "operation_id": operation_id
                    }))
        
        elif msg_type == "unsubscribe":
            operation_id = data.get("operation_id")
            if operation_id:
                if self.streamer.unsubscribe_from_operation(connection_id, operation_id):
                    await websocket.send(json.dumps({
                        "type": "unsubscribed",
                        "operation_id": operation_id
                    }))
        
        elif msg_type == "ping":
            await websocket.send(json.dumps({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            }))