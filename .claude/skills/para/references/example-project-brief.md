# Interactive Avatar MVP Brief

*Six-week roadmap for clinic-ready demo*

---

## Summary

This brief outlines the purpose, scope, and success criteria for Mindora's **Interactive Avatar MVP**, a low-code demo that showcases real-time AI-driven patient intake with emotional expressiveness and HIPAA-aligned data handling. The project will culminate in a live walkthrough for three pilot clinicians on **September 12, 2025**, proving technical feasibility and gathering usability feedback for the fund-raising deck.

## Key Takeaways

- **Clear Outcome:** Working demo + clinician feedback
- **Timeline:** Aug 4 → Sept 12 (6 weeks)
- **Tech Stack:** Next.js, HeyGen API, Firebase
- **Key Constraint:** HIPAA-Lite Compliance (no PHI at rest; transient tokens)
- **Stakeholders:** Minda (CTO), Bhaskar (Clinical Lead), Tanya K (UI/UX), Ira (Frontend Dev)

## Implementation Uses

- Copy directly into `00-Brief.md` inside your project folder
- Onboard new teammates in < 5 minutes
- Evaluate scope creep during weekly check-ins

---

## 1. Objective

Deliver a clickable, browser-based avatar that can:

1. Greet patients, ask ASRS questions, and collect answers
2. Store responses in Firebase (anonymized IDs)
3. Hand off a PDF summary to the clinician's inbox

## 2. Success Criteria

| Metric | Target | Measurement Date |
|--------|--------|------------------|
| End-to-end latency | ≤ 2.5s per turn | Sept 5 smoke test |
| Demo stability | 3 consecutive 20-min sessions crash-free | Sept 10 rehearsal |
| Clinician NPS | ≥ +30 | Sept 12 pilot debrief |

## 3. Scope In / Out

| In Scope | Out of Scope |
|----------|--------------|
| Web app UI (desktop) | Mobile optimization |
| English voice + captions | Multilingual support |
| Basic data encryption | Full HIPAA BAA signing |

## 4. Stakeholders

| Name | Role | RACI | Preferred Channel |
|------|------|------|-------------------|
| **Minda** | CTO / PM | **A**ccountable | Slack #avatar-mvp |
| Bhaskar | Lead Clinician | **C**onsulted | Biweekly Zoom |
| Tanya K | UI/UX Designer | **R**esponsible | Figma comments |
| Ira | Front-end Dev | **R**esponsible | GitHub issues |
| Ken Chen | Adviser | **I**nformed | Monday recap email |

## 5. Milestones & Timeline

| Date | Milestone | Owner |
|------|-----------|-------|
| **Aug 4** | Kick-off & tech spike | Ira |
| **Aug 11** | Avatar demo v0.1 (static prompts) | Tanya K |
| **Aug 22** | Firebase integration complete | Ira |
| **Aug 29** | Usability test #1 (internal) | Minda |
| **Sept 5** | Feature freeze & load test | Ira |
| **Sept 12** | Clinician pilot demo | Minda |
| **Sept 15** | Post-mortem + archive | Team |

## 6. Dependencies & Risks

| Dependency/Risk | Mitigation Strategy |
|-----------------|---------------------|
| HeyGen API rate limits | Pre-cache avatar responses |
| Clinician availability | Secure backup pilot by Aug 15 |
| Latency spikes | Add CDN if p95 > 2.5s |

## 7. Budget Snapshot

| Line Item | Estimate | Notes |
|-----------|----------|-------|
| HeyGen credits | $450 | ~3 hrs video generation |
| Firebase Blaze tier | $60 | 3 months |
| Contingency (15%) | $80 | Misc expenses |
| **Total** | **$590** | |

## 8. Open Questions

1. Will the PDF summary require branding elements?
2. Do we need consent banners for demo data collection?
3. Should we capture voice recordings for later analysis?

---

## Post-Project

When the demo ships:

1. **Archive** this brief to `Archive/2025-09/Interactive-Avatar-MVP/00-Brief.md`
2. **Promote** reusable insights (e.g., HIPAA-lite pattern) to `Areas/Compliance/`
3. **Document** lessons learned in post-mortem
4. **Update** engineering standards based on what worked
