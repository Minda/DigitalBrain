# Per-Video Agent Prompt Template

Template for the Task agent launched for each individual YouTube video.
The orchestrator fills in [PLACEHOLDERS] before injecting.

---

## Agent Instructions

[CALIBRATION_PROMPT injected from agents-spinning-up/references/calibration-prompt.md]

---

Fetch the YouTube transcript for this video and create a thorough summary:

**Video URL:** [VIDEO_URL]

Use the youtube-fetching-transcripts skill to fetch the transcript. Then read the full transcript that was saved.

After reading the transcript, produce a structured summary with these sections:

### 1. Video Title and Topic
What is this video about? Who is speaking? What format (talk, interview, lecture, panel)?

### 2. Key Takeaways (3-7 bullet points)
The most important points, ideas, or arguments. Be specific, not vague.

### 3. Surprising or Non-Obvious Information
Things that would catch an informed viewer off guard. Counter-intuitive claims. Lesser-known facts. If nothing is genuinely surprising, say so.

### 4. Practical Implications
What should someone DO differently after watching this? If nothing actionable, say that too.

### 5. Notable Quotes or Moments
Specific memorable statements (paraphrase if needed, with approximate timestamps when available).

### 6. Critical Assessment
Where is the speaker wrong, speculative, or overselling? What are the weak arguments? What evidence is missing? If the video is solid, say what makes it solid specifically.

---

## Quality Standards

- State what the video actually says, including where the speaker is wrong or speculative.
- If the video contains weak arguments, hype, or unsupported claims, say so directly.
- No content-free approval signals ("That's a great point").
- No hyperbolic frames ("This changes everything").
- Answer what the video IS about, not what it's adjacent to.
- If the speaker contradicts themselves, flag it.
- Plain English. Short sentences. No em dashes.

Return the full structured summary as your output. Include the video URL at the top.
