"""Pydantic models for invoice data and extraction results."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator


class LineItem(BaseModel):
    """A single line item on an invoice."""

    description: str = Field(..., description="Item or service description")
    amount: float = Field(..., description="Amount for this line item")


class Invoice(BaseModel):
    """Structured invoice data — this schema is passed directly to Gemini via response_schema."""

    vendor_name: str = Field(..., description="Vendor / company name")
    invoice_date: date = Field(..., description="Invoice date (YYYY-MM-DD)")
    currency: str = Field(
        ..., description="ISO 4217 currency code (e.g. EUR, USD, GBP)"
    )
    subtotal: float = Field(
        default=0.0,
        description="Subtotal before tax (sum of all line items, e.g. Imponibile)",
    )
    tax_amount: float = Field(
        default=0.0,
        description="Total tax amount (VAT, IVA, sales tax). Set to 0.0 if tax-exempt or 0%",
    )
    total_amount: float = Field(..., description="Total amount due — must be positive")
    line_items: list[LineItem] = Field(
        ..., description="List of line items on the invoice"
    )

    @field_validator("total_amount")
    @classmethod
    def validate_total_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("total_amount must be greater than 0")
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) != 3:
            raise ValueError("currency must be a 3-letter ISO code")
        return v

    @field_validator("line_items")
    @classmethod
    def validate_line_items(cls, v: list[LineItem]) -> list[LineItem]:
        if not v:
            raise ValueError("Invoice must contain at least one line item")
        return v

    @model_validator(mode="after")
    def reconcile_totals(self) -> Invoice:
        """Verify that line items sum to subtotal, and subtotal + tax_amount equals total_amount."""
        items_sum = round(sum(item.amount for item in self.line_items), 2)

        # If subtotal was omitted or defaulted to 0.0, auto-fill it if items match total and tax is 0
        if self.subtotal == 0.0 and self.tax_amount == 0.0 and abs(items_sum - self.total_amount) <= 0.02:
            self.subtotal = items_sum
        elif self.subtotal == 0.0 and abs(items_sum - (self.total_amount - self.tax_amount)) <= 0.02:
            self.subtotal = items_sum

        # Check 1: Sum of line items matches subtotal (tolerance = 0.02)
        if abs(items_sum - self.subtotal) > 0.02:
            raise ValueError(
                f"Reconciliation error: sum of line items ({items_sum:.2f}) "
                f"does not match subtotal ({self.subtotal:.2f})"
            )

        # Check 2: subtotal + tax_amount matches total_amount (tolerance = 0.02)
        expected_total = round(self.subtotal + self.tax_amount, 2)
        if abs(expected_total - self.total_amount) > 0.02:
            raise ValueError(
                f"Reconciliation error: subtotal ({self.subtotal:.2f}) + "
                f"tax_amount ({self.tax_amount:.2f}) = {expected_total:.2f}, "
                f"which does not match total_amount ({self.total_amount:.2f})"
            )

        return self


class ExtractionResult(BaseModel):
    """Wraps an extracted Invoice together with API telemetry."""

    invoice: Invoice
    token_count: int = Field(..., ge=0)
    response_time_s: float = Field(..., ge=0)
    model_used: str
