"""
Document parsers for different formats supported by GitScribe.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
import html2text
from bs4 import BeautifulSoup
from markdown import markdown

logger = logging.getLogger(__name__)


@dataclass
class ParsedDocument:
    """Represents a parsed document with extracted content."""
    title: str
    content: str
    metadata: Dict
    sections: List[Dict]
    code_blocks: List[Dict]
    links: List[Dict]
    images: List[Dict]
    raw_content: str
    file_path: str
    format_type: str


class BaseParser(ABC):
    """Base class for document parsers."""
    
    def __init__(self):
        self.supported_extensions = []
    
    @abstractmethod
    def can_parse(self, file_path: str, content: str) -> bool:
        """Check if this parser can handle the given file."""
        pass
    
    @abstractmethod
    def parse(self, content: str, file_path: str) -> ParsedDocument:
        """Parse the document content."""
        pass
    
    def extract_code_blocks(self, content: str) -> List[Dict]:
        """Extract code blocks from content."""
        code_blocks = []
        
        # Match fenced code blocks (```language)
        fenced_pattern = r'```(\w*)\n(.*?)\n```'
        for match in re.finditer(fenced_pattern, content, re.DOTALL):
            language = match.group(1) or 'text'
            code = match.group(2).strip()
            if code:
                code_blocks.append({
                    'language': language,
                    'code': code,
                    'type': 'fenced'
                })
        
        # Match indented code blocks
        indented_pattern = r'(?:^|\n)(?:    .+(?:\n|$))+'
        for match in re.finditer(indented_pattern, content, re.MULTILINE):
            code = '\n'.join(line[4:] for line in match.group().strip().split('\n'))
            if code:
                code_blocks.append({
                    'language': 'text',
                    'code': code,
                    'type': 'indented'
                })
        
        return code_blocks
    
    def extract_links(self, content: str) -> List[Dict]:
        """Extract links from content."""
        links = []
        
        # Markdown links [text](url)
        md_link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(md_link_pattern, content):
            links.append({
                'text': match.group(1),
                'url': match.group(2),
                'type': 'markdown'
            })
        
        # HTML links
        html_link_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>'
        for match in re.finditer(html_link_pattern, content, re.IGNORECASE):
            links.append({
                'text': match.group(2),
                'url': match.group(1),
                'type': 'html'
            })
        
        return links
    
    def extract_sections(self, content: str) -> List[Dict]:
        """Extract sections/headings from content."""
        sections = []
        
        # Markdown headings
        heading_pattern = r'^(#{1,6})\s+(.+)$'
        for match in re.finditer(heading_pattern, content, re.MULTILINE):
            level = len(match.group(1))
            title = match.group(2).strip()
            sections.append({
                'level': level,
                'title': title,
                'type': 'markdown'
            })
        
        return sections


class MarkdownParser(BaseParser):
    """Parser for Markdown files."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['md', 'markdown', 'mdown', 'mkd']
    
    def can_parse(self, file_path: str, content: str) -> bool:
        """Check if this is a Markdown file."""
        extension = file_path.split('.')[-1].lower()
        return extension in self.supported_extensions
    
    def parse(self, content: str, file_path: str) -> ParsedDocument:
        """Parse Markdown content."""
        # Extract title from first heading or filename
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.split('/')[-1]
        
        # Extract metadata from front matter
        metadata = self._extract_frontmatter(content)
        
        # Remove front matter from content
        content_without_frontmatter = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
        
        # Convert to HTML for better text extraction
        html_content = markdown(content_without_frontmatter, extensions=['codehilite', 'tables', 'toc'])
        
        # Extract plain text
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        plain_content = h.handle(html_content)
        
        return ParsedDocument(
            title=title,
            content=plain_content,
            metadata=metadata,
            sections=self.extract_sections(content),
            code_blocks=self.extract_code_blocks(content),
            links=self.extract_links(content),
            images=self._extract_images(content),
            raw_content=content,
            file_path=file_path,
            format_type='markdown'
        )
    
    def _extract_frontmatter(self, content: str) -> Dict:
        """Extract YAML front matter from Markdown."""
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if frontmatter_match:
            try:
                import yaml
                return yaml.safe_load(frontmatter_match.group(1))
            except ImportError:
                logger.warning("PyYAML not installed, cannot parse front matter")
                return {}
            except yaml.YAMLError as e:
                logger.warning(f"Failed to parse YAML front matter: {e}")
                return {}
        return {}
    
    def _extract_images(self, content: str) -> List[Dict]:
        """Extract images from Markdown content."""
        images = []
        
        # Markdown images ![alt](url)
        img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        for match in re.finditer(img_pattern, content):
            images.append({
                'alt': match.group(1),
                'url': match.group(2),
                'type': 'markdown'
            })
        
        return images


class HTMLParser(BaseParser):
    """Parser for HTML files."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['html', 'htm', 'xhtml']
    
    def can_parse(self, file_path: str, content: str) -> bool:
        """Check if this is an HTML file."""
        extension = file_path.split('.')[-1].lower()
        if extension in self.supported_extensions:
            return True
        
        # Check content for HTML tags
        return bool(re.search(r'<html[^>]*>', content, re.IGNORECASE))
    
    def parse(self, content: str, file_path: str) -> ParsedDocument:
        """Parse HTML content."""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else file_path.split('/')[-1]
        
        # Extract metadata
        metadata = self._extract_html_metadata(soup)
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup.body or soup
        
        # Convert to text
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        plain_content = h.handle(str(main_content))
        
        return ParsedDocument(
            title=title,
            content=plain_content,
            metadata=metadata,
            sections=self._extract_html_sections(soup),
            code_blocks=self._extract_html_code_blocks(soup),
            links=self._extract_html_links(soup),
            images=self._extract_html_images(soup),
            raw_content=content,
            file_path=file_path,
            format_type='html'
        )
    
    def _extract_html_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract metadata from HTML head."""
        metadata = {}
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
        
        return metadata
    
    def _extract_html_sections(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract sections from HTML headings."""
        sections = []
        
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            level = int(heading.name[1])
            title = heading.get_text().strip()
            sections.append({
                'level': level,
                'title': title,
                'type': 'html'
            })
        
        return sections
    
    def _extract_html_code_blocks(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract code blocks from HTML."""
        code_blocks = []
        
        # Code elements
        for code in soup.find_all('code'):
            language = code.get('class', ['text'])[0] if code.get('class') else 'text'
            code_text = code.get_text().strip()
            if code_text:
                code_blocks.append({
                    'language': language,
                    'code': code_text,
                    'type': 'html'
                })
        
        # Pre elements
        for pre in soup.find_all('pre'):
            code_text = pre.get_text().strip()
            if code_text:
                code_blocks.append({
                    'language': 'text',
                    'code': code_text,
                    'type': 'html_pre'
                })
        
        return code_blocks
    
    def _extract_html_links(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract links from HTML."""
        links = []
        
        for link in soup.find_all('a', href=True):
            links.append({
                'text': link.get_text().strip(),
                'url': link['href'],
                'type': 'html'
            })
        
        return links
    
    def _extract_html_images(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract images from HTML."""
        images = []
        
        for img in soup.find_all('img', src=True):
            images.append({
                'alt': img.get('alt', ''),
                'url': img['src'],
                'type': 'html'
            })
        
        return images


class ReStructuredTextParser(BaseParser):
    """Parser for reStructuredText files."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['rst', 'rest']
    
    def can_parse(self, file_path: str, content: str) -> bool:
        """Check if this is a reStructuredText file."""
        extension = file_path.split('.')[-1].lower()
        return extension in self.supported_extensions
    
    def parse(self, content: str, file_path: str) -> ParsedDocument:
        """Parse reStructuredText content."""
        # Extract title (usually the first line followed by ===)
        lines = content.split('\n')
        title = file_path.split('/')[-1]
        
        for i, line in enumerate(lines[:-1]):
            if line.strip() and lines[i+1].strip().startswith('='):
                title = line.strip()
                break
        
        return ParsedDocument(
            title=title,
            content=content,
            metadata={},
            sections=self._extract_rst_sections(content),
            code_blocks=self._extract_rst_code_blocks(content),
            links=self.extract_links(content),
            images=[],
            raw_content=content,
            file_path=file_path,
            format_type='rst'
        )
    
    def _extract_rst_sections(self, content: str) -> List[Dict]:
        """Extract sections from reStructuredText."""
        sections = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines[:-1]):
            next_line = lines[i+1]
            if line.strip() and next_line.strip() and all(c in '=-~^"' for c in next_line.strip()):
                sections.append({
                    'level': 1,  # Simplified level detection
                    'title': line.strip(),
                    'type': 'rst'
                })
        
        return sections
    
    def _extract_rst_code_blocks(self, content: str) -> List[Dict]:
        """Extract code blocks from reStructuredText."""
        code_blocks = []
        
        # Code blocks starting with ::
        code_pattern = r'::\s*\n\n((?:    .+\n?)+)'
        for match in re.finditer(code_pattern, content):
            code = '\n'.join(line[4:] for line in match.group(1).split('\n') if line.strip())
            if code:
                code_blocks.append({
                    'language': 'text',
                    'code': code,
                    'type': 'rst'
                })
        
        return code_blocks


class CodeParser(BaseParser):
    """Parser for source code files."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['py', 'js', 'ts', 'java', 'cpp', 'c', 'go', 'rs', 'rb', 'php']
        self.comment_patterns = {
            'py': r'#.*$',
            'js': r'//.*$|/\*.*?\*/',
            'ts': r'//.*$|/\*.*?\*/',
            'java': r'//.*$|/\*.*?\*/',
            'cpp': r'//.*$|/\*.*?\*/',
            'c': r'//.*$|/\*.*?\*/',
            'go': r'//.*$|/\*.*?\*/',
            'rs': r'//.*$|/\*.*?\*/',
            'rb': r'#.*$',
            'php': r'//.*$|/\*.*?\*/|#.*$'
        }
    
    def can_parse(self, file_path: str, content: str) -> bool:
        """Check if this is a source code file."""
        extension = file_path.split('.')[-1].lower()
        return extension in self.supported_extensions
    
    def parse(self, content: str, file_path: str) -> ParsedDocument:
        """Parse source code file."""
        extension = file_path.split('.')[-1].lower()
        title = file_path.split('/')[-1]
        
        # Extract comments as documentation
        comments = self._extract_comments(content, extension)
        
        # Extract function/class definitions
        definitions = self._extract_definitions(content, extension)
        
        return ParsedDocument(
            title=title,
            content=content,
            metadata={'language': extension, 'definitions': definitions},
            sections=definitions,
            code_blocks=[{'language': extension, 'code': content, 'type': 'source'}],
            links=[],
            images=[],
            raw_content=content,
            file_path=file_path,
            format_type='code'
        )
    
    def _extract_comments(self, content: str, language: str) -> List[str]:
        """Extract comments from source code."""
        comments = []
        
        if language in self.comment_patterns:
            pattern = self.comment_patterns[language]
            for match in re.finditer(pattern, content, re.MULTILINE):
                comment = match.group(0).strip()
                if comment:
                    comments.append(comment)
        
        return comments
    
    def _extract_definitions(self, content: str, language: str) -> List[Dict]:
        """Extract function/class definitions from source code."""
        definitions = []
        
        patterns = {
            'py': [
                r'^(def\s+\w+\([^)]*\):)',
                r'^(class\s+\w+(?:\([^)]*\))?:)'
            ],
            'js': [
                r'(function\s+\w+\s*\([^)]*\))',
                r'(\w+\s*:\s*function\s*\([^)]*\))',
                r'(const\s+\w+\s*=\s*\([^)]*\)\s*=>)'
            ],
            'java': [
                r'(public\s+[\w\s]+\([^)]*\))',
                r'(private\s+[\w\s]+\([^)]*\))',
                r'(class\s+\w+)'
            ]
        }
        
        if language in patterns:
            for pattern in patterns[language]:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    definitions.append({
                        'level': 1,
                        'title': match.group(1),
                        'type': 'definition'
                    })
        
        return definitions


class DocumentParserFactory:
    """Factory for creating document parsers."""
    
    def __init__(self):
        self.parsers = [
            MarkdownParser(),
            HTMLParser(),
            ReStructuredTextParser(),
            CodeParser()
        ]
    
    def get_parser(self, file_path: str, content: str) -> Optional[BaseParser]:
        """Get appropriate parser for the given file."""
        for parser in self.parsers:
            if parser.can_parse(file_path, content):
                return parser
        return None
    
    def parse_document(self, file_path: str, content: str) -> Optional[ParsedDocument]:
        """Parse document using appropriate parser."""
        parser = self.get_parser(file_path, content)
        if parser:
            try:
                return parser.parse(content, file_path)
            except Exception as e:
                logger.error(f"Failed to parse {file_path}: {e}")
                return None
        
        logger.warning(f"No suitable parser found for {file_path}")
        return None
