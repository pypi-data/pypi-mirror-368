

import argparse
import sqlite3
import json

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

def main():
    parser = argparse.ArgumentParser(description='LLM Program CLI')
    subparsers = parser.add_subparsers(dest='command')

    # generate-dataset command
    parser_generate_dataset = subparsers.add_parser('generate-dataset', help='Generate an instruction dataset for LLM fine-tuning.')
    parser_generate_dataset.add_argument('database_path', help='The path to the SQLite database file.')
    parser_generate_dataset.add_argument('output_path', help='The path to write the generated dataset to.')

    args = parser.parse_args()

    if args.command == 'generate-dataset':
        generate_dataset(args.database_path, args.output_path)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

