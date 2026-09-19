# Document Data

Document Data loads document-oriented and public information sources into document state.

## Source Families

- Text and NLTK corpora.
- CSV, Excel, JSON, XML, HTML, and Markdown.
- PDF, Word, and PowerPoint.
- arXiv and Wikipedia.
- GitHub and web sources.
- Google Drive and configured cloud object stores.
- Public/research loaders exposed by `loaders.py`.

## Processing

Loaded documents can flow through recursive chunking, embedding generation, vector validation, Chroma or Pinecone persistence, and document/chunk/vector inspection.

See [AI / ML Processing](../processing.md).
