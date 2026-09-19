# File Upload

File Upload ingests supported local files for preview, extraction, and processing.

## Supported Families

- Text.
- CSV and Excel.
- JSON and XML.
- HTML and Markdown.
- PDF.
- Word.
- PowerPoint.

```text
Uploaded file
    │
    ▼
Loader / parser
    │
    ▼
Document state
    │
    ├──► Preview
    ├──► Chunking
    ├──► Embeddings
    └──► Vector storage
```
