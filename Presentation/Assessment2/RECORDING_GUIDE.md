# Quick Reference: Assessment 2 - Live Discussion Preparation

**Format**: 60-Minute Live Technical Interview/Discussion
**Subject**: Trello Board Replication (Assessment 1)
**Preparation Time**: 30 minutes
**Discussion Time**: 60 minutes (3 segments)
**Script Reference**: [VIDEO_TRANSCRIPT.md](VIDEO_TRANSCRIPT.md)

---

## Overview

Assessment 2 is a **live technical discussion** where you present and defend your Trello Board Replication work from Assessment 1. This is NOT a recorded video - it's a live interview with interviewers asking questions.

**Three Segments**:
- **Segment 1** (25 min): Walkthrough & Detail Review
- **Segment 2** (20 min): Workflow & Velocity Discussion
- **Segment 3** (15 min): Scalability & Component Design

---

## Before the Discussion (30 Minutes Prior)

### Technical Setup Checklist

- [ ] **Application Running**: Frontend (port 3000) + Backend (port 5000)
- [ ] **Browser Tabs Ready**:
  - Tab 1: Your Trello app (localhost:3000)
  - Tab 2: Trello.com (for comparison)
  - Tab 3: Documentation (if needed)
- [ ] **Code Editor Open** with key files:
  - `src/components/Card/Card.tsx`
  - `src/hooks/useDragAndDrop.ts`
  - `src/store/boardSlice.ts`
  - `src/styles/Board.module.css`
- [ ] **Terminal Ready**: In project directory
- [ ] **Screen Sharing Tested**: Verify it works smoothly
- [ ] **Audio/Video Tested**: Microphone and camera working

### Documentation Ready

- [ ] [VIDEO_TRANSCRIPT.md](VIDEO_TRANSCRIPT.md) - Review all segments
- [ ] [WORKFLOW_EFFICIENCY_REPORT.md](../Assessment1/WORKFLOW_EFFICIENCY_REPORT.md) - Have open for reference
- [ ] [IMPLEMENTATION_DETAILS.md](../Assessment1/IMPLEMENTATION_DETAILS.md) - Quick reference

### Environment Setup

- [ ] Close unnecessary applications
- [ ] Silence all notifications (Slack, email, etc.)
- [ ] Clean desktop (hide personal files)
- [ ] Set browser zoom to 100-125% (comfortable viewing)
- [ ] Increase terminal font size (easier to see when sharing)
- [ ] Water/coffee nearby
- [ ] Good lighting (if video call)

---

## Segment 1: Walkthrough & Detail Review (25 minutes)

### What to Prepare

**Live Demo Features**:
1. Board interface with horizontal scrolling
2. Create/edit lists
3. Create cards with inline editing
4. **Drag-and-drop** between lists (main feature!)
5. Card detail modal with all interactions
6. Error handling demonstration (simulate network failure)

**Code to Discuss**:
- CSS challenges solved (horizontal scroll, z-index, drag feedback)
- Drag-and-drop implementation (state management)
- Redux/Zustand normalized state structure
- Edge case handling

### Key Talking Points

- **Opening (2 min)**: Project overview, 4-hour timeline, 10/10 score
- **Live Demo (5 min)**: Show all features working smoothly
- **CSS Challenges (5 min)**: Explain 4 major CSS problems solved
- **Drag-and-Drop (5 min)**: Deep dive into implementation
- **State Management (5 min)**: Normalized Redux structure
- **Edge Cases (3 min)**: How you handled errors and edge cases

### Tips for This Segment

✅ **Do**:
- Start with live demo immediately (show, don't just tell)
- Have code files ready to show specific examples
- Explain "why" not just "what" for technical decisions
- Be ready to navigate to any file quickly
- Demonstrate actual interactions (drag cards, open modals)

❌ **Don't**:
- Spend too long on any one topic (watch time)
- Read code line-by-line (highlight key parts)
- Get lost in details (stay high-level with code examples)

---

## Segment 2: Workflow & Velocity Discussion (20 minutes)

### What to Prepare

**AI Tools Usage**:
- GitHub Copilot: Specific examples of boilerplate generated
- ChatGPT/Claude: Algorithm help, debugging assistance
- Quantified time savings (45 minutes from AI tools)

**Efficiency Methods**:
- Design token extraction script
- Mock-first development approach
- Screenshot-driven development
- Copy-paste-modify technique
- "Good enough" backend

**Time Savings Breakdown**:
- Total time saved: 315 minutes (52%)
- Breakdown by method (have numbers ready)

### Key Talking Points

- **AI Development (5 min)**: Copilot examples, Claude assistance
- **Design Tokens (5 min)**: Extraction method, pixel-perfect accuracy
- **Mock-First (5 min)**: How it parallelized work
- **Non-Conventional (5 min)**: Screenshot-driven, copy-paste-modify, etc.

### Tips for This Segment

✅ **Do**:
- Provide specific examples with code snippets
- Quantify everything (45 min saved, 80% auto-generated, etc.)
- Show enthusiasm for efficiency techniques
- Admit what you'd do differently
- Reference WORKFLOW_EFFICIENCY_REPORT.md

❌ **Don't**:
- Claim AI did everything (you made decisions)
- Be vague ("it was helpful" → "saved 45 minutes on boilerplate")
- Forget to mention tradeoffs

---

## Segment 3: Scalability & Component Design (15 minutes)

### What to Prepare

**Production Evolution Topics**:
- Real-time collaboration (WebSockets + OT)
- Database migration (JSON → PostgreSQL)
- API design (REST → GraphQL)
- Performance optimization (virtualization, memoization)
- Security (auth, rate limiting)
- Testing infrastructure

**Architecture Proposals**:
- Have mental model of production architecture
- Understand tradeoffs (complexity vs features)
- Know realistic timelines (6-8 weeks)

### Key Talking Points

- **Real-Time Collab (5 min)**: WebSocket implementation, conflict resolution
- **Database/API (5 min)**: PostgreSQL schema, GraphQL benefits
- **Performance/Scale (5 min)**: Virtualization, caching, query optimization

### Tips for This Segment

✅ **Do**:
- Think holistically (end-to-end)
- Mention security considerations
- Be realistic about timelines
- Show systems thinking
- Provide specific technical solutions

❌ **Don't**:
- Overpromise ("easy to scale")
- Ignore security or testing
- Be too vague ("just use Kubernetes")

---

## Time Management

### If Running Over Time

**Can Shorten**:
- Code walkthrough details (show less code)
- Mock-first explanation (brief mention)
- Database schema details (high-level)

**Must Cover**:
- Live demo of drag-and-drop
- AI tool usage with examples
- Time savings quantification
- Production evolution path
- Security considerations

### Time Checkpoints

- **25 min mark**: Should be starting Segment 2
- **45 min mark**: Should be starting Segment 3
- **55 min mark**: Start wrapping up
- **60 min mark**: Finish with time for questions

---

## Speaking Tips

### General Presentation

✅ **Do**:
- Speak clearly and confidently
- Pause briefly between topics
- Ask "Does that make sense?" periodically
- Take a breath if you need to collect thoughts
- Show enthusiasm for the work
- Make eye contact (if video call)

❌ **Don't**:
- Rush through explanations
- Speak in monotone
- Say "um" or "like" excessively (pause instead)
- Read directly from notes
- Get defensive about choices
- Forget to breathe!

### Answering Questions

✅ **Do**:
- Listen carefully to the full question
- Clarify if you're unsure what they're asking
- Structure your answer (First..., Second..., Finally...)
- Provide concrete examples
- Admit if you don't know something

❌ **Don't**:
- Interrupt the interviewer
- Give vague answers
- Make up information
- Ignore the question asked

---

## Common Questions to Prepare

### Segment 1 Questions

- "Why did you choose Redux over Context/Zustand?"
- "How would you handle this specific edge case?"
- "What was the most challenging CSS problem?"
- "Walk me through your drag-and-drop state management."
- "How did you ensure pixel-perfect accuracy?"

### Segment 2 Questions

- "How specifically did Copilot save you time?"
- "Can you quantify the time savings more precisely?"
- "What would you do differently with more time?"
- "How do you balance speed with code quality?"
- "What was the most effective efficiency method?"

### Segment 3 Questions

- "How would you handle 10,000+ cards?"
- "What security considerations are most important?"
- "How would multiple users collaborate in real-time?"
- "What's your testing strategy for production?"
- "What's the biggest risk in scaling this?"

---

## Technical Demo Preparation

### Before Starting

**Test Everything**:
```bash
# Start backend
cd server && npm start

# Start frontend (in new terminal)
npm run dev

# Verify both running
curl http://localhost:5000/api/health  # Backend
curl http://localhost:3000              # Frontend
```

**Practice Scenarios**:
1. Create new list → works
2. Create card in list → works
3. Drag card between lists → smooth
4. Open card modal → opens/closes
5. Edit card title → saves
6. Simulate network error → shows error, rolls back

### Font Sizes for Sharing

Increase visibility:
- **Terminal**: 16-18pt font
- **VS Code**: 14-16pt font
- **Browser**: 125% zoom

---

## If Something Goes Wrong

### Application Issues

**App crashes**:
- "Let me restart that quickly..." (restart server)
- Have backup: Show code instead of demo

**Drag-and-drop glitches**:
- "Let me refresh..." (F5)
- Explain what should happen while fixing

**Network errors**:
- Perfect opportunity to show error handling!
- "Actually, this demonstrates our rollback feature..."

### Technical Issues

**Screen sharing fails**:
- "One moment, reconnecting..." (stay calm)
- Have phone as backup to show screen

**Audio issues**:
- Type in chat that you'll fix audio
- Mute/unmute, check settings quickly

**Lost train of thought**:
- "Let me revisit that..." (it's okay)
- Refer to VIDEO_TRANSCRIPT.md

---

## Opening Script (Memorize This)

> "Thank you for having me today. I'm excited to walk through my Trello Board Replication project from Assessment 1.
>
> As a quick overview: I built a pixel-perfect replication of Trello's board interface in exactly 4 hours, including full drag-and-drop functionality, complete CRUD operations, and a REST API backend. I achieved what I believe is a 10/10 score across all evaluation criteria.
>
> I saved 315 minutes through systematic efficiency methods - that's a 52% time reduction - using AI tools, design token extraction, and mock-first development.
>
> Today I'll walk through three main areas: first, the technical implementation with a live demo; second, my workflow efficiency methods; and third, how this would scale to production.
>
> Shall I start with the live demo?"

---

## Closing Script (Memorize This)

> "To summarize, this project demonstrates three key things:
>
> First, velocity without compromise - pixel-perfect quality in 4 hours through smart tooling.
>
> Second, tool maximalism - strategic use of AI, automation, and modern development practices.
>
> Third, production thinking - this prototype has a clear evolution path to a scalable, secure system.
>
> The code is production-ready, well-documented, and demonstrates the rapid prototyping skills needed for this role.
>
> I'm happy to answer any questions or dive deeper into any aspect. Thank you!"

---

## Final Checklist

**Technical Ready**:
- [ ] App running (frontend + backend)
- [ ] Screen sharing works
- [ ] Audio/video tested
- [ ] Code editor open with files ready
- [ ] Terminal ready with increased font

**Documentation Ready**:
- [ ] VIDEO_TRANSCRIPT.md reviewed
- [ ] WORKFLOW_EFFICIENCY_REPORT.md available
- [ ] Key talking points memorized

**Environment Ready**:
- [ ] Notifications silenced
- [ ] Clean desktop
- [ ] Good lighting/audio
- [ ] Water nearby
- [ ] Calm and confident!

**Mental Ready**:
- [ ] Reviewed all 3 segments
- [ ] Practiced demo
- [ ] Know your time savings numbers
- [ ] Understand tradeoffs made
- [ ] Ready for questions

---

## Emergency Contacts

**If you have last-minute questions**:
- Review VIDEO_TRANSCRIPT.md (complete Q&A)
- Check README.md for evaluation criteria
- Look at SUBMISSION.md for preparation tips

---

## Remember

This is a **conversation**, not a presentation. The interviewers want to understand:
- Your technical depth
- Your efficiency mindset
- Your judgment
- Your systems thinking

Be yourself, be confident, and show your passion for building things quickly and well.

**You've got this! 🚀**

---

**Last Updated**: February 21, 2026
**Discussion Duration**: 60 minutes
**Format**: Live technical interview with Q&A
