"""SQLite helpers — schema creation, insert, and query."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from invoice_extractor.models import ExtractionResult


_SCHEMA = """\
CREATE TABLE IF NOT EXISTS invoices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_name     TEXT    NOT NULL,
    invoice_date    TEXT    NOT NULL,
    currency        TEXT    NOT NULL,
    subtotal        REAL    NOT NULL DEFAULT 0.0,
    tax_amount      REAL    NOT NULL DEFAULT 0.0,
    total_amount    REAL    NOT NULL,
    raw_input       TEXT,
    gemini_model    TEXT,
    token_count     INTEGER,
    response_time   REAL,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS line_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id      INTEGER NOT NULL,
    description     TEXT    NOT NULL,
    amount          REAL    NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
);
"""


def init_db(db_path: str | Path) -> sqlite3.Connection:
    """Create / open the database and ensure tables exist."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


def save_invoice(
    conn: sqlite3.Connection,
    result: ExtractionResult,
    raw_input: str | None = None,
) -> int:
    """Insert an invoice and its line items in a single transaction.  Returns the new invoice ID."""
    inv = result.invoice
    cursor = conn.execute(
        """
        INSERT INTO invoices
            (vendor_name, invoice_date, currency, subtotal, tax_amount, total_amount,
             raw_input, gemini_model, token_count, response_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            inv.vendor_name,
            inv.invoice_date.isoformat(),
            inv.currency,
            inv.subtotal,
            inv.tax_amount,
            inv.total_amount,
            raw_input,
            result.model_used,
            result.token_count,
            result.response_time_s,
        ),
    )
    invoice_id = cursor.lastrowid

    for item in inv.line_items:
        conn.execute(
            "INSERT INTO line_items (invoice_id, description, amount) VALUES (?, ?, ?)",
            (invoice_id, item.description, item.amount),
        )

    conn.commit()
    return invoice_id


def list_invoices(conn: sqlite3.Connection) -> list[dict]:
    """Return every invoice with its nested line_items (most-recent first)."""
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM invoices ORDER BY created_at DESC").fetchall()

    invoices: list[dict] = []
    for row in rows:
        invoice = dict(row)
        items = conn.execute(
            "SELECT description, amount FROM line_items WHERE invoice_id = ?",
            (row["id"],),
        ).fetchall()
        invoice["line_items"] = [dict(item) for item in items]
        invoices.append(invoice)

    return invoices
