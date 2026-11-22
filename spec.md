# Project: Structured Invoice Extractor (Mini-Project 1)

## Goal
Build a Python CLI tool using `uv` that reads a messy text or PDF invoice, sends it to the Gemini API (`gemini-3.8-flash`), extracts clean structured data, validates it with Pydantic, and saves it to a local SQLite database.

## Required Extracted Fields
- vendor_name (string)
- invoice_date (YYYY-MM-DD)
- currency (EUR, USD, etc.)
- total_amount (float)
- line_items (list of descriptions and amounts)

## Engineering Rules
- Load `GEMINI_API_KEY` strictly from a `.env` file (add `.env` to `.gitignore`).
- If an invoice is missing `total_amount` or is unreadable, fail loudly with a clear error message instead of guessing.
- Log the token count and response time for every run.
- Include at least 3 `pytest` unit tests (including 1 test with broken/invalid input).
- Include 2 realistic sample invoices (one English, one Italian) in a `samples/` folder so I can run it immediately.