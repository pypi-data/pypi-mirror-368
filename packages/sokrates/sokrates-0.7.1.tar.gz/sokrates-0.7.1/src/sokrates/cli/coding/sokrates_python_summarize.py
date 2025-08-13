#!/usr/bin/env python3
"""
LM Studio Benchmark Script
Benchmarks LLM performance through LM Studio's OpenAI-compatible API
"""

import argparse
import os
from ...coding.python_analyzer import PythonAnalyzer
from ...output_printer import OutputPrinter
from ...colors import Colors

def main():
    """Main execution function"""
    OutputPrinter.print_header("🚀 Python summarize code 🚀", Colors.BRIGHT_CYAN, 50)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Create a summary document for a given python source code directory.')
    parser.add_argument('--source-directory', '-sd', type=str, required=True,
                       help='Directory containing python code files to summarize')
    parser.add_argument('--output', '-o', type=str, required=True,
                       help='Destination of the summary document to generate')
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output for the script execution'
    )
    args = parser.parse_args()
    PythonAnalyzer.create_markdown_documentation_for_directory(directory_path=args.source_directory, 
                                                               target_file=args.output, verbose=args.verbose)
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()