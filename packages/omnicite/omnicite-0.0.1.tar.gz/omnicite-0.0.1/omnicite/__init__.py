#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OmniCite: Universal Citation Management and Academic Reference Toolkit

A comprehensive Python package for managing bibliographic data and generating
citations in multiple formats.
"""

__version__ = "0.0.1a1"
__author__ = "OmniCite Team"
__email__ = "team@omnicite.org"
__license__ = "MIT"

from .core import (
    RawEntry,
    IdentifiedEntry,
    CompletedEntry,
    TemplateLoader,
    PipelineController,
    process_references,
)

from .exceptions import (
    OmniCiteError,
    ValidationError,
    ParseError,
    ResolverError,
)

__all__ = [
    # Core data structures
    "RawEntry",
    "IdentifiedEntry",
    "CompletedEntry",
    
    # Core classes
    "TemplateLoader",
    "PipelineController",
    
    # Main API
    "process_references",
    
    # Exceptions
    "OmniCiteError",
    "ValidationError", 
    "ParseError",
    "ResolverError",
    
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]

# Package metadata
__title__ = "omnicite"
__description__ = "Universal citation management and academic reference toolkit"
__url__ = "https://github.com/omnicite/omnicite"
