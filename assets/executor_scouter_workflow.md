# Executor Scouter Workflow - Claude in Chrome Integration

## Overview

This document describes how to use Claude in Chrome as your Executor Scouter (VECTOR DELTA) for autonomous partnership development.

---

## Setup Checklist

- [ ] Claude Pro or Max subscription active
- [ ] Claude in Chrome extension installed
- [ ] LinkedIn profile optimized
- [ ] Assets ready:
  - `linkedin_posts_ready.md` - 5 posts ready to publish
  - `target_contacts.md` - Investor/partner targets with templates
  - `.claude/SKILL.md` - Executor Scouter agent configuration

---

## Daily Workflow

### Morning Block (15 min)

1. **Open LinkedIn in Chrome**
2. **Open Claude sidebar** (click extension icon)
3. **Give context:**
   ```
   I'm Dre, founder of FREQ. Today I need to:
   - Post content about AI infrastructure
   - Send 5 connection requests to AI/maritime investors
   - Engage with 3 posts from target contacts

   My content is in my repo at assets/linkedin_posts_ready.md
   My targets are in assets/target_contacts.md

   Guide me through this efficiently.
   ```

4. **Claude sees your screen** and guides you step by step

---

## Specific Workflows

### Workflow 1: Publish LinkedIn Post

**You say:**
```
Help me publish today's LinkedIn post. It's [Monday/Tuesday/etc].
```

**Claude will:**
- Reference your posting schedule
- Tell you which post to use
- Guide you to the post composer
- Help you paste and publish

---

### Workflow 2: Send Connection Requests

**You say:**
```
I need to send connection requests to AI infrastructure VCs.
Help me find and connect with partners at a16z, Lux Capital, or Sequoia.
```

**Claude will:**
- Guide you to LinkedIn search
- Help you identify the right people
- Draft personalized connection notes
- Keep you within rate limits

---

### Workflow 3: Engage With Target Posts

**You say:**
```
Help me find recent posts from VCs investing in AI infrastructure
so I can leave thoughtful comments.
```

**Claude will:**
- Navigate to relevant profiles
- Find their recent posts
- Help you craft substantive comments (not "Great post!")

---

### Workflow 4: Follow Up on Connections

**You say:**
```
Check my recent connection accepts and help me send intro messages.
```

**Claude will:**
- Navigate to your network/connections
- Identify new accepts
- Draft personalized follow-up messages

---

## Workflow Recording (Automation)

Once you've done a workflow a few times, you can record it:

1. Click **"Record Workflow"** in Claude sidebar
2. Perform your actions (search → connect → message)
3. Stop recording
4. Name it: "Daily LinkedIn Outreach"
5. Claude can now repeat this on schedule

**Recommended recordings:**
- "Post Daily Content" - Navigate to post, paste from schedule, publish
- "Morning Connection Batch" - Search targets, send 5 requests
- "Engagement Round" - Find and comment on 3 posts

---

## Prompts Library

### Research a Person

```
I'm about to connect with [Name] at [Company].
Look at their profile and recent posts.
What should I mention in my connection request?
```

### Draft Outreach

```
Help me draft a message to [Name]. They're a [role] at [company].
I want to mention our Vertex AI work and multi-agent architecture.
Keep it under 300 characters.
```

### Find Warm Paths

```
I want to reach [Target Name] at [Company].
Help me find if I have any mutual connections who might intro me.
```

### Post Engagement

```
I just published a post about [topic].
Help me find 5 relevant people to tag or notify who might engage.
```

### Meeting Prep

```
I have a call with [Name] from [Company] tomorrow.
Help me research them - their background, company, recent news.
What questions should I prepare?
```

---

## Rate Limits (Stay Safe)

| Action | Daily Max | Per Hour |
|--------|-----------|----------|
| Connection requests | 10 | 3 |
| Messages | 25 | 8 |
| Comments | 15 | 5 |
| Posts | 2 | 1 |

Claude will help you track this. If you're approaching limits, it will warn you.

---

## Integration with Claude Code

While Claude in Chrome handles browser tasks, Claude Code (terminal) handles:
- Updating your asset files
- Research and analysis
- Code development on FREQ/SOL
- Strategy planning

**Unified workflow:**
1. Claude Code prepares content → saves to assets/
2. Claude Chrome helps you publish and execute
3. Results feed back into strategy

---

## Weekly Review

Every Friday, review with Claude:

```
Help me review this week's LinkedIn activity:
- How many connections did I send/accept?
- Which posts performed best?
- Any responses I need to follow up on?
- Who should I prioritize next week?
```

---

## Emergency Prompts

### If You're Stuck

```
I have 10 minutes. What's the highest-impact thing I can do
on LinkedIn right now for FREQ?
```

### If You're Overwhelmed

```
Prioritize my LinkedIn tasks. What are the top 3 things
that will move the needle this week?
```

### If You Need a Quick Win

```
Find me one person I should connect with today who's
actively investing in AI infrastructure.
```
