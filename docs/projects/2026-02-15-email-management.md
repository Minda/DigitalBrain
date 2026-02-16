## Project: Email Management & Organization

**Category**: AI & Automation

TODAY: February 15 2026

---

### Overview

A comprehensive system for managing, organizing, and automating Gmail workflows. This project focuses on creating intelligent tools to classify emails, manage labels, and automate common email tasks using AI and the Gmail API.

---

### Problem Space

**What problems are we solving?**

- Gmail label sprawl - 163+ labels accumulated over years, many outdated
- Manual email classification is time-consuming
- Clothing/shopping emails need automated filtering and organization
- No systematic way to archive or remove old organizational systems
- Difficulty finding and managing relevant emails across many labels

**Who is affected?**

- Primary user (Minda) managing personal and professional email
- Anyone with long-term Gmail accounts facing label accumulation
- Users wanting to automate email classification and organization

---

### Goals

**Primary Goals**:

- [ ] Clean up and consolidate Gmail labels (remove 80+ obsolete labels)
- [ ] Implement AI-based email classification (clothing, shopping, etc.)
- [ ] Build automated email management workflows
- [ ] Create sustainable email organization system
- [ ] Integrate Gmail MCP server with AI classification tools

**Success Metrics**:

- Reduce total labels from 163 to <50 active, relevant labels
- Automate 80%+ of clothing/shopping email classification
- Zero manual label management for routine emails
- Complete label cleanup without data loss

---

### Scope

**In Scope**:

- Gmail label deletion and cleanup
- AI-powered email classification (Haiku-based)
- Clothing/shopping email automation
- MCP server enhancements (label management, batch operations)
- Email statistics and analytics
- Unsubscribe automation for marketing emails

**Out of Scope**:

- Email client UI development
- Third-party email service integrations (non-Gmail)
- Calendar or contact management
- Email template creation tools

---

### Related Features

Features that are part of this project:

- [ ] Delete Old Gmail Labels - In Progress
  - Link: `../features/2026-02-15-delete-old-gmail-labels.md`
- [ ] AI Email Classification System - Planned
- [ ] Clothing Email Automation - In Progress (existing scripts)
- [ ] Unsubscribe Link Extraction & Cleanup - In Progress
  - Link: `../features/2026-02-15-unsubscribe-extraction-cleanup.md`
- [ ] Gmail MCP Server Enhancements - In Progress

---

### Technical Architecture

**Key Components**:

- **Gmail MCP Server** - Tool interface for Gmail operations (app/mcp/gmail/)
- **Python Classification Scripts** - AI-based email categorization (src/python/)
- **Database Layer** - SQLite for classification tracking and statistics
- **Claude Integration** - LLM-powered email understanding and routing

**Dependencies**:

- Google Gmail API (via google-api-python-client)
- Anthropic Claude API (Haiku for classification)
- FastMCP framework
- SQLite for persistence

**Technology Stack**:

- Python (uv for package management)
- Gmail API with OAuth2
- Anthropic Claude API (Haiku model)
- SQLite
- FastMCP (Model Context Protocol)

---

### Milestones

**Phase 1**: Label Cleanup - Feb 2026
- [ ] Implement label deletion in MCP server
- [ ] Create deletion plan identifying obsolete labels
- [ ] Execute label deletion (preserve 30+ keep labels)
- [ ] Verify no data loss

**Phase 2**: Classification Automation - Mar 2026
- [ ] Integrate existing clothing classifier
- [ ] Expand to other email categories
- [ ] Build feedback loop for improving classification
- [ ] Create dashboard for classification stats

**Phase 3**: Advanced Automation - Apr 2026
- [ ] Implement unsubscribe automation
- [ ] Build email routing rules
- [ ] Create scheduled cleanup tasks
- [ ] Develop email analytics dashboard

---

### Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Accidental deletion of important labels | High | Low | Test deletion on non-critical labels first, maintain list of labels to keep |
| Gmail API rate limits | Medium | Medium | Implement batching, caching, and exponential backoff |
| Classification accuracy issues | Medium | Medium | Start with high-confidence classifications, build feedback mechanism |
| OAuth token expiration | Low | Medium | Implement automatic token refresh handling |

---

### Resources

**Documentation**:
- Gmail API Reference: https://developers.google.com/gmail/api
- MCP Protocol: https://modelcontextprotocol.io/
- Existing implementation: app/mcp/gmail/, src/python/

**Related Projects**:
- Exobrain infrastructure
- Personal AI assistant workflows

**External References**:
- FastMCP documentation
- Google OAuth2 guides

---

### Team

**Project Lead**: Minda
**Contributors**: Claude (AI assistant)
**Stakeholders**: Minda

---

**Created**: 2026-02-15
**Last Updated**: 2026-02-15
**Status**: In Progress
**Priority**: High
