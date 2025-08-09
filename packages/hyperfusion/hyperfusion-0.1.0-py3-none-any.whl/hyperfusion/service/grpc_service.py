import grpc
from concurrent import futures
import asyncio
from typing import AsyncIterator, Optional
import pyarrow as pa
from . import hyperfusion_pb2
from . import hyperfusion_pb2_grpc
from .ipc import serialize_record_batch, deserialize_record_batch, serialize_schema, table_to_record_batch, record_batch_to_table
import logging
from asyncio import Queue
from .bus import Bus
from .messages import ExecuteFunctionRequest
from ..udtf.registry import registry

logger = logging.getLogger(__name__)


class ExecutorService(hyperfusion_pb2_grpc.ExecutionServiceServicer):
    def __init__(self, bus: Bus):
        self.bus = bus
        self.registry = registry
        self.logger = logger
        self.outgoing_queue: Optional[Queue] = None
        
    async def send_message(self, message: hyperfusion_pb2.ExecutorMessage):
        """Send a message to the connected Caller"""
        if self.outgoing_queue:
            await self.outgoing_queue.put(message)
    
    async def send_log(self, level: str, message: str):
        """Send a log message to the Caller"""
        await self.send_message(
            hyperfusion_pb2.ExecutorMessage(
                log=hyperfusion_pb2.LogMessage(
                    level=level,
                    message=message,
                    timestamp=int(asyncio.get_event_loop().time() * 1000)
                )
            )
        )
    
    async def send_executed_function(self, name: str, uuid: str, 
                                    output_batch: Optional[bytes] = None,
                                    error_batch: Optional[bytes] = None,
                                    error: Optional[str] = None):
        """Send function execution result to the Caller"""
        msg = hyperfusion_pb2.ExecutedFunctionMessage(
            name=name,
            uuid=uuid,
        )
        if output_batch:
            msg.output_record_batch = output_batch
        if error_batch:
            msg.error_record_batch = error_batch
        if error:
            msg.error = error
            
        await self.send_message(
            hyperfusion_pb2.ExecutorMessage(executed_function=msg)
        )
        
    async def Stream(self, 
                     request_iterator: AsyncIterator[hyperfusion_pb2.CallerMessage],
                     context: grpc.aio.ServicerContext
                     ) -> AsyncIterator[hyperfusion_pb2.ExecutorMessage]:
        """Handle bidirectional streaming connection from Caller"""
        
        self.logger.info("New gRPC Stream connection established")
        
        # Create queue for outgoing messages
        self.outgoing_queue = Queue()
        
        # Send all function definitions immediately when Caller connects
        functions = []
        for name, info in self.registry.functions.items():
            self.logger.info(f"Preparing to send function definition: {name}")
            functions.append(hyperfusion_pb2.FunctionDefinition(
                name=name,
                in_schema=serialize_schema(info.input_schema),
                out_schema=serialize_schema(info.output_schema),
                err_schema=serialize_schema(info.error_schema),
            ))
        
        self.logger.info(f"Sending {len(functions)} function definitions to caller")
        # Send all functions at once
        await self.outgoing_queue.put(
            hyperfusion_pb2.ExecutorMessage(
                expose_functions=hyperfusion_pb2.ExposeFunctionsMessage(
                    functions=functions
                )
            )
        )
        self.logger.info("Function definitions queued for sending")
        
        # Create tasks for handling incoming and outgoing messages
        async def handle_incoming():
            self.logger.info("Starting to handle incoming caller messages")
            async for caller_msg in request_iterator:
                self.logger.info(f"Received caller message: {caller_msg}")
                if caller_msg.HasField('get_functions'):
                    self.logger.info("Received get_functions request, re-sending function definitions")
                    # Re-send function definitions if requested
                    await self.outgoing_queue.put(
                        hyperfusion_pb2.ExecutorMessage(
                            expose_functions=hyperfusion_pb2.ExposeFunctionsMessage(
                                functions=functions
                            )
                        )
                    )
                    
                elif caller_msg.HasField('execute_function'):
                    # Publish execution request to bus for MainService to handle
                    exec_msg = caller_msg.execute_function
                    await self.bus.publish(ExecuteFunctionRequest(exec_msg=exec_msg))
        
        # Run both tasks concurrently
        incoming_task = asyncio.create_task(handle_incoming())
        
        try:
            self.logger.info("Starting to handle outgoing messages")
            while True:
                self.logger.debug("Waiting for outgoing message...")
                message = await self.outgoing_queue.get()
                if message is None:  # Sentinel to stop
                    self.logger.info("Received stop sentinel, ending outgoing handler")
                    break
                yield message
        finally:
            incoming_task.cancel()
            self.outgoing_queue = None
    
    async def HealthCheck(self, request, context):
        return hyperfusion_pb2.HealthStatus(ready=True, message="Healthy")


