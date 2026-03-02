# AI-Powered Job Filtering

This module provides intelligent job filtering using Claude 3.5 Haiku to automatically filter out irrelevant jobs during the scraping process.

## How It Works

1. **Profile-Based Filtering**: Reads your job profile from `config/job-profile.md`
2. **AI Analysis**: Uses Claude to analyze each job posting against your profile
3. **Conservative Filtering**: Only filters out clearly irrelevant jobs (office manager, sales, marketing roles with no AI component, etc.)
4. **Skip Unrelated Jobs**: Filtered jobs never touch the database

## Setup

### 1. Add API Key

Add your Anthropic API key to `.env.local`:

```bash
ANTHROPIC_API_KEY=sk-ant-...
```

Get your API key from: https://console.anthropic.com/

### 2. Update Job Profile (Optional)

Edit `config/job-profile.md` to reflect your preferences:
- Target roles and seniority
- Technical interests
- Company preferences
- Dealbreakers

The filter will use this profile to make relevance decisions.

### 3. Test the Filter

Run the test script to validate the filtering logic:

```bash
ANTHROPIC_API_KEY=sk-ant-... npx tsx scripts/test-job-filter.ts
```

This tests 10 sample jobs (office manager, sales, AI safety engineer, etc.) and shows which would be filtered.

## Usage

The filter runs automatically during HN scraping. No code changes needed!

```bash
# Scrape with AI filtering enabled (default)
# Visit http://localhost:3000/jobs and click "Scrape HN"
```

The UI will show: `Last scrape: 5m ago · 12 new jobs · 8 filtered out`

## Disabling the Filter

To disable AI filtering (for testing or debugging):

```bash
# In .env.local
ENABLE_JOB_FILTER=false
```

## Cost Estimate

- **Model**: Claude 3.5 Haiku
- **Cost per job**: ~$0.001
- **Monthly cost**: ~$0.50 (for 500 jobs/month)
- **Benefit**: Saves 10-20 minutes of manual triage per scrape

## Filter Behavior

### Jobs that ARE filtered out:
- ❌ Office manager, administrative roles
- ❌ Sales, marketing positions (no AI component)
- ❌ Junior roles (below mid-level)
- ❌ Pure frontend roles (no AI/ML)
- ❌ Crypto/web3 positions (dealbreaker)
- ❌ Military/security clearance roles (dealbreaker)

### Jobs that are NOT filtered:
- ✅ AI/ML Engineer roles at any company
- ✅ AI Safety / Alignment positions
- ✅ Platform/Observability roles at AI companies
- ✅ Generic "Software Engineer" at frontier AI labs (OpenAI, Anthropic, DeepMind)
- ✅ Any role with an AI/ML component, even if title is generic

## Architecture

```
HN Scraper
    ↓
Parse job posting (company, title, description)
    ↓
AI Filter: isJobRelevant(description, title, company)
    ↓
    ├─ isRelevant: true  → Continue to save job
    └─ isRelevant: false → Skip job, increment filtered count
```

## Files

- `ai-filter.ts` - Core filtering logic
- `../../scrapers/hn.ts` - Integration with HN scraper
- `../../../scripts/test-job-filter.ts` - Test script
- `config/job-profile.md` - Your job preferences (project root)

## Troubleshooting

**Filter not working?**
- Check that `ANTHROPIC_API_KEY` is set in `.env.local`
- Verify `ENABLE_JOB_FILTER` is not set to `false`
- Check console logs during scraping for filter output

**Too many jobs filtered?**
- The filter is conservative - this shouldn't happen
- Review `config/job-profile.md` to ensure it's accurate
- Check console logs to see why jobs are being filtered

**Not enough jobs filtered?**
- Update `config/job-profile.md` with clearer dealbreakers
- The filter is designed to fail open (let borderline jobs through)

## Future Enhancements

- [ ] Batch filtering for improved performance
- [ ] Filter confidence scoring
- [ ] Learning from user dismissals
- [ ] Multi-source filter support (not just HN)
