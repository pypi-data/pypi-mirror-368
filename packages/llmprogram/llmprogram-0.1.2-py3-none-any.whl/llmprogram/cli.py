

import argparse
import sqlite3
import json
import yaml
import asyncio
import sys
from pathlib import Path

# Add the parent directory to sys.path to import LLMProgram
sys.path.append(str(Path(__file__).parent.parent))

from llmprogram.LLMProgram import LLMProgram
from llmprogram.analytics import get_analytics_engine


def generate_dataset(db_path, output_path):
    """Generates a dataset for LLM fine-tuning from a SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT llm_input, llm_output FROM program_logs")
    rows = cursor.fetchall()
    conn.close()

    with open(output_path, 'w') as f:
        for row in rows:
            llm_input, llm_output = row
            # The llm_input is a combination of the system prompt and the user prompt.
            # We can use this as the "instruction" for fine-tuning.
            instruction = llm_input
            output = llm_output

            dataset_entry = {
                "instruction": instruction,
                "output": output
            }
            f.write(json.dumps(dataset_entry) + '\n')


def load_inputs(input_path):
    """Load inputs from a JSON or YAML file."""
    with open(input_path, 'r') as f:
        if input_path.endswith('.yaml') or input_path.endswith('.yml'):
            return yaml.safe_load(f)
        else:
            return json.load(f)


async def run_program(program_path, inputs, output_path=None, stream=False):
    """Run an LLM program with the given inputs."""
    try:
        # Load inputs from file if provided
        if isinstance(inputs, str):
            inputs = load_inputs(inputs)
        
        # If inputs is a list, run in batch mode
        if isinstance(inputs, list):
            print(f"Running batch processing with {len(inputs)} inputs...")
            async with LLMProgram(program_path) as program:
                results = await program.batch_process(inputs)
        else:
            # Run in single mode
            async with LLMProgram(program_path) as program:
                if stream:
                    print("Streaming response:")
                    results = []
                    async for chunk in program.stream(**inputs):
                        if chunk['type'] == 'content':
                            print(json.dumps(chunk['data'], indent=2))
                            results.append(chunk['data'])
                        elif chunk['type'] == 'tool_result':
                            print(f"Tool '{chunk['tool_name']}' result: {chunk['result']}")
                        elif chunk['type'] == 'tool_error':
                            print(f"Tool '{chunk['tool_name']}' error: {chunk['error']}")
                else:
                    results = await program(**inputs)
        
        # Output results
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {output_path}")
        else:
            if not stream:
                print(json.dumps(results, indent=2))
                
    except Exception as e:
        print(f"Error running program: {str(e)}", file=sys.stderr)
        sys.exit(1)


async def generate_yaml_program(description, example_input=None, example_output=None, 
                               output_path=None, api_key=None):
    """Generate a YAML program file based on user input."""
    try:
        # Use the built-in yaml_generator program
        yaml_generator_path = Path(__file__).parent / "../examples/yaml_generator.yaml"
        if not yaml_generator_path.exists():
            # If the yaml_generator.yaml doesn't exist, create it inline
            yaml_generator_config = {
                "name": "yaml_generator",
                "description": "Generates LLM program YAML files based on user descriptions",
                "version": "1.0.0",
                "model": {
                    "provider": "openai",
                    "name": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "response_format": "json_object"
                },
                "system_prompt": """You are an expert at creating LLM program configurations in YAML format.
Your task is to generate a complete, valid YAML configuration for an LLM program based on a user's description.

The YAML should include:
1. A descriptive name (kebab-case)
2. A clear description
3. Version (starting at 1.0.0)
4. Model configuration with provider, name, temperature, max_tokens, and response_format
5. A well-crafted system prompt that guides the LLM
6. Input schema using JSON Schema to validate inputs
7. Output schema using JSON Schema to validate outputs
8. A Jinja2 template for the user prompt

Guidelines:
- Use gpt-4 or gpt-3.5-turbo as the model name
- Temperature should be between 0.0 and 1.0 (0.7 is a good default for creative tasks)
- max_tokens should be appropriate for the task (500-2000)
- response_format should be "json_object" for structured outputs
- System prompt should be detailed and specific
- Input schema should be comprehensive but not overly complex
- Output schema should define clear, structured responses
- Template should effectively use the input variables
- All fields should be properly formatted YAML

Return ONLY the YAML content as a JSON object with a single "yaml_content" field containing the YAML as a string.""",
                "input_schema": {
                    "type": "object",
                    "required": ["description"],
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "A detailed description of what the LLM program should do"
                        },
                        "example_input": {
                            "type": "string",
                            "description": "An example of the input the program will receive"
                        },
                        "example_output": {
                            "type": "string",
                            "description": "An example of the output the program should generate"
                        }
                    }
                },
                "output_schema": {
                    "type": "object",
                    "required": ["yaml_content"],
                    "properties": {
                        "yaml_content": {
                            "type": "string",
                            "description": "The generated YAML content for the LLM program"
                        }
                    }
                },
                "template": """Create an LLM program configuration based on this description:

Description: {{description}}
{% if example_input %}Example Input: {{example_input}}{% endif %}
{% if example_output %}Example Output: {{example_output}}{% endif %}

Generate a complete, valid YAML configuration following the specified format."""
            }
        else:
            yaml_generator_config = str(yaml_generator_path)
        
        # Prepare inputs for the YAML generator
        generator_inputs = {
            "description": description
        }
        if example_input:
            generator_inputs["example_input"] = example_input
        if example_output:
            generator_inputs["example_output"] = example_output
        
        # Run the YAML generator
        async with LLMProgram(yaml_generator_config, api_key=api_key) as generator:
            result = await generator(**generator_inputs)
        
        # Extract the YAML content
        yaml_content = result["yaml_content"]
        
        # Output the YAML content
        if output_path:
            with open(output_path, 'w') as f:
                f.write(yaml_content)
            print(f"YAML program generated and saved to {output_path}")
        else:
            print(yaml_content)
            
    except Exception as e:
        print(f"Error generating YAML program: {str(e)}", file=sys.stderr)
        sys.exit(1)


async def show_analytics(analytics_db_path, program_name=None, model_name=None):
    """Show analytics data."""
    try:
        analytics_engine = await get_analytics_engine(analytics_db_path)
        
        print("=== LLM Call Statistics ===")
        llm_stats = analytics_engine.get_llm_call_stats(
            program_name=program_name,
            model_name=model_name
        )
        if llm_stats:
            for stat in llm_stats:
                print(f"Program: {stat['program_name']}")
                print(f"  Model: {stat['model_name']}")
                print(f"  Calls: {stat['call_count']}")
                print(f"  Tokens: {stat['total_tokens']} (prompt: {stat['total_prompt_tokens']}, completion: {stat['total_completion_tokens']})")
                print(f"  Avg Execution Time: {stat['avg_execution_time_ms']:.2f}ms")
                print(f"  Cache Hits: {stat['cache_hits']}")
                print(f"  Unique Users: {stat['unique_users']}")
                print()
        else:
            print("No LLM call data found.")
        
        print("=== Program Usage Statistics ===")
        program_stats = analytics_engine.get_program_usage_stats(
            program_name=program_name
        )
        if program_stats:
            for stat in program_stats:
                print(f"Program: {stat['program_name']}")
                print(f"  Usage Count: {stat['usage_count']}")
                print(f"  Successful Calls: {stat['successful_calls']}")
                print(f"  Failed Calls: {stat['failed_calls']}")
                print(f"  Avg Execution Time: {stat['avg_execution_time_ms']:.2f}ms")
                print(f"  Unique Users: {stat['unique_users']}")
                print()
        else:
            print("No program usage data found.")
        
        print("=== Token Usage Statistics ===")
        token_stats = analytics_engine.get_token_usage_stats(
            program_name=program_name,
            model_name=model_name
        )
        if token_stats:
            for stat in token_stats:
                print(f"Program: {stat['program_name']}")
                print(f"  Model: {stat['model_name']}")
                print(f"  Tokens: {stat['total_tokens']} (prompt: {stat['total_prompt_tokens']}, completion: {stat['total_completion_tokens']})")
                print(f"  Estimated Cost: ${stat['total_cost_estimate']:.4f}")
                print(f"  Unique Users: {stat['unique_users']}")
                print()
        else:
            print("No token usage data found.")
            
    except Exception as e:
        print(f"Error showing analytics: {str(e)}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='LLM Program CLI')
    subparsers = parser.add_subparsers(dest='command')

    # generate-dataset command
    parser_generate_dataset = subparsers.add_parser('generate-dataset', help='Generate an instruction dataset for LLM fine-tuning.')
    parser_generate_dataset.add_argument('database_path', help='The path to the SQLite database file.')
    parser_generate_dataset.add_argument('output_path', help='The path to write the generated dataset to.')

    # run command
    parser_run = subparsers.add_parser('run', help='Run an LLM program with inputs.')
    parser_run.add_argument('program_path', help='The path to the program YAML file.')
    parser_run.add_argument('--inputs', '-i', help='Path to JSON/YAML file containing inputs.')
    parser_run.add_argument('--output', '-o', help='Path to output file (default: stdout).')
    parser_run.add_argument('--stream', '-s', action='store_true', help='Stream the response.')
    parser_run.add_argument('--input-json', help='JSON string of inputs.')

    # generate-yaml command
    parser_generate_yaml = subparsers.add_parser('generate-yaml', help='Generate an LLM program YAML file based on description.')
    parser_generate_yaml.add_argument('description', help='Description of what the LLM program should do.')
    parser_generate_yaml.add_argument('--example-input', help='Example of the input the program will receive.')
    parser_generate_yaml.add_argument('--example-output', help='Example of the output the program should generate.')
    parser_generate_yaml.add_argument('--output', '-o', help='Path to output YAML file (default: stdout).')
    parser_generate_yaml.add_argument('--api-key', help='OpenAI API key (optional, defaults to OPENAI_API_KEY env var).')

    # analytics command
    parser_analytics = subparsers.add_parser('analytics', help='Show analytics data.')
    parser_analytics.add_argument('--db-path', default='llmprogram_analytics.duckdb', help='Path to the analytics database.')
    parser_analytics.add_argument('--program', help='Filter by program name.')
    parser_analytics.add_argument('--model', help='Filter by model name.')

    args = parser.parse_args()

    if args.command == 'generate-dataset':
        generate_dataset(args.database_path, args.output_path)
    elif args.command == 'run':
        # Handle inputs
        inputs = {}
        if args.input_json:
            inputs = json.loads(args.input_json)
        elif args.inputs:
            inputs = args.inputs  # Will be loaded in run_program
        else:
            # Try to read from stdin if no input file is provided
            if not sys.stdin.isatty():
                inputs = json.load(sys.stdin)
        
        # Run the program
        asyncio.run(run_program(args.program_path, inputs, args.output, args.stream))
    elif args.command == 'generate-yaml':
        # Generate YAML program
        asyncio.run(generate_yaml_program(
            args.description, 
            args.example_input, 
            args.example_output, 
            args.output,
            args.api_key
        ))
    elif args.command == 'analytics':
        # Show analytics
        asyncio.run(show_analytics(args.db_path, args.program, args.model))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

