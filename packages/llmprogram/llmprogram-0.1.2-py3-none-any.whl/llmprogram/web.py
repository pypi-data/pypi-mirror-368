"""Web service module for exposing LLM programs as FastAPI endpoints."""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, create_model
import uvicorn

from llmprogram.LLMProgram import LLMProgram
from llmprogram.analytics import get_analytics_engine


class ProgramInfo(BaseModel):
    """Information about a program."""
    name: str
    description: Optional[str] = None
    version: Optional[str] = None


class ProgramRequest(BaseModel):
    """Request model for program execution."""
    inputs: Dict[str, Any]
    stream: bool = False


class ProgramResponse(BaseModel):
    """Response model for program execution."""
    result: Dict[str, Any]
    log_id: Optional[str] = None


class AnalyticsFilter(BaseModel):
    """Filter parameters for analytics queries."""
    program_name: Optional[str] = None
    model_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class LLMCallStats(BaseModel):
    """Statistics for LLM calls."""
    program_name: str
    model_name: str
    call_count: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    avg_execution_time_ms: float
    cache_hits: int
    unique_users: int


class ProgramUsageStats(BaseModel):
    """Statistics for program usage."""
    program_name: str
    usage_count: int
    successful_calls: int
    failed_calls: int
    avg_execution_time_ms: float
    unique_users: int


class TokenUsageStats(BaseModel):
    """Statistics for token usage."""
    program_name: str
    model_name: str
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    total_cost_estimate: float
    unique_users: int


def create_pydantic_model_from_schema(schema: Dict[str, Any], model_name: str) -> BaseModel:
    """Create a Pydantic model from a JSON schema."""
    # This is a simplified implementation that handles basic types
    # A full implementation would need to handle all JSON schema features
    properties = schema.get('properties', {})
    required = set(schema.get('required', []))
    
    fields = {}
    for prop_name, prop_schema in properties.items():
        prop_type = prop_schema.get('type')
        is_required = prop_name in required
        
        # Map JSON schema types to Python types
        if prop_type == 'string':
            field_type = str
        elif prop_type == 'integer':
            field_type = int
        elif prop_type == 'number':
            field_type = float
        elif prop_type == 'boolean':
            field_type = bool
        elif prop_type == 'array':
            field_type = List[Any]  # Simplified
        elif prop_type == 'object':
            field_type = Dict[str, Any]  # Simplified
        else:
            field_type = Any
            
        # Handle optional fields
        if not is_required:
            field_type = Optional[field_type]
            
        fields[prop_name] = (field_type, ...)
        
    return create_model(model_name, **fields)


def load_programs_from_directory(directory: str) -> Dict[str, LLMProgram]:
    """Load all LLM programs from a directory of YAML files."""
    programs = {}
    dir_path = Path(directory)
    
    if not dir_path.exists():
        raise ValueError(f"Directory {directory} does not exist")
        
    for yaml_file in dir_path.glob("*.yaml"):
        try:
            program_name = yaml_file.stem  # filename without extension
            program = LLMProgram(str(yaml_file))
            programs[program_name] = program
        except Exception as e:
            print(f"Warning: Could not load program from {yaml_file}: {e}")
            
    for yml_file in dir_path.glob("*.yml"):
        try:
            program_name = yml_file.stem  # filename without extension
            program = LLMProgram(str(yml_file))
            programs[program_name] = program
        except Exception as e:
            print(f"Warning: Could not load program from {yml_file}: {e}")
            
    return programs


def create_app(programs_directory: str, analytics_db_path: str = "llmprogram_analytics.duckdb") -> FastAPI:
    """Create a FastAPI app with endpoints for all programs in the directory."""
    app = FastAPI(
        title="LLM Program API",
        description="API for running LLM programs defined in YAML files",
        version="0.1.0"
    )
    
    # Load programs
    try:
        programs = load_programs_from_directory(programs_directory)
    except Exception as e:
        print(f"Error loading programs: {e}")
        programs = {}
    
    # Store programs and analytics engine in app state
    app.state.programs = programs
    app.state.analytics_db_path = analytics_db_path
    
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "LLM Program API",
            "programs": list(programs.keys()),
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    
    @app.get("/programs", response_model=List[ProgramInfo])
    async def list_programs():
        """List all available programs."""
        program_infos = []
        for name, program in programs.items():
            try:
                config = program.config
                program_infos.append(ProgramInfo(
                    name=name,
                    description=config.get('description'),
                    version=config.get('version')
                ))
            except Exception:
                # If we can't get the config, still include the program
                program_infos.append(ProgramInfo(name=name))
        return program_infos
    
    @app.get("/programs/{program_name}")
    async def get_program_info(program_name: str):
        """Get detailed information about a specific program."""
        if program_name not in programs:
            raise HTTPException(status_code=404, detail="Program not found")
            
        program = programs[program_name]
        try:
            return program.config
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting program info: {e}")
    
    # Create endpoints for each program
    for program_name, program in programs.items():
        # Create endpoint for this program
        @app.post(f"/programs/{program_name}/run", 
                  response_model=ProgramResponse,
                  name=f"run_{program_name}",
                  description=f"Run the {program_name} program")
        async def run_program(
            program_name: str = program_name,  # Capture the program_name in closure
            request: ProgramRequest = None
        ):
            if program_name not in programs:
                raise HTTPException(status_code=404, detail="Program not found")
                
            program = programs[program_name]
            inputs = request.inputs if request else {}
            
            try:
                # Run the program
                result = await program(**inputs)
                return ProgramResponse(result=result)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error running program: {e}")
    
    # Analytics endpoints
    @app.get("/analytics/llm-calls", response_model=List[LLMCallStats])
    async def get_llm_call_stats(filter: AnalyticsFilter = None):
        """Get LLM call statistics."""
        try:
            analytics_engine = await get_analytics_engine(app.state.analytics_db_path)
            stats = analytics_engine.get_llm_call_stats(
                program_name=filter.program_name if filter else None,
                model_name=filter.model_name if filter else None,
                start_date=filter.start_date if filter else None,
                end_date=filter.end_date if filter else None
            )
            return [LLMCallStats(**stat) for stat in stats]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting LLM call stats: {e}")
    
    @app.get("/analytics/program-usage", response_model=List[ProgramUsageStats])
    async def get_program_usage_stats(filter: AnalyticsFilter = None):
        """Get program usage statistics."""
        try:
            analytics_engine = await get_analytics_engine(app.state.analytics_db_path)
            stats = analytics_engine.get_program_usage_stats(
                program_name=filter.program_name if filter else None,
                start_date=filter.start_date if filter else None,
                end_date=filter.end_date if filter else None
            )
            return [ProgramUsageStats(**stat) for stat in stats]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting program usage stats: {e}")
    
    @app.get("/analytics/token-usage", response_model=List[TokenUsageStats])
    async def get_token_usage_stats(filter: AnalyticsFilter = None):
        """Get token usage statistics."""
        try:
            analytics_engine = await get_analytics_engine(app.state.analytics_db_path)
            stats = analytics_engine.get_token_usage_stats(
                program_name=filter.program_name if filter else None,
                model_name=filter.model_name if filter else None,
                start_date=filter.start_date if filter else None,
                end_date=filter.end_date if filter else None
            )
            return [TokenUsageStats(**stat) for stat in stats]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting token usage stats: {e}")
    
    return app


def run_server(
    programs_directory: str = "examples",
    analytics_db_path: str = "llmprogram_analytics.duckdb",
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False
):
    """Run the FastAPI server."""
    app = create_app(programs_directory, analytics_db_path)
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run LLM Program web service")
    parser.add_argument(
        "--directory",
        "-d",
        default="examples",
        help="Directory containing program YAML files"
    )
    parser.add_argument(
        "--analytics-db",
        default="llmprogram_analytics.duckdb",
        help="Path to the analytics database"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the server to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes"
    )
    
    args = parser.parse_args()
    run_server(
        programs_directory=args.directory,
        analytics_db_path=args.analytics_db,
        host=args.host,
        port=args.port,
        reload=args.reload
    )