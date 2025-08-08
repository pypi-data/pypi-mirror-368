"""
Streaming Handler for ModelBridge
Handles real-time streaming responses from providers
"""
import asyncio
import json
import time
import logging
from typing import Dict, Any, List, Optional, AsyncIterator, Callable, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class StreamEventType(Enum):
    """Types of streaming events"""
    START = "start"
    CHUNK = "chunk"
    DELTA = "delta"
    COMPLETE = "complete"
    ERROR = "error"
    METADATA = "metadata"


@dataclass
class StreamEvent:
    """Streaming event data"""
    event_type: StreamEventType
    data: Any
    timestamp: float
    request_id: str
    provider: Optional[str] = None
    model: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "event_type": self.event_type.value,
            "data": self.data,
            "timestamp": self.timestamp,
            "request_id": self.request_id,
            "provider": self.provider,
            "model": self.model,
            "metadata": self.metadata or {}
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


class StreamProcessor(ABC):
    """Abstract base class for stream processors"""
    
    @abstractmethod
    async def process_chunk(self, chunk: Any, context: Dict[str, Any]) -> Optional[StreamEvent]:
        """Process a streaming chunk"""
        pass
    
    @abstractmethod
    async def finalize_stream(self, context: Dict[str, Any]) -> Optional[StreamEvent]:
        """Finalize the stream processing"""
        pass


class TextStreamProcessor(StreamProcessor):
    """Processor for text-based streaming"""
    
    async def process_chunk(self, chunk: Any, context: Dict[str, Any]) -> Optional[StreamEvent]:
        """Process a text chunk"""
        if isinstance(chunk, str) and chunk.strip():
            return StreamEvent(
                event_type=StreamEventType.CHUNK,
                data={"text": chunk},
                timestamp=time.time(),
                request_id=context.get("request_id", ""),
                provider=context.get("provider"),
                model=context.get("model")
            )
        return None
    
    async def finalize_stream(self, context: Dict[str, Any]) -> Optional[StreamEvent]:
        """Finalize text stream"""
        return StreamEvent(
            event_type=StreamEventType.COMPLETE,
            data={"message": "Stream completed"},
            timestamp=time.time(),
            request_id=context.get("request_id", ""),
            provider=context.get("provider"),
            model=context.get("model")
        )


class JSONStreamProcessor(StreamProcessor):
    """Processor for JSON-based streaming"""
    
    def __init__(self):
        self.buffer = ""
    
    async def process_chunk(self, chunk: Any, context: Dict[str, Any]) -> Optional[StreamEvent]:
        """Process a JSON chunk"""
        if isinstance(chunk, str):
            self.buffer += chunk
            
            # Try to extract complete JSON objects
            events = []
            while True:
                try:
                    # Try to find a complete JSON object
                    start_idx = self.buffer.find('{')
                    if start_idx == -1:
                        break
                    
                    # Find matching closing brace
                    brace_count = 0
                    end_idx = -1
                    for i, char in enumerate(self.buffer[start_idx:], start_idx):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i
                                break
                    
                    if end_idx == -1:
                        break  # No complete JSON object yet
                    
                    json_str = self.buffer[start_idx:end_idx + 1]
                    json_obj = json.loads(json_str)
                    
                    # Remove processed JSON from buffer
                    self.buffer = self.buffer[end_idx + 1:]
                    
                    return StreamEvent(
                        event_type=StreamEventType.DELTA,
                        data=json_obj,
                        timestamp=time.time(),
                        request_id=context.get("request_id", ""),
                        provider=context.get("provider"),
                        model=context.get("model")
                    )
                    
                except json.JSONDecodeError:
                    # Remove invalid JSON start
                    self.buffer = self.buffer[start_idx + 1:]
                    continue
                
                break
        
        return None
    
    async def finalize_stream(self, context: Dict[str, Any]) -> Optional[StreamEvent]:
        """Finalize JSON stream"""
        # Process any remaining buffer data
        if self.buffer.strip():
            try:
                final_data = json.loads(self.buffer)
                return StreamEvent(
                    event_type=StreamEventType.COMPLETE,
                    data=final_data,
                    timestamp=time.time(),
                    request_id=context.get("request_id", ""),
                    provider=context.get("provider"),
                    model=context.get("model")
                )
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse final buffer: {self.buffer}")
        
        return StreamEvent(
            event_type=StreamEventType.COMPLETE,
            data={"message": "JSON stream completed"},
            timestamp=time.time(),
            request_id=context.get("request_id", ""),
            provider=context.get("provider"),
            model=context.get("model")
        )


class StreamingHandler:
    """Main streaming handler for ModelBridge"""
    
    def __init__(self):
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.processors: Dict[str, StreamProcessor] = {
            "text": TextStreamProcessor(),
            "json": JSONStreamProcessor()
        }
        self.stream_callbacks: Dict[str, List[Callable]] = {}
        
    async def create_stream(
        self, 
        request_id: str, 
        provider_name: str, 
        model_id: str,
        stream_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[StreamEvent]:
        """Create a new streaming session"""
        
        stream_context = {
            "request_id": request_id,
            "provider": provider_name,
            "model": model_id,
            "stream_type": stream_type,
            "start_time": time.time(),
            "metadata": metadata or {},
            "processed_chunks": 0,
            "total_bytes": 0
        }
        
        self.active_streams[request_id] = stream_context
        
        # Send start event
        start_event = StreamEvent(
            event_type=StreamEventType.START,
            data={"message": f"Stream started for {provider_name}:{model_id}"},
            timestamp=time.time(),
            request_id=request_id,
            provider=provider_name,
            model=model_id,
            metadata=metadata
        )
        
        yield start_event
        
        try:
            # This is where we would integrate with actual provider streaming
            # For now, we'll create a placeholder async generator
            async for event in self._process_provider_stream(stream_context):
                yield event
                
        except Exception as e:
            logger.error(f"Stream error for request {request_id}: {e}")
            error_event = StreamEvent(
                event_type=StreamEventType.ERROR,
                data={"error": str(e)},
                timestamp=time.time(),
                request_id=request_id,
                provider=provider_name,
                model=model_id
            )
            yield error_event
        
        finally:
            # Cleanup
            if request_id in self.active_streams:
                del self.active_streams[request_id]
    
    async def _process_provider_stream(self, context: Dict[str, Any]) -> AsyncIterator[StreamEvent]:
        """Process streaming data from provider"""
        request_id = context["request_id"]
        stream_type = context["stream_type"]
        processor = self.processors.get(stream_type, self.processors["text"])
        
        # This would be replaced with actual provider streaming integration
        # For now, simulate streaming chunks
        sample_chunks = [
            "Hello", " world", "! This", " is", " a", " streaming", " response", " from", " the", " model", "."
        ]
        
        for chunk in sample_chunks:
            # Simulate some processing delay
            await asyncio.sleep(0.1)
            
            # Update context
            context["processed_chunks"] += 1
            context["total_bytes"] += len(str(chunk))
            
            # Process the chunk
            event = await processor.process_chunk(chunk, context)
            if event:
                # Execute callbacks
                await self._execute_callbacks(request_id, event)
                yield event
        
        # Finalize stream
        final_event = await processor.finalize_stream(context)
        if final_event:
            await self._execute_callbacks(request_id, final_event)
            yield final_event
    
    async def _execute_callbacks(self, request_id: str, event: StreamEvent):
        """Execute registered callbacks for stream events"""
        callbacks = self.stream_callbacks.get(request_id, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Stream callback error: {e}")
    
    def register_callback(self, request_id: str, callback: Callable):
        """Register a callback for stream events"""
        if request_id not in self.stream_callbacks:
            self.stream_callbacks[request_id] = []
        self.stream_callbacks[request_id].append(callback)
    
    def unregister_callback(self, request_id: str, callback: Callable):
        """Unregister a callback for stream events"""
        if request_id in self.stream_callbacks:
            try:
                self.stream_callbacks[request_id].remove(callback)
            except ValueError:
                pass
    
    async def process_provider_stream(
        self, 
        provider_stream: AsyncIterator[Any], 
        request_id: str,
        processor_type: str = "text"
    ) -> AsyncIterator[StreamEvent]:
        """Process a stream from a provider"""
        
        context = self.active_streams.get(request_id, {})
        processor = self.processors.get(processor_type, self.processors["text"])
        
        try:
            async for raw_chunk in provider_stream:
                # Update stats
                if request_id in self.active_streams:
                    self.active_streams[request_id]["processed_chunks"] += 1
                    self.active_streams[request_id]["total_bytes"] += len(str(raw_chunk))
                
                # Process chunk
                event = await processor.process_chunk(raw_chunk, context)
                if event:
                    await self._execute_callbacks(request_id, event)
                    yield event
            
            # Finalize
            final_event = await processor.finalize_stream(context)
            if final_event:
                await self._execute_callbacks(request_id, final_event)
                yield final_event
                
        except Exception as e:
            error_event = StreamEvent(
                event_type=StreamEventType.ERROR,
                data={"error": str(e)},
                timestamp=time.time(),
                request_id=request_id,
                provider=context.get("provider"),
                model=context.get("model")
            )
            yield error_event
    
    def get_stream_stats(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Get streaming statistics"""
        if request_id:
            return self.active_streams.get(request_id, {})
        else:
            return {
                "active_streams": len(self.active_streams),
                "streams": {
                    stream_id: {
                        "provider": stream_data.get("provider"),
                        "model": stream_data.get("model"),
                        "processed_chunks": stream_data.get("processed_chunks", 0),
                        "total_bytes": stream_data.get("total_bytes", 0),
                        "duration": time.time() - stream_data.get("start_time", time.time())
                    }
                    for stream_id, stream_data in self.active_streams.items()
                }
            }
    
    async def close_stream(self, request_id: str):
        """Close a streaming session"""
        if request_id in self.active_streams:
            # Send completion event
            stream_data = self.active_streams[request_id]
            
            completion_event = StreamEvent(
                event_type=StreamEventType.COMPLETE,
                data={
                    "message": "Stream closed",
                    "stats": {
                        "processed_chunks": stream_data.get("processed_chunks", 0),
                        "total_bytes": stream_data.get("total_bytes", 0),
                        "duration": time.time() - stream_data.get("start_time", time.time())
                    }
                },
                timestamp=time.time(),
                request_id=request_id,
                provider=stream_data.get("provider"),
                model=stream_data.get("model")
            )
            
            await self._execute_callbacks(request_id, completion_event)
            
            # Cleanup
            del self.active_streams[request_id]
            if request_id in self.stream_callbacks:
                del self.stream_callbacks[request_id]
    
    async def close_all_streams(self):
        """Close all active streaming sessions"""
        stream_ids = list(self.active_streams.keys())
        for stream_id in stream_ids:
            await self.close_stream(stream_id)
    
    def add_processor(self, name: str, processor: StreamProcessor):
        """Add a custom stream processor"""
        self.processors[name] = processor
    
    def remove_processor(self, name: str):
        """Remove a stream processor"""
        if name in self.processors and name not in ["text", "json"]:  # Don't remove built-ins
            del self.processors[name]