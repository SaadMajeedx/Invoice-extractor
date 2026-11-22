"""Tests for Gemini extraction logic using mocks (no real API calls)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from invoice_extractor.config import Settings
from invoice_extractor.extractor import extract_invoice
from invoice_extractor.models import ExtractionResult


@pytest.fixture
def mock_settings() -> Settings:
    return Settings(
        gemini_api_key=SecretStr("mock-key-12345"),
        gemini_model="gemini-3.8-flash",
        database_path=":memory:",
    )


def test_extract_invoice_success(tmp_path: Path, mock_settings: Settings, sample_invoice):
    """Successful extraction properly constructs an ExtractionResult."""
    test_file = tmp_path / "invoice.txt"
    test_file.write_text("Sample invoice content", encoding="utf-8")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = sample_invoice.model_dump_json()
    mock_response.usage_metadata.total_token_count = 142
    mock_client.models.generate_content.return_value = mock_response

    with patch("invoice_extractor.extractor.genai.Client", return_value=mock_client):
        result = extract_invoice(test_file, mock_settings)

    assert isinstance(result, ExtractionResult)
    assert result.invoice.vendor_name == "Bright Pixel Studios Ltd."
    assert result.invoice.total_amount == 4599.00
    assert result.token_count == 142
    assert result.model_used == "gemini-3.8-flash"
    assert result.response_time_s >= 0


def test_extract_invoice_empty_response_fails_loudly(tmp_path: Path, mock_settings: Settings):
    """An empty or unreadable invoice response raises a clear descriptive ValueError."""
    test_file = tmp_path / "broken_invoice.txt"
    test_file.write_text("asdkjhasd non-invoice text", encoding="utf-8")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "{}"  # Empty JSON object indicating failure to extract
    mock_response.usage_metadata.total_token_count = 35
    mock_client.models.generate_content.return_value = mock_response

    with patch("invoice_extractor.extractor.genai.Client", return_value=mock_client):
        with pytest.raises(ValueError) as exc_info:
            extract_invoice(test_file, mock_settings)

    assert "Extraction failed" in str(exc_info.value)
    assert "broken_invoice.txt" in str(exc_info.value)


def test_extract_invoice_unsupported_file_extension(tmp_path: Path, mock_settings: Settings):
    """Files other than .txt and .pdf raise a ValueError."""
    unsupported_file = tmp_path / "image.png"
    unsupported_file.write_bytes(b"dummy")

    with pytest.raises(ValueError) as exc_info:
        extract_invoice(unsupported_file, mock_settings)

    assert "Unsupported file type: '.png'" in str(exc_info.value)
