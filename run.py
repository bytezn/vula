#!/usr/bin/env python3
"""Pfula — AI That Opens Government for Every South African.

Start the application:
    python run.py

Then open:
    http://localhost:8000          — WhatsApp chat interface
    http://localhost:8000/tracker  — Case tracker
    http://localhost:8000/dashboard — Analytics dashboard
"""

import os
import sys

def main():
    # Check for API key
    from dotenv import load_dotenv
    load_dotenv()

    demo_mode = not os.getenv("ANTHROPIC_API_KEY")

    print("\n" + "=" * 60)
    print("  PFULA (to open)")
    print("  AI That Opens Government for Every South African")
    print("=" * 60)
    if demo_mode:
        print("\n  ⚡ Running in DEMO MODE (no API key)")
        print("  Add ANTHROPIC_API_KEY to .env for live Claude responses")
    print(f"\n  Chat:      http://localhost:8000")
    print(f"  Tracker:   http://localhost:8000/tracker")
    print(f"  Dashboard: http://localhost:8000/dashboard")
    print("\n" + "=" * 60 + "\n")

    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("ENV", "development") == "development",
    )


if __name__ == "__main__":
    main()
