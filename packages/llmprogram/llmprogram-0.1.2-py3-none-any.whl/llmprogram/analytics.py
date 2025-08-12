"""Analytics module for tracking LLM program usage with DuckDB."""

import json
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import asyncio
import logging

# Try to import duckdb, but make it optional
try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    duckdb = None
    DUCKDB_AVAILABLE = False

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Event-driven analytics engine using DuckDB."""
    
    def __init__(self, db_path: str = "llmprogram_analytics.duckdb"):
        """Initialize the analytics engine.
        
        Args:
            db_path: Path to the DuckDB database file
        """
        if not DUCKDB_AVAILABLE:
            logger.warning("DuckDB not available. Analytics will not be recorded.")
            self._available = False
            return
            
        self.db_path = db_path
        self._initialized = False
        self._queue = asyncio.Queue()
        self._worker_task = None
        self._shutdown_event = asyncio.Event()
        self._available = True
        self._ensure_initialized()
    
    def _ensure_initialized(self):
        """Ensure the database and tables are initialized."""
        if not self._available or self._initialized:
            return
            
        try:
            # Create connection and initialize schema
            conn = duckdb.connect(self.db_path)
            
            # Create tables for analytics
            conn.execute("""
                CREATE TABLE IF NOT EXISTS llm_calls (
                    id VARCHAR PRIMARY KEY,
                    timestamp TIMESTAMP,
                    program_name VARCHAR,
                    model_name VARCHAR,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    total_tokens INTEGER,
                    execution_time_ms INTEGER,
                    cache_hit BOOLEAN,
                    user_id VARCHAR,
                    metadata JSON
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS program_usage (
                    id VARCHAR PRIMARY KEY,
                    timestamp TIMESTAMP,
                    program_name VARCHAR,
                    user_id VARCHAR,
                    execution_time_ms INTEGER,
                    success BOOLEAN,
                    error_message VARCHAR,
                    input_params JSON
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS token_usage (
                    id VARCHAR PRIMARY KEY,
                    timestamp TIMESTAMP,
                    program_name VARCHAR,
                    model_name VARCHAR,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    total_tokens INTEGER,
                    user_id VARCHAR,
                    cost_estimate FLOAT
                )
            """)
            
            conn.close()
            self._initialized = True
            
            # Start the background worker
            self._worker_task = asyncio.create_task(self._process_queue())
        except Exception as e:
            logger.error(f"Failed to initialize analytics engine: {str(e)}")
            self._available = False
    
    async def _process_queue(self):
        """Process queued analytics events in the background."""
        if not self._available:
            return
            
        while not self._shutdown_event.is_set():
            try:
                # Use wait_for to periodically check shutdown event
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                try:
                    self._process_event(event)
                except Exception as e:
                    logger.error(f"Failed to process analytics event: {str(e)}")
                finally:
                    self._queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in analytics queue processing: {str(e)}")
                continue
    
    def _process_event(self, event: Dict[str, Any]):
        """Process a single analytics event."""
        if not self._available:
            return
            
        event_type = event.get('type')
        conn = duckdb.connect(self.db_path)
        
        try:
            if event_type == 'llm_call':
                conn.execute("""
                    INSERT INTO llm_calls VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event['id'],
                    event['timestamp'],
                    event['program_name'],
                    event['model_name'],
                    event.get('prompt_tokens', 0),
                    event.get('completion_tokens', 0),
                    event.get('total_tokens', 0),
                    event.get('execution_time_ms', 0),
                    event.get('cache_hit', False),
                    event.get('user_id', 'unknown'),
                    json.dumps(event.get('metadata', {}))
                ))
            elif event_type == 'program_usage':
                conn.execute("""
                    INSERT INTO program_usage VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event['id'],
                    event['timestamp'],
                    event['program_name'],
                    event.get('user_id', 'unknown'),
                    event.get('execution_time_ms', 0),
                    event.get('success', True),
                    event.get('error_message', None),
                    json.dumps(event.get('input_params', {}))
                ))
            elif event_type == 'token_usage':
                conn.execute("""
                    INSERT INTO token_usage VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event['id'],
                    event['timestamp'],
                    event['program_name'],
                    event['model_name'],
                    event.get('prompt_tokens', 0),
                    event.get('completion_tokens', 0),
                    event.get('total_tokens', 0),
                    event.get('user_id', 'unknown'),
                    event.get('cost_estimate', 0.0)
                ))
            
            conn.commit()
        finally:
            conn.close()
    
    async def track_llm_call(self, 
                           program_name: str,
                           model_name: str,
                           prompt_tokens: int = 0,
                           completion_tokens: int = 0,
                           total_tokens: int = 0,
                           execution_time_ms: int = 0,
                           cache_hit: bool = False,
                           user_id: str = "unknown",
                           metadata: Optional[Dict[str, Any]] = None):
        """Track an LLM call event."""
        if not self._available:
            return
            
        await self._ensure_initialized()
        event = {
            'type': 'llm_call',
            'id': f"llm_{int(time.time() * 1000000)}",
            'timestamp': datetime.now().isoformat(),
            'program_name': program_name,
            'model_name': model_name,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens,
            'execution_time_ms': execution_time_ms,
            'cache_hit': cache_hit,
            'user_id': user_id,
            'metadata': metadata or {}
        }
        await self._queue.put(event)
    
    async def track_program_usage(self,
                                program_name: str,
                                execution_time_ms: int = 0,
                                success: bool = True,
                                error_message: Optional[str] = None,
                                user_id: str = "unknown",
                                input_params: Optional[Dict[str, Any]] = None):
        """Track a program usage event."""
        if not self._available:
            return
            
        await self._ensure_initialized()
        event = {
            'type': 'program_usage',
            'id': f"prog_{int(time.time() * 1000000)}",
            'timestamp': datetime.now().isoformat(),
            'program_name': program_name,
            'execution_time_ms': execution_time_ms,
            'success': success,
            'error_message': error_message,
            'user_id': user_id,
            'input_params': input_params or {}
        }
        await self._queue.put(event)
    
    async def track_token_usage(self,
                              program_name: str,
                              model_name: str,
                              prompt_tokens: int = 0,
                              completion_tokens: int = 0,
                              total_tokens: int = 0,
                              user_id: str = "unknown",
                              cost_estimate: float = 0.0):
        """Track token usage event."""
        if not self._available:
            return
            
        await self._ensure_initialized()
        event = {
            'type': 'token_usage',
            'id': f"tok_{int(time.time() * 1000000)}",
            'timestamp': datetime.now().isoformat(),
            'program_name': program_name,
            'model_name': model_name,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens,
            'user_id': user_id,
            'cost_estimate': cost_estimate
        }
        await self._queue.put(event)
    
    def get_llm_call_stats(self, 
                          program_name: Optional[str] = None,
                          model_name: Optional[str] = None,
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get LLM call statistics."""
        if not self._available:
            return []
            
        conn = duckdb.connect(self.db_path)
        try:
            query = """
                SELECT 
                    program_name,
                    model_name,
                    COUNT(*) as call_count,
                    SUM(prompt_tokens) as total_prompt_tokens,
                    SUM(completion_tokens) as total_completion_tokens,
                    SUM(total_tokens) as total_tokens,
                    AVG(execution_time_ms) as avg_execution_time_ms,
                    SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_hits,
                    COUNT(DISTINCT user_id) as unique_users
                FROM llm_calls
                WHERE 1=1
            """
            
            params = []
            if program_name:
                query += " AND program_name = ?"
                params.append(program_name)
            if model_name:
                query += " AND model_name = ?"
                params.append(model_name)
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            query += " GROUP BY program_name, model_name"
            
            result = conn.execute(query, params).fetchall()
            
            # Convert to list of dicts
            columns = ['program_name', 'model_name', 'call_count', 'total_prompt_tokens', 
                      'total_completion_tokens', 'total_tokens', 'avg_execution_time_ms', 
                      'cache_hits', 'unique_users']
            return [dict(zip(columns, row)) for row in result]
        finally:
            conn.close()
    
    def get_program_usage_stats(self,
                               program_name: Optional[str] = None,
                               start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get program usage statistics."""
        if not self._available:
            return []
            
        conn = duckdb.connect(self.db_path)
        try:
            query = """
                SELECT 
                    program_name,
                    COUNT(*) as usage_count,
                    COUNT(CASE WHEN success THEN 1 END) as successful_calls,
                    COUNT(CASE WHEN NOT success THEN 1 END) as failed_calls,
                    AVG(execution_time_ms) as avg_execution_time_ms,
                    COUNT(DISTINCT user_id) as unique_users
                FROM program_usage
                WHERE 1=1
            """
            
            params = []
            if program_name:
                query += " AND program_name = ?"
                params.append(program_name)
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            query += " GROUP BY program_name"
            
            result = conn.execute(query, params).fetchall()
            
            # Convert to list of dicts
            columns = ['program_name', 'usage_count', 'successful_calls', 'failed_calls', 
                      'avg_execution_time_ms', 'unique_users']
            return [dict(zip(columns, row)) for row in result]
        finally:
            conn.close()
    
    def get_token_usage_stats(self,
                             program_name: Optional[str] = None,
                             model_name: Optional[str] = None,
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get token usage statistics."""
        if not self._available:
            return []
            
        conn = duckdb.connect(self.db_path)
        try:
            query = """
                SELECT 
                    program_name,
                    model_name,
                    SUM(prompt_tokens) as total_prompt_tokens,
                    SUM(completion_tokens) as total_completion_tokens,
                    SUM(total_tokens) as total_tokens,
                    SUM(cost_estimate) as total_cost_estimate,
                    COUNT(DISTINCT user_id) as unique_users
                FROM token_usage
                WHERE 1=1
            """
            
            params = []
            if program_name:
                query += " AND program_name = ?"
                params.append(program_name)
            if model_name:
                query += " AND model_name = ?"
                params.append(model_name)
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            query += " GROUP BY program_name, model_name"
            
            result = conn.execute(query, params).fetchall()
            
            # Convert to list of dicts
            columns = ['program_name', 'model_name', 'total_prompt_tokens', 
                      'total_completion_tokens', 'total_tokens', 'total_cost_estimate', 
                      'unique_users']
            return [dict(zip(columns, row)) for row in result]
        finally:
            conn.close()
    
    async def close(self):
        """Close the analytics engine and wait for pending operations."""
        if not self._available or not self._worker_task:
            return
            
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


# Global analytics engine instance
_analytics_engine: Optional[AnalyticsEngine] = None


async def get_analytics_engine(db_path: str = "llmprogram_analytics.duckdb") -> AnalyticsEngine:
    """Get the global analytics engine instance."""
    global _analytics_engine
    if _analytics_engine is None:
        _analytics_engine = AnalyticsEngine(db_path)
    return _analytics_engine


async def close_analytics_engine():
    """Close the global analytics engine."""
    global _analytics_engine
    if _analytics_engine is not None:
        await _analytics_engine.close()
        _analytics_engine = None