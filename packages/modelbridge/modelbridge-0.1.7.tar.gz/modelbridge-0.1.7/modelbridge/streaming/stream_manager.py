"""
Stream Manager for ModelBridge
Centralized management of streaming across different protocols
"""
import asyncio
import time
import uuid
import logging
from typing import Dict, Any, List, Optional, AsyncIterator, Callable, Union, Set
from dataclasses import dataclass, field
from enum import Enum

from .streaming_handler import StreamingHandler, StreamEvent, StreamEventType
from .websocket_handler import WebSocketHandler, WebSocketEventType
from .sse_handler import SSEHandler, SSEEventType

logger = logging.getLogger(__name__)


class StreamProtocol(Enum):
    """Supported streaming protocols"""
    HTTP_STREAM = "http_stream"
    WEBSOCKET = "websocket"
    SSE = "sse"


@dataclass
class StreamSession:
    """Unified stream session"""
    session_id: str
    protocol: StreamProtocol
    connection_id: str
    stream_id: str
    provider_name: str
    model_id: str
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Stream state
    is_active: bool = True
    chunks_sent: int = 0
    bytes_sent: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "protocol": self.protocol.value,
            "connection_id": self.connection_id,
            "stream_id": self.stream_id,
            "provider_name": self.provider_name,
            "model_id": self.model_id,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "metadata": self.metadata,
            "is_active": self.is_active,
            "chunks_sent": self.chunks_sent,
            "bytes_sent": self.bytes_sent
        }


class StreamManager:
    """Centralized streaming management across protocols"""
    
    def __init__(self):
        # Protocol handlers
        self.streaming_handler = StreamingHandler()
        self.websocket_handler = WebSocketHandler()
        self.sse_handler = SSEHandler()
        
        # Active sessions
        self.sessions: Dict[str, StreamSession] = {}
        self.session_by_connection: Dict[str, Set[str]] = {}  # connection_id -> set of session_ids
        
        # Event routing
        self.event_callbacks: List[Callable] = []
        self.protocol_callbacks: Dict[StreamProtocol, List[Callable]] = {}
        
        # Statistics
        self.stats = {
            "total_sessions": 0,
            "active_sessions": 0,
            "sessions_by_protocol": {
                StreamProtocol.HTTP_STREAM: 0,
                StreamProtocol.WEBSOCKET: 0,
                StreamProtocol.SSE: 0
            },
            "total_chunks_sent": 0,
            "total_bytes_sent": 0,
            "errors": 0
        }
        
        # Setup cross-protocol event routing
        self._setup_event_routing()
        
        # Background cleanup
        self._cleanup_task = None
        self._start_cleanup_task()
    
    def _setup_event_routing(self):
        """Setup event routing between protocols"""
        
        # Register WebSocket event handlers
        self.websocket_handler.register_message_handler(
            WebSocketEventType.STREAM_START,
            self._handle_websocket_stream_start
        )
        
        # Register SSE callbacks
        self.sse_handler.register_connection_callback(self._handle_sse_connection)
        self.sse_handler.register_disconnection_callback(self._handle_sse_disconnection)
        
        # Register streaming callbacks
        # This would be setup when streams are created
    
    def _start_cleanup_task(self):
        """Start background cleanup task"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
        except RuntimeError:
            logger.info("No event loop available for StreamManager cleanup task")
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of stale sessions"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                await self._cleanup_stale_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"StreamManager cleanup error: {e}")
    
    async def _cleanup_stale_sessions(self):
        """Clean up stale streaming sessions"""
        current_time = time.time()
        stale_threshold = 3600  # 1 hour
        
        stale_sessions = []
        for session_id, session in self.sessions.items():
            if current_time - session.last_activity > stale_threshold:
                stale_sessions.append(session_id)
        
        for session_id in stale_sessions:
            logger.info(f"Cleaning up stale stream session: {session_id}")
            await self.end_stream_session(session_id, reason="stale_cleanup")
    
    async def create_stream_session(
        self,
        protocol: StreamProtocol,
        connection_id: str,
        provider_name: str,
        model_id: str,
        stream_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new streaming session"""
        
        session_id = str(uuid.uuid4())
        stream_id = str(uuid.uuid4())
        
        session = StreamSession(
            session_id=session_id,
            protocol=protocol,
            connection_id=connection_id,
            stream_id=stream_id,
            provider_name=provider_name,
            model_id=model_id,
            metadata=stream_metadata or {}
        )
        
        self.sessions[session_id] = session
        
        # Track by connection
        if connection_id not in self.session_by_connection:
            self.session_by_connection[connection_id] = set()
        self.session_by_connection[connection_id].add(session_id)
        
        # Update statistics
        self.stats["total_sessions"] += 1
        self.stats["active_sessions"] += 1
        self.stats["sessions_by_protocol"][protocol] += 1
        
        # Initialize protocol-specific session
        if protocol == StreamProtocol.WEBSOCKET:
            await self._init_websocket_session(session)
        elif protocol == StreamProtocol.SSE:
            await self._init_sse_session(session)
        elif protocol == StreamProtocol.HTTP_STREAM:
            await self._init_http_stream_session(session)
        
        logger.info(f"Created stream session {session_id} for {protocol.value}")
        return session_id
    
    async def _init_websocket_session(self, session: StreamSession):
        """Initialize WebSocket streaming session"""
        # Subscribe WebSocket connection to the stream
        await self.websocket_handler.subscribe_to_stream(
            session.connection_id,
            session.stream_id
        )
    
    async def _init_sse_session(self, session: StreamSession):
        """Initialize SSE streaming session"""
        # Start SSE stream
        await self.sse_handler.start_stream(
            session.connection_id,
            session.stream_id,
            session.metadata
        )
        
        # Subscribe to stream
        self.sse_handler.subscribe_to_stream(
            session.connection_id,
            session.stream_id
        )
    
    async def _init_http_stream_session(self, session: StreamSession):
        """Initialize HTTP streaming session"""
        # HTTP streaming is handled directly through streaming_handler
        # No additional setup needed
        pass
    
    async def send_stream_chunk(
        self,
        session_id: str,
        chunk_data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send chunk to streaming session"""
        
        if session_id not in self.sessions:
            logger.warning(f"Stream session not found: {session_id}")
            return False
        
        session = self.sessions[session_id]
        
        if not session.is_active:
            logger.warning(f"Stream session not active: {session_id}")
            return False
        
        try:
            # Update session stats
            session.chunks_sent += 1
            session.bytes_sent += len(str(chunk_data))
            session.last_activity = time.time()
            
            # Send chunk based on protocol
            if session.protocol == StreamProtocol.WEBSOCKET:
                success = await self.websocket_handler.send_stream_chunk(
                    session.connection_id,
                    session.stream_id,
                    chunk_data
                )
            elif session.protocol == StreamProtocol.SSE:
                success = await self.sse_handler.send_stream_chunk(
                    session.connection_id,
                    session.stream_id,
                    chunk_data,
                    metadata
                )
            elif session.protocol == StreamProtocol.HTTP_STREAM:
                # For HTTP streaming, we would need to yield to the response stream
                # This would be handled differently in actual HTTP response
                success = True
                logger.debug(f"HTTP stream chunk for {session_id}: {chunk_data}")
            else:
                success = False
            
            if success:
                self.stats["total_chunks_sent"] += 1
                self.stats["total_bytes_sent"] += session.bytes_sent
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending chunk to session {session_id}: {e}")
            self.stats["errors"] += 1
            await self.end_stream_session(session_id, reason="send_error")
            return False
    
    async def broadcast_stream_chunk(
        self,
        stream_id: str,
        chunk_data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Broadcast chunk to all sessions for a stream"""
        
        sent_count = 0
        
        for session_id, session in self.sessions.items():
            if session.stream_id == stream_id and session.is_active:
                if await self.send_stream_chunk(session_id, chunk_data, metadata):
                    sent_count += 1
        
        return sent_count
    
    async def end_stream_session(self, session_id: str, reason: str = "completed"):
        """End a streaming session"""
        
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        session.is_active = False
        
        try:
            # End stream based on protocol
            if session.protocol == StreamProtocol.WEBSOCKET:
                # WebSocket streams end naturally when connection closes
                pass
            elif session.protocol == StreamProtocol.SSE:
                await self.sse_handler.end_stream(
                    session.connection_id,
                    session.stream_id,
                    reason
                )
            elif session.protocol == StreamProtocol.HTTP_STREAM:
                # HTTP streams end when the response generator completes
                pass
            
            # Execute callbacks
            await self._execute_stream_end_callbacks(session, reason)
            
        except Exception as e:
            logger.error(f"Error ending stream session {session_id}: {e}")
        
        finally:
            # Cleanup
            del self.sessions[session_id]
            
            # Remove from connection tracking
            if session.connection_id in self.session_by_connection:
                self.session_by_connection[session.connection_id].discard(session_id)
                if not self.session_by_connection[session.connection_id]:
                    del self.session_by_connection[session.connection_id]
            
            # Update statistics
            self.stats["active_sessions"] -= 1
            self.stats["sessions_by_protocol"][session.protocol] -= 1
            
            logger.info(f"Ended stream session {session_id}: {reason}")
    
    async def get_stream_for_session(self, session_id: str) -> Optional[AsyncIterator[Any]]:
        """Get stream iterator for HTTP streaming session"""
        
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        
        if session.protocol != StreamProtocol.HTTP_STREAM:
            logger.error(f"Session {session_id} is not an HTTP stream session")
            return
        
        # Create stream using streaming handler
        stream_context = {
            "request_id": session.stream_id,
            "provider": session.provider_name,
            "model": session.model_id,
            "stream_type": "text",
            "metadata": session.metadata
        }
        
        try:
            async for event in self.streaming_handler.create_stream(
                session.stream_id,
                session.provider_name,
                session.model_id,
                metadata=session.metadata
            ):
                # Update session activity
                session.last_activity = time.time()
                
                # Convert stream event to chunk data
                if event.event_type in [StreamEventType.CHUNK, StreamEventType.DELTA]:
                    chunk_data = event.data
                    session.chunks_sent += 1
                    session.bytes_sent += len(str(chunk_data))
                    yield chunk_data
                elif event.event_type == StreamEventType.COMPLETE:
                    break
                elif event.event_type == StreamEventType.ERROR:
                    logger.error(f"Stream error for session {session_id}: {event.data}")
                    break
        
        except Exception as e:
            logger.error(f"Stream error for session {session_id}: {e}")
        
        finally:
            await self.end_stream_session(session_id, reason="stream_completed")
    
    async def _handle_websocket_stream_start(self, connection_id: str, message: Any):
        """Handle WebSocket stream start request"""
        try:
            # Extract stream request data from message
            stream_data = message.data if hasattr(message, 'data') else {}
            
            provider_name = stream_data.get("provider", "unknown")
            model_id = stream_data.get("model", "unknown")
            
            # Create streaming session
            session_id = await self.create_stream_session(
                StreamProtocol.WEBSOCKET,
                connection_id,
                provider_name,
                model_id,
                stream_data
            )
            
            logger.info(f"Started WebSocket stream session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error handling WebSocket stream start: {e}")
    
    async def _handle_sse_connection(self, connection: Any):
        """Handle new SSE connection"""
        logger.info(f"New SSE connection: {connection.connection_id}")
    
    async def _handle_sse_disconnection(self, connection: Any):
        """Handle SSE disconnection"""
        connection_id = connection.connection_id
        
        # End all sessions for this connection
        if connection_id in self.session_by_connection:
            session_ids = list(self.session_by_connection[connection_id])
            for session_id in session_ids:
                await self.end_stream_session(session_id, reason="connection_lost")
        
        logger.info(f"SSE connection disconnected: {connection_id}")
    
    async def _execute_stream_end_callbacks(self, session: StreamSession, reason: str):
        """Execute callbacks when stream ends"""
        for callback in self.event_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback("stream_end", session, reason)
                else:
                    callback("stream_end", session, reason)
            except Exception as e:
                logger.error(f"Stream end callback error: {e}")
        
        # Protocol-specific callbacks
        protocol_callbacks = self.protocol_callbacks.get(session.protocol, [])
        for callback in protocol_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback("stream_end", session, reason)
                else:
                    callback("stream_end", session, reason)
            except Exception as e:
                logger.error(f"Protocol callback error: {e}")
    
    def register_event_callback(self, callback: Callable):
        """Register event callback"""
        self.event_callbacks.append(callback)
    
    def register_protocol_callback(self, protocol: StreamProtocol, callback: Callable):
        """Register protocol-specific callback"""
        if protocol not in self.protocol_callbacks:
            self.protocol_callbacks[protocol] = []
        self.protocol_callbacks[protocol].append(callback)
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        session = self.sessions.get(session_id)
        return session.to_dict() if session else None
    
    def get_sessions_for_connection(self, connection_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a connection"""
        if connection_id not in self.session_by_connection:
            return []
        
        session_ids = self.session_by_connection[connection_id]
        return [
            self.sessions[session_id].to_dict()
            for session_id in session_ids
            if session_id in self.sessions
        ]
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        return [session.to_dict() for session in self.sessions.values()]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get streaming statistics"""
        return {
            **self.stats,
            "protocol_handler_stats": {
                "streaming": self.streaming_handler.get_stream_stats(),
                "websocket": self.websocket_handler.get_stats(),
                "sse": self.sse_handler.get_stats()
            },
            "session_details": {
                session_id: {
                    "protocol": session.protocol.value,
                    "chunks_sent": session.chunks_sent,
                    "bytes_sent": session.bytes_sent,
                    "duration": time.time() - session.created_at
                }
                for session_id, session in self.sessions.items()
            }
        }
    
    async def close_all_sessions(self):
        """Close all active streaming sessions"""
        session_ids = list(self.sessions.keys())
        
        for session_id in session_ids:
            await self.end_stream_session(session_id, reason="shutdown")
        
        # Close protocol handlers
        await self.streaming_handler.close_all_streams()
        await self.websocket_handler.close_all_connections()
        await self.sse_handler.close_all_connections()
    
    def cleanup(self):
        """Cleanup stream manager"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        self.streaming_handler = None
        self.websocket_handler.cleanup()
        self.sse_handler.cleanup()