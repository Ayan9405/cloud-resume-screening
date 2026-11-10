"""Document Parsing Service for PDF and DOCX files.
Supports Amazon Textract for cloud OCR as well as local fallback parsers
(pypdf and python-docx) for offline development and testing.
"""

import io
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    boto3 = None


class DocumentParser:
    """Extracts raw text from PDF and DOCX resumes using AWS Textract or local fallbacks."""

    def __init__(self, region_name: Optional[str] = None):
        self.region_name = region_name or os.environ.get("AWS_REGION", "us-east-1")
        self.textract_client = None
        if boto3 and os.environ.get("USE_AWS_SERVICES", "false").lower() == "true":
            try:
                self.textract_client = boto3.client("textract", region_name=self.region_name)
            except Exception as e:
                logger.warning(f"Failed to initialize AWS Textract client: {e}. Falling back to local parser.")

    def extract_text(
        self,
        file_bytes: bytes,
        filename: str,
        s3_bucket: Optional[str] = None,
        s3_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Extract text from a resume document.

        Args:
            file_bytes: Raw binary content of the file.
            filename: Name of the file with extension.
            s3_bucket: Optional S3 bucket name if using Textract via S3 object.
            s3_key: Optional S3 key if using Textract via S3 object.

        Returns:
            Dict containing 'text', 'page_count', 'method', and 'status'.
        """
        ext = os.path.splitext(filename)[1].lower()

        # Try AWS Textract if configured and file is PDF/Image
        if self.textract_client and ext in [".pdf", ".png", ".jpg", ".jpeg"]:
            try:
                textract_result = self._extract_with_textract(file_bytes, s3_bucket, s3_key)
                if textract_result.get("text"):
                    return textract_result
            except Exception as e:
                logger.warning(f"Textract extraction failed: {e}. Reverting to local parser.")

        # Local Fallback Parsers
        if ext == ".pdf":
            return self._extract_pdf_local(file_bytes)
        elif ext in [".docx", ".doc"]:
            return self._extract_docx_local(file_bytes)
        elif ext in [".txt", ".md"]:
            return {
                "text": file_bytes.decode("utf-8", errors="ignore").strip(),
                "page_count": 1,
                "method": "plain_text",
                "status": "success",
            }
        else:
            # Attempt best effort decode
            text = file_bytes.decode("utf-8", errors="ignore").strip()
            return {
                "text": text,
                "page_count": 1,
                "method": "fallback_decode",
                "status": "partial" if text else "unsupported_format",
            }

    def _extract_with_textract(
        self,
        file_bytes: bytes,
        s3_bucket: Optional[str] = None,
        s3_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Call Amazon Textract detect_document_text API."""
        if not self.textract_client:
            raise RuntimeError("Textract client not initialized")

        if s3_bucket and s3_key:
            response = self.textract_client.detect_document_text(
                Document={"S3Object": {"Bucket": s3_bucket, "Name": s3_key}}
            )
        else:
            response = self.textract_client.detect_document_text(
                Document={"Bytes": file_bytes}
            )

        extracted_lines = []
        for block in response.get("Blocks", []):
            if block.get("BlockType") == "LINE":
                extracted_lines.append(block.get("Text", ""))

        full_text = "\n".join(extracted_lines)
        return {
            "text": full_text,
            "page_count": response.get("DocumentMetadata", {}).get("Pages", 1),
            "method": "aws_textract",
            "status": "success",
        }

    def _extract_pdf_local(self, file_bytes: bytes) -> Dict[str, Any]:
        """Extract text from PDF using pypdf."""
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            pages_text = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    pages_text.append(extracted)
            full_text = "\n".join(pages_text).strip()
            return {
                "text": full_text,
                "page_count": len(reader.pages),
                "method": "local_pypdf",
                "status": "success" if full_text else "empty_text",
            }
        except Exception as e:
            logger.error(f"Failed to parse PDF locally: {e}")
            # Try simple latin1/utf-8 string fallback
            raw_text = file_bytes.decode("utf-8", errors="ignore")
            # Extract printable ascii runs
            import re
            cleaned = " ".join(re.findall(r"[A-Za-z0-9@._,\-\s]{4,}", raw_text))
            return {
                "text": cleaned,
                "page_count": 1,
                "method": "local_regex_fallback",
                "status": "fallback",
            }

    def _extract_docx_local(self, file_bytes: bytes) -> Dict[str, Any]:
        """Extract text from DOCX using python-docx."""
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            paragraphs.append(cell.text.strip())
            full_text = "\n".join(paragraphs).strip()
            return {
                "text": full_text,
                "page_count": 1,
                "method": "local_python_docx",
                "status": "success" if full_text else "empty_text",
            }
        except Exception as e:
            logger.error(f"Failed to parse DOCX locally: {e}")
            return {
                "text": "",
                "page_count": 0,
                "method": "local_docx_failed",
                "status": "error",
            }
