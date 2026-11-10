"""Tests for Document Parser."""

import pytest
from backend.services.document_parser import DocumentParser


def test_plain_text_extraction():
    parser = DocumentParser()
    sample_text = "John Doe\nSoftware Engineer\nPython, AWS, Docker"
    result = parser.extract_text(sample_text.encode("utf-8"), "resume.txt")

    assert result["status"] == "success"
    assert "John Doe" in result["text"]
    assert "Python" in result["text"]
    assert result["page_count"] == 1


def test_empty_file_handling():
    parser = DocumentParser()
    result = parser.extract_text(b"", "empty.txt")
    assert result["text"] == ""
