import argparse
import json
import importlib
import os
from typing import Dict, Any, Optional, Type

from rebel.workflow import Workflow
from rebel.extractor import Extractor
from rebel.collector import Collector, OpenAIAPIClient
from rebel.evaluator import Evaluator
from rebel.aggregator import Aggregator
from rebel.saver import Saver


def load_custom_client_class(module_path: str, class_name: str) -> Type:
    """Dynamically load a custom API client class from a module."""
    try:
        module = importlib.import_module(module_path)
        client_class = getattr(module, class_name)
        
        # Verify it's a valid API client (optional validation)
        if not hasattr(client_class, 'request'):
            raise ValueError(f"{class_name} must implement 'request' method")
        
        return client_class
    except ImportError as e:
        raise ImportError(f"Could not import module {module_path}: {e}")
    except AttributeError:
        raise AttributeError(f"Class {class_name} not found in module {module_path}")


def create_client_from_config(config_path: Dict[str, Any]) -> OpenAIAPIClient:
    """Factory function to create API clients based on configuration."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return OpenAIAPIClient(
        api_key=config.get('api_key'),
        base_url=config.get('base_url'),
        model=config.get('model')
    )


def create_api_client(
    api_client_module: Optional[str] = None,
    api_client_class: Optional[str] = None,
    api_client_args: Optional[str] = None,
    api_config: Optional[str] = None,
):
    """
    Create API client with the following priority:
    1. Custom client (if module and class specified)
    2. Config file client (if config path specified)
    3. Fallback to OpenAI client with URL (backward compatibility)
    """
    # Priority 1: Custom client specified
    if api_client_module and api_client_class:
        client_class = load_custom_client_class(api_client_module, api_client_class)
        
        # Parse constructor arguments
        client_args = {}
        if api_client_args:
            client_args = json.loads(api_client_args)
        
        return client_class(**client_args)
    
    # Priority 2: Config file specified
    if api_config:
        return create_client_from_config(api_config)
    
    raise ValueError("Must provide either custom client, config file, or API URL")


def main():
    """Main CLI entry point for rebel."""
    parser = argparse.ArgumentParser(description="REBEL - RAG Evaluation Benchmark and Evaluation Library")
    
    # Core arguments
    parser.add_argument("--test-dir", required=True, help="Directory containing test files")
    parser.add_argument("--output-folder", required=True, help="Directory to store test results")
    parser.add_argument("--keyword", help="Filter tests by keyword")
    parser.add_argument("--tags", help="Filter tests by tags")
    parser.add_argument("--exclude-tags", help="Exclude tests with these tags")
    parser.add_argument("--num-workers-api", type=int, default=4, help="Number of API worker threads")
    parser.add_argument("--num-workers-eval", type=int, default=4, help="Number of evaluation worker threads")
    
    # API Client Configuration Options (in priority order)
    # Option 1: Custom client (highest priority)
    parser.add_argument("--api-client-module", help="Python module path for custom API client")
    parser.add_argument("--api-client-class", help="Class name of custom API client")
    parser.add_argument("--api-client-args", help="JSON string of arguments for API client constructor")
    
    # Option 2: Config file (medium priority)
    parser.add_argument("--api-config", help="Path to API configuration file (JSON)")
    
    args = parser.parse_args()
    
    # Create API client using merged approach
    try:
        api_client = create_api_client(
            api_client_module=args.api_client_module,
            api_client_class=args.api_client_class,
            api_client_args=args.api_client_args,
            api_config=args.api_config,
        )
    except Exception as e:
        print(f"Error creating API client: {e}")
        return 1
    
    # Initialize workflow components
    extractor = Extractor(
        test_dir=args.test_dir,
        keyword=args.keyword,
        tags=args.tags,
        exclude_tags=args.exclude_tags
    )
    
    collector = Collector(api_client=api_client, num_workers=args.num_workers_api)
    evaluator = Evaluator(num_workers=args.num_workers_eval)
    aggregator = Aggregator()
    saver = Saver(output_folder=args.output_folder)
    
    workflow = Workflow(
        extractor=extractor,
        collector=collector,
        evaluator=evaluator,
        aggregator=aggregator,
        saver=saver
    )
    
    workflow.execute()


if __name__ == "__main__":
    exit(main())
