# Skill Optimization Checklist

A systematic checklist for optimizing Claude Code skills from initial version to production-ready.

## Pre-Optimization

Before starting optimization, complete this checklist:

### Requirements Clarity
- [ ] Skill purpose is clear and focused
- [ ] Use cases are documented
- [ ] Success criteria are defined
- [ ] Performance targets are set (if applicable)

### Baseline Measurement
- [ ] Tested with realistic data
- [ ] Timed performance on actual use cases
- [ ] Memory usage measured
- [ ] Token consumption estimated
- [ ] User feedback collected

### Problem Identification
- [ ] Specific pain points identified
- [ ] Bottlenecks measured (not guessed)
- [ ] User confusion points documented
- [ ] Error scenarios catalogued

**Don't proceed without baselines!** You can't measure improvement without knowing where you started.

---

## Performance Optimization

### File Operations
- [ ] Minimize file system walks
- [ ] Use indexing for searches (if >100 files)
- [ ] Cache file reads when reused
- [ ] Stream large files instead of loading fully
- [ ] Read only what's needed (tail-read for logs)

### Data Processing
- [ ] Identify O(n²) or worse algorithms
- [ ] Use appropriate data structures (sets vs lists, dicts vs arrays)
- [ ] Avoid redundant parsing
- [ ] Cache expensive computations
- [ ] Process in parallel when possible

### External Operations
- [ ] Batch API calls when possible
- [ ] Use async for I/O-bound operations
- [ ] Add timeouts to prevent hangs
- [ ] Cache API responses with TTL
- [ ] Handle rate limits gracefully

### Memory Management
- [ ] Avoid loading entire datasets in memory
- [ ] Stream processing for large files
- [ ] Release resources explicitly
- [ ] Use generators instead of lists
- [ ] Profile memory usage at scale

### Context Optimization
- [ ] SKILL.md is <500 lines
- [ ] Detailed docs moved to references/
- [ ] Examples are concise
- [ ] Dynamic context uses `!` commands sparingly
- [ ] Frontmatter is minimal

---

## Clarity Optimization

### Instructions
- [ ] Steps are clear and actionable
- [ ] Language is direct (not tentative)
- [ ] Examples are provided for complex concepts
- [ ] Jargon is explained or avoided
- [ ] Workflow is easy to follow

### Output Quality
- [ ] Format is consistent
- [ ] Information density is appropriate
- [ ] Visual hierarchy is clear (headers, bullets, etc.)
- [ ] Success indicators are obvious
- [ ] Error states are distinguishable

### Error Messages
- [ ] Say what went wrong
- [ ] Explain why it happened
- [ ] Suggest how to fix it
- [ ] Include relevant context
- [ ] Are friendly and helpful (not blaming)

### Examples
- [ ] Cover common use cases
- [ ] Show actual input and output
- [ ] Are realistic (not toy examples)
- [ ] Demonstrate best practices
- [ ] Include edge cases

---

## Robustness Optimization

### Error Handling
- [ ] All error cases have explicit handling
- [ ] No silent failures
- [ ] Errors include recovery suggestions
- [ ] Stack traces are supplemented with explanation
- [ ] Graceful degradation where appropriate

### Input Validation
- [ ] Required parameters are checked
- [ ] Types are validated
- [ ] Ranges are enforced
- [ ] File existence verified before processing
- [ ] Format validation before parsing

### Edge Cases
- [ ] Empty inputs handled
- [ ] Null/undefined handled
- [ ] Very large inputs don't crash
- [ ] Special characters escaped properly
- [ ] Concurrent access safe (if applicable)

### Fallbacks
- [ ] Defaults for optional parameters
- [ ] Fallback behavior when resources unavailable
- [ ] Partial results on non-critical failures
- [ ] Clear indication when operating in fallback mode

---

## Structure Optimization

### File Organization
- [ ] SKILL.md focuses on core workflow
- [ ] Details moved to references/
- [ ] Scripts in scripts/ directory
- [ ] Templates in templates/ or examples/
- [ ] README.md exists and is helpful

### Modularity
- [ ] Complex logic extracted to scripts
- [ ] Reusable components identified
- [ ] Clear separation of concerns
- [ ] Can be tested independently
- [ ] Dependencies are explicit

### Documentation
- [ ] README explains what skill does
- [ ] Prerequisites are listed
- [ ] Installation steps are clear
- [ ] Usage examples are provided
- [ ] Known limitations documented

### Progressive Disclosure
- [ ] Basic usage is simple
- [ ] Advanced features optional
- [ ] References loaded on-demand
- [ ] Complexity hidden until needed
- [ ] Clear path from basic to advanced

---

## Integration Optimization

### Skill Composition
- [ ] Works well with related skills
- [ ] No tool permission conflicts
- [ ] Output format compatible with other skills
- [ ] Shared resources handled properly

### Workflow Integration
- [ ] Fits into realistic workflows
- [ ] Handoffs to other skills are smooth
- [ ] Context preserved appropriately
- [ ] Can be used standalone or in sequence

### Tool Usage
- [ ] Correct tools for each operation
- [ ] Allowed-tools list is accurate
- [ ] Permission requests are justified
- [ ] Tool patterns match actual usage

---

## Distribution Readiness

### Validation
- [ ] Passes package_skill.py validation
- [ ] Frontmatter is valid YAML
- [ ] Name follows conventions
- [ ] Description is specific and useful
- [ ] No hardcoded paths

### Documentation
- [ ] README is complete
- [ ] Prerequisites listed
- [ ] Installation instructions clear
- [ ] Examples are runnable
- [ ] Troubleshooting section exists

### Versioning
- [ ] ITERATIONS.md tracks changes
- [ ] Breaking changes documented
- [ ] Migration guide provided (if needed)
- [ ] Performance improvements noted
- [ ] Version number follows semver

### Testing
- [ ] Tested on clean install
- [ ] Works without personal configuration
- [ ] Examples work as documented
- [ ] Edge cases handled
- [ ] No dangling references to private paths

---

## Iteration Tracking

### Documentation
- [ ] ITERATIONS.md exists
- [ ] Each optimization round documented
- [ ] Performance metrics recorded
- [ ] Tradeoffs noted
- [ ] Breaking changes highlighted

### Measurement
- [ ] Before/after performance measured
- [ ] Improvements quantified
- [ ] Memory impact noted
- [ ] Token budget tracked
- [ ] User feedback incorporated

---

## Final Review

### Self-Check
- [ ] Would I use this skill myself?
- [ ] Would I recommend it to others?
- [ ] Am I proud of the code quality?
- [ ] Is it better than the first version?
- [ ] Have I learned from this process?

### Completion Criteria
- [ ] All tests pass
- [ ] Performance meets targets
- [ ] User feedback is positive
- [ ] Documentation is complete
- [ ] Ready for wider use

---

## Optimization Priorities

Not all optimizations are equal. Focus on these in order:

### Priority 1: Correctness
**Must have:**
- Produces correct results
- Handles errors gracefully
- Doesn't corrupt data
- Validates inputs

**Why:** A fast but wrong skill is useless.

### Priority 2: Usability
**Should have:**
- Clear instructions
- Good error messages
- Helpful examples
- Easy to understand

**Why:** An unclear skill won't be used.

### Priority 3: Performance
**Nice to have:**
- Fast enough for realistic use
- Scales to actual data sizes
- Doesn't waste resources

**Why:** Makes the skill pleasant to use.

### Priority 4: Elegance
**Optional:**
- Beautiful code
- Perfect abstractions
- Zero technical debt

**Why:** Perfect is the enemy of good.

---

## When to Stop Optimizing

**Stop when:**
- ✓ Skill meets user needs
- ✓ Performance is acceptable
- ✓ No critical bugs remain
- ✓ You'd use it yourself
- ✓ Further optimization shows diminishing returns

**Don't stop if:**
- ✗ Users are confused
- ✗ Performance is unacceptable
- ✗ Critical bugs exist
- ✗ You wouldn't use it yourself

---

## Quick Optimization Triage

**If skill is slow:**
1. Profile to find bottleneck
2. Apply appropriate pattern (see performance-patterns.md)
3. Measure improvement
4. Iterate if needed

**If skill is confusing:**
1. Get user feedback
2. Simplify instructions
3. Add examples
4. Test with new user

**If skill is brittle:**
1. Identify failure modes
2. Add error handling
3. Add validation
4. Test edge cases

**If skill is too complex:**
1. Extract to references
2. Create basic vs advanced modes
3. Simplify common case
4. Add progressive disclosure

---

**Remember:** Optimization is a process, not a destination. Ship when it's good enough, improve based on real usage.
