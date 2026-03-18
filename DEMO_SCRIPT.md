# Pfula Demo Script — Data & AI Community Day Durban
## "AI Unplugged" | 14 March 2026 | Presenter: Lawrance Reddy

---

## SECTION 1: FULL DEMO NARRATIVE SCRIPT

**Total time: ~22 minutes**

---

### 1. OPENING HOOK (2 minutes)

[LIGHTS UP — STAND CENTRE STAGE, NO SLIDES YET]

Good morning, everyone. Before I show you a single line of code, I want to tell you a story.

[PAUSE — LET THE ROOM SETTLE]

Imagine you're a single mother in Umlazi. You have two children. You lost your job three months ago. You've been surviving on piece work — washing, ironing, whatever comes.

You heard about the SRD grant. Three hundred and seventy rand a month. It's not much, but it's the difference between your children eating or not eating.

So you wake up at 4am. You take a taxi to the SASSA office. You wait in a queue for five hours. You finally get to the counter. And the official looks at your documents and says...

[PAUSE]

"Come back tomorrow. You're missing a form."

[PAUSE]

You don't know which form. You don't know where to get it. You've just spent R40 on taxi fare you couldn't afford. And now you have to do it all again.

[CLICK — FIRST SLIDE: "What if it didn't have to be this way?"]

This is not an edge case. This is not an exaggeration. This is Tuesday in South Africa.

And today, I want to show you what happens when we point AI at this problem. Not AI for Silicon Valley. Not AI for enterprise dashboards. AI for the person in that queue.

[CLICK — SLIDE: "Pfula" with tagline]

---

### 2. THE PROBLEM AT SCALE (2 minutes)

[CLICK — STATISTICS SLIDE]

Let me give you some numbers.

South Africa has roughly 28 million people who interact with government services regularly. SASSA alone processes over 18 million grants. Home Affairs handles millions of ID applications, births, deaths, marriages every year. SARS processes over 7 million individual tax returns.

Now here's the painful part.

The average South African spends 3 to 5 hours per government visit. Many need multiple visits for a single service. A survey found that 40% of people visiting government offices are turned away on their first attempt — wrong documents, wrong queue, wrong day.

[CLICK — COST SLIDE]

Think about the cost. Not just the government's cost — the citizen's cost. Taxi fare. A day's wages lost. Airtime spent calling hotlines that don't answer. Data spent searching websites that were last updated in 2019.

And here's what breaks my heart — the people who need these services the most are the people who can least afford to get it wrong.

[PAUSE]

So. What do we do about it?

---

### 3. INTRODUCING PFULA (2 minutes)

[CLICK — PFULA INTRO SLIDE]

We build Pfula.

Pfula is a Tshivenda word. It means "to open." To unlock. To make accessible.

Pfula is an AI civic assistant built specifically for South Africans. It knows our government services. It knows our forms. It knows our legislation. It knows our languages.

[CLICK — FEATURE LIST]

What if every South African had a personal government navigator in their pocket? Someone who never gets tired. Never says "come back tomorrow." Never sends you to the wrong queue. Someone who knows the difference between a BI-9 and a DHA-9. Someone who can tell you exactly what documents you need, what your rights are, and what to do when things go wrong.

That's Pfula.

It's not a chatbot. It's not a search engine wrapper. It's a purpose-built civic assistant powered by Claude, grounded in verified South African government knowledge, and designed to serve the people who need it most.

[CLICK]

Let me show you how we built it.

---

### 4. ARCHITECTURE WALKTHROUGH (3 minutes)

[CLICK — ARCHITECTURE DIAGRAM SLIDE]

Alright, let's talk tech. This is a community of builders, so let's look under the hood.

[CLICK — FRONTEND]

The frontend is React with TypeScript. Nothing exotic — but it's responsive, it's accessible, and it streams responses in real time via WebSockets. When you ask Pfula a question, you don't wait for the full answer. You see it thinking. You see it writing. That matters — because when someone is stressed about their grant, watching a loading spinner for 15 seconds feels like an eternity.

[CLICK — BACKEND]

The backend is Node.js with Express. It handles session management, conversation history, and the critical piece — knowledge injection.

[CLICK — AI LAYER]

Now here's where it gets interesting. We use Anthropic's Claude API. But — and this is important — we do NOT use naive RAG.

[PAUSE — LET THAT LAND]

I know RAG is the buzzword. Retrieve, augment, generate. And it works great for many use cases. But when someone asks about their legal rights, or how much tax they owe, or whether they qualify for a grant — I don't want a model retrieving fragments from a vector database and hoping for the best. I don't want hallucinated legislation. I don't want approximate eligibility criteria.

[CLICK — KNOWLEDGE BASE APPROACH]

Instead, we use curated, structured, verified knowledge bases. Every fact in Pfula has been researched. Every threshold, every form number, every piece of legislation — verified against official sources. The knowledge is injected as structured context, not retrieved from embeddings. The model's job is to be empathetic, conversational, and helpful — but the facts come from us.

[CLICK — DEPLOYMENT]

Deployment is Azure App Service, automated via GitHub Actions with OIDC authentication. No secrets stored in the repo. Push to main, it deploys. Clean, secure, repeatable.

---

### 5. KNOWLEDGE BASE DEEP DIVE (2 minutes)

[CLICK — KNOWLEDGE BASE SLIDE]

Let me tell you what's actually in this thing.

Pfula currently covers 7 government service areas:

[CLICK — LIST BUILDS]

1. **SASSA** — All social grants. SRD, child support, old age, disability. Means tests, application processes, appeal procedures, payment methods.

2. **Home Affairs** — Smart IDs, passports, birth certificates, marriages, death certificates. Timelines, costs, required documents, what to do when things go wrong.

3. **SARS** — Individual tax. Brackets, rebates, medical tax credits, retirement annuity deductions, provisional tax, penalties.

4. **UIF** — Unemployment insurance. Claims, maternity benefits, illness benefits. The UI-19 nightmare. What happens when your employer didn't register you.

5. **Municipal Services** — Water, electricity, rates, refuse. Indigent support. What to do about disconnections. Your rights under the Municipal Systems Act.

6. **CIPC** — Company registration, annual returns, deregistration, re-instatement. BEE compliance.

7. **Public Protector & Legal Rights** — PAJA, PAIA, constitutional rights, how to escalate, how to complain formally.

[CLICK — WORD COUNT]

Combined, that's over 52,000 words of verified content. Real form numbers. Real phone numbers. Real legislation references. Real appeal processes.

This is not a generic chatbot that says "please visit your nearest office." This is a system that says "you need form DHA-9, here's what to fill in on section 3, and here's the number to call if they give you trouble."

[PAUSE]

Now. Enough slides. Let me show you the real thing.

---

### 6. LIVE DEMO (8-10 minutes)

[SWITCH TO LIVE DEMO — BROWSER OPEN TO PFULA]

[TAKE A BREATH — SMILE]

Alright. Let's talk to Pfula.

---

#### Demo 6a: SASSA Grant Rejection (2 min)

[TYPE THE QUESTION — READ IT ALOUD AS YOU TYPE]

I'm going to start with something that happens every single day across this country.

**Type:** "My SASSA SRD grant was rejected and I don't understand why. I'm unemployed and have no income. The status just says 'declined'. What can I do?"

[WAIT FOR RESPONSE TO STREAM]

[AS IT STREAMS, NARRATE:]

Watch what happens here. It's not just giving a generic answer. Look — it's explaining the specific reasons SRD grants get declined. It's giving the actual appeal process. It's mentioning the specific timeframes. It's giving the SASSA contact details.

And notice the tone. It's not cold. It's not bureaucratic. It starts with empathy. Because the person asking this question is scared. They need to know someone understands.

[PAUSE — LET AUDIENCE READ]

That right there — that response — would have saved our mother from Umlazi an entire wasted trip.

---

#### Demo 6b: Home Affairs Delay (1.5 min)

[TYPE NEXT QUESTION]

Now let's try something everyone in this room has probably experienced.

**Type:** "I applied for my Smart ID at Durban Home Affairs 4 months ago. They said 6-8 weeks. Nobody answers the phone. What are my realistic options?"

[WAIT FOR RESPONSE]

[NARRATE:]

Look at this. It knows the realistic timelines — not the official ones, the real ones. It's suggesting bank branch alternatives for collection. It's giving tracking steps. It even mentions the online tracking portal.

This is institutional knowledge. The kind of thing you only learn after three visits and a lot of frustration. Pfula gives it to you upfront.

---

#### Demo 6c: IsiZulu Query (1.5 min)

[PAUSE — LOOK AT AUDIENCE]

Now. We're in Durban. So let me ask something in isiZulu.

**Type:** "Ngifuna ukwazi ukuthi ngingayithola kanjani imali yesibonelelo sikahulumeni sokondla ingane yami. Ngineminyaka engu-25 futhi ngingasebenzi."

[WAIT FOR RESPONSE]

[NARRATE:]

Look at that. It understood the isiZulu query. And watch — it's responding with a mix, making it accessible. It understands the context: a 25-year-old unemployed person asking about the child support grant. And it gives the full, accurate answer — the same quality as the English queries.

This is what accessibility looks like. Not just a translate button. Real understanding.

---

#### Demo 6d: Escalation Letter (2 min)

[TYPE NEXT QUESTION]

Now here's where it gets powerful. Sometimes being informed isn't enough. Sometimes you need to take action.

**Type:** "My disability grant application was rejected without any written reasons. I want to demand written reasons under PAJA. Can you help me write a formal letter?"

[WAIT FOR RESPONSE — THIS ONE WILL BE LONGER]

[NARRATE AS IT STREAMS:]

Watch this carefully. It's generating a formal letter. Look — it's citing the Promotion of Administrative Justice Act. It's citing the specific sections. It's giving the correct timeframe the department must respond in. It's structuring it as a proper legal demand.

[PAUSE]

A lawyer would charge you R2,000 for this letter. Pfula just wrote it in 10 seconds.

[LET THAT LAND]

---

#### Demo 6e: Dashboard (1 min)

[CLICK — NAVIGATE TO DASHBOARD]

Now let me show you something else. Every interaction Pfula has generates data. And data tells a story.

[WALK THROUGH DASHBOARD]

Here's our analytics dashboard. You can see query volumes, which services are most asked about, response times, user satisfaction.

Now imagine this at scale. Imagine the Department of Home Affairs could see, in real time, that 40% of queries this week are about Smart ID delays in KZN. That's not just a chatbot metric — that's a service delivery signal. That's accountability data.

---

#### Demo 6f: Case Tracker (1 min)

[CLICK — NAVIGATE TO CASE TRACKER]

And finally — the case tracker. Because sometimes a conversation isn't enough. Sometimes you need to track an ongoing issue.

[WALK THROUGH CASE TRACKER]

Users can log cases, track status, set follow-up dates. It creates accountability. It creates a paper trail. It means when you phone that SASSA office for the fifth time, you have a record of every previous interaction.

[PAUSE]

This is the full picture. Information. Action. Accountability.

[SWITCH BACK TO SLIDES]

---

### 7. IMPACT & VISION (2 minutes)

[CLICK — IMPACT SLIDE]

Let me talk about what this could mean at scale.

[CLICK — COST COMPARISON]

A single government office visit costs the average citizen between R80 and R200 when you factor in transport, lost income, and incidentals. A Pfula interaction costs fractions of a cent in API calls.

If we could prevent even 10% of unnecessary government visits — just the ones where people are turned away for wrong documents or wrong information — we're talking about saving millions of rand. More importantly, we're saving millions of hours. Hours that a mother could spend with her children. Hours that a job seeker could spend looking for work.

[CLICK — VISION SLIDE]

The vision is bigger than a web app.

Phase 2: WhatsApp integration. Because 95% of South African smartphone users are on WhatsApp. You shouldn't need a web browser to access your rights.

Phase 3: All 11 official languages. Full, native support. Not translation — understanding.

Phase 4: Voice input. Because literacy shouldn't be a barrier to accessing government services.

Phase 5: Offline capability. Pre-loaded knowledge for areas with limited connectivity.

[CLICK]

And here's the thing — the AI is the easy part. Claude is extraordinary. The hard part is the knowledge. The curation. The verification. The understanding of how government actually works on the ground, not how it works in policy documents.

That's the moat. That's the value.

---

### 8. CLOSE (1 minute)

[CLICK — FINAL SLIDE: "Pfula — To Open"]

[STEP FORWARD — NO PODIUM — DIRECT TO AUDIENCE]

Pfula means "to open."

Today we've opened a door. We've shown that AI can be more than enterprise tooling and productivity hacks. It can be a bridge between a government and its people. It can be the translator between bureaucracy and humanity.

[PAUSE]

But a door is only useful if people walk through it.

So here's my ask. If you're a developer — the code is there. Contribute. If you're in government — let's talk about deployment. If you're in this room and you've ever waited in a queue that broke your spirit — help me make sure nobody else has to.

[PAUSE]

The question isn't whether AI can help South Africans navigate their government. We just proved it can.

The question is — who walks through this door with us?

[PAUSE]

Thank you.

[HOLD — DON'T RUSH OFF — LET THE APPLAUSE COME]

---

## SECTION 2: KILLER DEMO QUESTIONS

### How to use this section
Each question below is designed to showcase a specific capability of Pfula. They are ordered for maximum dramatic effect if used sequentially, but any can be used standalone. For each question, you'll find:
- **Question** — Exactly what to type (copy-paste ready)
- **Why it's impressive** — What the audience will notice
- **Knowledge area tested** — Which part of the knowledge base is activated

---

### EMOTIONAL / HUMAN STORIES

These questions show that Pfula doesn't just retrieve information — it understands the human behind the question.

---

**Question 1: The grandmother whose pension stopped**

**Type:**
```
My grandmother is 68 years old and her SASSA old age pension just stopped with no warning. She depends on it completely. She can't walk well and can't easily get to the SASSA office. What should we do?
```

**Why it's impressive:** The response should demonstrate empathy first, then provide a step-by-step action plan that accounts for the grandmother's mobility issues. It should mention the SASSA toll-free line, the option to send an authorised representative, and the specific documents needed to resolve a suspended pension. The audience will feel the human-centred design.

**Knowledge area tested:** SASSA — Old Age Pension, suspension/reinstatement procedures, accessibility accommodations.

---

**Question 2: The young person denied their first ID**

**Type:**
```
I'm 16 and I went to Home Affairs to get my first ID but they said there's a problem with my birth certificate. My mom passed away and I don't have her documents. I'm living with my aunt. What can I do?
```

**Why it's impressive:** This is a complex, emotionally sensitive scenario involving a minor, a deceased parent, and guardianship issues. The response should handle the emotional context with care while providing practical guidance about late registration of birth, the role of the aunt as guardian, required affidavits, and the specific Home Affairs processes for resolving birth certificate discrepancies.

**Knowledge area tested:** Home Affairs — ID applications, birth certificate issues, guardianship documentation.

---

**Question 3: The retrenched worker without a UI-19**

**Type:**
```
I was retrenched 2 months ago. My company closed down completely and I can't get my UI-19 form from them because the offices are locked. I need to claim UIF but they say I can't without the UI-19. I have a family to feed. Please help.
```

**Why it's impressive:** This is a notorious real-world problem. The response should know that there are alternatives to the UI-19 when an employer has closed — including the option to submit a sworn affidavit, approach the UIF directly with proof of employment (payslips, bank statements), and involve the CCMA if needed. Most people don't know these alternatives exist.

**Knowledge area tested:** UIF — Claims process, employer non-compliance, alternative documentation, CCMA involvement.

---

### TECHNICAL / COMPLEX

These questions prove Pfula has deep, accurate, calculation-ready knowledge — not vague summaries.

---

**Question 4: SASSA means test specifics**

**Type:**
```
I earn about R2,500 per month from piece jobs — it's not regular work. I also receive R800 child maintenance from my ex. Do I qualify for the SRD R370 grant? Does the maintenance count as income?
```

**Why it's impressive:** This tests whether Pfula understands the nuances of the SRD means test. The maintenance income question is a real grey area that confuses applicants. The response should explain the income threshold, how irregular income is assessed, and whether maintenance is counted — demonstrating genuine depth, not surface-level knowledge.

**Knowledge area tested:** SASSA — SRD grant, means testing, income definitions, eligibility criteria.

---

**Question 5: Tax calculation**

**Type:**
```
I earn R320,000 per year before tax. I contribute R2,000 per month to my retirement annuity and I'm on a medical aid with 3 dependants (me, my wife, and our child). I'm 34 years old. Can you estimate my annual tax and monthly take-home?
```

**Why it's impressive:** This requires actual calculation using the SARS tax brackets, the retirement annuity deduction rules (subject to limits), and the medical tax credit formula for 3 dependants. If Pfula can walk through this step by step with accurate numbers, it demonstrates a level of practical utility that a generic AI simply cannot match.

**Knowledge area tested:** SARS — Tax brackets, retirement annuity deductions (section 11F limits), medical tax credits, rebates.

---

**Question 6: Property transfer**

**Type:**
```
I'm buying my first home for R1.8 million in Durban. What transfer duty will I pay? What are the approximate conveyancing fees? And how long does the transfer process usually take?
```

**Why it's impressive:** This tests knowledge of the transfer duty sliding scale, typical conveyancing fee ranges, and realistic transfer timelines. The first-time buyer mention may trigger additional relevant information about any applicable exemptions or programs. The audience — many of whom will be property owners — will immediately verify the accuracy in their heads.

**Knowledge area tested:** SARS — Transfer duty, property transactions, conveyancing.

---

### ESCALATION / RIGHTS

These questions show that Pfula isn't just informational — it empowers people to assert their legal rights.

---

**Question 7: PAJA written reasons demand**

**Type:**
```
SASSA rejected my disability grant application but they didn't give me any reasons. I believe I have a right to written reasons for their decision. Can you explain my rights under PAJA and help me draft a formal request for written reasons?
```

**Why it's impressive:** The response should correctly cite the Promotion of Administrative Justice Act (Act 3 of 2000), specifically the right to written reasons under section 5. It should explain the 90-day request window, the 90-day response requirement, and generate a usable template letter. This demonstrates Pfula's legal knowledge depth.

**Knowledge area tested:** Public Protector & Legal Rights — PAJA, administrative justice, formal correspondence generation.

---

**Question 8: Public Protector complaint**

**Type:**
```
I've been trying to get my late father's estate finalised through the Master of the High Court for over 2 years. They keep losing documents and nobody returns my calls. I want to file a formal complaint with the Public Protector. Can you help me write it?
```

**Why it's impressive:** This requires knowledge of the Public Protector's jurisdiction, the complaint process, and the ability to generate a structured formal complaint. The Master of the High Court scenario is common and relatable. The response should include practical details like the Public Protector's contact information, what to include in the complaint, and what supporting documents to attach.

**Knowledge area tested:** Public Protector & Legal Rights — Complaint procedures, jurisdiction, formal correspondence.

---

**Question 9: Emergency municipal disconnection**

**Type:**
```
The municipality cut off my water yesterday without any notice. I have two young children at home. Is this legal? What are my immediate rights and what can I do right now?
```

**Why it's impressive:** This is an emergency scenario. The response should know that disconnection without notice may be unlawful under the Water Services Act and the Municipal Systems Act, that there are protections for households with children, and it should provide immediate practical steps (not just legal theory). The urgency and the children element should trigger a response that prioritises immediate action.

**Knowledge area tested:** Municipal Services — Water disconnection, notice requirements, constitutional right to water, emergency procedures.

---

### MULTILINGUAL

These questions demonstrate that Pfula serves all South Africans, not just English speakers.

---

**Question 10: IsiZulu — SASSA query**

**Type:**
```
Sawubona, ngicela usizo. Umama wami uneminyaka engu-62 futhi akasebenzi. Singayithola kanjani imali yesibonelelo sabadala ku-SASSA? Yimaphi amaphepha esiwadingayo?
```

**Translation:** "Hello, I need help. My mother is 62 and unemployed. How can we get the old age grant from SASSA? What documents do we need?"

**Why it's impressive:** The query is in natural isiZulu. The response should demonstrate comprehension of the specific question (old age grant, age 62, documents needed) and provide accurate, detailed information. The age detail is important — 62 is below the current qualifying age for women (60) — wait, actually 62 qualifies. The response should confirm eligibility and list required documents.

**Knowledge area tested:** SASSA — Old Age Pension, eligibility, required documentation. Multilingual capability.

---

**Question 11: IsiZulu — Home Affairs query**

**Type:**
```
Ngifuna ukushintsha isibongo sami emva komshado. Ngenzenjani futhi kubiza malini e-Home Affairs?
```

**Translation:** "I want to change my surname after marriage. What do I do and how much does it cost at Home Affairs?"

**Why it's impressive:** A practical, everyday question in isiZulu. The response should cover the surname change process after marriage, required documents (marriage certificate, current ID), the HA-9 form, applicable fees, and expected timelines. Demonstrating this in isiZulu shows genuine linguistic capability, not just English-with-translation.

**Knowledge area tested:** Home Affairs — Surname change, marriage-related amendments, forms, fees. Multilingual capability.

---

### EDGE CASES

These questions test Pfula's ability to handle unusual, complex, real-world scenarios that generic chatbots would fumble.

---

**Question 12: Unregistered domestic worker**

**Type:**
```
I worked as a domestic worker for 5 years but my employer never registered me for UIF. Now I've been let go and I have nothing. Is there anything I can do? Can I still claim?
```

**Why it's impressive:** This is a tragically common situation in South Africa. The response should explain that the employer was legally obligated to register and contribute, that the worker can report the employer to the Department of Labour, that there may be options through the CCMA for compensation, and outline the practical steps. It should not simply say "you can't claim" — it should open doors.

**Knowledge area tested:** UIF — Employer obligations, non-compliance, domestic worker protections, CCMA recourse, Department of Labour complaints.

---

**Question 13: Deregistered company while overseas**

**Type:**
```
My company was deregistered by CIPC while I was working overseas for 2 years. I missed the annual return filings. The company has assets and contracts. How do I get it reinstated?
```

**Why it's impressive:** This is a specific CIPC scenario requiring knowledge of the re-instatement process, the difference between voluntary and involuntary deregistration, the application procedure, required documents, fees, and the implications for existing assets and contracts during the deregistered period. Most people assume a deregistered company is gone forever — Pfula should know better.

**Knowledge area tested:** CIPC — Deregistration, re-instatement process (section 82 of the Companies Act), annual returns, compliance.

---

**Question 14: Identity theft — company registered in your name**

**Type:**
```
I just discovered that someone used my ID number to register a company with CIPC without my knowledge. I'm worried about tax implications and liability. What do I do?
```

**Why it's impressive:** This is an identity theft scenario that crosses multiple domains — CIPC, SARS, and potentially SAPS. The response should provide a multi-step action plan: report to SAPS, file a complaint with CIPC, check SARS for any tax implications, consider the Companies Tribunal, and suggest identity protection steps. The cross-domain knowledge is what makes this impressive.

**Knowledge area tested:** CIPC — Fraudulent registration, complaints process. Cross-reference with SARS implications and legal rights.

---

### THE SHOWSTOPPER

Save this for last. This is the mic-drop moment.

---

**Question 15: Full formal escalation letter**

**Type:**
```
I've been waiting 10 months for my Smart ID card from Durban Home Affairs. I've visited 4 times and called dozens of times. Nobody can tell me what happened to my application. I need a formal escalation letter citing my constitutional rights and relevant legislation. My name is Thandi Nkosi, ID number 8501015009081, reference number DUR-2025-44891.
```

**Why it's impressive:** This is the grand finale. Pfula should generate a complete, formal escalation letter addressed to the Department of Home Affairs. It should include:
- Proper letter formatting with date, reference numbers, and addressee
- The applicant's personal details as provided
- A clear chronology of the complaint (10 months, 4 visits, multiple calls)
- Citation of constitutional rights (Section 195 of the Constitution — public administration values)
- Reference to the Promotion of Administrative Justice Act (PAJA)
- Reference to the Batho Pele principles
- A clear demand with a reasonable deadline for response
- Mention of further escalation options (Public Protector, legal action)
- Professional, assertive tone

When this letter appears on screen, fully formatted, citing real legislation, with the person's actual details filled in — the audience will understand. This isn't a toy. This is a tool that gives ordinary South Africans the power that used to be reserved for people who could afford attorneys.

**Knowledge area tested:** Home Affairs — Smart ID timelines, escalation procedures. Public Protector & Legal Rights — Constitutional rights, PAJA, Batho Pele, formal correspondence generation. Full integration test.

---

### DEMO TIPS

- **Pace yourself.** Let responses stream. Don't talk over them.
- **Read key parts aloud.** The audience in the back can't read the screen. Highlight the most impressive parts verbally.
- **React naturally.** If something surprising comes out, acknowledge it. "I didn't even prompt it to include that section reference — it just knows."
- **Have a backup.** If the network drops or the API is slow, have screenshots of previous responses ready.
- **End with Question 15.** Always. The letter is the emotional and technical climax. Let it land. Let the room read it. Then close.

---

*"Pfula — to open. Opening doors to rights, services, and dignity for every South African."*
