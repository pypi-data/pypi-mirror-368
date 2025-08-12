#!/usr/bin/env python3
"""
Command Line Interface for bilateral-truth bilateral factuality evaluation.

This CLI allows users to enter natural language assertions and get back
generalized truth values using various LLM models.
"""

import argparse
import sys
import os
from typing import Optional
from pathlib import Path

from .assertions import Assertion
from .zeta_function import zeta_c, clear_cache, get_cache_size
from .model_router import ModelRouter, get_model_info
from .truth_values import GeneralizedTruthValue


def load_env_file(env_path: Optional[str] = None) -> bool:
    """
    Load environment variables from a .env file.

    Args:
        env_path: Optional path to .env file. If None, looks for .env in current directory
                 and parent directories.

    Returns:
        True if .env file was found and loaded, False otherwise
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        print(
            "Warning: python-dotenv not installed. Install with: pip install python-dotenv"
        )
        return False

    if env_path:
        # Use specified path
        env_file = Path(env_path)
        if env_file.exists():
            load_dotenv(env_file)
            return True
        else:
            print(f"Warning: .env file not found at {env_path}")
            return False
    else:
        # Look for .env file in current directory and parent directories
        current_dir = Path.cwd()

        # Check current directory and up to 3 parent directories
        for i in range(4):
            env_file = current_dir / ".env"
            if env_file.exists():
                load_dotenv(env_file)
                return True
            if current_dir.parent == current_dir:
                break  # Reached filesystem root
            current_dir = current_dir.parent

        return False


def check_api_keys() -> dict:
    """
    Check which API keys are available.

    Returns:
        Dictionary mapping provider names to boolean availability
    """
    keys = {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "openrouter": bool(os.getenv("OPENROUTER_API_KEY")),
    }
    return keys


def show_api_key_status():
    """Display the status of API keys."""
    print("API Key Status:")
    keys = check_api_keys()

    for provider, available in keys.items():
        status = "✓ Available" if available else "✗ Missing"
        env_var = f"{provider.upper()}_API_KEY"
        if provider == "openrouter":
            env_var = "OPENROUTER_API_KEY"
        print(f"  {provider.capitalize()}: {status} ({env_var})")

    if not any(keys.values()):
        print("\nNo API keys found. You can:")
        print("  1. Create a .env file with your API keys")
        print("  2. Set environment variables directly")
        print("  3. Use the mock model for testing: -m mock")
    print()


def format_truth_value(truth_value: GeneralizedTruthValue) -> str:
    """Format a GeneralizedTruthValue for display."""
    # Truth values now use ASCII directly
    u_symbol = truth_value.u.value
    v_symbol = truth_value.v.value

    return f"<{u_symbol},{v_symbol}>"


def interactive_mode(model_name: str, samples: int = 1, tiebreak: str = "random"):
    """Run in interactive mode for continuous evaluation."""
    print("bilateral-truth Interactive Mode")
    print(f"Model: {model_name}")
    if samples > 1:
        print(f"Sampling: {samples} samples with '{tiebreak}' tiebreaking")

    # Check if API key is available for the model
    provider, _ = ModelRouter.get_provider_info(model_name)
    if provider != "mock":
        keys = check_api_keys()
        if not keys.get(provider, False):
            print(f"⚠️  Warning: No API key found for {provider}")
            print(f"   Set {provider.upper()}_API_KEY in environment or .env file")

    print("Enter natural language assertions to evaluate. Type 'quit' to exit.\n")

    try:
        evaluator = ModelRouter.create_evaluator(model_name)
    except Exception as e:
        print(f"Error creating evaluator: {e}")
        if "API key" in str(e):
            print("Hint: Use --api-keys to check your API key status")
        return 1

    while True:
        try:
            # Get user input
            assertion_text = input("Assertion: ").strip()

            if not assertion_text:
                continue

            if assertion_text.lower() in ["quit", "exit", "q"]:
                break

            if assertion_text.lower() in ["help", "h"]:
                print("\nCommands:")
                print("  help, h     - Show this help")
                print("  cache       - Show cache information")
                print("  clear       - Clear the cache")
                print("  quit, q     - Exit interactive mode")
                print()
                continue

            if assertion_text.lower() == "cache":
                print(f"Cache size: {get_cache_size()} entries\n")
                continue

            if assertion_text.lower() == "clear":
                clear_cache()
                print("Cache cleared.\n")
                continue

            # Evaluate the assertion
            assertion = Assertion(assertion_text)
            print(f"Evaluating: '{assertion}'")
            if samples > 1:
                print(f"Taking {samples} samples...")

            try:
                result = zeta_c(
                    assertion,
                    evaluator.evaluate_bilateral,
                    samples=samples,
                    tiebreak_strategy=tiebreak,
                )
                print(f"Result: {format_truth_value(result)}\n")
            except Exception as e:
                print(f"Evaluation error: {e}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break

    return 0


def single_evaluation(
    assertion_text: str,
    model_name: str,
    verbose: bool = False,
    samples: int = 1,
    tiebreak: str = "random",
) -> int:
    """Evaluate a single assertion and print the result."""
    try:
        evaluator = ModelRouter.create_evaluator(model_name)
    except Exception as e:
        print(f"Error creating evaluator: {e}")
        if "API key" in str(e):
            print("Hint: Use --api-keys to check your API key status")
        return 1

    assertion = Assertion(assertion_text)

    if verbose:
        print(f"Model: {model_name}")
        print(f"Assertion: '{assertion}'")
        if samples > 1:
            print(f"Samples: {samples} (tiebreak: {tiebreak})")
        print("Evaluating...")

    try:
        result = zeta_c(
            assertion,
            evaluator.evaluate_bilateral,
            samples=samples,
            tiebreak_strategy=tiebreak,
        )

        if verbose:
            print(f"Result: {format_truth_value(result)}")
        else:
            print(format_truth_value(result))

        return 0
    except Exception as e:
        print(f"Evaluation error: {e}")
        return 1


def list_models():
    """List all available models."""
    print("Available Models:\n")

    models = ModelRouter.list_available_models()
    for provider, model_list in models.items():
        print(f"{provider.upper()}:")
        for model in model_list:
            print(f"  {model}")
        print()

    print("Aliases:")
    aliases = ModelRouter.list_aliases()
    for alias, canonical in aliases.items():
        print(f"  {alias} → {canonical}")


def show_model_info(model_name: str):
    """Show information about a specific model."""
    print(get_model_info(model_name))


def main():
    """Main CLI entry point."""
    # Try to load .env file before parsing arguments
    load_env_file()

    parser = argparse.ArgumentParser(
        description="bilateral-truth - Bilateral Factuality Evaluation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode with GPT-4
  %(prog)s --model gpt-4 --interactive
  
  # Evaluate single assertion with Claude
  %(prog)s --model claude "The capital of France is Paris"
  
  # Use majority voting with 5 samples
  %(prog)s --model llama3 --samples 5 "Climate change is real"
  
  # Use pessimistic tiebreaking with 4 samples
  %(prog)s --model gpt4 --samples 4 --tiebreak pessimistic "The Earth is round"
  
  # Interactive mode with sampling
  %(prog)s --model mixtral --samples 3 --tiebreak random --interactive
  
  # Check API key status
  %(prog)s --api-keys
  
  # List available models
  %(prog)s --list-models
        """,
    )

    parser.add_argument(
        "assertion", nargs="?", help="Natural language assertion to evaluate"
    )

    parser.add_argument(
        "--model",
        default="mock",
        help="Model name to use (default: mock). Use --list-models to see options.",
    )

    parser.add_argument(
        "--interactive", action="store_true", help="Run in interactive mode"
    )

    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    parser.add_argument(
        "--list-models", action="store_true", help="List all available models and exit"
    )

    parser.add_argument(
        "--model-info",
        metavar="MODEL_NAME",
        help="Show information about a specific model and exit",
    )

    parser.add_argument(
        "--cache-size", action="store_true", help="Show current cache size and exit"
    )

    parser.add_argument(
        "--clear-cache", action="store_true", help="Clear the evaluation cache and exit"
    )

    parser.add_argument(
        "--env-file", metavar="PATH", help="Path to .env file containing API keys"
    )

    parser.add_argument(
        "--api-keys", action="store_true", help="Show API key status and exit"
    )

    parser.add_argument(
        "--samples",
        type=int,
        default=1,
        help="Number of samples for majority voting (default: 1)",
    )

    parser.add_argument(
        "--tiebreak",
        choices=["random", "pessimistic", "optimistic"],
        default="random",
        help="Tiebreaking strategy when samples tie: random (default), optimistic (prefer verified/refuted), pessimistic (prefer cannot verify/refute)",
    )

    args = parser.parse_args()

    # Load custom .env file if specified
    if args.env_file:
        if not load_env_file(args.env_file):
            return 1

    # Handle info commands first
    if args.api_keys:
        show_api_key_status()
        return 0

    if args.list_models:
        list_models()
        return 0

    if args.model_info:
        show_model_info(args.model_info)
        return 0

    if args.cache_size:
        print(f"Cache size: {get_cache_size()} entries")
        return 0

    if args.clear_cache:
        clear_cache()
        print("Cache cleared.")
        return 0

    # Validate samples parameter
    if args.samples <= 0:
        print("Error: Number of samples must be positive")
        return 1

    # Main evaluation modes
    if args.interactive:
        return interactive_mode(args.model, args.samples, args.tiebreak)

    if args.assertion:
        return single_evaluation(
            args.assertion, args.model, args.verbose, args.samples, args.tiebreak
        )

    # No assertion provided and not interactive - show help
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
