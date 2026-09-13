# SIPA TRACE Dashboard

A deterministic audit trail and visualization dashboard for AI infrastructure pipelines. This frontend is built with React, TypeScript, Vite, and Tailwind CSS.

## Features Implemented
- **Live Trace Stream:** Fetches and displays AI pipeline execution steps in real-time from the FastAPI backend.
- **Tamper Verification:** Displays a "Verified" badge by checking the cryptographic hash chain of the trace logs.
- **Live Inspection Panel:** Highlights structural state diffs, risk escalations, and action reversibility between consecutive events.
- **Tailwind UI:** Custom dark-mode aesthetic with color-coded risk badges (`NONE`, `MEDIUM`, `CRITICAL`).

## How to Run

1. **Start the FastAPI Backend:**
   ```bash
   # From the root project folder
   python -m uvicorn api:app --port 8000