
import io
import unittest
from pathlib import Path

import pymupdf
from docx import Document

from src.document_parser import (
    DocumentExtractionError,
    extract_document,
    extract_from_path,
    normalize_text,
)


class TestDocumentParser(unittest.TestCase):

    def test_valid_txt(self):
        result = extract_document(
            "candidate.txt",
            b"Python\nMachine Learning\nSQL"
        )
        self.assertEqual(result.file_type, "TXT")
        self.assertIn("Python", result.text)
        self.assertGreater(result.character_count, 0)

    def test_utf8_bom(self):
        content = b"\xef\xbb\xbfPython Developer"
        result = extract_document("resume.txt", content)
        self.assertEqual(result.text, "Python Developer")

    def test_empty_document(self):
        with self.assertRaises(DocumentExtractionError):
            extract_document("empty.txt", b"")

    def test_unsupported_format(self):
        with self.assertRaises(DocumentExtractionError):
            extract_document("resume.exe", b"example")

    def test_invalid_pdf(self):
        with self.assertRaises(DocumentExtractionError):
            extract_document("resume.pdf", b"not a pdf")

    def test_invalid_docx(self):
        with self.assertRaises(DocumentExtractionError):
            extract_document("resume.docx", b"not a docx")

    def test_invalid_txt_encoding(self):
        with self.assertRaises(DocumentExtractionError):
            extract_document("resume.txt", b"\xff\xfe\x00")

    def test_normalize_text(self):
        result = normalize_text(
            "Python   SQL\r\n\r\n\r\nMachine Learning"
        )
        self.assertEqual(
            result,
            "Python SQL\n\nMachine Learning"
        )

    def test_valid_pdf(self):
        document = pymupdf.open()
        page = document.new_page()
        page.insert_text(
            (72, 72),
            "Python Machine Learning SQL"
        )
        pdf_bytes = document.tobytes()
        document.close()

        result = extract_document("resume.pdf", pdf_bytes)

        self.assertEqual(result.file_type, "PDF")
        self.assertEqual(result.page_count, 1)
        self.assertIn("Machine Learning", result.text)

    def test_scanned_pdf_without_text(self):
        document = pymupdf.open()
        document.new_page()
        pdf_bytes = document.tobytes()
        document.close()

        with self.assertRaises(DocumentExtractionError):
            extract_document("scan.pdf", pdf_bytes)

    def test_valid_docx(self):
        document = Document()
        document.add_paragraph("Python Developer")
        document.add_paragraph("Machine Learning")

        buffer = io.BytesIO()
        document.save(buffer)

        result = extract_document(
            "resume.docx",
            buffer.getvalue()
        )

        self.assertEqual(result.file_type, "DOCX")
        self.assertIn("Python Developer", result.text)
        self.assertIn("Machine Learning", result.text)

    def test_docx_table(self):
        document = Document()
        table = document.add_table(rows=1, cols=2)
        table.cell(0, 0).text = "Skill"
        table.cell(0, 1).text = "Python"

        buffer = io.BytesIO()
        document.save(buffer)

        result = extract_document(
            "resume.docx",
            buffer.getvalue()
        )

        self.assertIn("Skill", result.text)
        self.assertIn("Python", result.text)

    def test_file_not_found(self):
        with self.assertRaises(DocumentExtractionError):
            extract_from_path(
                "data/resumes/nonexistent_candidate.txt"
            )

    def test_oversized_document(self):
        content = b"A" * (10 * 1024 * 1024 + 1)

        with self.assertRaises(DocumentExtractionError):
            extract_document("large.txt", content)

    def test_actual_synthetic_resume(self):
        path = Path(
            "data/resumes/candidate_01.txt"
        )

        self.assertTrue(
            path.is_file(),
            "Generate the synthetic resumes first."
        )

        result = extract_from_path(path)

        self.assertEqual(result.file_type, "TXT")
        self.assertTrue(result.text)
        self.assertGreater(result.character_count, 0)


if __name__ == "__main__":
    unittest.main()
