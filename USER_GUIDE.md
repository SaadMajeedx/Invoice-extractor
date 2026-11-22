# User Guide: Structured Invoice Extractor

A simple, reliable tool that turns messy invoices into clean, organized business records in seconds.

---

## 1. What Problem This Solves

Typing invoice details by hand into spreadsheets is slow, repetitive, and prone to costly typos. This tool uses smart AI to instantly read invoices in both English and Italian—whether they are text files or PDFs. It pulls out key numbers, double-checks the math automatically, and saves everything neatly in one place without you lifting a finger.

---

## 2. Who This Is For

- **Freelancers & Contractors:** Track your incoming and outgoing bills without wasting billable hours on bookkeeping.
- **Small Business Owners:** Eliminate tedious receipt-entry and keep an accurate record of expenses.
- **Finance & Operations Teams:** Process mixed English and Italian bills (such as VAT / *IVA* invoices) quickly and accurately.
- **Recruiters & Hiring Managers:** See a practical, real-world example of modern AI solving everyday business data entry.

---

## 3. How It Works (The 4-Step Flow)

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  1. Upload      │  ───> │  2. AI Reads    │  ───> │  3. Math Check  │  ───> │  4. Saved       │
│  Select any     │       │  Pulls vendor,  │       │  Verifies items │       │  Stored safely  │
│  invoice file   │       │  date, amounts, │       │  add up to the  │       │  in your local  │
│  (TXT or PDF)   │       │  and tax cleanly│       │  exact total    │       │  database       │
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
```

1. **Upload Invoice:** You hand the tool an invoice file.
2. **AI Reads It:** Google's Gemini AI reads the document in any language, finding who issued it, the date, currency, line items, taxes, and total due.
3. **Automatic Math & Error Check:** The system verifies that every line item adds up to the subtotal, and that the subtotal plus tax matches the final total. If anything looks off or amounts are missing, it stops immediately instead of guessing.
4. **Saved Safely to Database:** Clean, verified data is saved into your private database, ready to review anytime.

---

## 4. How to Use It Day-to-Day

You only need two simple commands:

### A. Extract an Invoice
Process any invoice with one command:
```bash
uv run invoice-extractor extract samples/invoice_en.txt
```
*(Or for an Italian invoice: `uv run invoice-extractor extract samples/invoice_it.txt`)*

**What you will see:**
```text
Processing: invoice_en.txt
Model: gemini-3.5-flash-lite
Response time: 1.8s
✅ Saved invoice #1 from 'Bright Pixel Studios Ltd.'

{
  "vendor_name": "Bright Pixel Studios Ltd.",
  "invoice_date": "2024-03-15",
  "currency": "USD",
  "subtotal": 4599.0,
  "tax_amount": 0.0,
  "total_amount": 4599.0,
  "line_items": [
    {"description": "Website redesign (Phase 1)", "amount": 3200.0},
    {"description": "SEO audit & optimization", "amount": 850.0},
    {"description": "Monthly hosting (3 months)", "amount": 450.0},
    {"description": "SSL certificate (annual renewal)", "amount": 99.0}
  ]
}
```

---

### B. View All Saved Invoices
See every invoice you have processed so far:
```bash
uv run invoice-extractor list
```

**What you will see:**
```text
──────────────────────────────────────────────────
  #2  Rossi & Bianchi S.r.l.
  Date: 2024-02-22
  Subtotal: EUR 4195.00  |  Tax: EUR 922.90
  Total:    EUR 5117.90
  Items:
    • Consulenza strategica (8 ore): 1200.00
    • Sviluppo sito web aziendale: 2800.00
    • Hosting annuale (server dedicato): 180.00
    • Rinnovo dominio (.it): 15.00
  Saved: 2026-11-22 21:55:21
```

---

### C. What Happens on Broken or Invalid Invoices?
If you provide an unreadable document or an invoice missing crucial figures, the tool **fails loudly with a clear error** to protect your business records:

```text
Value error, total_amount must be greater than 0
Value error, Invoice must contain at least one line item
```

No corrupted numbers or fabricated "guesses" will ever make it into your records.
