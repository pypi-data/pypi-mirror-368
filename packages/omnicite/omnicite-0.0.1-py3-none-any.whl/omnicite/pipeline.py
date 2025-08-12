#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OmniCite Processing Pipeline Module
Implementation of various modules for the 4-stage processing pipeline
"""

import re
import os
import logging
from typing import List, Dict, Optional, Callable, Any
import requests
from bs4 import BeautifulSoup
import bibtexparser
from thefuzz import fuzz
from scholarly import scholarly

from .core import RawEntry, IdentifiedEntry, CompletedEntry
from .exceptions import ParseError, ResolverError


class ParserModule:
    """Stage 1: Parse and Extract Module"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse(self, input_content: str, input_type: str) -> List[RawEntry]:
        """
        Parse input content into a list of raw entries
        
        Args:
            input_content: Input content string
            input_type: Input type ('txt' or 'bib')
        
        Returns:
            List of raw entries
        """
        self.logger.info(f"Starting to parse {input_type} format input content")
        
        if input_type.lower() == 'bib':
            return self._parse_bibtex(input_content)
        elif input_type.lower() == 'txt':
            return self._parse_text(input_content)
        else:
            raise ParseError(f"Unsupported input type: {input_type}")
    
    def _parse_bibtex(self, bibtex_content: str) -> List[RawEntry]:
        """Parse BibTeX format content"""
        entries = []
        try:
            bib_database = bibtexparser.loads(bibtex_content)
            for i, entry in enumerate(bib_database.entries):
                raw_entry: RawEntry = {
                    'id': i,
                    'raw_text': str(entry),
                    'doi': entry.get('doi'),
                    'url': entry.get('url'),
                    'query_string': None
                }
                
                # If no DOI is available, generate query string
                if not raw_entry['doi']:
                    query_parts = []
                    if 'title' in entry:
                        query_parts.append(entry['title'])
                    if 'author' in entry:
                        query_parts.append(entry['author'])
                    if 'year' in entry:
                        query_parts.append(entry['year'])
                    raw_entry['query_string'] = ' '.join(query_parts)
                
                entries.append(raw_entry)
            
            self.logger.info(f"Successfully parsed {len(entries)} BibTeX entries")
            return entries
            
        except Exception as e:
            self.logger.error(f"BibTeX parsing failed: {str(e)}")
            raise ParseError(f"BibTeX parsing failed: {str(e)}")
    
    def _parse_text(self, text_content: str) -> List[RawEntry]:
        """Parse plain text format content"""
        entries = []
        
        # Split text blocks using double newlines
        text_blocks = text_content.split('\n\n')
        
        for i, block in enumerate(text_blocks):
            block = block.strip()
            if not block:
                continue
            
            raw_entry: RawEntry = {
                'id': i,
                'raw_text': block,
                'doi': None,
                'url': None,
                'query_string': None
            }
            
            # Find DOI
            doi_match = re.search(r'10\.\d{4,}/[^\s]+', block)
            if doi_match:
                raw_entry['doi'] = doi_match.group()
            
            # Find URL
            url_match = re.search(r'https?://[^\s]+', block)
            if url_match:
                raw_entry['url'] = url_match.group()
            
            # If no DOI or URL found, build a concise query string from title/author/year
            if not raw_entry['doi'] and not raw_entry['url']:
                lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
                title_text = lines[0] if lines else block
                authors_text = lines[1] if len(lines) > 1 else ''
                year_match = re.search(r'(19|20)\d{2}', block)
                year_text = year_match.group(0) if year_match else ''

                query_parts: List[str] = []
                if title_text:
                    query_parts.append(title_text)
                if authors_text:
                    query_parts.append(authors_text)
                if year_text:
                    query_parts.append(year_text)

                raw_entry['query_string'] = ' '.join(query_parts) or block
            
            entries.append(raw_entry)
        
        self.logger.info(f"Successfully parsed {len(entries)} text entries")
        return entries


class IdentifierModule:
    """Stage 2: Identification and Standardization Module"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.crossref_base_url = "https://api.crossref.org/works"
        
        # Well-known papers that might not have DOIs
        self.well_known_papers = {
            'attention is all you need': {
                'title': 'Attention Is All You Need',
                'authors': ['Vaswani, Ashish', 'Shazeer, Noam', 'Parmar, Niki', 'Uszkoreit, Jakob', 
                           'Jones, Llion', 'Gomez, Aidan N', 'Kaiser, Lukasz', 'Polosukhin, Illia'],
                'year': '2017',
                'journal': 'Advances in Neural Information Processing Systems',
                'arxiv_id': '1706.03762',
                'url': 'https://arxiv.org/abs/1706.03762',
                'type': 'conference'
            }
        }
    
    def identify(self, raw_entries: List[RawEntry], 
                interactive_callback: Callable[[List[Dict]], int]) -> List[IdentifiedEntry]:
        """
        Identify and standardize entries, finding DOI for each entry
        
        Args:
            raw_entries: List of raw entries
            interactive_callback: Interactive callback function
        
        Returns:
            List of identified entries
        """
        self.logger.info(f"Starting to identify {len(raw_entries)} entries")
        identified_entries = []
        
        for entry in raw_entries:
            identified_entry = self._identify_single_entry(entry, interactive_callback)
            identified_entries.append(identified_entry)
        
        successful_count = sum(1 for e in identified_entries if e['status'] == 'identified')
        self.logger.info(f"Identification completed: {successful_count}/{len(identified_entries)} entries successfully identified")
        
        return identified_entries
    
    def _identify_single_entry(self, raw_entry: RawEntry, 
                              interactive_callback: Callable[[List[Dict]], int]) -> IdentifiedEntry:
        """Identify a single entry"""
        identified_entry: IdentifiedEntry = {
            'id': raw_entry['id'],
            'raw_text': raw_entry['raw_text'],
            'doi': None,
            'arxiv_id': None,
            'url': None,
            'metadata': {},
            'status': 'identification_failed'
        }
        
        # If valid DOI already exists, mark as identified directly
        if raw_entry.get('doi'):
            if self._validate_doi(raw_entry['doi']):
                identified_entry['doi'] = raw_entry['doi']
                identified_entry['status'] = 'identified'
                self.logger.info(f"Entry {raw_entry['id']} already has valid DOI: {raw_entry['doi']}")
                return identified_entry
        
        # Check for arXiv ID in raw text
        arxiv_id = self._extract_arxiv_id(raw_entry['raw_text'])
        if arxiv_id:
            identified_entry['arxiv_id'] = arxiv_id
            identified_entry['status'] = 'identified'
            self.logger.info(f"Entry {raw_entry['id']} has arXiv ID: {arxiv_id}")
            return identified_entry
        
        # Try to extract DOI or arXiv ID from URL
        if raw_entry.get('url'):
            # Check if it's an arXiv URL
            if 'arxiv.org' in raw_entry['url']:
                arxiv_id = self._extract_arxiv_id_from_url(raw_entry['url'])
                if arxiv_id:
                    identified_entry['arxiv_id'] = arxiv_id
                    identified_entry['url'] = raw_entry['url']
                    identified_entry['status'] = 'identified'
                    self.logger.info(f"Entry {raw_entry['id']} extracted arXiv ID from URL: {arxiv_id}")
                    return identified_entry
            else:
                # Try to extract DOI
                extracted_doi = self._extract_doi_from_url(raw_entry['url'])
                if extracted_doi:
                    identified_entry['doi'] = extracted_doi
                    identified_entry['status'] = 'identified'
                    self.logger.info(f"Entry {raw_entry['id']} extracted DOI from URL: {extracted_doi}")
                    return identified_entry
                # Store URL for conference papers
                identified_entry['url'] = raw_entry['url']
        
        # Fuzzy search
        if raw_entry.get('query_string'):
            return self._fuzzy_search(raw_entry, interactive_callback)
        
        self.logger.warning(f"Entry {raw_entry['id']} identification failed")
        return identified_entry
    
    def _validate_doi(self, doi: str) -> bool:
        """Validate DOI format"""
        doi_pattern = r'^10\.\d{4,}/.+'
        return bool(re.match(doi_pattern, doi))
    
    def _extract_arxiv_id(self, text: str) -> Optional[str]:
        """Extract arXiv ID from text"""
        # Match both old (e.g., 1706.03762) and new (e.g., arxiv:1706.03762) formats
        arxiv_patterns = [
            r'arxiv[:\s]*(\d{4}\.\d{4,5})',  # New format
            r'\b(\d{4}\.\d{4,5})\b',  # Standalone ID
            r'arXiv:(\d{4}\.\d{4,5})',  # With arXiv prefix
        ]
        
        for pattern in arxiv_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_arxiv_id_from_url(self, url: str) -> Optional[str]:
        """Extract arXiv ID from arXiv URL"""
        # Match patterns like https://arxiv.org/abs/1706.03762
        match = re.search(r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})', url)
        if match:
            return match.group(1)
        return None
    
    def _extract_doi_from_url(self, url: str) -> Optional[str]:
        """Extract DOI from URL page"""
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'OmniCite/1.0'})
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for DOI in meta tags
            doi_meta = soup.find('meta', attrs={'name': 'citation_doi'}) or \
                      soup.find('meta', attrs={'name': 'dc.identifier'}) or \
                      soup.find('meta', attrs={'property': 'citation_doi'})
            
            if doi_meta and 'content' in doi_meta.attrs:
                doi = doi_meta['content']
                if self._validate_doi(doi):
                    return doi
            
            # Search for DOI in page content
            doi_match = re.search(r'10\.\d{4,}/[^\s"<>]+', response.text)
            if doi_match:
                doi = doi_match.group()
                if self._validate_doi(doi):
                    return doi
                    
        except Exception as e:
            self.logger.warning(f"Failed to extract DOI from URL {url}: {str(e)}")
        
        return None
    
    def _fuzzy_search(self, raw_entry: RawEntry, 
                     interactive_callback: Callable[[List[Dict]], int]) -> IdentifiedEntry:
        """Perform fuzzy search"""
        query_string = raw_entry['query_string']
        
        # Check if it's a well-known paper first
        query_lower = query_string.lower()
        for key, paper_data in self.well_known_papers.items():
            if key in query_lower or fuzz.ratio(key, query_lower) > 85:
                self.logger.info(f"Entry {raw_entry['id']} matched well-known paper: {paper_data['title']}")
                return IdentifiedEntry(
                    id=raw_entry['id'],
                    raw_text=raw_entry['raw_text'],
                    doi=None,
                    arxiv_id=paper_data.get('arxiv_id'),
                    url=paper_data.get('url'),
                    metadata=paper_data,
                    status='identified'
                )
        
        # Multi-source query
        candidates = []
        
        # CrossRef search
        crossref_results = self._search_crossref(query_string)
        candidates.extend(crossref_results)
        
        # Google Scholar search (simplified implementation)
        scholar_results = self._search_google_scholar(query_string)
        candidates.extend(scholar_results)
        
        if not candidates:
            self.logger.warning(f"Entry {raw_entry['id']}: no candidate results found")
            return IdentifiedEntry(
                id=raw_entry['id'],
                raw_text=raw_entry['raw_text'],
                doi=None,
                arxiv_id=None,
                url=None,
                metadata={},
                status='identification_failed'
            )
        
        # Calculate match scores
        scored_candidates = self._score_candidates(candidates, query_string)
        scored_candidates.sort(key=lambda x: x['match_score'], reverse=True)

        best_candidate = scored_candidates[0]
        # Prefer candidates with DOI when scores are close
        doi_candidates = [c for c in scored_candidates if c.get('doi')]
        if doi_candidates:
            best_doi_candidate = doi_candidates[0]
            if (not best_candidate.get('doi') or
                best_doi_candidate['match_score'] >= best_candidate['match_score'] - 5):
                best_candidate = best_doi_candidate

        # If best does not have DOI but looks strong, try title-only CrossRef lookup to resolve DOI
        if (not best_candidate.get('doi')) and best_candidate.get('title') and best_candidate.get('match_score', 0) >= 85:
            try:
                resolved = self._resolve_doi_via_crossref_title(best_candidate['title'], query_string)
                if resolved and resolved.get('doi'):
                    best_candidate = resolved
            except Exception:
                pass
        
        # Decision logic
        if best_candidate['match_score'] >= 80:
            # High confidence: auto adopt
            if len(scored_candidates) == 1 or best_candidate['match_score'] - scored_candidates[1]['match_score'] > 10:
                self.logger.info(f"Entry {raw_entry['id']} high confidence match: {best_candidate.get('doi', 'no-doi')}")
                return IdentifiedEntry(
                    id=raw_entry['id'],
                    raw_text=raw_entry['raw_text'],
                    doi=best_candidate.get('doi'),
                    arxiv_id=best_candidate.get('arxiv_id'),
                    url=best_candidate.get('url'),
                    metadata=best_candidate,
                    status='identified'
                )
        
        if 70 <= best_candidate['match_score'] < 80:
            # Medium confidence: trigger interactive mode
            top_candidates = scored_candidates[:5]  # Top 5 candidates
            try:
                user_choice = interactive_callback(top_candidates)
                if 0 <= user_choice < len(top_candidates):
                    chosen_candidate = top_candidates[user_choice]
                    self.logger.info(f"Entry {raw_entry['id']} user selection: {chosen_candidate.get('doi', 'no-doi')}")
                    return IdentifiedEntry(
                        id=raw_entry['id'],
                        raw_text=raw_entry['raw_text'],
                        doi=chosen_candidate.get('doi'),
                        arxiv_id=chosen_candidate.get('arxiv_id'),
                        url=chosen_candidate.get('url'),
                        metadata=chosen_candidate,
                        status='identified'
                    )
                else:
                    # Non-interactive or user skipped: fallback to best candidate if sufficiently strong
                    if best_candidate['match_score'] >= 75:
                        self.logger.info(
                            f"Entry {raw_entry['id']} fallback adopt best candidate (score={best_candidate['match_score']}): {best_candidate.get('doi', 'no-doi')}"
                        )
                        return IdentifiedEntry(
                            id=raw_entry['id'],
                            raw_text=raw_entry['raw_text'],
                            doi=best_candidate.get('doi'),
                            arxiv_id=best_candidate.get('arxiv_id'),
                            url=best_candidate.get('url'),
                            metadata=best_candidate,
                            status='identified'
                        )
                    self.logger.info(f"Entry {raw_entry['id']} user skipped")
            except Exception as e:
                self.logger.error(f"Interactive callback failed: {str(e)}")
                # Fallback in case interactive path is unavailable
                if best_candidate['match_score'] >= 75:
                    self.logger.info(
                        f"Entry {raw_entry['id']} fallback adopt best candidate after interactive error (score={best_candidate['match_score']}): {best_candidate.get('doi', 'no-doi')}"
                    )
                    return IdentifiedEntry(
                        id=raw_entry['id'],
                        raw_text=raw_entry['raw_text'],
                        doi=best_candidate.get('doi'),
                        arxiv_id=best_candidate.get('arxiv_id'),
                        url=best_candidate.get('url'),
                        metadata=best_candidate,
                        status='identified'
                    )
        
        # Low confidence but if score is decent and has title, mark as identified
        if best_candidate['match_score'] >= 65 and best_candidate.get('title'):
            self.logger.info(f"Entry {raw_entry['id']} adopting best candidate with score {best_candidate['match_score']}")
            return IdentifiedEntry(
                id=raw_entry['id'],
                raw_text=raw_entry['raw_text'],
                doi=best_candidate.get('doi'),
                arxiv_id=best_candidate.get('arxiv_id'),
                url=best_candidate.get('url'),
                metadata=best_candidate,
                status='identified'
            )
        
        # Low confidence: mark as failed
        self.logger.warning(f"Entry {raw_entry['id']} low confidence match, marking as failed")
        return IdentifiedEntry(
            id=raw_entry['id'],
            raw_text=raw_entry['raw_text'],
            doi=None,
            arxiv_id=None,
            url=None,
            metadata={},
            status='identification_failed'
        )

    def _resolve_doi_via_crossref_title(self, candidate_title: str, original_query: str) -> Optional[Dict]:
        """Try to resolve DOI by querying CrossRef with title only (plus hints).
        Returns a candidate dict with DOI if found and strongly matched.
        """
        try:
            url = f"{self.crossref_base_url}"
            # Build a focused query using title and optional year tokens from original query
            year_match = re.search(r"(19|20)\d{2}", original_query)
            year_text = year_match.group(0) if year_match else ''
            focused_query = candidate_title
            if year_text:
                focused_query = f"{candidate_title} {year_text}"
            params = {
                'query.title': candidate_title,
                'query.bibliographic': focused_query,
                'rows': 5,
                'mailto': 'omnicite@example.com'
            }
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            items = data.get('message', {}).get('items', [])
            best_item = None
            best_score = -1
            for item in items:
                title = (item.get('title', [''])[0] or '').lower()
                if not title:
                    continue
                # Use robust fuzzy comparison against candidate title
                base = candidate_title.lower()
                score = max(
                    fuzz.ratio(base, title),
                    fuzz.partial_ratio(base, title),
                    fuzz.token_set_ratio(base, title)
                )
                if score > best_score and item.get('DOI'):
                    best_score = score
                    best_item = item
            if best_item and best_score >= 90:
                return {
                    'source': 'crossref',
                    'doi': best_item.get('DOI'),
                    'title': (best_item.get('title', [''])[0] or ''),
                    'authors': [f"{a.get('given', '')} {a.get('family', '')}" for a in best_item.get('author', [])],
                    'year': best_item.get('published-print', {}).get('date-parts', [[None]])[0][0] or
                            best_item.get('published-online', {}).get('date-parts', [[None]])[0][0],
                    'journal': best_item.get('container-title', [''])[0] if best_item.get('container-title') else '',
                    'citations': best_item.get('is-referenced-by-count', 0)
                }
        except Exception:
            return None
        return None
    
    def _search_crossref(self, query: str, limit: int = 10) -> List[Dict]:
        """Search in CrossRef"""
        try:
            url = f"{self.crossref_base_url}"
            params = {
                'query': query,
                'query.bibliographic': query,
                'rows': limit,
                'mailto': 'omnicite@example.com'
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('message', {}).get('items', []):
                result = {
                    'source': 'crossref',
                    'doi': item.get('DOI'),
                    'title': item.get('title', [''])[0] if item.get('title') else '',
                    'authors': [f"{a.get('given', '')} {a.get('family', '')}" 
                              for a in item.get('author', [])],
                    'year': item.get('published-print', {}).get('date-parts', [[None]])[0][0] or
                           item.get('published-online', {}).get('date-parts', [[None]])[0][0],
                    'journal': item.get('container-title', [''])[0] if item.get('container-title') else '',
                    'citations': item.get('is-referenced-by-count', 0)
                }
                if result['doi']:
                    results.append(result)
            
            self.logger.info(f"CrossRef search returned {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"CrossRef search failed: {str(e)}")
            return []
    
    def _search_google_scholar(self, query: str, limit: int = 5) -> List[Dict]:
        """Search in Google Scholar (simplified implementation)"""
        try:
            search_query = scholarly.search_pubs(query)
            results = []
            
            for i, pub in enumerate(search_query):
                if i >= limit:
                    break
                    
                # Extract more fields from Google Scholar
                bib = pub.get('bib', {})
                
                result = {
                    'source': 'google_scholar',
                    'doi': None,  # Scholar API usually doesn't return DOI
                    'title': bib.get('title', '') or pub.get('title', ''),
                    'authors': bib.get('author', []) if isinstance(bib.get('author'), list) else 
                              (bib.get('author').split(' and ') if bib.get('author') else []),
                    'year': bib.get('pub_year', '') or pub.get('year'),
                    'journal': bib.get('venue', '') or pub.get('venue', '') or pub.get('journal', ''),
                    'citations': pub.get('num_citations', 0),
                    'url': pub.get('pub_url', '') or pub.get('url', ''),
                    'arxiv_id': None
                }
                
                # Try to extract arXiv ID from eprint or other fields
                if 'eprint' in pub:
                    arxiv_match = re.search(r'(\d{4}\.\d{4,5})', pub['eprint'])
                    if arxiv_match:
                        result['arxiv_id'] = arxiv_match.group(1)
                
                # For conference papers, venue often contains conference name
                if result['journal'] and ('conference' in result['journal'].lower() or 
                                         'proceedings' in result['journal'].lower() or
                                         'nips' in result['journal'].lower() or
                                         'neurips' in result['journal'].lower()):
                    result['type'] = 'conference'
                
                results.append(result)
            
            self.logger.info(f"Google Scholar search returned {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Google Scholar search failed: {str(e)}")
            return []
    
    def _score_candidates(self, candidates: List[Dict], query_string: str) -> List[Dict]:
        """Calculate match scores for candidate results"""
        scored_candidates = []
        
        # Normalize query for robust title matching
        normalized_query = query_string.strip()
        # Try to derive a probable title part: cut at first 4-digit year
        title_part = re.split(r'\b(19|20)\d{2}\b', normalized_query)[0].strip() or normalized_query
        # Remove common "et al." noise
        title_part = re.sub(r'\bet\s*al\.?\b', '', title_part, flags=re.IGNORECASE).strip()

        # Domain-specific synonyms mapping (lightweight)
        synonyms = {
            'nips': 'neural information processing systems',
            'neurips': 'neural information processing systems',
            'cvpr': 'computer vision and pattern recognition',
            'iclr': 'international conference on learning representations',
            'icml': 'international conference on machine learning'
        }
        normalized_query_lower = normalized_query.lower()
        for k, v in synonyms.items():
            if k in normalized_query_lower and v not in normalized_query_lower:
                normalized_query += f" {v}"
        
        # Also normalize candidate journal/venue names
        def normalize_venue(venue):
            venue_lower = venue.lower()
            for k, v in synonyms.items():
                if k in venue_lower:
                    return venue.replace(k, v).replace(k.upper(), v)
            return venue

        for candidate in candidates:
            # Title similarity (50% weight)
            candidate_title = candidate['title'].lower()
            base_title = title_part.lower()
            # Use multiple fuzzy measures and take the best
            ratio = fuzz.ratio(base_title, candidate_title)
            partial = fuzz.partial_ratio(base_title, candidate_title)
            token = fuzz.token_set_ratio(base_title, candidate_title)
            title_score = max(ratio, partial, token)
            
            # Author/year matching (30% weight)
            author_year_score = 0
            if candidate['authors']:
                authors_text = ' '.join(candidate['authors']).lower()
                author_score = fuzz.partial_ratio(normalized_query.lower(), authors_text)
                author_year_score += author_score * 0.7
            
            if candidate['year']:
                year_str = str(candidate['year'])
                if year_str in normalized_query:
                    author_year_score += 30  # Year matching bonus
            
            # Venue matching for conference papers (bonus)
            venue_bonus = 0
            if candidate.get('journal'):
                normalized_venue = normalize_venue(candidate['journal'])
                if fuzz.partial_ratio(normalized_query.lower(), normalized_venue.lower()) > 70:
                    venue_bonus = 20  # Bonus for venue match
            
            # Citation count normalized score (10% weight for newer papers)
            # Reduce citation weight since newer important papers may have fewer citations
            citation_score = min(candidate.get('citations', 0) / 100, 1) * 100  # Maximum 100 points
            
            # Weighted total score calculation
            # Adjust weights: title is most important, then author/year, venue bonus, and citations last
            match_score = (title_score * 0.6 + 
                          author_year_score * 0.25 + 
                          venue_bonus * 0.1 +
                          citation_score * 0.05)
            
            candidate_copy = candidate.copy()
            candidate_copy['match_score'] = round(match_score, 2)
            scored_candidates.append(candidate_copy)
        
        return scored_candidates


class EnricherModule:
    """Stage 3: Enrichment and Validation Module"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.crossref_base_url = "https://api.crossref.org/works"
    
    def enrich(self, identified_entries: List[IdentifiedEntry], 
               template: Dict) -> List[CompletedEntry]:
        """
        Enrich entries to obtain complete bibliographic information.
        
        Args:
            identified_entries: List of identified entries
            template: Template configuration
        
        Returns:
            List of completed records
        """
        self.logger.info(f"Starting enrichment for {len(identified_entries)} entries")
        completed_entries = []
        
        for entry in identified_entries:
            if entry['status'] == 'identified':
                # Process entries with DOI, arXiv ID, or other metadata
                if entry.get('doi') or entry.get('arxiv_id') or entry.get('metadata'):
                    completed_entry = self._enrich_single_entry(entry, template)
                    completed_entries.append(completed_entry)
                else:
                    # Entries without any identifier
                    failed_entry: CompletedEntry = {
                        'id': entry['id'],
                        'doi': '',
                        'status': 'enrichment_failed',
                        'bib_key': '',
                        'bib_data': {}
                    }
                    completed_entries.append(failed_entry)
            else:
                # Entries that were not identified are marked as failed
                failed_entry: CompletedEntry = {
                    'id': entry['id'],
                    'doi': '',
                    'status': 'enrichment_failed',
                    'bib_key': '',
                    'bib_data': {}
                }
                completed_entries.append(failed_entry)
        
        successful_count = sum(1 for e in completed_entries if e['status'] == 'completed')
        self.logger.info(f"Enrichment completed: {successful_count}/{len(completed_entries)} entries successfully completed")
        
        return completed_entries
    
    def _enrich_single_entry(self, identified_entry: IdentifiedEntry, 
                            template: Dict) -> CompletedEntry:
        """Enrich a single entry"""
        doi = identified_entry.get('doi')
        arxiv_id = identified_entry.get('arxiv_id')
        metadata = identified_entry.get('metadata', {})
        
        try:
            base_record = None
            
            # Try to get metadata from various sources
            if doi:
                # Get base record from CrossRef
                base_record = self._get_crossref_metadata(doi)
            elif arxiv_id:
                # Get base record from arXiv
                base_record = self._get_arxiv_metadata(arxiv_id)
            elif metadata:
                # Use metadata from search results
                base_record = self._convert_search_metadata(metadata)
            
            if not base_record:
                return CompletedEntry(
                    id=identified_entry['id'],
                    doi=doi or '',
                    status='enrichment_failed',
                    bib_key='',
                    bib_data={}
                )
            
            # Generate BibTeX key
            bib_key = self._generate_bibtex_key(base_record)
            
            # Complete missing fields according to the template
            completed_data = self._complete_fields(base_record, template)
            
            # Set the entry type based on content
            if metadata.get('type') == 'conference' or 'conference' in completed_data.get('journal', '').lower():
                completed_data['ENTRYTYPE'] = 'inproceedings'
            else:
                completed_data['ENTRYTYPE'] = template.get('entry_type', '@article').lstrip('@')
            
            completed_data['ID'] = bib_key
            
            # Add DOI if available
            if doi:
                completed_data['doi'] = doi
            
            # Add arXiv ID if available
            if arxiv_id:
                completed_data['arxiv'] = arxiv_id
                if not completed_data.get('url'):
                    completed_data['url'] = f'https://arxiv.org/abs/{arxiv_id}'
            
            self.logger.info(f"Entry {identified_entry['id']} enrichment successful")
            
            return CompletedEntry(
                id=identified_entry['id'],
                doi=doi or '',
                status='completed',
                bib_key=bib_key,
                bib_data=completed_data
            )
            
        except Exception as e:
            self.logger.error(f"Entry {identified_entry['id']} enrichment failed: {str(e)}")
            return CompletedEntry(
                id=identified_entry['id'],
                doi=doi or '',
                status='enrichment_failed',
                bib_key='',
                bib_data={}
            )
    
    def _get_crossref_metadata(self, doi: str) -> Optional[Dict]:
        """Get metadata from the CrossRef API"""
        try:
            url = f"{self.crossref_base_url}/{doi}"
            headers = {'Accept': 'application/json'}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            work = data.get('message', {})
            
            # Convert to a standard format
            metadata = {
                'doi': work.get('DOI'),
                'title': work.get('title', [''])[0] if work.get('title') else '',
                'author': self._format_authors(work.get('author', [])),
                'journal': work.get('container-title', [''])[0] if work.get('container-title') else '',
                'year': self._extract_year(work),
                'volume': work.get('volume'),
                'number': work.get('issue'),
                'pages': work.get('page'),
                'publisher': work.get('publisher'),
                'url': work.get('URL')
            }
            
            return {k: v for k, v in metadata.items() if v is not None}
            
        except Exception as e:
            self.logger.error(f"Failed to get CrossRef metadata for {doi}: {str(e)}")
            return None
    
    def _get_arxiv_metadata(self, arxiv_id: str) -> Optional[Dict]:
        """Get metadata from arXiv API"""
        try:
            import feedparser
            url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
            
            feed = feedparser.parse(url)
            if not feed.entries:
                return None
            
            entry = feed.entries[0]
            
            # Extract authors
            authors = []
            for author in entry.get('authors', []):
                name = author.get('name', '')
                if name:
                    # Convert "First Last" to "Last, First"
                    parts = name.split()
                    if len(parts) >= 2:
                        authors.append(f"{parts[-1]}, {' '.join(parts[:-1])}")
                    else:
                        authors.append(name)
            
            # Extract year from published date
            published = entry.get('published', '')
            year = published[:4] if len(published) >= 4 else None
            
            metadata = {
                'arxiv': arxiv_id,
                'title': entry.get('title', '').replace('\n', ' ').strip(),
                'author': ' and '.join(authors),
                'year': year,
                'journal': 'arXiv preprint',
                'url': f'https://arxiv.org/abs/{arxiv_id}',
                'abstract': entry.get('summary', '').replace('\n', ' ').strip()
            }
            
            return {k: v for k, v in metadata.items() if v}
            
        except Exception as e:
            self.logger.error(f"Failed to get arXiv metadata for {arxiv_id}: {str(e)}")
            return None
    
    def _convert_search_metadata(self, metadata: Dict) -> Optional[Dict]:
        """Convert search result metadata to standard format"""
        try:
            # Handle authors - they might be in list or string format
            authors = metadata.get('authors', [])
            if isinstance(authors, list):
                formatted_authors = ' and '.join(authors)
            else:
                formatted_authors = str(authors)
            
            # Determine if it's a conference paper
            journal = metadata.get('journal', '')
            if metadata.get('type') == 'conference' or any(conf in journal.lower() 
                for conf in ['conference', 'proceedings', 'symposium', 'workshop', 'nips', 'neurips']):
                # For conference papers, use booktitle instead of journal
                result = {
                    'title': metadata.get('title', ''),
                    'author': formatted_authors,
                    'booktitle': journal,
                    'year': str(metadata.get('year', '')),
                }
            else:
                result = {
                    'title': metadata.get('title', ''),
                    'author': formatted_authors,
                    'journal': journal,
                    'year': str(metadata.get('year', '')),
                }
            
            # Add optional fields
            if metadata.get('doi'):
                result['doi'] = metadata['doi']
            if metadata.get('url'):
                result['url'] = metadata['url']
            if metadata.get('arxiv_id'):
                result['arxiv'] = metadata['arxiv_id']
            if metadata.get('pages'):
                result['pages'] = metadata['pages']
            if metadata.get('volume'):
                result['volume'] = metadata['volume']
            if metadata.get('number'):
                result['number'] = metadata['number']
            
            return {k: v for k, v in result.items() if v}
            
        except Exception as e:
            self.logger.error(f"Failed to convert search metadata: {str(e)}")
            return None
    
    def _format_authors(self, authors: List[Dict]) -> str:
        """Format the author list"""
        formatted_authors = []
        for author in authors:
            given = author.get('given', '')
            family = author.get('family', '')
            if family:
                if given:
                    formatted_authors.append(f"{family}, {given}")
                else:
                    formatted_authors.append(family)
        
        return ' and '.join(formatted_authors)
    
    def _extract_year(self, work: Dict) -> Optional[str]:
        """Extract publication year"""
        # Try multiple date fields
        date_fields = ['published-print', 'published-online', 'created']
        for field in date_fields:
            if field in work:
                date_parts = work[field].get('date-parts', [[]])
                if date_parts and date_parts[0]:
                    return str(date_parts[0][0])
        return None
    
    def _generate_bibtex_key(self, metadata: Dict) -> str:
        """Generate BibTeX key"""
        # Format: First author's surname + year + first word of the title
        key_parts = []
        
        # First author's surname
        if metadata.get('author'):
            first_author = metadata['author'].split(' and ')[0]
            if ',' in first_author:
                family_name = first_author.split(',')[0].strip()
            else:
                family_name = first_author.split()[-1]
            key_parts.append(re.sub(r'[^\w]', '', family_name))
        
        # Year
        if metadata.get('year'):
            key_parts.append(metadata['year'])
        
        # First word of title
        if metadata.get('title'):
            title_words = metadata['title'].split()
            if title_words:
                first_word = re.sub(r'[^\w]', '', title_words[0])
                key_parts.append(first_word)
        
        return ''.join(key_parts) or 'unknown'
    
    def _complete_fields(self, base_record: Dict, template: Dict) -> Dict:
        """Complete missing fields according to template"""
        completed_data = base_record.copy()
        
        # Check required fields in template
        for field_config in template.get('fields', []):
            field_name = field_config['name']
            
            # If field is missing and has completion strategy
            if field_name not in completed_data or not completed_data[field_name]:
                if 'source_priority' in field_config:
                    value = self._fetch_missing_field(field_name, field_config['source_priority'], base_record)
                    if value:
                        completed_data[field_name] = value
        
        return completed_data
    
    def _fetch_missing_field(self, field_name: str, source_priority: List[str], base_record: Dict) -> Optional[str]:
        """Get missing fields according to priority strategy"""
        for source in source_priority:
            if source == 'crossref_api':
                # Already got from CrossRef, skip
                continue
            elif source == 'google_scholar_scraper':
                # Simplified implementation: complete from Google Scholar search
                value = self._fetch_from_google_scholar(field_name, base_record)
                if value:
                    return value
            elif source == 'user_prompt':
                # User input not handled here, left to frontend
                continue
        
        return None
    
    def _fetch_from_google_scholar(self, field_name: str, base_record: Dict) -> Optional[str]:
        """Get field value from Google Scholar (simplified implementation)"""
        try:
            # Search using title and authors
            query = base_record.get('title', '')
            if not query:
                return None
            
            search_query = scholarly.search_pubs(query)
            pub = next(search_query, None)
            
            if pub and field_name in pub:
                return str(pub[field_name])
                
        except Exception as e:
            self.logger.warning(f"Getting field {field_name} from Google Scholar failed: {str(e)}")
        
        return None


class FormatterModule:
    """Stage 4: Formatting and Generation Module"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def format(self, completed_entries: List[CompletedEntry], 
               output_format: str) -> Dict[str, Any]:
        """
        Format completed records to specified output format
        
        Args:
            completed_entries: List of completed records
            output_format: Output format
        
        Returns:
            Formatting results and report
        """
        self.logger.info(f"Starting to format {len(completed_entries)} entries to {output_format} format")
        
        formatted_strings = []
        failed_entries = []
        
        for entry in completed_entries:
            if entry['status'] == 'completed':
                try:
                    if output_format.lower() == 'bibtex':
                        formatted_string = self._format_bibtex(entry)
                    elif output_format.lower() == 'apa':
                        formatted_string = self._format_apa(entry)
                    elif output_format.lower() == 'mla':
                        formatted_string = self._format_mla(entry)
                    else:
                        # Default to BibTeX
                        formatted_string = self._format_bibtex(entry)
                    
                    formatted_strings.append(formatted_string)
                    
                except Exception as e:
                    self.logger.error(f"Formatting entry {entry['id']} failed: {str(e)}")
                    failed_entries.append({
                        'id': entry['id'],
                        'error': str(e),
                        'doi': entry.get('doi', 'unknown')
                    })
            else:
                failed_entries.append({
                    'id': entry['id'],
                    'error': 'Entry processing failed',
                    'status': entry['status']
                })
        
        report = {
            'total': len(completed_entries),
            'succeeded': len(formatted_strings),
            'failed_entries': failed_entries
        }
        
        self.logger.info(f"Formatting completed: {len(formatted_strings)}/{len(completed_entries)} entries successful")
        
        return {
            'results': formatted_strings,
            'report': report
        }
    
    def _format_bibtex(self, entry: CompletedEntry) -> str:
        """Format to BibTeX format"""
        bib_data = entry['bib_data']
        entry_type = bib_data.get('ENTRYTYPE', 'article')
        entry_id = bib_data.get('ID', entry['bib_key'])
        
        lines = [f"@{entry_type}{{{entry_id},"]
        
        for key, value in bib_data.items():
            if key not in ['ENTRYTYPE', 'ID'] and value:
                # Clean and format values
                clean_value = str(value).replace('{', '').replace('}', '')
                if key in ['volume', 'number', 'year']:
                    lines.append(f"  {key} = {clean_value},")
                else:
                    lines.append(f'  {key} = "{clean_value}",')
        
        lines.append('}')
        return '\n'.join(lines)
    
    def _format_apa(self, entry: CompletedEntry) -> str:
        """Format to APA format"""
        bib_data = entry['bib_data']
        parts = []
        
        # Authors
        if bib_data.get('author'):
            authors = bib_data['author'].replace(' and ', ', ')
            parts.append(authors)
        
        # Year
        if bib_data.get('year'):
            parts.append(f"({bib_data['year']})")
        
        # Title
        if bib_data.get('title'):
            parts.append(f"{bib_data['title']}.")
        
        # Journal information
        if bib_data.get('journal'):
            journal_part = f"*{bib_data['journal']}*"
            if bib_data.get('volume'):
                journal_part += f", {bib_data['volume']}"
            if bib_data.get('number'):
                journal_part += f"({bib_data['number']})"
            if bib_data.get('pages'):
                journal_part += f", {bib_data['pages']}"
            parts.append(journal_part + ".")
        
        return ' '.join(parts)
    
    def _format_mla(self, entry: CompletedEntry) -> str:
        """Format to MLA format (simplified implementation)"""
        # Simplified MLA format, should be more complex in practice
        return self._format_apa(entry)
