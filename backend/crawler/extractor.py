"""
Docusaurus content extractor for the Book Content Embeddings Backend.

Extracts clean text content from Docusaurus documentation sites.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
from urllib.parse import urljoin, urlparse
import re

from models.entities import DocumentContent
from utils.logger import get_logger
from utils.exceptions import CrawlerError, ContentExtractionError
from services.base_service import CrawlerService


class DocusaurusExtractor(CrawlerService):
    """Extracts clean content from Docusaurus documentation sites."""

    def __init__(self, session: requests.Session = None):
        super().__init__()
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; BookEmbeddingsBot/1.0; +http://example.com/bot)'
        })

    def _execute(self, url: str, include_subpages: bool = False) -> List[DocumentContent]:
        """
        Extract content from a Docusaurus URL.

        Args:
            url: The Docusaurus URL to extract content from
            include_subpages: Whether to follow links and extract subpages

        Returns:
            List of DocumentContent objects containing the extracted content
        """
        if include_subpages:
            return self.extract_with_subpages(url)
        else:
            return [self.extract_single_page(url)]

    def extract_single_page(self, url: str) -> DocumentContent:
        """
        Extract content from a single Docusaurus page.

        Args:
            url: The URL to extract content from

        Returns:
            DocumentContent object with the extracted content
        """
        try:
            # Fetch the page
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else "Untitled"

            # Extract main content by looking for common Docusaurus content containers
            content = self._extract_main_content(soup)

            # Create DocumentContent object
            doc_content = DocumentContent(
                url=url,
                title=title,
                content=content
            )

            self.logger.info(f"Successfully extracted content from {url} ({len(content)} chars)")

            return doc_content

        except requests.RequestException as e:
            raise CrawlerError(
                f"Failed to fetch URL {url}: {str(e)}",
                url=url,
                status_code=getattr(e.response, 'status_code', None)
            )
        except Exception as e:
            raise ContentExtractionError(
                f"Failed to extract content from {url}: {str(e)}",
                url=url
            )

    def extract_with_subpages(self, base_url: str) -> List[DocumentContent]:
        """
        Extract content from a Docusaurus site including subpages.

        Args:
            base_url: The base URL of the Docusaurus site

        Returns:
            List of DocumentContent objects containing content from all pages
        """
        # Try to use sitemap.xml for comprehensive coverage
        sitemap_url = base_url.rstrip('/') + '/sitemap.xml'
        urls = self._get_urls_from_sitemap(sitemap_url, base_url)

        if not urls:
            # Fallback to link crawling if sitemap is not available
            self.logger.info("Sitemap not found, falling back to link crawling")
            urls = self._get_urls_by_crawling(base_url)

        all_docs = []
        for url in urls:
            try:
                doc = self.extract_single_page(url)
                all_docs.append(doc)

                # Be respectful with rate limiting
                time.sleep(0.5)

            except Exception as e:
                self.logger.warning(f"Failed to process {url}: {str(e)}")
                continue

        self.logger.info(f"Successfully extracted {len(all_docs)} pages from {base_url}")
        return all_docs

    def _get_urls_from_sitemap(self, sitemap_url: str, base_url: str) -> List[str]:
        """
        Extract URLs from sitemap.xml.

        Args:
            sitemap_url: URL of the sitemap.xml file
            base_url: Base URL for domain validation

        Returns:
            List of URLs extracted from sitemap
        """
        try:
            response = self.session.get(sitemap_url, timeout=30)
            response.raise_for_status()

            # Try different parsers in order of preference
            parsers_to_try = ['xml', 'lxml-xml', 'html.parser']

            soup = None
            for parser in parsers_to_try:
                try:
                    soup = BeautifulSoup(response.content, parser)
                    break
                except Exception:
                    continue

            if soup is None:
                raise Exception("Could not parse with any available parser")

            # Find all <url><loc> elements in the sitemap
            url_elements = soup.find_all('loc')
            urls = []

            for elem in url_elements:
                url = elem.get_text().strip()
                if url and self._is_same_domain(base_url, url):
                    # Filter out non-documentation URLs if needed
                    if self._is_documentation_url(url):
                        urls.append(url)

            self.logger.info(f"Found {len(urls)} URLs from sitemap")
            return urls

        except Exception as e:
            self.logger.warning(f"Could not fetch or parse sitemap {sitemap_url}: {str(e)}")
            return []

    def _get_urls_by_crawling(self, base_url: str) -> List[str]:
        """
        Extract URLs by crawling and following links (fallback method).

        Args:
            base_url: The base URL of the Docusaurus site

        Returns:
            List of URLs found by crawling
        """
        urls = []
        visited_urls = set()
        urls_to_visit = [base_url]

        while urls_to_visit:
            current_url = urls_to_visit.pop(0)

            # Skip if already visited
            if current_url in visited_urls:
                continue

            # Only process URLs from the same domain
            if not self._is_same_domain(base_url, current_url):
                continue

            visited_urls.add(current_url)
            urls.append(current_url)

            # Find links on the page to add to queue
            if len(visited_urls) < 50:  # Limit to prevent infinite crawling
                try:
                    response = self.session.get(current_url, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    new_urls = self._find_internal_links(soup, base_url)
                    for new_url in new_urls:
                        if new_url not in visited_urls and new_url not in urls_to_visit:
                            urls_to_visit.append(new_url)
                except Exception as e:
                    self.logger.warning(f"Failed to crawl links from {current_url}: {str(e)}")
                    continue

        self.logger.info(f"Found {len(urls)} URLs by crawling")
        return urls

    def _is_documentation_url(self, url: str) -> bool:
        """
        Check if a URL is likely to be documentation content.

        Args:
            url: URL to check

        Returns:
            True if URL appears to be documentation content
        """
        # Exclude common non-documentation URLs
        excluded_patterns = [
            '/blog/',
            '/tag',
            '/author',
            '/search',
            '/assets/',
            '.css',
            '.js',
            '.png',
            '.jpg',
            '.jpeg',
            '.gif',
            '.svg',
            '.ico',
            '.pdf'
        ]

        url_lower = url.lower()
        for pattern in excluded_patterns:
            if pattern in url_lower:
                return False

        # Include URLs that look like documentation pages
        doc_patterns = ['/docs/', '/chapter', '/lesson', '/guide', '/tutorial']
        for pattern in doc_patterns:
            if pattern in url_lower:
                return True

        # If it doesn't match any exclusion patterns, assume it's content
        return True

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extract the main content from a BeautifulSoup object.

        Args:
            soup: BeautifulSoup object containing the parsed HTML

        Returns:
            Clean text content
        """
        # Look for common Docusaurus content containers in order of preference
        content_selectors = [
            'main div[class*="docItem"]',  # Docusaurus v2+ doc item
            'article',  # Standard article tag
            'main',  # Main content area
            'div.main-wrapper',  # Docusaurus main wrapper
            'div[class*="docContent"]',  # Docusaurus doc content
            'div[class*="container"]',  # General container
            'div.content',  # Generic content div
        ]

        content_element = None
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                break

        if content_element:
            # Remove navigation, headers, and other non-content elements
            for element in content_element.find_all(['nav', 'header', 'footer', 'aside']):
                element.decompose()

            # Remove script and style elements
            for element in content_element.find_all(['script', 'style', 'noscript']):
                element.decompose()

            # Get text content and clean it up
            text_content = content_element.get_text(separator=' ', strip=True)
        else:
            # If no specific content container found, try to get all text
            text_content = soup.get_text(separator=' ', strip=True)

        # Clean up the text
        text_content = re.sub(r'\s+', ' ', text_content)  # Replace multiple spaces with single space
        text_content = text_content.strip()

        return text_content

    def _is_same_domain(self, base_url: str, url: str) -> bool:
        """
        Check if two URLs are from the same domain.

        Args:
            base_url: The base URL
            url: The URL to check

        Returns:
            True if both URLs are from the same domain, False otherwise
        """
        base_domain = urlparse(base_url).netloc
        url_domain = urlparse(url).netloc
        return base_domain == url_domain

    def _find_internal_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Find internal links on a page.

        Args:
            soup: BeautifulSoup object containing the parsed HTML
            base_url: The base URL to resolve relative links against

        Returns:
            List of internal URLs found on the page
        """
        links = []
        base_domain = urlparse(base_url).netloc

        for link in soup.find_all('a', href=True):
            href = link['href']

            # Skip anchor links and external links
            if href.startswith('#') or '://' in href and urlparse(href).netloc != base_domain:
                continue

            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)

            # Only add if it's a documentation page (not an external link)
            if self._is_same_domain(base_url, absolute_url):
                # Filter out non-documentation URLs (like social media, etc.)
                if not any(skip in absolute_url.lower() for skip in ['twitter', 'github', 'facebook', 'linkedin']):
                    links.append(absolute_url)

        return list(set(links))  # Remove duplicates