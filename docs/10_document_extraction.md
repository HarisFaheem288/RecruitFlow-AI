# \# RecruitFlow AI — Document Extraction Module

# 

# \## 1. Objective

# 

# Convert candidate resumes in supported formats into normalized, readable text for downstream evidence-based screening.

# 

# \## 2. Supported Formats

# 

# | Format | Library | Notes |

# |---|---|---|

# | TXT | Python standard library | UTF-8 text |

# | PDF | PyMuPDF | Text-based PDFs |

# | DOCX | python-docx | Paragraphs and tables |

# 

# \## 3. Input Contract

# 

# Function:

# 

# `extract\_document(filename: str, content: bytes)`

# 

# Required:

# \- Filename with supported extension

# \- Nonempty file content

# \- File size no greater than 10 MB

# 

# \## 4. Output Contract

# 

# ExtractionResult contains:

# 

# \- filename

# \- file\_type

# \- text

# \- character\_count

# \- page\_count

# \- warnings

# 

# \## 5. Processing Pipeline

# 

# 1\. Validate filename and extension.

# 2\. Validate document size.

# 3\. Check PDF or DOCX file structure.

# 4\. Extract text using the appropriate parser.

# 5\. Normalize whitespace.

# 6\. Reject documents without readable text.

# 7\. Return structured extraction result.

# 

# \## 6. Error Handling

# 

# The module handles:

# 

# \- Unsupported extensions

# \- Empty files

# \- Oversized files

# \- Invalid UTF-8 text

# \- Invalid PDF signatures

# \- Corrupted DOCX files

# \- Password-protected PDFs

# \- PDFs without extractable text

# \- Missing local files

# 

# Errors use the DocumentExtractionError exception.

# 

# \## 7. Known Limitations

# 

# \- OCR is not implemented.

# \- Scanned PDFs without embedded text cannot be processed.

# \- Complex visual resume layouts may lose their original reading order.

# \- Some content inside shapes, headers, footers, or embedded objects may not be extracted.

# \- The module does not evaluate candidate qualifications.

# \- A file passing basic validation is not guaranteed to be harmless or correctly formatted.

# \- The module does not implement resource-isolated processing for untrusted documents.

# 

# \## 8. Testing

# 

# Automated tests cover:

# 

# \- Valid TXT, PDF, DOCX extraction

# \- UTF-8 BOM handling

# \- Document normalization

# \- Invalid file types

# \- Corrupted files

# \- Empty files

# \- Missing files

# \- Oversized files

# \- Synthetic candidate resume extraction

# 

# \## 9. Example Command

# 

# `python test\_document\_parser.py data\\resumes\\candidate\_01.txt`

# 

# \## 10. Status

# 

# Implementation complete when all extraction tests pass on the development environment.

# 

# PDF and DOCX extraction must be validated with generated test documents before the module is considered verified.



