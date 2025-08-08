#!/usr/bin/env python3
"""
WorldQuant BRAIN Forum Functions - Python Version
Comprehensive forum functionality including glossary, search, and post viewing.
"""

import asyncio
import re
import sys
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import os
import shutil

# Initialize forum MCP server
try:
    from mcp.server.fastmcp import FastMCP
    forum_mcp = FastMCP('brain_forum_server')
except ImportError:
    # Fallback for testing
    forum_mcp = None

def log(message: str, level: str = "INFO"):
    """Log message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}", file=sys.stderr)

class ForumClient:
    """Forum client for WorldQuant BRAIN support site."""
    
    def __init__(self):
        self.base_url = "https://support.worldquantbrain.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        })
        
    def get_brain_session(self):
        """Get authenticated session from BrainApiClient."""
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from platform_functions import brain_client
            return brain_client.session
        except ImportError:
            return None
        
    def check_webdriver_availability(self) -> Dict[str, Any]:
        """Check if WebDriver is available and provide installation guidance."""
        try:
            browser_type = self.detect_available_browser()
            driver = None
            
            try:
                driver = self.create_driver(headless=True)
                driver.quit()
                return {
                    "available": True,
                    "browser": browser_type,
                    "message": f"{browser_type.title()} WebDriver is available and working"
                }
            except Exception as e:
                return {
                    "available": False,
                    "browser": browser_type,
                    "error": str(e),
                    "help": self.get_driver_installation_help(browser_type)
                }
                
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "help": "Please install either ChromeDriver or Edge WebDriver"
            }
    
    def setup_chrome_options(self, headless: bool = True) -> Options:
        """Setup Chrome options for web scraping."""
        options = Options()
        
        if headless:
            options.add_argument('--headless')
        
        # Performance optimizations
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--log-level=3')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36')
        
        return options
    
    async def create_driver(self, headless: bool = True):
        """Create and configure WebDriver with cross-browser support."""
        browser_type = self.detect_available_browser()
        log(f"Using browser: {browser_type}", "INFO")
        
        options = self.setup_browser_options(headless, browser_type)
        
        try:
            if browser_type.lower() == "chrome":
                driver = webdriver.Chrome(options=options)
            elif browser_type.lower() == "edge":
                driver = webdriver.Edge(options=options)
            else:
                # Fallback to Chrome
                log("Falling back to Chrome", "WARNING")
                driver = webdriver.Chrome(options=options)
            
            # Set aggressive timeouts for speed
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            return driver
            
        except Exception as e:
            log(f"Failed to create {browser_type} driver: {str(e)}", "ERROR")
            help_text = self.get_driver_installation_help(browser_type)
            log(help_text, "ERROR")
            
            # Try Chrome as fallback if Edge failed
            if browser_type.lower() != "chrome":
                try:
                    log("Trying Chrome as fallback", "INFO")
                    chrome_options = self.setup_browser_options(headless, "chrome")
                    driver = webdriver.Chrome(options=chrome_options)
                    driver.set_page_load_timeout(30)
                    driver.implicitly_wait(10)
                    return driver
                except Exception as e2:
                    log(f"Chrome fallback also failed: {str(e2)}", "ERROR")
                    chrome_help = self.get_driver_installation_help("chrome")
                    log(chrome_help, "ERROR")
            
            raise Exception(f"Could not create any browser driver. {help_text}")
    
    async def login_to_forum(self, driver, email: str, password: str) -> bool:
        """Login to the WorldQuant BRAIN forum using existing authentication."""
        try:
            # Import BrainApiClient from platform_functions
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            
            try:
                from platform_functions import brain_client
                log("Using existing BrainApiClient for authentication", "INFO")
                
                # First authenticate with BrainApiClient
                auth_result = await brain_client.authenticate(email, password)
                if auth_result.get('status') != 'authenticated':
                    log("BrainApiClient authentication failed", "ERROR")
                    return False
                
                log("Successfully authenticated via BrainApiClient", "SUCCESS")
                
                # Navigate to forum with authenticated session
                log("Navigating to forum with authenticated session", "WORK")
                driver.get("https://support.worldquantbrain.com/hc/en-us")
                await asyncio.sleep(2)
                
                # Add authentication cookies to browser
                cookies = brain_client.session.cookies
                for cookie in cookies:
                    driver.add_cookie({
                        'name': cookie.name,
                        'value': cookie.value,
                        'domain': '.worldquantbrain.com'
                    })
                
                # Refresh page with cookies
                driver.refresh()
                await asyncio.sleep(2)
                
                return True
                
            except ImportError:
                log("BrainApiClient not available, using manual login", "WARNING")
                
                # Fallback to manual login
                driver.get("https://support.worldquantbrain.com/hc/en-us/signin")
                await asyncio.sleep(3)
                
                email_input = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "email"))
                )
                password_input = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "currentPassword"))
                )
                
                email_input.clear()
                email_input.send_keys(email)
                password_input.clear()
                password_input.send_keys(password)
                
                login_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))
                )
                login_button.click()
                await asyncio.sleep(3)
                
                return True
            
        except Exception as e:
            log(f"Login failed: {str(e)}", "ERROR")
            return False

    async def get_glossary_terms(self, email: str, password: str, headless: bool = False) -> Dict[str, Any]:
        """Extract glossary terms from the forum."""
        driver = None
        try:
            log("Starting glossary extraction process", "INFO")
            
            # Add timeout protection
            async def extraction_with_timeout():
                return await self._perform_glossary_extraction(email, password, headless)
            
            # Run with 5-minute timeout
            result = await asyncio.wait_for(extraction_with_timeout(), timeout=300)
            return result
            
        except asyncio.TimeoutError:
            log("Glossary extraction timed out after 5 minutes", "ERROR")
            return {"error": "Glossary extraction timed out after 5 minutes"}
        except Exception as e:
            log(f"Glossary extraction failed: {str(e)}", "ERROR")
            return {"error": str(e)}
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    async def _perform_glossary_extraction(self, email: str, password: str, headless: bool) -> Dict[str, Any]:
        """Perform the actual glossary extraction."""
        driver = None
        try:
            driver = await self.create_driver(headless)
            
            # Login
            if not await self.login_to_forum(driver, email, password):
                raise Exception("Failed to login to forum")
            
            # Navigate to glossary page
            log("Navigating to glossary page", "WORK")
            driver.get("https://support.worldquantbrain.com/hc/en-us/articles/4902349883927-Click-here-for-a-list-of-terms-and-their-definitions")
            await asyncio.sleep(5)
            
            # Extract content
            log("Extracting glossary content", "WORK")
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Parse glossary terms
            terms = self._parse_glossary_terms(page_source)
            
            log(f"Extracted {len(terms)} glossary terms", "SUCCESS")
            return {
                "terms": terms,
                "total_count": len(terms),
                "extraction_timestamp": datetime.now().isoformat()
            }
            
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def _parse_glossary_terms(self, content: str) -> List[Dict[str, str]]:
        """Parse glossary terms from HTML content."""
        terms = []
        lines = content.split('\n')
        
        current_term = None
        current_definition = []
        is_collecting_definition = False
        found_first_real_term = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip navigation and metadata lines at the beginning
            if not found_first_real_term and self._is_navigation_or_metadata(line):
                continue
            
            # Check if this line looks like a term
            if self._looks_like_term(line) and not is_collecting_definition:
                # Mark that we found the first real term
                if not found_first_real_term:
                    found_first_real_term = True
                
                # Save previous term if exists
                if current_term and current_definition:
                    terms.append({
                        "term": current_term.strip(),
                        "definition": " ".join(current_definition).strip()
                    })
                
                current_term = line
                current_definition = []
                is_collecting_definition = True
            elif is_collecting_definition and found_first_real_term:
                # Check if this is the start of a new term
                if self._looks_like_term(line):
                    # Save current term
                    if current_term and current_definition:
                        terms.append({
                            "term": current_term.strip(),
                            "definition": " ".join(current_definition).strip()
                        })
                    
                    current_term = line
                    current_definition = []
                else:
                    # Add to definition
                    if current_definition:
                        current_definition.append(line)
                    else:
                        current_definition = [line]
        
        # Don't forget the last term
        if current_term and current_definition and found_first_real_term:
            terms.append({
                "term": current_term.strip(),
                "definition": " ".join(current_definition).strip()
            })
        
        # Filter out invalid terms and improve quality
        return [term for term in terms if 
                len(term["term"]) > 0 and 
                len(term["definition"]) > 10 and  # Ensure meaningful definitions
                not self._is_navigation_or_metadata(term["term"]) and
                "ago" not in term["definition"] and  # Remove timestamp-like definitions
                "minute read" not in term["definition"]]  # Remove reading time

    def _looks_like_term(self, line: str) -> bool:
        """Check if a line looks like a glossary term."""
        # Skip very long lines (likely definitions)
        if len(line) > 100:
            return False
        
        # Skip navigation and metadata
        if self._is_navigation_or_metadata(line):
            return False
        
        # Skip lines that start with common definition words
        definition_starters = ['the', 'a', 'an', 'this', 'that', 'it', 'is', 'are', 'was', 'were', 'for', 'to', 'in', 'on', 'at', 'by', 'with']
        first_word = line.lower().split(' ')[0]
        if first_word and first_word in definition_starters:
            return False
        
        # Check if line has characteristics of a term
        # Terms are often short, may be all caps, or start with capital
        is_short = len(line) <= 80
        starts_with_capital = bool(re.match(r'^[A-Z]', line))
        has_all_caps = bool(re.match(r'^[A-Z\s\-\/\(\)]+$', line))
        has_reasonable_length = len(line) >= 2
        
        return is_short and has_reasonable_length and (starts_with_capital or has_all_caps)
    
    def _is_navigation_or_metadata(self, line: str) -> bool:
        """Check if a line is navigation or metadata."""
        navigation_patterns = [
            r'^\d+ days? ago$',
            r'~\d+ minute read',
            r'^Follow',
            r'^Not yet followed',
            r'^Updated$',
            r'^AS\d+$',
            r'^[A-Z] - [A-Z] - [A-Z]',  # Letter navigation
            r'^A$',
            r'^B$',
            r'^[A-Z]$'  # Single letters
        ]
        
        return any(re.match(pattern, line.strip()) for pattern in navigation_patterns)

    def get_driver_installation_help(self, browser_type: str) -> str:
        """Provide helpful instructions for installing WebDriver."""
        if browser_type.lower() == "chrome":
            return """
Chrome WebDriver not found. Please install ChromeDriver:
1. Download from: https://chromedriver.chromium.org/downloads
2. Make sure version matches your Chrome browser
3. Add to PATH or place in current directory
4. Alternative: Install via pip: pip install chromedriver-autoinstaller
"""
        elif browser_type.lower() == "edge":
            return """
Edge WebDriver not found. Please install Edge WebDriver:
1. Download from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
2. Make sure version matches your Edge browser
3. Add to PATH or place in current directory
4. Alternative: Install via pip: pip install msedge-selenium-tools
"""
        else:
            return "Please install either ChromeDriver or Edge WebDriver for browser automation."

    async def read_full_forum_post(self, email: str, password: str, post_url_or_id: str, 
                                 headless: bool = False, include_comments: bool = True) -> Dict[str, Any]:
        """Read a complete forum post with optional comments."""
        driver = None
        try:
            log("Starting forum post reading process", "INFO")
            
            # Determine if input is URL or article ID
            is_url = post_url_or_id.startswith('http')
            if is_url:
                post_url = post_url_or_id
            else:
                post_url = f"https://support.worldquantbrain.com/hc/zh-cn/community/posts/{post_url_or_id}"
            
            log(f"Target URL: {post_url}", "INFO")
            log(f"Include comments: {include_comments}", "INFO")
            
            driver = await self.create_driver(headless)
            
            # Login
            if not await self.login_to_forum(driver, email, password):
                raise Exception("Failed to login to forum")
            
            # Navigate directly to post URL
            log(f"Opening post: {post_url}", "WORK")
            driver.get(post_url)
            log("Post page loaded, extracting content immediately", "WORK")
            
            # Wait minimal time for content to appear
            await asyncio.sleep(2)
            
            # Extract post content quickly
            post_data = {}
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract post title
            title = soup.select_one('.post-title, h1, .article-title')
            if not title:
                title = soup.select_one('title')
            post_data['title'] = title.get_text().strip() if title else 'Unknown Title'
            
            # Extract post author
            author = soup.select_one('.post-author, .author, .article-author')
            if not author:
                author = soup.select_one('.comment-author')
            post_data['author'] = author.get_text().strip() if author else 'Unknown Author'
            
            # Extract post date
            date = soup.select_one('.post-date, .date, .article-date, time')
            if not date:
                time_element = soup.select_one('time')
                if time_element:
                    date = time_element.get('datetime') or time_element.get('title') or time_element.get_text().strip()
                else:
                    date = 'Unknown Date'
            else:
                date = date.get_text().strip()
            post_data['date'] = date if date else 'Unknown Date'
            
            # Extract post content
            post_content = soup.select_one('.post-body, .article-body, .content, .post-content')
            if not post_content:
                post_content = soup.select_one('article, main')
            
            if post_content:
                post_data['content_html'] = str(post_content)
                post_data['content_text'] = post_content.get_text().strip()
            else:
                post_data['content_html'] = 'No content found'
                post_data['content_text'] = 'No content found'
            
            post_data['url'] = post_url
            post_data['current_url'] = driver.current_url
            
            log(f"Post content extracted: \"{post_data['title']}\"", "SUCCESS")
            
            comments = []
            total_comments = 0
            
            # Extract comments conditionally
            if include_comments:
                log("Extracting comments...", "WORK")
                comments = await self._extract_forum_comments_full(driver, soup)
                total_comments = len(comments)
                log(f"Extracted {total_comments} comments", "SUCCESS")
            else:
                log("Skipping comment extraction (includeComments=false)", "INFO")
            
            return {
                "success": True,
                "post": post_data,
                "comments": comments,
                "total_comments": total_comments,
                "extracted_at": datetime.now().isoformat(),
                "processing_time": "full_extraction_with_comments" if include_comments else "post_only_extraction",
                "include_comments": include_comments
            }
            
        except Exception as e:
            log(f"Failed to read forum post: {str(e)}", "ERROR")
            return {"error": str(e)}
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    async def _extract_forum_comments_full(self, driver, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all comments from forum post with pagination support."""
        all_comments = []
        page_num = 1
        
        try:
            # First extract comments from current page source
            page_comments = self._parse_comments_from_html(soup)
            all_comments.extend(page_comments)
            log(f"Found {len(page_comments)} comments on page {page_num}", "INFO")
            
            # Check for pagination and continue if needed
            while True:
                try:
                    # Look for next page button
                    next_button = driver.find_element(By.CSS_SELECTOR, "span.pagination-next-text, .pagination-next, .next")
                    next_text = next_button.text
                    
                    if "下一页" in next_text or "Next" in next_text or "next" in next_text.lower():
                        log(f"Found next page, continuing to page {page_num + 1}", "INFO")
                        next_button.click()
                        await asyncio.sleep(2)  # Minimal wait for next page
                        
                        # Extract comments from new page
                        new_page_source = driver.page_source
                        new_soup = BeautifulSoup(new_page_source, 'html.parser')
                        new_page_comments = self._parse_comments_from_html(new_soup)
                        
                        if len(new_page_comments) == 0:
                            break
                        
                        all_comments.extend(new_page_comments)
                        page_num += 1
                        log(f"Found {len(new_page_comments)} comments on page {page_num}", "INFO")
                    else:
                        break
                except Exception as e:
                    log("No more pages found", "INFO")
                    break
            
            return all_comments
            
        except Exception as e:
            log(f"Error in comment extraction: {str(e)}", "WARNING")
            return all_comments

    def _parse_comments_from_html(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse comments from HTML using BeautifulSoup."""
        comments = []
        
        # Try multiple selectors for comments
        comment_selectors = [
            'ul#comments.comment-list li.comment',
            '.comment-list .comment',
            '.comments .comment',
            'li.comment',
            '.comment-item'
        ]
        
        comment_elements = None
        
        for selector in comment_selectors:
            comment_elements = soup.select(selector)
            if comment_elements:
                log(f"Found comments using selector: {selector}", "INFO")
                break
        
        if not comment_elements:
            log("No comments found on this page", "INFO")
            return comments
        
        for index, element in enumerate(comment_elements):
            try:
                comment = {}
                
                # Extract comment ID
                comment['id'] = element.get('id') or f"comment-{index}"
                
                # Extract author
                author_element = element.select_one('.comment-author a, .author a, .comment-author')
                comment['author'] = author_element.get_text().strip() if author_element else 'Unknown Author'
                comment['author_link'] = author_element.get('href') if author_element else ''
                
                # Extract date
                time_element = element.select_one('.meta-data time, time, .date, .comment-date')
                if time_element:
                    comment['date'] = time_element.get('datetime') or time_element.get('title') or time_element.get_text().strip()
                    comment['date_display'] = time_element.get('title') or time_element.get_text().strip()
                else:
                    comment['date'] = 'Unknown Date'
                    comment['date_display'] = 'Unknown Date'
                
                # Extract content
                content_element = element.select_one('.comment-body, .comment-content, .content')
                if content_element:
                    comment['content_html'] = str(content_element)
                    comment['content_text'] = content_element.get_text().strip()
                else:
                    comment['content_html'] = ''
                    comment['content_text'] = ''
                
                # Extract votes
                vote_element = element.select_one('.vote-up span, .votes, .vote-count')
                comment['votes'] = vote_element.get_text().strip() if vote_element else '0'
                
                # Extract status
                status_element = element.select_one('.status-label, .status, .badge')
                comment['status'] = status_element.get_text().strip() if status_element else '普通评论'
                
                if comment['content_text']:
                    comments.append(comment)
                
            except Exception as e:
                log(f"Error parsing comment {index}: {str(e)}", "WARNING")
        
        return comments

    async def search_forum_posts(self, email: str, password: str, search_query: str, 
                               max_results: int = 50, headless: bool = True) -> Dict[str, Any]:
        """Search forum posts."""
        driver = None
        try:
            log("Starting forum search process", "INFO")
            log(f"Search query: '{search_query}'", "INFO")
            log(f"Max results: {max_results}", "INFO")
            
            driver = await self.create_driver(headless)
            
            # Login
            if not await self.login_to_forum(driver, email, password):
                raise Exception("Failed to login to forum")
            
            # Navigate to search
            encoded_query = requests.utils.quote(search_query)
            search_url = f"https://support.worldquantbrain.com/hc/zh-cn/search?utf8=%E2%9C%93&query={encoded_query}"
            log(f"Opening search URL: {search_url}", "WORK")
            
            driver.get(search_url)
            await asyncio.sleep(2)
            
            # Collect results with pagination
            all_results = []
            page_num = 1
            
            log("Starting result collection with pagination", "WORK")
            
            while len(all_results) < max_results:
                log(f"Processing page {page_num}", "INFO")
                
                # Wait for search results
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.search-results-list, .search-result-list-item'))
                    )
                except TimeoutException:
                    log(f"No search results found on page {page_num}", "WARNING")
                    break
                
                # Extract results from current page
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                page_results = self._extract_search_results(soup, page_num)
                
                if not page_results:
                    log(f"No more results found on page {page_num}", "INFO")
                    break
                
                all_results.extend(page_results)
                
                # Check if we have enough results
                if len(all_results) >= max_results:
                    all_results = all_results[:max_results]
                    break
                
                # Try to go to next page
                if not await self._go_to_next_search_page(driver, soup):
                    log("No more pages available", "INFO")
                    break
                
                page_num += 1
                await asyncio.sleep(1)
            
            # Analyze results
            analysis = self._analyze_search_results(all_results, search_query)
            
            log(f"Search completed. Found {len(all_results)} results", "SUCCESS")
            return {
                "results": all_results,
                "total_found": len(all_results),
                "search_query": search_query,
                "analysis": analysis,
                "search_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            log(f"Search failed: {str(e)}", "ERROR")
            return {"error": str(e)}
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def _extract_search_results(self, soup: BeautifulSoup, page_num: int) -> List[Dict[str, Any]]:
        """Extract search results from a page."""
        results = []
        
        # Look for search result items
        result_items = soup.find_all(['article', 'div'], class_=re.compile(r'search-result|article-item'))
        
        for item in result_items:
            try:
                # Extract title
                title_elem = item.find(['h1', 'h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|heading'))
                title = title_elem.get_text().strip() if title_elem else "No title"
                
                # Extract link
                link_elem = item.find('a', href=True)
                link = link_elem['href'] if link_elem else ""
                if link and not link.startswith('http'):
                    link = f"https://support.worldquantbrain.com{link}"
                
                # Extract snippet
                snippet_elem = item.find(['p', 'div'], class_=re.compile(r'snippet|excerpt|summary'))
                snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                
                # Extract metadata
                meta_elem = item.find(['span', 'div'], class_=re.compile(r'meta|date|author'))
                metadata = meta_elem.get_text().strip() if meta_elem else ""
                
                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet,
                    "metadata": metadata,
                    "page": page_num
                })
                
            except Exception as e:
                log(f"Error extracting result: {str(e)}", "WARNING")
                continue
        
        return results
    
    async def _go_to_next_search_page(self, driver: webdriver.Chrome, soup: BeautifulSoup) -> bool:
        """Navigate to the next search page."""
        try:
            # Look for next page link
            next_link = soup.find('a', string=re.compile(r'next|下一页', re.IGNORECASE))
            if not next_link:
                next_link = soup.find('a', {'rel': 'next'})
            
            if next_link and next_link.get('href'):
                next_url = next_link['href']
                if not next_url.startswith('http'):
                    next_url = f"https://support.worldquantbrain.com{next_url}"
                
                driver.get(next_url)
                await asyncio.sleep(2)
                return True
            
            return False
            
        except Exception as e:
            log(f"Error navigating to next page: {str(e)}", "WARNING")
            return False
    
    def _analyze_search_results(self, results: List[Dict[str, Any]], search_query: str) -> Dict[str, Any]:
        """Analyze search results for insights."""
        if not results:
            return {"message": "No results found"}
        
        # Basic statistics
        total_results = len(results)
        
        # Categorize results by type
        categories = {}
        for result in results:
            title = result.get('title', '').lower()
            if 'tutorial' in title or 'guide' in title:
                categories['tutorials'] = categories.get('tutorials', 0) + 1
            elif 'api' in title or 'reference' in title:
                categories['api_docs'] = categories.get('api_docs', 0) + 1
            elif 'error' in title or 'issue' in title or 'problem' in title:
                categories['troubleshooting'] = categories.get('troubleshooting', 0) + 1
            elif 'competition' in title or 'event' in title:
                categories['competitions'] = categories.get('competitions', 0) + 1
            else:
                categories['general'] = categories.get('general', 0) + 1
        
        # Find most relevant results (containing search terms)
        search_terms = search_query.lower().split()
        relevant_results = []
        
        for result in results:
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            text = f"{title} {snippet}"
            
            term_matches = sum(1 for term in search_terms if term in text)
            if term_matches > 0:
                relevant_results.append({
                    "result": result,
                    "relevance_score": term_matches / len(search_terms)
                })
        
        # Sort by relevance
        relevant_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return {
            "total_results": total_results,
            "categories": categories,
            "most_relevant": relevant_results[:5] if relevant_results else [],
            "search_terms": search_terms
        }

# Initialize forum client
forum_client = ForumClient()

# MCP Tools for Forum Functions
if forum_mcp:
    @forum_mcp.tool()
    async def get_glossary_terms(email: str, password: str, headless: bool = False) -> Dict[str, Any]:
        """
        📚 Extract glossary terms from WorldQuant BRAIN forum.
        
        Args:
            email: Your BRAIN platform email address
            password: Your BRAIN platform password
            headless: Run browser in headless mode (default: False)
        
        Returns:
            Glossary terms with definitions
        """
        try:
            return await forum_client.get_glossary_terms(email, password, headless)
        except Exception as e:
            return {"error": str(e)}

    @forum_mcp.tool()
    async def search_forum_posts(email: str, password: str, search_query: str, 
                               max_results: int = 50, headless: bool = True) -> Dict[str, Any]:
        """
        🔍 Search forum posts on WorldQuant BRAIN support site.
        
        Args:
            email: Your BRAIN platform email address
            password: Your BRAIN platform password
            search_query: Search term or phrase
            max_results: Maximum number of results to return (default: 50)
            headless: Run browser in headless mode (default: True)
        
        Returns:
            Search results with analysis
        """
        try:
            return await forum_client.search_forum_posts(email, password, search_query, max_results, headless)
        except Exception as e:
            return {"error": str(e)}

    @forum_mcp.tool()
    async def read_full_forum_post(email: str, password: str, post_url_or_id: str, 
                                  headless: bool = False, include_comments: bool = True) -> Dict[str, Any]:
        """
        📖 Read a full forum post with optional comments.
        
        Args:
            email: Your BRAIN platform email address
            password: Your BRAIN platform password
            post_url_or_id: URL or ID of the post to read
            headless: Run browser in headless mode (default: False)
            include_comments: Include comments in the result (default: True)
        
        Returns:
            Complete forum post with all content
        """
        try:
            return await forum_client.read_full_forum_post(email, password, post_url_or_id, headless, include_comments)
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    print("📚 WorldQuant BRAIN Forum Functions Server Starting...", file=sys.stderr)
    if forum_mcp:
        forum_mcp.run()
    else:
        print("FastMCP is not available. Please install it to run the server.", file=sys.stderr) 