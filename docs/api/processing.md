# AI / Processing API

## Pipeline Functions

| Function | Purpose |
|---|---|
| `chunk_documents(...)` | Split LangChain documents into retrieval chunks. |
| `create_embeddings(...)` | Create and validate vectors for chunks. |
| `store_documents(...)` | Persist chunks to Chroma or Pinecone. |
| `initialize_mode_document_state(...)` | Initialize isolated mode processing state. |
| `serialize_mode_result(...)` | Serialize structured results for document content. |
| `sync_mode_document(...)` | Synchronize a mode result into LangChain document state. |

The pipeline module imports the full parser stack, so this page documents its public orchestration surface without importing it during MkDocs generation.

## Embedding Factory

::: embedders.EmbeddingFactory

## Local GGUF Embeddings

::: embedders.LocalGGUFEmbeddings

## Vector Stores

::: stores.vector
