"""Pfula — AI That Opens Government for Every South African.

FastAPI backend with Claude conversation engine, case management,
escalation letter generation, and analytics dashboard.
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import anthropic

from backend.knowledge import load_all_knowledge
from backend.system_prompt import get_system_prompt
from backend.demo_responses import get_demo_response, stream_demo_response
from backend.database import (
    init_db, seed_demo_data,
    create_conversation, get_conversation, add_message,
    get_conversation_messages,
    create_case, update_case, get_case, get_cases_for_conversation, get_all_cases,
    save_escalation_letter, get_escalation_letters,
    log_analytics, get_analytics_summary,
)

load_dotenv()

# --- App Setup ---
app = FastAPI(title="Pfula", description="AI That Opens Government for Every South African")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
STATIC_DIR = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Initialize
knowledge_base = load_all_knowledge()
system_prompt = get_system_prompt(knowledge_base)

# Demo mode detection
DEMO_MODE = not os.getenv("ANTHROPIC_API_KEY")

# Claude async client (None in demo mode)
# Using AsyncAnthropic so streaming never blocks the event loop on Azure
client = None if DEMO_MODE else anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))


@app.on_event("startup")
async def startup():
    init_db()
    seed_demo_data()


# --- Pages ---

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main WhatsApp simulation interface."""
    html_path = Path(__file__).parent.parent / "frontend" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the admin analytics dashboard."""
    html_path = Path(__file__).parent.parent / "frontend" / "dashboard.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/simulator", response_class=HTMLResponse)
async def simulator():
    """Serve the iPhone simulator view — for stage presentations."""
    html_path = Path(__file__).parent.parent / "frontend" / "simulator.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/mockup", response_class=HTMLResponse)
async def mockup():
    """Serve the UX mockup page."""
    html_path = Path(__file__).parent.parent / "frontend" / "mockup.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/tracker", response_class=HTMLResponse)
async def tracker():
    """Serve the case tracker page."""
    html_path = Path(__file__).parent.parent / "frontend" / "tracker.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


# --- API Endpoints ---

@app.post("/api/conversation")
async def new_conversation(data: dict = None):
    """Create a new conversation."""
    name = data.get("name", "Citizen") if data else "Citizen"
    language = data.get("language", "en") if data else "en"
    conv_id = create_conversation(name, language)
    return {"conversation_id": conv_id}


@app.post("/api/chat")
async def chat(data: dict):
    """Send a message and get a response from Pfula."""
    conv_id = data.get("conversation_id")
    message = data.get("message", "").strip()

    if not conv_id or not message:
        raise HTTPException(status_code=400, detail="conversation_id and message are required")

    # Ensure conversation exists
    conv = get_conversation(conv_id)
    if not conv:
        conv_id = create_conversation()

    # Save user message
    add_message(conv_id, "user", message)

    # Detect language
    language = _detect_language(message)
    log_analytics("query", _detect_service(message), message, language)

    # Get conversation history
    messages = get_conversation_messages(conv_id)

    # Call Claude (or use demo responses)
    if DEMO_MODE:
        assistant_message = get_demo_response(message)
    else:
        try:
            response = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                system=system_prompt,
                messages=messages,
            )
            assistant_message = response.content[0].text
        except Exception as e:
            print(f"[Pfula ERROR /api/chat] {type(e).__name__}: {e}")
            assistant_message = (
                "I'm having trouble connecting right now. Please try again in a moment. "
                "If this persists, you can call the relevant service directly — "
                "SASSA: 0800 60 10 11, Home Affairs: 0800 60 11 90, SARS: 0800 00 7277."
            )

    # Save assistant response
    add_message(conv_id, "assistant", assistant_message)

    return {
        "conversation_id": conv_id,
        "response": assistant_message,
        "language": language,
    }


@app.get("/api/conversation/{conv_id}")
async def get_conv(conv_id: str):
    """Get conversation details and messages."""
    conv = get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


# --- WebSocket for streaming responses ---

@app.websocket("/ws/chat/{conv_id}")
async def websocket_chat(websocket: WebSocket, conv_id: str):
    """WebSocket endpoint for streaming chat responses."""
    await websocket.accept()

    # Ensure conversation exists
    conv = get_conversation(conv_id)
    if not conv:
        conv_id = create_conversation()

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "").strip()

            if not user_message:
                continue

            # Save user message
            add_message(conv_id, "user", user_message)

            language = _detect_language(user_message)
            log_analytics("query", _detect_service(user_message), user_message, language)

            # Get history
            messages = get_conversation_messages(conv_id)

            # Stream response
            full_response = ""
            if DEMO_MODE:
                async for chunk in stream_demo_response(user_message):
                    full_response += chunk
                    await websocket.send_json({
                        "type": "stream",
                        "content": chunk,
                    })
            else:
                try:
                    async with client.messages.stream(
                        model="claude-sonnet-4-20250514",
                        max_tokens=2048,
                        system=system_prompt,
                        messages=messages,
                    ) as stream:
                        async for text in stream.text_stream:
                            full_response += text
                            await websocket.send_json({
                                "type": "stream",
                                "content": text,
                            })
                except Exception as e:
                    print(f"[Pfula ERROR /ws/chat] {type(e).__name__}: {e}")
                    full_response = (
                        "I'm having trouble connecting right now. Please try again in a moment."
                    )
                    await websocket.send_json({
                        "type": "stream",
                        "content": full_response,
                    })

            # Save full response
            add_message(conv_id, "assistant", full_response)

            # Signal completion
            await websocket.send_json({
                "type": "complete",
                "content": full_response,
                "language": language,
            })

    except WebSocketDisconnect:
        pass


# --- Case Management API ---

@app.post("/api/case")
async def create_new_case(data: dict):
    """Create a new tracked case."""
    case_id = create_case(
        conversation_id=data.get("conversation_id", ""),
        service_type=data["service_type"],
        title=data["title"],
        description=data.get("description", ""),
    )
    return {"case_id": case_id}


@app.get("/api/case/{case_id}")
async def get_case_details(case_id: str):
    """Get case details."""
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@app.put("/api/case/{case_id}")
async def update_case_details(case_id: str, data: dict):
    """Update case details."""
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    update_case(case_id, **data)
    return {"status": "updated"}


@app.get("/api/cases")
async def list_cases():
    """List all cases."""
    return {"cases": get_all_cases()}


@app.get("/api/cases/{conv_id}")
async def list_cases_for_conversation(conv_id: str):
    """List cases for a specific conversation."""
    return {"cases": get_cases_for_conversation(conv_id)}


# --- Escalation Letter API ---

@app.post("/api/escalation-letter")
async def generate_escalation_letter(data: dict):
    """Generate a formal escalation letter using Claude."""
    case_id = data.get("case_id", "")
    conv_id = data.get("conversation_id", "")
    problem_description = data.get("problem_description", "")
    service_type = data.get("service_type", "")
    citizen_name = data.get("citizen_name", "")
    citizen_id = data.get("citizen_id", "")
    reference_number = data.get("reference_number", "")

    # Use Claude to generate the letter
    letter_prompt = f"""Generate a formal escalation/complaint letter for a South African citizen.

Details:
- Service: {service_type}
- Problem: {problem_description}
- Citizen Name: {citizen_name}
- ID Number: {citizen_id}
- Reference Number: {reference_number}
- Date: {datetime.now().strftime('%d %B %Y')}

The letter must:
1. Be addressed to the correct authority for this type of complaint
2. Cite the specific South African legislation that applies
3. State the facts clearly and professionally
4. Request specific action with a 14 business day deadline
5. Be formatted as a formal letter with proper salutation and closing
6. Include the citizen's constitutional rights that are being violated

Return the letter as a JSON object with these fields:
- recipient: who it's addressed to (name and position)
- subject: the subject line
- body: the full letter text
- legislation_cited: array of legislation references used

Return ONLY the JSON object, no other text."""

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": letter_prompt}],
        )

        # Parse the response
        response_text = response.content[0].text.strip()
        # Handle potential markdown code blocks
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            response_text = response_text.rsplit("```", 1)[0]

        letter_data = json.loads(response_text)

        # Save the letter
        letter_id = save_escalation_letter(
            case_id=case_id,
            conversation_id=conv_id,
            recipient=letter_data["recipient"],
            subject=letter_data["subject"],
            body=letter_data["body"],
            legislation=letter_data["legislation_cited"],
        )

        log_analytics("escalation", service_type)

        return {
            "letter_id": letter_id,
            **letter_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate letter: {str(e)}")


@app.get("/api/escalation-letters")
async def list_letters():
    """List all escalation letters."""
    return {"letters": get_escalation_letters()}


# --- Analytics API ---

@app.get("/api/analytics")
async def analytics():
    """Get analytics summary."""
    return get_analytics_summary()


# --- Utility Functions ---

def _detect_language(text: str) -> str:
    """Simple language detection for isiZulu vs English."""
    zulu_markers = [
        "sawubona", "ngicela", "ngifuna", "yini", "kanjani", "ngiyabonga",
        "unjani", "ngingu", "ngi", "uku", "uma", "futhi", "kodwa", "mina",
        "wena", "isicelo", "imali", "umsebenzi", "isibonelelo", "ukusiza",
        "ngingakusiza", "ungakhathazeki", "yebo", "cha", "nceda",
    ]
    text_lower = text.lower()
    zulu_count = sum(1 for marker in zulu_markers if marker in text_lower)
    return "zu" if zulu_count >= 2 else "en"


def _detect_service(text: str) -> str:
    """Detect which government service the query relates to."""
    text_lower = text.lower()

    service_keywords = {
        "sassa": ["sassa", "grant", "srd", "r370", "child support", "disability grant",
                   "pension", "old age", "foster", "social grant", "isibonelelo"],
        "home_affairs": ["home affairs", "id", "smart id", "passport", "birth certificate",
                         "death certificate", "marriage", "identity document", "ipasipoti"],
        "uif": ["uif", "unemployment", "ui-19", "ui19", "labour centre", "retrench",
                "maternity", "ufiling", "retrenched"],
        "sars": ["sars", "tax", "efiling", "vat", "income tax", "tax return",
                 "tax clearance", "irp5"],
        "municipal": ["municipal", "rates", "water", "electricity", "ethekwini",
                      "refuse", "sewage", "bill", "load shedding", "prepaid", "meter"],
        "deeds_office": ["deeds", "title deed", "property", "transfer", "bond",
                         "conveyancing", "erf"],
        "cipc": ["cipc", "company registration", "pty ltd", "annual return",
                 "trademark", "director", "business registration"],
    }

    for service, keywords in service_keywords.items():
        if any(kw in text_lower for kw in keywords):
            return service

    return "general"
