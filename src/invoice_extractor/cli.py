"""CLI entry-point — ``invoice-extractor extract <file>`` and ``invoice-extractor list``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from invoice_extractor.config import load_settings
from invoice_extractor.database import init_db, list_invoices, save_invoice
from invoice_extractor.extractor import extract_invoice
from invoice_extractor.logger import log_extraction, setup_logger


# ── Commands ─────────────────────────────────────────────────────────────


def cmd_extract(args: argparse.Namespace) -> None:
    """Extract structured data from a single invoice file."""
    logger = setup_logger()
    settings = load_settings()

    file_path = Path(args.file)
    if not file_path.exists():
        raise SystemExit(f"❌ File not found: {file_path}")

    logger.info("Processing: %s", file_path.name)

    # Keep the raw text for auditability (PDFs are stored as None)
    raw_input: str | None = None
    if file_path.suffix.lower() in (".txt", ".text"):
        raw_input = file_path.read_text(encoding="utf-8")

    # Extract via Gemini
    try:
        result = extract_invoice(file_path, settings)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    # Log telemetry
    log_extraction(logger, result.model_used, result.token_count, result.response_time_s)

    # Persist to SQLite
    conn = init_db(settings.database_path)
    try:
        invoice_id = save_invoice(conn, result, raw_input=raw_input)
        logger.info("✅ Saved invoice #%d from '%s'", invoice_id, result.invoice.vendor_name)
    finally:
        conn.close()

    # Print the extracted JSON to stdout
    print("\n" + result.invoice.model_dump_json(indent=2))


def cmd_list(args: argparse.Namespace) -> None:
    """List every invoice stored in the database."""
    settings = load_settings()
    conn = init_db(settings.database_path)
    try:
        invoices = list_invoices(conn)
    finally:
        conn.close()

    if not invoices:
        print("No invoices found.")
        return

    for inv in invoices:
        print(f"\n{'─' * 50}")
        print(f"  #{inv['id']}  {inv['vendor_name']}")
        print(f"  Date: {inv['invoice_date']}")
        print(f"  Subtotal: {inv['currency']} {inv.get('subtotal', 0.0):.2f}  |  Tax: {inv['currency']} {inv.get('tax_amount', 0.0):.2f}")
        print(f"  Total:    {inv['currency']} {inv['total_amount']:.2f}")
        print(f"  Items:")
        for item in inv["line_items"]:
            print(f"    • {item['description']}: {item['amount']:.2f}")
        print(f"  Saved: {inv['created_at']}")


# ── Argument parser ──────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="invoice-extractor",
        description="Extract structured data from invoices using the Gemini API.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # extract
    p_extract = sub.add_parser("extract", help="Extract data from an invoice file")
    p_extract.add_argument("file", help="Path to the invoice file (.txt or .pdf)")
    p_extract.set_defaults(func=cmd_extract)

    # list
    p_list = sub.add_parser("list", help="List all saved invoices")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
