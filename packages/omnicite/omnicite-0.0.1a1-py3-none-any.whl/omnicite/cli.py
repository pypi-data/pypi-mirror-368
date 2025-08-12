#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command-line interface for OmniCite.
"""

import argparse
import sys
from typing import Optional

from .core import CitationManager, DOIResolver
from .exceptions import OmniCiteError
from . import __version__


def main() -> int:
    """
    Main entry point for the OmniCite CLI.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        if args.command == 'resolve':
            return resolve_doi_command(args)
        elif args.command == 'convert':
            return convert_command(args)
        elif args.command == 'validate':
            return validate_command(args)
        elif args.command == 'version':
            print(f"OmniCite version {__version__}")
            return 0
        else:
            parser.print_help()
            return 1
            
    except OmniCiteError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured parser
    """
    parser = argparse.ArgumentParser(
        prog='omnicite',
        description='Universal citation management and academic reference toolkit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  omnicite resolve 10.1038/nature12373
  omnicite convert input.bib --output output.ris --format ris
  omnicite validate references.bib
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # DOI resolution command
    resolve_parser = subparsers.add_parser(
        'resolve',
        help='Resolve DOI to citation metadata'
    )
    resolve_parser.add_argument(
        'doi',
        help='DOI identifier to resolve'
    )
    resolve_parser.add_argument(
        '--format',
        choices=['bibtex', 'ris', 'apa', 'json'],
        default='bibtex',
        help='Output format (default: bibtex)'
    )
    resolve_parser.add_argument(
        '--output',
        '-o',
        help='Output file (default: stdout)'
    )
    
    # Format conversion command
    convert_parser = subparsers.add_parser(
        'convert',
        help='Convert between citation formats'
    )
    convert_parser.add_argument(
        'input_file',
        help='Input citation file'
    )
    convert_parser.add_argument(
        '--output',
        '-o',
        help='Output file (default: stdout)'
    )
    convert_parser.add_argument(
        '--format',
        choices=['bibtex', 'ris', 'apa', 'json'],
        default='bibtex',
        help='Output format (default: bibtex)'
    )
    convert_parser.add_argument(
        '--input-format',
        choices=['bibtex', 'ris', 'json'],
        help='Input format (auto-detected if not specified)'
    )
    
    # Validation command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate citation file format and content'
    )
    validate_parser.add_argument(
        'file',
        help='Citation file to validate'
    )
    validate_parser.add_argument(
        '--format',
        choices=['bibtex', 'ris', 'json'],
        help='File format (auto-detected if not specified)'
    )
    
    return parser


def resolve_doi_command(args) -> int:
    """
    Handle DOI resolution command.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code
    """
    resolver = DOIResolver()
    
    try:
        citation = resolver.resolve(args.doi)
        
        if args.format == 'bibtex':
            output = citation.to_bibtex()
        elif args.format == 'ris':
            output = citation.to_ris()
        elif args.format == 'apa':
            output = citation.to_apa()
        elif args.format == 'json':
            import json
            output = json.dumps(citation.to_dict(), indent=2)
        else:
            output = citation.to_bibtex()
            
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
        else:
            print(output)
            
        return 0
        
    except Exception as e:
        print(f"Failed to resolve DOI: {e}", file=sys.stderr)
        return 1


def convert_command(args) -> int:
    """
    Handle format conversion command.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code
    """
    # Placeholder implementation
    print("Format conversion not yet implemented", file=sys.stderr)
    return 1


def validate_command(args) -> int:
    """
    Handle validation command.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code
    """
    # Placeholder implementation
    print("Validation not yet implemented", file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
