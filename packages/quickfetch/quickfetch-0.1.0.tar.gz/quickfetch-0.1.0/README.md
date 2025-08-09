# 🚀 quickfetch - Quick Fetch

**Fast, simple, and beautifully minimal web scraping.**

[![PyPI version](https://badge.fury.io/py/quickfetch.svg)](https://badge.fury.io/py/quickfetch)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ The Problem

Python developers who need to grab HTML or JSON from the web must currently:

1. Import `requests` to fetch content
2. Import `BeautifulSoup` or `lxml` to parse HTML  
3. Write **6–10 lines** of boilerplate code just to get basic data

This is slow, repetitive, and messy for quick scripts.

## 🎯 The Solution

**quickfetch** makes web scraping a **1–2 line task** with auto-detection of HTML/JSON content.

## 🚀 Quick Start

### Installation

```bash
pip install quickfetch
```

### Basic Usage

```python
from quickfetch import get

# Fetch a webpage
page = get("https://example.com")
print(page.select("h1").text)  # Get first h1 text
print(page.links)              # Get all links
print(page.images)             # Get all images

# Fetch JSON API
data = get("https://api.github.com/users/octocat")
print(data.json["name"])       # Access JSON data directly
```

## 🎨 Features

### Core Features

- **`get(url)`** → Returns a response object with:
  - `.html` → Raw HTML content (if HTML response)
  - `.json` → Parsed JSON data (if JSON response)
  - `.select(css_selector)` → CSS selector matching
  - `.xpath(xpath_expr)` → XPath expression matching
  - `.links` → All hyperlinks on the page
  - `.images` → All image URLs on the page

### Auto-Detection

quickfetch automatically detects if the response is HTML or JSON:

```python
# HTML page
page = get("https://example.com")
print(page.html)    # Raw HTML
print(page.json)    # None

# JSON API
data = get("https://api.github.com/users/octocat")
print(data.html)    # None
print(data.json)    # Parsed JSON dict
```

### CSS Selectors

```python
page = get("https://example.com")

# Get first element
title = page.select("h1")[0].text

# Get all elements
links = page.select("a[href]")
for link in links:
    print(link.text, link["href"])

# Nested selection
articles = page.select("article")
for article in articles:
    title = article.select("h2")[0].text
    content = article.select("p")[0].text
```

### XPath Support

```python
page = get("https://example.com")

# XPath expressions
elements = page.xpath("//h1[@class='title']")
for elem in elements:
    print(elem.text)
```

### Link & Image Extraction

```python
page = get("https://example.com")

# Get all links
all_links = page.links
print(f"Found {len(all_links)} links")

# Get all images
all_images = page.images
print(f"Found {len(all_images)} images")
```

### Element Properties

```python
page = get("https://example.com")
element = page.select("a")[0]

print(element.text)     # Text content
print(element.html)     # HTML content
print(element.attrs)    # All attributes
print(element["href"])  # Specific attribute
```

## 📚 Examples

### Scraping News Headlines

```python
from quickfetch import get

# Get headlines from a news site
page = get("https://news.ycombinator.com")
headlines = page.select(".titleline > a")

for headline in headlines[:5]:
    print(f"• {headline.text}")
    print(f"  {headline['href']}\n")
```

### API Data Extraction

```python
from quickfetch import get

# Get GitHub user data
user = get("https://api.github.com/users/octocat")
data = user.json

print(f"Name: {data['name']}")
print(f"Location: {data['location']}")
print(f"Followers: {data['followers']}")
```

### Image Gallery Scraper

```python
from quickfetch import get

# Get all images from a gallery
page = get("https://example.com/gallery")
images = page.images

print("Found images:")
for img_url in images:
    print(f"  {img_url}")
```

### Form Data Extraction

```python
from quickfetch import get

# Get form fields
page = get("https://example.com/contact")
forms = page.select("form")

for form in forms:
    inputs = form.select("input")
    for input_elem in inputs:
        name = input_elem.get("name", "")
        type_attr = input_elem.get("type", "text")
        print(f"Input: {name} ({type_attr})")
```

## 🔧 Advanced Usage

### Custom Headers

```python
from quickfetch import get

# Add custom headers
page = get("https://api.example.com", 
           headers={"User-Agent": "MyBot/1.0"})
```

### Error Handling

```python
from quickfetch import get

try:
    page = get("https://example.com")
    if page.html:
        print("Successfully fetched HTML")
    elif page.json:
        print("Successfully fetched JSON")
    else:
        print("No content found")
except Exception as e:
    print(f"Error: {e}")
```

### Batch Processing

```python
from quickfetch import get

urls = [
    "https://example1.com",
    "https://example2.com", 
    "https://example3.com"
]

for url in urls:
    page = get(url)
    title = page.select("title")[0].text if page.select("title") else "No title"
    print(f"{url}: {title}")
```

## 📦 Installation

### From PyPI

```bash
pip install quickfetch
```

### From Source

```bash
git clone https://github.com/quickfetch/quickfetch.git
cd quickfetch
pip install -e .
```

## 🛠 Dependencies

- **requests** ≥ 2.25.0 - HTTP library
- **selectolax** ≥ 0.3.0 - Fast HTML parser

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [requests](https://requests.readthedocs.io/) for HTTP
- Powered by [selectolax](https://selectolax.readthedocs.io/) for HTML parsing
- Inspired by the need for simpler web scraping workflows

---

**Made with ❤️ for Python developers who just want to get things done quickly.**
