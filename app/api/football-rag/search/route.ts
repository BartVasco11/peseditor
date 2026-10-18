import { auth } from '@/app/(auth)/auth';
import postgres from 'postgres';
import { NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

type SearchRow = {
  chunk_id: string;
  chunk_index: number;
  content: string;
  language: string | null;
  title_path: string[];
  score: number;
};

let client: ReturnType<typeof postgres> | undefined;

function getClient() {
  const connectionString = process.env.NEON_DATABASE_URL;
  if (!connectionString) {
    throw new Error('NEON_DATABASE_URL is not configured');
  }

  if (!client) {
    client = postgres(connectionString, {
      max: 1,
      connect_timeout: 10,
      idle_timeout: 20,
      prepare: false,
      connection: { application_name: 'peseditor-football-rag-search' },
    });
  }

  return client;
}

export async function GET(request: Request) {
  const session = await auth();
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const url = new URL(request.url);
  const query = (url.searchParams.get('q') ?? '').trim();

  if (!query || query.length > 200) {
    return NextResponse.json(
      { error: 'Provide a search query between 1 and 200 characters.' },
      { status: 400 },
    );
  }

  const requestedLimit = Number(url.searchParams.get('limit') ?? '5');
  const limit = Number.isFinite(requestedLimit)
    ? Math.min(10, Math.max(1, Math.floor(requestedLimit)))
    : 5;

  try {
    const sql = getClient();
    const rows = (await sql`
      SELECT
        chunk_id,
        chunk_index,
        content,
        language,
        title_path,
        ts_rank_cd(search_vector, plainto_tsquery('simple', ${query}))::float8 AS score
      FROM football_rag.chunks
      WHERE search_vector @@ plainto_tsquery('simple', ${query})
      ORDER BY score DESC, chunk_id
      LIMIT ${limit}
    `) as unknown as SearchRow[];

    return NextResponse.json({
      query,
      count: rows.length,
      results: rows.map((row) => ({
        chunkId: row.chunk_id,
        chunkIndex: row.chunk_index,
        content: row.content,
        language: row.language,
        titlePath: row.title_path,
        score: Number(row.score.toFixed(6)),
      })),
    });
  } catch (error) {
    console.error(
      'football-rag search failed',
      error instanceof Error ? error.message : 'Unknown database error',
    );
    return NextResponse.json(
      { error: 'Football knowledge search is temporarily unavailable.' },
      { status: 503 },
    );
  }
}
