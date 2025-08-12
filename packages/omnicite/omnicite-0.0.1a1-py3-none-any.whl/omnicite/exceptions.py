#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exception classes for OmniCite package.
"""


class OmniCiteError(Exception):
    """
    Base exception class for all OmniCite errors.
    
    This is the parent class for all custom exceptions in the OmniCite package.
    """
    pass


class ValidationError(OmniCiteError):
    """
    Raised when citation data validation fails.
    
    This exception is raised when citation data doesn't meet required
    formatting or completeness standards.
    """
    pass


class ParseError(OmniCiteError):
    """
    Raised when parsing citation files fails.
    
    This exception is raised when BibTeX, RIS, or other citation format
    files cannot be properly parsed.
    """
    pass


class ResolverError(OmniCiteError):
    """
    Raised when DOI or other identifier resolution fails.
    
    This exception is raised when external services (like CrossRef)
    cannot resolve identifiers to citation metadata.
    """
    pass


class FormatError(OmniCiteError):
    """
    Raised when citation formatting fails.
    
    This exception is raised when citations cannot be formatted
    in the requested style.
    """
    pass


class ImportError(OmniCiteError):
    """
    Raised when importing citation data fails.
    
    This exception is raised when citation files cannot be imported
    due to format or access issues.
    """
    pass


class ExportError(OmniCiteError):
    """
    Raised when exporting citation data fails.
    
    This exception is raised when citations cannot be exported
    to the requested format or location.
    """
    pass
