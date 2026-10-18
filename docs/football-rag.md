# Football RAG search

The authenticated endpoint `GET /api/football-rag/search` searches the Neon `football_rag.chunks` corpus using PostgreSQL full-text search.

## Request

```http
GET /api/football-rag/search?q=futebol&limit=5
```

A valid application session is required. The `q` parameter must contain 1–200 characters. `limit` is clamped to 1–10 (default 5).

## Response

The response contains `query`, `count`, and `results`. Each result includes `chunkId`, `chunkIndex`, `content`, `language`, `titlePath`, and a full-text relevance `score`. Local source paths and credentials are not returned.

## Database access

Configure `NEON_DATABASE_URL` as a sensitive Vercel environment variable using the `peseditor_rag_reader` role. This role has read access to `football_rag` and no insert/update privileges. The route runs server-side only.

## Current indexing state

- 14,978 source-corpus chunks are loaded and full-text indexed.
- 7,939 canonical PES 2013 player records are loaded into `football_rag.canonical_players`.
- Jina/OpenAI vector embeddings have not yet been generated. This endpoint uses PostgreSQL full-text search, not vector similarity.
