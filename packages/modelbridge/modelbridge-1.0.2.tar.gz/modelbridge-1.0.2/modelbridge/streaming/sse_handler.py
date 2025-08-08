"""
Server-Sent Events (SSE) Handler for ModelBridge
Handles Server-Sent Events for streaming responses
"""
import asyncio
import json
import time
import uuid
import logging
from typing import Dict, Any, List, Optional, AsyncIterator, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class SSEEventType(Enum):
    """Server-Sent Events event types"""
    MESSAGE = "message"
    STREAM_START = "stream_start"
    STREAM_CHUNK = "stream_chunk"
    STREAM_END = "stream_end" 
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    METADATA = "metadata"


@dataclass
class SSEEvent:
    """Server-Sent Event structure"""
    event_type: SSEEventType
    data: Any
    event_id: Optional[str] = None
    retry: Optional[int] = None
    timestamp: float = field(default_factory=time.time)
    
    def format_sse(self) -> str:
        """Format as Server-Sent Event string"""
        lines = []
        
        # Add event type
        if self.event_type != SSEEventType.MESSAGE:
            lines.append(f"event: {self.event_type.value}")
        
        # Add event ID
        if self.event_id:
            lines.append(f"id: {self.event_id}")
        
        # Add retry interval
        if self.retry is not None:
            lines.append(f"retry: {self.retry}")
        
        # Add data (can be multi-line)
        if isinstance(self.data, (dict, list)):
            data_str = json.dumps(self.data)
        else:
            data_str = str(self.data)
        
        # Handle multi-line data
        for line in data_str.split('\n'):
            lines.append(f"data: {line}")
        
        # End with double newline
        lines.append("")
        lines.append("")
        
        return "\n".join(lines)


@dataclass
class SSEConnection:
    """SSE connection information"""
    connection_id: str
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    last_event_id: Optional[str] = None
    connected_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    active_streams: set = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "connection_id": self.connection_id,
            "client_ip": self.client_ip,
            "user_agent": self.user_agent,
            "last_event_id": self.last_event_id,
            "connected_at": self.connected_at,
            "last_activity": self.last_activity,
            "active_streams": list(self.active_streams),
            "metadata": self.metadata
        }


class SSEHandler:
    """Server-Sent Events handler for real-time streaming"""
    
    def __init__(self, heartbeat_interval: int = 30):
        self.heartbeat_interval = heartbeat_interval
        self.connections: Dict[str, SSEConnection] = {}
        self.event_queues: Dict[str, asyncio.Queue] = {}
        self.event_handlers: Dict[SSEEventType, List[Callable]] = {}
        
        # Connection callbacks
        self.connection_callbacks: List[Callable] = []
        self.disconnection_callbacks: List[Callable] = []
        
        # Statistics
        self.stats = {
            "total_connections": 0,
            "current_connections": 0,
            "events_sent": 0,
            "heartbeats_sent": 0,
            "errors": 0
        }
        
        # Background tasks
        self._heartbeat_task = None
        self._cleanup_task = None
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background tasks"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        except RuntimeError:
            logger.info("No event loop available for SSE background tasks")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats to all connections"""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                # Send heartbeat to all connections
                for connection_id in list(self.connections.keys()):
                    try:
                        await self.send_event(
                            connection_id,
                            SSEEventType.HEARTBEAT,
                            {"timestamp": time.time()}
                        )
                        self.stats["heartbeats_sent"] += 1
                    except Exception as e:
                        logger.error(f"Heartbeat failed for {connection_id}: {e}")
                        await self.disconnect_client(connection_id)
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
    
    async def _cleanup_loop(self):
        """Clean up stale connections"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                await self._cleanup_stale_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    async def _cleanup_stale_connections(self):
        """Remove stale connections"""
        current_time = time.time()
        stale_threshold = 3600  # 1 hour
        
        stale_connections = []
        for conn_id, connection in self.connections.items():
            if current_time - connection.last_activity > stale_threshold:
                stale_connections.append(conn_id)
        
        for conn_id in stale_connections:
            logger.info(f"Cleaning up stale SSE connection: {conn_id}")
            await self.disconnect_client(conn_id)
    
    async def create_connection(
        self,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        last_event_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new SSE connection"""
        
        connection_id = str(uuid.uuid4())
        
        connection = SSEConnection(
            connection_id=connection_id,
            client_ip=client_ip,
            user_agent=user_agent,
            last_event_id=last_event_id,
            metadata=metadata or {}
        )
        
        self.connections[connection_id] = connection
        self.event_queues[connection_id] = asyncio.Queue()
        
        # Update stats
        self.stats["total_connections"] += 1
        self.stats["current_connections"] = len(self.connections)
        
        # Execute connection callbacks
        for callback in self.connection_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(connection)
                else:
                    callback(connection)
            except Exception as e:
                logger.error(f"SSE connection callback error: {e}")
        
        logger.info(f"SSE connection created: {connection_id}")
        return connection_id
    
    async def disconnect_client(self, connection_id: str):
        """Disconnect SSE client"""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        # Execute disconnection callbacks
        for callback in self.disconnection_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(connection)
                else:
                    callback(connection)
            except Exception as e:
                logger.error(f"SSE disconnection callback error: {e}")
        
        # Cleanup
        del self.connections[connection_id]
        if connection_id in self.event_queues:
            del self.event_queues[connection_id]
        
        # Update stats
        self.stats["current_connections"] = len(self.connections)
        
        logger.info(f"SSE connection disconnected: {connection_id}")
    
    async def get_event_stream(self, connection_id: str) -> AsyncIterator[str]:
        """Get event stream for a connection"""
        if connection_id not in self.connections:
            logger.error(f"SSE connection not found: {connection_id}")
            return
        
        connection = self.connections[connection_id]
        queue = self.event_queues[connection_id]
        
        # Send initial connection event
        welcome_event = SSEEvent(
            event_type=SSEEventType.MESSAGE,
            data={
                "message": "SSE connection established",
                "connection_id": connection_id,
                "server_time": time.time()
            },
            event_id=str(uuid.uuid4())
        )
        
        yield welcome_event.format_sse()
        self.stats["events_sent"] += 1
        
        try:
            # Stream events from queue
            while connection_id in self.connections:
                try:
                    # Wait for next event with timeout
                    event = await asyncio.wait_for(queue.get(), timeout=60.0)
                    
                    if event is None:  # Disconnect signal
                        break
                    
                    connection.last_activity = time.time()
                    yield event.format_sse()
                    self.stats["events_sent"] += 1
                    
                except asyncio.TimeoutError:
                    # Send heartbeat on timeout
                    heartbeat_event = SSEEvent(
                        event_type=SSEEventType.HEARTBEAT,
                        data={"timestamp": time.time()},
                        event_id=str(uuid.uuid4())
                    )
                    yield heartbeat_event.format_sse()
                    self.stats["heartbeats_sent"] += 1
                    
                except Exception as e:
                    logger.error(f"SSE stream error for {connection_id}: {e}")
                    error_event = SSEEvent(
                        event_type=SSEEventType.ERROR,
                        data={"error": str(e)},
                        event_id=str(uuid.uuid4())
                    )
                    yield error_event.format_sse()
                    self.stats["errors"] += 1
                    break
        
        finally:
            # Clean up connection
            await self.disconnect_client(connection_id)
    
    async def send_event(
        self,
        connection_id: str,
        event_type: SSEEventType,
        data: Any,
        event_id: Optional[str] = None,
        retry: Optional[int] = None
    ) -> bool:
        """Send event to a specific connection"""
        
        if connection_id not in self.event_queues:
            return False
        
        event = SSEEvent(
            event_type=event_type,
            data=data,
            event_id=event_id or str(uuid.uuid4()),
            retry=retry
        )
        
        try:
            queue = self.event_queues[connection_id]
            await queue.put(event)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SSE event to {connection_id}: {e}")
            await self.disconnect_client(connection_id)
            return False
    
    async def broadcast_event(
        self,
        event_type: SSEEventType,
        data: Any,
        filter_func: Optional[Callable] = None,
        event_id: Optional[str] = None
    ) -> int:
        """Broadcast event to all connections (optionally filtered)"""
        
        if not event_id:
            event_id = str(uuid.uuid4())
        
        sent_count = 0
        
        for connection_id, connection in self.connections.items():
            if filter_func is None or filter_func(connection):
                if await self.send_event(connection_id, event_type, data, event_id):
                    sent_count += 1
        
        return sent_count
    
    async def send_stream_chunk(
        self,
        connection_id: str,
        stream_id: str,
        chunk_data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send streaming chunk to connection"""
        
        data = {
            "stream_id": stream_id,
            "chunk": chunk_data,
            "timestamp": time.time()
        }
        
        if metadata:
            data["metadata"] = metadata
        
        return await self.send_event(
            connection_id,
            SSEEventType.STREAM_CHUNK,
            data
        )
    
    async def broadcast_stream_chunk(
        self,
        stream_id: str,
        chunk_data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Broadcast streaming chunk to all relevant connections"""
        
        def stream_filter(connection: SSEConnection) -> bool:
            return stream_id in connection.active_streams
        
        data = {
            "stream_id": stream_id,
            "chunk": chunk_data,
            "timestamp": time.time()
        }
        
        if metadata:
            data["metadata"] = metadata
        
        return await self.broadcast_event(
            SSEEventType.STREAM_CHUNK,
            data,
            stream_filter
        )
    
    async def start_stream(
        self,
        connection_id: str,
        stream_id: str,
        stream_metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Start a stream for connection"""
        
        if connection_id not in self.connections:
            return False
        
        connection = self.connections[connection_id]
        connection.active_streams.add(stream_id)
        
        data = {
            "stream_id": stream_id,
            "status": "started",
            "timestamp": time.time()
        }
        
        if stream_metadata:
            data["metadata"] = stream_metadata
        
        return await self.send_event(
            connection_id,
            SSEEventType.STREAM_START,
            data
        )
    
    async def end_stream(
        self,
        connection_id: str,
        stream_id: str,
        reason: str = "completed"
    ) -> bool:
        """End a stream for connection"""
        
        if connection_id not in self.connections:
            return False
        
        connection = self.connections[connection_id]
        connection.active_streams.discard(stream_id)
        
        return await self.send_event(
            connection_id,
            SSEEventType.STREAM_END,
            {
                "stream_id": stream_id,
                "reason": reason,
                "timestamp": time.time()
            }
        )
    
    async def broadcast_stream_end(self, stream_id: str, reason: str = "completed") -> int:
        """Broadcast stream end to all relevant connections"""
        
        sent_count = 0
        
        for connection_id, connection in self.connections.items():
            if stream_id in connection.active_streams:
                if await self.end_stream(connection_id, stream_id, reason):
                    sent_count += 1
        
        return sent_count
    
    def subscribe_to_stream(self, connection_id: str, stream_id: str) -> bool:
        """Subscribe connection to a stream"""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            connection.active_streams.add(stream_id)
            return True
        return False
    
    def unsubscribe_from_stream(self, connection_id: str, stream_id: str) -> bool:
        """Unsubscribe connection from a stream"""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            connection.active_streams.discard(stream_id)
            return True
        return False
    
    def register_event_handler(self, event_type: SSEEventType, handler: Callable):
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def unregister_event_handler(self, event_type: SSEEventType, handler: Callable):
        """Unregister event handler"""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    def register_connection_callback(self, callback: Callable):
        """Register connection callback"""
        self.connection_callbacks.append(callback)
    
    def register_disconnection_callback(self, callback: Callable):
        """Register disconnection callback"""
        self.disconnection_callbacks.append(callback)
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection information"""
        connection = self.connections.get(connection_id)
        return connection.to_dict() if connection else None
    
    def get_all_connections(self) -> List[Dict[str, Any]]:
        """Get all connection information"""
        return [conn.to_dict() for conn in self.connections.values()]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get SSE statistics"""
        current_time = time.time()
        
        # Calculate connection duration stats
        durations = []
        for connection in self.connections.values():
            durations.append(current_time - connection.connected_at)
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            **self.stats,
            "avg_connection_duration": avg_duration,
            "active_streams": sum(len(conn.active_streams) for conn in self.connections.values()),
            "queue_sizes": {
                conn_id: queue.qsize() 
                for conn_id, queue in self.event_queues.items()
            }
        }
    
    async def close_all_connections(self):
        """Close all SSE connections"""
        connection_ids = list(self.connections.keys())
        
        # Send disconnect signal to all queues
        for conn_id in connection_ids:
            if conn_id in self.event_queues:
                try:
                    await self.event_queues[conn_id].put(None)  # Disconnect signal
                except Exception as e:
                    logger.error(f"Error closing connection {conn_id}: {e}")
        
        # Wait a bit for graceful shutdown
        await asyncio.sleep(1.0)
        
        # Force cleanup remaining connections
        for conn_id in connection_ids:
            await self.disconnect_client(conn_id)
    
    def cleanup(self):
        """Cleanup SSE handler"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()