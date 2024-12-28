import re
import time
import random
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin
import requests

def extract_links(soup, base_url):
    links = []
    nav = soup.find('nav', class_='md-nav--primary')
    if nav:
        for a in nav.find_all('a', class_='md-nav__link'):
            href = a.get('href')
            if href and not href.startswith(('#', 'javascript:')):
                full_url = urljoin(base_url, href)
                if full_url not in links:
                    links.append(full_url)
    return links

def fetch_content(session, url, max_retries=5, base_delay=1):
    for attempt in range(max_retries):
        try:
            response = session.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                print(f"Failed to fetch {url} after {max_retries} attempts")
    return None

def html_to_markdown(element):
    if isinstance(element, NavigableString):
        return str(element)
    elif element.name == 'code':
        return f'`{element.get_text()}`'
    elif element.name == 'pre':
        code = element.find('code')
        if code:
            return f'```\n{code.get_text()}\n```\n'
        return f'```\n{element.get_text()}\n```\n'
    elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        return f'{"#" * int(element.name[1])} {element.get_text()}\n\n'
    elif element.name == 'p':
        return f'{element.get_text()}\n\n'
    elif element.name == 'ul':
        return ''.join(f'- {html_to_markdown(li)}\n' for li in element.find_all('li', recursive=False))
    elif element.name == 'ol':
        return ''.join(f'{i+1}. {html_to_markdown(li)}\n' for i, li in enumerate(element.find_all('li', recursive=False)))
    elif element.name == 'li':
        return element.get_text()
    elif element.name == 'a':
        href = element.get('href', '')
        return f'[{element.get_text()}]({href})'
    elif element.name == 'br':
        return '\n'
    else:
        return ''.join(html_to_markdown(child) for child in element.children)

def process_content(content_div):
    output = ""
    for element in content_div.children:
        output += html_to_markdown(element)
    return output

def process_documentation(start_url):
    session = requests.Session()
    base_content = fetch_content(session, start_url)
    if not base_content:
        print(f"Failed to fetch content from {start_url}")
        return

    soup = BeautifulSoup(base_content, 'html.parser')
    links = extract_links(soup, start_url)
    
    output = "# Lmaobox Lua Documentation\n\n"
    
    for link in links:
        print(f"Fetching content from: {link}")
        content = fetch_content(session, link)
        if content:
            page_soup = BeautifulSoup(content, 'html.parser')
            content_div = page_soup.find('div', class_='md-content')
            if content_div:
                page_title = page_soup.find('h1')
                title = page_title.get_text() if page_title else link.split('/')[-1] or "Home"
                output += f"## {title}\n\n"
                output += process_content(content_div)
        time.sleep(2)  # Add a 2-second delay between requests
    
    try:
        with open('lmaobox_lua_documentation.md', 'w', encoding='utf-8') as f:
            f.write(output)
        print("Documentation has been extracted and saved to 'lmaobox_lua_documentation.md'")
    except IOError as e:
        print(f"Error writing to output file: {e}")

# Usage
start_url = "https://lmaobox.net/lua/"
process_documentation(start_url)
