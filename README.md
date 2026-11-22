# Structured Invoice Extractor

A fast CLI tool using `uv`, Pydantic, and the official Google GenAI SDK (`google-genai`) to parse messy text or PDF invoices into structured, validated data stored in a local SQLite database.

> 📖 **Non-technical reader or recruiter?** Check out the [Plain-English User Guide](file:///c:/Users/saQib/Desktop/invoice%20extractor/USER_GUIDE.md) for a 2-minute overview of what problem this solves and how to use it day-to-day.

## Features

- **Gemini Structured Outputs**: Utilizes native Gemini schema constraints (`response_schema=Invoice`, `response_mime_type="application/json"`).
- **Strict Validation**: Pydantic models enforce positive amounts, valid dates, 3-letter currency codes, and non-empty item lists.
- **Fail Loudly**: If an invoice is missing `total_amount` or is unreadable, it aborts immediately with a clear error without hallucinating or guessing.
- **Auditability**: Logs token consumption and latency for every run, and persists the raw input with the database record.
- **Configurable Models**: Switch effortlessly between `gemini-3.8-flash` and `gemini-3.5-flash-lite` via `.env`.
- **Multilingual**: Tested with English and Italian invoices.

---

## Installation & Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd "c:\Users\saQib\Desktop\invoice extractor"
   ```

2. **Install dependencies with `uv`:**
   ```bash
   uv sync --all-extras
   ```

3. **Configure your API key:**
   Copy `.env.example` to `.env` and fill in your Gemini API key:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key
   GEMINI_MODEL=gemini-3.8-flash
   DATABASE_PATH=invoices.db
   ```

---

## Usage

### Extract an Invoice
Run the CLI tool against any text or PDF invoice:
```bash
uv run invoice-extractor extract samples/invoice_en.txt
```
or Italian invoice:
```bash
uv run invoice-extractor extract samples/invoice_it.txt
```

Example output:
```text
22:30:15 | INFO    | Processing: invoice_en.txt
22:30:16 | INFO    | Model: gemini-3.8-flash
22:30:16 | INFO    | Tokens used: 285
22:30:16 | INFO    | Response time: 1.120s
22:30:16 | INFO    | ✅ Saved invoice #1 from 'Bright Pixel Studios Ltd.'

{
  "vendor_name": "Bright Pixel Studios Ltd.",
  "invoice_date": "2024-03-15",
  "currency": "USD",
  "total_amount": 4599.0,
  "line_items": [
    {
      "description": "Website redesign (Phase 1)",
      "amount": 3200.0
    },
    ...
  ]
}
```

### List Saved Invoices
View all invoices saved in SQLite:
```bash
uv run invoice-extractor list
```

---

## Running Tests

All unit tests run completely offline using mocked Gemini API responses (no API quota or key required):

```bash
uv run pytest
```
