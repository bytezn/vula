# Pfula (to open)

**AI That Opens Government for Every South African**

Pfula is a WhatsApp-style AI assistant that helps South African citizens navigate government services — SASSA, Home Affairs, UIF, SARS, eThekwini Municipal Services, the Deeds Office, and CIPC. Built on Claude AI with a comprehensive South African government services knowledge base.

## What It Does

- **Conversational guidance** in English and isiZulu for any government service query
- **Step-by-step instructions** — which office, which form, which documents, which queue
- **Rights awareness** — tells citizens what the law says they're entitled to, citing specific legislation
- **Application tracking** — tracks active government applications with status, documents, and timelines
- **Escalation letters** — generates formal complaint letters citing SA legislation, addressed to the correct authority
- **Analytics dashboard** — aggregate data showing query patterns, service failures, and resolution rates

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. Run
python run.py
```

Then open:
- **http://localhost:8000** — WhatsApp chat interface
- **http://localhost:8000/tracker** — Case tracker
- **http://localhost:8000/dashboard** — Analytics dashboard

## Stage Demo Scenarios

The interface includes pre-built demo scenarios accessible via the attachment button (📎):

1. **SASSA Grant Rejection** — SRD grant declined without explanation
2. **Home Affairs 8-Month Delay** — Smart ID stuck in processing
3. **Municipal Bill Mystery** — Rates bill tripled overnight
4. **First-Time Taxpayer** — Young person filing first SARS return
5. **IsiZulu SASSA** — Grant enquiry in isiZulu
6. **Escalation Letter** — Generate formal complaint letter

## Architecture

```
pfula/
├── backend/
│   ├── app.py              # FastAPI server, API endpoints, WebSocket streaming
│   ├── database.py         # SQLite case management, analytics, conversations
│   ├── knowledge.py        # Knowledge base loader
│   └── system_prompt.py    # Claude system prompt with SA government expertise
├── frontend/
│   ├── index.html          # WhatsApp simulation interface
│   ├── tracker.html        # Case tracker
│   └── dashboard.html      # Analytics dashboard
├── knowledge_base/
│   ├── sassa.json          # SASSA grants, offices, rights, escalation
│   ├── home_affairs.json   # IDs, passports, births, deaths, marriages
│   ├── uif.json            # Unemployment, maternity, illness benefits
│   ├── sars.json           # Tax returns, VAT, clearance certificates
│   ├── municipal.json      # eThekwini rates, water, electricity, housing
│   ├── deeds_office.json   # Title deeds, property transfers, bonds
│   └── cipc.json           # Company registration, trademarks, annual returns
├── static/
│   ├── css/whatsapp.css    # WhatsApp-style dark theme UI
│   └── js/chat.js          # Chat engine with WebSocket streaming
├── run.py                  # Entry point
├── requirements.txt
└── .env.example
```

## Knowledge Base Coverage

| Service | Coverage |
|---------|----------|
| SASSA | SRD, Child Support, Old Age, Disability, Foster, Care Dependency grants. Full appeal process. eThekwini offices. |
| Home Affairs | Smart ID, Passport, Birth/Death certificates, Marriage. Bank branch services. Escalation to Director General. |
| UIF | Unemployment, Illness, Maternity, Adoption, Dependants benefits. uFiling. Employer obligations. |
| SARS | Individual tax, VAT, Tax Clearance. eFiling guide. First-time taxpayer walkthrough. Tax Ombud escalation. |
| Municipal | eThekwini rates, water, electricity, housing, refuse. Indigent subsidy. Ward councillor escalation. |
| Deeds Office | Title deed search, property transfer, bond registration/cancellation. Property Alert. |
| CIPC | Company registration (Pty Ltd), annual returns, director changes, trademarks. Online portal tips. |

## Tech Stack

- **Backend**: Python, FastAPI, WebSockets
- **AI**: Claude API (Anthropic)
- **Database**: SQLite (zero config)
- **Frontend**: Vanilla HTML/CSS/JS (no build step)
- **Knowledge Base**: Structured JSON

## Built by Lawrance Reddy

For the Data & AI Community Day Durban: AI Unplugged — 14 March 2026

*Pfula means "to open" in Xitsonga. Because government services should be open to everyone.*
