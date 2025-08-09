"""
qfetch - Quick Fetch: Fast, simple, and beautifully minimal web scraping.

A lightweight Python library that makes web scraping and data fetching
fast, simple, and beautifully minimal with just 1-2 lines of code.
"""

import requests
from selectolax.parser import HTMLParser
import json
from typing import Union, List, Optional, Any
from urllib.parse import urljoin, urlparse


class QFetchResponse:
    """Response object with HTML parsing and JSON capabilities."""
    
    def __init__(self, response: requests.Response):
        self.response = response
        self._html_parser = None
        self._is_html = None
        self._is_json = None
        
    @property
    def html(self) -> Optional[str]:
        """Get raw HTML content if the response is HTML."""
        if self._is_html is None:
            self._detect_content_type()
        return self.response.text if self._is_html else None
    
    @property
    def json(self) -> Optional[Any]:
        """Get parsed JSON content if the response is JSON."""
        if self._is_json is None:
            self._detect_content_type()
        if self._is_json:
            try:
                return self.response.json()
            except json.JSONDecodeError:
                return None
        return None
    
    def select(self, css_selector: str) -> List['QFetchElement']:
        """Select elements using CSS selector."""
        if not self._html_parser:
            self._parse_html()
        
        if not self._html_parser:
            return []
        
        elements = self._html_parser.css(css_selector)
        return [QFetchElement(elem) for elem in elements]
    
    def xpath(self, xpath_expr: str) -> List['QFetchElement']:
        """Select elements using XPath expression."""
        if not self._html_parser:
            self._parse_html()
        
        if not self._html_parser:
            return []
        
        elements = self._html_parser.xpath(xpath_expr)
        return [QFetchElement(elem) for elem in elements]
    
    @property
    def links(self) -> List[str]:
        """Get all hyperlinks on the page."""
        if not self._html_parser:
            self._parse_html()
        
        if not self._html_parser:
            return []
        
        links = []
        for link in self._html_parser.css('a[href]'):
            href = link.attributes.get('href')
            if href:
                # Make relative URLs absolute
                absolute_url = urljoin(self.response.url, href)
                links.append(absolute_url)
        
        return links
    
    @property
    def images(self) -> List[str]:
        """Get all image URLs on the page."""
        if not self._html_parser:
            self._parse_html()
        
        if not self._html_parser:
            return []
        
        images = []
        for img in self._html_parser.css('img[src]'):
            src = img.attributes.get('src')
            if src:
                # Make relative URLs absolute
                absolute_url = urljoin(self.response.url, src)
                images.append(absolute_url)
        
        return images
    
    def _detect_content_type(self):
        """Detect if response is HTML or JSON based on content-type and content."""
        content_type = self.response.headers.get('content-type', '').lower()
        
        # Check content-type header first
        if 'application/json' in content_type:
            self._is_json = True
            self._is_html = False
        elif 'text/html' in content_type:
            self._is_html = True
            self._is_json = False
        else:
            # Fallback: try to parse as JSON, if it fails, assume HTML
            try:
                self.response.json()
                self._is_json = True
                self._is_html = False
            except (json.JSONDecodeError, ValueError):
                self._is_html = True
                self._is_json = False
    
    def _parse_html(self):
        """Parse HTML content."""
        if self._is_html is None:
            self._detect_content_type()
        
        if self._is_html:
            try:
                self._html_parser = HTMLParser(self.response.text)
            except Exception:
                self._html_parser = None


class QFetchElement:
    """Wrapper for HTML elements with convenient accessors."""
    
    def __init__(self, element):
        self.element = element
    
    @property
    def text(self) -> str:
        """Get text content of the element."""
        return self.element.text() if self.element else ""
    
    @property
    def html(self) -> str:
        """Get HTML content of the element."""
        return self.element.html if self.element else ""
    
    @property
    def attrs(self) -> dict:
        """Get attributes of the element."""
        return self.element.attributes if self.element else {}
    
    def select(self, css_selector: str) -> List['QFetchElement']:
        """Select child elements using CSS selector."""
        if not self.element:
            return []
        
        elements = self.element.css(css_selector)
        return [QFetchElement(elem) for elem in elements]
    
    def __getitem__(self, attr: str) -> str:
        """Get attribute value."""
        return self.attrs.get(attr, "")
    
    def __str__(self) -> str:
        return self.text
    
    def __repr__(self) -> str:
        return f"<QFetchElement: {self.text[:50]}{'...' if len(self.text) > 50 else ''}>"


def get(url: str, **kwargs) -> QFetchResponse:
    """
    Fetch content from a URL and return a QFetchResponse object.
    
    Args:
        url: The URL to fetch
        **kwargs: Additional arguments to pass to requests.get()
    
    Returns:
        QFetchResponse object with HTML parsing and JSON capabilities
    
    Example:
        >>> from qfetch import get
        >>> page = get("https://example.com")
        >>> print(page.select("h1").text)
        >>> print(page.links)
    """
    try:
        response = requests.get(url, **kwargs)
        response.raise_for_status()
        return QFetchResponse(response)
    except requests.RequestException as e:
        # Create a mock response for error handling
        class MockResponse:
            def __init__(self, error):
                self.text = ""
                self.url = url
                self.headers = {}
                self.error = error
            
            def json(self):
                raise json.JSONDecodeError("Invalid JSON", "", 0)
        
        mock_response = MockResponse(e)
        return QFetchResponse(mock_response)


# Convenience function for backward compatibility
def fetch(url: str, **kwargs) -> QFetchResponse:
    """Alias for get() function."""
    return get(url, **kwargs)


__version__ = "0.1.0"
__author__ = "quickfetch"
__description__ = "Fast, simple, and beautifully minimal web scraping"
