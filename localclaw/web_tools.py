"""Web search tools for LocalClaw"""
import json
import urllib.request
import urllib.parse
from typing import List, Dict, Any


class WebSearch:
    """Web search using DuckDuckGo (no API key required)"""
    
    DUCKDUCKGO_URL = "https://duckduckgo.com/html/"
    
    def __init__(self, max_results: int = 5):
        self.max_results = max_results
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search the web using DuckDuckGo"""
        try:
            # DuckDuckGo instant answer API (no rate limit, no key)
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&skip_disambig=1"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
            results = []
            
            # Add abstract if available
            if data.get('AbstractText'):
                results.append({
                    'title': data.get('Heading', 'Instant Answer'),
                    'snippet': data['AbstractText'],
                    'url': data.get('AbstractURL', '')
                })
            
            # Add related topics
            for topic in data.get('RelatedTopics', [])[:self.max_results - len(results)]:
                if 'Text' in topic:
                    results.append({
                        'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                        'snippet': topic['Text'],
                        'url': topic.get('FirstURL', '')
                    })
            
            return results
            
        except Exception as e:
            # Fallback: return helpful message with search suggestions
            return [{
                'title': 'Search unavailable',
                'snippet': f'Could not perform web search: {str(e)}. Try searching manually at https://duckduckgo.com/?q={urllib.parse.quote(query)}',
                'url': f'https://duckduckgo.com/?q={urllib.parse.quote(query)}'
            }]
    
    def search_formatted(self, query: str) -> str:
        """Search and return formatted results"""
        results = self.search(query)
        
        if not results:
            return "No results found."
        
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"{i}. **{result['title']}**\n   {result['snippet'][:200]}...\n   <{result['url']}>\n")
        
        return "\n".join(formatted)


class WebFetch:
    """Fetch and extract content from URLs"""
    
    def __init__(self, max_chars: int = 5000):
        self.max_chars = max_chars
    
    def fetch(self, url: str) -> Dict[str, Any]:
        """Fetch content from a URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read().decode('utf-8', errors='ignore')
            
            # Simple HTML to text extraction
            text = self._extract_text(content)
            
            return {
                'url': url,
                'title': self._extract_title(content),
                'content': text[:self.max_chars],
                'truncated': len(text) > self.max_chars
            }
            
        except Exception as e:
            return {
                'url': url,
                'title': 'Error',
                'content': f'Failed to fetch URL: {str(e)}',
                'truncated': False
            }
    
    def _extract_title(self, html: str) -> str:
        """Extract title from HTML"""
        import re
        match = re.search(r'<title[^>]*>([^<]*)</title>', html, re.IGNORECASE)
        return match.group(1).strip() if match else 'No title'
    
    def _extract_text(self, html: str) -> str:
        """Simple HTML to text extraction"""
        import re
        
        # Remove script and style tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+?>', ' ', html)
        
        # Decode HTML entities
        import html as html_module
        text = html_module.unescape(text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def fetch_formatted(self, url: str) -> str:
        """Fetch and return formatted content"""
        result = self.fetch(url)
        
        truncated_note = "\n\n[Content truncated...]" if result['truncated'] else ""
        
        return f"**{result['title']}**\n<{result['url']}>\n\n{result['content']}{truncated_note}"
