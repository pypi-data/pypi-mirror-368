#!/usr/bin/env python3
# this_file: d361api/cli.py
"""CLI tool for d361api package."""

import argparse
import asyncio
import json
import os
import sys
from typing import Any, Dict, Optional

from d361api import ApiClient, Configuration, __version__
from d361api.d361api import ArticlesApi, CategoriesApi, ProjectVersionsApi
from d361api.exceptions import ApiException


class D361ApiCLI:
    """Command line interface for d361api."""

    def __init__(self):
        """Initialize CLI."""
        self.config = Configuration()
        self.setup_config()

    def setup_config(self):
        """Setup configuration from environment variables."""
        # Get API token from environment
        api_token = os.getenv('D361_API_TOKEN') or os.getenv('DOCUMENT360_API_TOKEN')
        if api_token:
            self.config.api_key['api_token'] = api_token

        # Get custom host if provided
        custom_host = os.getenv('D361_API_HOST')
        if custom_host:
            self.config.host = custom_host

    async def list_articles(self, project_version_id: str, limit: int = 10) -> Dict[str, Any]:
        """List articles in a project version."""
        async with ApiClient(self.config) as client:
            api = ArticlesApi(client)
            try:
                # This is a placeholder - actual API method depends on the generated client
                response = await api.v2_project_versions_project_version_id_articles_get(
                    project_version_id=project_version_id
                )
                return {"articles": response.data if hasattr(response, 'data') else str(response)}
            except ApiException as e:
                return {"error": f"API Error: {e.status} - {e.reason}"}
            except Exception as e:
                return {"error": f"Unexpected error: {str(e)}"}

    async def list_categories(self, project_version_id: str) -> Dict[str, Any]:
        """List categories in a project version."""
        async with ApiClient(self.config) as client:
            api = CategoriesApi(client)
            try:
                response = await api.v2_project_versions_project_version_id_categories_get(
                    project_version_id=project_version_id
                )
                return {"categories": response.data if hasattr(response, 'data') else str(response)}
            except ApiException as e:
                return {"error": f"API Error: {e.status} - {e.reason}"}
            except Exception as e:
                return {"error": f"Unexpected error: {str(e)}"}

    async def list_project_versions(self) -> Dict[str, Any]:
        """List project versions."""
        async with ApiClient(self.config) as client:
            api = ProjectVersionsApi(client)
            try:
                response = await api.v2_project_versions_get()
                return {"project_versions": response.data if hasattr(response, 'data') else str(response)}
            except ApiException as e:
                return {"error": f"API Error: {e.status} - {e.reason}"}
            except Exception as e:
                return {"error": f"Unexpected error: {str(e)}"}

    async def search_articles(self, project_version_id: str, lang_code: str, query: str) -> Dict[str, Any]:
        """Search articles in a project version."""
        async with ApiClient(self.config) as client:
            api = ProjectVersionsApi(client)
            try:
                response = await api.v2_project_versions_project_version_id_lang_code_get(
                    project_version_id=project_version_id,
                    lang_code=lang_code,
                    q=query
                )
                return {"search_results": response.data if hasattr(response, 'data') else str(response)}
            except ApiException as e:
                return {"error": f"API Error: {e.status} - {e.reason}"}
            except Exception as e:
                return {"error": f"Unexpected error: {str(e)}"}

    def print_result(self, result: Dict[str, Any], output_format: str = 'json'):
        """Print result in specified format."""
        if output_format == 'json':
            print(json.dumps(result, indent=2, default=str))
        elif output_format == 'table':
            # Simple table format
            for key, value in result.items():
                if isinstance(value, list):
                    print(f"{key.upper()}:")
                    for item in value:
                        if isinstance(item, dict):
                            print(f"  - {item.get('title', item.get('name', str(item)))}")
                        else:
                            print(f"  - {item}")
                else:
                    print(f"{key}: {value}")
        else:
            print(result)

    def check_config(self):
        """Check if configuration is valid."""
        if not self.config.api_key.get('api_token'):
            print("Error: API token not found.", file=sys.stderr)
            print("Please set D361_API_TOKEN or DOCUMENT360_API_TOKEN environment variable.", file=sys.stderr)
            print("Or use --api-token option.", file=sys.stderr)
            return False
        return True


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='CLI tool for Document360 API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # List project versions
  d361api project-versions

  # List articles in a project version
  d361api articles PROJECT_VERSION_ID

  # Search articles
  d361api search PROJECT_VERSION_ID en "search query"

  # Use custom API token
  d361api --api-token YOUR_TOKEN project-versions

Environment Variables:
  D361_API_TOKEN        API token for authentication
  DOCUMENT360_API_TOKEN Alternative API token variable
  D361_API_HOST         Custom API host (default: https://apihub.document360.io)
        '''
    )

    parser.add_argument('--version', action='version', version=f'd361api {__version__}')
    parser.add_argument('--api-token', help='API token for authentication')
    parser.add_argument('--host', help='Custom API host')
    parser.add_argument('--format', choices=['json', 'table'], default='json', help='Output format')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Project versions command
    subparsers.add_parser('project-versions', help='List project versions')

    # Articles command
    articles_parser = subparsers.add_parser('articles', help='List articles')
    articles_parser.add_argument('project_version_id', help='Project version ID')
    articles_parser.add_argument('--limit', type=int, default=10, help='Limit number of results')

    # Categories command
    categories_parser = subparsers.add_parser('categories', help='List categories')
    categories_parser.add_argument('project_version_id', help='Project version ID')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search articles')
    search_parser.add_argument('project_version_id', help='Project version ID')
    search_parser.add_argument('lang_code', help='Language code (e.g., en)')
    search_parser.add_argument('query', help='Search query')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize CLI
    cli = D361ApiCLI()

    # Override config with command line arguments
    if args.api_token:
        cli.config.api_key['api_token'] = args.api_token
    if args.host:
        cli.config.host = args.host

    # Check configuration
    if not cli.check_config():
        return 1

    # Run command
    try:
        if args.command == 'project-versions':
            result = asyncio.run(cli.list_project_versions())
        elif args.command == 'articles':
            result = asyncio.run(cli.list_articles(args.project_version_id, args.limit))
        elif args.command == 'categories':
            result = asyncio.run(cli.list_categories(args.project_version_id))
        elif args.command == 'search':
            result = asyncio.run(cli.search_articles(args.project_version_id, args.lang_code, args.query))
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1

        cli.print_result(result, args.format)
        
        # Return appropriate exit code
        if 'error' in result:
            return 1
        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 1
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())