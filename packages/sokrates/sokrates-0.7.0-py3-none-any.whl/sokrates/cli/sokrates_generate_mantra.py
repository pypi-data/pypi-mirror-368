#!/usr/bin/env python3
"""
Python Script to generate a daily mantra and practical call to action utilizing a LLM via REST Endpoint (OpenAI Compatible API)
"""
import argparse
from pathlib import Path

from ..colors import Colors
from ..config import Config
from ..refinement_workflow import RefinementWorkflow
from ..output_printer import OutputPrinter

def main():
    """Main function to handle command line arguments and orchestrate the process."""
    
    # Print beautiful header
    OutputPrinter.print_header("🤖 DAILY MANTRA GENERATOR 🌱", Colors.BRIGHT_CYAN, 60)
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Generates a daily mantra with a matching practical call to action',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # TODO: use parameter below
    parser.add_argument(
        '--context-directory', '-c',
        required=False,
        help='Path to a directoy with text/markdown files to add to the context'
    )
    
    parser.add_argument(
        '--generation-prompt-file', '-g',
        required=False,
        help='Path to a file containing with markdown files to add to the context'
    )
    
    parser.add_argument(
        '--api-endpoint',
        required=False,
        default=Config().api_endpoint,
        help=f"LLM server API endpoint. Default is {Config.DEFAULT_API_ENDPOINT}"
    )
    
    parser.add_argument(
        '--api-key',
        default=Config().api_key,
        help='API key for authentication (many local servers don\'t require this)'
    )
    
    parser.add_argument(
        '--model', '-m',
        default=Config().default_model,
        help=f"A model name to use for the generation (default: {Config.DEFAULT_MODEL})."
    )
    
    parser.add_argument(
        '--max-tokens', '-mt',
        type=int,
        default=4000,
        help='Maximum tokens in response (default: 4000)'
    )
    
    parser.add_argument(
        '--temperature', '-t',
        type=float,
        default=Config().default_model_temperature,
        help='Temperature for response generation (default: 0.7)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with debug information'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output filename to save the response (e.g., response.md)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    config = Config(verbose=args.verbose)
    
    api_endpoint = args.api_endpoint
    if not api_endpoint:
        api_endpoint = config.api_endpoint
    
    api_key = args.api_key
    if not api_key:
        api_key = config.api_key
        
    model = args.model
    if not model:
        model = config.default_model
    
# TODO: Implement all parameters and error handling
    # TODO: Implement all parameters and error handling....
    workflow = RefinementWorkflow(api_endpoint=api_endpoint, api_key=api_key, 
        verbose=args.verbose, model=model,
        temperature=args.temperature, max_tokens=args.max_tokens)
    
    context_files = [
        Path(f"{Path(__file__).parent.parent.resolve()}/prompts/context/self-improvement-principles-v1.md").resolve()
    ]
    generated = workflow.generate_mantra(context_files=context_files)
    if args.verbose:
        OutputPrinter.print_info("context_files", context_files)

    OutputPrinter.print_section(f"✨ YOUR MANTRA FOR TODAY ✨\n", Colors.BRIGHT_MAGENTA, "═")
    print(f"{Colors.WHITE}{generated}{Colors.RESET}")
    
    
if __name__ == "__main__":
    main()
    