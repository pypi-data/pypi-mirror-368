"""
WebSocket Handler for ModelBridge
Handles real-time WebSocket connections for streaming
"""
import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class WebSocketEventType(Enum):
    """WebSocket event types"""
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    MESSAGE = "message"
    STREAM_START = "stream_start"
    STREAM_CHUNK = "stream_chunk"
    STREAM_END = "stream_end"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"


@dataclass
class WebSocketConnection:
    """WebSocket connection information"""
    connection_id: str
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    connected_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    subscriptions: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    active_streams: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "connection_id": self.connection_id,
            "client_ip": self.client_ip,
            "user_agent": self.user_agent,
            "connected_at": self.connected_at,
            "last_activity": self.last_activity,
            "subscriptions": list(self.subscriptions),
            "metadata": self.metadata,
            "active_streams": list(self.active_streams)
        }


@dataclass 
class WebSocketMessage:
    """WebSocket message structure"""
    message_id: str
    event_type: WebSocketEventType
    data: Any
    timestamp: float = field(default_factory=time.time)
    connection_id: Optional[str] = None
    stream_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "message_id": self.message_id,
            "event_type": self.event_type.value,
            "data": self.data,
            "timestamp": self.timestamp,
            "connection_id": self.connection_id,
            "stream_id": self.stream_id
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WebSocketMessage':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls(
            message_id=data.get("message_id", str(uuid.uuid4())),
            event_type=WebSocketEventType(data.get("event_type", "message")),
            data=data.get("data"),
            timestamp=data.get("timestamp", time.time()),
            connection_id=data.get("connection_id"),
            stream_id=data.get("stream_id")
        )


class WebSocketHandler:
    """WebSocket handler for real-time streaming"""
    
    def __init__(self, max_connections: int = 1000):
        self.max_connections = max_connections
        self.connections: Dict[str, WebSocketConnection] = {}
        self.websocket_objects: Dict[str, Any] = {}  # Store actual WebSocket objects
        self.message_handlers: Dict[WebSocketEventType, List[Callable]] = {}
        self.connection_callbacks: List[Callable] = []
        self.disconnection_callbacks: List[Callable] = []
        
        # Statistics
        self.stats = {
            "total_connections": 0,
            "current_connections": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "streams_active": 0,
            "errors": 0
        }
        
        # Start cleanup task
        self._cleanup_task = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background cleanup task"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
        except RuntimeError:
            logger.info("No event loop available for WebSocket cleanup task")
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of stale connections"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self._cleanup_stale_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"WebSocket cleanup error: {e}")
    
    async def _cleanup_stale_connections(self):
        """Clean up stale connections"""
        current_time = time.time()
        stale_threshold = 3600  # 1 hour
        
        stale_connections = []
        for conn_id, connection in self.connections.items():
            if current_time - connection.last_activity > stale_threshold:
                stale_connections.append(conn_id)
        
        for conn_id in stale_connections:
            logger.info(f"Cleaning up stale connection: {conn_id}")
            await self.disconnect_client(conn_id)
    
    async def connect_client(
        self, 
        websocket: Any, 
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Handle new WebSocket connection"""
        
        # Check connection limit
        if len(self.connections) >= self.max_connections:
            logger.warning("WebSocket connection limit reached")
            raise Exception("Connection limit exceeded")
        
        connection_id = str(uuid.uuid4())
        
        connection = WebSocketConnection(
            connection_id=connection_id,
            client_ip=client_ip,
            user_agent=user_agent,
            metadata=metadata or {}
        )
        
        self.connections[connection_id] = connection
        self.websocket_objects[connection_id] = websocket
        
        # Update stats
        self.stats["total_connections"] += 1
        self.stats["current_connections"] = len(self.connections)
        
        # Send connection confirmation
        welcome_message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            event_type=WebSocketEventType.CONNECT,
            data={
                "connection_id": connection_id,
                "server_time": time.time(),
                "message": "Connected to ModelBridge WebSocket"
            },
            connection_id=connection_id
        )
        
        await self._send_message_to_connection(connection_id, welcome_message)
        
        # Execute connection callbacks
        for callback in self.connection_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(connection)
                else:
                    callback(connection)
            except Exception as e:
                logger.error(f"Connection callback error: {e}")
        
        logger.info(f"WebSocket client connected: {connection_id}")
        return connection_id
    
    async def disconnect_client(self, connection_id: str):
        """Handle WebSocket disconnection"""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        # Clean up active streams
        for stream_id in list(connection.active_streams):
            await self._cleanup_stream(connection_id, stream_id)
        
        # Execute disconnection callbacks
        for callback in self.disconnection_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(connection)
                else:
                    callback(connection)
            except Exception as e:
                logger.error(f"Disconnection callback error: {e}")
        
        # Remove connection
        del self.connections[connection_id]
        if connection_id in self.websocket_objects:
            del self.websocket_objects[connection_id]
        
        # Update stats
        self.stats["current_connections"] = len(self.connections)
        
        logger.info(f"WebSocket client disconnected: {connection_id}")
    
    async def handle_message(self, connection_id: str, message_data: str):
        """Handle incoming WebSocket message"""
        if connection_id not in self.connections:
            logger.warning(f"Message from unknown connection: {connection_id}")
            return
        
        connection = self.connections[connection_id]
        connection.last_activity = time.time()
        
        try:
            message = WebSocketMessage.from_json(message_data)
            message.connection_id = connection_id
            
            self.stats["messages_received"] += 1
            
            # Handle built-in message types
            if message.event_type == WebSocketEventType.PING:
                await self._handle_ping(connection_id, message)
            elif message.event_type == WebSocketEventType.STREAM_START:
                await self._handle_stream_start(connection_id, message)
            else:
                # Execute registered handlers
                handlers = self.message_handlers.get(message.event_type, [])
                for handler in handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(connection_id, message)
                        else:
                            handler(connection_id, message)
                    except Exception as e:
                        logger.error(f"Message handler error: {e}")
                        await self._send_error(connection_id, f"Handler error: {e}")
        
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self._send_error(connection_id, f"Message processing error: {e}")
    
    async def _handle_ping(self, connection_id: str, message: WebSocketMessage):
        """Handle ping message"""
        pong_message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            event_type=WebSocketEventType.PONG,
            data={"ping_id": message.data.get("ping_id", "unknown")},
            connection_id=connection_id
        )
        await self._send_message_to_connection(connection_id, pong_message)
    
    async def _handle_stream_start(self, connection_id: str, message: WebSocketMessage):
        """Handle stream start request"""
        try:
            stream_data = message.data
            stream_id = stream_data.get("stream_id", str(uuid.uuid4()))
            
            connection = self.connections[connection_id]
            connection.active_streams.add(stream_id)
            
            # Start the stream (this would integrate with StreamingHandler)
            response_message = WebSocketMessage(
                message_id=str(uuid.uuid4()),
                event_type=WebSocketEventType.STREAM_START,
                data={
                    "stream_id": stream_id,
                    "status": "started",
                    "message": "Stream initiated"
                },
                connection_id=connection_id,
                stream_id=stream_id
            )
            
            await self._send_message_to_connection(connection_id, response_message)
            
            self.stats["streams_active"] += 1
            
        except Exception as e:
            await self._send_error(connection_id, f"Stream start error: {e}")
    
    async def _cleanup_stream(self, connection_id: str, stream_id: str):
        """Clean up a stream"""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            connection.active_streams.discard(stream_id)
            
            # Send stream end message
            end_message = WebSocketMessage(
                message_id=str(uuid.uuid4()),
                event_type=WebSocketEventType.STREAM_END,
                data={
                    "stream_id": stream_id,
                    "reason": "cleanup"
                },
                connection_id=connection_id,
                stream_id=stream_id
            )
            
            await self._send_message_to_connection(connection_id, end_message)
            
            if self.stats["streams_active"] > 0:
                self.stats["streams_active"] -= 1
    
    async def send_stream_chunk(self, connection_id: str, stream_id: str, chunk_data: Any):
        """Send a streaming chunk to a connection"""
        if connection_id not in self.connections:
            return False
        
        chunk_message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            event_type=WebSocketEventType.STREAM_CHUNK,
            data=chunk_data,
            connection_id=connection_id,
            stream_id=stream_id
        )
        
        return await self._send_message_to_connection(connection_id, chunk_message)
    
    async def broadcast_stream_chunk(self, stream_id: str, chunk_data: Any):
        """Broadcast a streaming chunk to all relevant connections"""
        sent_count = 0
        
        for connection_id, connection in self.connections.items():
            if stream_id in connection.active_streams:
                if await self.send_stream_chunk(connection_id, stream_id, chunk_data):
                    sent_count += 1
        
        return sent_count
    
    async def send_message(self, connection_id: str, event_type: WebSocketEventType, data: Any):
        """Send a message to a specific connection"""
        if connection_id not in self.connections:
            return False
        
        message = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            event_type=event_type,
            data=data,
            connection_id=connection_id
        )
        
        return await self._send_message_to_connection(connection_id, message)
    
    async def broadcast_message(self, event_type: WebSocketEventType, data: Any, filter_func: Optional[Callable] = None):
        """Broadcast a message to all connections (optionally filtered)"""
        sent_count = 0
        
        for connection_id, connection in self.connections.items():
            if filter_func is None or filter_func(connection):
                if await self.send_message(connection_id, event_type, data):
                    sent_count += 1
        
        return sent_count
    
    async def _send_message_to_connection(self, connection_id: str, message: WebSocketMessage) -> bool:
        """Send message to a specific WebSocket connection"""
        if connection_id not in self.websocket_objects:
            return False
        
        try:
            websocket = self.websocket_objects[connection_id]
            
            # This is a placeholder - actual implementation depends on WebSocket library
            # For example, with websockets library: await websocket.send(message.to_json())
            # For fastapi: await websocket.send_text(message.to_json())
            
            # Placeholder implementation
            logger.debug(f"Would send to {connection_id}: {message.to_json()}")
            
            self.stats["messages_sent"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to {connection_id}: {e}")
            self.stats["errors"] += 1
            # Disconnect the client on send error
            await self.disconnect_client(connection_id)
            return False
    
    async def _send_error(self, connection_id: str, error_message: str):
        """Send error message to connection"""
        error_msg = WebSocketMessage(
            message_id=str(uuid.uuid4()),
            event_type=WebSocketEventType.ERROR,
            data={"error": error_message},
            connection_id=connection_id
        )
        await self._send_message_to_connection(connection_id, error_msg)
    
    def register_message_handler(self, event_type: WebSocketEventType, handler: Callable):
        """Register a message handler"""
        if event_type not in self.message_handlers:
            self.message_handlers[event_type] = []
        self.message_handlers[event_type].append(handler)
    
    def unregister_message_handler(self, event_type: WebSocketEventType, handler: Callable):
        """Unregister a message handler"""
        if event_type in self.message_handlers:
            try:
                self.message_handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    def register_connection_callback(self, callback: Callable):
        """Register a connection callback"""
        self.connection_callbacks.append(callback)
    
    def register_disconnection_callback(self, callback: Callable):
        """Register a disconnection callback"""
        self.disconnection_callbacks.append(callback)
    
    async def subscribe_to_stream(self, connection_id: str, stream_id: str):
        """Subscribe connection to a stream"""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            connection.active_streams.add(stream_id)
            return True
        return False
    
    async def unsubscribe_from_stream(self, connection_id: str, stream_id: str):
        """Unsubscribe connection from a stream"""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            connection.active_streams.discard(stream_id)
            return True
        return False
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection information"""
        connection = self.connections.get(connection_id)
        return connection.to_dict() if connection else None
    
    def get_all_connections(self) -> List[Dict[str, Any]]:
        """Get all connection information"""
        return [conn.to_dict() for conn in self.connections.values()]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket statistics"""
        current_time = time.time()
        
        # Calculate connection duration stats
        durations = []
        for connection in self.connections.values():
            durations.append(current_time - connection.connected_at)
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            **self.stats,
            "avg_connection_duration": avg_duration,
            "connection_details": {
                conn_id: {
                    "duration": current_time - conn.connected_at,
                    "last_activity_ago": current_time - conn.last_activity,
                    "active_streams": len(conn.active_streams)
                }
                for conn_id, conn in self.connections.items()
            }
        }
    
    async def close_all_connections(self):
        """Close all WebSocket connections"""
        connection_ids = list(self.connections.keys())
        for conn_id in connection_ids:
            await self.disconnect_client(conn_id)
    
    def cleanup(self):
        """Cleanup WebSocket handler"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # In a real implementation, you would close all WebSocket connections here