# Optimization History: [skill-name]

Track the evolution of your skill through optimization iterations.

---

## v1.1 - YYYY-MM-DD

### Changes
<!-- List what changed in this iteration -->
-
-
-

### Performance
<!-- Before → After measurements -->
- Execution time: ___ → ___ (**___x faster**)
- Memory usage: ___ → ___ (**___x smaller**)
- Token budget: ___ → ___ tokens
- Files processed: ___ → ___ per second

### Technical Approach
<!-- Explain how you achieved the improvements -->

Applied the [pattern name] pattern:
-
-
-

### Breaking Changes
<!-- List any breaking changes -->
- [ ] None - fully backwards compatible
- [ ] Minor - [describe what changed]
- [ ] Major - [describe what changed and migration path]

### Tradeoffs
<!-- What did you give up to get the improvements? -->

**Pros:**
-
-

**Cons:**
-
-

### Lessons Learned
<!-- What did you learn from this optimization? -->
-
-

### Next Steps
<!-- What could be improved next? -->
- [ ]
- [ ]
- [ ]

---

## v1.0 - YYYY-MM-DD

Initial version.

### Baseline Metrics
- Execution time: ___
- Memory usage: ___
- Token budget: ___ tokens
- Lines in SKILL.md: ___

### Known Issues
-
-

### Improvement Ideas
-
-

---

## Template Usage

### Recording a New Iteration

1. Copy the v1.1 template above
2. Update version number (following [semver](https://semver.org/))
3. Fill in the date (YYYY-MM-DD format)
4. Document changes made
5. Record performance measurements (before → after)
6. Explain technical approach
7. Note any breaking changes
8. Document tradeoffs made
9. Record lessons learned
10. Add to top of this file (newest first)

### Version Numbering

Follow semantic versioning:

- **v1.0.0** - Initial release
- **v1.0.1** - Bug fixes, no new features (patch)
- **v1.1.0** - New features, backwards compatible (minor)
- **v2.0.0** - Breaking changes (major)

### Performance Metrics to Track

**Execution time:**
- Run skill 5-10 times
- Report median (p50) time
- Note if there's high variance

**Memory usage:**
- Use `tracemalloc` for Python scripts
- Report peak memory, not just final
- Test with realistic data sizes

**Token budget:**
- SKILL.md file size
- Plus any auto-loaded references
- Measure in Claude tokens (roughly 4 chars = 1 token)

**Throughput:**
- Items processed per second
- Files per second
- Queries per second

### Example Entry

```markdown
## v2.0 - 2024-01-22

### Changes
- Replaced file-walking search with SQLite FTS5 index
- Moved detailed documentation to references/
- Added incremental indexing for updates
- Improved error messages with recovery suggestions

### Performance
- Query time: 15.2s → 0.08s (**190x faster**)
- Memory usage: 2,048 MB → 14 MB (**146x smaller**)
- Token budget: 8,200 → 2,100 tokens (**3.9x smaller**)
- Index build time: N/A → 12s (one-time cost)

### Technical Approach

Applied the **File-Based → Index-Based** pattern:

1. Created SQLite database with FTS5 extension for full-text search
2. Built index once, storing: file paths, titles, content, metadata
3. Queries now use SQL instead of file system walks
4. Added incremental indexing to update only changed files

Key implementation details:
- Used FTS5 `rank` for relevance sorting
- Added `snippet()` function for context previews
- Cached index in `~/.cache/skill-name/index.db`
- Rebuild index if >30 days old or on demand

### Breaking Changes
- [x] Minor - New dependency on SQLite (ships with Python)
- [x] Minor - First run requires index build (~10-15s for 2,400 files)
- [ ] Major - Output format unchanged, fully compatible

Migration:
- No action needed for existing users
- First invocation will build index automatically
- Run `/skill-name index` to rebuild manually

### Tradeoffs

**Pros:**
- Dramatically faster searches (190x improvement)
- Scales to much larger datasets (tested to 50,000 files)
- Supports complex search syntax (AND, OR, phrases, etc.)
- Lower memory footprint (doesn't load all files)

**Cons:**
- Added dependency on SQLite (acceptable - ships with Python)
- Index needs initial build time (~12s, but one-time)
- Index needs updating when files change (automated)
- Added complexity (~150 lines of indexing code)

### Lessons Learned

**What worked:**
- Profiling first revealed file-walking as bottleneck (not parsing)
- Testing with real data (2,400 files) showed true performance
- SQLite FTS5 is extremely fast for text search
- Incremental updates keep index fresh without full rebuilds

**What didn't work:**
- Initially tried JSON index - too slow for search
- Considered regex-based search - O(n) wouldn't scale
- Tried in-memory cache - memory usage too high

**Recommendations:**
- For any skill searching >100 files, use indexing
- SQLite FTS5 is perfect for full-text search
- One-time costs (index build) are acceptable for huge speedups
- Always test with realistic data volumes

### Next Steps

**Potential improvements:**
- [ ] Add fuzzy search for typo tolerance
- [ ] Support searching by file type, date, size
- [ ] Add search history and suggestions
- [ ] Optimize index build time (currently 12s for 2,400 files)
- [ ] Add index statistics command

**Nice to have:**
- [ ] Web interface for browsing index
- [ ] Export search results to different formats
- [ ] Integration with other search tools

---

## v1.0 - 2024-01-15

Initial version.

### Baseline Metrics
- Query time: 15.2s (median over 10 runs)
- Memory usage: ~2 GB peak
- Token budget: 8,200 tokens
- Lines in SKILL.md: 340

### Known Issues
- Slow for large number of files (>500 files)
- High memory usage when processing all files
- No progress indicator for long operations
- Error messages sometimes unclear

### Improvement Ideas
- Add caching layer
- Investigate indexing solutions
- Move documentation to references
- Add better progress feedback
```

---

## Why Track Iterations?

**Learning:** Document what works and what doesn't
**Accountability:** See concrete improvements over time
**Communication:** Show others the evolution and rationale
**Decision-making:** Review tradeoffs when considering changes
**Motivation:** Visualize progress and impact

---

**Pro tip:** Update this file immediately after each optimization, while details are fresh. Future you will thank you.
