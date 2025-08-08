"""
Documentation scraper for GitScribe.

Handles web scraping of documentation from various sources including
Git repositories, documentation websites, and static site generators.
"""

import asyncio
import logging
import re
import ssl
import time
from typing import Dict, List, Optional, Set, Tuple, Any
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path
import aiohttp
from bs4 import BeautifulSoup
import markdown
import git
from git import Repo
import tempfile
import shutil

from .config import GitScribeConfig
from .parsers import DocumentParserFactory

logger = logging.getLogger(__name__)


class DocumentationScraper:
    """Scrapes documentation from various sources."""
    
    def __init__(self, config: GitScribeConfig):
        """Initialize the scraper."""
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.visited_urls: Set[str] = set()
        self.scraped_content: List[Dict[str, Any]] = []
        self.rate_limiter = asyncio.Semaphore(config.concurrent_requests)
        self.last_request_time = 0.0
        self.parser_factory = DocumentParserFactory()
    
    async def __aenter__(self):
        """Async context manager entry."""
        # Create SSL context that's more permissive for development
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers=self.config.get_headers(),
            connector=connector
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def cleanup(self):
        """Clean up scraper resources."""
        logger.info("Cleaning up scraper resources...")
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("Scraper cleanup completed")
    
    async def scrape_documentation(
        self, 
        url: str, 
        max_depth: Optional[int] = None,
        supported_formats: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Scrape documentation from a URL.
        
        Args:
            url: The URL to scrape
            max_depth: Maximum crawling depth
            supported_formats: List of supported file formats
        
        Returns:
            List of scraped documents
        """
        max_depth = max_depth or self.config.max_depth
        supported_formats = supported_formats or self.config.supported_formats
        
        logger.info(f"Starting documentation scraping from {url}")
        
        # Reset state
        self.visited_urls.clear()
        self.scraped_content.clear()
        
        async with self:
            # Check if it's a Git repository
            if self._is_git_repository(url):
                await self._scrape_git_repository(url, supported_formats)
            else:
                await self._scrape_website(url, max_depth, supported_formats)
        
        logger.info(f"Scraping completed. Found {len(self.scraped_content)} documents")
        return self.scraped_content
    
    def _is_git_repository(self, url: str) -> bool:
        """Check if URL points to a Git repository."""
        parsed = urlparse(url)
        git_indicators = [
            'github.com', 'gitlab.com', 'bitbucket.org', 'dev.azure.com',
            '.git', '/tree/', '/blob/', '/src/'
        ]
        return any(indicator in url.lower() for indicator in git_indicators)
    
    async def _scrape_git_repository(self, url: str, supported_formats: List[str]):
        """Scrape documentation from a Git repository."""
        logger.info(f"Scraping Git repository: {url}")
        
        # Convert GitHub/GitLab URLs to clone URLs if needed
        clone_url = self._get_clone_url(url)
        
        # Clone repository to temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                logger.info(f"Cloning repository to {temp_dir}")
                repo = Repo.clone_from(clone_url, temp_dir, depth=1)
                
                # Scan repository for documentation files
                await self._scan_repository_files(temp_dir, supported_formats, url)
                
            except Exception as e:
                logger.error(f"Error cloning repository {clone_url}: {e}")
                # Fallback to web scraping if cloning fails
                await self._scrape_website(url, self.config.max_depth, supported_formats)
    
    def _get_clone_url(self, url: str) -> str:
        """Convert web URL to clone URL."""
        if url.endswith('.git'):
            return url
        
        # GitHub
        if 'github.com' in url:
            # Convert https://github.com/user/repo to https://github.com/user/repo.git
            clean_url = url.split('/tree/')[0].split('/blob/')[0]
            return f"{clean_url}.git"
        
        # GitLab
        if 'gitlab.com' in url:
            clean_url = url.split('/-/')[0].split('/tree/')[0]
            return f"{clean_url}.git"
        
        # Bitbucket
        if 'bitbucket.org' in url:
            clean_url = url.split('/src/')[0]
            return f"{clean_url}.git"
        
        return url
    
    async def _scan_repository_files(self, repo_path: str, supported_formats: List[str], base_url: str):
        """Scan repository files for documentation."""
        repo_path_obj = Path(repo_path)
        
        for file_path in repo_path_obj.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(repo_path_obj)
                
                # Check if file should be ignored
                if self.config.should_ignore(str(relative_path)):
                    continue
                
                # Check if file format is supported
                if not self.config.is_supported_format(str(file_path)):
                    continue
                
                try:
                    content = await self._read_file_content(file_path)
                    if content:
                        # Use parser to extract structured content
                        parsed_doc = self.parser_factory.parse_document(str(relative_path), content)
                        
                        if parsed_doc:
                            doc = {
                                'url': f"{base_url}/blob/main/{relative_path}",
                                'title': parsed_doc.title,
                                'content': parsed_doc.content,
                                'metadata': parsed_doc.metadata,
                                'sections': parsed_doc.sections,
                                'code_blocks': parsed_doc.code_blocks,
                                'links': parsed_doc.links,
                                'file_path': str(relative_path),
                                'file_type': file_path.suffix.lower().lstrip('.'),
                                'source_type': 'git_repository',
                                'base_url': base_url,
                                'scraped_at': time.time()
                            }
                        else:
                            # Fallback to basic structure
                            doc = {
                                'url': f"{base_url}/blob/main/{relative_path}",
                                'title': file_path.name,
                                'content': content,
                                'file_path': str(relative_path),
                                'file_type': file_path.suffix.lower().lstrip('.'),
                                'source_type': 'git_repository',
                                'base_url': base_url,
                                'scraped_at': time.time()
                            }
                        
                        self.scraped_content.append(doc)
                        
                except Exception as e:
                    logger.warning(f"Error reading file {file_path}: {e}")
    
    async def _read_file_content(self, file_path: Path) -> Optional[str]:
        """Read content from a file."""
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    
                    # Convert markdown to text if needed
                    if file_path.suffix.lower() in ['.md', '.markdown']:
                        content = self._markdown_to_text(content)
                    
                    return content
                except UnicodeDecodeError:
                    continue
            
            logger.warning(f"Could not decode file {file_path}")
            return None
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    def _markdown_to_text(self, md_content: str) -> str:
        """Convert markdown content to plain text."""
        try:
            html = markdown.markdown(md_content)
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
        except Exception:
            # Fallback: basic markdown stripping
            text = re.sub(r'#+ ', '', md_content)  # Remove headers
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
            text = re.sub(r'\*(.*?)\*', r'\1', text)  # Remove italic
            text = re.sub(r'`(.*?)`', r'\1', text)  # Remove inline code
            text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Remove links
            return text
    
    async def _scrape_website(self, url: str, max_depth: int, supported_formats: List[str]):
        """Scrape documentation from a website."""
        logger.info(f"Scraping website: {url}")
        
        urls_to_visit = [(url, 0)]  # (url, depth)
        
        while urls_to_visit and len(self.scraped_content) < self.config.max_pages:
            current_url, depth = urls_to_visit.pop(0)
            
            if current_url in self.visited_urls or depth > max_depth:
                continue
            
            self.visited_urls.add(current_url)
            
            try:
                async with self.rate_limiter:
                    # Rate limiting
                    await self._apply_rate_limit()
                    
                    # Fetch page content
                    content_data = await self._fetch_page_content(current_url)
                    if content_data:
                        self.scraped_content.append(content_data)
                        
                        # Extract links for further crawling
                        if depth < max_depth:
                            new_urls = self._extract_links(content_data.get('raw_html', ''), current_url)
                            for new_url in new_urls:
                                if new_url not in self.visited_urls:
                                    urls_to_visit.append((new_url, depth + 1))
                
            except Exception as e:
                logger.warning(f"Error scraping {current_url}: {e}")
                
            # Respect rate limits
            await asyncio.sleep(0.1)
    
    async def _apply_rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.config.request_delay:
            await asyncio.sleep(self.config.request_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    async def _fetch_page_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch content from a web page."""
        if not self.session:
            return None
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
                
                content_type = response.headers.get('Content-Type', '').lower()
                
                # Only process text content
                if not any(ct in content_type for ct in ['text/', 'application/json', 'application/xml']):
                    return None
                
                html_content = await response.text()
                
                # Parse HTML content
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract title
                title = soup.find('title')
                title_text = title.get_text(strip=True) if title else urlparse(url).path.split('/')[-1]
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Extract main content
                main_content = self._extract_main_content(soup)
                
                # Extract code blocks
                code_blocks = self._extract_code_blocks(soup)
                
                # Try to parse with document parsers for better extraction
                parsed_doc = self.parser_factory.parse_document(url, html_content)
                
                if parsed_doc:
                    return {
                        'url': url,
                        'title': parsed_doc.title,
                        'content': parsed_doc.content,
                        'metadata': parsed_doc.metadata,
                        'sections': parsed_doc.sections,
                        'code_blocks': parsed_doc.code_blocks,
                        'links': parsed_doc.links,
                        'raw_html': html_content,
                        'content_type': content_type,
                        'source_type': 'website',
                        'scraped_at': time.time()
                    }
                else:
                    # Fallback to basic extraction
                    return {
                    'url': url,
                    'title': title_text,
                    'content': main_content,
                    'code_blocks': code_blocks,
                    'raw_html': html_content,
                    'content_type': content_type,
                    'source_type': 'website',
                    'scraped_at': time.time()
                }
                
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML."""
        # Try to find main content area
        main_selectors = [
            'main', 'article', '.content', '.main-content', 
            '.documentation', '.docs', '#content', '.container'
        ]
        
        for selector in main_selectors:
            main_element = soup.select_one(selector)
            if main_element:
                return main_element.get_text(separator=' ', strip=True)
        
        # Fallback to body content
        body = soup.find('body')
        if body:
            return body.get_text(separator=' ', strip=True)
        
        return soup.get_text(separator=' ', strip=True)
    
    def _extract_code_blocks(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract code blocks from HTML."""
        code_blocks = []
        
        # Find code blocks
        for code_element in soup.find_all(['code', 'pre']):
            code_text = code_element.get_text(strip=True)
            if len(code_text) > 10:  # Only meaningful code blocks
                language = self._detect_code_language(code_element)
                code_blocks.append({
                    'code': code_text,
                    'language': language,
                    'context': self._get_code_context(code_element)
                })
        
        return code_blocks
    
    def _detect_code_language(self, code_element) -> str:
        """Detect programming language from code element."""
        # Check class attributes for language hints
        classes = code_element.get('class', [])
        for cls in classes:
            if cls.startswith('language-'):
                return cls.replace('language-', '')
            if cls.startswith('lang-'):
                return cls.replace('lang-', '')
        
        # Check parent classes
        parent = code_element.parent
        if parent:
            parent_classes = parent.get('class', [])
            for cls in parent_classes:
                if cls.startswith('language-'):
                    return cls.replace('language-', '')
        
        return 'unknown'
    
    def _get_code_context(self, code_element) -> str:
        """Get context around code block."""
        # Look for preceding heading or paragraph
        context_elements = []
        
        current = code_element
        while current and len(context_elements) < 3:
            prev_sibling = current.find_previous_sibling(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])
            if prev_sibling:
                context_elements.append(prev_sibling.get_text(strip=True))
                current = prev_sibling
            else:
                break
        
        return ' '.join(reversed(context_elements))
    
    def _extract_links(self, html_content: str, base_url: str) -> List[str]:
        """Extract links from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # Filter links
            if self._should_follow_link(full_url, base_url):
                links.append(full_url)
        
        return links
    
    def _should_follow_link(self, url: str, base_url: str) -> bool:
        """Check if a link should be followed."""
        parsed_url = urlparse(url)
        parsed_base = urlparse(base_url)
        
        # Only follow links on the same domain
        if parsed_url.netloc != parsed_base.netloc:
            return False
        
        # Skip certain file types
        skip_extensions = ['.pdf', '.doc', '.docx', '.zip', '.tar', '.gz', '.exe']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Skip fragments and query parameters for now
        if '#' in url or '?' in url:
            return False
        
        return True
