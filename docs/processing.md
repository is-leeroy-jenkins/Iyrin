# AI / ML Processing

Iyrin converts supported results and loaded content into LangChain `Document` objects for chunking, embeddings, vector persistence, semantic retrieval, and agent context.

## Chunking

- `RecursiveCharacterTextSplitter`.
- Configurable chunk size.
- Configurable overlap.
- Stable `chunk_id` metadata.
- Downstream invalidation when chunk settings change.

## Embeddings

| Provider | Models / Mode |
|---|---|
| OpenAI | `text-embedding-3-small`, `text-embedding-3-large` |
| Google Generative AI | `gemini-embedding-2-preview` |
| Mistral AI | `mistral-embed` |
| Hugging Face | `sentence-transformers/all-MiniLM-L6-v2`, `sentence-transformers/all-mpnet-base-v2` |
| Local GGUF | Local embedding-capable GGUF models through `llama-cpp-python` |

## Validation

- One vector per chunk.
- Consistent vector dimensions.
- Finite numeric values.
- Local model-path validation before GGUF loading.

## Vector Storage

- Chroma persistent collections.
- Pinecone indexes with optional namespaces.
