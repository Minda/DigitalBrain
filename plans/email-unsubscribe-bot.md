# Email Unsubscribe Bot - Implementation Plan

**Created**: 2026-02-13
**Status**: Ready for review
**Goal**: Automate unsubscribing from marketing email lists with safety mechanisms and comprehensive tracking

---

## Executive Summary

This plan details a production-ready email unsubscribe bot that processes unsubscribe links from marketing emails. The bot integrates with the existing clothing email classifier system, handles various unsubscribe mechanisms (HTTP links, mailto links, preference centers), and includes extensive safety features to prevent unsubscribing from important emails.

**Key Design Principles**:
- Safety-first: Multiple validation layers before any unsubscribe action
- Privacy-first: All data stored in `personal/` directory (private repo)
- Incremental execution: Manual review checkpoints at each step
- Reversibility: Track all actions with ability to audit and rollback
- Integration: Leverages existing Gmail API and database infrastructure

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Email Unsubscribe Bot                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Extractor   │→│  Classifier   │→│   Executor      │   │
│  │   Component   │  │  Component    │  │   Component     │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
│         │                 │                    │            │
│         ↓                 ↓                    ↓            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              SQLite Database (personal/)              │  │
│  │  - unsubscribe_links                                  │  │
│  │  - unsubscribe_attempts                               │  │
│  │  - sender_whitelist                                   │  │
│  │  - unsubscribe_patterns                               │  │
│  └──────────────────────────────────────────────────────┘  │
│         ↑                 ↑                    ↑            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Gmail API (via MCP server)               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**1. Extractor Component** (`src/python/extract_unsubscribe_links.py`)
- Fetches emails from Gmail API
- Parses email headers for `List-Unsubscribe` and `List-Unsubscribe-Post`
- Extracts unsubscribe links from email body (HTML and plain text)
- Classifies link types (HTTP GET, HTTP POST, mailto, form-based)
- Stores extracted links in database

**2. Classifier Component** (`src/python/classify_unsubscribe_safety.py`)
- Validates sender against whitelist (never unsubscribe from these)
- Checks sender reputation (purchase history, important domain)
- Analyzes unsubscribe link legitimacy (phishing detection)
- Assigns safety score (0-100) to each unsubscribe candidate
- Flags high-risk unsubscribes for manual review

**3. Executor Component** (`src/python/execute_unsubscribe.py`)
- Handles HTTP GET unsubscribe requests
- Handles HTTP POST unsubscribe requests (RFC 8058 compliant)
- Handles mailto-based unsubscribes
- Handles form-based preference centers (interactive)
- Logs all attempts with success/failure status
- Implements rate limiting and retry logic

---

## Database Schema

### New Tables

All tables stored in: `personal/data/email-classifier/clothing_emails.db`

#### 1. `unsubscribe_links`
Stores all extracted unsubscribe links with metadata.

```sql
CREATE TABLE IF NOT EXISTS unsubscribe_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id TEXT NOT NULL,
    sender_email TEXT NOT NULL,
    sender_name TEXT,
    subject TEXT,
    link_url TEXT NOT NULL,
    link_type TEXT NOT NULL CHECK(link_type IN (
        'http_get',           -- Simple HTTP GET link
        'http_post',          -- RFC 8058 POST request
        'mailto',             -- Email-based unsubscribe
        'form',               -- Preference center form
        'one_click',          -- RFC 8058 one-click
        'unknown'
    )),
    header_source TEXT CHECK(header_source IN (
        'list_unsubscribe',   -- From List-Unsubscribe header
        'body_html',          -- Extracted from HTML body
        'body_text',          -- Extracted from plain text
        'list_unsubscribe_post' -- From List-Unsubscribe-Post header
    )),
    safety_score INTEGER CHECK(safety_score >= 0 AND safety_score <= 100),
    safety_flags TEXT,        -- JSON array of safety concerns
    is_whitelisted BOOLEAN DEFAULT FALSE,
    status TEXT DEFAULT 'pending' CHECK(status IN (
        'pending',            -- Not yet processed
        'approved',           -- Safe to unsubscribe
        'rejected',           -- Unsafe/important sender
        'processed',          -- Unsubscribe attempted
        'failed',             -- Unsubscribe failed
        'manual_review'       -- Needs human review
    )),
    extracted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed_at DATETIME,
    processed_at DATETIME,
    FOREIGN KEY (email_id) REFERENCES classifications(email_id),
    UNIQUE(email_id, link_url)  -- Prevent duplicate links
);
```

#### 2. `unsubscribe_attempts`
Logs every unsubscribe attempt with full details.

```sql
CREATE TABLE IF NOT EXISTS unsubscribe_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    link_id INTEGER NOT NULL,
    sender_email TEXT NOT NULL,
    link_url TEXT NOT NULL,
    link_type TEXT NOT NULL,
    method TEXT NOT NULL CHECK(method IN (
        'http_get',
        'http_post',
        'mailto',
        'form_submit',
        'manual'
    )),
    attempt_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    http_status_code INTEGER,
    response_headers TEXT,    -- JSON
    response_body TEXT,       -- Truncated to 1000 chars
    success BOOLEAN,
    error_message TEXT,
    confirmation_detected BOOLEAN DEFAULT FALSE,
    confirmation_text TEXT,
    user_agent TEXT,
    ip_address TEXT,          -- For audit trail
    session_id TEXT,          -- Group related attempts
    FOREIGN KEY (link_id) REFERENCES unsubscribe_links(id)
);
```

#### 3. `sender_whitelist`
Senders that should NEVER be unsubscribed from.

```sql
CREATE TABLE IF NOT EXISTS sender_whitelist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_email TEXT UNIQUE NOT NULL,
    sender_domain TEXT,
    reason TEXT NOT NULL CHECK(reason IN (
        'purchase_history',   -- User has bought from them
        'important_service',  -- Bank, utility, etc.
        'manual_add',         -- User explicitly added
        'high_engagement'     -- User frequently opens/replies
    )),
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    added_by TEXT,            -- 'system' or 'user'
    notes TEXT
);
```

#### 4. `unsubscribe_patterns`
Learned patterns for identifying unsubscribe links.

```sql
CREATE TABLE IF NOT EXISTS unsubscribe_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT NOT NULL CHECK(pattern_type IN (
        'url_regex',          -- URL pattern matching
        'text_pattern',       -- Link text pattern
        'domain_pattern',     -- Specific domain patterns
        'header_format'       -- Header value format
    )),
    pattern TEXT NOT NULL,
    description TEXT,
    success_rate REAL,        -- How often this pattern works
    false_positive_rate REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used DATETIME,
    use_count INTEGER DEFAULT 0
);
```

#### 5. `unsubscribe_config`
Runtime configuration and feature flags.

```sql
CREATE TABLE IF NOT EXISTS unsubscribe_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    value_type TEXT CHECK(value_type IN ('string', 'integer', 'boolean', 'json')),
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Default config values
INSERT OR IGNORE INTO unsubscribe_config VALUES
    ('rate_limit_per_minute', '10', 'integer', 'Max unsubscribe attempts per minute', CURRENT_TIMESTAMP),
    ('rate_limit_per_hour', '50', 'integer', 'Max unsubscribe attempts per hour', CURRENT_TIMESTAMP),
    ('min_safety_score', '70', 'integer', 'Minimum safety score to auto-approve', CURRENT_TIMESTAMP),
    ('dry_run_mode', 'true', 'boolean', 'If true, log but do not execute', CURRENT_TIMESTAMP),
    ('require_confirmation', 'true', 'boolean', 'Require manual confirmation before executing', CURRENT_TIMESTAMP),
    ('user_agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', 'string', 'User agent for HTTP requests', CURRENT_TIMESTAMP),
    ('timeout_seconds', '10', 'integer', 'HTTP request timeout', CURRENT_TIMESTAMP),
    ('max_redirects', '5', 'integer', 'Max HTTP redirects to follow', CURRENT_TIMESTAMP);
```

#### 6. Updates to Existing Tables

```sql
-- Add unsubscribe tracking to marketing_emails table
ALTER TABLE marketing_emails ADD COLUMN unsubscribe_extracted BOOLEAN DEFAULT FALSE;
ALTER TABLE marketing_emails ADD COLUMN unsubscribe_attempted BOOLEAN DEFAULT FALSE;
ALTER TABLE marketing_emails ADD COLUMN unsubscribe_success BOOLEAN DEFAULT FALSE;
ALTER TABLE marketing_emails ADD COLUMN last_attempt_date DATETIME;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_unsubscribe_links_status ON unsubscribe_links(status);
CREATE INDEX IF NOT EXISTS idx_unsubscribe_links_sender ON unsubscribe_links(sender_email);
CREATE INDEX IF NOT EXISTS idx_unsubscribe_links_safety ON unsubscribe_links(safety_score);
CREATE INDEX IF NOT EXISTS idx_unsubscribe_attempts_success ON unsubscribe_attempts(success);
CREATE INDEX IF NOT EXISTS idx_whitelist_domain ON sender_whitelist(sender_domain);
```

---

## Gmail API Integration

### Required API Scopes

Already available from existing implementation:
- `https://www.googleapis.com/auth/gmail.modify` - Modify messages (trash after unsubscribe)
- `https://www.googleapis.com/auth/gmail.readonly` - Read message content

### API Usage Patterns

#### 1. Message Retrieval
```python
# Fetch message with full headers and body
message = get_message(service, message_id, format='full')
```

#### 2. Header Parsing
```python
headers = get_headers_dict(message)
list_unsubscribe = headers.get('List-Unsubscribe', '')
list_unsubscribe_post = headers.get('List-Unsubscribe-Post', '')
```

#### 3. Body Parsing
```python
# Extract both HTML and plain text parts
html_body = parse_message_body_html(message)
text_body = parse_message_body(message)  # Existing function
```

#### 4. Rate Limiting Strategy

Gmail API quotas:
- **250 quota units per user per second**
- **1 quota unit** per `messages.get()` call
- **5 quota units** per `messages.modify()` call

Implementation:
```python
import time
from collections import deque

class GmailRateLimiter:
    def __init__(self, max_per_second=200):  # Conservative limit
        self.max_per_second = max_per_second
        self.requests = deque()

    def acquire(self):
        now = time.time()
        # Remove requests older than 1 second
        while self.requests and self.requests[0] < now - 1:
            self.requests.popleft()

        if len(self.requests) >= self.max_per_second:
            sleep_time = 1 - (now - self.requests[0])
            time.sleep(sleep_time)

        self.requests.append(time.time())
```

---

## Unsubscribe Mechanism Handlers

### 1. HTTP GET Handler (Simple Links)

**Pattern**: `https://unsubscribe.example.com/remove?email=user@example.com`

**Implementation**:
```python
import requests
from urllib.parse import urlparse

def handle_http_get_unsubscribe(link_url, timeout=10):
    """
    Execute HTTP GET unsubscribe request.

    Returns:
        dict: {
            'success': bool,
            'status_code': int,
            'confirmation_detected': bool,
            'response_preview': str
        }
    """
    try:
        # Validate URL
        parsed = urlparse(link_url)
        if parsed.scheme not in ['http', 'https']:
            return {'success': False, 'error': 'Invalid scheme'}

        headers = {
            'User-Agent': get_config('user_agent'),
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        response = requests.get(
            link_url,
            headers=headers,
            timeout=timeout,
            allow_redirects=True,
            max_redirects=5
        )

        # Check for success indicators
        confirmation_keywords = [
            'unsubscribed',
            'removed from list',
            'successfully unsubscribed',
            'preference updated',
            'subscription cancelled'
        ]

        response_text = response.text.lower()
        confirmation_detected = any(
            keyword in response_text
            for keyword in confirmation_keywords
        )

        return {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'confirmation_detected': confirmation_detected,
            'response_preview': response.text[:500],
            'final_url': response.url,
            'redirects': len(response.history)
        }

    except requests.Timeout:
        return {'success': False, 'error': 'Timeout'}
    except requests.RequestException as e:
        return {'success': False, 'error': str(e)}
```

### 2. HTTP POST Handler (RFC 8058 One-Click)

**Pattern**: List-Unsubscribe-Post header present

**RFC 8058 Spec**:
```
List-Unsubscribe: <https://example.com/unsubscribe/opaquepart>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

**Implementation**:
```python
def handle_http_post_unsubscribe(link_url, post_data='List-Unsubscribe=One-Click'):
    """
    Execute RFC 8058 compliant POST unsubscribe.
    """
    try:
        headers = {
            'User-Agent': get_config('user_agent'),
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = requests.post(
            link_url,
            data=post_data,
            headers=headers,
            timeout=10,
            allow_redirects=False  # RFC 8058: should not redirect
        )

        # RFC 8058: Success is 2xx status
        success = 200 <= response.status_code < 300

        return {
            'success': success,
            'status_code': response.status_code,
            'confirmation_detected': success,
            'response_preview': response.text[:500]
        }

    except requests.RequestException as e:
        return {'success': False, 'error': str(e)}
```

### 3. Mailto Handler (Email-based Unsubscribe)

**Pattern**: `mailto:unsubscribe@example.com?subject=unsubscribe`

**Implementation**:
```python
from email.mime.text import MIMEText
from urllib.parse import urlparse, parse_qs

def handle_mailto_unsubscribe(mailto_url, gmail_service, user_email):
    """
    Send unsubscribe email via Gmail API.
    """
    try:
        # Parse mailto URL
        parsed = urlparse(mailto_url)
        if parsed.scheme != 'mailto':
            return {'success': False, 'error': 'Not a mailto URL'}

        to_address = parsed.path

        # Parse query parameters
        params = parse_qs(parsed.query)
        subject = params.get('subject', ['Unsubscribe'])[0]
        body = params.get('body', ['Please unsubscribe me.'])[0]

        # Create email message
        message = create_message(
            sender=user_email,
            to=to_address,
            subject=subject,
            message_text=body
        )

        # Send via Gmail API
        result = send_email(gmail_service, message)

        return {
            'success': True,
            'message_id': result['id'],
            'to': to_address,
            'subject': subject
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}
```

### 4. Form Handler (Preference Centers)

**Pattern**: Link leads to a page with form fields

**Implementation**:
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

def handle_form_unsubscribe(link_url, email_address, headless=True):
    """
    Handle form-based unsubscribe (requires Selenium).

    This is the most complex case and may require manual intervention.
    """
    # Note: This requires Selenium which adds complexity
    # Recommended approach: Flag for manual review instead

    return {
        'success': False,
        'requires_manual': True,
        'reason': 'Form-based unsubscribe requires manual interaction',
        'link': link_url
    }
```

### 5. Link Detection Patterns

**From HTML Body**:
```python
import re
from bs4 import BeautifulSoup

def extract_unsubscribe_links_from_html(html_content):
    """Extract unsubscribe links from HTML email body."""
    soup = BeautifulSoup(html_content, 'html.parser')
    links = []

    # Pattern 1: Links with "unsubscribe" in text
    for a_tag in soup.find_all('a', href=True):
        text = a_tag.get_text().lower()
        href = a_tag['href']

        if any(keyword in text for keyword in [
            'unsubscribe',
            'opt out',
            'remove me',
            'manage preferences',
            'email preferences'
        ]):
            links.append({
                'url': href,
                'text': a_tag.get_text().strip(),
                'source': 'body_html'
            })

    # Pattern 2: Links with unsubscribe in URL
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href'].lower()
        if any(keyword in href for keyword in [
            'unsubscribe',
            'optout',
            'remove',
            'preferences'
        ]):
            if not any(l['url'] == a_tag['href'] for l in links):
                links.append({
                    'url': a_tag['href'],
                    'text': a_tag.get_text().strip(),
                    'source': 'body_html'
                })

    return links
```

**From Plain Text Body**:
```python
def extract_unsubscribe_links_from_text(text_content):
    """Extract unsubscribe links from plain text email body."""
    # Match URLs
    url_pattern = r'https?://[^\s<>"]+'
    urls = re.findall(url_pattern, text_content)

    links = []
    for url in urls:
        if any(keyword in url.lower() for keyword in [
            'unsubscribe',
            'optout',
            'remove',
            'preferences'
        ]):
            links.append({
                'url': url,
                'text': '',
                'source': 'body_text'
            })

    return links
```

---

## Safety Mechanisms

### 1. Sender Whitelist Auto-Population

Automatically whitelist senders based on:

```python
def auto_populate_whitelist(db_path):
    """
    Automatically add senders to whitelist based on criteria.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Criterion 1: Senders with purchase history
    cursor.execute("""
        INSERT OR IGNORE INTO sender_whitelist (sender_email, sender_domain, reason, added_by)
        SELECT DISTINCT sender,
               substr(sender, instr(sender, '@') + 1),
               'purchase_history',
               'system'
        FROM classifications
        WHERE category = 'purchase'
    """)

    # Criterion 2: Important service domains
    important_domains = [
        'bank', 'credit', 'amazon.com', 'paypal.com',
        'apple.com', 'google.com', 'microsoft.com',
        '.gov', '.edu', 'irs.gov', 'healthcare'
    ]

    for domain_pattern in important_domains:
        cursor.execute("""
            INSERT OR IGNORE INTO sender_whitelist (sender_email, sender_domain, reason, added_by)
            SELECT DISTINCT sender,
                   substr(sender, instr(sender, '@') + 1),
                   'important_service',
                   'system'
            FROM classifications
            WHERE sender LIKE ?
        """, (f'%{domain_pattern}%',))

    conn.commit()
    conn.close()
```

### 2. Safety Score Calculation

```python
def calculate_safety_score(sender_email, link_url, db_path):
    """
    Calculate safety score (0-100) for unsubscribe link.
    Higher score = safer to unsubscribe

    Returns:
        dict: {
            'score': int,
            'flags': List[str],
            'recommendation': str
        }
    """
    score = 50  # Start neutral
    flags = []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check 1: Is sender whitelisted? (BLOCK)
    cursor.execute(
        "SELECT 1 FROM sender_whitelist WHERE sender_email = ?",
        (sender_email,)
    )
    if cursor.fetchone():
        score = 0
        flags.append('whitelisted_sender')
        return {'score': 0, 'flags': flags, 'recommendation': 'NEVER_UNSUBSCRIBE'}

    # Check 2: Has purchase history? (Caution)
    cursor.execute(
        "SELECT COUNT(*) FROM classifications WHERE sender = ? AND category = 'purchase'",
        (sender_email,)
    )
    purchase_count = cursor.fetchone()[0]
    if purchase_count > 0:
        score -= 30
        flags.append(f'purchase_history_{purchase_count}')

    # Check 3: Link legitimacy
    parsed_link = urlparse(link_url)
    parsed_sender = sender_email.split('@')[-1]

    # Good sign: Link domain matches sender domain
    if parsed_sender in parsed_link.netloc:
        score += 20
    else:
        score -= 10
        flags.append('domain_mismatch')

    # Check 4: Link uses HTTPS (good)
    if parsed_link.scheme == 'https':
        score += 10
    else:
        score -= 5
        flags.append('http_not_https')

    # Check 5: Suspicious patterns in URL
    suspicious_patterns = [
        'bit.ly', 'tinyurl', 'goo.gl',  # URL shorteners (could hide destination)
        'login', 'signin', 'verify',      # Phishing keywords
        '..', '//', '%2e%2e'              # Path traversal attempts
    ]
    if any(pattern in link_url.lower() for pattern in suspicious_patterns):
        score -= 20
        flags.append('suspicious_url_pattern')

    # Check 6: From List-Unsubscribe header (reliable)
    cursor.execute(
        "SELECT header_source FROM unsubscribe_links WHERE link_url = ?",
        (link_url,)
    )
    result = cursor.fetchone()
    if result and result[0] == 'list_unsubscribe':
        score += 15

    # Check 7: Sender has high email volume (likely marketing)
    cursor.execute(
        "SELECT COUNT(*) FROM classifications WHERE sender = ? AND category = 'marketing'",
        (sender_email,)
    )
    marketing_count = cursor.fetchone()[0]
    if marketing_count >= 10:
        score += 10

    conn.close()

    # Clamp score to 0-100
    score = max(0, min(100, score))

    # Recommendation
    if score >= 70:
        recommendation = 'SAFE'
    elif score >= 40:
        recommendation = 'MANUAL_REVIEW'
    else:
        recommendation = 'REJECT'

    return {
        'score': score,
        'flags': flags,
        'recommendation': recommendation
    }
```

### 3. Phishing Detection

```python
def detect_phishing(link_url, sender_email, subject):
    """
    Detect potential phishing attempts.
    """
    risk_indicators = []

    # Indicator 1: Generic sender but claims to be major brand
    major_brands = ['amazon', 'paypal', 'apple', 'microsoft', 'google']
    sender_lower = sender_email.lower()

    for brand in major_brands:
        if brand in subject.lower() and brand not in sender_lower:
            risk_indicators.append(f'brand_impersonation_{brand}')

    # Indicator 2: IP address in URL
    if re.search(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', link_url):
        risk_indicators.append('ip_address_url')

    # Indicator 3: Excessive subdomains
    parsed = urlparse(link_url)
    subdomain_count = parsed.netloc.count('.')
    if subdomain_count > 3:
        risk_indicators.append('excessive_subdomains')

    # Indicator 4: Homograph attack (lookalike domains)
    # e.g., "paypa1.com" instead of "paypal.com"
    homograph_chars = ['1', '0', 'rn', 'vv', 'l1']
    domain = urlparse(link_url).netloc
    if any(char in domain for char in homograph_chars):
        risk_indicators.append('potential_homograph')

    return risk_indicators
```

### 4. Confirmation Required for High-Risk Actions

```python
def requires_manual_confirmation(safety_score, flags):
    """
    Determine if manual confirmation is needed before unsubscribe.
    """
    # Always require confirmation if:
    if safety_score < 70:
        return True, "Safety score below threshold"

    if 'purchase_history' in ' '.join(flags):
        return True, "Sender has purchase history"

    if 'domain_mismatch' in flags:
        return True, "Unsubscribe domain doesn't match sender"

    if any('phishing' in flag or 'suspicious' in flag for flag in flags):
        return True, "Potential phishing detected"

    return False, "Safe to proceed"
```

---

## Error Handling & Edge Cases

### 1. Network Errors

```python
class UnsubscribeError(Exception):
    """Base exception for unsubscribe operations."""
    pass

class NetworkError(UnsubscribeError):
    """Network-related errors."""
    pass

class RateLimitError(UnsubscribeError):
    """Rate limit exceeded."""
    pass

class ValidationError(UnsubscribeError):
    """Link validation failed."""
    pass

def execute_with_retry(func, max_retries=3, backoff_factor=2):
    """
    Execute function with exponential backoff retry.
    """
    for attempt in range(max_retries):
        try:
            return func()
        except NetworkError as e:
            if attempt == max_retries - 1:
                raise
            sleep_time = backoff_factor ** attempt
            time.sleep(sleep_time)
        except RateLimitError as e:
            # Respect rate limit
            time.sleep(60)  # Wait 1 minute
            if attempt == max_retries - 1:
                raise

    raise UnsubscribeError(f"Failed after {max_retries} retries")
```

### 2. Invalid Links

```python
def validate_unsubscribe_link(link_url):
    """
    Validate unsubscribe link before attempting.
    """
    if not link_url:
        raise ValidationError("Empty link")

    # Check for common invalid patterns
    invalid_patterns = [
        'javascript:',
        'data:',
        'file://',
        'about:',
        '#',  # Fragment-only
    ]

    if any(link_url.startswith(pattern) for pattern in invalid_patterns):
        raise ValidationError(f"Invalid link scheme: {link_url}")

    # Validate URL structure
    try:
        parsed = urlparse(link_url)
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError("Malformed URL")
    except Exception as e:
        raise ValidationError(f"URL parsing failed: {e}")

    return True
```

### 3. Rate Limiting (External Services)

```python
class UnsubscribeRateLimiter:
    """
    Rate limiter for external unsubscribe requests.
    """
    def __init__(self, db_path):
        self.db_path = db_path

    def check_rate_limit(self):
        """
        Check if we're within rate limits.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get configured limits
        cursor.execute("SELECT value FROM unsubscribe_config WHERE key = ?", ('rate_limit_per_minute',))
        per_minute = int(cursor.fetchone()[0])

        cursor.execute("SELECT value FROM unsubscribe_config WHERE key = ?", ('rate_limit_per_hour',))
        per_hour = int(cursor.fetchone()[0])

        # Count recent attempts
        cursor.execute("""
            SELECT COUNT(*) FROM unsubscribe_attempts
            WHERE attempt_timestamp > datetime('now', '-1 minute')
        """)
        recent_minute = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM unsubscribe_attempts
            WHERE attempt_timestamp > datetime('now', '-1 hour')
        """)
        recent_hour = cursor.fetchone()[0]

        conn.close()

        if recent_minute >= per_minute:
            raise RateLimitError(f"Rate limit exceeded: {recent_minute}/{per_minute} per minute")

        if recent_hour >= per_hour:
            raise RateLimitError(f"Rate limit exceeded: {recent_hour}/{per_hour} per hour")

        return True
```

### 4. Malformed Email Headers

```python
def parse_list_unsubscribe_header(header_value):
    """
    Parse List-Unsubscribe header which can contain multiple URLs.

    Format: <mailto:unsub@example.com>, <https://example.com/unsub>
    """
    if not header_value:
        return []

    # Extract URLs within < > brackets
    urls = re.findall(r'<([^>]+)>', header_value)

    parsed_links = []
    for url in urls:
        url = url.strip()
        if url.startswith('http'):
            parsed_links.append({
                'url': url,
                'type': 'http_get',
                'source': 'list_unsubscribe'
            })
        elif url.startswith('mailto:'):
            parsed_links.append({
                'url': url,
                'type': 'mailto',
                'source': 'list_unsubscribe'
            })

    return parsed_links
```

### 5. Confirmation Email Monitoring

```python
def monitor_unsubscribe_confirmations(gmail_service, sender_email, days=3):
    """
    After unsubscribe attempt, monitor for confirmation emails.
    """
    query = f'from:{sender_email} after:{days}d (unsubscribe OR confirmed OR removed)'

    messages = list_messages(gmail_service, query=query, max_results=10)

    confirmations = []
    for msg_ref in messages:
        msg = get_message(gmail_service, msg_ref['id'])
        headers = get_headers_dict(msg)
        subject = headers.get('Subject', '').lower()

        confirmation_keywords = [
            'unsubscribed',
            'removed from list',
            'subscription cancelled',
            'preferences updated'
        ]

        if any(keyword in subject for keyword in confirmation_keywords):
            confirmations.append({
                'email_id': msg_ref['id'],
                'subject': subject,
                'received_date': headers.get('Date', '')
            })

    return confirmations
```

---

## Security & Privacy Considerations

### 1. Data Privacy

**All personal data stored in `personal/` directory**:
- Email content and metadata
- Unsubscribe links (may contain personal identifiers)
- Processing logs
- User preferences

**Never commit to public repo**:
- `personal/data/email-classifier/` is in `.gitignore`
- Database files never tracked in git
- Credentials stored in `app/mcp/gmail/` (also gitignored)

### 2. Credential Management

```python
# Existing pattern (already implemented)
credentials_path = Path("app/mcp/gmail/credentials.json")
token_path = Path("app/mcp/gmail/token.json")

# Both files in .gitignore
# Credentials never logged or exposed
```

### 3. URL Safety

Before making any HTTP request:
- Validate URL format
- Check against known malicious domains
- Use timeout to prevent hanging
- Limit redirects to prevent loops
- Log all requests for audit

### 4. Email Address Exposure

Some unsubscribe links contain email addresses:
- `https://example.com/unsub?email=user@example.com`

**Protection**:
- URLs stored in private database only
- Never log full URLs in console output
- Truncate URLs in error messages
- Use parameterized queries to prevent injection

### 5. Audit Trail

Every action logged:
```python
def log_unsubscribe_attempt(link_id, sender_email, link_url, result):
    """
    Create comprehensive audit trail.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO unsubscribe_attempts (
            link_id, sender_email, link_url, link_type, method,
            http_status_code, response_headers, response_body,
            success, error_message, user_agent, session_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        link_id,
        sender_email,
        link_url,  # Full URL for audit
        result.get('link_type'),
        result.get('method'),
        result.get('status_code'),
        json.dumps(result.get('headers', {})),
        result.get('body', '')[:1000],  # Truncate
        result.get('success'),
        result.get('error'),
        result.get('user_agent'),
        result.get('session_id')
    ))

    conn.commit()
    conn.close()
```

---

## Testing Strategy

### 1. Unit Tests

**File**: `tests/test_unsubscribe_bot.py`

```python
import unittest
from src.python.extract_unsubscribe_links import (
    parse_list_unsubscribe_header,
    extract_unsubscribe_links_from_html,
    extract_unsubscribe_links_from_text
)
from src.python.classify_unsubscribe_safety import (
    calculate_safety_score,
    detect_phishing
)

class TestLinkExtraction(unittest.TestCase):
    def test_parse_list_unsubscribe_header(self):
        header = '<mailto:unsub@example.com>, <https://example.com/unsub>'
        links = parse_list_unsubscribe_header(header)
        self.assertEqual(len(links), 2)
        self.assertEqual(links[0]['type'], 'mailto')
        self.assertEqual(links[1]['type'], 'http_get')

    def test_extract_from_html(self):
        html = '<a href="https://example.com/unsubscribe">Unsubscribe</a>'
        links = extract_unsubscribe_links_from_html(html)
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]['url'], 'https://example.com/unsubscribe')

    def test_phishing_detection(self):
        # Test IP address detection
        link = "http://192.168.1.1/unsubscribe"
        indicators = detect_phishing(link, "test@example.com", "Test")
        self.assertIn('ip_address_url', indicators)

        # Test brand impersonation
        indicators = detect_phishing(
            "http://evil.com/unsub",
            "noreply@evil.com",
            "Amazon Order Confirmation"
        )
        self.assertIn('brand_impersonation_amazon', indicators)

class TestSafetyScoring(unittest.TestCase):
    def test_whitelisted_sender(self):
        # Mock database with whitelisted sender
        result = calculate_safety_score(
            "billing@amazon.com",
            "https://amazon.com/unsub",
            ":memory:"
        )
        self.assertEqual(result['score'], 0)
        self.assertEqual(result['recommendation'], 'NEVER_UNSUBSCRIBE')

    def test_safe_marketing_email(self):
        result = calculate_safety_score(
            "marketing@newsletter.com",
            "https://newsletter.com/unsubscribe",
            ":memory:"
        )
        self.assertGreater(result['score'], 50)
```

### 2. Integration Tests

**File**: `tests/test_unsubscribe_integration.py`

```python
class TestGmailIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use test Gmail account with sample emails
        cls.service = get_gmail_service()

    def test_extract_from_real_email(self):
        # Use a known test email ID
        message = get_message(self.service, TEST_EMAIL_ID)
        links = extract_all_unsubscribe_links(message)
        self.assertGreater(len(links), 0)

    def test_rate_limiter(self):
        limiter = GmailRateLimiter(max_per_second=5)

        start = time.time()
        for i in range(10):
            limiter.acquire()
        duration = time.time() - start

        # Should take at least 1 second (10 requests at 5/sec)
        self.assertGreater(duration, 1.0)
```

### 3. End-to-End Tests

**Manual Test Plan**:

#### Phase 1: Link Extraction Test
1. Select 10 marketing emails manually
2. Run extraction script
3. Verify all unsubscribe links found
4. Check for false positives

#### Phase 2: Safety Classification Test
1. Test with whitelisted sender (should reject)
2. Test with known safe marketing email (should approve)
3. Test with suspicious link (should flag for review)

#### Phase 3: Dry Run Test
1. Enable `dry_run_mode` config
2. Run full unsubscribe flow
3. Verify no actual HTTP requests made
4. Check all logs created correctly

#### Phase 4: Live Test (Controlled)
1. Create test email list subscription
2. Send test marketing email to self
3. Run unsubscribe bot on test email
4. Verify unsubscribe successful
5. Confirm no more emails received

#### Phase 5: Monitoring Test
1. Execute 5 unsubscribes
2. Wait 3 days
3. Run confirmation monitor
4. Verify confirmation emails detected

### 4. Safety Tests

```python
class TestSafetyMechanisms(unittest.TestCase):
    def test_whitelist_protection(self):
        # Ensure whitelisted senders are never unsubscribed
        pass

    def test_rate_limit_enforcement(self):
        # Ensure rate limits are respected
        pass

    def test_dry_run_mode(self):
        # Ensure dry run doesn't make real requests
        pass

    def test_phishing_rejection(self):
        # Ensure phishing links are rejected
        pass
```

---

## Integration with Clothing Classifier

### Shared Infrastructure

Both systems use:
- Same SQLite database (`personal/data/email-classifier/clothing_emails.db`)
- Same Gmail API service instance
- Same authentication credentials
- Same data privacy principles

### Data Flow Integration

```
┌─────────────────────────────────────────────────────────┐
│              Clothing Email Classifier                   │
│  1. Fetches emails from Gmail                           │
│  2. Classifies as purchase/marketing/other              │
│  3. Stores in `classifications` table                   │
│  4. Stores marketing emails in `marketing_emails`       │
└────────────────────┬───────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│              Email Unsubscribe Bot                       │
│  1. Reads from `marketing_emails` table                 │
│  2. Extracts unsubscribe links                          │
│  3. Stores in `unsubscribe_links` table                 │
│  4. Calculates safety scores                            │
│  5. Executes approved unsubscribes                      │
│  6. Updates `marketing_emails.unsubscribe_success`      │
└─────────────────────────────────────────────────────────┘
```

### Shared Code Modules

Create shared utilities in `src/python/email_utils.py`:

```python
# Shared functions used by both systems
def get_gmail_service_instance():
    """Shared Gmail service initialization."""
    # Already exists in gmail_clothing_classifier.py
    # Move to shared module

def get_headers_dict(message):
    """Extract headers from message."""
    # Already exists in app/mcp/gmail/mcp_gmail/gmail.py

def get_db_connection():
    """Get connection to shared database."""
    db_path = Path("personal/data/email-classifier/clothing_emails.db")
    return sqlite3.connect(db_path)
```

### Unified Command-Line Interface

```python
# src/python/email_manager_cli.py

import argparse

def main():
    parser = argparse.ArgumentParser(description='Email Management Tools')
    subparsers = parser.add_subparsers(dest='command')

    # Clothing classifier commands
    classify_parser = subparsers.add_parser('classify', help='Classify clothing emails')
    classify_parser.add_argument('--sample-size', type=int, default=100)

    # Unsubscribe bot commands
    unsub_parser = subparsers.add_parser('unsubscribe', help='Manage unsubscribes')
    unsub_parser.add_argument('--extract', action='store_true', help='Extract links')
    unsub_parser.add_argument('--classify', action='store_true', help='Classify safety')
    unsub_parser.add_argument('--execute', action='store_true', help='Execute unsubscribes')
    unsub_parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    unsub_parser.add_argument('--sender', type=str, help='Target specific sender')

    # Shared commands
    stats_parser = subparsers.add_parser('stats', help='Show statistics')

    args = parser.parse_args()

    if args.command == 'classify':
        from gmail_clothing_classifier import main as classify_main
        classify_main()
    elif args.command == 'unsubscribe':
        from execute_unsubscribe import main as unsub_main
        unsub_main(args)
    elif args.command == 'stats':
        from email_stats import show_statistics
        show_statistics()

if __name__ == '__main__':
    main()
```

### Database Query Integration

```python
# Queries that leverage both systems

def get_unsubscribe_candidates():
    """
    Get marketing emails that are good unsubscribe candidates.

    Criteria:
    - Classified as 'marketing'
    - No purchase history from same sender
    - Not whitelisted
    - Unsubscribe link extracted
    - High safety score
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ul.id,
            ul.sender_email,
            ul.sender_name,
            ul.subject,
            ul.link_url,
            ul.link_type,
            ul.safety_score,
            COUNT(DISTINCT c.id) as email_count
        FROM unsubscribe_links ul
        JOIN classifications c ON ul.sender_email = c.sender
        WHERE ul.status = 'approved'
          AND ul.safety_score >= 70
          AND ul.is_whitelisted = 0
          AND NOT EXISTS (
              SELECT 1 FROM classifications c2
              WHERE c2.sender = ul.sender_email
                AND c2.category = 'purchase'
          )
        GROUP BY ul.sender_email
        ORDER BY email_count DESC, ul.safety_score DESC
    """)

    return cursor.fetchall()
```

---

## Implementation Phases

### Phase 0: Database Setup (30 minutes)

**Files to create**:
- `src/python/setup_unsubscribe_db.py` - Database schema setup

**Tasks**:
1. Extend existing `setup_email_classifier_db.py`
2. Add new tables (unsubscribe_links, unsubscribe_attempts, etc.)
3. Create indexes
4. Populate default config
5. Run migration script

**Checkpoint**: Database created with all tables, verified with SQLite browser

---

### Phase 1: Link Extraction (2-3 hours)

**Files to create**:
- `src/python/extract_unsubscribe_links.py` - Main extraction logic
- `tests/test_link_extraction.py` - Unit tests

**Tasks**:
1. Implement `parse_list_unsubscribe_header()`
2. Implement `extract_from_html_body()`
3. Implement `extract_from_text_body()`
4. Write extraction tests
5. Test on 20 sample emails

**Checkpoint**: Successfully extract unsubscribe links from 20 marketing emails

---

### Phase 2: Safety Classification (2-3 hours)

**Files to create**:
- `src/python/classify_unsubscribe_safety.py` - Safety scoring logic
- `tests/test_safety_classification.py` - Unit tests

**Tasks**:
1. Implement whitelist auto-population
2. Implement safety score calculation
3. Implement phishing detection
4. Write classification tests
5. Test on extracted links from Phase 1

**Checkpoint**: All 20 sample links classified with safety scores, manual review confirms accuracy

---

### Phase 3: Unsubscribe Execution (3-4 hours)

**Files to create**:
- `src/python/execute_unsubscribe.py` - Execution logic
- `src/python/http_handlers.py` - HTTP GET/POST handlers
- `src/python/mailto_handler.py` - Email-based handler
- `tests/test_execution.py` - Unit tests

**Tasks**:
1. Implement HTTP GET handler
2. Implement HTTP POST handler (RFC 8058)
3. Implement mailto handler
4. Implement rate limiter
5. Implement retry logic
6. Add comprehensive logging

**Checkpoint**: Test with 2 controlled unsubscribes in dry-run mode, verify logging

---

### Phase 4: Dry Run Testing (1-2 hours)

**Tasks**:
1. Enable dry_run_mode in config
2. Run full pipeline on 50 emails
3. Verify no actual HTTP requests
4. Review all logs and database entries
5. Check safety scores and recommendations

**Checkpoint**: Dry run completes without errors, all data looks correct

---

### Phase 5: Live Testing (1 hour + 3 days monitoring)

**Tasks**:
1. Create 2 test email subscriptions
2. Disable dry_run_mode
3. Run on test emails only
4. Monitor for confirmation emails
5. Verify no more emails from those senders after 3 days

**Checkpoint**: Test unsubscribes successful, confirmations received

---

### Phase 6: Batch Processing (2-3 hours)

**Files to create**:
- `src/python/batch_unsubscribe.py` - Batch processing logic

**Tasks**:
1. Implement batch processing with progress reporting
2. Add checkpointing (resume on failure)
3. Add summary statistics
4. Test on 100 emails
5. Generate final report

**Checkpoint**: Successfully unsubscribe from 100+ marketing lists

---

### Phase 7: Monitoring & Maintenance (Ongoing)

**Files to create**:
- `src/python/monitor_unsubscribe_success.py` - Success monitoring
- `src/python/email_stats.py` - Statistics dashboard

**Tasks**:
1. Monitor confirmation emails
2. Track new emails from "unsubscribed" senders (failures)
3. Update success rates in database
4. Generate weekly reports
5. Refine safety scoring based on results

**Checkpoint**: 7-day report showing unsubscribe success rate > 90%

---

## CLI Usage Examples

### Extract Unsubscribe Links

```bash
# Extract from all marketing emails
python src/python/extract_unsubscribe_links.py

# Extract from specific sender
python src/python/extract_unsubscribe_links.py --sender "marketing@example.com"

# Extract from emails in date range
python src/python/extract_unsubscribe_links.py --after 2026-01-01 --before 2026-02-01
```

### Classify Safety

```bash
# Classify all pending links
python src/python/classify_unsubscribe_safety.py

# Show safety scores
python src/python/classify_unsubscribe_safety.py --show-scores

# Approve all links with score >= 80
python src/python/classify_unsubscribe_safety.py --auto-approve --threshold 80
```

### Execute Unsubscribes

```bash
# Dry run (no actual requests)
python src/python/execute_unsubscribe.py --dry-run

# Execute approved links only
python src/python/execute_unsubscribe.py --approved-only

# Execute specific sender
python src/python/execute_unsubscribe.py --sender "marketing@example.com"

# Batch process with rate limit
python src/python/execute_unsubscribe.py --batch-size 50 --rate-limit 10
```

### Monitor Success

```bash
# Check for confirmations
python src/python/monitor_unsubscribe_success.py --days 3

# Show statistics
python src/python/email_stats.py --unsubscribe-stats

# Generate report
python src/python/email_stats.py --report --output report.txt
```

---

## Configuration File

**File**: `personal/data/email-classifier/unsubscribe_config.json`

```json
{
  "safety": {
    "min_score_auto_approve": 70,
    "require_manual_review_below": 50,
    "never_unsubscribe_domains": [
      "amazon.com",
      "paypal.com",
      "bank.com",
      ".gov",
      ".edu"
    ]
  },
  "rate_limiting": {
    "max_per_minute": 10,
    "max_per_hour": 50,
    "max_per_day": 200,
    "backoff_on_error": true
  },
  "http_client": {
    "timeout_seconds": 10,
    "max_redirects": 5,
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "verify_ssl": true
  },
  "execution": {
    "dry_run": true,
    "require_confirmation": true,
    "auto_trash_after_unsubscribe": false,
    "monitor_confirmations": true,
    "confirmation_wait_days": 3
  },
  "logging": {
    "level": "INFO",
    "log_file": "personal/data/email-classifier/logs/unsubscribe.log",
    "log_http_requests": true,
    "truncate_urls_in_logs": true
  }
}
```

---

## Error Scenarios & Handling

| Error Scenario | Detection | Handling | Recovery |
|----------------|-----------|----------|----------|
| Network timeout | HTTP request timeout | Log error, mark as failed | Retry with exponential backoff |
| Invalid URL | URL parsing exception | Log validation error | Skip, flag for manual review |
| Rate limit hit | 429 status code | Sleep 60s, retry | Resume after cooldown |
| Phishing detected | Safety classifier | Block, alert user | Add to blacklist |
| Whitelisted sender | Database query | Skip, log reason | None needed |
| Link requires login | HTTP 401/403 | Flag as form-based | Manual review |
| Confirmation not received | Email monitoring | Mark uncertain | Retry after 7 days |
| Gmail API quota exceeded | API error | Pause processing | Resume next hour |
| Database locked | SQLite exception | Wait and retry | Use WAL mode |
| Malformed email | Parsing exception | Log, skip email | Continue with next |

---

## Success Metrics

### Key Performance Indicators

1. **Extraction Accuracy**
   - Target: > 95% of marketing emails have unsubscribe link extracted
   - Measure: Manual review of 100 random samples

2. **Safety Classification Accuracy**
   - Target: < 1% false positives (safe senders marked unsafe)
   - Target: < 5% false negatives (unsafe senders marked safe)
   - Measure: Manual review + monitoring for issues

3. **Unsubscribe Success Rate**
   - Target: > 90% of attempted unsubscribes succeed
   - Measure: Confirmation emails + lack of future emails

4. **Phishing Detection**
   - Target: 100% of known phishing attempts blocked
   - Measure: Test with known phishing samples

5. **Email Volume Reduction**
   - Target: > 50% reduction in marketing email volume
   - Measure: Email count before/after over 30 days

6. **Processing Speed**
   - Target: < 5 seconds per email for extraction + classification
   - Target: < 2 seconds per unsubscribe execution
   - Measure: Timing logs in database

### Monitoring Dashboard

```
Email Unsubscribe Bot - Weekly Summary
=====================================

Emails Processed:         1,247
Unsubscribe Links Found:    892 (71.5%)
Safety Approved:            645 (72.3%)
Manual Review Required:     189 (21.2%)
Rejected (Unsafe):           58 (6.5%)

Unsubscribe Attempts:       645
Successful:                 612 (94.9%)
Failed:                      33 (5.1%)

Confirmations Received:     578 (89.6%)

Top Unsubscribed Senders:
1. marketing@retailer.com     45 emails
2. deals@shop.com            38 emails
3. newsletter@brand.com       32 emails

Safety Blocks (Whitelist):    23
Phishing Attempts Blocked:     2

Estimated Time Saved: 18 hours/year reading unwanted emails
```

---

## Future Enhancements

### Version 2.0 Features

1. **Machine Learning Classification**
   - Train model on user unsubscribe patterns
   - Predict which marketing emails user wants to keep
   - Auto-approve based on confidence

2. **Smart Preference Centers**
   - Selenium integration for form-based unsubscribes
   - Handle CAPTCHA with manual intervention
   - Remember form patterns for similar senders

3. **Unsubscribe Preview**
   - Show what emails will be affected
   - Preview last 5 emails from sender
   - "Undo" feature if unsubscribed by mistake

4. **Integration with Email Client**
   - Browser extension for one-click unsubscribe
   - Mobile app integration
   - Real-time processing as emails arrive

5. **Collaborative Filtering**
   - Share unsubscribe patterns (anonymized)
   - Learn from community success rates
   - Crowdsourced phishing detection

6. **Advanced Analytics**
   - Email volume trends over time
   - Sender reputation scoring
   - Unsubscribe success prediction

---

## Appendix A: RFC 8058 Compliance

The bot implements RFC 8058 "Signaling One-Click Functionality for List Email Headers" for modern unsubscribe handling.

**Key Requirements**:
1. Check for `List-Unsubscribe-Post` header
2. If present, use POST instead of GET
3. POST body must be: `List-Unsubscribe=One-Click`
4. Content-Type: `application/x-www-form-urlencoded`
5. Should NOT follow redirects
6. Success indicated by 2xx status code

**Example**:
```
List-Unsubscribe: <https://example.com/unsubscribe/opaque123>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

**Implementation** (see HTTP POST Handler section above)

---

## Appendix B: Sample Database Queries

### Find High-Volume Senders Ready to Unsubscribe

```sql
SELECT
    sender_email,
    COUNT(*) as email_count,
    MAX(safety_score) as safety_score,
    GROUP_CONCAT(DISTINCT link_type) as available_methods
FROM unsubscribe_links
WHERE status = 'approved'
  AND safety_score >= 70
GROUP BY sender_email
HAVING email_count >= 10
ORDER BY email_count DESC
LIMIT 20;
```

### Unsubscribe Success Rate by Link Type

```sql
SELECT
    link_type,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
    ROUND(AVG(CASE WHEN success = 1 THEN 100.0 ELSE 0.0 END), 1) as success_rate
FROM unsubscribe_attempts
GROUP BY link_type
ORDER BY success_rate DESC;
```

### Senders Still Sending After Unsubscribe

```sql
SELECT
    ul.sender_email,
    ua.attempt_timestamp as unsubscribed_at,
    COUNT(c.id) as emails_since_unsubscribe
FROM unsubscribe_attempts ua
JOIN unsubscribe_links ul ON ua.link_id = ul.id
JOIN classifications c ON c.sender = ul.sender_email
WHERE ua.success = 1
  AND c.date > ua.attempt_timestamp
GROUP BY ul.sender_email
HAVING emails_since_unsubscribe > 0
ORDER BY emails_since_unsubscribe DESC;
```

### Safety Score Distribution

```sql
SELECT
    CASE
        WHEN safety_score >= 80 THEN '80-100 (Safe)'
        WHEN safety_score >= 60 THEN '60-79 (Moderate)'
        WHEN safety_score >= 40 THEN '40-59 (Caution)'
        ELSE '0-39 (Unsafe)'
    END as score_range,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM unsubscribe_links), 1) as percentage
FROM unsubscribe_links
GROUP BY score_range
ORDER BY score_range DESC;
```

---

## Appendix C: Recommended Python Dependencies

**File**: `requirements.txt` (add to existing)

```txt
# HTTP client (already included likely)
requests>=2.31.0

# HTML parsing
beautifulsoup4>=4.12.0
lxml>=4.9.0

# Gmail API (already included)
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.1.0
google-api-python-client>=2.0.0

# URL parsing (stdlib, no install needed)
# urllib.parse

# Optional: Advanced form handling (Phase 2)
# selenium>=4.15.0
# webdriver-manager>=4.0.0

# Optional: Better regex
# regex>=2023.10.0
```

---

## Review Checklist

Before implementation, verify:

- [ ] Database schema reviewed and approved
- [ ] Safety mechanisms understood and validated
- [ ] Privacy considerations addressed
- [ ] Integration points with classifier identified
- [ ] Test strategy defined
- [ ] Error handling comprehensive
- [ ] Rate limiting appropriate
- [ ] Phishing detection sufficient
- [ ] Whitelist auto-population safe
- [ ] Manual review checkpoints clear
- [ ] Monitoring plan in place
- [ ] Rollback strategy defined
- [ ] Success metrics measurable

---

## Next Steps

1. **Review this plan** with another developer or security expert
2. **Critique safety mechanisms** - are they sufficient?
3. **Validate database schema** - any missing fields?
4. **Test phishing detection** with known samples
5. **Set up Phase 0** (database) when ready to proceed
6. **Proceed incrementally** through phases with checkpoints

---

**Document Status**: Ready for review and critique
**Last Updated**: 2026-02-13
**Author**: Claude (Sonnet 4.5)
**Reviewer**: [To be assigned]
