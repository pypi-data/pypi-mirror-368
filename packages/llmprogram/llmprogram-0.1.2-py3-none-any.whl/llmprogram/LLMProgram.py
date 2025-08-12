import os
import yaml
import json
import time
import logging
from typing import Any, Dict, Optional, AsyncGenerator, Union, List
from pathlib import Path
from openai import AsyncOpenAI
from jinja2 import Template
from jsonschema import validate, ValidationError
import hashlib
import json
from redis.asyncio import Redis
from datetime import timedelta
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import uuid
from contextlib import asynccontextmanager
import aiosqlite

from llmprogram.analytics import get_analytics_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLiteLogger:
    """Manages logging of program executions to SQLite database."""
    def __init__(self, program_path: str, db_path: Optional[str] = None):
        """Initialize SQLite logger for a specific program.
        
        Args:
            program_path: Path to the program YAML file
            db_path: Optional custom path for the database file. If not provided,
                    the database will be stored in the same directory as the program file.
        """
        self.program_path = program_path
        # Use custom db path if provided, otherwise use default location
        self.db_path = Path(db_path) if db_path else Path(program_path).with_suffix('.db')
        self._initialized = False
        self._queue = asyncio.Queue()
        self._worker_task = None
        self._shutdown_event = asyncio.Event()
    
    async def _ensure_initialized(self):
        """Ensure database is initialized with proper schema."""
        if not self._initialized:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS program_logs (
                        id TEXT PRIMARY KEY,
                        timestamp REAL,
                        function_input TEXT,
                        function_output TEXT,
                        llm_input TEXT,
                        llm_output TEXT,
                        function_version TEXT,
                        response_metadata TEXT,
                        execution_time REAL
                    )
                """)
                await db.commit()
            self._initialized = True
            # Start the background worker
            self._worker_task = asyncio.create_task(self._process_queue())
    
    async def _process_queue(self):
        """Process queued log entries in the background."""
        while not self._shutdown_event.is_set():
            try:
                # Use wait_for to periodically check shutdown event
                log_entry = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                try:
                    async with aiosqlite.connect(self.db_path) as db:
                        await db.execute("""
                            INSERT INTO program_logs 
                            (id, timestamp, function_input, function_output, llm_input, 
                             llm_output, function_version, response_metadata, execution_time)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            log_entry['id'],
                            log_entry['timestamp'],
                            json.dumps(log_entry['function_input']),
                            json.dumps(log_entry['function_output']),
                            log_entry['llm_input'],
                            log_entry['llm_output'],
                            log_entry['function_version'],
                            json.dumps(log_entry['response_metadata']),
                            log_entry['execution_time']
                        ))
                        await db.commit()
                except Exception as e:
                    logger.error(f"Failed to write to SQLite: {str(e)}")
                finally:
                    self._queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in queue processing: {str(e)}")
                continue
    
    async def log_execution(self, function_input: Dict[str, Any], function_output: Dict[str, Any],
                          llm_input: str, llm_output: str, function_version: str,
                          response_metadata: Dict[str, Any], execution_time: float):
        """Log a program execution asynchronously."""
        await self._ensure_initialized()
        log_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': time.time(),
            'function_input': function_input,
            'function_output': function_output,
            'llm_input': llm_input,
            'llm_output': llm_output,
            'function_version': function_version,
            'response_metadata': response_metadata,
            'execution_time': execution_time
        }
        await self._queue.put(log_entry)
        return log_entry['id']
    
    async def close(self):
        """Close the logger and wait for pending operations."""
        if self._worker_task:
            # Signal shutdown
            self._shutdown_event.set()
            # Wait for queue to be empty
            if not self._queue.empty():
                await self._queue.join()
            # Cancel the worker task
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

class LLMProgramError(Exception):
    """Base exception for LLM program errors."""
    pass

class ValidationError(LLMProgramError):
    """Exception raised for validation errors."""
    pass

class RedisCacheManager:
    """Manages caching of LLM responses using Redis."""
    def __init__(self, redis_url: str = "redis://localhost:6379", ttl: int = 3600):
        """Initialize Redis cache manager.
        
        Args:
            redis_url: Redis connection URL
            ttl: Time to live for cached items in seconds (default: 1 hour)
        """
        self.redis_url = redis_url
        self.ttl = ttl
        self._redis = None
        self._initialized = False
    
    async def _ensure_connection(self):
        """Ensure Redis connection is established."""
        if not self._initialized:
            try:
                self._redis = Redis.from_url(self.redis_url)
                self._initialized = True
                logger.info("Redis connection established")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {str(e)}")
                raise LLMProgramError(f"Redis connection failed: {str(e)}")
    
    def _generate_cache_key(self, prompt: str, **kwargs) -> str:
        """Generate a unique cache key based on the prompt and parameters."""
        cache_data = {
            'prompt': prompt,
            'params': kwargs
        }
        return f"llm_cache:{hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()}"
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a cached response from Redis."""
        await self._ensure_connection()
        try:
            cached_data = await self._redis.get(key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve from Redis cache: {str(e)}")
            return None
    
    async def set(self, key: str, value: Dict[str, Any]) -> None:
        """Store a response in Redis cache."""
        await self._ensure_connection()
        try:
            await self._redis.set(
                key,
                json.dumps(value),
                ex=self.ttl
            )
        except Exception as e:
            logger.error(f"Failed to store in Redis cache: {str(e)}")
    
    async def clear(self, pattern: str = "llm_cache:*") -> None:
        """Clear cache entries matching the pattern."""
        await self._ensure_connection()
        try:
            keys = await self._redis.keys(pattern)
            if keys:
                await self._redis.delete(*keys)
                logger.info(f"Cleared {len(keys)} cache entries")
        except Exception as e:
            logger.error(f"Failed to clear Redis cache: {str(e)}")
    
    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.aclose()
            self._initialized = False
            logger.info("Redis connection closed")

class LLMProgram:
    def __init__(self, program_path: str, enable_cache: bool = True, 
                 redis_url: str = "redis://localhost:6379", cache_ttl: int = 3600,
                 max_workers: int = 4, tools: Optional[List[Dict[str, Any]]] = None,
                 api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize an LLM program from a YAML file.
        
        Args:
            program_path: Path to the program YAML file
            enable_cache: Whether to enable response caching
            redis_url: Redis connection URL for caching
            cache_ttl: Cache time-to-live in seconds
            max_workers: Maximum number of worker threads
            tools: Optional list of tools/functions available to the LLM
            api_key: OpenAI API key. Defaults to OPENAI_API_KEY env var.
            base_url: OpenAI base URL. Useful for custom endpoints like Ollama.
        """
        self.program_path = program_path
        self.config = self._load_config()
        self.client = AsyncOpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url
        )
        self.cache_manager = RedisCacheManager(redis_url, cache_ttl) if enable_cache else None
        self.metrics = {
            'total_calls': 0,
            'cache_hits': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'avg_response_time': 0.0,
            'tool_calls': 0
        }
        self.max_workers = max_workers
        self._local_cache = {}
        self._local_cache_ttl = 300  # 5 minutes
        self._local_cache_timestamps = {}
        self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        # Initialize SQLite logger with optional custom db path from config
        db_path = self.config.get('database', {}).get('path')
        self.logger = SQLiteLogger(program_path, db_path)
        self.version = self.config.get('version', '1.0.0')
        self.tools = tools or []
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.cache_manager:
            await self.cache_manager.close()
        # Close the OpenAI client's session
        await self.client.close()
        # Shutdown thread pool
        self._thread_pool.shutdown(wait=True)
        # Close SQLite logger
        await self.logger.close()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the program configuration from YAML."""
        with open(self.program_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _render_template(self, **kwargs) -> str:
        """Render the template with the given variables."""
        template = Template(self.config['template'])
        return template.render(**kwargs)
    
    def _validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate input data against the input schema."""
        try:
            validate(instance=input_data, schema=self.config['input_schema'])
        except ValidationError as e:
            raise ValidationError(f"Input validation failed: {str(e)}")
    
    def _validate_output(self, output_data: Dict[str, Any]) -> None:
        """Validate output data against the output schema."""
        try:
            validate(instance=output_data, schema=self.config['output_schema'])
        except ValidationError as e:
            raise ValidationError(f"Output validation failed: {str(e)}")
    
    def _update_metrics(self, response: Any, execution_time: float) -> None:
        """Update program metrics with the latest execution data."""
        self.metrics['total_calls'] += 1
        self.metrics['avg_response_time'] = (
            (self.metrics['avg_response_time'] * (self.metrics['total_calls'] - 1) + execution_time)
            / self.metrics['total_calls']
        )
        
        # Update token usage and cost if available
        if hasattr(response, 'usage'):
            self.metrics['total_tokens'] += response.usage.total_tokens
            # Approximate cost calculation (adjust rates as needed)
            cost_per_1k_tokens = 0.002  # Example rate
            self.metrics['total_cost'] += (response.usage.total_tokens / 1000) * cost_per_1k_tokens
    
    def _clean_local_cache(self):
        """Clean expired entries from local cache."""
        current_time = time.time()
        expired_keys = [
            k for k, t in self._local_cache_timestamps.items()
            if current_time - t > self._local_cache_ttl
        ]
        for k in expired_keys:
            del self._local_cache[k]
            del self._local_cache_timestamps[k]

    async def batch_process(self, inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple inputs in parallel."""
        async def process_single(input_data: Dict[str, Any]) -> Dict[str, Any]:
            return await self.__call__(**input_data)

        # Clean local cache before processing
        self._clean_local_cache()

        # Process inputs in parallel
        tasks = [process_single(input_data) for input_data in inputs]
        results = await asyncio.gather(*tasks)
        return results

    async def __call__(self, **kwargs) -> Dict[str, Any]:
        """Execute the LLM program with the given inputs."""
        try:
            start_time = time.time()
            
            # Validate input against schema
            self._validate_input(kwargs)
            
            # Render the template
            user_prompt = self._render_template(**kwargs)
            
            # Check local cache first
            cache_key = self.cache_manager._generate_cache_key(user_prompt, **kwargs) if self.cache_manager else None
            if cache_key and cache_key in self._local_cache:
                if time.time() - self._local_cache_timestamps[cache_key] <= self._local_cache_ttl:
                    self.metrics['cache_hits'] += 1
                    logger.info(f"Local cache hit for program {self.program_path}")
                    result = self._local_cache[cache_key]
                    # Log the cached execution
                    execution_time = time.time() - start_time
                    await self.logger.log_execution(
                        function_input=kwargs,
                        function_output=result,
                        llm_input=user_prompt,
                        llm_output=json.dumps(result),
                        function_version=self.version,
                        response_metadata={'cache_hit': True, 'cache_source': 'local'},
                        execution_time=execution_time
                    )
                    
                    # Track analytics for cache hit
                    analytics_engine = await get_analytics_engine()
                    program_name = Path(self.program_path).stem
                    await analytics_engine.track_llm_call(
                        program_name=program_name,
                        model_name=self.config['model']['name'],
                        execution_time_ms=int(execution_time * 1000),
                        cache_hit=True,
                        user_id="unknown"
                    )
                    await analytics_engine.track_program_usage(
                        program_name=program_name,
                        execution_time_ms=int(execution_time * 1000),
                        success=True,
                        user_id="unknown",
                        input_params=kwargs
                    )
                    
                    return result
            
            # Check Redis cache if enabled
            if self.cache_manager:
                cached_response = await self.cache_manager.get(cache_key)
                if cached_response:
                    self.metrics['cache_hits'] += 1
                    logger.info(f"Redis cache hit for program {self.program_path}")
                    # Update local cache
                    self._local_cache[cache_key] = cached_response
                    self._local_cache_timestamps[cache_key] = time.time()
                    # Log the cached execution
                    execution_time = time.time() - start_time
                    await self.logger.log_execution(
                        function_input=kwargs,
                        function_output=cached_response,
                        llm_input=user_prompt,
                        llm_output=json.dumps(cached_response),
                        function_version=self.version,
                        response_metadata={'cache_hit': True, 'cache_source': 'redis'},
                        execution_time=execution_time
                    )
                    
                    # Track analytics for cache hit
                    analytics_engine = await get_analytics_engine()
                    program_name = Path(self.program_path).stem
                    await analytics_engine.track_llm_call(
                        program_name=program_name,
                        model_name=self.config['model']['name'],
                        execution_time_ms=int(execution_time * 1000),
                        cache_hit=True,
                        user_id="unknown"
                    )
                    await analytics_engine.track_program_usage(
                        program_name=program_name,
                        execution_time_ms=int(execution_time * 1000),
                        success=True,
                        user_id="unknown",
                        input_params=kwargs
                    )
                    
                    return cached_response
            
            # Prepare messages and tools for API call
            messages = [
                {"role": "system", "content": self.config['system_prompt']},
                {"role": "user", "content": user_prompt}
            ]
            
            # Add tools if available
            tools_config = None
            if self.tools:
                tools_config = [{"type": "function", "function": tool} for tool in self.tools]
            
            # Make the API call
            response = await self.client.chat.completions.create(
                model=self.config['model']['name'],
                messages=messages,
                temperature=self.config['model']['temperature'],
                max_tokens=self.config['model']['max_tokens'],
                response_format={"type": self.config['model']['response_format']},
                tools=tools_config
            )
            
            # Handle tool calls if present
            if response.choices[0].message.tool_calls:
                self.metrics['tool_calls'] += len(response.choices[0].message.tool_calls)
                # Add tool calls to messages
                messages.append(response.choices[0].message)
                
                # Execute tool calls
                for tool_call in response.choices[0].message.tool_calls:
                    # Find the tool function
                    tool = next((t for t in self.tools if t['name'] == tool_call.function.name), None)
                    if tool:
                        try:
                            # Execute the tool function
                            tool_args = json.loads(tool_call.function.arguments)
                            tool_result = await self._execute_tool(tool['name'], tool_args)
                            
                            # Add tool response to messages
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(tool_result)
                            })
                        except Exception as e:
                            logger.error(f"Tool execution failed: {str(e)}")
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps({"error": str(e)})
                            })
                
                # Get final response after tool calls
                response = await self.client.chat.completions.create(
                    model=self.config['model']['name'],
                    messages=messages,
                    temperature=self.config['model']['temperature'],
                    max_tokens=self.config['model']['max_tokens'],
                    response_format={"type": self.config['model']['response_format']}
                )
            
            # Parse and validate response
            result = json.loads(response.choices[0].message.content)
            self._validate_output(result)
            
            # Add usage information to the result
            response_metadata = {}
            if hasattr(response, 'usage'):
                response_metadata['usage'] = {
                    'completion_tokens': response.usage.completion_tokens,
                    'prompt_tokens': response.usage.prompt_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            
            # Update metrics
            execution_time = time.time() - start_time
            self._update_metrics(response, execution_time)
            
            # Track analytics
            analytics_engine = await get_analytics_engine()
            program_name = Path(self.program_path).stem
            
            # Track program usage
            await analytics_engine.track_program_usage(
                program_name=program_name,
                execution_time_ms=int(execution_time * 1000),
                success=True,
                user_id="unknown",  # This could be customized
                input_params=kwargs
            )
            
            # Track LLM call and token usage if available
            if hasattr(response, 'usage'):
                await analytics_engine.track_llm_call(
                    program_name=program_name,
                    model_name=self.config['model']['name'],
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    execution_time_ms=int(execution_time * 1000),
                    cache_hit=False,  # This is a new call, not a cache hit
                    user_id="unknown"
                )
                
                # Calculate cost estimate (simplified)
                # GPT-4 pricing as of 2023: $0.03/1K prompt tokens, $0.06/1K completion tokens
                cost_estimate = (
                    (response.usage.prompt_tokens / 1000) * 0.03 +
                    (response.usage.completion_tokens / 1000) * 0.06
                )
                
                await analytics_engine.track_token_usage(
                    program_name=program_name,
                    model_name=self.config['model']['name'],
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    user_id="unknown",
                    cost_estimate=cost_estimate
                )
            
            # Cache the result if caching is enabled
            if self.cache_manager:
                await self.cache_manager.set(cache_key, result)
                # Update local cache
                self._local_cache[cache_key] = result
                self._local_cache_timestamps[cache_key] = time.time()
            
            # Log the execution
            log_id = await self.logger.log_execution(
                function_input=kwargs,
                function_output=result,
                llm_input=user_prompt,
                llm_output=json.dumps(result),
                function_version=self.version,
                response_metadata=response_metadata,
                execution_time=execution_time
            )
            
            # Add log ID to the result
            result['log_id'] = log_id
            
            logger.info(f"Program {self.program_path} executed successfully in {execution_time:.2f}s")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            raise LLMProgramError(f"Failed to parse LLM response as JSON: {str(e)}")
        except Exception as e:
            logger.error(f"LLM program execution failed: {str(e)}")
            
            # Track analytics for failed execution
            try:
                execution_time = time.time() - start_time
                analytics_engine = await get_analytics_engine()
                program_name = Path(self.program_path).stem
                await analytics_engine.track_program_usage(
                    program_name=program_name,
                    execution_time_ms=int(execution_time * 1000),
                    success=False,
                    error_message=str(e),
                    user_id="unknown",
                    input_params=kwargs
                )
            except Exception as analytics_error:
                logger.error(f"Failed to track analytics for failed execution: {str(analytics_error)}")
            
            raise LLMProgramError(f"LLM program execution failed: {str(e)}")
    
    async def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool function.
        
        Args:
            tool_name: Name of the tool to execute
            args: Arguments for the tool function
            
        Returns:
            Result of the tool execution
        """
        # Find the tool function
        tool = next((t for t in self.tools if t['name'] == tool_name), None)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        
        # Execute the tool function
        if 'function' in tool:
            return await tool['function'](**args)
        else:
            raise ValueError(f"Tool {tool_name} has no function implementation")
    
    async def stream(self, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute the LLM program with streaming support."""
        try:
            # Validate input against schema
            self._validate_input(kwargs)
            
            # Render the template
            user_prompt = self._render_template(**kwargs)
            
            # Prepare messages and tools for API call
            messages = [
                {"role": "system", "content": self.config['system_prompt']},
                {"role": "user", "content": user_prompt}
            ]
            
            # Add tools if available
            tools_config = None
            if self.tools:
                tools_config = [{"type": "function", "function": tool} for tool in self.tools]
            
            # Make the streaming API call
            stream = await self.client.chat.completions.create(
                model=self.config['model']['name'],
                messages=messages,
                temperature=self.config['model']['temperature'],
                max_tokens=self.config['model']['max_tokens'],
                stream=True,
                tools=tools_config
            )
            
            # Track tool calls
            current_tool_calls = []
            current_tool_call_id = None
            
            # Stream the responses
            async for chunk in stream:
                if chunk.choices[0].delta.tool_calls:
                    # Handle tool call deltas
                    for tool_call in chunk.choices[0].delta.tool_calls:
                        if tool_call.id:
                            current_tool_call_id = tool_call.id
                            current_tool_calls.append({
                                'id': tool_call.id,
                                'name': tool_call.function.name,
                                'arguments': tool_call.function.arguments
                            })
                        elif current_tool_call_id:
                            # Append to existing tool call arguments
                            for tc in current_tool_calls:
                                if tc['id'] == current_tool_call_id:
                                    tc['arguments'] += tool_call.function.arguments
                    
                    # If we have complete tool calls, execute them
                    if current_tool_calls:
                        for tool_call in current_tool_calls:
                            try:
                                # Execute the tool function
                                tool_args = json.loads(tool_call['arguments'])
                                tool_result = await self._execute_tool(tool_call['name'], tool_args)
                                
                                # Add tool response to messages
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call['id'],
                                    "content": json.dumps(tool_result)
                                })
                                
                                # Yield tool result
                                yield {
                                    "type": "tool_result",
                                    "tool_name": tool_call['name'],
                                    "result": tool_result
                                }
                            except Exception as e:
                                logger.error(f"Tool execution failed: {str(e)}")
                                yield {
                                    "type": "tool_error",
                                    "tool_name": tool_call['name'],
                                    "error": str(e)
                                }
                        
                        # Clear tool calls after execution
                        current_tool_calls = []
                        current_tool_call_id = None
                
                elif chunk.choices[0].delta.content:
                    try:
                        # Try to parse each chunk as JSON
                        result = json.loads(chunk.choices[0].delta.content)
                        yield {
                            "type": "content",
                            "data": result
                        }
                    except json.JSONDecodeError:
                        # If not valid JSON, yield the raw content
                        yield {
                            "type": "content",
                            "data": {"content": chunk.choices[0].delta.content}
                        }
            
        except Exception as e:
            logger.error(f"Streaming execution failed: {str(e)}")
            raise LLMProgramError(f"Streaming execution failed: {str(e)}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get the current program metrics."""
        return self.metrics
    
    async def clear_cache(self, pattern: str = "llm_cache:*") -> None:
        """Clear cache entries matching the pattern."""
        if self.cache_manager:
            await self.cache_manager.clear(pattern)
        # Clear local cache
        self._local_cache.clear()
        self._local_cache_timestamps.clear()

    def __del__(self):
        """Cleanup thread pool on object destruction."""
        if hasattr(self, '_thread_pool'):
            self._thread_pool.shutdown(wait=False)
        # Ensure client is closed
        if hasattr(self, 'client'):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self.client.close())
                else:
                    loop.run_until_complete(self.client.close())
            except RuntimeError:
                # No event loop available, can't clean up async resources
                pass

async def load_program(program_name: str) -> LLMProgram:
    """Load an LLM program by name.
    
    Args:
        program_name: Name of the program file (without .yaml extension)
        
    Returns:
        An async context manager that yields an LLMProgram instance
        
    Example:
        async with await load_program("analyze_content") as program:
            result = await program(**kwargs)
    """
    program_path = Path(__file__).parent / f"{program_name}.yaml"
    if not program_path.exists():
        raise FileNotFoundError(f"Program {program_name} not found at {program_path}")
    return LLMProgram(str(program_path)) 
