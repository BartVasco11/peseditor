import 'server-only';

import postgres from 'postgres';

export type FootballChunk = {
  chunk_id: string;
  chunk_index: number;
  content: string;
  language: string | null;
  title_path: string[] | null;
  score: number;
};

let client: ReturnType<typeof postgres> | undefined;

function getClient() {
  const connectionString = process.env.NEON_DATABASE_URL;
  if (!connectionString) return null;

  if (!client) {
    client = postgres(connectionString, {
      max: 1,
      connect_timeout: 10,
      idle_timeout: 20,
      prepare: false,
      connection: { application_name: 'peseditor-football-rag' },
    });
  }

  return client;
}

function buildTsQuery(input: string) {
  const tokens = input.normalize('NFKC').match(/[\p{L}\p{N}]{2,}/gu) ?? [];
  const stopwords = new Set(['the', 'and', 'for', 'with', 'that', 'this', 'how', 'what', 'why', 'when', 'where', 'can', 'could', 'would', 'should', 'de', 'da', 'do', 'das', 'dos', 'e', 'ou', 'em', 'no', 'na', 'nos', 'nas', 'para', 'por', 'com', 'sem', 'que', 'um', 'uma', 'uns', 'umas', 'ao', 'aos', 'as', 'os', 'o', 'a']);
  const uniqueTokens = [...new Set(tokens.map((token) => token.toLowerCase()).filter((token) => !stopwords.has(token) && (/[\\p{L}]/u.test(token) ? token.length >= 3 : token.length >= 2)))].slice(0, 12);
  return uniqueTokens.map((token) => `${token}:*`).join(' | ');
}

export async function searchFootballKnowledge(
  input: string,
  limit = 5,
): Promise<FootballChunk[]> {
  const tsQuery = buildTsQuery(input);
  if (!tsQuery) return [];

  const sql = getClient();
  if (!sql) {
    console.warn('Football RAG is not configured; skipping retrieval.');
    return [];
  }

  const safeLimit = Math.min(5, Math.max(1, Math.floor(limit)));

  try {
    const rows = (await sql`
      SELECT
        chunk_id,
        chunk_index,
        content,
        language,
        title_path,
        ts_rank_cd(search_vector, to_tsquery('simple', ${tsQuery}))::float8 AS score
      FROM football_rag.chunks
      WHERE search_vector @@ to_tsquery('simple', ${tsQuery})
      ORDER BY score DESC, chunk_id
      LIMIT ${safeLimit}
    `) as unknown as FootballChunk[];

    return rows;
  } catch (error) {
    console.error(
      'Football RAG retrieval failed',
      error instanceof Error ? error.message : 'Unknown database error',
    );
    return [];
  }
}
