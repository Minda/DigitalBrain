# Skill Testing Guide

Comprehensive strategies for testing Claude Code skills before and during optimization.

## Testing Philosophy

**Test to learn, not to prove.** The goal is to discover how the skill behaves in real scenarios, identify bottlenecks, and understand user experience.

## Testing Phases

### Phase 1: Functional Testing

Verify the skill does what it's supposed to do.

#### Happy Path Testing

Test the skill with typical, expected inputs:

```
Test: /skill-name with standard arguments
Expected: Skill completes successfully with correct output
Observe:
  - Does it produce the expected result?
  - Is the output format correct?
  - Are instructions clear?
```

**Examples:**
- **Search skill:** Search for a term that exists
- **Transform skill:** Transform a well-formed input file
- **Generate skill:** Generate from complete, valid inputs

#### Edge Case Testing

Test boundary conditions and unusual inputs:

**Common edge cases:**
- Empty input
- Missing files
- Invalid arguments
- Very large inputs
- Very small inputs
- Special characters
- Unicode/encoding issues
- Permissions errors

**Testing checklist:**
```
[ ] Empty string input
[ ] Null/undefined values
[ ] Missing required files
[ ] Wrong file types
[ ] Files too large
[ ] Invalid format
[ ] Network errors (if applicable)
[ ] Timeout scenarios
[ ] Concurrent access
```

**Example test plan:**
```markdown
## Edge Case Tests for search-skill

1. **Empty query**
   → /search-skill ""
   → Expected: Clear error message, suggest what to search for

2. **Non-existent directory**
   → /search-skill "term" --path /does/not/exist
   → Expected: Helpful error, check if user meant something else

3. **Very long query (>1000 chars)**
   → /search-skill "[very long string]"
   → Expected: Handle gracefully or truncate with warning

4. **Special regex characters**
   → /search-skill "foo(bar)*"
   → Expected: Escape properly or guide user to use literal mode
```

### Phase 2: Performance Testing

Measure how the skill performs under realistic conditions.

#### Timing Tests

**Subjective timing:**
Ask user to report how long operations feel:
- Instant (<100ms)
- Fast (<1s)
- Acceptable (1-3s)
- Slow (3-10s)
- Very slow (>10s)

**Objective timing:**
```python
import time

start = time.time()
result = run_skill()
elapsed = time.time() - start

print(f"Completed in {elapsed:.2f}s")
```

**Percentile analysis:**
Run skill 10+ times with realistic data and measure:
- p50 (median)
- p95 (95th percentile)
- p99 (worst case)
- max (absolute worst)

This reveals consistency and outliers.

#### Scalability Tests

Test with increasing data sizes:

```
Small: 10 files, ~100KB
Medium: 100 files, ~10MB
Large: 1,000 files, ~100MB
Very Large: 10,000+ files, ~1GB
```

**What to measure:**
- Time vs. size (linear? logarithmic? exponential?)
- Memory usage at each scale
- Where it breaks down
- Acceptable limits

**Example:**
```
Files  | Time   | Memory | Notes
-------|--------|--------|------------------
10     | 0.1s   | 5 MB   | ✓ Instant
100    | 0.8s   | 45 MB  | ✓ Fast
1,000  | 12.5s  | 420 MB | ⚠ Getting slow
10,000 | 180s   | 4 GB   | ✗ Unusable
```

**Insight:** This reveals O(n) file walking. Time for indexing pattern.

#### Memory Profiling

**Simple approach:**
```python
import tracemalloc

tracemalloc.start()

# Run skill
result = run_skill()

current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"Current: {current / 1024 / 1024:.1f} MB")
print(f"Peak: {peak / 1024 / 1024:.1f} MB")
```

**What to look for:**
- Peak memory vs. input size
- Memory leaks (memory keeps growing)
- Unnecessary data retention
- Large objects in memory

### Phase 3: User Experience Testing

How does it feel to use?

#### Clarity Testing

**Ask testers:**
- Did you understand what to do?
- Were error messages helpful?
- Did output make sense?
- What was confusing?

**Common UX issues:**
- Unclear parameter names
- Too much output (information overload)
- Too little output (unclear what happened)
- Jargon without explanation
- No examples when needed
- Poor error messages

**Error message quality checklist:**
```
Good error messages:
  ✓ Say what went wrong
  ✓ Say why it went wrong
  ✓ Suggest how to fix it
  ✓ Show relevant context

Bad error messages:
  ✗ "Error"
  ✗ "Failed"
  ✗ Stack traces without explanation
  ✗ Technical jargon only
```

**Example improvement:**
```
Before: "FileNotFoundError: [Errno 2] No such file or directory: 'config.json'"

After: "Config file not found: config.json

       I looked in: /current/directory/config.json

       Try:
       - Create config.json with /create-config
       - Specify a different path with --config
       - Check if you're in the right directory"
```

#### Cognitive Load Testing

**Count the decisions user must make:**
- How many parameters?
- How many modes/options?
- How much domain knowledge required?
- How many steps in workflow?

**Simplification checklist:**
```
[ ] Can parameters have smart defaults?
[ ] Can modes be auto-detected?
[ ] Can steps be combined?
[ ] Can we guide instead of asking?
[ ] Can we show examples upfront?
```

### Phase 4: Integration Testing

Test skill in realistic workflows.

#### Workflow Testing

**Design realistic scenarios:**
```markdown
## Scenario: Developer adding new feature

1. Use /search-skill to find similar code
2. Read relevant files
3. Use /generate-skill to create boilerplate
4. Edit and refine
5. Use /test-skill to verify
6. Use /commit-skill to save

Test each transition:
  - Does output from step N work as input to step N+1?
  - Is context preserved appropriately?
  - Are files in expected states?
```

#### Skill Composition Testing

**Test when multiple skills interact:**
- Do they conflict?
- Do they complement each other?
- Is there redundancy?
- Do permissions work correctly?

### Phase 5: Regression Testing

**After optimizations, retest everything:**

```markdown
## Regression Test Checklist

Functional:
  [ ] All happy path tests pass
  [ ] All edge cases still handled
  [ ] No new errors introduced
  [ ] Output format unchanged (unless intentional)

Performance:
  [ ] Faster than before (measure)
  [ ] Memory usage acceptable
  [ ] Scales better than before

UX:
  [ ] Still clear and understandable
  [ ] Error messages still helpful
  [ ] No new confusion introduced
```

## Automated Testing

### Unit Tests for Scripts

If your skill includes Python scripts:

```python
import pytest
from skill_name import process_file

def test_process_valid_file():
    """Test with valid input"""
    result = process_file("test_data/valid.txt")
    assert result['status'] == 'success'
    assert len(result['items']) > 0

def test_process_empty_file():
    """Test with empty file"""
    result = process_file("test_data/empty.txt")
    assert result['status'] == 'success'
    assert len(result['items']) == 0

def test_process_missing_file():
    """Test with missing file"""
    with pytest.raises(FileNotFoundError):
        process_file("does_not_exist.txt")

def test_process_invalid_format():
    """Test with malformed input"""
    result = process_file("test_data/invalid.txt")
    assert result['status'] == 'error'
    assert 'message' in result
```

### Performance Benchmarks

```python
import pytest

@pytest.mark.benchmark
def test_performance_baseline(benchmark):
    """Benchmark current performance"""
    result = benchmark(run_skill, test_data)

    # Assert performance requirements
    assert benchmark.stats['mean'] < 0.5  # Must avg < 500ms
    assert benchmark.stats['max'] < 1.0   # Must never exceed 1s

@pytest.mark.parametrize('size', [10, 100, 1000])
def test_scalability(size):
    """Test performance scales appropriately"""
    data = generate_test_data(size)

    start = time.time()
    result = run_skill(data)
    elapsed = time.time() - start

    # Should be sub-linear with indexing
    assert elapsed < size * 0.001  # <1ms per item
```

### Validation Tests

```python
def test_skill_structure():
    """Validate SKILL.md structure"""
    skill_path = Path(".claude/skills/skill-name/SKILL.md")

    assert skill_path.exists()

    content = skill_path.read_text()

    # Check frontmatter
    assert content.startswith('---')
    assert 'name:' in content
    assert 'description:' in content

    # Check required sections
    assert '## When to Use' in content
    assert '## Instructions' in content or '## Workflow' in content
```

## Real-World Testing

### Beta Testing Process

1. **Find test users**
   - Someone unfamiliar with the skill
   - Someone familiar but critical
   - Someone with different use case

2. **Prepare test scenarios**
   - Write realistic scenarios
   - Provide test data
   - Set expectations

3. **Observe without helping**
   - Watch where they get stuck
   - Note what they skip/ignore
   - Record what they ask about

4. **Debrief**
   - What was confusing?
   - What was helpful?
   - What would you change?
   - Would you use this again?

### Dogfooding

**Use your own skill regularly:**
- Daily use reveals pain points
- You'll notice slowness
- You'll discover edge cases
- You'll find better ways

**Keep a "pain log":**
```markdown
# Skill-Name Pain Log

2024-01-22:
  - Searching through large repo takes forever
  - Error message when file missing is cryptic
  - Forgot what arguments are available

2024-01-23:
  - Output format hard to parse visually
  - Would be nice to cache results
```

## Testing Checklist Template

```markdown
# Testing Checklist: [skill-name]

## Functional Testing
- [ ] Happy path works
- [ ] Edge cases handled
- [ ] Error cases graceful
- [ ] Output correct

## Performance Testing
- [ ] Timed with realistic data
- [ ] Tested at multiple scales
- [ ] Memory usage acceptable
- [ ] No obvious bottlenecks

## UX Testing
- [ ] Instructions clear
- [ ] Error messages helpful
- [ ] Output understandable
- [ ] Examples work

## Integration Testing
- [ ] Works in realistic workflows
- [ ] Composes with other skills
- [ ] No conflicts

## Regression Testing
- [ ] All previous tests pass
- [ ] Performance improved
- [ ] No new issues

## Real-World Testing
- [ ] Used by someone else
- [ ] Used in actual work
- [ ] Pain points documented
```

## When to Stop Testing

**You've tested enough when:**
- ✓ All critical paths work
- ✓ Edge cases handled reasonably
- ✓ Performance meets expectations
- ✓ User feedback is positive
- ✓ You'd be comfortable using it yourself

**You haven't tested enough if:**
- ✗ You're unsure if it works at scale
- ✗ You haven't tried it with real data
- ✗ Error cases are unexplored
- ✗ No one else has used it
- ✗ You're guessing about performance

---

**Remember:** Testing is learning. The goal is to understand your skill's behavior, not to achieve 100% code coverage.
