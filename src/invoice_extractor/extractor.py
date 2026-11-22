"""Gemini extraction — uses native Structured Outputs (response_schema + response_mime_type)."""

from __future__ import annotations

import time
from pathlib import Path

from google import genai
from google.genai import types

from invoice_extractor.config import Settings
from invoice_extractor.models import ExtractionResult, Invoice

EXTRACTION_PROMPT = """\
You are an expert invoice parser. Extract the following structured fields from \
the invoice provided:

• vendor_name   — the company / person that issued the invoice.
• invoice_date  — the date on the invoice, formatted as YYYY-MM-DD.
• currency      — the 3-letter ISO 4217 currency code (e.g. EUR, USD, GBP).
• subtotal      — subtotal before tax / sum of all line items (e.g. Subtotal, Imponibile).
• tax_amount    — total tax amount (VAT, IVA, sales tax). If 0% or tax exempt, set to 0.0.
• total_amount  — the final total amount due. Must equal subtotal + tax_amount.
• line_items    — every item or service listed, each with a description and its amount.

RULES
1. If the total amount is missing or the invoice is completely unreadable, \
return an empty JSON object {}.
2. Reconcile math: ensure sum(line_items) equals subtotal, and subtotal + tax_amount equals total_amount.
3. Do NOT guess or fabricate any value.
4. Handle invoices in any language.
"""


def extract_invoice(file_path: Path, settings: Settings) -> ExtractionResult:
    """Read an invoice file, send it to Gemini, and return validated structured data.

    Supports .txt and .pdf files.  Uses Gemini's native structured-output mode
    (``response_schema=Invoice``) so the response is guaranteed to match the
    Pydantic schema — no manual JSON parsing required.
    """
    client = genai.Client(api_key=settings.gemini_api_key.get_secret_value())

    # ── Build the content parts ──────────────────────────────────────────
    suffix = file_path.suffix.lower()

    if suffix in (".txt", ".text"):
        invoice_text = file_path.read_text(encoding="utf-8")
        contents: str | list = (
            f"{EXTRACTION_PROMPT}\n\n"
            f"--- INVOICE START ---\n{invoice_text}\n--- INVOICE END ---"
        )

    elif suffix == ".pdf":
        pdf_bytes = file_path.read_bytes()
        contents = [
            EXTRACTION_PROMPT,
            types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
        ]

    else:
        raise ValueError(
            f"Unsupported file type: '{suffix}'.  Supported formats: .txt, .pdf"
        )

    # ── Call Gemini with native structured output ────────────────────────
    start = time.perf_counter()

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Invoice,          # ← Pydantic schema passed directly
        ),
    )

    elapsed = time.perf_counter() - start

    # ── Validate the response ────────────────────────────────────────────
    raw_json = response.text
    if not raw_json or raw_json.strip() in ("{}", "null", ""):
        raise ValueError(
            f"❌ Extraction failed: Gemini could not extract data from "
            f"'{file_path.name}'.  The invoice may be unreadable or missing "
            f"required fields (e.g. total_amount)."
        )

    # Even though Gemini guarantees the shape, we still run Pydantic
    # validation to enforce our custom constraints (gt=0, math reconciliation, etc.)
    invoice = Invoice.model_validate_json(raw_json)

    # ── Token telemetry ──────────────────────────────────────────────────
    token_count = 0
    if response.usage_metadata:
        token_count = response.usage_metadata.total_token_count or 0

    return ExtractionResult(
        invoice=invoice,
        token_count=token_count,
        response_time_s=round(elapsed, 3),
        model_used=settings.gemini_model,
    )
