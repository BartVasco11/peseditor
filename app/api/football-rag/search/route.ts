import { auth } from '@/app/(auth)/auth';
import { searchFootballKnowledge } from '@/lib/ai/football-rag';
import { NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

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
    ? Math.min(5, Math.max(1, Math.floor(requestedLimit)))
    : 5;
  const results = await searchFootballKnowledge(query, limit);

  return NextResponse.json({
    query,
    count: results.length,
    results: results.map((row) => ({
      chunkId: row.chunk_id,
      chunkIndex: row.chunk_index,
      content: row.content,
      language: row.language,
      titlePath: row.title_path,
      score: Number(row.score.toFixed(6)),
    })),
  });
}
