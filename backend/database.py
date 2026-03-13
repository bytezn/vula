"""Database models and operations for Pfula — SQLite-based case management."""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "pfula.db"


def get_db() -> sqlite3.Connection:
    """Get a database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Initialize the database schema."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_name TEXT DEFAULT 'Citizen',
            user_phone TEXT DEFAULT '',
            language TEXT DEFAULT 'en',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            messages TEXT DEFAULT '[]'
        );

        CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY,
            conversation_id TEXT,
            service_type TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            description TEXT DEFAULT '',
            documents_submitted TEXT DEFAULT '[]',
            documents_needed TEXT DEFAULT '[]',
            next_action TEXT DEFAULT '',
            expected_timeline TEXT DEFAULT '',
            escalation_level INTEGER DEFAULT 0,
            notes TEXT DEFAULT '[]',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        );

        CREATE TABLE IF NOT EXISTS escalation_letters (
            id TEXT PRIMARY KEY,
            case_id TEXT,
            conversation_id TEXT,
            recipient TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            legislation_cited TEXT DEFAULT '[]',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (case_id) REFERENCES cases(id),
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        );

        CREATE TABLE IF NOT EXISTS analytics_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            service_type TEXT DEFAULT '',
            query_text TEXT DEFAULT '',
            language TEXT DEFAULT 'en',
            resolved INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


# --- Conversation Operations ---

def create_conversation(user_name: str = "Citizen", language: str = "en") -> str:
    """Create a new conversation and return its ID."""
    conv_id = str(uuid.uuid4())[:8]
    conn = get_db()
    conn.execute(
        "INSERT INTO conversations (id, user_name, language) VALUES (?, ?, ?)",
        (conv_id, user_name, language)
    )
    conn.commit()
    conn.close()
    return conv_id


def get_conversation(conv_id: str) -> Optional[dict]:
    """Get a conversation by ID."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM conversations WHERE id = ?", (conv_id,)
    ).fetchone()
    conn.close()
    if row:
        result = dict(row)
        result["messages"] = json.loads(result["messages"])
        return result
    return None


def add_message(conv_id: str, role: str, content: str):
    """Add a message to a conversation."""
    conn = get_db()
    row = conn.execute(
        "SELECT messages FROM conversations WHERE id = ?", (conv_id,)
    ).fetchone()
    if row:
        messages = json.loads(row["messages"])
        messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        conn.execute(
            "UPDATE conversations SET messages = ?, updated_at = datetime('now') WHERE id = ?",
            (json.dumps(messages), conv_id)
        )
        conn.commit()
    conn.close()


def get_conversation_messages(conv_id: str) -> list:
    """Get all messages for a conversation in Claude API format."""
    conn = get_db()
    row = conn.execute(
        "SELECT messages FROM conversations WHERE id = ?", (conv_id,)
    ).fetchone()
    conn.close()
    if row:
        messages = json.loads(row["messages"])
        return [{"role": m["role"], "content": m["content"]} for m in messages]
    return []


# --- Case Operations ---

def create_case(conversation_id: str, service_type: str, title: str, description: str = "") -> str:
    """Create a new case and return its ID."""
    case_id = "PF-" + str(uuid.uuid4())[:6].upper()
    conn = get_db()
    conn.execute(
        "INSERT INTO cases (id, conversation_id, service_type, title, description) VALUES (?, ?, ?, ?, ?)",
        (case_id, conversation_id, service_type, title, description)
    )
    conn.commit()
    conn.close()

    log_analytics("case_created", service_type)
    return case_id


def update_case(case_id: str, **kwargs):
    """Update case fields."""
    conn = get_db()
    for key, value in kwargs.items():
        if isinstance(value, (list, dict)):
            value = json.dumps(value)
        conn.execute(
            f"UPDATE cases SET {key} = ?, updated_at = datetime('now') WHERE id = ?",
            (value, case_id)
        )
    conn.commit()
    conn.close()


def get_case(case_id: str) -> Optional[dict]:
    """Get a case by ID."""
    conn = get_db()
    row = conn.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
    conn.close()
    if row:
        result = dict(row)
        for field in ["documents_submitted", "documents_needed", "notes"]:
            result[field] = json.loads(result[field])
        return result
    return None


def get_cases_for_conversation(conv_id: str) -> list:
    """Get all cases for a conversation."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM cases WHERE conversation_id = ? ORDER BY created_at DESC", (conv_id,)
    ).fetchall()
    conn.close()
    cases = []
    for row in rows:
        result = dict(row)
        for field in ["documents_submitted", "documents_needed", "notes"]:
            result[field] = json.loads(result[field])
        cases.append(result)
    return cases


def get_all_cases() -> list:
    """Get all cases across all conversations."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM cases ORDER BY created_at DESC").fetchall()
    conn.close()
    cases = []
    for row in rows:
        result = dict(row)
        for field in ["documents_submitted", "documents_needed", "notes"]:
            result[field] = json.loads(result[field])
        cases.append(result)
    return cases


# --- Escalation Letter Operations ---

def save_escalation_letter(case_id: str, conversation_id: str, recipient: str,
                           subject: str, body: str, legislation: list) -> str:
    """Save an escalation letter and return its ID."""
    letter_id = str(uuid.uuid4())[:8]
    conn = get_db()
    conn.execute(
        "INSERT INTO escalation_letters (id, case_id, conversation_id, recipient, subject, body, legislation_cited) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (letter_id, case_id, conversation_id, recipient, subject, body, json.dumps(legislation))
    )
    conn.commit()
    conn.close()
    return letter_id


def get_escalation_letters(case_id: str = None) -> list:
    """Get escalation letters, optionally filtered by case."""
    conn = get_db()
    if case_id:
        rows = conn.execute(
            "SELECT * FROM escalation_letters WHERE case_id = ? ORDER BY created_at DESC",
            (case_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM escalation_letters ORDER BY created_at DESC"
        ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


# --- Analytics Operations ---

def log_analytics(event_type: str, service_type: str = "", query_text: str = "",
                  language: str = "en", resolved: bool = False):
    """Log an analytics event."""
    conn = get_db()
    conn.execute(
        "INSERT INTO analytics_events (event_type, service_type, query_text, language, resolved) VALUES (?, ?, ?, ?, ?)",
        (event_type, service_type, query_text, language, 1 if resolved else 0)
    )
    conn.commit()
    conn.close()


def get_analytics_summary() -> dict:
    """Get aggregate analytics data."""
    conn = get_db()

    total_conversations = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
    total_cases = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
    open_cases = conn.execute("SELECT COUNT(*) FROM cases WHERE status = 'open'").fetchone()[0]
    resolved_cases = conn.execute("SELECT COUNT(*) FROM cases WHERE status = 'resolved'").fetchone()[0]
    total_letters = conn.execute("SELECT COUNT(*) FROM escalation_letters").fetchone()[0]

    # Service type breakdown
    service_breakdown = {}
    rows = conn.execute(
        "SELECT service_type, COUNT(*) as count FROM analytics_events WHERE service_type != '' GROUP BY service_type ORDER BY count DESC"
    ).fetchall()
    for row in rows:
        service_breakdown[row["service_type"]] = row["count"]

    # Language breakdown
    language_breakdown = {}
    rows = conn.execute(
        "SELECT language, COUNT(*) as count FROM analytics_events GROUP BY language"
    ).fetchall()
    for row in rows:
        language_breakdown[row["language"]] = row["count"]

    # Recent events
    recent_events = conn.execute(
        "SELECT * FROM analytics_events ORDER BY created_at DESC LIMIT 50"
    ).fetchall()

    # Queries per day (last 7 days)
    daily_queries = conn.execute("""
        SELECT DATE(created_at) as day, COUNT(*) as count
        FROM analytics_events
        WHERE created_at >= datetime('now', '-7 days')
        GROUP BY DATE(created_at)
        ORDER BY day
    """).fetchall()

    conn.close()

    return {
        "total_conversations": total_conversations,
        "total_cases": total_cases,
        "open_cases": open_cases,
        "resolved_cases": resolved_cases,
        "total_escalation_letters": total_letters,
        "service_breakdown": service_breakdown,
        "language_breakdown": language_breakdown,
        "recent_events": [dict(e) for e in recent_events],
        "daily_queries": [dict(d) for d in daily_queries]
    }


# Seed demo data for the stage presentation
def seed_demo_data():
    """Populate the database with realistic demo data for the stage presentation."""
    conn = get_db()

    # Check if already seeded
    count = conn.execute("SELECT COUNT(*) FROM analytics_events").fetchone()[0]
    if count > 10:
        conn.close()
        return

    # Seed analytics events showing realistic usage patterns
    demo_events = [
        ("query", "sassa", "My SRD grant was rejected", "en"),
        ("query", "sassa", "Isicelo sami sesibonelelo senziwe kanjani?", "zu"),
        ("query", "home_affairs", "How long for my Smart ID?", "en"),
        ("query", "home_affairs", "Ngifuna ipasipoti", "zu"),
        ("query", "municipal", "My rates bill is too high", "en"),
        ("query", "sars", "First time filing tax return", "en"),
        ("query", "uif", "Employer won't give me UI-19 form", "en"),
        ("query", "sassa", "Child support grant stopped", "en"),
        ("query", "cipc", "How to register a company", "en"),
        ("query", "municipal", "No water in my area for 3 days", "en"),
        ("query", "sassa", "Umama wami akayitholi imali yakhe", "zu"),
        ("query", "home_affairs", "Birth certificate late registration", "en"),
        ("query", "sars", "Tax clearance certificate needed", "en"),
        ("query", "uif", "Maternity benefit application", "en"),
        ("query", "deeds_office", "Title deed search for property", "en"),
        ("query", "municipal", "Electricity meter not accepting tokens", "en"),
        ("query", "sassa", "Disability grant application", "en"),
        ("query", "home_affairs", "Marriage registration customary", "zu"),
        ("query", "sars", "VAT registration for small business", "en"),
        ("query", "municipal", "Sewage overflow in my street", "en"),
        ("case_created", "sassa", "", "en"),
        ("case_created", "home_affairs", "", "en"),
        ("case_created", "sassa", "", "zu"),
        ("case_created", "municipal", "", "en"),
        ("case_created", "uif", "", "en"),
        ("escalation", "sassa", "", "en"),
        ("escalation", "home_affairs", "", "en"),
        ("resolved", "sassa", "", "en"),
        ("resolved", "municipal", "", "en"),
    ]

    for event_type, service, query, lang in demo_events:
        conn.execute(
            "INSERT INTO analytics_events (event_type, service_type, query_text, language, resolved) VALUES (?, ?, ?, ?, ?)",
            (event_type, service, query, lang, 1 if event_type == "resolved" else 0)
        )

    # Seed some demo cases
    demo_cases = [
        ("PF-A1B2C3", "conv-1", "sassa", "SRD Grant Rejection Appeal", "open",
         "Grant rejected due to income threshold. Applicant states they are unemployed."),
        ("PF-D4E5F6", "conv-2", "home_affairs", "Smart ID Application Follow-up", "open",
         "Applied 8 months ago. No response. Reference number provided."),
        ("PF-G7H8I9", "conv-3", "municipal", "Incorrect Municipal Bill Dispute", "resolved",
         "Rates bill tripled overnight. Estimated reading used instead of actual."),
        ("PF-J1K2L3", "conv-4", "uif", "UIF Claim - Employer Withholding UI-19", "open",
         "Retrenched employee. Employer refusing to issue discharge certificate."),
        ("PF-M4N5O6", "conv-5", "sassa", "Child Support Grant Suspension", "open",
         "Grant stopped without notification. Child is 12 years old."),
    ]

    for case_id, conv_id, service, title, status, desc in demo_cases:
        conn.execute(
            "INSERT OR IGNORE INTO cases (id, conversation_id, service_type, title, status, description) VALUES (?, ?, ?, ?, ?, ?)",
            (case_id, conv_id, service, title, status, desc)
        )

    conn.commit()
    conn.close()
