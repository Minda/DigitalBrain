# Fixes Applied to Article Download Function

## Issues Found and Fixed

### Issue 1: Missing `--script` Flag
**Problem:** The `download_article.py` script uses inline PEP 723 dependency declarations but wasn't being invoked with `uv run --script`, causing:
```
ModuleNotFoundError: No module named 'bs4'
```

**Fix:**
```python
# Before
['uv', 'run', 'python', 'download_article.py', url, str(temp_dir)]

# After
['uv', 'run', '--script', 'download_article.py', url, '--output-dir', str(temp_dir)]
```

### Issue 2: Wrong Argument Format
**Problem:** Script expects `--output-dir <path>` but we were passing positional argument

**Fix:** Added `--output-dir` flag before the path argument

### Issue 3: Date Subdirectory Search
**Problem:** The `download_article.py` script creates files in date-based subdirectories (e.g., `2026-02/`), but our script was looking for PDFs directly in the temp directory with `glob("*.pdf")`

**Fix:**
```python
# Before
pdf_files = list(temp_dir.glob("*.pdf"))

# After
pdf_files = list(temp_dir.glob("**/*.pdf"))  # Recursive search
```

## Testing

All fixes verified by successfully downloading test articles:
- ✅ Anthropic research articles
- ✅ Bluedot blog posts
- ✅ Alignment Forum posts
- ✅ LessWrong articles

## Files Updated

1. `src/python/browser_automation/download_high_value_resources.py`
2. `.claude/skills/playwright-downloading-courses/scripts/download_high_value_resources.py`

Both files now have identical fixes applied.
