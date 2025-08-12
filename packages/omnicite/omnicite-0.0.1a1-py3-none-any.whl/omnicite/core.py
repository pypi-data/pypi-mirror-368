#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Core classes for OmniCite citation management.
"""

import re
import json
from typing import List, Dict, Optional, Union, Any
from datetime import datetime

from .exceptions import ValidationError, ParseError, ResolverError


class Citation:
    """
    Represents a single academic citation with metadata.
    
    This class provides a unified interface for handling bibliographic data
    across different citation formats and styles.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize a Citation object.
        
        Args:
            **kwargs: Citation metadata including title, authors, journal, etc.
        """
        self.title = kwargs.get('title', '')
        self.authors = kwargs.get('authors', [])
        self.journal = kwargs.get('journal', '')
        self.year = kwargs.get('year')
        self.volume = kwargs.get('volume')
        self.issue = kwargs.get('issue')
        self.pages = kwargs.get('pages')
        self.doi = kwargs.get('doi')
        self.isbn = kwargs.get('isbn')
        self.url = kwargs.get('url')
        self.abstract = kwargs.get('abstract', '')
        self.keywords = kwargs.get('keywords', [])
        self.citation_type = kwargs.get('type', 'article')
        
        # Additional metadata
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
    def validate(self) -> bool:
        """
        Validate citation data completeness and format.
        
        Returns:
            bool: True if validation passes
            
        Raises:
            ValidationError: If validation fails
        """
        if not self.title:
            raise ValidationError("Title is required")
            
        if not self.authors:
            raise ValidationError("At least one author is required")
            
        if self.year and not isinstance(self.year, int):
            raise ValidationError("Year must be an integer")
            
        if self.doi and not self._validate_doi(self.doi):
            raise ValidationError("Invalid DOI format")
            
        return True
        
    def _validate_doi(self, doi: str) -> bool:
        """Validate DOI format."""
        doi_pattern = r'^10\.\d{4,}/.+'
        return bool(re.match(doi_pattern, doi))
        
    def to_bibtex(self) -> str:
        """
        Convert citation to BibTeX format.
        
        Returns:
            str: BibTeX formatted citation
        """
        # Placeholder implementation
        bibtex_type = self.citation_type or 'article'
        key = self._generate_key()
        
        lines = [f"@{bibtex_type}{{{key},"]
        
        if self.title:
            lines.append(f'  title = "{self.title}",')
        if self.authors:
            authors_str = ' and '.join(self.authors)
            lines.append(f'  author = "{authors_str}",')
        if self.journal:
            lines.append(f'  journal = "{self.journal}",')
        if self.year:
            lines.append(f'  year = {self.year},')
        if self.volume:
            lines.append(f'  volume = {self.volume},')
        if self.pages:
            lines.append(f'  pages = "{self.pages}",')
        if self.doi:
            lines.append(f'  doi = "{self.doi}",')
            
        lines.append('}')
        return '\n'.join(lines)
        
    def to_apa(self) -> str:
        """
        Convert citation to APA format.
        
        Returns:
            str: APA formatted citation
        """
        # Placeholder APA formatting
        parts = []
        
        if self.authors:
            if len(self.authors) == 1:
                parts.append(self.authors[0])
            else:
                parts.append(', '.join(self.authors[:-1]) + f', & {self.authors[-1]}')
                
        if self.year:
            parts.append(f'({self.year})')
            
        if self.title:
            parts.append(f'{self.title}.')
            
        if self.journal:
            journal_part = f'*{self.journal}*'
            if self.volume:
                journal_part += f', {self.volume}'
            if self.issue:
                journal_part += f'({self.issue})'
            if self.pages:
                journal_part += f', {self.pages}'
            parts.append(journal_part + '.')
            
        return ' '.join(parts)
        
    def to_ris(self) -> str:
        """
        Convert citation to RIS format.
        
        Returns:
            str: RIS formatted citation
        """
        lines = ['TY  - JOUR']  # Journal article type
        
        if self.title:
            lines.append(f'TI  - {self.title}')
        for author in self.authors:
            lines.append(f'AU  - {author}')
        if self.journal:
            lines.append(f'JO  - {self.journal}')
        if self.year:
            lines.append(f'PY  - {self.year}')
        if self.volume:
            lines.append(f'VL  - {self.volume}')
        if self.issue:
            lines.append(f'IS  - {self.issue}')
        if self.pages:
            lines.append(f'SP  - {self.pages}')
        if self.doi:
            lines.append(f'DO  - {self.doi}')
            
        lines.append('ER  -')
        return '\n'.join(lines)
        
    def _generate_key(self) -> str:
        """Generate BibTeX key from citation data."""
        if self.authors and self.year:
            first_author = self.authors[0].split(',')[0].replace(' ', '')
            return f"{first_author}{self.year}"
        return "unknown"
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert citation to dictionary."""
        return {
            'title': self.title,
            'authors': self.authors,
            'journal': self.journal,
            'year': self.year,
            'volume': self.volume,
            'issue': self.issue,
            'pages': self.pages,
            'doi': self.doi,
            'isbn': self.isbn,
            'url': self.url,
            'abstract': self.abstract,
            'keywords': self.keywords,
            'type': self.citation_type,
        }


class CitationManager:
    """
    Manages collections of citations with import/export capabilities.
    """
    
    def __init__(self):
        """Initialize citation manager."""
        self.citations: List[Citation] = []
        
    def add_citation(self, citation: Citation) -> None:
        """
        Add a citation to the collection.
        
        Args:
            citation: Citation object to add
        """
        citation.validate()
        self.citations.append(citation)
        
    def remove_citation(self, index: int) -> None:
        """
        Remove citation by index.
        
        Args:
            index: Index of citation to remove
        """
        if 0 <= index < len(self.citations):
            del self.citations[index]
            
    def get_citation(self, index: int) -> Optional[Citation]:
        """
        Get citation by index.
        
        Args:
            index: Index of citation to retrieve
            
        Returns:
            Citation object or None if not found
        """
        if 0 <= index < len(self.citations):
            return self.citations[index]
        return None
        
    def search_citations(self, query: str) -> List[Citation]:
        """
        Search citations by title or author.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching citations
        """
        results = []
        query_lower = query.lower()
        
        for citation in self.citations:
            if (query_lower in citation.title.lower() or
                any(query_lower in author.lower() for author in citation.authors)):
                results.append(citation)
                
        return results
        
    def export_bibliography(self, style: str = "apa") -> str:
        """
        Export bibliography in specified style.
        
        Args:
            style: Citation style ('apa', 'mla', 'chicago', 'bibtex', 'ris')
            
        Returns:
            Formatted bibliography string
        """
        if style.lower() == 'bibtex':
            return '\n\n'.join(citation.to_bibtex() for citation in self.citations)
        elif style.lower() == 'ris':
            return '\n\n'.join(citation.to_ris() for citation in self.citations)
        elif style.lower() == 'apa':
            return '\n\n'.join(citation.to_apa() for citation in self.citations)
        else:
            # Default to APA for unsupported styles
            return '\n\n'.join(citation.to_apa() for citation in self.citations)
            
    def import_from_file(self, filepath: str, format_type: str = "bibtex") -> int:
        """
        Import citations from file.
        
        Args:
            filepath: Path to citation file
            format_type: File format ('bibtex', 'ris', 'json')
            
        Returns:
            Number of citations imported
        """
        # Placeholder implementation
        return 0
        
    def export_to_file(self, filepath: str, format_type: str = "bibtex") -> None:
        """
        Export citations to file.
        
        Args:
            filepath: Output file path
            format_type: Export format ('bibtex', 'ris', 'json')
        """
        # Placeholder implementation
        pass


class DOIResolver:
    """
    Resolves DOI identifiers to citation metadata.
    """
    
    def __init__(self):
        """Initialize DOI resolver."""
        self.base_url = "https://api.crossref.org/works/"
        
    def resolve(self, doi: str) -> Citation:
        """
        Resolve single DOI to citation.
        
        Args:
            doi: DOI identifier
            
        Returns:
            Citation object
            
        Raises:
            ResolverError: If DOI resolution fails
        """
        # Placeholder implementation
        # In real implementation, this would make HTTP request to CrossRef API
        return Citation(
            title=f"Sample Title for {doi}",
            authors=["Sample Author"],
            journal="Sample Journal",
            year=2024,
            doi=doi
        )
        
    def resolve_batch(self, dois: List[str]) -> List[Citation]:
        """
        Resolve multiple DOIs to citations.
        
        Args:
            dois: List of DOI identifiers
            
        Returns:
            List of Citation objects
        """
        return [self.resolve(doi) for doi in dois]
        
    def get_citation(self, doi: str) -> Citation:
        """Alias for resolve method."""
        return self.resolve(doi)


class BibTeXParser:
    """
    Parses BibTeX format citation files.
    """
    
    def __init__(self):
        """Initialize BibTeX parser."""
        pass
        
    def parse_string(self, bibtex_str: str) -> List[Citation]:
        """
        Parse BibTeX string to citations.
        
        Args:
            bibtex_str: BibTeX formatted string
            
        Returns:
            List of Citation objects
        """
        # Placeholder implementation
        return []
        
    def parse_file(self, filepath: str) -> List[Citation]:
        """
        Parse BibTeX file to citations.
        
        Args:
            filepath: Path to BibTeX file
            
        Returns:
            List of Citation objects
        """
        # Placeholder implementation
        return []


class RISParser:
    """
    Parses RIS format citation files.
    """
    
    def __init__(self):
        """Initialize RIS parser."""
        pass
        
    def parse_string(self, ris_str: str) -> List[Citation]:
        """
        Parse RIS string to citations.
        
        Args:
            ris_str: RIS formatted string
            
        Returns:
            List of Citation objects
        """
        # Placeholder implementation
        return []
        
    def parse_file(self, filepath: str) -> List[Citation]:
        """
        Parse RIS file to citations.
        
        Args:
            filepath: Path to RIS file
            
        Returns:
            List of Citation objects
        """
        # Placeholder implementation
        return []


class CitationFormatter:
    """
    Formats citations in various academic styles.
    """
    
    def __init__(self):
        """Initialize citation formatter."""
        self.supported_styles = ['apa', 'mla', 'chicago', 'ieee', 'harvard']
        
    def format_citation(self, citation: Citation, style: str = "apa") -> str:
        """
        Format citation in specified style.
        
        Args:
            citation: Citation object to format
            style: Citation style
            
        Returns:
            Formatted citation string
        """
        if style.lower() == 'apa':
            return citation.to_apa()
        elif style.lower() == 'mla':
            return self._format_mla(citation)
        elif style.lower() == 'chicago':
            return self._format_chicago(citation)
        else:
            return citation.to_apa()  # Default to APA
            
    def _format_mla(self, citation: Citation) -> str:
        """Format citation in MLA style."""
        # Placeholder MLA formatting
        return citation.to_apa()
        
    def _format_chicago(self, citation: Citation) -> str:
        """Format citation in Chicago style."""
        # Placeholder Chicago formatting
        return citation.to_apa()
